"""Portable Intent 1.0.0. No network, capture, automatic consent, or background work."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid

VERSION = "1.0.0"
LIMIT = 1_000_000


class IntentError(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def validate(raw):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= LIMIT:
        raise IntentError("Intent must be nonempty UTF-8 Markdown, at most 1 MB")
    text = raw.decode("utf-8-sig")
    if not text.strip() or "\x00" in text:
        raise IntentError("Intent must contain text without NUL characters")
    return {"capability_version": VERSION, "sha256": digest(raw), "bytes": len(raw),
            "valid": True, "semantic_approval": False}


def safe(path):
    path = Path(path).absolute()
    if path.resolve() != path or any(p.is_symlink() or
            (hasattr(p, "is_junction") and p.is_junction()) for p in (path, *path.parents)):
        raise IntentError("Linked paths are not supported")
    return path


def private(path, workspace):
    path = safe(path)
    if path == workspace or workspace in path.parents or path in workspace.parents:
        raise IntentError("State must be outside the workspace")
    if any((p / ".git").exists() for p in (path, *path.parents)):
        raise IntentError("State must be outside every Git checkout")
    return path


def read_json(path):
    raw = safe(path).read_bytes()
    if len(raw) > LIMIT:
        raise IntentError("Metadata exceeds limit")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise IntentError("Metadata must be an object")
    return value


def atomic(path, raw):
    path = safe(path)
    temporary = safe(path.with_name(path.name + "." + uuid.uuid4().hex + ".pending"))
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode()


class Store:
    def __init__(self, workspace, root, document=None, provenance=None, write_guard=None):
        self.workspace = safe(workspace)
        self.root = private(root, self.workspace)
        self.document = safe(document or self.root / "intent.md")
        # Only an explicit repository INTENT.md or the private canonical file is writable.
        if self.document not in (self.workspace / "INTENT.md", self.root / "intent.md"):
            raise IntentError("Unsupported intent destination")
        self.meta = self.root / "intent-state.json"
        self.provenance = provenance or {}
        self.write_guard = write_guard or (lambda: None)

    def metadata(self):
        if not safe(self.meta).exists():
            return {"workspace": str(self.workspace), "revision": 0,
                    "accepted_sha256": None, "history": [], "pending": False}
        value = read_json(self.meta)
        if value.get("workspace") != str(self.workspace):
            raise IntentError("Workspace binding mismatch")
        if type(value.get("revision")) is not int or value["revision"] < 0:
            raise IntentError("Invalid revision")
        if not isinstance(value.get("history"), list) or type(value.get("pending")) is not bool:
            raise IntentError("Invalid history or pending state")
        return value

    def raw(self):
        path = safe(self.document)
        if not path.exists():
            return None
        raw = path.read_bytes()
        validate(raw)
        return raw

    def context(self):
        result = {"capability_version": VERSION, "provenance": self.provenance,
                  "availability": "unavailable", "revision": None, "intent": None,
                  "mutation_performed": False}
        try:
            meta, raw = self.metadata(), self.raw()
            result.update(revision=meta["revision"], pending=meta["pending"])
            if raw is not None:
                sha = digest(raw)
                result.update(availability="available", intent={"text": raw.decode("utf-8-sig"),
                    "sha256": sha, "accepted": not meta["pending"] and sha == meta.get("accepted_sha256"),
                    "confirmation_evidence": "Preserve attributed confirmation in the document; runtime acceptance is separate."})
        except (OSError, ValueError, KeyError, TypeError):
            result["reason"] = "Intent state is unavailable; inspect binding and integrity before mutation"
        return result

    def history(self):
        return self.checked_history(self.metadata())

    def checked_history(self, meta):
        records = []
        for row in meta["history"]:
            sha = row["sha256"]
            if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
                raise IntentError("Invalid history digest")
            raw = safe(self.root / "intent-history" / (sha + ".md")).read_bytes()
            if digest(raw) != sha:
                raise IntentError("History integrity mismatch")
            records.append(dict(row))
        return {"capability_version": VERSION, "history": records, "mutation_performed": False}

    @contextmanager
    def lock(self):
        self.write_guard()
        private(self.root, self.workspace).mkdir(parents=True, exist_ok=True)
        lock = safe(self.root / "intent.lock")
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise IntentError("Intent is locked; inspect an interrupted writer before explicit recovery") from error
        try:
            os.close(descriptor)
            yield
        finally:
            lock.unlink()

    def change(self, packet):
        if not isinstance(packet, dict) or packet.get("op") not in ("intent-revise", "intent-accept"):
            raise IntentError("Expected intent-revise or intent-accept")
        review = packet.get("operator_review")
        if not isinstance(review, str) or not review.strip() or len(review) > 12000:
            raise IntentError("Actual owner authorization must be referenced in operator_review")
        candidate = None
        if packet["op"] == "intent-revise":
            if not isinstance(packet.get("text"), str):
                raise IntentError("Revision requires reviewed text")
            candidate = packet["text"].encode("utf-8")
            validate(candidate)
        with self.lock():
            meta = self.metadata()
            self.checked_history(meta)
            old = self.raw()
            sha = digest(old) if old is not None else None
            if type(packet.get("revision")) is not int or packet["revision"] != meta["revision"]:
                raise IntentError("Stale revision")
            if "sha256" not in packet or packet["sha256"] != sha:
                raise IntentError("Intent digest mismatch")
            if packet["op"] == "intent-accept":
                if old is None or meta["pending"]:
                    raise IntentError("Missing or interrupted intent cannot be accepted")
                history = safe(self.root / "intent-history")
                history.mkdir(exist_ok=True)
                target = safe(history / (sha + ".md"))
                if target.exists() and target.read_bytes() != old:
                    raise IntentError("History collision or corruption")
                if not target.exists():
                    atomic(target, old)
                if not any(row["sha256"] == sha for row in meta["history"]):
                    meta["history"].append({"sha256": sha, "at": datetime.now(timezone.utc).isoformat()})
                meta.update(accepted_sha256=sha, acceptance={"sha256": sha, "review": review,
                            "at": datetime.now(timezone.utc).isoformat()})
            else:
                history = safe(self.root / "intent-history")
                history.mkdir(exist_ok=True)
                for raw in (old, candidate):
                    if raw is None:
                        continue
                    checksum = digest(raw)
                    target = safe(history / (checksum + ".md"))
                    if target.exists() and target.read_bytes() != raw:
                        raise IntentError("History collision or corruption")
                    if not target.exists():
                        atomic(target, raw)
                    if not any(r["sha256"] == checksum for r in meta["history"]):
                        meta["history"].append({"sha256": checksum,
                            "at": datetime.now(timezone.utc).isoformat()})
                # Invalidate acceptance durably BEFORE replacing the document.
                # An interrupted write remains unaccepted even if bytes happen to match.
                meta.update(accepted_sha256=None, pending=True, revision=meta["revision"] + 1)
                meta.pop("acceptance", None)
                meta["last_review"] = review
                atomic(self.meta, encoded(meta))
                atomic(self.document, candidate)
                meta["pending"] = False
            if packet["op"] == "intent-accept":
                meta["revision"] += 1
            atomic(self.meta, encoded(meta))
        return self.context()
