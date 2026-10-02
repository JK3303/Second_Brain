"""Check asset records and file identity, never decide legal permission."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

FIELDS = {"id", "path", "sha256", "status", "uses", "reviewer", "evidence", "credit", "expires"}


def check(root, records, usage, as_of):
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or not isinstance(usage, str) or not usage.strip():
        raise ValueError("A directory and a nonempty usage are required")
    day = date.fromisoformat(as_of)
    if not isinstance(records, list) or not 1 <= len(records) <= 500:
        raise ValueError("Provide 1–500 asset records")
    ids, paths, results = set(), set(), []
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError("Asset fields must match the example record exactly")
        for key in FIELDS - {"uses"}:
            if not isinstance(record[key], str) or len(record[key]) > 4000:
                raise ValueError(f"Invalid field: {key}")
        if not record["id"].strip() or record["id"] in ids or record["path"].casefold() in paths:
            raise ValueError("IDs and paths must be nonempty and unique")
        ids.add(record["id"])
        paths.add(record["path"].casefold())
        if record["status"] not in {"documented", "unknown", "restricted"}:
            raise ValueError("Status must be documented, unknown, or restricted")
        uses = record["uses"]
        if not isinstance(uses, list) or any(not isinstance(x, str) or not x.strip() for x in uses):
            raise ValueError("Uses must be a list of nonempty strings")
        name = record["path"]
        rel = PurePosixPath(name)
        if (not name or str(rel) != name or rel.is_absolute() or any(c in name for c in '\\:*?[]')
                or any(p.startswith(".") for p in rel.parts)):
            raise ValueError("Asset paths must be exact, visible, project-relative paths")
        findings = []
        if record["status"] != "documented":
            findings.append("usage-record-unresolved")
        if usage not in uses:
            findings.append("requested-use-not-recorded")
        for field in ("reviewer", "evidence", "credit"):
            if not record[field].strip():
                findings.append(f"missing-{field}")
        if record["expires"] == "none":
            pass
        elif record["expires"]:
            if day > date.fromisoformat(record["expires"]):
                findings.append("record-expired")
        else:
            findings.append("missing-expiry-or-none")
        expected = record["sha256"]
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            findings.append("missing-or-invalid-sha256")
        path = root
        for part in rel.parts:
            path = path / part
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError("Asset links are unsupported")
        actual = None
        if not path.is_file():
            findings.append("missing-file")
        elif not path.resolve().is_relative_to(root):
            raise ValueError("Asset escapes root")
        elif path.stat().st_size > 100 * 1024 * 1024:
            findings.append("file-exceeds-100MiB-limit")
        else:
            sha = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    sha.update(chunk)
            actual = sha.hexdigest()
            if re.fullmatch(r"[a-f0-9]{64}", expected) and actual != expected:
                findings.append("asset-changed-since-record")
        results.append({"id": record["id"], "path": name, "actual_sha256": actual,
                        "findings": findings, "credit": record["credit"], "evidence": record["evidence"]})
    return {"usage": usage, "as_of": day.isoformat(), "assets": results,
            "record_gaps": sum(bool(row["findings"]) for row in results),
            "notice": "Record completeness and byte identity only. Not legal clearance or publication approval."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--usage", required=True)
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD (explicit for reproducible checks)")
    args = parser.parse_args()
    try:
        with Path(args.records).open("rb") as stream:
            raw = stream.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("Records exceed 2 MiB")
        result = check(args.root, json.loads(raw), args.usage, args.as_of)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["record_gaps"] else 0
    except (OSError, ValueError) as exc:
        print(f"preflight: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
