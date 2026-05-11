"""
generate_assessments.py
-----------------------
Uses the Anthropic Claude API to generate impact assessments for
legislation in sl_legislation that doesn't yet have an assessment.

For each bill, Claude:
  1. Reads the bill title, summary, and linked news articles
  2. Assesses whether the legislation has been positive, negative,
     mixed, or unclear in its real-world impact
  3. Writes a structured assessment with evidence citations into
     sl_impact_assessments

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    ANTHROPIC_API_KEY=your-key \
    python generate_assessments.py

Optional env vars:
    MAX_BILLS=50         (default: 50, to stay within API limits)
    MODEL=claude-opus-4-5  (default: claude-opus-4-5)

Requirements:
    pip install supabase python-dotenv anthropic
"""

import os
import sys
import json
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import anthropic

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY")
MAX_BILLS            = int(os.environ.get("MAX_BILLS", "50"))
MODEL                = os.environ.get("MODEL", "claude-opus-4-5")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ASSESSMENT_PROMPT = """You are a nonpartisan policy analyst. Your job is to assess the real-world impact of a piece of state legislation based on its title, summary, and any news coverage available.

Bill information:
- State: {state}
- Bill number: {bill_number}
- Title: {title}
- Summary: {summary}
- Status: {status}

News coverage:
{news_coverage}

Provide your assessment in the following JSON format:
{{
  "verdict": "positive" | "negative" | "mixed" | "unclear",
  "summary": "2-4 sentence plain-language summary of the bill's real-world impact and why you gave this verdict",
  "evidence": [
    {{
      "source": "outlet name or official source",
      "url": "url if available",
      "excerpt": "key quote or finding that supports this assessment",
      "sentiment": "positive" | "negative" | "neutral" | "mixed"
    }}
  ]
}}

Guidelines:
- Be nonpartisan. Focus on measurable outcomes, not political framing.
- If there is little real-world data yet (bill recently signed, no news), use "unclear".
- If coverage is split, use "mixed" and explain both sides.
- Cite specific evidence from the news articles when available.
- Keep the summary concise and factual.
- Return only valid JSON, no additional text.
"""


def get_unassessed_bills(limit: int) -> list[dict]:
    """Get bills that don't yet have an impact assessment."""
    # Get IDs that already have assessments
    assessed = supabase.table("sl_impact_assessments").select("legislation_id").execute()
    assessed_ids = {row["legislation_id"] for row in assessed.data}

    result = (
        supabase.table("sl_legislation")
        .select("id, bill_number, title, summary, status, state_id")
        .in_("status", ["signed", "passed", "passed_chamber"])
        .limit(limit * 2)  # Fetch extra, filter out assessed
        .execute()
    )

    bills = [b for b in result.data if b["id"] not in assessed_ids]
    return bills[:limit]


def get_state_name(state_id: str) -> str:
    result = supabase.table("sl_states").select("name").eq("id", state_id).limit(1).execute()
    return result.data[0]["name"] if result.data else "Unknown"


def get_news_for_bill(legislation_id: str) -> list[dict]:
    result = (
        supabase.table("sl_news_sources")
        .select("headline, outlet, url, excerpt, sentiment")
        .eq("legislation_id", legislation_id)
        .limit(5)
        .execute()
    )
    return result.data


def format_news(news: list[dict]) -> str:
    if not news:
        return "No news coverage available."
    lines = []
    for n in news:
        lines.append(f"- [{n.get('outlet', 'Unknown')}] {n.get('headline', '')}")
        if n.get("excerpt"):
            lines.append(f"  Excerpt: {n['excerpt'][:300]}")
        if n.get("url"):
            lines.append(f"  URL: {n['url']}")
    return "\n".join(lines)


def assess_bill(bill: dict) -> dict | None:
    state_name = get_state_name(bill["state_id"])
    news       = get_news_for_bill(bill["id"])

    prompt = ASSESSMENT_PROMPT.format(
        state        = state_name,
        bill_number  = bill.get("bill_number", "N/A"),
        title        = bill.get("title", ""),
        summary      = bill.get("summary") or "No summary available.",
        status       = bill.get("status", ""),
        news_coverage= format_news(news),
    )

    try:
        message = client.messages.create(
            model      = MODEL,
            max_tokens = 1024,
            messages   = [{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        print(f"    WARNING: Assessment failed for {bill.get('bill_number')} — {e}")
        return None


def main() -> None:
    print(f"Generating impact assessments for up to {MAX_BILLS} bills...")
    bills = get_unassessed_bills(MAX_BILLS)
    print(f"  Found {len(bills)} unassessed bills.")

    completed = 0
    for bill in bills:
        print(f"  → {bill.get('bill_number', 'N/A')}: {bill.get('title', '')[:60]}...")
        assessment = assess_bill(bill)

        if not assessment:
            continue

        supabase.table("sl_impact_assessments").insert({
            "legislation_id": bill["id"],
            "verdict":        assessment.get("verdict", "unclear"),
            "summary":        assessment.get("summary", ""),
            "evidence":       assessment.get("evidence", []),
            "assessed_by":    f"claude ({MODEL})",
        }).execute()

        completed += 1
        print(f"    Verdict: {assessment.get('verdict', 'unclear')}")
        time.sleep(1)  # Avoid rate limits

    print(f"\nDone. Generated {completed} impact assessments.")


if __name__ == "__main__":
    main()
