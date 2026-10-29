# Explicit Dream contribution delivery

This candidate supplies an agent-owned final step after a successful, explicitly
user-invoked Dream in the Grace Gems project. It does not hook unattended autodream,
individual memory writes, personal synchronization or timers. Personal reflection
finishes once; delivery failure never reruns it. Merging does not activate delivery.

The participant must first adopt this route, designate private storage outside Git,
approve source identities, identify the actual host and verify Drive access to the
exchange folder. Credentials remain in the host's credential service. Configuration,
source maps, completion records, captures, bindings and history stay in that private
storage. No real participant configuration is supplied by the package.

The portable `team_delivery.py` helper has four operations, all without networking:

| Operation | Result |
| --- | --- |
| `status --config PRIVATE/config.json --host ACTUAL_HOST` | Read readiness and outstanding state without initializing storage. |
| `prepare --config … --host … --completion PRIVATE/completion.json --packet PRIVATE/reviewed.json --source-map PRIVATE/source-map.json --revision 1` | Validate activation, close evidence, review and source hashes; preserve immutable intent and export. |
| `check-upload --config … --host … --intent SHA256 --capture PRIVATE/capture.json [--download PRIVATE/download.json]` | Decide create, guarded update, verified, or blocked using fresh provider evidence. |
| `record-upload` with the same arguments | Advance the binding only after matching provider readback. |

Use the participant package's local tools directory. Source-map values are absolute
paths to authorized originals or exact provider captures; source IDs are opaque.
The existing compiler remains available for local export even when delivery is blocked.

## Private activation and completion records

Configuration fields are `private_root`, `owner` (`hannah` or `jon`),
`project: grace-gems`, `host`, `account`, `folder_id`, `drive_id`, `adopted: true`,
`adopted_at`, `adoption_evidence: {path, sha256}`,
`allowed_sources: {ID: ABSOLUTE_AUTHORIZED_SOURCE_PATH, …}`, and
`drive_access: {verified: true, account, folder_id, drive_id, observed_at}`.
Acquire Drive evidence freshly before execution; its timestamp must be within five
minutes. Populate these values from participant authority and actual observations.

After the personal close succeeds, the active agent writes a completion declaration:
`status: completed`, `trigger: explicit-project-dream`, `host`, `project`,
`declaration_kind: agent-observed`, `completed_at`, `evidence: {path, sha256}`,
`invocation_ref` pointing to the user's actual invocation evidence,
`record_id` explicitly identifying a local adapter record, `native_session_ref`
containing the actual host reference when available (otherwise null), and `basis`
matching the reviewed contribution. Basis contains `id`, `version`, `sha256`,
`observed_at`; the latter equals completion time. Do not invent a native run ID.
This is an evidence-supported agent declaration, never independent machine attestation.
Failed, missing, pre-adoption, future, or older-than-24-hour completion blocks delivery.

Exchange date uses **America/Denver**, with closes before 06:00 assigned to the
preceding business date. Personal Journal calendars remain unchanged. One explicit
close can produce one reviewed contribution; changed content needs renewed audience
review and an explicitly higher contribution revision.

## Agent connector sequence

1. Run status and prepare. Retain the returned intent digest. Local export is
   `current-contribution.json`; the remote name is exactly
   `hannah-current-contribution.json` or `jon-current-contribution.json`.
2. Fetch destination folder/shared-drive metadata, perform a complete exact-name
   search in that folder, and download any matched file. Never infer zero matches
   from a partial page. Multiple matches block creation. Capture actual account,
   folder ID, drive ID, observed time, exact name, search completeness, matches and
   downloaded file ID. Each match contains `id`, `name`, `mime_type`, `parent_ids`,
   `drive_id`, `version` and `trashed`. Keep bytes separately.
3. Record `prior_write_outcome: not-attempted` only before any write of this intent.
   Before sending a mutation, persist `uncertain` in its existing private capture
   and retain the intent. A timeout/interruption must never reset this to not-attempted.
   A zero-match bootstrap permits creation only before an attempted write. Otherwise
   reconcile destination/history; never blindly recreate or retry.
4. Run check-upload. Create only the owner's exact filename in the verified folder;
   update only its bound ID with the returned required provider version. If the
   connector cannot enforce a version precondition, block the update. Independent
   edits block replacement. Same-close/same-digest bytes need verification, not upload.
5. Fetch metadata and downloaded bytes again, then run record-upload. Verify ID,
   MIME type, parent, shared drive and bytes. Only this establishes verified delivery.
   Preserve prior intent/readback history. An upload success response is insufficient.

The agent must reconcile an uncertain write before another preparation or write.
The helper trusts provider captures as agent evidence; it cannot authenticate a
fabricated capture or enforce the connector's network behavior.

Mira alone fetches available contributions, reconciles the shared bilingual brief,
and composes/sends the combined email under its existing reservation, duplicate-search
and sent-message verification controls. Missing owners remain explicit. After sending,
later contributions neither trigger another email nor rewrite the sent brief.
Late-arrival handling remains a separate unresolved policy.

At Coffee, fetch the latest verified shared brief and check relevant unresolved
items against current owning records before supplying the existing re-entry helper.
Hannah receives them only through the Coffee evidence packet and retains Chinese
orientation. Jon retains the Artistic Director/project boundary and existing Open
Brain synchronization. Missing shared evidence does not block personal orientation.

Synthetic tests establish capability only. Before activation, verify adoption,
installation, actual host identity, designated private storage, sources and Drive
access on the participant's host. The next ordinary eligible Dream supplies the
first real delivery check; there is no additional daily ritual. Observed usefulness
requires real use and must not be inferred from test success.
