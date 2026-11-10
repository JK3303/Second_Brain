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
Follow the late-arrival policy below; reservation freezes the bundle and the next
ordinary close reconsiders relevant unresolved work with original dates.

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

## Late arrivals: receive once, reconsider at the next ordinary close

Apply this policy after participant adoption within
the existing explicit Dream workflow; it creates no timer, waiting window, second
daily email, reporting queue, new recipient or participant activation. Arrival means
Mira has actually fetched and verified the contribution, not merely that an owner
reports uploading it. An upload receipt proves delivery to Drive, not inclusion in
an email or receipt by every teammate.

The **send reservation** freezes the reviewed email and its matching shared brief
and evidence. A prepared draft before reservation is provisional. The sent brief
must never be retroactively changed to imply a late contribution was included.
The stable `current-team-brief.json` may advance to a genuinely new eligible close;
that is a new dated brief, not a rewrite of the earlier sent snapshot. Preserve the
earlier bytes and reserved envelope in existing private/Drive history.

| Arrival state | Required disposition |
| --- | --- |
| Before preparation or before reservation | If the contribution matches the current exchange date/project, review and verify it. If it changes the draft, recompose the whole bundle, renew audience review and verify any replacement shared copy before reservation. Do not wait indefinitely for missing owners. |
| After reservation, with send outcome uncertain | Freeze the reserved bundle. Reconcile that send using its existing evidence; do not release the reservation, replace the brief or send again because a contribution arrived. Other dates may proceed independently under existing rules. |
| After verified send | Accept an otherwise eligible verified owner upload, but report in the current conversation or next ordinary handoff that it arrived after the cutoff and was not included in that sent brief. Do not amend finalized close records, resend, patch the sent summary or create an automatic addendum. |
| Older or expired close that is no longer eligible to deliver | Preserve the local export and owning evidence. Do not bypass completion freshness, alter its date or replay the old email. Reconsider consequential unresolved work at the next eligible personal Dream. |

Before replacing their current contribution at the next ordinary Dream, each owner
reconciles relevant late work from existing owning records and private delivery
history. Mira does the same for contributions actually received. No one must keep
a second log or obtain a daily acknowledgment. This is not a guarantee that every
historical contribution will be read before its stable remote file advances.

Carry forward only still-relevant **decisions, blockers or next actions** after
checking current owning records. Build a new current-date contribution bound to
the new successfully completed explicit close, with fresh source hashes and renewed
audience review. Retain the item's original `event_date`, stable outcome identity,
and `carry_forward: true`; the existing renderer labels that original date in both
languages. Preserve proposal/commitment distinctions and current relevance. Never
copy an old packet wholesale, invent assignments, or relabel old progress as today.
Resolved, superseded, irrelevant and unknown-state items do not become obligations.

A material correction first belongs in the owning record. At the next eligible
close, describe the actual current correction and its consequence, preserving the
original claim's date and identity in the evidence. A changed artifact revision or
decision must be real, not invented to pass today's-date validation. Do not use a
cross-day `supersedes` reference whose target is absent from the exchange; the
compiler deliberately rejects that. Unchanged completed historical progress stays
in history and need not be repeated in a daily email.

Coffee continues to use only relevant unresolved items from the latest verified
brief and fresh owning-record checks. Late raw contributions are not silently
injected as though already reconciled into that brief. A participant's own late
work can still inform their ordinary personal evidence: Hannah through her packet,
Jon through the Artistic Director handoff, and Mira through existing owning records.
State missing shared coverage honestly; personal orientation does not wait.

If a late blocker or correction makes waiting for the next close consequential,
surface the specific impact and needed decision in the active conversation.
Additional outreach requires its own applicable authority; urgency does not
authorize another daily email or a new recipient. No automatic alert is added.

Acceptance examples: a pre-reservation late decision requires renewed review;
an uncertain send remains reserved; a post-send old progress item stays historical;
an unresolved prior-day blocker enters the next contribution with its original date;
a resolved blocker is excluded; a late correction changes the owning record, not
the sent brief. These dispositions use existing compiler and duplicate-send gates.
Including this policy in a draft PR does not establish participant adoption or
claim that an installed agent already follows it.
