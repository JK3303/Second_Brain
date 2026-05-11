"""
import_sos_results.py
---------------------
Imports election results from a Secretary of State CSV export and
writes them into pol_candidates and pol_election_results.

Most state SOS websites publish downloadable CSV/XML files of election
results. Download one for your target election year, point RESULTS_CSV_PATH
at it, and run this script.

CSV column names vary by state and year. If the script warns about missing
columns, open the CSV and update the column mapping constants below.

Environment variables (required):
    SUPABASE_URL          — Your Supabase project URL
    SUPABASE_SERVICE_KEY  — Your Supabase service role key
    RESULTS_CSV_PATH      — Path to the downloaded SOS results CSV
    ELECTION_YEAR         — Four-digit year (default: 2024)
    ELECTION_TYPE         — primary | general | special | runoff (default: general)

Environment variables (optional):
    STATE_NAME            — Used in the source attribution (default: Unknown State)
    SOS_URL               — URL of the SOS results portal for source attribution

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    RESULTS_CSV_PATH=path/to/results.csv \
    ELECTION_YEAR=2024 \
    ELECTION_TYPE=general \
    STATE_NAME=Colorado \
    SOS_URL=https://www.sos.state.co.us/pubs/elections/Results/ \
    python import_sos_results.py

Requirements:
    pip install supabase python-dotenv pandas
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
RESULTS_CSV_PATH     = os.environ.get("RESULTS_CSV_PATH")
ELECTION_YEAR        = int(os.environ.get("ELECTION_YEAR", "2024"))
ELECTION_TYPE        = os.environ.get("ELECTION_TYPE", "general")
STATE_NAME           = os.environ.get("STATE_NAME", "Unknown State")
SOS_URL              = os.environ.get("SOS_URL", "")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "RESULTS_CSV_PATH"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_or_create_candidate(full_name: str, party: str, office: str, district_id: str | None) -> str:
    """Returns the UUID of an existing or newly created candidate."""
    existing = (
        supabase.table("pol_candidates")
        .select("id")
        .eq("full_name", full_name)
        .eq("office", office)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]["id"]

    party_map = {
        "dem": "Democrat", "democratic": "Democrat",
        "rep": "Republican", "republican": "Republican",
        "lib": "Libertarian", "libertarian": "Libertarian",
        "grn": "Green", "green": "Green",
        "unaffiliated": "Independent", "ind": "Independent",
    }
    normalized_party = party_map.get(party.lower().strip(), "Other") if party else "Other"

    source_entry = {"name": f"{STATE_NAME} Secretary of State"}
    if SOS_URL:
        source_entry["url"] = SOS_URL

    result = (
        supabase.table("pol_candidates")
        .insert({
            "full_name":    full_name,
            "party":        normalized_party,
            "office":       office,
            "district_id":  district_id,
            "active":       True,
            "sources":      [source_entry],
        })
        .execute()
    )
    return result.data[0]["id"]


def get_district_id(office: str) -> str | None:
    """Attempts to match an office string to a district UUID.

    Edit the lookup_map below to match your state's SOS office name format.
    Examples: "U.S. House District 2", "State Senate District 14", "State Representative District 30"
    """
    lookup_map = [
        ("U.S. House District", "congressional", "CD-"),
        ("State Senate District", "state_senate", "SD-"),
        ("State Representative District", "state_house", "HD-"),
    ]
    for prefix, district_type, number_prefix in lookup_map:
        if prefix in office:
            number = office.replace(prefix, "").strip()
            result = (
                supabase.table("pol_districts")
                .select("id")
                .eq("type", district_type)
                .eq("district_number", f"{number_prefix}{number}")
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]["id"]
    return None


def main() -> None:
    print(f"Importing {ELECTION_YEAR} {ELECTION_TYPE} results from: {RESULTS_CSV_PATH}")
    df = pd.read_csv(RESULTS_CSV_PATH)

    # SOS exports typically have columns like:
    # Contest Name | Candidate Name | Party | Votes | Percent | Winner
    # Adjust column names below to match the actual file you downloaded.
    required_cols = {"Contest Name", "Candidate Name", "Party", "Votes", "Percent"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"WARNING: Expected columns not found: {missing}")
        print(f"Available columns: {list(df.columns)}")
        print("Edit the column mapping in this script to match your CSV.")

    results_to_insert = []
    total_votes_by_contest: dict[str, int] = (
        df.groupby("Contest Name")["Votes"].sum().to_dict()
        if "Votes" in df.columns and "Contest Name" in df.columns
        else {}
    )

    for _, row in df.iterrows():
        office     = str(row.get("Contest Name", "")).strip()
        full_name  = str(row.get("Candidate Name", "")).strip()
        party      = str(row.get("Party", "")).strip()
        votes_raw  = row.get("Votes", 0)
        pct_raw    = row.get("Percent", None)
        winner_raw = str(row.get("Winner", "")).strip().lower()

        if not full_name or not office:
            continue

        district_id  = get_district_id(office)
        candidate_id = get_or_create_candidate(full_name, party, office, district_id)

        results_to_insert.append({
            "district_id":      district_id,
            "candidate_id":     candidate_id,
            "election_year":    ELECTION_YEAR,
            "election_type":    ELECTION_TYPE,
            "votes":            int(votes_raw) if pd.notna(votes_raw) else None,
            "percentage":       float(pct_raw) if pct_raw and pd.notna(pct_raw) else None,
            "won":              winner_raw in ("yes", "true", "1", "winner"),
            "total_votes_cast": total_votes_by_contest.get(office),
            "source_url":       SOS_URL or None,
        })

    if results_to_insert:
        supabase.table("pol_election_results").insert(results_to_insert).execute()
        print(f"Inserted {len(results_to_insert)} election result rows.")
    else:
        print("No results to insert — check your CSV column names.")

    print("Done.")


if __name__ == "__main__":
    main()
