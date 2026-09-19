"""Validate decision receipt completeness, not the truth or authority of its claims."""

import argparse
import json
from pathlib import Path
import re
import sys

STATES = set("idea explore shortlist brief draft review-ready approved executing delivered published complete held rejected superseded".split())
REQUIRED = ("Decision ID", "Project", "Status", "Source", "Decision owner", "Evidence",
            "Alternatives considered", "Uncertainty", "Authority or approval", "Reversible", "Next action")
OPTIONAL = ("Missing item", "Why it matters", "Needed from", "Reconsider when", "Superseded by")
PLACEHOLDERS = {"", "tbd", "todo", "...", "?", "fill in", "yes / no", "<fill in>"}
MAX_BYTES = 256_000


def parse_receipt(text):
    """One receipt per file; prefer the unique code fence containing Decision ID."""
    lines = text.splitlines()
    blocks = []
    active = None
    fence = None
    for index, line in enumerate(lines, 1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if active is None:
                active, fence = [], marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                blocks.append(active)
                active, fence = None, None
            else:
                active.append((index, line))
        elif active is not None:
            active.append((index, line))
    if active is not None:
        raise ValueError("Unclosed code fence")
    candidates = [b for b in blocks if any(re.match(r"^Decision ID:", line) for _, line in b)]
    if len(candidates) > 1:
        raise ValueError("Multiple receipts in one file; use one file per decision")
    selected = candidates[0] if candidates else list(enumerate(lines, 1))
    result, current = {}, None
    known = set(REQUIRED + OPTIONAL)
    for number, line in selected:
        match = re.match(r"^([A-Za-z][A-Za-z -]+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            current = None
            if key not in known:
                raise ValueError(f"Unknown field on line {number}: {key}")
            if key in result:
                raise ValueError(f"Duplicate field on line {number}: {key}")
            result[key] = {"value": value.strip(), "line": number}
            current = key
        elif line.startswith((" ", "\t")) and current:
            result[current]["value"] += "\n" + line.strip()
        elif line.strip():
            current = None
    return result


def audit(files):
    if not files:
        raise ValueError("At least one receipt is required")
    reports = []
    seen_paths = set()
    for file in files:
        path = Path(file).resolve(strict=True)
        if path in seen_paths:
            raise ValueError(f"Same input supplied twice: {file}")
        seen_paths.add(path)
        with path.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError(f"Receipt exceeds {MAX_BYTES} bytes: {file}")
        text = raw.decode("utf-8-sig")
        try:
            fields = parse_receipt(text)
            errors = []
        except ValueError as exc:
            fields, errors = {}, [str(exc)]
        report = {"path": str(file), "fields": fields, "errors": errors}
        reports.append(report)
        if errors:
            continue

        def value(key):
            return fields.get(key, {}).get("value", "")

        def require(key):
            if value(key).strip().casefold() in PLACEHOLDERS:
                errors.append(f"Missing or placeholder field: {key}")

        for key in REQUIRED:
            require(key)
        state = value("Status")
        if state not in STATES:
            errors.append(f"Unknown status: {state!r}")
        if value("Reversible").casefold() not in {"yes", "no"}:
            errors.append("Reversible must be yes or no")
        if state == "held":
            for key in ("Missing item", "Why it matters", "Needed from"):
                require(key)
        if state in {"rejected", "superseded"}:
            require("Reconsider when")
        if state == "superseded":
            require("Superseded by")
        if state in {"approved", "executing", "delivered", "published", "complete"}:
            authority = value("Authority or approval").strip().casefold()
            if authority in {"none", "n/a", "unknown"} or re.match(r"^(no\b|not\b|pending\b|awaiting\b|unapproved\b)", authority):
                errors.append("Advanced state has missing, pending, or negative authority claim")

    by_id = {}
    for report in reports:
        fields = report["fields"]
        decision_id = fields.get("Decision ID", {}).get("value", "")
        if decision_id:
            by_id.setdefault(decision_id, []).append(report)
    for decision_id, matches in by_id.items():
        if len(matches) > 1:
            for report in matches:
                report["errors"].append(f"Duplicate Decision ID: {decision_id}")

    edges = {}
    for report in reports:
        fields = report["fields"]
        decision_id = fields.get("Decision ID", {}).get("value", "")
        target = fields.get("Superseded by", {}).get("value", "")
        if fields.get("Status", {}).get("value") != "superseded" or not target:
            continue
        targets = by_id.get(target, [])
        if len(targets) != 1:
            report["errors"].append(f"Superseded by must identify one receipt in this input set: {target}")
        elif targets[0]["fields"].get("Project", {}).get("value") != fields.get("Project", {}).get("value"):
            report["errors"].append("Replacement belongs to a different project")
        elif decision_id:
            edges[decision_id] = target
    # Every starting node that reaches a cycle is invalid, including chains into it.
    for start in edges:
        visited, node = set(), start
        while node in edges and node not in visited:
            visited.add(node)
            node = edges[node]
        if node in visited:
            for report in by_id[start]:
                report["errors"].append("Supersession chain contains a cycle")

    return {"schema_version": 1, "valid": all(not r["errors"] for r in reports),
            "authority_effect": "none", "scope": "receipt completeness and supplied-set consistency only",
            "receipts": reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipts", type=Path, nargs="+")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        result = audit(args.receipts)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=True))
        else:
            print("Receipt validation: " + ("PASS" if result["valid"] else "NEEDS REVIEW"))
            print(result["scope"] + "; no authority granted")
            for receipt in result["receipts"]:
                print(f"{receipt['path']}: " + ("complete" if not receipt["errors"] else "incomplete"))
                for error in receipt["errors"]:
                    print("  - " + error)
        return 0 if result["valid"] else 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot validate receipts: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
