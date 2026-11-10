from copy import deepcopy
import hashlib
import json

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import team_contributions as team


def packet(owner="mira"):
    p = {"schema": team.SCHEMA, "owner": owner, "project": "grace-gems", "date": "2026-10-28",
         "timezone": "America/Denver", "audience": team.AUDIENCE,
         "basis": {"id": "close-1", "version": "1", "sha256": "a" * 64, "observed_at": "2026-10-28T12:00:00Z"},
         "coverage": [{"kind": k, "status": "unavailable" if k == "email" else "checked", "en": "Scoped source only", "zh": "仅限指定来源"} for k in sorted(team.KINDS)],
         "sources": [{"id": "source-1", "version": "v1", "sha256": "b" * 64}],
         "outcomes": [{"id": "claim-1", "outcome_id": "brief", "artifact_id": "brief-file", "revision": "v1",
                       "event_date": "2026-10-28", "category": "progress", "evidence": "verified",
                       "delivery": {"state": "local", "destination": "review folder", "version": "v1", "evidence_id": "source-1"},
                       "source_ids": ["source-1"], "en": "Brief prepared", "zh": "简报已准备",
                       "uncertainty": "Usefulness unobserved / 实际效果尚未观察", "supersedes": []}]}
    return reviewed(p)


def reviewed(p):
    p["review"] = {"reviewer": "reviewer", "sha256": team.review_digest(p)}
    return p


def compose(*packets):
    return team.compose(packets, business_date="2026-10-28", timezone="America/Denver", project="grace-gems", expected_owners=["mira", "hannah", "jon"])


def test_duplicate_owner_delivery_is_one_outcome_with_provenance():
    a, b = packet(), packet("hannah")
    b["sources"][0]["id"] = "independent-readback"
    b["outcomes"][0]["source_ids"] = ["independent-readback"]
    b["outcomes"][0]["delivery"]["evidence_id"] = "independent-readback"
    result = compose(a, reviewed(b))
    assert len(result["results"]) == 1
    assert len(result["results"][0]["variants"][0]["provenance"]) == 2
    assert result["coverage"][1] == {"owner": "jon", "sources": None}
    assert "contribution unavailable" in team.render(result)
    assert "unavailable" in team.render(result)
    assert "draft-not-sent" == result["delivery"]


def test_matching_prose_is_not_identity_and_conflicts_remain():
    a, b = packet(), packet("hannah")
    b["outcomes"][0]["outcome_id"] = "another-brief"
    assert len(compose(a, reviewed(b))["results"]) == 2
    b["outcomes"][0]["outcome_id"] = "brief"
    b["outcomes"][0]["en"] = "Brief needs correction"
    assert compose(a, reviewed(b))["results"][0]["status"] == "unresolved"


def test_revised_artifact_and_cross_owner_correction():
    a, b = packet(), packet("hannah")
    old = a["outcomes"][0]
    new = b["outcomes"][0]
    new.update(revision="v2", en="Corrected brief", zh="已修订简报", supersedes=[{"owner": "mira", "id": old["id"], "sha256": team.digest(old)}])
    new["delivery"].update(version="v2", state="verified")
    result = compose(a, reviewed(b))
    assert len(result["corrections"]) == 1
    assert len(result["results"][0]["variants"]) == 1
    assert result["results"][0]["variants"][0]["outcome"]["revision"] == "v2"


@pytest.mark.parametrize("change", ["date", "timezone", "audience", "private", "source", "review", "delivery", "old", "future"])
def test_invalid_projection_fails(change):
    p = packet()
    if change == "date": p["date"] = "2026-10-27"
    if change == "timezone": p["timezone"] = "UTC"
    if change == "audience": p["audience"] = "private"
    if change == "private": p["raw_transcript"] = "Private body"
    if change == "source": p["outcomes"][0]["source_ids"] = ["absent"]
    if change == "review": p["outcomes"][0]["en"] = "Changed after review"
    if change == "delivery": p["outcomes"][0]["delivery"].update(state="verified", version="old")
    if change == "old": p["outcomes"][0]["event_date"] = "2026-10-27"
    if change == "future": p["outcomes"][0]["event_date"] = "2026-10-29"
    if change != "review": reviewed(p)
    with pytest.raises(ValueError): compose(p)


