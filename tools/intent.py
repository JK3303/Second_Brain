"""Explicit, versioned enduring-intent operations; reads never initialize state."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

from intent_lifecycle import IntentError, LIMIT, Store, VERSION, read_json, validate


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoreAdapter:
    def __init__(self, repo, root=None):
        sys.path.insert(0, str(repo / "scripts"))
        module = load(repo / "scripts/mira_attention.py", "intent_core_attention")
        self.store = module.Store(root=root, repo=repo)

    def context(self):
        return self.store.intent_context()

    def change(self, packet):
        if packet.get("op") not in ("intent-revise", "intent-accept"):
            raise IntentError("Only intent lifecycle mutations are supported")
        self.store.change(packet)
        return self.context()

    def history(self):
        return self.store.intent_history()

    def validate(self, raw):
        return self.store.intent_validate(raw)


def configured(repo, state_root=None):
    repo = Path(repo).resolve()
    manifest = read_json(repo / "intent-capability.json")
    if manifest.get("capability_version") != VERSION:
        raise IntentError("Unsupported intent capability version")
    adapter = manifest["adapter"]
    if adapter == "core-attention":
        return CoreAdapter(repo, state_root)
    guard = None
    if adapter == "approved-instance":
        # Read-only verification of existing setup, never activation or capture.
        history = load(repo / "tools/history.py", "intent_instance_history")
        _, approved_root, _ = history.approved(repo)
        expected = approved_root / "intent"
        if state_root is not None and Path(state_root).resolve() != expected.resolve():
            raise IntentError("Intent state must remain in the approved instance")
        root = expected
        guard = lambda: history.approved(repo)
    elif adapter in ("repository-document", "private-document"):
        token = hashlib.sha256(str(repo).encode()).hexdigest()
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share"))
        root = Path(state_root) if state_root else base / "IntentCapability" / token
    else:
        raise IntentError("Unknown intent adapter")
    document = repo / "INTENT.md" if adapter == "repository-document" else None
    return Store(repo, root, document, manifest.get("source", {}), guard)


def context(repo, state_root=None):
    try:
        return configured(repo, state_root).context()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return {"capability_version": VERSION, "availability": "unavailable", "intent": None,
                "revision": None, "mutation_performed": False,
                "reason": "Intent configuration or approved setup unavailable; no initialization performed"}
    except Exception as error:
        # Instance setup has its own exception class. Preserve fail-closed preview.
        if type(error).__name__ != "HistoryError":
            raise
        return {"capability_version": VERSION, "availability": "unavailable", "intent": None,
                "revision": None, "mutation_performed": False,
                "reason": "Approved instance setup unavailable; preview remains inactive"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("context", "validate", "revise", "accept", "history"))
    parser.add_argument("--state-root", type=Path, help="Explicit private state root; never inside Git")
    parser.add_argument("--input", type=Path, help="UTF-8 Markdown for validate; JSON review packet for writes")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    try:
        if args.command == "context":
            result = context(repo, args.state_root)
        elif args.command == "validate":
            if args.input is None:
                raise IntentError("--input is required")
            raw = args.input.read_bytes()
            result = validate(raw)
            if read_json(repo / "intent-capability.json")["adapter"] == "core-attention":
                result = configured(repo, args.state_root).validate(raw)
        else:
            store = configured(repo, args.state_root)
            if args.command == "history":
                result = store.history()
            else:
                if args.input is None or args.input.stat().st_size > LIMIT:
                    raise IntentError("A bounded --input JSON packet is required")
                packet = read_json(args.input)
                if packet.get("op") != "intent-" + args.command:
                    raise IntentError("Command and packet operation differ")
                result = store.change(packet)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"ok": False, "error_type": type(error).__name__,
                          "reason": "Intent operation refused; inspect input, current state, and owner authorization"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
