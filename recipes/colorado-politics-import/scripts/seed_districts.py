"""
seed_districts.py
-----------------
Seeds all Colorado political districts into the co_districts table:
  - 8 US Congressional districts
  - 35 State Senate districts
  - 65 State House districts
  - 64 Counties (as county-level districts)

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    python seed_districts.py

Requirements:
    pip install supabase python-dotenv
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    sys.exit("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ---------------------------------------------------------------------------
# Congressional Districts
# ---------------------------------------------------------------------------
CONGRESSIONAL_DISTRICTS = [
    {"district_number": "CD-1",  "name": "Colorado's 1st Congressional District",  "notable_cities": ["Denver"]},
    {"district_number": "CD-2",  "name": "Colorado's 2nd Congressional District",  "notable_cities": ["Boulder", "Fort Collins", "Steamboat Springs"]},
    {"district_number": "CD-3",  "name": "Colorado's 3rd Congressional District",  "notable_cities": ["Grand Junction", "Pueblo", "Durango"]},
    {"district_number": "CD-4",  "name": "Colorado's 4th Congressional District",  "notable_cities": ["Greeley", "Colorado Springs (east)", "Pueblo (east)"]},
    {"district_number": "CD-5",  "name": "Colorado's 5th Congressional District",  "notable_cities": ["Colorado Springs", "Woodland Park"]},
    {"district_number": "CD-6",  "name": "Colorado's 6th Congressional District",  "notable_cities": ["Aurora", "Centennial", "Highlands Ranch"]},
    {"district_number": "CD-7",  "name": "Colorado's 7th Congressional District",  "notable_cities": ["Lakewood", "Jefferson County", "Adams County"]},
    {"district_number": "CD-8",  "name": "Colorado's 8th Congressional District",  "notable_cities": ["Greeley", "Brighton", "Commerce City"]},
]

# ---------------------------------------------------------------------------
# Colorado Counties
# ---------------------------------------------------------------------------
COLORADO_COUNTIES = [
    "Adams", "Alamosa", "Arapahoe", "Archuleta", "Baca", "Bent", "Boulder",
    "Broomfield", "Chaffee", "Cheyenne", "Clear Creek", "Conejos", "Costilla",
    "Crowley", "Custer", "Delta", "Denver", "Dolores", "Douglas", "Eagle",
    "El Paso", "Elbert", "Fremont", "Garfield", "Gilpin", "Grand", "Gunnison",
    "Hinsdale", "Huerfano", "Jackson", "Jefferson", "Kiowa", "Kit Carson",
    "La Plata", "Lake", "Larimer", "Las Animas", "Lincoln", "Logan", "Mesa",
    "Mineral", "Moffat", "Montezuma", "Montrose", "Morgan", "Otero", "Ouray",
    "Park", "Phillips", "Pitkin", "Prowers", "Pueblo", "Rio Blanco", "Rio Grande",
    "Routt", "Saguache", "San Juan", "San Miguel", "Sedgwick", "Summit",
    "Teller", "Washington", "Weld", "Yuma"
]


def build_state_districts(district_type: str, prefix: str, count: int) -> list[dict]:
    return [
        {
            "district_number": f"{prefix}-{i}",
            "name": f"Colorado {district_type} District {i}",
            "notable_cities": [],
        }
        for i in range(1, count + 1)
    ]


def upsert_districts(records: list[dict], district_type: str) -> None:
    rows = [
        {
            "name": r["name"],
            "type": district_type,
            "district_number": r["district_number"],
            "notable_cities": r.get("notable_cities", []),
        }
        for r in records
    ]
    result = supabase.table("co_districts").upsert(rows, on_conflict="name").execute()
    print(f"  Upserted {len(rows)} {district_type} districts.")


def main() -> None:
    print("Seeding Colorado districts...")

    print("→ Congressional districts")
    upsert_districts(CONGRESSIONAL_DISTRICTS, "congressional")

    print("→ State Senate districts")
    upsert_districts(build_state_districts("State Senate", "SD", 35), "state_senate")

    print("→ State House districts")
    upsert_districts(build_state_districts("State House", "HD", 65), "state_house")

    print("→ Counties")
    county_records = [
        {"name": f"{c} County", "district_number": c, "notable_cities": []}
        for c in COLORADO_COUNTIES
    ]
    upsert_districts(county_records, "county")

    print("Done. All Colorado districts seeded.")


if __name__ == "__main__":
    main()
