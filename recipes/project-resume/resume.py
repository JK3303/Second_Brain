"""Read-only, source-bound project resumption. Python 3.11+, standard library."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 512_000
SUPPORTING = (
    "decisions/holds-and-rejections.md",
    "memory/open-questions.md",
)


def read_source(root, relative):
    """Only read small UTF-8 files inside the explicitly selected project."""
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or ":" in relative:
        raise ValueError(f"Unsafe project-relative path: {relative}")
    path = (root / candidate).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path leaves project: {relative}")
    if not path.is_file():
        return {"path": relative, "status": "missing"}
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"Source exceeds {MAX_BYTES} bytes: {relative}")
    content = raw.decode("utf-8-sig")
    return {"path": relative, "status": "read", "sha256": hashlib.sha256(raw).hexdigest(),
            "lines": content.splitlines()}


def fields(source):
    """Read the existing manifest's key/value block without inventing defaults."""
    found = {}
    for number, line in enumerate(source.get("lines", []), 1):
        match = re.fullmatch(r"([A-Za-z][A-Za-z -]+):\s*(.*)", line)
        if match:
            key, value = match.groups()
            if key in found:
                raise ValueError(f"Duplicate manifest field: {key}")
            found[key] = {"value": value.strip(), "source": source["path"], "line": number}
    return found


def sections(source):
    result = []
    current = None
    for number, line in enumerate(source.get("lines", []), 1):
        if line.startswith("## "):
            current = {"heading": line[3:].strip(), "source": source["path"],
                       "line": number, "text": []}
            result.append(current)
        elif current is not None:
            current["text"].append(line)
    for section in result:
        section["text"] = "\n".join(section["text"]).strip()
    return result


def fingerprint(sources):
    # File order and timestamps do not affect content equivalence.
    values = sorted((s["path"], s["status"], s.get("sha256")) for s in sources)
    return hashlib.sha256(json.dumps(values, ensure_ascii=True).encode()).hexdigest()


def build_packet(project_root, previous=None):
    root = Path(project_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    manifest = read_source(root, "manifest.md")
    if manifest["status"] != "read":
        raise ValueError("Project needs manifest.md; use projects/_template/manifest.md")
    manifest_fields = fields(manifest)
    entry = manifest_fields.get("Current entry point", {}).get("value")
    if not entry:
        raise ValueError("Manifest needs a Current entry point")
    # Accept the template's plain path or a single code-formatted path.
    entry = entry.strip("`")
    sources = [manifest]
    for relative in dict.fromkeys(["README.md", entry, *SUPPORTING]):
        if relative != "manifest.md":
            sources.append(read_source(root, relative))
    current = next(s for s in sources if s["path"] == entry)
    source_index = [{k: v for k, v in s.items() if k != "lines"} for s in sources]
    report = {
        "schema_version": 1,
        "project": manifest_fields.get("Project", {}).get("value", root.name),
        "authority_effect": "none",
        "interpretation": "Source claims are shown together; no approval or current truth is inferred.",
        "manifest_fields": manifest_fields,
        "entry_point": entry,
        "entry_sections": sections(current),
        "supporting_sources": [{"path": s["path"], "text": "\n".join(s.get("lines", []))}
                               for s in sources if s["path"] in SUPPORTING and s["status"] == "read"],
        "sources": source_index,
        "fingerprint": fingerprint(source_index),
        "attention": [],
        "comparison": {"status": "not-requested"},
    }
    for source in sources:
        if source["status"] == "missing":
            report["attention"].append(f"Missing source: {source['path']}")
    if not report["entry_sections"]:
        report["attention"].append("Entry point has no level-two sections; read it directly before acting.")
    report["attention"].append("Reconcile manifest State / External-action rule / Next review with entry-point claims before acting.")
    if previous is not None:
        if not isinstance(previous, dict) or previous.get("schema_version") != 1:
            raise ValueError("Previous packet must use schema_version 1")
        old = previous.get("sources")
        if not isinstance(old, list) or not all(isinstance(s, dict) and isinstance(s.get("path"), str)
                                              and s.get("status") in ("read", "missing") for s in old):
            raise ValueError("Previous packet has invalid sources")
        for source in old:
            if source["status"] == "read" and (not isinstance(source.get("sha256"), str)
                                               or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])):
                raise ValueError("Previous packet has an invalid source fingerprint")
        if len({s['path'] for s in old}) != len(old):
            raise ValueError("Previous packet has duplicate sources")
        if previous.get("project") != report["project"] or previous.get("entry_point") != entry:
            raise ValueError("Previous packet belongs to a different project or entry point")
        if previous.get("fingerprint") != fingerprint(old):
            raise ValueError("Previous packet fingerprint does not match its source index")
        before = {s["path"]: (s["status"], s.get("sha256")) for s in old}
        after = {s["path"]: (s["status"], s.get("sha256")) for s in source_index}
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        report["comparison"] = {"status": "changed" if changed else "unchanged", "changed_paths": changed,
                                "scope": "selected source bytes only; not the whole project or external state"}
    return report


def markdown(report):
    lines = [f"# Resume: {report['project']}", "", report["interpretation"], "",
             "## Manifest controls", ""]
    for key, field in report["manifest_fields"].items():
        lines.append(f"- {key}: {field['value']} ({field['source']}:{field['line']})")
    lines.extend(["", "## Entry-point claims", ""])
    for section in report["entry_sections"]:
        lines.extend([f"### {section['heading']}", "", f"Source: {section['source']}:{section['line']}",
                      "", section["text"], ""])
    lines.extend(["## Questions and holds", ""])
    for source in report["supporting_sources"]:
        # Quote source headings so they do not become report navigation.
        lines.extend([f"Source: {source['path']}", "", *["> " + s for s in source["text"].splitlines()], ""])
    lines.extend(["## Attention", "", *[f"- {item}" for item in report["attention"]], "",
                  "## Freshness", "", f"Comparison: {report['comparison']['status']}",
                  f"Fingerprint: `{report['fingerprint']}`", ""])
    for path in report["comparison"].get("changed_paths", []):
        lines.append(f"- Changed: {path}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--previous", type=Path, help="Prior JSON packet to compare selected source bytes")
    args = parser.parse_args()
    try:
        previous = None
        if args.previous:
            with args.previous.open("rb") as handle:
                raw = handle.read(4 * MAX_BYTES + 1)
            if len(raw) > 4 * MAX_BYTES:
                raise ValueError("Previous packet is too large")
            previous = json.loads(raw.decode("utf-8-sig"))
        report = build_packet(args.project_root, previous)
        print(json.dumps(report, ensure_ascii=True, indent=2) if args.format == "json" else markdown(report), end="\n")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot resume: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
