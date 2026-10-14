---
name: workspace-github
description: Inspect GitHub issues, pull requests and checks, or carry an explicitly authorized Git change through its requested endpoint using scoped validation and verified destination evidence. Use for GitHub reviews, CI investigation and Git publication work; ordinary file edits do not activate publication.
---

# Workspace GitHub

Read [the workspace adapter](references/workspace.md) first. It identifies the
repository, owner approvals, authentication lane, checks and publication tools.
Current user authority and repository controls take precedence. Missing or
contradictory controls permit read-only diagnosis, not guessed execution.

## Recover the endpoint

Distinguish inspection, local editing, staging, committing, pushing, opening a
PR, posting feedback, merging and deployment. Carry existing authority forward;
ask only for a genuinely missing boundary. Reading a PR does not authorize
posting a review; creating one does not authorize merging or deploying it.

For ordinary reads, obtain fresh issue/PR head, diff and check evidence. Prepare
file/line findings in the requested surface; recheck anchors before authorized
submission. Do not run publication gates merely to inspect an issue or PR.
If the connector fails, try an already authenticated CLI before declaring access
unavailable. Distinguish account mismatch, missing file, visibility, transport and
rate limits. A 404 alone does not prove revoked access. Never print credentials.

At the first publication request, check target and identity readiness early.
A remote blocker does not prevent independently authorized local preparation.
Preserve the requested endpoint: a branch push is not requested main landing,
and a prepared review is not a posted review. Stop at the authorized boundary.

## Establish candidate and context

Resolve the exact absolute Git root, task owner, branch, HEAD and current index.
Preserve unrelated work, including staged files. Bound status output to counts
and top-level groups before expanding it. State exact candidate paths/hunks,
declared tests/dependencies, exclusions and the desired terminal state. Resolve
ownership before concurrent work; a clean tree or quiet chat is not a writer hold.
Branch/worktree creation follows local permission rules, not this skill's defaults.

The optional read-only helper uses Git and Python 3.9+:

```text
python <skill>/scripts/preflight.py --repo <absolute-root> --candidate <relative-file> --input <selected-test-or-dependency>
```

Repeat either flag for individual files. Inputs include selected tests, fixtures,
configuration and executable dependencies. Explicit tracked deletions are valid
candidates and have a null content hash; missing untracked files and missing
required inputs block. Rename candidates must name both destinations and origins.
The helper does not discover undeclared dependencies, prove tests or authorize work.

`fingerprint` describes selected Git-normalized content. `context_fingerprint`
describes root, HEAD, branch and index entries separately. Unchanged content can
reuse validation after an authorized commit while Git context must be refreshed.
Neither fingerprint proves raw-byte recovery, authentication or remote freshness.
Staged-state fields are bounded; an eligible result may still contain unrelated
staged work. Inspect the entire intended commit unit before committing and never
include or unstage someone else's work to make the candidate appear clean.

Before commit preparation, inspect the outgoing stack against the intended base.
Name earlier unrelated commits a later push would include. Refresh the exact
remote target before publication; local tracking refs alone are not fresh evidence.
Remote-ahead, divergence, changed candidate or entangled staging requires a scoped
disposition. Do not silently rebase, merge, broaden refspecs or replace the endpoint.

## Validate and preserve

Select the cheapest sufficient repository checks for the candidate before staging.
Inspect their relevant dependencies; a working-tree pass cannot prove a candidate
that omits a changed required test/control. Run from immutable candidate content
when needed to settle that difference. Do not run Full solely because unrelated
files are dirty or commit metadata changed. Reuse successful evidence only when
selected content, runtime and relevant environment still match. New failures or
changed dependencies invalidate affected evidence, not all unrelated passing checks.

Before an operation whose rollback might rewrite unfinished work, require a
verified recoverable baseline: original bytes and existence of every affected
tracked/untracked file, current HEAD/index context and stopped competing execution.
Normalized hashes and conflict-free previews are insufficient. Use existing local
preservation/recovery tools; if none exists, stop that operation and prepare an
exact recovery plan. Do not invent a reset/stash/lock-removal shortcut.

## Execute only the authorized transition

Before each GitHub mutation verify the effective account for that tool. Before
publication also verify destination, author/committer and push authentication.
Browser, CLI, connector and Git push identities are separate facts. Preserve
existing credentials, hooks, owner approvals and repository visibility.

Stage exact paths/hunks and inspect the staged diff against the validated scope.
Before committing, verify the index contains only the authorized commit unit.
Use the adapter's guarded publisher when present; do not bypass it with raw Git
or provider ref writes. When none exists, ordinary Git remains subject to the same
checks, explicit full destination ref and exact source commit. No force push,
implicit rebase, hook installation or access change follows from this workflow.

After an interrupted action, inspect its actual effects before recovery or retry.
Preserve current bytes and completed state; do not replay a batch over newer edits.
For credentials or locks, diagnose the specific boundary and use existing recovery
controls. Do not change global auth, blindly delete locks or restart duplicate
login/push processes. Retain the exact live process/run handle until terminal.
Cache an unchanged unavailable context; retry only after relevant state changes.
An uncertain remote outcome requires readback before another write.

## Verify and report

Read the destination ref after a push and compare the exact expected commit.
After a PR or review write, read back its identity, head/content and actual URL.
Follow checks on that submitted SHA with one bounded watcher. Inspect the published
workflow's expected jobs; missing, skipped, failed or unfinished required jobs
cannot establish success. No hosted workflow means hosted evidence is unavailable,
not a green run. Do not rerun CI or publish another change merely to hide failure.

Report separately: edited, validated, staged, committed, pushed, PR opened,
hosted checks and merged/deployed. For blockers give the reached state, exact
target/source SHA, remaining action, missing evidence/authority and a bounded
resumption step. Avoid credentials and unrelated private context in that packet.
Package inclusion or PR merge does not establish live client loading, personal
adoption or improved performance. Use [the scenarios](references/scenarios.md)
for contract review; helper tests are not evidence that an agent followed them.
