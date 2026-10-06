# Shared workspace standard 0.2.0 — adoption decision

Repository-level decision record for the proposal in
[`docs/workspace-standard-proposal.md`](../workspace-standard-proposal.md),
merged from PR #15.

**Merging the proposal did not adopt it.** The documents are reference material until
an adoption decision is recorded here and in
[`workspace-standard.json`](../../workspace-standard.json).

```text
Decision ID: WS-STD-0.2.0
Project: Second_Brain workspace
Status: review-ready
Source: PR #15, head 1efe6fceea6d2e674d0333096cd81ee3bf348d76, merged as d0cd6cea7d3c85623b8c5107fd6a5b52bbe086f3
Decision owner: JK
Evidence: All four proposed files reviewed in full, 245 lines. Both verifiable digests matched the delivered bytes before merge and again on fresh GitHub readback after it: standard 7fd9de91, exchange contract b13d525f, proposal 6f8bb27a. workspace-standard.json parses and its five referenced local-adaptation paths all exist on main. OB1 gate 15/15 and Markdown lint clean on the final head.
Alternatives considered: Adopt as written; adopt with named exclusions; decline and keep current practice unchanged; defer until the upstream source is independently readable.
Uncertainty: upstream_source_sha256 9c387535 and source_revision e2b99ad4 reference a source repository not readable from this workspace, so upstream parity is asserted rather than verified. The standard itself states that documented practices are not measured effectiveness.
Authority or approval: None recorded.
Reversible: yes
Next action: JK decides adoption and scope, then updates this record and sets adoption.status and reviewed_on in workspace-standard.json.
Reconsider when: The upstream source becomes independently readable, a named rule conflicts with existing practice, or a later standard version supersedes 0.2.0.
```

## On approval

Four fields change together. Nothing is adopted until all four are written.

| Where | Field | From | To |
|-------|-------|------|-----|
| this record | `Status` | `review-ready` | `approved` |
| this record | `Authority or approval` | `None recorded` | JK, with the date |
| `workspace-standard.json` | `adoption.status` | `proposed` | `adopted` |
| `workspace-standard.json` | `adoption.reviewed_on` | `null` | the date |

Scope is recorded below rather than in the JSON, which has no field for it.

## Scope, if approved

The proposal asks which guidance applies within existing agreements and permissions.
Deliberately unfilled: an unscoped adoption would claim more than the decision being
made.

**Applies to:**

**Does not apply to:**

**Authoritative regardless of adoption**, per the proposal's own local-adaptations
list: [`AGENTS.md`](../../AGENTS.md),
[project membranes](../second-brain/project-membranes.md),
[decision states](../second-brain/decision-states.md),
[calibration loop](../second-brain/calibration-loop.md),
[lesson promotion](../second-brain/lesson-promotion.md).

## What adoption would not grant

Per the proposal's own authority limits: no capture, runtime activation, automatic
synchronization, private-data intake, client contact, publication, spending, account
changes, or sharing permissions. Existing task-specific permissions remain necessary.
