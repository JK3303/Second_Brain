# Intent

## What it does

This skill helps an owner review enduring intentions, propose revisions and
accept exact reviewed bytes. Its optional Python lifecycle tools preserve
revision history in private storage and refuse stale or damaged state.

## Prerequisites

- A working Open Brain instance and an AI client that can load a plain-text skill.
- Python 3.10 or newer for the optional lifecycle tools.
- Owner authorization before saving a revision or accepting its digest.
- pytest 9.1.1 only when running the fictional conformance suite.

This package does not connect to an Open Brain database or MCP server. The
instance is the receiving environment; installation grants no capture, scheduled
work, execution, publishing or personal adoption authority.

## Step-by-step instructions

1. Place this complete folder at `skills/intent` in your receiving checkout.
   Leave root instructions, tools, existing intent documents and personal stores
   unchanged. Load [SKILL.md](SKILL.md) in your client when intent review is requested.
2. Read [the lifecycle guide](docs/intent-capability.md). Run tool commands from
   this package directory so the manifest and workspace binding stay together:

   ```sh
   cd skills/intent
   python tools/intent.py context
   ```

   Missing state returns unavailable without creating storage. This is expected
   before an owner has approved their first saved entry.
3. Propose changes conversationally. Only after explicit saving authorization,
   prepare a private JSON packet using the guide's revision and digest fields,
   then run `python tools/intent.py revise --input ABSOLUTE_PRIVATE_JSON`.
   Acceptance is a separate owner decision; use `accept` only for the exact
   authorized revision and digest. Read back context and history after writes.
4. For fictional validation, install the test dependency and run the suite:

   ```sh
   python -m pip install pytest==9.1.1
   python -m pytest -q tests/test_intent_conformance.py
   ```

   This suite checks portable lifecycle behavior; it does not prove owner
   adoption or own-instance testing. Repository CI installation is a separate
   maintainer proposal rather than part of this folder.

## Expected outcome

An authorized revision preserves old and new snapshots and clears acceptance.
An authorized acceptance binds the current revision and exact SHA-256 digest.
Damaged history produces unavailable context; stale writes are refused. Reads
of missing state leave the document and private storage absent.

## Troubleshooting

- **Unavailable context:** inspect the private manifest/state binding and history;
  do not initialize or repair state without owner authorization.
- **Stale revision or digest:** read fresh context, re-review the intended action
  and prepare a packet for that exact state instead of retrying blindly.
- **Linked path or invalid storage location:** choose a real private directory
  outside every Git checkout with `--state-root`; never put state in this folder.
- **Leftover lock or interrupted write:** verify no writer is active and follow
  separately authorized recovery; do not restore acceptance or clear flags manually.

## Upgrade and provenance

This package rearranges the portable lifecycle code and tests from the earlier
public Intent proposal at commit `e3589b874dd81b4404b0238d3d078946c9871577`.
Their bytes and existing authorship are preserved. Mira prepared this packaging
revision; capability version remains 1.0.0 and package version is 1.0.1.
The [manifest](intent-capability.json) retains the original landed source pin
and records the packaged resources. Original source license obligations remain.

The workspace binding is now this package directory. An older repository-root
private store is not automatically reused, migrated or accepted. Moving folders
also changes the binding. Any migration requires a separate owner-reviewed plan.
No receiving-instance demonstration or owner adoption is claimed by packaging.
