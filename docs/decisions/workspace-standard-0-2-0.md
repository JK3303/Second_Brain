# Shared workspace standard 0.2.0 — adoption decision

Repository-level decision record for the proposal in
[`docs/workspace-standard-proposal.md`](../workspace-standard-proposal.md),
merged from PR #15.

**Merging the proposal did not adopt it.** Adoption was decided separately, and is
recorded below and in [`workspace-standard.json`](../../workspace-standard.json).

```text
Decision ID: WS-STD-0.2.0
Project: Second_Brain workspace
Status: approved
Source: PR #15, head 1efe6fceea6d2e674d0333096cd81ee3bf348d76, merged as d0cd6cea7d3c85623b8c5107fd6a5b52bbe086f3
Decision owner: JK
Evidence: All four proposed files reviewed in full, 245 lines. Both verifiable digests matched the delivered bytes before merge and again on fresh GitHub readback after it: standard 7fd9de91, exchange contract b13d525f, proposal 6f8bb27a. workspace-standard.json parses and its five referenced local-adaptation paths all exist on main. OB1 gate 15/15 and Markdown lint clean on the final head.
Alternatives considered: Adopt as written; adopt with named exclusions; decline and keep current practice unchanged; defer until the upstream source is independently readable.
Uncertainty: upstream_source_sha256 9c387535 and source_revision e2b99ad4 reference a source repository not readable from this workspace, so upstream parity is asserted rather than verified. The standard itself states that documented practices are not measured effectiveness.
Authority or approval: Approved by JK on 2026-10-14. Scope and conditions recorded below.
Reversible: yes
Next action: Remediate the client-decision occurrences named under condition 2; that remains open and is not resolved by this decision.
Reconsider when: The upstream source becomes independently readable, a named rule conflicts with existing practice, or a later standard version supersedes 0.2.0.
```

## What this decision changed

Recorded together on 2026-10-14.

| Where | Field | From | To |
|-------|-------|------|-----|
| this record | `Status` | `review-ready` | `approved` |
| this record | `Authority or approval` | `None recorded` | `Approved by JK on 2026-10-14` |
| `workspace-standard.json` | `adoption.status` | `proposed` | `adopted` |
| `workspace-standard.json` | `adoption.reviewed_on` | `null` | `2026-10-14` |

The proposal asks that approval, reviewed version, source revision, scope, and date
be recorded in `workspace-standard.json`. Its `adoption` block held only a status and
a date, so `approved_by`, `reviewed_version`, `reviewed_source_revision`, a `scope`
summary, and a `scope_record` pointer were added. `standard.status` and
`local_adaptations` are unchanged.

## Scope

Determined by mapping all eight behavioural rules in
[the standard](../personal-workspace-standard.md) against existing repository controls.
No rule conflicts with an existing control, so no change request arises under the
proposal's invitation to request one.

**Applies to:** all eight rules, as guidance within existing agreements and permissions.
What adoption changes differs by rule:

| Rule | Effect of adopting |
|------|-------------------|
| 1 — single entry point; opening does not activate | No operational change. Already required by project membranes and supplied by `manifest.md` |
| 2 — working agreements; not every task becomes a lesson | No operational change. `working-agreement.md` already triggers lesson proposal after a revision cycle, not per task |
| 3 — distinguish intentions, proposals, historical priorities, unknowns | No operational change. `decision-states.md` is finer-grained, with fourteen states and an explicit rule against inferring approval |
| 4 — revise only requested scope; preserve authorship; do not invent | No operational change. Covered by the calibration loop's critique preservation and by accepted Lesson 4 |
| 5 — stable deliverable; read back; verify each destination separately | **New as a written rule.** Formalizes existing practice. Adopted in full |
| 6 — resume from evidence; no mandatory cadence | Adopted **subject to condition 1 below** |
| 7 — declare memory and privacy boundaries; private state outside Git | Adopted as the standard going forward. See condition 2 below |
| 8 — upgrade deliberately; record version and source digest | **New machinery**, already built as `workspace-standard.json`. Adopted in full |

**Does not apply to:**

- **Runtime 1.2.0.** Not installed, not activated, out of scope. Adoption of the
  standard is not adoption of a runtime.
- **Capture mode.** Records-only use is adopted. Raw-session capture is not, and the
  standard's own Windows and macOS live-capture checks are therefore not triggered.
- **Any permission.** Adoption grants nothing: no synchronization, private-data intake,
  client contact, publication, spending, account changes, or sharing. Existing
  task-specific permissions remain necessary.
- **Retroactive validation.** Adoption does not declare past work compliant, and does
  not resolve the existing boundary occurrences recorded under condition 2.

### Condition 1 — rule 6 does not displace the Linear requirement

Rule 6 ends "No mandatory cadence or tracking." [`AGENTS.md`](../../AGENTS.md) requires,
for feature work tied to a Linear issue, updates at the start of work, at meaningful
checkpoints, and before handing back.

Both hold. Rule 6 prevents a *new universal* cadence being imposed; `AGENTS.md` keeps a
*scoped* one for issue-tied work. Where they appear to conflict, `AGENTS.md` governs
within its scope. Adopting rule 6 introduces no new tracker and removes no existing
obligation.

### Condition 2 — rule 7 is forward-looking; existing occurrences are separate

Rule 7's declared boundaries are adopted as the standard. They do not retroactively
clean what is already committed.

A full-repository scan found twelve occurrences of the client name across eight files
outside the engagement practice folder. They sort into three classes:

- **Protective** — the name appears in order to restrict or disclaim it, and removing it
  would make the rule vaguer: `docs/second-brain/project-membranes.md`,
  `charter/boundaries.md`, `manifest.md`, `projects/artistic-director/README.md`, and
  `recipes/brand-palette/README.md`. Defensible to keep.
- **Phase labels** — the name without content: `projects/artistic-director/README.md`
  and `handoff/current-state.md`. Low value either way.
- **Client decisions** — `decisions/creative-decisions.md` records the selected
  territory, the rejected alternatives, the selection reasoning, and names an individual
  as a rejected option. `decisions/review-receipts.md` records the review outcome. The
  two-surface split in
  [`authority-boundaries.md`](../../projects/artistic-director/methods/rebranding/authority-boundaries.md)
  assigns these to the approved private surface.

**Only the third class is a breach.** It is recorded here as an open remediation and is
not resolved by this decision. Under the historical exception, migrating it is the AD's
call, and migration changes what remains recoverable from history — the repository is
public and prior commits stay readable either way.

### On adopting a draft

`workspace-standard.json` records `standard.status: "draft"`, and the standard states
that draft, proposed, verified, and adopted are different states. This decision adopts
version 0.2.0 **while it is a draft**, deliberately: the eight rules are either already
satisfied or small additions, so waiting for a non-draft release would defer agreement on
behavior that is already in practice. A later version supersedes this record rather than
amending it.

**Authoritative regardless of adoption**, per the proposal's own local-adaptations list:
[`AGENTS.md`](../../AGENTS.md),
[project membranes](../second-brain/project-membranes.md),
[decision states](../second-brain/decision-states.md),
[calibration loop](../second-brain/calibration-loop.md),
[lesson promotion](../second-brain/lesson-promotion.md).

## What adoption would not grant

Per the proposal's own authority limits: no capture, runtime activation, automatic
synchronization, private-data intake, client contact, publication, spending, account
changes, or sharing permissions. Existing task-specific permissions remain necessary.
