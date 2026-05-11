"""
import_census_demographics.py
-----------------------------
Fetches demographic data from the US Census Bureau API
(American Community Survey 5-year estimates) for Colorado
congressional and state legislative districts, and writes
it into the co_districts.demographics JSONB column.

Free Census API key: https://api.census.gov/data/key_signup.html

Variables fetched (ACS 5-year):
  B01003_001E — Total population
  B19013_001E — Median household income
  B02001_002E — White alone
  B02001_003E — Black or African American alone
  B02001_004E — American Indian and Alaska Native alone
  B02001_005E — Asian alone
  B03003_003E — Hispanic or Latino
  B15003_022E — Bachelor's degree (25+)
  B27001_001E — Health insurance coverage

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    CENSUS_API_KEY=your-key \
    python import_census_demographics.py

Requirements:
    pip install supabase python-dotenv requests
"""

import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
CENSUS_API_KEY       = os.environ.get("CENSUS_API_KEY")

for var in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "CENSUS_API_KEY"):
    if not os.environ.get(var):
        sys.exit(f"ERROR: Set {var} environment variable.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

CENSUS_BASE = "https://api.census.gov/data"
ACS_YEAR    = "2022"  # Most recent stable ACS 5-year
CO_FIPS     = "08"    # Colorado FIPS code

VARIABLES = ",".join([
    "NAME",
    "B01003_001E",   # Total population
    "B19013_001E",   # Median household income
    "B02001_002E",   # White alone
    "B02001_003E",   # Black or African American alone
    "B02001_004E",   # American Indian and Alaska Native alone
    "B02001_005E",   # Asian alone
    "B03003_003E",   # Hispanic or Latino
    "B15003_022E",   # Bachelor's degree (25+)
])

VARIABLE_LABELS = {
    "B01003_001E": "total_population",
    "B19013_001E": "median_household_income",
    "B02001_002E": "pop_white_alone",
    "B02001_003E": "pop_black_alone",
    "B02001_004E": "pop_native_american_alone",
    "B02001_005E": "pop_asian_alone",
    "B03003_003E": "pop_hispanic_latino",
    "B15003_022E": "pop_bachelors_degree_25plus",
}


def fetch_census(geography: str, geo_filter: str) -> list[dict]:
    """Fetch ACS 5-year data for a geography type in Colorado."""
    url = f"{CENSUS_BASE}/{ACS_YEAR}/acs/acs5"
    params = {
        "get": VARIABLES,
        "for": geography,
        "in": f"state:{CO_FIPS}",
        "key": CENSUS_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        rows = r.json()
        headers = rows[0]
        return [dict(zip(headers, row)) for row in rows[1:]]
    except requests.RequestException as e:
        print(f"  WARNING: Census fetch failed for {geography} — {e}")
        return []


def build_demographics(row: dict) -> dict:
    result = {}
    total_pop = int(row.get("B01003_001E", 0) or 0)
    for var_code, label in VARIABLE_LABELS.items():
        raw = row.get(var_code)
        try:
            val = int(raw) if raw and int(raw) >= 0 else None
        except (ValueError, TypeError):
            val = None
        result[label] = val

    # Compute percentage breakdowns if total_pop > 0
    if total_pop > 0:
        for pop_key in ("pop_white_alone", "pop_black_alone", "pop_native_american_alone",
                        "pop_asian_alone", "pop_hispanic_latino"):
            raw_val = result.get(pop_key)
            if raw_val is not None:
                result[f"{pop_key}_pct"] = round(raw_val / total_pop * 100, 1)

    result["acs_year"] = ACS_YEAR
    return result


def update_district_demographics(district_type: str, district_number_prefix: str,
                                  census_rows: list[dict], number_field: str) -> int:
    updated = 0
    for row in census_rows:
        raw_number = row.get(number_field, "").lstrip("0") or "0"
        district_number = f"{district_number_prefix}{raw_number}"
        demographics = build_demographics(row)

        result = (
            supabase.table("co_districts")
            .update({"demographics": demographics})
            .eq("type", district_type)
            .eq("district_number", district_number)
            .execute()
        )
        if result.data:
            updated += 1
    return updated


def main() -> None:
    print(f"Importing Census ACS {ACS_YEAR} demographics for Colorado districts...")

    # Congressional districts
    print("  → Congressional districts")
    rows = fetch_census("congressional district:*", f"state:{CO_FIPS}")
    n = update_district_demographics("congressional", "CD-", rows, "congressional district")
    print(f"    Updated {n} congressional districts.")

    # State Senate districts
    print("  → State Senate districts")
    rows = fetch_census("state legislative district (upper chamber):*", f"state:{CO_FIPS}")
    n = update_district_demographics("state_senate", "SD-", rows, "state legislative district (upper chamber)")
    print(f"    Updated {n} state senate districts.")

    # State House districts
    print("  → State House districts")
    rows = fetch_census("state legislative district (lower chamber):*", f"state:{CO_FIPS}")
    n = update_district_demographics("state_house", "HD-", rows, "state legislative district (lower chamber)")
    print(f"    Updated {n} state house districts.")

    # Counties
    print("  → Counties")
    rows = fetch_census("county:*", f"state:{CO_FIPS}")
    updated = 0
    for row in rows:
        county_name = row.get("NAME", "").replace(", Colorado", "").strip()
        demographics = build_demographics(row)
        result = (
            supabase.table("co_districts")
            .update({"demographics": demographics})
            .eq("type", "county")
            .ilike("name", f"%{county_name}%")
            .execute()
        )
        if result.data:
            updated += 1
    print(f"    Updated {updated} counties.")

    print("Done. Census demographics imported.")


if __name__ == "__main__":
    main()
