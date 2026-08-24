# Rebranding Workflow

Thirteen steps, each with a named owner and an exit gate. A step is not complete until its exit gate is satisfied. Steps may loop backward; they may not be skipped forward.

```
authority/source gate
  → intake
    → current-brand reading
      → territory generation
        → AD shortlist
          → equal proposal development
            → evidence, rights, and completeness validation
              → PDF assembly
                → AD recommendation
                  → client decision
                    → feedback capture
                      → lesson classification
                        → cohort review
```

Roles used below:

- **AD** — the human artistic director. Owns creative judgment and the recommendation.
- **Decision-maker** — the single named person at the client who holds selection authority.
- **AI** — the assisting system. Organizes, drafts, validates, and assembles. Decides nothing.

---

## Step 1 — Authority / source gate

**Owner:** AD.
**Purpose:** Establish, before any work, who may decide what and where engagement material may live.

**Inputs:** The engagement request.

**Outputs:**
- Named decision-maker and the scope of their authority.
- Named approved private surface for engagement-specific material, with its path or address.
- List of approved sources AI may draw from.
- Explicit list of actions this engagement does *not* authorize.

**Exit gate — all must be true:**
- [ ] The decision-maker is a specific named person, not a group or a role.
- [ ] An approved private engagement surface exists and has been designated by the AD.
- [ ] The non-authorization list is written down.

**If the gate fails:** stop. Do not create engagement-specific material anywhere, including in a general-purpose or public repository. Report the blocker and the proposed structure. Do not create or designate a private surface unilaterally — designation is a human authority act.

---

## Step 2 — Intake

**Owner:** AD, with AI drafting questions.
**Purpose:** Capture what the engagement is for and what is deliberately excluded.

**Inputs:** Step 1 outputs; any client-supplied brief.

**Outputs:** Completed [`intake.md`](../../templates/rebranding/intake.md).

**Exit gate:**
- [ ] The business problem is stated in the client's words where available, and marked as inferred where not.
- [ ] Exclusions are explicit (what is out of scope, what must not change).
- [ ] Unknowns are listed with an owner for each, rather than filled in.
- [ ] Count of clarification questions is recorded for the baseline.

**Anti-pattern:** completing intake by inference so the work can start. An intake with ten honest unknowns is more useful than one with ten confident guesses.

---

## Step 3 — Current-brand reading

**Owner:** AI drafts, AD corrects and signs off.
**Purpose:** Describe what the brand currently is, from approved sources only.

**Inputs:** Approved source list from Step 1.

**Outputs:** Completed [`current-brand-reading.md`](../../templates/rebranding/current-brand-reading.md) and [`source-register.md`](../../templates/rebranding/source-register.md).

**Exit gate:**
- [ ] Every factual claim traces to a registered source, or is labeled as unverified.
- [ ] Direct observations are separated from interpretations.
- [ ] No company history, customer characteristics, sourcing claims, product facts, business plans, or decision-maker preferences have been invented.
- [ ] Missing evidence is listed with a named owner who could supply it.
- [ ] AD has reviewed and recorded the number of factual corrections made.

---

## Step 4 — Territory generation

**Owner:** AI generates, AD directs.
**Purpose:** Produce more candidate territories than will be used, so the shortlist is a real choice.

**Inputs:** Step 3 outputs.

**Outputs:** A pool of candidate territories, each stated as a one-sentence premise plus the answer to "what sits at the center of this brand?"

**The distinctness test.** Two territories are materially distinct only if they differ on at least two of:

1. **Center of gravity** — what the brand is fundamentally about (the maker, the material, the customer, the occasion, the institution, the method, the outcome).
2. **Customer promise** — what the customer is told they are getting.
3. **Proof mechanism** — what makes the promise believable.
4. **Primary content engine** — what the brand must keep producing to stay alive.

Territories that differ only in palette, typeface, photographic treatment, or tagline are **stylistic variants of one idea**. Reject them and record the rejection count for the baseline.

**Exit gate:**
- [ ] At least twice as many candidates generated as will be shortlisted.
- [ ] Each candidate passes or fails the distinctness test explicitly, in writing.
- [ ] Superficial variants are recorded as rejected, with the count.

---

## Step 5 — AD shortlist

**Owner:** AD alone.
**Purpose:** Select the territories that will be developed.

**Outputs:** Named shortlist with a one-line rationale per selection, and a one-line rationale per non-selection.

**Exit gate:**
- [ ] The shortlist is the AD's, not a ranking produced by AI.
- [ ] Non-selected candidates are preserved rather than deleted — one may return as a combination element at decision time.
- [ ] Shortlisted territories collectively pass the distinctness test pairwise.

---

## Step 6 — Equal proposal development

**Owner:** AI produces, AD directs and corrects.
**Purpose:** Develop each shortlisted territory to identical depth.

**Outputs:** One completed [`creative-territory.md`](../../templates/rebranding/creative-territory.md) per proposal, plus [`asset-register.md`](../../templates/rebranding/asset-register.md) entries for every asset produced or referenced.

**Depth parity rule.** Every proposal receives the same sections, the same number of representative applications, the same application *types*, and comparable treatment length. If one territory gets a full application suite and another gets two sketches, the comparison is invalid regardless of the scores.

