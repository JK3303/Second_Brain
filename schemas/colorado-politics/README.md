# Colorado Politics Schema

Adds five structured tables to your Open Brain database for tracking Colorado political districts, candidates, election results, campaign finance, and research notes — with a foreign key link back to the core `thoughts` table so every research note you capture is also semantically searchable.

## What it does

Creates a relational layer on top of Open Brain specifically for Colorado political research. Structured tables let you run precise queries ("show all active Republican candidates in HD-18") while the `co_research_notes` join table connects those entities back to your Open Brain thoughts for vector search and Claude context.

## Prerequisites

- Working Open Brain setup (Supabase project with the `thoughts` table)
- Access to your Supabase SQL Editor or `psql`

## Step-by-step instructions

![Step 1](https://img.shields.io/badge/Step_1-Open_the_SQL_Editor-1B5E20?style=for-the-badge)

In your Supabase dashboard, go to **SQL Editor → New Query**.

![Step 2](https://img.shields.io/badge/Step_2-Run_the_Schema-1B5E20?style=for-the-badge)

Copy and paste the contents of `schema.sql` into the editor and click **Run**.

<details>
<summary>📋 <strong>SQL: Full schema (click to expand)</strong></summary>

```sql
-- See schema.sql in this folder for the full content
```

</details>

✅ **Done when:** The query returns no errors and you can see `co_districts`, `co_candidates`, `co_election_results`, `co_campaign_finance`, and `co_research_notes` in your Supabase Table Editor.

![Step 3](https://img.shields.io/badge/Step_3-Verify_Permissions-1B5E20?style=for-the-badge)

The schema includes `GRANT` statements for `service_role`. Confirm they ran by checking **Database → Roles** in Supabase — or just proceed to the import recipe and verify writes succeed.

✅ **Done when:** Import scripts in the companion recipe can write rows without permission errors.

## Expected outcome

Five new tables in your Supabase `public` schema:

| Table | Purpose |
|---|---|
| `co_districts` | Congressional, state senate/house, county, and municipal districts |
| `co_candidates` | Candidate profiles with party, office, positions, and sources |
| `co_election_results` | Historical vote counts and percentages by district and year |
| `co_campaign_finance` | Fundraising, spending, and top-donor data by cycle year |
| `co_research_notes` | Join table linking Open Brain thoughts to political entities |

## Troubleshooting

**Error: relation "thoughts" does not exist**
You haven't set up Open Brain yet. Complete the [Getting Started guide](../../docs/01-getting-started.md) first — the `thoughts` table must exist before this schema can reference it.

**Error: permission denied for table co_districts**
The `GRANT` statements at the bottom of `schema.sql` may not have run. Re-run just the `GRANT` block in the SQL Editor.

**Table already exists errors**
All `CREATE TABLE` statements use `IF NOT EXISTS` — re-running the script is safe and idempotent.

**I need to reset and start over**
Drop the tables in reverse dependency order:
```sql
DROP TABLE IF EXISTS public.co_research_notes;
DROP TABLE IF EXISTS public.co_campaign_finance;
DROP TABLE IF EXISTS public.co_election_results;
DROP TABLE IF EXISTS public.co_candidates;
DROP TABLE IF EXISTS public.co_districts;
```
Then re-run `schema.sql`.