def test_carry_forward_and_missing_correction_target():
    p = packet()
    p["outcomes"][0].update(category="blocker", event_date="2026-10-27", carry_forward=True)
    assert "2026-10-27" in team.render(compose(reviewed(p)))
    p["outcomes"][0]["supersedes"] = [{"owner": "jon", "id": "missing", "sha256": "c" * 64}]
    with pytest.raises(ValueError, match="target absent"): compose(reviewed(p))


def test_idempotent_order_independent_regeneration_and_history(tmp_path):
    a, b = packet(), packet("hannah")
    first = compose(a, b)
    assert first == compose(b, a)
    folder = tmp_path / "private"
    repo = tmp_path / "repo"
    repo.mkdir()
    files = {"current-team-email.md": team.render(first).encode(), "current-evidence.json": team.encoded(first)}
    team.write_files(folder, files, repo)
    team.write_files(folder, files, repo)
    assert not (folder / ".history").exists()
    old = files["current-team-email.md"]
    files["current-team-email.md"] += b"Review update"
    team.write_files(folder, files, repo)
    assert (folder / ".history" / hashlib.sha256(old).hexdigest() / "current-team-email.md").read_bytes() == old
    assert (folder / "current-evidence.json").read_bytes() == files["current-evidence.json"]
    with pytest.raises(ValueError): team.write_files(repo / "private", files, repo)


def test_cli_compose_and_invalid_input_preserves_current(tmp_path):
    p = packet()
    source = tmp_path / "input.json"
    source.write_bytes(team.encoded(p))
    repo = tmp_path / "repo"
    repo.mkdir()
    output = tmp_path / "output"
    args = ["compose", "--input", str(source), "--date", p["date"], "--timezone", p["timezone"], "--project", p["project"], "--expected-owner", "mira", "--expected-owner", "jon", "--repo-root", str(repo), "--output", str(output)]
    assert team.main(args) == 0
    before = (output / "current-team-email.md").read_bytes()
    p["outcomes"][0]["en"] = "Unreviewed change"
    source.write_bytes(team.encoded(p))
    with pytest.raises(SystemExit): team.main(args)
    assert (output / "current-team-email.md").read_bytes() == before


def test_current_source_bytes_and_no_private_paths_in_export(tmp_path):
    p = packet()
    source = tmp_path / "private-source.txt"
    source.write_bytes(b"Inspected evidence")
    p["sources"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    reviewed(p)
    team.verify_sources(p, {"source-1": str(source)})
    assert str(source) not in team.encoded(p).decode()
    source.write_bytes(b"Changed evidence")
    with pytest.raises(ValueError, match="bytes changed"):
        team.verify_sources(p, {"source-1": str(source)})
    with pytest.raises(ValueError, match="exactly"):
        team.verify_sources(p, {})


def test_export_cli_requires_source_verification(tmp_path):
    p = packet()
    source = tmp_path / "source.txt"
    source.write_bytes(b"Current provider readback")
    p["sources"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    selection = tmp_path / "selection.json"
    selection.write_bytes(team.encoded(reviewed(p)))
    mapping = tmp_path / "map.json"
    mapping.write_text(json.dumps({"source-1": str(source)}))
    repo = tmp_path / "repo"
    repo.mkdir()
    output = tmp_path / "export"
    args = ["export", "--input", str(selection), "--source-map", str(mapping), "--date", p["date"], "--timezone", p["timezone"], "--project", p["project"], "--repo-root", str(repo), "--output", str(output)]
    assert team.main(args) == 0
    assert (output / "current-contribution.json").read_bytes() == team.encoded(p)
    source.write_bytes(b"New unreviewed revision")
    with pytest.raises(SystemExit): team.main(args)
    assert (output / "current-contribution.json").read_bytes() == team.encoded(p)
