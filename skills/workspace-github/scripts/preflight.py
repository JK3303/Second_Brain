"""Read-only, stdlib-only Git candidate inspection. No authentication or mutation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Git inspection failed; diagnose ownership/access without exposing raw errors")
    return result.stdout


def relative_file(root, value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("Selected paths must be repository-relative files")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("Selected file is missing or escapes the repository")
    return path.as_posix()


def changed_paths(root):
    fields = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").decode("utf-8", "surrogateescape").split("\0")
    changed = set()
    index = 0
    while index < len(fields) and fields[index]:
        entry = fields[index]
        changed.add(entry[3:])
        if "R" in entry[:2] or "C" in entry[:2]:
            index += 1
            if index < len(fields) and fields[index]:
                changed.add(fields[index])
        index += 1
    return changed


def inspect(repo, candidates=(), inputs=()):
    root = Path(repo).resolve()
    actual = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if root != actual:
        raise ValueError("--repo must be the exact Git repository root")
    candidate = {relative_file(root, p) for p in candidates}
    selected = candidate | {relative_file(root, p) for p in inputs}
    changed = changed_paths(root)
    blocked = sorted((changed & selected) - candidate)
    hashes = {p: git(root, "hash-object", "--", p).decode().strip() for p in sorted(selected)}
    groups = {}
    for p in changed:
        top = p.split("/", 1)[0] if "/" in p else "[root files]"
        groups[top] = groups.get(top, 0) + 1
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return {"root": str(root), "head": git(root, "rev-parse", "HEAD").decode().strip(),
            "changed_count": len(changed), "groups": dict(sorted(groups.items())[:20]),
            "candidate": sorted(candidate), "input_hashes": hashes,
            "fingerprint": fingerprint, "blocked_inputs": blocked,
            "status": "blocked" if blocked else "eligible", "validation_passed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--input", action="append", default=[])
    args = parser.parse_args()
    try:
        report = inspect(args.repo, args.candidate, args.input)
    except (ValueError, OSError):
        print(json.dumps({"status": "blocked", "error": "Root/path/Git inspection failed; verify exact repository and selected files"}))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if report["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
