"""
import_opensecrets.py
--------------------
Fetches Colorado campaign finance data from OpenSecrets API
and writes it into co_campaign_finance, matched to co_candidates.

OpenSecrets API docs: https://www.opensecrets.org/api/
Free API key: https://www.opensecrets.org/api/admin/index.php?function=signup
Rate limit: 200 calls/day on free tier.

This script targets:
  - /candSummary — Fundraising totals for a candidate/cycle
  - /candContrib — Top contributors per candidate

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    OPENSECRETS_API_KEY=your-key \
    CYCLE_YEAR=2024 \
    python import_opensecrets.py

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
OPENSECRETS_API_KEY  = os.environ.get("OPENSECRETS_API_KEY")
CYCLE_YEAR           = os.environ.get("CYCLE_YEAR", "2024")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "OPENSECRETS_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

OPENSECRETS_BASE = "https://www.opensecrets.org/api"
# Colorado state abbreviation for OpenSecrets
CO_STATE = "CO"


def fetch_legislators(state: str, cycle: str) -> list[dict]:
    """Fetch all current legislators for a state from OpenSecrets."""
    try:
        r = requests.get(
            OPENSECRETS_BASE,
            params={
                "method": "getLegislators",
                "id": state,
                "apikey": OPENSECRETS_API_KEY,
                "output": "json",
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("response", {}).get("legislator", [])
    except requests.RequestException as e:
        print(f"  WARNING: getLegislators failed — {e}")
        return []


def fetch_cand_summary(cid: str, cycle: str) -> dict:
    """Fetch fundraising summary for a candidate."""
    try:
        r = requests.get(
            OPENSECRETS_BASE,
            params={
                "method": "candSummary",
                "cid": cid,
                "cycle": cycle,
                "apikey": OPENSECRETS_API_KEY,
                "output": "json",
            },
            timeout=15,
        )
        r.raise_for_status()
        return r.json().get("response", {}).get("summary", {}).get("@attributes", {})
    except requests.RequestException as e:
        print(f"  WARNING: candSummary failed for {cid} — {e}")
        return {}


def fetch_top_contributors(cid: str, cycle: str) -> list[dict]:
    """Fetch top contributors for a candidate."""
    try:
        r = requests.get(
            OPENSECRETS_BASE,
            params={
                "method": "candContrib",
                "cid": cid,
                "cycle": cycle,
                "apikey": OPENSECRETS_API_KEY,
                "output": "json",
            },
            timeout=15,
        )
        r.raise_for_status()
        contributors = (
            r.json()
            .get("response", {})
            .get("contributors", {})
            .get("contributor", [])
        )
        return [
            {
                "name":  c.get("@attributes", {}).get("org_name"),
                "total": c.get("@attributes", {}).get("total"),
            }
            for c in contributors[:10]  # top 10
        ]
    except requests.RequestException as e:
        print(f"  WARNING: candContrib failed for {cid} — {e}")
        return []


def match_candidate_in_db(full_name: str) -> str | None:
    """Try to find a matching candidate in co_candidates by name."""
    # Try exact match first
    result = (
        supabase.table("co_candidates")
        .select("id")
        .ilike("full_name", full_name)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["id"]

    # Try last-name match
    last_name = full_name.split(",")[0].strip() if "," in full_name else full_name.split()[-1]
    result = (
        supabase.table("co_candidates")
        .select("id")
        .ilike("full_name", f"%{last_name}%")
        .limit(1)
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def main() -> None:
    print(f"Importing Colorado campaign finance from OpenSecrets (cycle {CYCLE_YEAR})...")
    legislators = fetch_legislators(CO_STATE, CYCLE_YEAR)
    print(f"  Found {len(legislators)} legislators from OpenSecrets.")

    inserted = 0
    for leg in legislators:
        attrs     = leg.get("@attributes", {})
        cid       = attrs.get("cid")
        firstlast = attrs.get("firstlast", "")
        if not cid:
            continue

        candidate_id = match_candidate_in_db(firstlast)
        if not candidate_id:
            print(f"  SKIP: {firstlast} not found in co_candidates — run import_ballotpedia.py first.")
            continue

        print(f"  → {firstlast} ({cid})")
        summary     = fetch_cand_summary(cid, CYCLE_YEAR)
        contributors = fetch_top_contributors(cid, CYCLE_YEAR)

        def to_float(val: str | None) -> float | None:
            try:
                return float(str(val).replace(",", "").replace("$", "")) if val else None
            except ValueError:
                return None

        row = {
            "candidate_id":  candidate_id,
            "cycle_year":    int(CYCLE_YEAR),
            "total_raised":  to_float(summary.get("total")),
            "total_spent":   to_float(summary.get("spent")),
            "cash_on_hand":  to_float(summary.get("cash_on_hand")),
            "top_donors":    contributors,
            "source":        "OpenSecrets",
            "source_url":    f"https://www.opensecrets.org/members-of-congress/summary?cid={cid}&cycle={CYCLE_YEAR}",
        }

        # Upsert on candidate + cycle
        existing = (
            supabase.table("co_campaign_finance")
            .select("id")
            .eq("candidate_id", candidate_id)
            .eq("cycle_year", int(CYCLE_YEAR))
            .limit(1)
            .execute()
        )
        if existing.data:
            supabase.table("co_campaign_finance").update(row).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("co_campaign_finance").insert(row).execute()

        inserted += 1
        time.sleep(0.3)  # Respect rate limits

    print(f"Done. Processed finance records for {inserted} candidates.")


if __name__ == "__main__":
    main()
