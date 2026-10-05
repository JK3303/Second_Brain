"""Shared Intent 1.0.0 conformance; all content and approvals here are fictional."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("conformance_intent", ROOT / "tools/intent.py")
intent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intent)
engine = sys.modules["intent_lifecycle"]

TEXT = """# Fictional intent

## INT-001 | Learn deliberately
Emphasis: ongoing
Why: Understand the work
Progress: Explain a choice
Constraints: Owner decides
Basis: Fictional test only
Sources: none
Links: none
"""


def packet(store, op, text=None):
    current = store.context()
    value = {"op": op, "revision": current["revision"],
             "sha256": current["intent"]["sha256"] if current["intent"] else None,
             "operator_review": "Fictional fixture authorization"}
    if text is not None:
        value["text"] = text
    return value


@pytest.fixture(params=["private", "repository"] + (["core"] if (ROOT / "scripts/mira_attention.py").exists() else []))
def store(tmp_path, request):
    repo = tmp_path / "workspace"
    repo.mkdir()
    if request.param == "core":
        value = intent.CoreAdapter(ROOT, tmp_path / "state")
        value.store.initialize(TEXT)
        return value
    document = repo / "INTENT.md" if request.param == "repository" else None
    value = engine.Store(repo, tmp_path / "state", document)
    value.change(packet(value, "intent-revise", TEXT))
    return value


def test_lifecycle_and_stale_writes(store):
    first = store.context()
    assert first["capability_version"] == "1.0.0"
    assert not first["intent"]["accepted"]
    stale = packet(store, "intent-accept")
    store.change(stale)
    assert store.context()["intent"]["accepted"]
    with pytest.raises(ValueError):
        store.change(stale)
    changed = TEXT.replace("Understand", "Understand cafÃ© ä¸­æ–‡") + "\n"
    store.change(packet(store, "intent-revise", changed))
    current = store.context()
    assert current["intent"]["text"] == changed
    assert not current["intent"]["accepted"]
    checksums = {row["sha256"] for row in store.history()["history"]}
    assert first["intent"]["sha256"] in checksums
    assert current["intent"]["sha256"] in checksums
    if isinstance(store, intent.CoreAdapter):
        assert current["paused"]
        store.change(packet(store, "intent-accept"))
        assert store.context()["paused"]


def test_external_change_invalidates_acceptance(store):
    store.change(packet(store, "intent-accept"))
    path = store.store.root / "intent.md" if isinstance(store, intent.CoreAdapter) else store.document
    path.write_bytes(TEXT.replace("deliberately", "carefully").encode())
    assert not store.context()["intent"]["accepted"]


def test_bad_digest_and_missing_review_refused(store):
    value = packet(store, "intent-accept")
    value["sha256"] = "0" * 64
    with pytest.raises(ValueError):
        store.change(value)
    value = packet(store, "intent-revise", TEXT)
    del value["operator_review"]
    with pytest.raises(ValueError):
        store.change(value)


def test_missing_context_does_not_create_state(tmp_path):
    repo = tmp_path / "workspace"
    repo.mkdir()
    root = tmp_path / "absent"
    value = engine.Store(repo, root)
    assert value.context()["availability"] == "unavailable"
    assert value.history()["history"] == []
    assert not root.exists()


def test_freeform_confirmations_preserved(tmp_path):
    repo = tmp_path / "workspace"
    repo.mkdir()
    raw = '# Confirmed direction\r\n\r\n**Owner:** Fictional person.\r\nä¸­æ–‡ cafÃ©\r\n'.encode()
    document = repo / "INTENT.md"
    document.write_bytes(raw)
    value = engine.Store(repo, tmp_path / "state", document)
    assert value.context()["intent"]["text"] == raw.decode()
    assert not value.context()["intent"]["accepted"]
    assert not value.root.exists()
    value.change(packet(value, "intent-accept"))
    assert value.history()["history"][0]["sha256"] == engine.digest(raw)
    value.change(packet(value, "intent-revise", raw.decode()))
    assert document.read_bytes() == raw


def test_workspace_binding_and_private_boundary(tmp_path):
    repo = tmp_path / "one"
    repo.mkdir()
    value = engine.Store(repo, tmp_path / "state")
    value.change(packet(value, "intent-revise", TEXT))
    other = tmp_path / "two"
    other.mkdir()
    foreign = engine.Store(other, value.root)
    assert foreign.context()["availability"] == "unavailable"
    with pytest.raises(ValueError):
        foreign.change({"op": "intent-accept", "revision": 1, "sha256": engine.digest(TEXT.encode()), "operator_review": "fixture"})
    with pytest.raises(ValueError):
        engine.Store(repo, repo / "state")


@pytest.mark.parametrize("same_bytes", [True, False])
@pytest.mark.parametrize("failure_point", ["before-replace", "after-replace"])
def test_interrupted_revision_fails_closed(store, monkeypatch, same_bytes, failure_point):
    store.change(packet(store, "intent-accept"))
    core = isinstance(store, intent.CoreAdapter)
    if core:
        store.store.change(packet(store, "resume"))
    text = store.context()["intent"]["text"]
    candidate = text if same_bytes else text + "\n"
    stale = packet(store, "intent-revise", candidate)
    if core:
        backend = store.store
        original = backend.replace_intent_file
        def fail_document(path, raw):
            if path == backend.root / "intent.md":
                if failure_point == "after-replace":
                    original(path, raw)
                raise OSError("simulated interruption")
            return original(path, raw)
        monkeypatch.setattr(backend, "replace_intent_file", fail_document)
    else:
        original = engine.atomic
        def fail_document(path, raw):
            if path == store.document:
                if failure_point == "after-replace":
                    original(path, raw)
                raise OSError("simulated interruption")
            return original(path, raw)
        monkeypatch.setattr(engine, "atomic", fail_document)
    with pytest.raises(OSError):
        store.change(stale)
    current = store.context()
    assert current["pending"]
    assert not current["intent"]["accepted"]
    if core:
        assert current["paused"]
        with pytest.raises(ValueError):
            store.store.change(packet(store, "resume"))
    with pytest.raises(ValueError):
        store.change(packet(store, "intent-accept"))
    monkeypatch.undo()
    with pytest.raises(ValueError):
        store.change(stale)
    store.change(packet(store, "intent-revise", candidate))
    assert not store.context()["pending"]
    store.change(packet(store, "intent-accept"))
    assert store.context()["intent"]["accepted"]
    if core:
        assert store.context()["paused"]


def test_write_guard_before_any_state_creation(tmp_path):
    repo = tmp_path / "workspace"
    repo.mkdir()
    def refuse():
        raise ValueError("unapproved setup")
    value = engine.Store(repo, tmp_path / "state", write_guard=refuse)
    with pytest.raises(ValueError):
        value.change(packet(value, "intent-revise", TEXT))
    assert not value.root.exists()


def test_inactive_instance_context_and_write_gate(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "intent-capability.json").write_text(json.dumps({
        "capability_version": "1.0.0", "adapter": "approved-instance"}))
    (tmp_path / "tools/history.py").write_text('def approved(root):\n    raise ValueError("inactive")\n')
    before = set(tmp_path.rglob("*"))
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        assert intent.context(tmp_path)["availability"] == "unavailable"
        with pytest.raises(ValueError):
            intent.configured(tmp_path)
    finally:
        sys.dont_write_bytecode = old
    assert set(tmp_path.rglob("*")) == before


def test_release_manifest_exact_shared_bytes():
    manifest = json.loads((ROOT / "intent-capability.json").read_text())
    assert manifest["capability_version"] == engine.VERSION == "1.0.0"
    for name, sha in manifest["shared_files"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name


def test_core_existing_acceptance_not_migrated(store):
    if not isinstance(store, intent.CoreAdapter):
        return
    store.change(packet(store, "intent-accept"))
    raw = (store.store.root / "intent.md").read_bytes()
    before = store.context()
    reopened = intent.CoreAdapter(ROOT, store.store.root)
    assert reopened.context() == before
    assert (store.store.root / "intent.md").read_bytes() == raw
