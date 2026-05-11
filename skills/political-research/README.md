# Political Research Skill

A reusable skill pack that turns Claude into a political research assistant for any US state or jurisdiction. Give it a candidate name, a district number, or a question about a race — and it knows how to query your Open Brain data, structure its answer, and offer to save findings back to memory.

## What it does

Provides Claude with structured instructions for:
- **Candidate lookup** — bio, party, positions, electoral history, campaign finance
- **District analysis** — demographics, partisan lean, all current candidates, competitive assessment
- **Race comparison** — side-by-side candidate comparison in the same district
- **Campaign finance review** — fundraising totals, spending, top donors
- **Competitive race identification** — surfaces battleground districts by margin analysis
- **Research note capture** — saves findings back to Open Brain thoughts with proper tags

## Prerequisites

- Working Open Brain setup (Supabase + pgvector + MCP connected)
- [Political Research Schema](../../schemas/political-research/) applied to your database
- [Political Data Import](../../recipes/political-data-import/) recipe run at least once to populate data

## Installation

**Supported Clients:** Claude Code, Claude Desktop, Cursor, or any AI client that supports custom skills/instructions.

![Step 1](https://img.shields.io/badge/Step_1-Copy_the_Skill_File-2E7D32?style=for-the-badge)

Copy `SKILL.md` into your AI client's skills directory:

- **Claude Code:** Place in `.claude/skills/political-research.md` at your project root, or in `~/.claude/skills/` for global access
- **Cursor:** Add the contents to your `.cursorrules` or system prompt
- **Claude Desktop:** Paste the contents into a Project instruction

✅ **Done when:** Your AI client loads the file without errors.

![Step 2](https://img.shields.io/badge/Step_2-Verify_Data_Is_Populated-2E7D32?style=for-the-badge)

Ask Claude:
```
How many political districts are in my database?
```
It should query `pol_districts` and return a count. If it returns zero, run the import recipe first.

✅ **Done when:** Claude returns a non-zero district count.

![Step 3](https://img.shields.io/badge/Step_3-Run_a_Test_Query-2E7D32?style=for-the-badge)

Try a sample research prompt:
```
Research the 2nd Congressional District — who are the current candidates,
what's the partisan lean, and what do the demographics look like?
```

✅ **Done when:** Claude returns a formatted district summary with candidates, demographics, and competitive assessment.

## Trigger Conditions

This skill activates when you:
- Ask about a specific candidate or elected official
- Ask about a political district ("who's running in HD-18?")
- Ask to compare candidates ("compare the candidates in CD-8")
- Ask about campaign finance ("who's out-raising whom in SD-22?")
- Ask which races are competitive or worth watching
- Say "research [candidate or district]"

## Expected Outcome

Claude responds with structured, sourced summaries for candidates and districts — and offers to save research findings back to Open Brain at the end of each session.

## Troubleshooting

**Claude says it can't query the database**
Make sure your Open Brain MCP server is connected and Claude has tool access. In Claude Desktop, check Settings → Connectors.

**Candidate or district not found**
The data tables may be empty or partially populated. Run `seed_districts.py` and at least one import script from the [Political Data Import](../../recipes/political-data-import/) recipe.

**Demographic data shows as null**
Run `import_census_demographics.py` from the import recipe. This is a separate step from seeding districts.

**Campaign finance shows as null**
Run `import_opensecrets.py`. You'll need a free OpenSecrets API key at opensecrets.org/api.
