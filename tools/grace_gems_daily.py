"""Validate agent-collected evidence and build a local bilingual draft. No send API."""
import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 3000:
        raise ValueError(f"Invalid {field}")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError(f"Control character in {field}")
    return value.strip()


def https(value):
    value = text(value, "URL")
    u = urlsplit(value)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError("Expected HTTPS URL without credentials")
    # Do not embed signed download references or tokens in retained drafts.
    if any(k in u.query.lower() for k in ("token=", "signature=", "x-goog-", "x-amz-")):
        raise ValueError("Credential-bearing URL is not an evidence link")
    return value


def validate(packet, business_date, timezone, repo_root):
    day = date.fromisoformat(business_date)
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Unknown IANA timezone; install timezone data if needed") from exc
    if not isinstance(packet, dict) or packet.get("version") != 1:
        raise ValueError("Unsupported packet version")
    if packet.get("date") != day.isoformat() or packet.get("timezone") != timezone:
        raise ValueError("Packet date/timezone differs from requested business period")
    coverage = packet.get("coverage")
    if not isinstance(coverage, list) or len(coverage) != 4:
        raise ValueError("Declare session, repository, email and drive coverage")
    seen = set()
    for row in coverage:
        kind = row.get("kind")
        if kind not in {"session", "repository", "email", "drive"} or kind in seen:
            raise ValueError("Invalid/duplicate coverage kind")
        seen.add(kind)
        if row.get("status") not in {"checked", "unavailable", "not_applicable"}:
            raise ValueError("Invalid coverage status")
        for lang in ("en", "zh"):
            text(row.get(lang), "coverage explanation")
    sources = packet.get("sources")
    facts = packet.get("facts")
    if not isinstance(sources, list) or not isinstance(facts, list):
        raise ValueError("Sources and facts must be lists")
    source_ids = set()
    root = Path(repo_root).resolve(strict=True)
    for source in sources:
        sid = text(source.get("id"), "source ID")
        if sid in source_ids:
            raise ValueError("Duplicate source ID")
        source_ids.add(sid)
        stamp = datetime.fromisoformat(text(source.get("retrieved_at"), "retrieval time").replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Retrieval time must include timezone")
        if stamp.astimezone(zone).date() < day:
            raise ValueError("Source was not retrieved for this reporting day or later")
        ref = text(source.get("ref"), "source reference")
        if source.get("kind") == "repo_file":
            rel = Path(ref)
            if rel.is_absolute() or ".." in rel.parts or "\\" in ref or ":" in ref:
                raise ValueError("Source must be a repository-relative path")
            path = (root / rel).resolve(strict=True)
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError("Source escapes repository or is not a file")
            if source.get("sha256") != digest(path.read_bytes()):
                raise ValueError("Source hash changed; collect fresh evidence")
        elif source.get("kind") == "external":
            https(ref)
        else:
            raise ValueError("Unknown source kind")
    fact_ids, unique, dedup = set(), [], set()
    for fact in facts:
        fid = text(fact.get("id"), "fact ID")
        if fid in fact_ids:
            raise ValueError("Duplicate fact ID")
        fact_ids.add(fid)
        category = fact.get("category")
        if category not in {"progress", "working", "blocker", "decision", "next"}:
            raise ValueError("Unknown fact category")
        level = fact.get("evidence")
        if level not in {"verified", "reported", "proposed"}:
            raise ValueError("Unknown evidence level")
        if category == "progress" and level == "proposed":
            raise ValueError("Proposed work cannot be reported as progress")
        if fact.get("audience") != "grace-gems-team":
            raise ValueError("Fact has not been reviewed for the team audience")
        event_day = date.fromisoformat(text(fact.get("event_date"), "event date"))
        if event_day > day:
            raise ValueError("Future event cannot be daily evidence")
        if event_day < day and not (category in {"blocker", "decision", "next"} and fact.get("carry_forward") is True):
            raise ValueError("Old progress cannot be relabeled as today's work")
        refs = fact.get("source_ids")
        if not isinstance(refs, list) or not refs or any(s not in source_ids for s in refs):
            raise ValueError("Fact needs valid evidence references")
        en, zh = text(fact.get("en"), "English wording"), text(fact.get("zh"), "Chinese wording")
        if fact.get("share_url"):
            https(fact["share_url"])
        key = (category, level, event_day, en, zh, fact.get("share_url"))
        if key not in dedup:
            dedup.add(key)
            unique.append(fact)
    return {**packet, "facts": unique}


def render(packet):
    lines = [f"Subject: Grace Gems daily update / 每日进展 — {packet['date']}",
             "", "DRAFT — NOT SENT / 草稿 — 未发送",
             "To: confirmed team recipients required / 收件人：须使用已确认的团队名单", "",
             f"Business date / 业务日期: {packet['date']} ({packet['timezone']})", "",
             "Coverage covers declared inputs only; it is not a claim of all work.",
             "范围仅限以下已声明来源，不代表已掌握全部工作。"]
    for row in packet["coverage"]:
        lines.append(f"- {row['kind']} [{row['status']}]: {row['en'].strip()} / {row['zh'].strip()}")
    labels = {"verified": "verified / 已核实", "reported": "reported / 据报",
              "proposed": "proposed / 建议"}
    for category, title in [("progress", "Progress / 进展"), ("working", "In progress / 进行中"),
                            ("blocker", "Blockers / 阻碍"), ("decision", "Decisions needed / 待决定"),
                            ("next", "Next established move / 下一步")]:
        rows = [f for f in packet["facts"] if f["category"] == category]
        if not rows:
            continue
        lines.extend(["", title])
        for fact in rows:
            carried = f"; carried from {fact['event_date']} / 延续事项" if fact["event_date"] != packet["date"] else ""
            lines.extend([f"- [{labels[fact['evidence']]}{carried}] {fact['en'].strip()}",
                          f"  {fact['zh'].strip()}"])
            if fact.get("share_url"):
                lines.append(f"  {fact['share_url']}")
    if not packet["facts"]:
        lines.extend(["", "No team-ready changes were established from the available evidence; this does not mean no work occurred.",
                      "现有依据未能确认可向团队报告的变化；不表示没有工作发生。"])
    lines.extend(["", "Prepared for Jon's review; no business release or sending is implied.",
                  "供 Jon 审阅；不代表业务放行或已发送。", ""])
    return "\n".join(lines)


def write_outputs(packet, output):
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=True)
    files = {"current-team-email.md": render(packet).encode("utf-8"),
             "current-evidence.json": (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}
    # Stage all content before replacing either current file. Keep old bytes recoverable.
    staged = []
    try:
        for name, data in files.items():
            path = folder / name
            if path.exists() and path.read_bytes() == data:
                continue
            if path.exists():
                old = path.read_bytes()
                history = folder / ".history" / digest(old)
                history.mkdir(parents=True, exist_ok=True)
                (history / name).write_bytes(old)
            with tempfile.NamedTemporaryFile(dir=folder, prefix=".draft-", delete=False) as stream:
                stream.write(data)
                staged.append((Path(stream.name), path))
        for temporary, path in staged:
            temporary.replace(path)
        for name, data in files.items():
            if (folder / name).read_bytes() != data:
                raise OSError(f"Readback mismatch: {name}")
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return folder / "current-team-email.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True, help="Designated private output outside this public checkout")
    args = parser.parse_args()
    try:
        packet = validate(json.loads(args.evidence.read_text(encoding="utf-8")), args.date, args.timezone, args.repo_root)
        if args.output.resolve().is_relative_to(args.repo_root.resolve()):
            raise ValueError("Private evidence and drafts must remain outside this public repository")
        path = write_outputs(packet, args.output)
    except (ValueError, OSError, TypeError, AttributeError, KeyError) as exc:
        parser.exit(2, f"Draft not completed: {exc}\n")
    print(f"Local draft verified: {path}; email not sent.")


if __name__ == "__main__":
    main()
