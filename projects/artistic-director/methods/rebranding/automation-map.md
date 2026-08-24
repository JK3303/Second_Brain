# Automation Map — Rebranding Workflow

Classification of each workflow step by how much of it can responsibly be automated.

## Classes

| Class | Definition | Rule |
|-------|-----------|------|
| **manual-judgment** | Requires human artistic or authority judgment | Never automate. AI may prepare inputs and present options; the human decides. |
| **AI-assisted** | Human-directed, AI-produced, human-corrected | Automate the production, never the direction or the acceptance. |
| **template-automatable** | Mechanical, rule-checkable, deterministic | Safe to automate fully, after the check has been validated against at least one completed engagement. |
| **blocked** | Cannot be automated within current authority | Requires human action or an authorization that AI does not hold. |

A classification is a claim about *this* method as currently practiced. Reclassify only with evidence from a completed engagement — see [`../../automation/rebranding/candidate-log.md`](../../automation/rebranding/candidate-log.md).

---

## Step classification

| # | Step | Class | Automatable portion | Human-held portion |
|---|------|-------|--------------------|--------------------|
| 1 | Authority / source gate | **blocked** | Presenting the gate checklist | Naming the decision-maker; designating the private surface; approving sources. AI cannot designate where client material lives. |
| 2 | Intake | **AI-assisted** | Drafting the question set; structuring answers; flagging unanswered fields | Answers; scope and exclusion decisions; judging which unknowns block work |
| 3 | Current-brand reading | **AI-assisted** | Gathering from approved sources; building the source register; separating observation from interpretation; listing gaps | Approving sources; correcting factual errors; sign-off |
| 4 | Territory generation | **AI-assisted** | Producing candidate volume; applying the distinctness test as a first pass | Judging whether a difference is *material*; setting creative direction |
| 5 | AD shortlist | **manual-judgment** | Presenting candidates side by side | The selection and its rationale. AI ranking here would pre-decide Step 9. |
| 6 | Equal proposal development | **AI-assisted** | Drafting sections; producing mockups; enforcing depth parity; maintaining the asset register | Creative direction; correction; rejecting work below standard |
| 7 | Evidence / rights / completeness validation | **template-automatable** | Unsourced-claim detection; unlabeled-asset detection; placeholder detection; parity comparison; reserved-word scan | Resolving what a flag means; rights determinations; sign-off |
| 8 | PDF assembly | **template-automatable** | Layout from the outline; page-structure parity; confidentiality mark; render | **Visual inspection of the render.** A build that exits zero is not an inspected document. |
| 9 | AD recommendation | **manual-judgment** | Assembling the evidence the AD asked for | The recommendation, the reasoning, the principal risk, and the falsification condition |
| 10 | Client decision | **blocked** | Preparing the receipt structure | The decision. Held solely by the named decision-maker. |
| 11 | Feedback capture | **AI-assisted** | Transcribing verbatim; structuring; routing to the private surface | Deciding what the feedback means; identifying divergences from expectation |
| 12 | Lesson classification | **manual-judgment** | Proposing candidate lessons; drafting sanitized wording | Classification and acceptance. Automatic promotion is prohibited. |
| 13 | Cohort review | **AI-assisted** | Collecting metrics; computing totals; formatting comparison | Interpreting the numbers; deciding whether a change is real |

**Totals:** manual-judgment 3 · AI-assisted 6 · template-automatable 2 · blocked 2

---

## Where the leverage is

Steps 7 and 8 are the only fully automatable stretch, and they are also where correction cost is highest late in the process — a provenance error discovered after render costs an assembly cycle. Automating the validation checklist and the layout parity check is the highest-value first automation target.

Steps 5, 9, 10, and 12 are deliberately excluded from automation. They are the points where authority lives. Automating them would not speed up the engagement; it would relocate the decision.

## Standing constraints

1. **No step may be reclassified toward more automation on the basis of a single engagement.** One clean run is not evidence that a check generalizes.
2. **Automation may flag; it may not resolve.** Every automated check outputs findings for a human, never a corrected artifact presented as final.
3. **A passing automated check is not a sign-off.** Sign-off remains a human act at Steps 3, 7, and 8.
4. **No automation may write to overlay memory.** Promotion is human-gated without exception.
5. **No efficiency claim without a comparable prior engagement.** The first run under this method is a baseline. "Faster" requires two data points and comparable scope.
