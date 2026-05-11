# State Legislation Import

Four scripts that populate your Open Brain database with legislation from all 50 US states, news coverage reporting on real-world outcomes, and Claude-generated impact assessments. Run them in order and your database will be ready for the [State Legislation Research skill](../../skills/state-legislation-research/).

## What it does

| Script | Source | What it imports |
|--------|--------|-----------------|
| `seed_states.py` | Built-in | All 50 states with region grouping |
| `import_legiscan.py` | LegiScan API | Bills, status, sponsors, session year — filtered to healthcare, housing, jobs, and 7 other topics |
| `import_news.py` | NewsAPI | News articles about state legislation linked to bills |
| `generate_assessments.py` | Claude API | Positive/negative/mixed impact verdicts with evidence citations |

## Prerequisites

- Working Open Brain setup
- [State Legislation Schema](../../schemas/state-legislation/) applied to your database
- Python 3.10+
- Free API keys for LegiScan, NewsAPI, and Anthropic (details in each step)

## Step-by-step instructions

![Step 1](https://img.shields.io/badge/Step_1-Apply_the_Schema-4A148C?style=for-the-badge)

Apply the [State Legislation Schema](../../schemas/state-legislation/) to your Supabase database first.

✅ **Done when:** All `sl_*` tables exist in Supabase, including the pre-seeded `sl_topics`.

![Step 2](https://img.shields.io/badge/Step_2-Install_Dependencies-4A148C?style=for-the-badge)

```bash
pip install supabase python-dotenv requests anthropic
```

✅ **Done when:** No install errors.

![Step 3](https://img.shields.io/badge/Step_3-Set_Environment_Variables-4A148C?style=for-the-badge)

Create a `.env` file in the `scripts/` directory (do not commit this file):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

LEGISCAN_API_KEY=your-legiscan-key
NEWS_API_KEY=your-newsapi-key
ANTHROPIC_API_KEY=your-anthropic-key
```

> [!IMPORTANT]
> Use the **service role key** from Supabase — not the anon key.

✅ **Done when:** `.env` is saved and variables are accessible.

![Step 4](https://img.shields.io/badge/Step_4-Seed_States-4A148C?style=for-the-badge)

```bash
cd scripts
python seed_states.py
```

✅ **Done when:** `sl_states` has 50 rows in Supabase.

![Step 5](https://img.shields.io/badge/Step_5-Import_Legislation_(LegiScan)-4A148C?style=for-the-badge)

Get a free key at [legiscan.com/user/register](https://legiscan.com/user/register), then:

```bash
python import_legiscan.py
```

> [!NOTE]
> The free LegiScan tier allows 500 API pulls/day. The script fetches all 50 state sessions and filters to topic-relevant bills only, minimizing API usage. For a full initial load, you may need to run it over 2-3 days.

✅ **Done when:** `sl_legislation` has bills and `sl_legislation_topics` has topic links.

![Step 6](https://img.shields.io/badge/Step_6-Import_News_Coverage-4A148C?style=for-the-badge)

Get a free key at [newsapi.org/register](https://newsapi.org/register), then:

```bash
python import_news.py
```

✅ **Done when:** `sl_news_sources` has articles linked to legislation.

![Step 7](https://img.shields.io/badge/Step_7-Generate_Impact_Assessments-4A148C?style=for-the-badge)

This step uses Claude to evaluate each signed/passed bill and produce a positive/negative/mixed verdict with evidence.

```bash
python generate_assessments.py
```

To control costs, limit the number of bills assessed per run:
```bash
MAX_BILLS=25 python generate_assessments.py
```

> [!NOTE]
> Assessments are generated only once per bill. Re-running is safe — already-assessed bills are skipped automatically.

✅ **Done when:** `sl_impact_assessments` has verdict rows for your legislation.

## Expected outcome

After all scripts complete:
- **50 states** seeded with regions
- **Bills across all 50 states** filtered to your 10 topic areas
- **News articles** linked to legislation with sentiment tags
- **Impact assessments** with positive/negative/mixed verdicts and evidence citations

Ready for the [State Legislation Research skill](../../skills/state-legislation-research/).

## Troubleshooting

**LegiScan returns no sessions**
Your API key may not be activated yet. Check your email for a confirmation link after registering.

**`import_legiscan.py` runs out of API calls**
You've hit the 500/day free tier limit. The script is resumable — bills already imported are skipped on re-run. Continue the next day.

**NewsAPI returns no articles**
The free tier only allows articles from the past month. For older coverage, consider a paid plan or supplement with manual article entry via the Supabase Table Editor.

**Claude assessments say "unclear" for everything**
This usually means there's no news coverage yet for those bills. Run `import_news.py` first, then re-run `generate_assessments.py`.

**Bills not matching topics**
The topic keyword matching in `import_legiscan.py` is keyword-based. You can add keywords to the `TOPIC_KEYWORDS` dictionary to improve coverage for niche legislation.
