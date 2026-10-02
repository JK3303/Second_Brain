# Decision Receipt Validation

```text
Named Markdown receipts -> completeness + cross-reference checks -> review findings
Human approval and factual verification remain outside this validator.
```

## What it does

Check the existing Second_Brain decision-receipt format before relying on it in a
handoff. Find missing evidence, placeholders, duplicate IDs, incomplete holds,
unknown states, and missing, cross-project, or cyclic replacements. Files are never
edited. This turns the [decision-state contract](../../docs/second-brain/decision-states.md)
into optional, reproducible checks without changing historical creative logs.

## Prerequisites

- Python 3.11+; standard library only.
- A Second_Brain/Open Brain checkout and local decision receipt files.
- No database, credentials, network access, or new dependencies.

## Step-by-step instructions

1. Run the fictional example from the repository root:

   ```bash
   python recipes/decision-receipts/validate.py recipes/decision-receipts/example.md
   ```

2. For a real decision, use the existing
   [receipt template](../../projects/_template/decision-receipt.md). Record the
   owner's actual decision and evidence; do not invent them to satisfy the tool.
   Use one receipt per file, as plain key/value text or a fenced code block.
   Indent continuation lines for multiline evidence or uncertainty.

3. Validate the exact set of related receipts:

   ```bash
   python recipes/decision-receipts/validate.py /your/private/decision-1.md /your/private/decision-2.md --format json
   ```

4. Fix transcription gaps or ask the decision owner to resolve missing judgment.
   Leave unresolved fields unresolved until evidence exists. A failed check is
   useful information; it is not a request for an agent to manufacture approval.

## Expected outcome

Exit code 0 means structurally complete receipts. Code 1 means review findings;
code 2 means unreadable or invalid input. JSON includes fields and their source
line numbers, plus per-file errors. Text output summarizes actionable gaps.
An empty stock template should fail, while the included fictional hold passes.

## State-specific fields

The eleven fields in the existing template remain required. These explicit extra
fields make its narrative rules checkable:

| State | Additional fields |
| --- | --- |
| `held` | `Missing item`, `Why it matters`, `Needed from` |
| `rejected` | `Reconsider when` |
| `superseded` | `Reconsider when`, `Superseded by` (another Decision ID in the input set) |

Advanced states such as `approved` and `executing` require a non-placeholder
authority claim; obvious `None`, `pending`, and negative claims fail. **This is a
completeness check, not approval authentication or natural-language adjudication.**
A fabricated or ambiguous authority statement can still pass syntax checks.
Review the actual source and scope before any action. Creative approval never
automatically authorizes publication, spending, or deployment.

Receipt IDs must be unique across the supplied set. Replacement chains must remain
inside the same project and cannot contain cycles. No directory crawl, remote
lookup, historical log conversion, memory admission, or execution occurs.

## Validation

```bash
python -B -m unittest discover -s recipes/decision-receipts -p "test_*.py" -v
```

Tests cover the canonical format, multiline fields, duplicate identifiers, lifecycle
requirements, replacement graphs, placeholders, malformed fences, size limits,
CLI exit codes, and source non-mutation. Tests use a writable OS temporary directory.
The recipe operates on local repository files; no live Supabase test is claimed.

## Troubleshooting

- **Missing replacement:** include the named replacement receipt in the same command.
- **Unknown field:** check spelling; the validator deliberately rejects silent typos.
- **Historical table fails:** tables are not receipts. Preserve history; use the
  template for a new decision only when the owner actually makes one.
- **Large input:** each receipt is limited to 256 KB. Link to evidence rather than
  embedding an entire transcript. JSON output inherits the receipt's privacy.

## Provenance

Based on Second_Brain's decision states and receipt template, built on
[Nate B. Jones's Open Brain](https://github.com/NateBJones-Projects/OB1).
More practical systems: [Nate's writing](https://substack.com/@natesnewsletter)
and [website](https://natebjones.com).
