"""
import_legiscan.py
-----------------
Fetches recent legislation from the LegiScan API across all 50 states
and writes it into sl_legislation, filtered by topic keywords.

LegiScan API docs: https://legiscan.com/legiscan
Free API key: https://legiscan.com/user/register (500 pulls/day free tier)

This script:
  1. Fetches the current legislative session for each state
  2. Searches bills by topic keywords (healthcare, housing, jobs, etc.)
  3. Upserts matching bills into sl_legislation
  4. Links bills to topic categories in sl_legislation_topics

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    LEGISCAN_API_KEY=your-key \
    python import_legiscan.py

Requirements:
    pip install supabase python-dotenv requests
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
LEGISCAN_API_KEY     = os.environ.get("LEGISCAN_API_KEY")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "LEGISCAN_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

LEGISCAN_BASE = "https://api.legiscan.com"

# Keywords used to match bills to topic categories
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "healthcare":       ["health", "medicaid", "medicare", "insurance", "hospital",
                         "prescription", "mental health", "behavioral health", "pharmacy"],
    "housing":          ["housing", "rent", "zoning", "affordable", "eviction",
                         "homelessness", "landlord", "tenant", "mortgage"],
    "jobs":             ["employment", "workforce", "minimum wage", "labor", "job",
                         "economic development", "small business", "apprenticeship", "unemployment"],
    "education":        ["education", "school", "teacher", "curriculum", "student",
                         "higher education", "college", "university", "literacy"],
    "criminal-justice": ["criminal", "police", "sentencing", "incarceration", "parole",
                         "probation", "reentry", "prison", "bail", "juvenile"],
    "environment":      ["climate", "environment", "renewable", "energy", "emissions",
                         "carbon", "clean air", "clean water", "conservation"],
    "taxes":            ["tax", "revenue", "budget", "fiscal", "income tax",
                         "property tax", "sales tax", "exemption"],
    "infrastructure":   ["infrastructure", "broadband", "transit", "road", "bridge",
                         "utility", "water system", "public works"],
    "immigration":      ["immigration", "immigrant", "sanctuary", "visa", "asylum",
                         "undocumented", "border"],
    "voting":           ["voting", "election", "ballot", "voter", "redistricting",
                         "campaign finance", "primary", "ranked choice"],
}

# Bill statuses that map to our schema enum
STATUS_MAP = {
    1: "introduced",
    2: "in_committee",
    3: "passed_chamber",
    4: "passed",
    5: "signed",
    6: "vetoed",
    7: "failed",
}


def legiscan_get(op: str, params: dict) -> dict:
    """Make a LegiScan API call."""
    try:
        r = requests.get(
            LEGISCAN_BASE,
            params={"key": LEGISCAN_API_KEY, "op": op, **params},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"    WARNING: LegiScan {op} failed — {e}")
        return {}


def get_state_id(abbreviation: str) -> str | None:
    result = (
        supabase.table("sl_states")
        .select("id")
        .eq("abbreviation", abbreviation)
        .limit(1)
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def get_topic_ids() -> dict[str, str]:
    """Returns {slug: id} for all topics."""
    result = supabase.table("sl_topics").select("id,slug").execute()
    return {row["slug"]: row["id"] for row in result.data}


def match_topics(title: str, description: str, topic_ids: dict[str, str]) -> list[str]:
    """Returns list of matching topic UUIDs based on keyword matching."""
    text = f"{title} {description}".lower()
    matched = []
    for slug, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            if slug in topic_ids:
                matched.append(topic_ids[slug])
    return matched


def upsert_bill(bill: dict, state_id: str, topic_ids: dict[str, str]) -> str | None:
    """Upserts a bill and returns its UUID."""
    legiscan_id = bill.get("bill_id")
    if not legiscan_id:
        return None

    title       = bill.get("title", "").strip()
    description = bill.get("description", "") or ""
    status_raw  = bill.get("status", 1)
    status      = STATUS_MAP.get(int(status_raw), "introduced")

    row = {
        "state_id":         state_id,
        "bill_number":      bill.get("bill_number"),
        "title":            title,
        "summary":          description[:2000] if description else None,
        "full_text_url":    bill.get("url"),
        "status":           status,
        "session_year":     bill.get("session", {}).get("year_start") if isinstance(bill.get("session"), dict) else None,
        "introduced_date":  bill.get("introduced_date") or None,
        "passed_date":      bill.get("last_action_date") if status in ("passed", "signed") else None,
        "sponsor":          bill.get("sponsors", [{}])[0].get("name") if bill.get("sponsors") else None,
        "sponsor_party":    bill.get("sponsors", [{}])[0].get("party") if bill.get("sponsors") else None,
        "legiscan_id":      legiscan_id,
        "sources":          [{"name": "LegiScan", "url": bill.get("url", "")}],
    }

    # Upsert on legiscan_id
    existing = (
        supabase.table("sl_legislation")
        .select("id")
        .eq("legiscan_id", legiscan_id)
        .limit(1)
        .execute()
    )
    if existing.data:
        leg_id = existing.data[0]["id"]
        supabase.table("sl_legislation").update(row).eq("id", leg_id).execute()
    else:
        result = supabase.table("sl_legislation").insert(row).execute()
        leg_id = result.data[0]["id"] if result.data else None

    if not leg_id:
        return None

    # Link topics
    matched_topic_ids = match_topics(title, description, topic_ids)
    for topic_id in matched_topic_ids:
        supabase.table("sl_legislation_topics").upsert(
            {"legislation_id": leg_id, "topic_id": topic_id},
            on_conflict="legislation_id,topic_id"
        ).execute()

    return leg_id


def main() -> None:
    print("Fetching state legislation from LegiScan...")
    topic_ids = get_topic_ids()
    print(f"  Loaded {len(topic_ids)} topic categories.")

    # Get all state sessions
    sessions_data = legiscan_get("getSessionList", {"state": "ALL"})
    sessions = sessions_data.get("sessions", [])

    if not sessions:
        print("  No sessions returned — check your API key.")
        return

    # Group sessions by state, keep only the most recent
    latest_by_state: dict[str, dict] = {}
    for session in sessions:
        state = session.get("state_abbr") or session.get("state", "")
        year  = session.get("year_start", 0)
        if state not in latest_by_state or year > latest_by_state[state].get("year_start", 0):
            latest_by_state[state] = session

    total_bills = 0
    for abbr, session in sorted(latest_by_state.items()):
        state_id = get_state_id(abbr)
        if not state_id:
            continue

        session_id = session.get("session_id")
        print(f"  → {abbr} (session {session_id}, {session.get('year_start')})")

        # Fetch master list for this session
        master = legiscan_get("getMasterList", {"id": session_id})
        bill_list = list(master.get("masterlist", {}).values())

        imported = 0
        for bill_stub in bill_list:
            if not isinstance(bill_stub, dict):
                continue
            title = bill_stub.get("title", "").lower()
            description = bill_stub.get("description", "") or ""
            # Only fetch detail for bills matching our topics (saves API calls)
            if not match_topics(title, description, topic_ids):
                continue

            bill_id = bill_stub.get("bill_id")
            if not bill_id:
                continue

            # Fetch full bill detail
            detail = legiscan_get("getBill", {"id": bill_id})
            bill   = detail.get("bill", bill_stub)
            result = upsert_bill(bill, state_id, topic_ids)
            if result:
                imported += 1
            time.sleep(0.2)

        print(f"    Imported {imported} matching bills.")
        total_bills += imported
        time.sleep(1)

    print(f"\nDone. Total bills imported: {total_bills}")


if __name__ == "__main__":
    main()
