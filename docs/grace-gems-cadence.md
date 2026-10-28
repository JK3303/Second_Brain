# Grace Gems daily consolidation - proposal for Jon

The purpose is a useful team email produced from work already done, not another
journal for Jon to maintain. This is a review candidate; merge is not personal
adoption, scheduling activation, email permission or a change to business policy.

## The rhythm

- **Re-entry:** use the existing Artistic Director handoff and boundaries for a brief Grace Gems orientation; do not add or replace a global Coffee command.
- **During authorized work:** finish the result and update the existing owning
  record within current permission. Do not create a second manual progress log.
- **Grace Gems dream / daily closeout:** the agent gathers relevant evidence,
  consolidates duplicates and corrections, preserves authorized current records,
  and prepares one concise English/Simplified Chinese team-email draft.
- **Daily run, after activation:** the same agent prompt runs at Jon's chosen
  business-day cutoff. It checks repository/session evidence and available
  connected email/Drive sources, then regenerates the stable draft. No scheduler
  or email service is activated by this proposal.

Example: a brief was drafted, corrected and uploaded during three conversations.
The update reports one corrected, verified uploaded brief with its current link;
it does not report three completed tasks. If the upload was not verified, it says
local/draft or upload unverified. A missing invoice match remains a blocker;
preparing a payment summary does not establish that payment was reconciled.

Only Grace Gems team-relevant material enters the email. A Grace Mar business
record can support a fact relevant to Grace Gems, but this does not authorize
sharing that entire record, private mentoring, unrelated clients or family work.
The agent reviews the selected wording and links before setting the audience
field. The script validates structure/provenance, not the truth, confidentiality
or translation quality of arbitrary prose; human/agent judgment remains required.

## Compile and inspect a draft

The agent, not Jon, prepares the temporary JSON packet described below from
inspected sources. `repo_root` is the checkout containing the actual source files.
External evidence is represented by the provider reference and retrieval time;
it must have been read by the collecting agent, not inferred from a filename.

Type this command from the repository root, substituting the actual business
date, timezone and temporary packet location:

```sh
python3 tools/grace_gems_daily.py --date YYYY-MM-DD --timezone AREA/CITY --evidence /path/to/packet.json --repo-root . --output /approved/private/location/grace-gems-daily
```

The compiler verifies local file hashes, source references, evidence dates and
audience labels before writing. It produces `current-team-email.md` and
`current-evidence.json` on the explicitly designated private surface outside the checkout. Reruns update these
stable names; prior differing bytes are preserved under `.history/`. Identical
reruns do not add another version. Invalid input leaves prior output untouched.
It does not fetch connectors, edit source records, create a Gmail draft, send
email, synchronize Drive, commit or push. These remain agent/provider operations
under existing authority. A local Markdown draft is not a delivered email.

### Evidence packet v1

Top-level fields:

| Field | Meaning |
|---|---|
| `version` | `1` |
| `date`, `timezone` | Explicit business date and IANA zone; match CLI arguments |
| `coverage` | One row each for `session`, `repository`, `email`, `drive`: `status` is `checked`, `unavailable` or `not_applicable`, with a concise bilingual `en`/`zh` explanation of exactly what was inspected or missing |
| `sources` | Source rows: unique `id`, `kind` (`repo_file` or `external`), `ref`, timezone-aware `retrieved_at`; local files also require exact `sha256` |
| `facts` | Selected team-safe facts; empty is allowed and is not proof of no work |

Each fact has a unique `id`, `category` (`progress`, `working`, `blocker`,
`decision`, `next`), `evidence` (`verified`, `reported`, `proposed`), explicit
`audience: grace-gems-team`, `event_date`, `source_ids`, and the matching concise
`en` / `zh` wording. Progress may be verified or reported, never proposed.
Older facts are permitted only as `blocker`, `decision` or `next` with
`carry_forward: true`; they are labeled as earlier context rather than new work.
Future facts and source-less facts are rejected. Sources can be older documents
retrieved now: their old publication date must not be rewritten as today's event.

`repo_file.ref` is a relative path inside the checkout; traversal and escaping
symlinks are rejected. `external.ref` is an HTTPS provider reference, not a local
path or credential. Source references remain in the private evidence file.
An optional `share_url` on a fact is an audience-reviewed HTTPS link; it is the
only evidence URL included in the email. Access still needs provider permission.
Never put credentials in URLs or use signed bearer download links.

The script deduplicates facts with identical category, evidence, date and bilingual
wording. The agent must reconcile semantically duplicated or contradictory claims
before compilation. Declared-source coverage is never represented as exhaustive
access to Jon's work. Missing sources and the no-selected-facts case appear
plainly in the draft. Reported and proposed statements remain labeled.

## Candidate daily-agent prompt

> Use the repository Grace Gems cadence skill. Determine the explicit business
> date using the approved timezone and cutoff. Inspect current authorized session,
> repository, email and Drive evidence relevant to Grace Gems, including earlier
> unresolved blockers only when still supported. Do not require Jon to fill a
> log. Consolidate repeated work and corrections into one result; check delivered
> artifacts where relevant. Preserve current records only within existing authority
> and follow the adopted paired-report route when it applies. Select concise
> team-safe bilingual facts and reviewed links, record missing source coverage,
> compile and read back the stable daily draft. Keep a draft separate from sent
> mail. Stay quiet on unchanged reruns; surface a material change, failure or
> consequential decision. Do not send without applicable explicit sending authority;
> reconcile provider history before any authorized retry.

## Activation decisions, only when Jon chooses to use it

Choose the daily time and business timezone, accessible source accounts/locations,
and whether the result remains a draft or may be sent under an explicit standing
policy. Sending requires the confirmed sender and exact team recipient list, plus
the scope of content permitted and handling of incomplete evidence. A scheduled
draft can be activated without granting sending permission. Do not infer these
choices from old team correspondence or this PR.

Respect the Artistic Director project membrane, charter boundaries, rebranding
authority boundaries and automation-adoption gate. No operational source packet,
filled report or team draft may be committed to this public method repository.
The CLI requires an output path outside the checkout; this is a containment check,
not permission to designate that path. Jon must designate the private surface.
Keep creative selection, client approval, rights clearance and implementation
authority distinct in the digest. Do not promote any client fact to global memory
or trigger autodream-brain-sync. Adoption evidence and efficiency improvements
are not established by the compiler's tests. Use existing authorized
correspondence preservation rather than another mailbox mirror.

Official references: [repository skills](https://learn.chatgpt.com/docs/build-skills)
and [scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).
The host's actual capabilities and access must be checked at activation.

This method is prepared in Second_Brain's Open Brain lineage. For the broader
practical systems behind that work, see [Nate B. Jones's newsletter](https://substack.com/@natesnewsletter)
and [Nate's site](https://natebjones.com). This cadence does not capture client
evidence into Open Brain or imply Nate's endorsement of a client workflow.
