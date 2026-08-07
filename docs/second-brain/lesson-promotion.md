# Lesson Promotion

How observations become durable lessons — and why no lesson is promoted automatically.

## Lesson categories

| Category | What it means | Destination |
|----------|--------------|-------------|
| Accepted | Human-approved reusable rule | `memory/accepted-lessons.md` |
| Rejected | Approach explicitly not to repeat | `memory/rejected-lessons.md` |
| Held | Plausible but unresolved pattern | `memory/open-questions.md` |
| Project-specific | Useful only within one project | Stays in the project area |

## Minimum lesson format

**Accepted lessons:**

```
Lesson:
Evidence:
Applies when:
Does not apply when:
Accepted by:
Date:
Scope: project-specific / reusable
```

**Rejected lessons:**

```
Approach to avoid:
Why rejected:
What to do instead:
Evidence:
Date:
```

## Rules

- No automatic promotion. The agent may propose a lesson, but only the human may accept it into reusable memory.
- A project-specific observation does not become a global rule merely because the AI encountered it.
- Lessons require explicit human acceptance before entering `memory/accepted-lessons.md`.
- Rejected lessons are not just prohibitions — they must include constructive alternatives.
- Open questions mark areas where the AI must not pretend confidence.
- Lessons include scope and applicability conditions, not just the rule itself.

## Reference implementation

The Artistic Director project maintains the reference implementation:

- `projects/artistic-director/memory/accepted-lessons.md` — Rule / Evidence / Applies when
- `projects/artistic-director/memory/rejected-lessons.md` — Approach to avoid / Why rejected / What to do instead
- `projects/artistic-director/memory/open-questions.md` — numbered unresolved questions
- `projects/artistic-director/memory/role-principles.md` — role-level rules that survive holder changes
