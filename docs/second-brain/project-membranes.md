# Project Membranes

Each project in `projects/` operates within a membrane — a boundary that controls what information enters, leaves, and persists.

## What a membrane defines

Every project README must identify:

- **Owner** — who holds creative and decision authority
- **Purpose** — what the project is for
- **State** — current phase
- **AI contribution** — how AI systems are used
- **External-authority boundary** — what the project cannot authorize
- **Current entry point** — where to start reading
- **Next review** — what happens next and who decides

Projects that handle sensitive, client, or rights-dependent material should additionally specify:

- **Privacy level** — public, internal, or restricted
- **Allowed sources** — what the project may use
- **Prohibited sources** — what the project must not use
- **What may become reusable memory** — lessons that could be promoted to global scope
- **What must remain project-local** — facts, decisions, and material that must not leak

## Rules

- Project-local information does not become global memory automatically.
- Encountering a fact inside a project does not make it a repo-wide fact.
- A draft, recommendation, or polished artifact inside a project is not approval to publish, deploy, spend, or contact external parties.
- Reusable work moves from `projects/` into `recipes/`, `skills/`, or another shared surface only through a separate review.

## Reference implementation

`projects/artistic-director/charter/boundaries.md` is the reference implementation. Grace Gems facts, customer information, rights questions, campaign decisions, and client materials are bounded within that project.

## Template

See `projects/_template/manifest.md` for a reusable project manifest template.
