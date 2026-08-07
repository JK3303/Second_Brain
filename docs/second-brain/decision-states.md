# Decision States

A unified vocabulary for tracking the lifecycle of ideas, decisions, and deliverables across projects.

## States

| State | Meaning |
|-------|---------|
| `idea` | Captured but not yet explored |
| `explore` | Under active investigation |
| `shortlist` | Narrowed to a small set of options |
| `brief` | Defined objective and constraints for the next round |
| `draft` | Work in progress, not yet ready for review |
| `review-ready` | Complete enough for human review |
| `approved` | Human has approved the creative or technical direction |
| `executing` | Approved work is being built or produced |
| `delivered` | Work has been handed off or deployed |
| `published` | Publicly visible |
| `complete` | Finished, no further action needed |
| `held` | Blocked on missing information, unresolved question, or authority |
| `rejected` | Explicitly declined — record why and what would change the decision |
| `superseded` | Replaced by a later decision — link to the replacement |

## Rules

- The agent must not infer approval from a polished artifact, previous practice, silence, urgency, or a recommendation.
- A recommendation is not approval. `review-ready` does not become `approved` without explicit human action.
- `held` requires naming the exact missing item, why it matters, and who should decide or supply it.
- `rejected` and `superseded` must include conditions under which the decision could be reconsidered.

## Minimum decision receipt

```
Decision ID:
Project:
Status:
Source:
Decision owner:
Evidence:
Alternatives considered:
Uncertainty:
Authority or approval:
Reversible: yes / no
Next action:
```

## Mapping to existing Artistic Director states

The Artistic Director system uses an 8-state creative workflow (Exploration, Shortlist, Brief, Draft, Review-ready, Approved, Delivered, Published). These map directly: Exploration=explore, Shortlist=shortlist, Brief=brief, Draft=draft, Review-ready=review-ready, Approved=approved, Delivered=delivered, Published=published.

## Reference implementation

- `projects/artistic-director/decisions/creative-decisions.md` — creative choices (table format)
- `projects/artistic-director/decisions/holds-and-rejections.md` — blocked and declined directions
- `projects/artistic-director/decisions/review-receipts.md` — review evidence
- `projects/artistic-director/practice/grace-gems-phase2/04-review-receipt.md` — detailed project receipt
