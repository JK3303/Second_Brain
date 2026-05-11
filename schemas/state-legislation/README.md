# State Legislation Schema

Adds seven structured tables to your Open Brain database for tracking legislation across all 50 US states. Covers bill status, topic categorization (healthcare, housing, jobs, and more), Claude-generated impact assessments, linked news sources, and research notes tied back to your Open Brain thoughts.

## What it does

Creates a relational layer for multi-state legislative research. The schema is designed to answer questions like:
- "Which states have passed housing reform bills in the last 3 years, and did they work?"
- "What healthcare legislation is currently being considered, and what does the coverage say?"
- "What are the best job-growth bills that have passed recently, and what were the outcomes?"

## Prerequisites

- Working Open Brain setup (Supabase project with the `thoughts` table)
- Access to your Supabase SQL Editor or `psql`

## Step-by-step instructions

![Step 1](https://img.shields.io/badge/Step_1-Open_the_SQL_Editor-4A148C?style=for-the-badge)

In your Supabase dashboard, go to **SQL Editor → New Query**.

![Step 2](https://img.shields.io/badge/Step_2-Run_the_Schema-4A148C?style=for-the-badge)

Copy and paste the contents of `schema.sql` into the editor and click **Run**.

<details>
<summary>📋 <strong>SQL: Tables created (click to expand)</strong></summary>

| Table | Purpose |
|---|---|
| `sl_states` | All 50 US states with region grouping |
| `sl_topics` | Topic categories (healthcare, housing, jobs, etc.) — pre-seeded |
| `sl_legislation` | Bills with status, session year, sponsor, and source links |
| `sl_legislation_topics` | Many-to-many join between bills and topics |
| `sl_impact_assessments` | Positive/negative/mixed verdicts with evidence links |
| `sl_news_sources` | News articles linked to specific legislation |
| `sl_research_notes` | Joins Open Brain thoughts to legislative entities |

</details>

✅ **Done when:** All seven tables appear in your Supabase Table Editor, and `sl_topics` is pre-populated with 10 topic categories.

![Step 3](https://img.shields.io/badge/Step_3-Verify_Permissions-4A148C?style=for-the-badge)

The schema includes `GRANT` statements for `service_role`. Confirm by running one of the import scripts from the companion recipe — a successful write confirms permissions are set.

✅ **Done when:** Import scripts can write rows without permission errors.

## Expected outcome

Seven tables ready to receive data, with `sl_topics` pre-seeded with:
`healthcare` · `housing` · `jobs` · `education` · `criminal-justice` · `environment` · `taxes` · `infrastructure` · `immigration` · `voting`

## Troubleshooting

**Error: relation "thoughts" does not exist**
Complete the [Getting Started guide](../../docs/01-getting-started.md) first — the core Open Brain `thoughts` table must exist.

**Error: permission denied**
Re-run the `GRANT` block at the bottom of `schema.sql` in the SQL Editor.

**Topics already exist on re-run**
All inserts use `ON CONFLICT DO NOTHING` — re-running is safe.

**Need to reset completely**
Drop in reverse dependency order:
```sql
DROP TABLE IF EXISTS public.sl_research_notes;
DROP TABLE IF EXISTS public.sl_news_sources;
DROP TABLE IF EXISTS public.sl_impact_assessments;
DROP TABLE IF EXISTS public.sl_legislation_topics;
DROP TABLE IF EXISTS public.sl_legislation;
DROP TABLE IF EXISTS public.sl_topics;
DROP TABLE IF EXISTS public.sl_states;
```
Then re-run `schema.sql`.
