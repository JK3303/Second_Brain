# Shared Coffee and Dream contract

## Coffee: useful choices, no second reporting ritual

Every Coffee recovers current direction, the latest relevant handoff, applicable
team items and the next useful action. Refresh sources only when they could
change the recommendation. Rank consequence, urgency and dependencies before
ease of completion. Missing shared evidence never blocks personal orientation.

End with exactly three substantive, distinct choices. Each is one short sentence
naming an action and its benefit: **A — Recommended**, **B**, **C**. Keep Hannah's
orientation primarily Chinese (A may be labelled 推荐). No filler, nested menus,
routine stop choices or invented obligations. When three useful choices cannot
be grounded, state the gap and ask one consequential question instead.

A letter selects the entire visible action within existing authority. Combined
selections retain all selected scopes, executed in dependency order. Carry the
selected wording into current task context; do not require restatement. Finish
selected work through its useful endpoint before another menu. An intermediate
status update is not a new choice point. Selection never independently authorizes
publication, spending, permission changes or external communication. An explicit
current instruction or a genuinely missing action-specific boundary controls.

Mira retains its canonical Journal, private Bridge and whole-day priorities.
Hannah retains her repository evidence packet and Chinese orientation. Jon retains
Artistic Director project re-entry and its project boundaries. No change to
Open Brain synchronization, private reflection or unrelated projects is implied.

## Dream: one shared close

Prepare reviewed Grace Gems contributions from existing inspected evidence,
without asking people to maintain another log. One coordinator composes the
brief and email: decisions needed, blocked work, meaningful progress, next
actions, then coverage. Work still in progress is separately labelled after
next actions when present. Omit empty sections. Pair English and Chinese wording,
retain material uncertainty beside each claim and preserve unresolved variants.
Aim for three meaningful progress items during agent selection; never discard
consequential decisions or blockers to meet a length target. Do not truncate
already-reviewed claims automatically. Detailed provenance stays in the private
evidence record. Missing contributions never mean no work occurred.

## Versioned action and handoff interfaces

Existing `team-contribution-v1` inputs remain valid. An outcome may add `action`:

```json
{
  "schema": "team-action-v1",
  "relevant_to": ["hannah"],
  "request": {"en": "Choose the proof layout", "zh": "选择校样布局"},
  "decision_maker": "hannah",
  "commitment": "proposed",
  "deadline": null,
  "state": "open"
}
```

Participants are mira, hannah, jon or eric. Unknown relevance is an empty list;
unknown decision-maker and deadline are null. Commitment is proposed, accepted
or unspecified; state is open, resolved or superseded. A deadline, when evidenced,
is an ISO calendar date. Attribution is never responsibility. Audience review and
source verification bind the action along with the rest of the contribution.
Old readers reject the extension, so update participating readers before using it;
new readers accept old contributions. Never strip action fields to bypass review.

Composition also writes `current-team-brief.json` (`team-brief-v1`) with stable
outcome/artifact identities, reviewed variants, coverage, an evidence digest and
an explicit timezone-aware through-cutoff (`--through-cutoff` for portable compose).
Unknown cutoff is null and cannot feed re-entry. The brief excludes private source
maps and provenance bodies. Email and brief use the same reconciled evidence.
The brief is a reviewed team artifact, not the private `current-evidence.json`.

The collecting agent reads the latest verified shared brief and current owning
records, then captures two private inputs. The readback receipt contains
`brief_sha256` (canonical JSON digest), `observed_at` and `latest_verified: true`.
The current-state review contains the same digest, its own `observed_at`, and
`items`, mapping the canonical digest of each reviewed variant to open, resolved
or superseded. These declarations record actual reads; do not fabricate them.
The helper checks bindings and freshness, not provider authenticity or truth.
Re-read changed owning records before making consequential recommendations.

Run `team_reentry.py --brief ABSOLUTE_JSON --receipt ABSOLUTE_JSON
--current-state ABSOLUTE_JSON --owner mira|hannah|jon` from the local tools
directory. It performs no network calls or writes. Receipts older than 24 hours,
future timestamps, missing inputs or changed hashes produce a nonblocking gap.
An old brief may still be useful if freshly confirmed latest and its actions
freshly reviewed. Return only explicitly relevant, open decisions, blockers and
next actions; preserve competing variants as disagreement, not assignments.
No action context means no inferred assignment. Unknown/resolved/superseded
current-state variants do not create recommendations.

For Hannah, the agent supplies explicit private paths through
`COFFEE_TEAM_BRIEF`, `COFFEE_TEAM_RECEIPT`, `COFFEE_TEAM_STATE` for that invocation.
Her collector embeds the filtered result in its existing packet. Do not set global
environment variables, auto-discover private files or inspect outside the packet
while composing Coffee. Unconfigured input is reported, not requested every day.
Mira and Jon use the same read-only helper during their existing re-entry.

## Adoption and delivery limits

Merge is not personal adoption. Participant readiness and activation remain
unverified. Follow the [late-arrival policy](team-participant-delivery.md#late-arrivals-receive-once-reconsider-at-the-next-ordinary-close):
preserve reserved/sent briefs and reconsider relevant unresolved work at the next
ordinary Dream, with original dates and renewed review. Preserve existing delivery authority,
stable Drive identities, audience review and duplicate-send protections. No new
schedule, recipient, permission, automatic GitHub publication or memory writer.

## Behavioral acceptance scenarios

- Three real options: A recommended and B/C materially different, with a benefit
  in each sentence; no duplicated action disguised by wording.
- Selection B: execute the previously displayed B, not a historical letter menu.
- Selection A,C: retain both scopes and finish them before offering another menu.
- Work still running: report progress and continue; no premature A/B/C footer.
- A publish boundary: prepare the reviewable result, then honor separate authority.
- Insufficient evidence: one consequential question, no three invented tasks.
- Missing team brief: continue personal Coffee with an explicit coverage limit.
- A resolved or superseded action: exclude it; a disagreement stays qualified.

Automated tests cover format validation, filtering, freshness and rendering.
These conversational scenarios require agent review; tests do not establish
semantic distinctness, translation quality, adoption or real-world time savings.
