"""
import_ballotpedia.py
---------------------
Fetches candidate data from Ballotpedia's public API for a target state
and upserts it into pol_candidates, linking to pol_districts.

Ballotpedia API docs: https://ballotpedia.org/API-documentation
Free tier: 500 requests/day. Register at https://ballotpedia.org/API-documentation

Environment variables:
    STATE_NAME   — Full state name to query (default: Colorado)
    OFFICE_TYPES — Comma-separated list of office types to fetch
                   (default: U.S. House,State Senate,State House,Governor,
                    Attorney General,Secretary of State,State Treasurer)

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    BALLOTPEDIA_API_KEY=your-key \
    STATE_NAME=Texas \
    python import_ballotpedia.py

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
BALLOTPEDIA_API_KEY  = os.environ.get("BALLOTPEDIA_API_KEY")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "BALLOTPEDIA_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

STATE_NAME = os.environ.get("STATE_NAME", "Colorado")

_DEFAULT_OFFICE_TYPES = (
    "U.S. House,State Senate,State House,Governor,"
    "Attorney General,Secretary of State,State Treasurer"
)
OFFICE_QUERIES = [
    {"office_type": t.strip(), "state": STATE_NAME}
    for t in os.environ.get("OFFICE_TYPES", _DEFAULT_OFFICE_TYPES).split(",")
    if t.strip()
]

BALLOTPEDIA_BASE = "https://api.ballotpedia.org/v1"
HEADERS = {"x-api-key": BALLOTPEDIA_API_KEY, "Content-Type": "application/json"}

PARTY_NORMALIZE = {
    "democratic party": "Democrat",
    "democratic": "Democrat",
    "republican party": "Republican",
    "republican": "Republican",
    "libertarian party": "Libertarian",
    "libertarian": "Libertarian",
    "green party": "Green",
    "green": "Green",
    "independent": "Independent",
    "nonpartisan": "Nonpartisan",
}


def normalize_party(raw: str) -> str:
    return PARTY_NORMALIZE.get(raw.lower().strip(), "Other") if raw else "Other"


def get_district_id_by_name(district_name: str) -> str | None:
    result = (
        supabase.table("pol_districts")
        .select("id")
        .ilike("name", f"%{district_name}%")
        .limit(1)
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def fetch_candidates(office_type: str, state: str) -> list[dict]:
    """Query Ballotpedia for active candidates for a given office type and state."""
    url = f"{BALLOTPEDIA_BASE}/candidates"
    params = {
        "office_type": office_type,
        "state": state,
        "is_active": True,
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"  WARNING: Failed to fetch {office_type} — {e}")
        return []


def upsert_candidate(candidate: dict) -> None:
    full_name    = candidate.get("name", "").strip()
    party_raw    = candidate.get("party", "")
    office       = candidate.get("office_name", "").strip()
    district_raw = candidate.get("district_name", "")
    bio          = candidate.get("summary", "")
    website      = candidate.get("url", "")
    incumbent    = candidate.get("is_incumbent", False)

    if not full_name or not office:
        return

    district_id = get_district_id_by_name(district_raw) if district_raw else None

    social = {}
    for field in ("twitter", "facebook", "instagram", "youtube"):
        val = candidate.get(field)
        if val:
            social[field] = val

    row = {
        "full_name":        full_name,
        "party":            normalize_party(party_raw),
        "office":           office,
        "district_id":      district_id,
        "bio":              bio,
        "campaign_website": website,
        "incumbent":        bool(incumbent),
        "active":           True,
        "social_media":     social,
        "sources":          [{"name": "Ballotpedia", "url": candidate.get("url", "")}],
    }

    existing = (
        supabase.table("pol_candidates")
        .select("id")
        .eq("full_name", full_name)
        .eq("office", office)
        .limit(1)
        .execute()
    )
    if existing.data:
        supabase.table("pol_candidates").update(row).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("pol_candidates").insert(row).execute()


def main() -> None:
    print(f"Importing {STATE_NAME} candidates from Ballotpedia...")
    total = 0
    for query in OFFICE_QUERIES:
        print(f"  → {query['office_type']}")
        candidates = fetch_candidates(query["office_type"], query["state"])
        for c in candidates:
            upsert_candidate(c)
            total += 1
        time.sleep(0.5)  # Respect rate limits

    print(f"Done. Processed {total} candidates from Ballotpedia.")


if __name__ == "__main__":
    main()
