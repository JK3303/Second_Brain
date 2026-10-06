# Intent capability 1.0.0

Enduring intent answers what matters over time. Intent recovery interprets a
current request; neither gives permission to execute work. This capability is
independent of package, activation-runtime, and personal adoption versions.

## Read and propose

Run `python tools/intent.py context` for text, SHA-256, revision, runtime
acceptance, provenance and availability. Reads never initialize personal state.
`history` checks preserved snapshot digests. `validate --input ABSOLUTE_MARKDOWN`
checks a candidate without saving or approving it. Technical validity does not
establish human intent. Preserve purpose, progress, constraints, emphasis and
attributed basis without forcing a particular Markdown layout.

Keep confirmed statements, proposals, historical directions and unknowns distinct.
An existing document's confirmation evidence is not a newly issued runtime
acceptance. When accepted bytes contain qualifications, report both signals.
No questionnaire, scheduled review, or record per conversation is required.

## Explicit writes

Read the original file as UTF-8 bytes. Never reconstruct it from terminal output.
Use a private JSON input file for `revise --input ABSOLUTE_JSON`. It contains
`op: intent-revise`, current `revision`, current `sha256`, exact reviewed `text`,
and `operator_review` referencing actual authorization. For an explicitly approved
first entry, use revision 0 and null digest only when context confirms no entry.
The tool cannot authenticate a person; a review string is not consent.

Revision preserves old and new snapshots and invalidates runtime acceptance.
Use `accept --input ABSOLUTE_JSON` only after separate exact-digest authorization;
its packet contains `op: intent-accept`, current revision and digest, and the
actual review reference. Verify context and history after writes. No operation
changes the owner's intentions merely because this capability was installed.

## Storage and recovery

The manifest selects the adapter. Repository-document mode keeps an established
INTENT.md in place. Private-document mode keeps the document outside Git. Both
use private workspace-bound lifecycle state under the OS user's data directory,
or an explicitly supplied `--state-root` outside all Git checkouts. An approved
personal instance always uses its verified instance state; an override cannot
escape that binding. Its setup and agreement gates remain authoritative.

Cloning or upgrading does not migrate private state or acceptance. Never copy
another person's state. Reads of missing state remain unavailable or unaccepted.
Existing attributed confirmations remain in their original document.

A stale revision/digest, changed workspace, linked path, or invalid history must
be investigated before retrying. An interrupted write exposes pending
state and refuses acceptance. After inspection and explicit owner authorization,
recover by revising from the newly read revision and digest. A leftover lock
requires verifying no writer is active before separately authorized removal.
Do not restore acceptance from a backup or clear a pending flag manually.

Mira Core retains its existing private attention backend and its stricter entry
format. Its existing `mira-attention` commands remain supported. A revision pauses
preparation; accepting intent never resumes it. Core commits revocation and
completion as separate revision transitions; always reread the current revision
rather than assuming an increment of one. Other adapters do not install a
preparation loop. Capability parity is established by the shared conformance
suite, not by adopting identical personal goals or operating systems.

## Release evidence

`intent-capability.json` records version, adapter, source revision/status, and
SHA-256 hashes of shared files. A candidate source pin is not a landed release.
The same tests run against portable adapters and Core's existing backend.
Fictional tests establish behavior, not owner consent or live platform adoption.
