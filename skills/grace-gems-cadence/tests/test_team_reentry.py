import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from copy import deepcopy
import json
import pytest
import team_contributions as team
from team_reentry import read_context
from test_grace_gems_daily import packet, reviewed, compose

AT = "2026-10-29T14:00:00+00:00"


def action_packet(owner="hannah", category="decision"):
    p = packet(owner)
    p["outcomes"][0].update(category=category, action={
        "schema": "team-action-v1", "relevant_to": [owner],
        "request": {"en": "Choose a proof", "zh": "选择校样"},
        "decision_maker": None, "commitment": "proposed", "deadline": None, "state": "open"})
    return reviewed(p)


def inputs(p=None):
    result = compose(p or action_packet())
    brief = team.shared_brief(result, "2026-10-28T23:00:00+00:00")
    proof = {"brief_sha256": team.digest(brief), "observed_at": AT, "latest_verified": True}
    state = {"brief_sha256": team.digest(brief), "observed_at": AT,
             "items": {team.digest(v): "open" for i in brief["items"] for v in i["variants"]}}
    return brief, proof, state


def test_old_contributions_remain_valid_without_inferred_assignment():
    brief, proof, state = inputs(packet())
    assert team.reentry(brief, proof, state, "mira", AT)["items"] == []
    assert "provenance" not in json.dumps(brief)
    assert "sources" not in brief["items"][0]["variants"][0]


def test_action_context_requires_fresh_audience_review():
    p = action_packet()
    p["outcomes"][0]["action"]["commitment"] = "accepted"
    with pytest.raises(ValueError, match="review is stale"):
        compose(p)


@pytest.mark.parametrize("field,value", [("schema", "v9"), ("commitment", "assumed"),
    ("state", "done"), ("deadline", "tomorrow"), ("relevant_to", ["stranger"]),
    ("decision_maker", "stranger")])
def test_invalid_action_rejected(field, value):
    p = action_packet()
    p["outcomes"][0]["action"][field] = value
    with pytest.raises(ValueError): compose(reviewed(p))


def test_action_first_bilingual_render_and_verified_links_only():
    packets = []
    for index, category in enumerate(["next", "progress", "blocker", "decision"]):
        p = action_packet()
        row = deepcopy(p["outcomes"][0])
        row.update(id=f"c{index}", outcome_id=f"o{index}", category=category,
                   share_url="https://example.org/reviewed")
        packets.append(row)
    p["outcomes"] = packets
    result = compose(reviewed(p))
    output = team.render(result)
    labels = ["Decisions needed", "Blocked work", "Meaningful progress", "Next actions", "Coverage"]
    assert [output.index(x) for x in labels] == sorted(output.index(x) for x in labels)
    assert "待决事项" in output and "选择校样" in output
    assert "https://example.org" not in output
    assert "Unspecified / 未指定" in output
    assert "Proposed / 提议" in output
    assert "source-1" not in output and "Scoped source only" in output
    p["outcomes"][0]["delivery"]["state"] = "verified"
    assert "https://example.org/reviewed" in team.render(compose(reviewed(p)))


def test_reentry_filters_owner_and_current_state():
    brief, proof, state = inputs()
    assert len(team.reentry(brief, proof, state, "hannah", AT)["items"]) == 1
    assert team.reentry(brief, proof, state, "jon", AT)["items"] == []
    key = next(iter(state["items"]))
    for status in ["resolved", "superseded", "unknown"]:
        state["items"][key] = status
        assert team.reentry(brief, proof, state, "hannah", AT)["items"] == []


def test_closed_actions_do_not_appear_as_decisions_needed():
    p = action_packet()
    p["outcomes"][0]["action"]["state"] = "resolved"
    assert "Decisions needed" not in team.render(compose(reviewed(p)))


@pytest.mark.parametrize("change", ["hash", "stale", "future", "latest", "state_hash", "unknown_cutoff", "missing"])
def test_reentry_gaps_are_nonblocking(change):
    brief, proof, state = inputs()
    if change == "hash": proof["brief_sha256"] = "0" * 64
    if change == "stale": proof["observed_at"] = "2026-10-27T14:00:00+00:00"
    if change == "future": state["observed_at"] = "2026-10-30T14:00:00+00:00"
    if change == "latest": proof["latest_verified"] = False
    if change == "state_hash": state["brief_sha256"] = "0" * 64
    if change == "unknown_cutoff": brief["through_cutoff"] = None
    if change == "missing": state = {}
    assert team.reentry(brief, proof, state, "hannah", AT)["items"] == []


def test_relevant_disagreement_keeps_competing_variants():
    a, b = action_packet(), action_packet("jon")
    b["outcomes"][0]["en"] = "Different proposed proof"
    result = compose(a, reviewed(b))
    brief = team.shared_brief(result, "2026-10-28T23:00:00+00:00")
    proof = {"brief_sha256": team.digest(brief), "observed_at": AT, "latest_verified": True}
    state = {"brief_sha256": team.digest(brief), "observed_at": AT,
             "items": {team.digest(v): "open" for v in brief["items"][0]["variants"]}}
    items = team.reentry(brief, proof, state, "hannah", AT)["items"]
    assert items[0]["status"] == "unresolved" and len(items[0]["variants"]) == 2
    assert "Disagreement unresolved" in team.render(result)


def test_file_intake_readonly_and_unavailable(tmp_path):
    brief, proof, state = inputs()
    paths = [tmp_path/f"{i}.json" for i in range(3)]
    for path, data in zip(paths, [brief, proof, state]): path.write_bytes(team.encoded(data))
    before = [p.read_bytes() for p in paths]
    assert read_context(*paths, owner="hannah", at=AT)["items"]
    assert before == [p.read_bytes() for p in paths]
    paths[0].unlink()
    assert read_context(*paths, owner="hannah", at=AT)["items"] == []
