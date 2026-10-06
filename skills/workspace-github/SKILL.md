---
name: workspace-github
description: Inspect GitHub issues, pull requests and checks, or carry an explicitly authorized Git change through its requested endpoint using scoped validation and verified destination evidence. Use for GitHub reviews and Git publication work; ordinary file edits do not activate publication.
---

# Workspace GitHub

Use this shared workflow with [the workspace adapter](references/workspace.md).
Read that adapter first: it identifies the owner, controlling instructions,
authentication lane, validation runner and permitted publication tools. Local
controls and the current user's explicit scope take precedence. A missing or
contradictory adapter permits read-only diagnosis, not guessed execution.

## Recover the requested endpoint

Distinguish inspection, local editing, staging, committing, pushing, opening a
PR, posting a review, merging and deployment. Carry existing authorization
forward; ask only for an actual missing boundary. Reading a PR does not authorize
posting feedback. Opening a PR does not authorize merging it. Keep private
evidence out of public descriptions, logs and outgoing attribution.

For inspection, obtain fresh provider evidence and report actionable findings
with file/line references. Avoid publication preflight for ordinary reads.
If a connector fails, try the already authenticated CLI before declaring access
unavailable. Separate account mismatch, missing file, visibility, transport and
rate limits; a 404 alone is not proof of revoked access. Never print credentials.

## Bound the candidate and evidence

Resolve the absolute Git root, owner and existing checkout state before edits.
Preserve unrelated changes. State exact candidate files or hunks, excluded work
and the desired terminal state. Do not create or switch branches/worktrees from
a generic recommendation: follow the adapter's permission and ownership rules.

The optional read-only helper summarizes status without dumping a large tree:

```text
python <skill>/scripts/preflight.py --repo <absolute-root> --candidate <relative-file> --input <selected-test-or-dependency>
```

Repeat either flag for individual files. Inputs must include the selected tests,
their fixtures/configuration and declared executable dependencies. The helper
blocks missing/escaping paths and changed declared inputs outside the candidate;
it cannot discover undeclared dependencies, prove test success or grant authority.
Its fingerprint records Git-normalized selected bytes, not a whole-tree gate.
Check scope again immediately before a write or Git mutation.

Choose the cheapest sufficient validation for the actual change using the local
runner. Include changed tests and dependencies deliberately. Do not select Full
merely because unrelated files are dirty. If Full is required, reuse successful
evidence only when its content, runtime and relevant environment still match.
An unchanged commit's metadata does not justify rerunning the same gate. Local
tests, landed data checks and hosted checks prove different claims.

## Execute only the authorized transition

Before each GitHub mutation, verify the effective submitting account for that
tool. Before publication also verify destination, outgoing author/committer and
push authentication. Stage exact paths/hunks and inspect the staged diff; never
use broad staging to absorb unrelated work. Use the adapter's validated publisher
and lock recovery procedure when supplied. Do not bypass them with an ad hoc
push, manually delete an index lock or install/change hooks without authority.
Hooks and receipts improve execution consistency; they are not an OS security
boundary. Preserve existing hooks and authentication settings.

If HEAD, candidate bytes, destination or remote base changes, reconcile the
specific change before proceeding. Do not silently force push, merge, rebase or
rewrite credentials. For a long-running operation retain its exact session/run
identifier and resume that process; do not launch a duplicate watcher or login.
After failure, preserve the concise cause and completed state, then repair only
the authorized scope. Never retry a publication whose outcome is unknown before
reading back the destination.

## Verify and report the terminal state

After a push, freshly read the destination ref and compare the exact expected
SHA. After a PR, review or other provider write, freshly read its identity and
content and link the actual result. Follow hosted checks for that exact SHA with
one watcher; a local pass or an older green run is insufficient. Attach created
or actively reviewed PRs in hosts supporting PR artifacts.

Report separately: locally edited, validated, staged, committed, pushed, PR
opened, hosted checks passed and merged. Name the exact blocker and remaining
action when the requested endpoint is incomplete. Do not claim owner adoption
from inclusion of this package. For regression review, use
[the bounded scenarios](references/scenarios.md).
