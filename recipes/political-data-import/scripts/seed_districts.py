"""
seed_districts.py
-----------------
Seeds political districts into the pol_districts table for a target state.

By default seeds Colorado (CO) as an example. Override via environment variables
to seed any other US state.

Environment variables:
    STATE_NAME   — Full state name used in district labels (default: Colorado)
    STATE_ABBR   — Two-letter abbreviation, unused here but read for consistency
    CD_COUNT     — Number of US Congressional districts (default: 8 for Colorado)
    SD_COUNT     — Number of State Senate districts (default: 35 for Colorado)
    HD_COUNT     — Number of State House districts (default: 65 for Colorado)
    COUNTIES     — Comma-separated list of county names (default: Colorado counties)

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    python seed_districts.py

    # Different state example:
    STATE_NAME=Texas CD_COUNT=38 SD_COUNT=31 HD_COUNT=150 \
    python seed_districts.py

Requirements:
    pip install supabase python-dotenv
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL         = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    sys.exit("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

STATE_NAME = os.environ.get("STATE_NAME", "Colorado")
CD_COUNT   = int(os.environ.get("CD_COUNT", "8"))
SD_COUNT   = int(os.environ.get("SD_COUNT", "35"))
HD_COUNT   = int(os.environ.get("HD_COUNT", "65"))

# Default to Colorado counties; override with COUNTIES env var (comma-separated)
_DEFAULT_COUNTIES = (
    "Adams,Alamosa,Arapahoe,Archuleta,Baca,Bent,Boulder,Broomfield,Chaffee,"
    "Cheyenne,Clear Creek,Conejos,Costilla,Crowley,Custer,Delta,Denver,Dolores,"
    "Douglas,Eagle,El Paso,Elbert,Fremont,Garfield,Gilpin,Grand,Gunnison,"
    "Hinsdale,Huerfano,Jackson,Jefferson,Kiowa,Kit Carson,La Plata,Lake,Larimer,"
    "Las Animas,Lincoln,Logan,Mesa,Mineral,Moffat,Montezuma,Montrose,Morgan,"
    "Otero,Ouray,Park,Phillips,Pitkin,Prowers,Pueblo,Rio Blanco,Rio Grande,"
    "Routt,Saguache,San Juan,San Miguel,Sedgwick,Summit,Teller,Washington,Weld,Yuma"
)
COUNTIES = [c.strip() for c in os.environ.get("COUNTIES", _DEFAULT_COUNTIES).split(",") if c.strip()]


def build_numbered_districts(district_type: str, prefix: str, count: int) -> list[dict]:
    return [
        {
            "district_number": f"{prefix}-{i}",
            "name": f"{STATE_NAME} {district_type} District {i}",
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
    supabase.table("pol_districts").upsert(rows, on_conflict="name").execute()
    print(f"  Upserted {len(rows)} {district_type} districts.")


def main() -> None:
    print(f"Seeding {STATE_NAME} districts...")

    print("→ Congressional districts")
    upsert_districts(
        [{"district_number": f"CD-{i}", "name": f"{STATE_NAME}'s {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'} Congressional District", "notable_cities": []}
         for i in range(1, CD_COUNT + 1)],
        "congressional",
    )

    print("→ State Senate districts")
    upsert_districts(build_numbered_districts("State Senate", "SD", SD_COUNT), "state_senate")

    print("→ State House districts")
    upsert_districts(build_numbered_districts("State House", "HD", HD_COUNT), "state_house")

    print("→ Counties")
    county_records = [
        {"name": f"{c} County", "district_number": c, "notable_cities": []}
        for c in COUNTIES
    ]
    upsert_districts(county_records, "county")

    print(f"Done. {STATE_NAME} districts seeded.")


if __name__ == "__main__":
    main()
