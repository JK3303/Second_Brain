# Repository decisions

Decision records for choices that apply to this repository as a whole — adopting a
shared standard, changing a convention, accepting an external dependency.

Project-scoped creative decisions do not belong here. Those live with their project,
for example [`projects/artistic-director/decisions/`](../../projects/artistic-director/decisions/).

## Format

Each record uses the receipt format validated by
[`recipes/decision-receipts`](../../recipes/decision-receipts/README.md), inside a
fenced `text` block. Eleven fields are required:

`Decision ID`, `Project`, `Status`, `Source`, `Decision owner`, `Evidence`,
`Alternatives considered`, `Uncertainty`, `Authority or approval`, `Reversible`,
`Next action`.

`Missing item`, `Why it matters`, `Needed from`, `Reconsider when`, and
`Superseded by` are optional.

Validate before committing:

```bash
python recipes/decision-receipts/validate.py docs/decisions/*.md
```

## Status values

Status comes from the vocabulary in
[`docs/second-brain/decision-states.md`](../second-brain/decision-states.md) and the
recipe's own set. `review-ready` means reviewed and awaiting a decision;
`approved`, `held`, `rejected`, and `superseded` mean what they say.

A record is not an approval. `Authority or approval` states who approved and when, or
that nothing is recorded. An empty or placeholder value is a record of an undecided
question, not a decision.

## Why these are public

Repository-level methodological decisions are generic method, so they sit on the
public side of the boundary described in
[project membranes](../second-brain/project-membranes.md) — alongside reusable methods
and explicitly accepted lessons.

Client decisions, preferences, commercial evidence, and engagement-specific material
do not. Those belong on an approved private surface and must not be recorded here.
Project-local material does not become repository-level simply because a decision
touched it.

## Records

| Record | Subject | Status |
|--------|---------|--------|
| [`workspace-standard-0-2-0.md`](workspace-standard-0-2-0.md) | Shared workspace standard 0.2.0 | review-ready |
