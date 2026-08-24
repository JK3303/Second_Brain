# Rebranding Automation

Candidate automations for the rebranding workflow, and the gate they must pass before adoption.

## What this folder is

A **candidate register**, not a toolchain. Nothing here runs automatically. Each entry is a proposal to automate a specific piece of the workflow, held until it has evidence and explicit human acceptance.

| File | Purpose |
|------|---------|
| [`candidate-log.md`](candidate-log.md) | Every proposed automation, its status, and its evidence |
| [`validation-checklist.md`](validation-checklist.md) | The Step 7 validation gate — the most mature automation target |

## The adoption gate

A candidate may be adopted only when **all five** are true:

1. **Two engagements of evidence.** The friction it addresses appeared in at least two comparable engagements. One occurrence is a coincidence, not a pattern.
2. **It flags, it does not resolve.** The automation produces findings for a human. It never emits a corrected artifact presented as final.
3. **It cannot cross an authority boundary.** It touches no step classified `manual-judgment` or `blocked` in [`../../methods/rebranding/automation-map.md`](../../methods/rebranding/automation-map.md).
4. **Its failure mode is known and safe.** A false negative is recoverable by the human step that follows it. Anything whose silent failure would ship an error unreviewed is not adoptable.
5. **Explicit AD acceptance,** recorded per candidate with a date.

Candidates that fail any of these stay logged. Logging is the point — the record of what was considered and declined is as useful as the record of what was adopted.

## Standing prohibitions

These are not automatable at any maturity level:

- **Designating where client material lives.** A private engagement surface is designated by a human authority act.
- **Shortlisting territories** (Step 5) and **the recommendation** (Step 9). Automating these relocates the artistic judgment the engagement exists to supply.
- **The client decision** (Step 10).
- **Lesson classification and promotion to memory** (Step 12). No automation may write to overlay memory under any circumstance.
- **Visual inspection of a rendered document** (Step 8). A build that exits zero has not been inspected. A human opens the file and looks at it.
- **Rights determinations.** A tool may detect a missing label; only an authorized party can grant clearance.

## Baseline discipline

The first engagement under this method establishes the measurement baseline. Until a second comparable engagement exists:

- No automation may be described as saving time.
- No metric may be described as improved.
- Candidate entries record *observed friction*, not *projected savings*.

## Interaction with the validation checklist

[`validation-checklist.md`](validation-checklist.md) is currently a **manual checklist**. It is written to be mechanically checkable so it can become automated later. Run it by hand until it has two engagements of evidence, then propose it as a candidate through the gate above like anything else.
