# Asset Record Preflight

A creative handoff can reference the wrong photo revision, omit its credit,
or rely on an unresolved usage record. This local check compares an explicit
asset inventory with the actual files and reports those gaps together.

It complements the Artistic Director's
[reference log](../../projects/artistic-director/references/reference-log.md)
and [attribution log](../../projects/artistic-director/references/rights-and-attribution.md).
It checks recorded data, not the validity of a license or a legal conclusion.

## Requirements

An Open Brain / Second_Brain project, Python 3.11+, and a private inventory.
Standard library only. No network requests, asset upload, or project changes.

## 1. Record the intended assets

Copy `example-records.json` outside a public checkout and add one record per
asset. The example is deliberately incomplete and should report gaps.

| Field | Meaning |
| --- | --- |
| `id` | Unique local identifier |
| `path` | Exact path relative to the specified project root |
| `sha256` | Hash of the exact bytes reviewed |
| `status` | `documented`, `unknown`, or `restricted` |
| `uses` | Explicit usage labels, such as `website` or `internal-review` |
| `reviewer` | Person responsible for the recorded review |
| `evidence` | Reference to the underlying permission or ownership record |
| `credit` | Required credit text, or an explicit explanation that none is recorded as required |
| `expires` | Inclusive `YYYY-MM-DD`, or explicit `none` if the record has no expiry |

`documented` means that someone recorded a review; it does not establish that
the record is authentic or sufficient. Keep the underlying evidence in its
appropriate private location. The tool does not open or validate that evidence.

Compute a SHA-256 locally, for example with PowerShell's `Get-FileHash`.
Store its lowercase hexadecimal value. Updating a hash after an asset changes
requires another human review; the tool never updates it for you.

**Done when:** the intended usage and exact reviewed asset bytes are recorded.

## 2. Check the handoff

Run from the repository root, replacing the private inventory path and date:

```bash
python recipes/asset-preflight/preflight.py --root projects/artistic-director --records PRIVATE_RECORDS.json --usage website --as-of 2026-09-19
```

JSON output lists findings per asset and includes the actual hash when readable.
Usage labels match exactly. The date is explicit so a saved check is reproducible.
An expiry date remains current through that date. `none` means no expiry is
recorded, not an independently established perpetual right.

Exit codes: **0** no detected record gaps; **1** gaps found; **2** malformed input
or unreadable input. No code means legal clearance or permission to publish.

**Done when:** every reported gap has been resolved or brought to the responsible
human. Retain the output privately with the handoff if useful.

## Coverage and limits

Only listed assets are checked; unlisted files are not discovered. Checks cover
file presence, byte identity, record status, exact usage membership, nonempty
reviewer/evidence/credit fields, and expiry. They do not evaluate ownership,
consent, license terms, trademark issues, fair use, or evidence authenticity.

Asset paths cannot escape the project or traverse symlinks/junctions. Hidden
paths and globs are unsupported. Limits: 500 records, 2 MiB inventory, 100 MiB
per asset. Files should remain stable during the check. JSON output contains
credits and evidence references, so treat it according to the project boundary.

## Verification

```bash
python -m unittest discover -s recipes/asset-preflight -p "test_*.py" -v
```

Tests use original synthetic bytes and cover changed/missing assets, usage,
expiry boundaries, incomplete records, malformed inputs, and path containment.
This is local repository testing; no live Supabase instance is involved.

## Provenance

Original companion for Second_Brain's creative delivery records. The repository
builds on [Open Brain](https://github.com/NateBJones-Projects/OB1) by Nate B. Jones:
[newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Authored with AI assistance by Mira.
