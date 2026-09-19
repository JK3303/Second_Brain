"""Retrieve review candidates from one project's existing Markdown memory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

FILES = {"accepted": "accepted-lessons.md", "rejected": "rejected-lessons.md", "unresolved": "open-questions.md"}
STOP = set("a an and are as at be by for from i in is it of on or that the this to with".split())


def tokens(text):
    return set(re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)) - STOP


def sections(text):
    """Keep entire level-two sections. Never truncate qualifiers inside a lesson."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    if not starts:
        return [{"title": "Document", "start_line": 1, "end_line": len(lines), "text": text}] if text.strip() else []
    result = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lines)
        result.append({"title": lines[start][3:].strip(), "start_line": start + 1,
                       "end_line": end, "text": "\n".join(lines[start:end])})
    return result


def retrieve(project, brief, limit=3):
    if not isinstance(brief, str) or not brief.strip() or len(brief) > 12000:
        raise ValueError("Brief must contain 1–12000 characters")
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError("Limit must be 1–10 per lesson category")
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project must be a directory")
    query = tokens(brief)
    result = {"query_terms": sorted(query), "sources": [], "accepted": [], "rejected": [],
              "unresolved": [], "notice": "Lexical review candidates, not applicability judgments or memory promotion."}
    for category, filename in FILES.items():
        path = root / "memory" / filename
        for part in [root / "memory", path]:
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError("Memory links are unsupported")
        source = {"path": f"memory/{filename}", "state": "missing"}
        result["sources"].append(source)
        if not path.exists():
            continue
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError("Memory path must be a project-local file")
        with path.open("rb") as stream:
            raw = stream.read(131073)
        if len(raw) > 131072:
            raise ValueError("Memory source exceeds 128 KiB")
        text = raw.decode("utf-8")
        if "\x00" in text:
            raise ValueError("Binary memory source")
        source.update(state="present", sha256=hashlib.sha256(raw).hexdigest())
        candidates = []
        for item in sections(text):
            matched = sorted(query & tokens(item["text"]))
            if category == "unresolved" or matched:
                candidates.append(dict(item, source=source["path"], matched_terms=matched))
        if category != "unresolved":
            candidates.sort(key=lambda row: (-len(row["matched_terms"]), row["start_line"]))
            result[category] = candidates[:limit]
            source["matching_sections"] = len(candidates)
            source["omitted_matches"] = max(0, len(candidates) - limit)
        else:
            # Questions are cautionary context, even when their vocabulary differs.
            result[category] = candidates
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    try:
        print(json.dumps(retrieve(args.project, args.brief, args.limit), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"context: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
