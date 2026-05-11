"""
seed_states.py
--------------
Seeds all 50 US states into the sl_states table.

Usage:
    SUPABASE_URL=https://xxx.supabase.co \
    SUPABASE_SERVICE_KEY=your-service-role-key \
    python seed_states.py

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

STATES = [
    ("Alabama",        "AL", "Southeast"),
    ("Alaska",         "AK", "West"),
    ("Arizona",        "AZ", "Southwest"),
    ("Arkansas",       "AR", "Southeast"),
    ("California",     "CA", "West"),
    ("Colorado",       "CO", "West"),
    ("Connecticut",    "CT", "Northeast"),
    ("Delaware",       "DE", "Northeast"),
    ("Florida",        "FL", "Southeast"),
    ("Georgia",        "GA", "Southeast"),
    ("Hawaii",         "HI", "West"),
    ("Idaho",          "ID", "West"),
    ("Illinois",       "IL", "Midwest"),
    ("Indiana",        "IN", "Midwest"),
    ("Iowa",           "IA", "Midwest"),
    ("Kansas",         "KS", "Midwest"),
    ("Kentucky",       "KY", "Southeast"),
    ("Louisiana",      "LA", "Southeast"),
    ("Maine",          "ME", "Northeast"),
    ("Maryland",       "MD", "Northeast"),
    ("Massachusetts",  "MA", "Northeast"),
    ("Michigan",       "MI", "Midwest"),
    ("Minnesota",      "MN", "Midwest"),
    ("Mississippi",    "MS", "Southeast"),
    ("Missouri",       "MO", "Midwest"),
    ("Montana",        "MT", "West"),
    ("Nebraska",       "NE", "Midwest"),
    ("Nevada",         "NV", "West"),
    ("New Hampshire",  "NH", "Northeast"),
    ("New Jersey",     "NJ", "Northeast"),
    ("New Mexico",     "NM", "Southwest"),
    ("New York",       "NY", "Northeast"),
    ("North Carolina", "NC", "Southeast"),
    ("North Dakota",   "ND", "Midwest"),
    ("Ohio",           "OH", "Midwest"),
    ("Oklahoma",       "OK", "Southwest"),
    ("Oregon",         "OR", "West"),
    ("Pennsylvania",   "PA", "Northeast"),
    ("Rhode Island",   "RI", "Northeast"),
    ("South Carolina", "SC", "Southeast"),
    ("South Dakota",   "SD", "Midwest"),
    ("Tennessee",      "TN", "Southeast"),
    ("Texas",          "TX", "Southwest"),
    ("Utah",           "UT", "West"),
    ("Vermont",        "VT", "Northeast"),
    ("Virginia",       "VA", "Southeast"),
    ("Washington",     "WA", "West"),
    ("West Virginia",  "WV", "Southeast"),
    ("Wisconsin",      "WI", "Midwest"),
    ("Wyoming",        "WY", "West"),
]


def main() -> None:
    print("Seeding all 50 US states...")
    rows = [
        {"name": name, "abbreviation": abbr, "region": region}
        for name, abbr, region in STATES
    ]
    supabase.table("sl_states").upsert(rows, on_conflict="abbreviation").execute()
    print(f"Done. Seeded {len(rows)} states.")


if __name__ == "__main__":
    main()
