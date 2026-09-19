# Project Lesson Context

Before generating a new direction, bring the relevant human lessons back into
view. This read-only tool searches one project's existing accepted and rejected
lesson files. It retains whole sections, including evidence, exceptions, and
scope, and always includes that project's unresolved questions.

It works directly with the current Artistic Director memory files. No database,
embeddings, indexing service, model, or new memory format is needed.

## Requirements

An Open Brain / Second_Brain project and Python 3.11+ (standard library only).
The three fixed inputs are `memory/accepted-lessons.md`,
`memory/rejected-lessons.md`, and `memory/open-questions.md` under the project.
Missing sources are reported explicitly. Nothing is created or changed.

## 1. Describe the current brief

From the repository root:

```bash
python recipes/lesson-context/context.py --project projects/artistic-director --brief "An organic logo with a negative space reveal and technology in the product"
```

Output is JSON with separate accepted, rejected, and unresolved lists. Every
candidate carries a relative source path, inclusive line range, full section
text, and the query terms that matched. Source records include SHA-256 hashes.

**Done when:** you can trace each candidate to its original memory section.

## 2. Decide applicability with the human

Read the conditions and exceptions before using a lesson. A match means only
that words overlap. It does not show that a lesson applies, that acceptance
was authenticated, or that project-local knowledge is globally reusable.

Review rejected approaches for their constructive alternatives. Unresolved
questions appear even without a keyword match so uncertainty is not silently
filtered away. If a source is missing, recover it before claiming memory was
fully consulted. No match does not mean no applicable lesson exists.

Use `--limit 5` to inspect more matches (1–10 per accepted/rejected category).
The output reports omitted matches. Questions are not ranked or truncated.

**Done when:** the human has selected applicable lessons and kept unresolved
questions visible. The tool never writes or promotes a lesson.

## Matching and limits

Matching uses case-folded Unicode words, removes a small list of English
function words, and sorts by the number of distinct matching words. Ties use
source order. There is no stemming, synonym expansion, or semantic inference.
Try alternate vocabulary when a relevant lesson does not appear.

Level-two Markdown headings define sections. A file without them is one
document. Introductory text before the first level-two heading is not a lesson;
read the full source for its preamble. Relative source paths and hashes refer
to the current files, not an immutable repository commit. Line endings are
normalized in section text; wording is preserved.

Each source is limited to 128 KiB and must be UTF-8 text. Memory symlinks and
junctions are rejected. Output may include private project context: keep it
inside the project's boundary. Brief text supplied on the command line may be
recorded in shell history; use non-sensitive search terms.

## Verification

```bash
python -m unittest discover -s recipes/lesson-context -p "test_*.py" -v
```

Tests cover qualifiers, references, rejected alternatives, unmatched questions,
missing files, deterministic ranking, Unicode, hashes, and bounds. This local
repository companion does not exercise a live Supabase instance.

## Provenance

Based on [Lesson Promotion](../../docs/second-brain/lesson-promotion.md) and the
existing Artistic Director memory, not a replacement for human acceptance.
Second_Brain builds on [Open Brain](https://github.com/NateBJones-Projects/OB1)
by Nate B. Jones: [newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Original code authored with AI assistance by Mira.
