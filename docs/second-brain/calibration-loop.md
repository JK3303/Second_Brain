# Calibration Loop

A repeatable process for improving human-AI collaboration through structured creative exercises.

## Canonical loop

```
Brief
  -> AI questions and restatement
  -> distinct options
  -> human critique
  -> AI revision
  -> human accepts, rejects, or holds lesson
  -> remaining misunderstanding recorded
```

## Steps

1. **Human states objective** — a brief or question
2. **AI asks clarifying questions** and restates the brief
3. **AI generates materially different options** — not minor variations
4. **Human critiques** — selects, rejects, or redirects
5. **AI revises** and explains what changed and why
6. **Human records the lesson** — accepts into reusable memory, rejects, or holds
7. **AI proposes a reusable rule** from the cycle
8. **Human accepts, rejects, or holds** the proposed rule

## Rules

- Each exercise must preserve the human's original critique, not only the AI's summary of it.
- Disagreements are preserved in the record, never silently flattened.
- The human always has the final decision on whether a proposed rule is accepted, rejected, or held.
- Historical exercises remain as historical evidence — do not rewrite them as generic rules without preserving their original project context.

## Minimum exercise format

```
Brief:
AI output:
Human critique:
Revised output:
Accepted lesson:
Rejected lesson:
Remaining gap:
```

## Reference implementation

- `projects/artistic-director/ai/calibration-set.md` — exercise framework + completed Rootmind exercise
- `projects/artistic-director/ai/collaboration-loop.md` — the 8-step canonical loop with ASCII flow diagram
- `projects/artistic-director/evaluations/` — human reviews, AI self-reviews, and cohort assessments
