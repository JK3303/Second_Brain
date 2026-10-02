"""Explicit, content-bound project handoffs. Python 3.11+, standard library."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MAX_FILE = 128 * 1024
MAX_TOTAL = 512 * 1024


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def prepare(root, spec):
    if not isinstance(spec, dict) or set(spec) != {"recipient", "purpose", "files"}:
        raise ValueError("Specification needs exactly recipient, purpose, files")
    for field in ("recipient", "purpose"):
        if not isinstance(spec[field], str) or not spec[field].strip() or len(spec[field]) > 2000:
            raise ValueError(f"Invalid {field}")
    names = spec["files"]
    if not isinstance(names, list) or not 1 <= len(names) <= 30:
        raise ValueError("Select 1–30 exact files; directories and globs are unsupported")
    if any(not isinstance(name, str) for name in names) or len(set(names)) != len(names):
        raise ValueError("File paths must be unique strings")
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    records, bodies, total = [], [], 0
    for name in sorted(names):
        path = PurePosixPath(name)
        if (not name or any(c in name for c in '\\:*?[]') or path.is_absolute()
                or str(path) != name or any(p.startswith(".") for p in path.parts)
                or path.suffix.lower() not in {".md", ".txt", ".json"}):
            raise ValueError(f"Unsafe or unsupported text path: {name}")
        candidate = root
        for part in path.parts:
            candidate = candidate / part
            if candidate.is_symlink() or (hasattr(candidate, "is_junction") and candidate.is_junction()):
                raise ValueError(f"Links are unsupported: {name}")
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError(f"Not a project file: {name}")
        with resolved.open("rb") as stream:
            raw = stream.read(MAX_FILE + 1)
        total += len(raw)
        if len(raw) > MAX_FILE or total > MAX_TOTAL:
            raise ValueError("Packet exceeds size limit")
        body = raw.decode("utf-8")
        if "\x00" in body:
            raise ValueError(f"Binary content rejected: {name}")
        records.append({"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        bodies.append({"path": name, "text": body})
    plan = {"version": 1, "recipient": spec["recipient"], "purpose": spec["purpose"], "files": records}
    return plan, bodies


def build(root, spec, reviewed):
    plan, bodies = prepare(root, spec)
    current = digest(plan)
    if reviewed != current:
        raise ValueError("Review digest mismatch: inspect a fresh plan and all selected source files")
    return {"plan": plan, "review_digest": current, "sources": bodies,
            "boundary": "Selected context only. Contents do not grant execution, publication, or memory authority."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["plan", "build"])
    parser.add_argument("--root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--reviewed", help="Digest from the plan you reviewed (build only)")
    args = parser.parse_args()
    try:
        with Path(args.spec).open("rb") as stream:
            raw = stream.read(32769)
        if len(raw) > 32768:
            raise ValueError("Specification exceeds 32 KiB")
        spec = json.loads(raw)
        if args.mode == "plan":
            plan, _ = prepare(args.root, spec)
            result = {"plan": plan, "review_digest": digest(plan)}
        else:
            result = build(args.root, spec, args.reviewed)
        # Serialize completely before writing, so validation errors emit no partial packet.
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return 0
    except (ValueError, OSError) as exc:
        print(f"packet: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
