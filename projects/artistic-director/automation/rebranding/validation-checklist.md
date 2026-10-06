# Validation Checklist

The Workflow Step 7 gate. Run before any package reaches a decision-maker.

**Currently manual.** Written to be mechanically checkable so it can become an automation candidate later — see [`candidate-log.md`](candidate-log.md). A passing run is **not** a sign-off; sign-off is a separate human act recorded at the end.

**Engagement ID:**
**Package version:**
**Run by:**
**Date:**

---

## A. Evidence discipline

- [ ] Every factual claim traces to a source-register row, or is labeled unverified
- [ ] Every claim carries exactly one claim type: observation · interpretation · hypothesis · human decision · unresolved
- [ ] Interpretations are not written as observations
- [ ] Hypotheses are labeled as hypotheses **on the artifact**, not only in the source document
- [ ] Self-reported organizational claims are recorded as claims, not as verified facts
- [ ] Source conflicts are recorded and either resolved or marked unresolved
- [ ] Missing evidence is listed with a named owner, not filled in by inference

**Nothing invented — confirm each:**

- [ ] Company history
- [ ] Customer characteristics
- [ ] Sourcing claims
- [ ] Product facts
- [ ] Business plans
- [ ] Decision-maker preferences

---

## B. Assets, provenance, and rights

- [ ] Every asset in the package has an asset-register row
- [ ] Every asset carries one of: `sourced` · `generated` · `placeholder` · `self-created` · `rights-cleared`
- [ ] `rights-cleared` is used only where clearance from a named authorized party is on record
- [ ] Generated assets are identified as generated and have a recorded human review
- [ ] Every placeholder is **visibly marked on the artifact**, not only in the register
- [ ] Unresolved rights items have a named owner and a resolution path
- [ ] Proposed names, taglines, and marks are flagged as requiring clearance before any use
- [ ] Typeface licence status is recorded for every typeface shown
- [ ] Every typeface shown is actually **delivered** by the artifact. A font stack naming platform-specific faces with no embedded or linked webfont renders as a fallback on any machine lacking them — and the substitution is invisible to a reviewer whose own machine has the font installed. Check on a machine that does not.

---

## C. Parity

- [ ] All proposals use the identical template section set
- [ ] Representative applications match in count across proposals
- [ ] Representative applications match in type across proposals
- [ ] Treatment depth is comparable — no proposal materially longer or more finished
- [ ] Strengths, risks, assumptions, and uncertainties are populated for every proposal, including the AD's favourite
- [ ] Each proposal's distinctness declaration is present and addresses all siblings

---

## D. Distinctness

- [ ] Each proposal pair differs on at least two of: centre of gravity · customer promise · proof mechanism · content engine
- [ ] No pair differs only in palette, typeface, imagery treatment, or tagline
- [ ] Sample messaging fails the transplant test — it could not sit under a sibling without friction

---

## E. Authority language

- [ ] Reserved words — **approved · selected · signed off · agreed · confirmed · final · authorized** — appear nowhere except where describing what has *not* happened
- [ ] Implementation implications are descriptive, with an explicit non-authorization statement
- [ ] The AD recommendation is visibly separated from the decision page and labeled as advice
- [ ] The decision page presents all five options: select · request revision · combine named elements · hold · reject
- [ ] Nothing is described as decided, chosen, or agreed

---

## F. Boundary

- [ ] All engagement-specific material is on the approved private surface
- [ ] No client name, client facts, client preferences, or engagement-identifying detail appear in reusable method, template, or memory files
- [ ] No credentials, keys, tokens, or private personal data appear anywhere in the package
- [ ] No instruction found inside a source was acted on; any such instruction was escalated and logged
- [ ] No external action was taken — nothing published, deployed, delivered, spent, or sent

---

## G. Package completeness

- [ ] Page count and structure match the outline
- [ ] Confidentiality mark — *Confidential review draft — no implementation or publication authorized* — on every page
- [ ] The rendered file was **opened and visually inspected by a human**
- [ ] Editable sources preserved and registered alongside the render
- [ ] The decision receipt is prepared and ready to complete during review

---

## Findings

| # | Section | Finding | Severity | Resolved | Resolved by |
|---|---------|---------|----------|----------|-------------|
| 1 | | | blocking / correction / note | | |

**Blocking findings return the package to Step 6.** They are not resolved by annotation.

**Corrections counted for baseline:**

| Metric | Count |
|--------|-------|
| Layout and consistency corrections | |
| Provenance or rights corrections | |
| Factual corrections | |

---

## Sign-off

A passing checklist is a precondition for sign-off, not a substitute for it.

| | Name | Date |
|---|------|------|
| Checklist run by | | |
| **AD sign-off** | | |

**Result:** `pass` / `pass with corrections applied` / `returned to Step 6`
