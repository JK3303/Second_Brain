# Intent Recovery

When a human instruction is compressed, ambiguous, or could mean more than one thing, the agent must recover intent before acting.

## Procedure

1. Preserve the literal human wording.
2. State the inferred meaning separately.
3. Distinguish creative intent from factual or business claims.
4. Preserve a material alternative interpretation.
5. Ask for correction when ambiguity would change the next action.
6. Never treat recovery as authorization.

## Minimum receipt

```
What was said:
What I think it means:
Clearer articulation:
Practical implication:
Uncertainty:
Next question or action:
```

## Rules

- Recovered intent is an inference, not a fact.
- If the human corrects the inference, record the correction.
- Do not silently flatten ambiguity into the interpretation that is easiest to act on.
- Do not treat a recovered intent as permission to publish, spend, deploy, or contact external parties.

## Project-specific extensions

Projects may extend this receipt with additional fields (e.g., the Artistic Director adds creative-intent fields like alternative interpretations and lesson-state tracking). Extensions must remain compatible with the canonical receipt — add fields, do not remove or rename them.

See `projects/artistic-director/ai/prompt-patterns.md` and the creative-intent handling template in the Phase 2 coding-agent instructions for the reference extension.