**Exit gate:**
- [ ] Section-by-section parity confirmed across all proposals.
- [ ] Representative applications match in type and count.
- [ ] Every asset carries a provenance label: `sourced`, `generated`, `placeholder`, `self-created`, or `rights-cleared`.
- [ ] Strengths, risks, assumptions, and uncertainties are populated for each — including for the AD's likely favorite.
- [ ] Implementation implications are stated descriptively, with no language implying they are authorized.
- [ ] Production time and human interventions per proposal are recorded.

---

## Step 7 — Evidence, rights, and completeness validation

**Owner:** AI runs the checklist, AD signs off.
**Purpose:** Catch unsourced claims, unlabeled assets, and parity failures before the package reaches the decision-maker.

**Inputs:** All Step 6 outputs.

**Outputs:** Completed [`../../automation/rebranding/validation-checklist.md`](../../automation/rebranding/validation-checklist.md) run.

**Exit gate:**
- [ ] Every factual claim is sourced or labeled uncertain.
- [ ] Every asset has provenance and rights status.
- [ ] Every placeholder is visibly marked as a placeholder in the artifact itself, not only in a register.
- [ ] No approval language appears anywhere in the package.
- [ ] Parity confirmed.
- [ ] Provenance and rights corrections are counted for the baseline.

---

## Step 8 — PDF assembly

**Owner:** AI assembles, AD inspects.
**Purpose:** Produce the review artifact the decision-maker will actually read.

**Outputs:** Rendered PDF plus preserved editable source files.

**Exit gate:**
- [ ] Structure matches [`pdf-outline.md`](../../templates/rebranding/pdf-outline.md).
- [ ] Every proposal uses the identical page structure.
- [ ] The confidentiality and non-authorization mark appears on the document.
- [ ] The rendered PDF has been opened and **visually inspected**, not merely generated without error.
- [ ] Editable sources are preserved alongside the render.
- [ ] Assembly time and layout/consistency corrections are recorded.

---

## Step 9 — AD recommendation

**Owner:** AD alone. AI must not draft the substance.
**Purpose:** Give the decision-maker the benefit of expert judgment without displacing their authority.

**Outputs:** A recommendation stating:
- Which proposal the AD recommends.
- Why it is strongest.
- The strongest preserved alternative.
- The principal risk of the recommended direction.
- What evidence or client feedback would change the AD's judgment.

**Exit gate:**
- [ ] The recommendation is visibly separated from the decision page and labeled as advice.
- [ ] The last item is substantive — a recommendation that nothing could change is a position, not a judgment.

---

## Step 10 — Client decision

**Owner:** Decision-maker alone.
**Purpose:** Record an authorized decision.

**Available decisions:** select · request revision · combine specifically named elements · hold · reject.

**Outputs:** Completed [`decision-receipt.md`](../../templates/rebranding/decision-receipt.md).

**Exit gate:**
- [ ] Reasons are recorded in the decision-maker's own words, not paraphrased into brand language.
- [ ] "Combine" names the specific elements being combined; an unspecified combine is a revision request, not a decision.
- [ ] The receipt states plainly that selection does not authorize implementation.

---

## Step 11 — Feedback capture

**Owner:** AD, with AI transcribing.
**Purpose:** Preserve what was learned about the client's judgment, including what surprised the team.

**Outputs:** Requested changes, unresolved questions, remaining exclusions, and whether a separate implementation brief is required.

**Exit gate:**
- [ ] Surprises are recorded explicitly — the places where the decision diverged from the AD's expectation are the highest-value learning signal.
- [ ] Client-specific feedback is written to the private surface only.

---

## Step 12 — Lesson classification

**Owner:** AD decides; AI proposes candidates.
**Purpose:** Prevent client-specific observations from silently becoming general rules.

Each candidate lesson is classified as exactly one of:

| Class | Meaning | Destination |
|-------|---------|-------------|
| **Client-specific** | True of this engagement, not generalizable | Private surface only |
| **Reusable** | True across rebranding engagements | Eligible for overlay memory, sanitized, after explicit AD acceptance |
| **Held** | Plausibly general but supported by one case only | Held list; revisit after a comparable engagement |
| **Rejected** | Tested and found not to hold | Rejected list, with the reason |

**Exit gate:**
- [ ] Every candidate has exactly one classification.
- [ ] Reusable lessons are sanitized — no client name, no client facts, no client preferences, no engagement-identifying detail.
- [ ] AD acceptance is explicit and per-lesson. Silence is not acceptance.
- [ ] Single-case generalizations default to **held**, not reusable.

---

## Step 13 — Cohort review

**Owner:** AD.
**Purpose:** Close the loop and set up the next comparison.

**Outputs:** Completed [`cohort-metrics.md`](../../templates/rebranding/cohort-metrics.md) and [`calibration-review.md`](../../templates/rebranding/calibration-review.md).

**Exit gate:**
- [ ] All measurable baseline metrics are recorded; unmeasured ones are marked **not measured**, never estimated.
- [ ] Each workflow step is classified per [`automation-map.md`](automation-map.md).
- [ ] No automation improvement is claimed unless a comparable prior engagement supplies the comparison.
- [ ] New automation candidates are logged in [`../../automation/rebranding/candidate-log.md`](../../automation/rebranding/candidate-log.md) as candidates only.
