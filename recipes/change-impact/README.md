# Project Change Impact

When a brief changes, a decision file may remain byte-for-byte identical while
the deliverable based on it needs review. This tool traces changes through
explicitly recorded dependencies and explains the route from changed input to
affected decision or artifact.

It uses local files and a small human-authored map. It never infers dependencies
from prose, rewrites decisions, or declares them invalid. This complements
Second_Brain's project boundaries and decision states without requiring a
database or another contribution.

## Requirements

An Open Brain / Second_Brain project and Python 3.11+, standard library only.
Store project maps and snapshots according to the project's privacy boundary.
No source text is included in output; paths and rationales can still be sensitive.

## 1. Declare the dependency map

Copy `example-map.json` and adapt it to your project. Each node has a stable
`id`, project-relative file `path`, `kind` (`source`, `decision`, or `artifact`),
`depends_on` IDs, and a human-written `rationale` for those dependencies.

The supplied example is fictional. It models brief → direction → delivery.
A dependency means “review this if that changes,” not “that authorizes this.”
Cycles, unknown IDs, duplicates, and paths outside the project are rejected.

**Done when:** the human agrees the recorded relationships are meaningful.

## 2. Save a baseline

From the repository root:

```bash
python recipes/change-impact/impact.py snapshot --root recipes/change-impact/example --map recipes/change-impact/example-map.json
```

Save standard output as UTF-8 JSON in a private location. Every node includes
the current file hash; a snapshot digest binds the map and hashes together.
Missing files have a null hash and produce exit code 1, so a missing source
cannot silently look like a complete baseline.

**Done when:** the saved snapshot matches the intended starting state and any
missing file is understood. Snapshots do not record human approval.

## 3. Compare after a change

Use your actual project root, map, and saved baseline:

```bash
python recipes/change-impact/impact.py compare --root PROJECT --map MAP.json --before BASELINE.json
```

`changed` includes changed bytes, added/removed nodes, paths, kinds, rationales,
and dependency edits. `review_candidates` explains a shortest dependency route
per changed trigger. Both the old and current map are used, so removing a
dependency does not silently erase its previous review implications.

`missing_current_files` remains visible even if a file was already missing in
the baseline. Unchanged unrelated nodes are not included as review candidates.
Several changed sources can independently trigger the same artifact.

**Done when:** the human has reviewed the relevant decisions and deliverables.
Create a new baseline only after accounting for the changes; comparison never
replaces the previous one automatically.

## Limits and verification

The graph is only as complete as the declared relationships. Byte changes may
be trivial; the report cannot judge significance, truth, approval, or quality.
Rationales are supplied by the map author, not generated explanations.
The digest detects accidental snapshot edits; it is not a signature or proof
that the baseline is authentic. Keep the baseline in trusted storage.

Input limits: 200 nodes, 2 MiB per tracked file, 16 MiB tracked total, 2 MiB per
JSON input. Hidden paths, globs, symlinks, and junctions are unsupported. Use
stable files during a snapshot. The tool only reads and writes standard output.

Exit codes: 0 unchanged/complete; 1 changes or missing files need attention;
2 invalid input or read failure. No exit code authorizes execution or publication.

```bash
python -m unittest discover -s recipes/change-impact -p "test_*.py" -v
```

Tests cover transitive routes, unrelated exclusions, missing/removed/new files,
dependency edits, cycles, unknown IDs, tampered snapshots, and path containment.
Local repository testing only; no live Supabase instance is involved.

## Provenance

Original companion for Second_Brain, which builds on
[Open Brain](https://github.com/NateBJones-Projects/OB1) by Nate B. Jones:
[newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Authored with AI assistance by Mira.
