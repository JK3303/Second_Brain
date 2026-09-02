# Automation Candidate Log

Every proposed automation for the rebranding workflow. Nothing here is adopted, scheduled, or built unless its status says so.

**Statuses:** `proposed` · `evidence pending` · `accepted` · `declined` · `retired`

**Default status for a new entry:** `proposed`.

---

## Register

| ID | Candidate | Step | Status | Evidence (engagements) | Failure mode | AD decision | Date |
|----|-----------|------|--------|----------------------|-------------|------------|------|
| AC-01 | Unsourced-claim detector — flag factual statements in proposal documents with no source-register reference | 7 | proposed | 0 | False negative: an unsourced claim reaches review. Recoverable at AD sign-off. | — | — |
| AC-02 | Unlabeled-asset detector — flag assets appearing in the package with no asset-register row or provenance label | 7 | proposed | 0 | False negative: an unlabeled asset reaches review. Recoverable at AD sign-off. | — | — |
| AC-03 | Placeholder-visibility check — confirm every placeholder in the register is visibly marked on the artifact itself | 7, 8 | proposed | 0 | False negative: an unmarked placeholder reads as finished work. Moderate — this one misleads the decision-maker. | — | — |
| AC-04 | Reserved-word scan — flag *approved · selected · signed off · agreed · confirmed · final · authorized* outside permitted contexts | 7, 8 | proposed | 0 | False positive is cheap; false negative lets premature approval language ship. | — | — |
| AC-05 | Depth-parity comparator — compare section presence, application count, application type, and treatment length across proposals | 6, 7 | proposed | 0 | False negative: an asymmetric package pre-decides the outcome. High value, low risk. | — | — |
| AC-06 | Page-structure parity check on the rendered package — confirm each proposal occupies the identical page structure | 8 | proposed | 0 | False negative caught by human visual inspection, which remains mandatory. | — | — |
| AC-07 | Confidentiality-mark presence check across all pages | 8 | proposed | 0 | False negative ships an unmarked confidential document. Cheap to check, meaningful to miss. | — | — |
| AC-08 | Template scaffolding — instantiate the engagement document set from the templates once the authority gate passes | 2 | proposed | 0 | Low risk. Must not pre-fill any content, only structure. | — | — |
| AC-09 | Metric collection — accumulate timings and correction counts into the cohort-metrics structure | 13 | proposed | 0 | Must record **not measured** rather than estimating. An estimating collector is worse than no collector. | — | — |
| AC-10 | Claim-type consistency check — confirm every claim carries exactly one of the five claim types | 3, 7 | proposed | 0 | False negative allows blended claim types, the failure this method exists to prevent. | — | — |
| AC-11 | Typeface delivery check — for any digital artifact, resolve each declared font stack against the faces the artifact actually ships, and flag stacks whose first available match is a system fallback | 6, 7 | proposed | 0 | False negative ships work whose typography silently substitutes for most viewers while looking correct to the reviewer who has the font installed. The failure is invisible on the machine most likely to be checking. | — | — |

---

## Declined by design

Logged so the reasoning is not relitigated.

| Candidate | Step | Reason declined |
|-----------|------|-----------------|
| Automated territory shortlisting or ranking | 5 | Relocates the artistic judgment the engagement exists to supply, and pre-decides Step 9 |
| Automated recommendation drafting | 9 | The recommendation is the AD's expert judgment; a drafted one is not one |
| Automatic lesson promotion to overlay memory | 12 | Prohibited without exception. Promotion is human-gated |
| Automated rights determination | 6, 7 | A tool can detect a missing label; only an authorized party grants clearance |
| Replacing human visual inspection of the render with a build check | 8 | A clean build is not an inspected document |
| Auto-designating a private engagement surface | 1 | Designating where client material lives is a human authority act |

---

## How to add a candidate

1. Add a row with status `proposed`, the step it touches, and the **failure mode if it silently fails** — not the benefit.
2. Confirm it touches no step classified `manual-judgment` or `blocked`.
3. Leave evidence at 0 until a second comparable engagement observes the same friction.
4. Adoption requires explicit AD acceptance recorded in the row, with a date. Silence is not acceptance.

## Evidence rule

The evidence column counts **engagements in which the friction was actually observed and recorded**, not engagements in which the automation would plausibly have helped. A candidate at 0 or 1 stays `proposed` regardless of how obviously useful it appears.
