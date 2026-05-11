# State Legislation Research Skill

A reusable skill pack that turns Claude into a nonpartisan state legislative research analyst. Ask it to find the best healthcare laws passed in the last three years, compare how states have tackled housing affordability, or evaluate whether a specific bill actually worked — and it knows how to query your Open Brain data, weigh the evidence, and give you a sourced answer.

## What it does

Provides Claude with structured instructions for:
- **Bill lookup** — find legislation by state, topic, status, or keyword
- **Impact evaluation** — positive / negative / mixed verdicts based on news and outcomes data
- **Cross-state comparison** — side-by-side table of how different states approached the same problem
- **Best ideas synthesis** — ranked list of the most effective legislation in a topic area with evidence
- **Trend identification** — which legislative approaches are spreading and which are stalling
- **Research note capture** — saves findings back to Open Brain thoughts with proper tags

## Prerequisites

- Working Open Brain setup (Supabase + pgvector + MCP connected)
- [State Legislation Schema](../../schemas/state-legislation/) applied to your database
- [State Legislation Import](../../recipes/state-legislation-import/) recipe run at least once

## Installation

**Supported Clients:** Claude Code, Claude Desktop, Cursor, or any AI client that supports custom skills/instructions.

![Step 1](https://img.shields.io/badge/Step_1-Copy_the_Skill_File-4A148C?style=for-the-badge)

Copy `SKILL.md` into your AI client's skills directory:

- **Claude Code:** Place in `.claude/skills/state-legislation-research.md` at your project root, or `~/.claude/skills/` for global access
- **Cursor:** Add the contents to your `.cursorrules` or system prompt
- **Claude Desktop:** Paste the contents into a Project instruction

✅ **Done when:** Your AI client loads the file without errors.

![Step 2](https://img.shields.io/badge/Step_2-Verify_Data_Is_Populated-4A148C?style=for-the-badge)

Ask Claude:
```
How many pieces of legislation are in my database, and which topics are covered?
```

✅ **Done when:** Claude returns a non-zero count with topic breakdown.

![Step 3](https://img.shields.io/badge/Step_3-Run_a_Test_Query-4A148C?style=for-the-badge)

Try a sample research prompt:
```
What are the best housing affordability bills passed in the last 3 years?
Show me which states passed them and whether they worked.
```

✅ **Done when:** Claude returns a ranked list with states, verdicts, and cited evidence.

## Trigger Conditions

This skill activates when you:
- Ask about legislation in a specific state or across multiple states
- Ask "what states have passed X type of law"
- Ask which legislative ideas have worked or failed
- Ask to compare how states are handling a policy area
- Ask for the "best" or "most effective" legislation on a topic
- Say "research [topic] legislation", "find the best [policy] laws", "compare states on [issue]"
- Ask about healthcare, housing, jobs, education, criminal justice, environment, taxes, infrastructure, immigration, or voting

## Expected Outcome

Claude responds with structured, evidence-based analyses — bill summaries, cross-state comparison tables, and ranked best-ideas reports — and offers to save research findings back to Open Brain at the end of each session.

## Troubleshooting

**Claude says it can't query the database**
Make sure your Open Brain MCP server is connected. In Claude Desktop, check Settings → Connectors.

**No legislation found for a topic**
Run `import_legiscan.py` from the import recipe. The database may be empty or only partially populated.

**Impact assessments are missing**
Run `generate_assessments.py` from the import recipe. This requires an Anthropic API key and targets bills with `signed` or `passed` status.

**News articles not linked to bills**
The `import_news.py` script uses keyword matching to link articles — some bills may not match. You can manually link articles via the Supabase Table Editor by inserting a row into `sl_news_sources` with the correct `legislation_id`.
