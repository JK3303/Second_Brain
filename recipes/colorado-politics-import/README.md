# Colorado Politics Import

A set of Python import scripts that populate your Open Brain database with Colorado political data from four public sources: the Colorado Secretary of State, Ballotpedia, OpenSecrets, and the US Census Bureau. Run them in order and your structured tables will be ready for the [Colorado Politics Research skill](../../skills/colorado-politics-research/).

## What it does

Provides four import scripts plus a district seeder:

| Script | Source | What it imports |
|--------|--------|-----------------|
| `seed_districts.py` | Built-in | All CO congressional, state senate/house, and county districts |
| `import_sos_results.py` | CO Secretary of State | Election results from SOS CSV exports |
| `import_ballotpedia.py` | Ballotpedia API | Candidate profiles, bios, party, office, social media |
| `import_opensecrets.py` | OpenSecrets API | Campaign finance: raised, spent, cash on hand, top donors |
| `import_census_demographics.py` | US Census ACS | Population, income, racial/ethnic breakdown by district |

## Prerequisites

- Working Open Brain setup (Supabase + pgvector)
- [Colorado Politics Schema](../../schemas/colorado-politics/) applied to your database
- Python 3.10+
- API keys (details in each step below) — all are **free**

## Step-by-step instructions

![Step 1](https://img.shields.io/badge/Step_1-Apply_the_Schema-1565C0?style=for-the-badge)

If you haven't already, apply the Colorado Politics Schema to your Supabase database. See [schemas/colorado-politics/](../../schemas/colorado-politics/).

✅ **Done when:** `co_districts`, `co_candidates`, `co_election_results`, `co_campaign_finance`, and `co_research_notes` tables exist in Supabase.

![Step 2](https://img.shields.io/badge/Step_2-Install_Dependencies-1565C0?style=for-the-badge)

```bash
pip install supabase python-dotenv pandas requests
```

✅ **Done when:** No install errors.

![Step 3](https://img.shields.io/badge/Step_3-Set_Environment_Variables-1565C0?style=for-the-badge)

Create a `.env` file in the `scripts/` directory (never commit this file):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Optional — only needed for the scripts that use them
BALLOTPEDIA_API_KEY=your-ballotpedia-key
OPENSECRETS_API_KEY=your-opensecrets-key
CENSUS_API_KEY=your-census-key
```

> [!IMPORTANT]
> Use your **service role key** (not the anon key) — it has write permissions to the tables.

✅ **Done when:** Variables are set and `.env` is saved.

![Step 4](https://img.shields.io/badge/Step_4-Seed_Districts-1565C0?style=for-the-badge)

Run this first — it creates all 172 Colorado districts (8 congressional + 35 senate + 65 house + 64 counties):

```bash
cd scripts
python seed_districts.py
```

✅ **Done when:** `co_districts` table has 172+ rows in Supabase.

![Step 5](https://img.shields.io/badge/Step_5-Import_Candidates_(Ballotpedia)-1565C0?style=for-the-badge)

Get a free API key at [ballotpedia.org/API-documentation](https://ballotpedia.org/API-documentation), then:

```bash
python import_ballotpedia.py
```

✅ **Done when:** `co_candidates` table is populated with active Colorado candidates.

![Step 6](https://img.shields.io/badge/Step_6-Import_Election_Results_(SOS)-1565C0?style=for-the-badge)

**6.1 — Download a results CSV from the SOS:**

Go to [sos.state.co.us/pubs/elections/Results](https://www.sos.state.co.us/pubs/elections/Results/) and download a CSV for your target election year.

**6.2 — Run the import:**

```bash
RESULTS_CSV_PATH=/path/to/results.csv \
ELECTION_YEAR=2024 \
ELECTION_TYPE=general \
python import_sos_results.py
```

> [!NOTE]
> The SOS CSV column names may vary by election year. If the script warns about missing columns, open the CSV and update the column mapping at the top of `import_sos_results.py`.

✅ **Done when:** `co_election_results` has rows for your target year.

![Step 7](https://img.shields.io/badge/Step_7-Import_Campaign_Finance_(OpenSecrets)-1565C0?style=for-the-badge)

Get a free key at [opensecrets.org/api](https://www.opensecrets.org/api/admin/index.php?function=signup), then:

```bash
CYCLE_YEAR=2024 python import_opensecrets.py
```

> [!NOTE]
> OpenSecrets free tier covers federal candidates only (congressional + statewide). State legislative candidates require a paid plan.

✅ **Done when:** `co_campaign_finance` has rows for your target cycle.

![Step 8](https://img.shields.io/badge/Step_8-Import_Demographics_(Census)-1565C0?style=for-the-badge)

Get a free Census API key at [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html), then:

```bash
python import_census_demographics.py
```

✅ **Done when:** `co_districts.demographics` is populated with population, income, and racial/ethnic data.

## Expected outcome

After all scripts complete:

- **172+ districts** seeded with names and types
- **Active Colorado candidates** imported with party, office, bio, and social links
- **Election results** for your chosen year with vote counts and percentages
- **Campaign finance** for federal candidates with raised/spent/top donors
- **District demographics** with ACS population and income data

You're ready to use the [Colorado Politics Research skill](../../skills/colorado-politics-research/).

## Troubleshooting

**`ERROR: Set SUPABASE_URL...`**
Your `.env` file isn't loading. Make sure it's in the same directory as the scripts, or export variables directly in your shell.

**Ballotpedia returns 0 candidates**
The free-tier API may require approval. Check your API key status at the Ballotpedia developer portal.

**OpenSecrets: candidate not found in co_candidates**
OpenSecrets uses its own name format. Run `import_ballotpedia.py` first, then rerun OpenSecrets. If mismatches persist, manually add the candidate via Supabase Table Editor.

**Census returns -666666666 for some values**
This is the Census Bureau's null sentinel. The script filters these out automatically, but if you see them in your data, run the script again after a fresh `seed_districts.py`.

**SOS CSV column names don't match**
Open the downloaded CSV in Excel or a text editor and check the header row. Update the column references near the top of `import_sos_results.py` to match.
