# Art: coherent creative practice and verified production

## What It Does

Art supports artistic encounter, interpretation, creation, critique, and deliberate
revision across media. It preserves accepted visual references, exact wording,
product features, and series identity, then checks the actual destination before
claiming production or delivery is complete.

## Supported Clients

Codex, Claude Code, and Cursor can load these plain-text instructions. Available
image, typography, presentation, and inspection tools differ by client; installing
the skill supplies methods, not those tools. Live client demonstrations are pending.

## Prerequisites

- An existing Open Brain workspace, following the [setup guide](../../docs/01-getting-started.md).
- A client that supports reusable skills or loading Markdown instructions.
- Authorized source assets and tools suitable for the requested medium.

This contribution follows Open Brain's metadata convention. The Art methods do
not call its database or MCP tools and do not require Music or Core integrations.

## Installation

1. Copy this entire folder, including `references/`, into the chosen client's project skill directory: `.agents/skills/art/` for Codex or `.claude/skills/art/` for Claude Code. For Cursor, load `SKILL.md` and its referenced files through the project's configured rules or instruction mechanism.
2. Keep [SKILL.md](SKILL.md) and all five references together; reload skill discovery as required by the client. Do not overwrite an existing customized Art skill without reviewing the difference.
3. In this repository, also load the [calibration loop](../../docs/second-brain/calibration-loop.md), [project membranes](../../docs/second-brain/project-membranes.md), [decision states](../../docs/second-brain/decision-states.md), and [lesson promotion](../../docs/second-brain/lesson-promotion.md) when doing project creative work.
4. Invoke Art with a direct creative request and inspect a fictional result and its requested revision before treating installation as verified.

## Trigger Conditions

Use Art for direct creative requests or artistic encounters: interpret a work,
design an invitation, revise an image, critique a draft, or build a coherent series.
An attachment or mention of art alone does not authorize creation or editing.

## JK Project Integration

Keep the project owner's creative and decision authority. Preserve the human's
original critique, disagreements, and historical exercise context. Human acceptance,
rejection, or a hold decides whether a proposed lesson becomes reusable; this skill
does not automatically record or promote lessons. Project-local material stays
inside its membrane. Publication, capture, and external communication require their
own authority. Existing personal guidance and project records remain authoritative.

## Expected Outcome

The agent connects visible artistic choices to the brief, completes authorized
revisions, preserves supplied facts and qualifications, and inspects actual files.
Concepts, previews, production-ready assets, delivery, and publication remain
distinct states. Stable deliverables replace earlier working versions only after
the candidate is validated and the previous version is preserved.

## Verification

[release.json](release.json) binds the six shared files to the same candidate source
used by the coordinated Art release. These files are byte-identical across the
release; metadata and installation guidance are repository-specific.

Run all three [review cases](references/review-cases.md) in the actual receiving
environment: an invitation and revision preserving event facts; a synthetic product
edit preserving features and visible damage; and a presentation revision preserving
numbers and qualifications. Inspect both initial and revised outputs. Missing tools
leave the corresponding demonstration incomplete, rather than borrowing another
environment's evidence. The prior candidate completed explicit-load Windows Codex demonstrations; those
results do not establish recipient-client adoption or creative performance of the
composition amendment. The amendment received contract and packaging review only.

## Troubleshooting

**The client cannot find the references:** install the entire folder, preserving its layout.

**A required font or production tool is unavailable:** report the specific gap and label the output's actual state; do not claim exact typography or verified production.

**A revision changes supplied facts or accepted design features:** restore the invariants and inspect the revised artifact before replacement.

## Provenance

This repository builds on [Nate B. Jones's Open Brain](https://github.com/NateBJones-Projects/OB1).
Nate shares practical systems through [his writing](https://substack.com/@natesnewsletter)
and [website](https://natebjones.com). This Art skill is contributed by Robert Kuhne;
its shared source is recorded in `release.json`.
