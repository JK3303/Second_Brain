"""Portable, explicit-only team contribution exchange. No retrieval or sending.

Audience review is an agent/human judgment bound to exact bytes, not a security
claim made by this compiler. Inputs are projections, never raw private memory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

SCHEMA = "team-contribution-v1"
AUDIENCE = "grace-gems-team"
KINDS = {"session", "repository", "email", "drive"}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 3000:
        raise ValueError(f"Missing or invalid {field}")
    if any(ord(c) < 32 for c in value):
        raise ValueError(f"Control character in {field}")
    return value


def keys(row, required, optional=()):
    if not isinstance(row, dict) or set(row) - set(required) - set(optional) or set(required) - set(row):
        raise ValueError("Unexpected or missing fields in reviewed projection")


def token(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", value):
        raise ValueError("Expected opaque identity, not a private path")
    return value


def sha(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("Expected SHA256")
    return value


def stamp(value):
    result = datetime.fromisoformat(text(value, "timestamp").replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timestamp requires timezone")
    return result


def url(value):
    parsed = urlsplit(text(value, "share URL"))
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Share URL must be HTTPS without credentials, query or fragment")


def review_digest(packet):
    return digest({k: v for k, v in packet.items() if k != "review"})


def verify_sources(packet, source_map):
    """Check local originals or exact provider-readback captures, never export paths."""
    if not isinstance(source_map, dict) or set(source_map) != {s["id"] for s in packet["sources"]}:
        raise ValueError("Source map must cover exactly the selected source identities")
    for source in packet["sources"]:
        path = Path(source_map[source["id"]])
        if not path.is_absolute() or not path.is_file():
            raise ValueError("Source map requires available absolute source paths")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Source bytes changed; reconcile and renew audience review")


def validate(packet, business_date, timezone, project):
    keys(packet, {"schema", "owner", "project", "date", "timezone", "audience", "basis", "coverage", "sources", "outcomes", "review"})
    day = date.fromisoformat(business_date)
    ZoneInfo(timezone)
    if packet["schema"] != SCHEMA or packet["date"] != day.isoformat() or packet["timezone"] != timezone or packet["project"] != project or packet["audience"] != AUDIENCE:
        raise ValueError("Incompatible contribution period, project or audience")
    token(packet["owner"]); token(project)
    keys(packet["basis"], {"id", "version", "sha256", "observed_at"})
    token(packet["basis"]["id"]); token(packet["basis"]["version"])
    sha(packet["basis"]["sha256"]); stamp(packet["basis"]["observed_at"])
    review = packet["review"]
    keys(review, {"reviewer", "sha256"})
    token(review["reviewer"])
    if review["sha256"] != review_digest(packet):
        raise ValueError("Audience review is stale; review the exact projection")
    coverage = packet["coverage"]
    if not isinstance(coverage, list) or len(coverage) != 4 or not all(isinstance(r, dict) for r in coverage) or {r.get("kind") for r in coverage} != KINDS:
        raise ValueError("Declare all four source coverage kinds exactly once")
    for row in coverage:
        keys(row, {"kind", "status", "en", "zh"})
        if row["status"] not in {"checked", "unavailable", "not_applicable"}:
            raise ValueError("Invalid coverage status")
        text(row["en"], "coverage"); text(row["zh"], "coverage")
    if not isinstance(packet["sources"], list) or not isinstance(packet["outcomes"], list):
        raise ValueError("Sources and outcomes must be lists")
    sources = {}
    for source in packet["sources"]:
        keys(source, {"id", "version", "sha256"})
        sid = token(source["id"])
        if sid in sources:
            raise ValueError("Duplicate source identity")
        token(source["version"]); sha(source["sha256"])
        sources[sid] = source
    seen = set()
    for row in packet["outcomes"]:
        keys(row, {"id", "outcome_id", "artifact_id", "revision", "event_date", "category", "evidence", "delivery", "source_ids", "en", "zh", "uncertainty", "supersedes"}, {"share_url", "carry_forward", "action"})
        if "action" in row:
            validate_action(row["action"])
        for field in ("id", "outcome_id", "artifact_id", "revision"):
            token(row[field])
        if row["id"] in seen:
            raise ValueError("Duplicate claim identity")
        seen.add(row["id"])
        if row["category"] not in {"progress", "working", "blocker", "decision", "next"} or row["evidence"] not in {"verified", "reported", "proposed"}:
            raise ValueError("Invalid category or evidence class")
        if row["category"] == "progress" and row["evidence"] == "proposed":
            raise ValueError("Proposal is not completed progress")
        event = date.fromisoformat(row["event_date"])
        if event > day or (event < day and not (row["category"] in {"blocker", "decision", "next"} and row.get("carry_forward") is True)):
            raise ValueError("Old progress or future event cannot be today's work")
        text(row["en"], "English wording"); text(row["zh"], "Chinese wording")
        text(row["uncertainty"], "uncertainty")
        if not isinstance(row["source_ids"], list) or not row["source_ids"] or any(s not in sources for s in row["source_ids"]):
            raise ValueError("Outcome needs versioned source references")
        delivery = row["delivery"]
        keys(delivery, {"state", "destination", "version", "evidence_id"})
        if delivery["state"] not in {"local", "draft", "attempted", "verified", "not_applicable"}:
            raise ValueError("Invalid delivery state")
        text(delivery["destination"], "delivery destination")
        text(delivery["version"], "delivery version")
        if delivery["state"] == "verified" and (delivery["evidence_id"] not in row["source_ids"] or delivery["version"] != row["revision"]):
            raise ValueError("Verified delivery needs readback for the current revision")
        if not isinstance(row["supersedes"], list):
            raise ValueError("Corrections require exact claim references")
        for ref in row["supersedes"]:
            keys(ref, {"owner", "id", "sha256"})
            token(ref["owner"]); token(ref["id"]); sha(ref["sha256"])
        if row.get("share_url"):
            url(row["share_url"])
    return deepcopy(packet)


def validate_action(action):
    keys(action, {"schema", "relevant_to", "request", "decision_maker", "commitment", "deadline", "state"})
    if action["schema"] != "team-action-v1":
        raise ValueError("Unsupported action context version")
    if not isinstance(action["relevant_to"], list) or len(set(action["relevant_to"])) != len(action["relevant_to"]):
        raise ValueError("Action participants must be unique")
    for person in action["relevant_to"]:
        if person not in {"mira", "hannah", "jon", "eric"}:
            raise ValueError("Unknown action participant")
    keys(action["request"], {"en", "zh"})
    text(action["request"]["en"], "action request"); text(action["request"]["zh"], "action request")
    if action["decision_maker"] not in {None, "mira", "hannah", "jon", "eric"}:
        raise ValueError("Unknown decision maker")
    if action["commitment"] not in {"proposed", "accepted", "unspecified"} or action["state"] not in {"open", "resolved", "superseded"}:
        raise ValueError("Invalid action state or commitment")
    if action["deadline"] is not None:
        date.fromisoformat(action["deadline"])


def compose(packets, *, business_date, timezone, project, expected_owners):
    """Reconcile declared identities; semantic interpretation remains upstream."""
    if not expected_owners or len(set(expected_owners)) != len(expected_owners):
        raise ValueError("Explicit unique expected owners required")
    for owner in expected_owners:
        token(owner)
    owners, claims, inputs = {}, {}, []
    for packet in packets:
        p = validate(packet, business_date, timezone, project)
        owner = p["owner"]
        if owner not in expected_owners or owner in owners:
            raise ValueError("Unexpected or duplicate owner contribution")
        owners[owner] = p
        inputs.append({"owner": owner, "sha256": digest(p), "basis": p["basis"]})
        for row in p["outcomes"]:
            claims[(owner, row["id"])] = row
    removed, edges = set(), {}
    for key, row in claims.items():
        edges[key] = []
        for ref in row["supersedes"]:
            old_key = (ref["owner"], ref["id"])
            old = claims.get(old_key)
            if old is None or digest(old) != ref["sha256"] or old_key == key:
                raise ValueError("Correction target absent, changed or self-referential")
            if (old["outcome_id"], old["artifact_id"]) != (row["outcome_id"], row["artifact_id"]) or old["event_date"] > row["event_date"]:
                raise ValueError("Correction changes outcome identity or reverses time")
            edges[key].append(old_key)
            removed.add(old_key)
    def visit(key, trail):
        if key in trail:
            raise ValueError("Cyclic corrections")
        for old in edges[key]:
            visit(old, trail | {key})
    for key in edges:
        visit(key, set())
    groups = {}
    for key, row in sorted(claims.items()):
        if key not in removed:
            groups.setdefault((row["outcome_id"], row["artifact_id"]), []).append((key, row))
    results = []
    for identity, group in sorted(groups.items()):
        variants = {}
        for (owner, cid), row in group:
            payload = {k: v for k, v in row.items() if k not in {"id", "source_ids", "supersedes"}}
            # Evidence IDs are owner-local; matching delivery is about destination,
            # version and state, while each readback remains attributed below.
            payload["delivery"] = {k: v for k, v in row["delivery"].items() if k != "evidence_id"}
            variant = variants.setdefault(digest(payload), {"outcome": payload, "provenance": []})
            variant["provenance"].append({"owner": owner, "id": cid, "sha256": digest(row), "delivery_evidence_id": row["delivery"]["evidence_id"], "sources": [next(s for s in owners[owner]["sources"] if s["id"] == sid) for sid in row["source_ids"]]})
        results.append({"outcome_id": identity[0], "artifact_id": identity[1], "status": "unresolved" if len(variants) > 1 else "reconciled", "variants": [variants[k] for k in sorted(variants)]})
    return {"schema": "team-draft-v1", "date": business_date, "timezone": timezone, "project": project,
            "audience": AUDIENCE, "delivery": "draft-not-sent", "inputs": sorted(inputs, key=lambda x: x["owner"]),
            "coverage": [{"owner": owner, "sources": owners[owner]["coverage"] if owner in owners else None} for owner in sorted(expected_owners)],
            "results": results, "corrections": [{"owner": key[0], "id": key[1], "sha256": digest(claims[key])} for key in sorted(removed)]}


def render(result):
    """Human-facing brief; full provenance stays in the evidence JSON."""
    lines = [f"Subject: Grace Gems daily update / 每日进展 — {result['date']}", "", "DRAFT — NOT SENT / 草稿 — 未发送", "", f"Business period / 业务日期: {result['date']} ({result['timezone']})"]
    headings = [("decision", "Decisions needed / 待决事项"), ("blocker", "Blocked work / 受阻工作"),
                ("progress", "Meaningful progress / 实质进展"), ("next", "Next actions / 下一步"),
                ("working", "Work in progress / 进行中的工作")]
    for category, heading in headings:
        entries = [(g, v) for g in result["results"] for v in g["variants"]
                   if v["outcome"]["category"] == category and not
                   (category in {"decision", "blocker", "next"} and
                    v["outcome"].get("action", {}).get("state") in {"resolved", "superseded"})]
        if not entries:
            continue
        lines += ["", heading]
        for group, variant in entries:
            row = variant["outcome"]
            lines += [f"- {row['en']}", f"  {row['zh']}"]
            if group["status"] == "unresolved":
                owners = ", ".join(p["owner"] for p in variant["provenance"])
                lines.append(f"  Disagreement unresolved / 分歧未解决 ({owners})")
            if row["evidence"] != "verified" and not (row["evidence"] == "proposed" and row.get("action", {}).get("commitment") == "proposed"):
                lines.append("  " + {"reported": "Reported / 据报告", "proposed": "Proposed / 提议"}[row["evidence"]])
            action = row.get("action")
            if action:
                maker = action["decision_maker"] or "Unspecified / 未指定"
                commitment = {"proposed": "Proposed / 提议", "accepted": "Accepted / 已接受", "unspecified": "Unspecified / 未明确"}[action["commitment"]]
                if action["request"] != {"en": row["en"], "zh": row["zh"]}:
                    lines.append(f"  Action / 行动: {action['request']['en']} / {action['request']['zh']}")
                relevant = ", ".join(action["relevant_to"]) or "Unspecified / 未指定"
                lines += [f"  For / 相关人员: {relevant}; {commitment}",
                          f"  Decision-maker / 决策人: {maker}"]
                if action["deadline"]:
                    lines.append(f"  Deadline / 截止日期: {action['deadline']}")
                if action["state"] != "open":
                    lines.append("  " + {"resolved": "Resolved / 已解决", "superseded": "Superseded / 已被替代"}[action["state"]])
            elif category in {"decision", "blocker", "next"}:
                lines.append("  Responsibility and commitment unspecified / 责任与承诺未明确")
            states = {"local": "Local only / 仅本地", "draft": "Draft / 草稿", "attempted": "Delivery unverified / 交付未核实", "verified": "Delivery verified / 交付已核实", "not_applicable": "Not applicable / 不适用"}
            if row["delivery"]["state"] != "not_applicable":
                lines.append("  " + states[row["delivery"]["state"]])
            lines.append(f"  Uncertainty / 不确定性: {row['uncertainty']}")
            if row.get("carry_forward"):
                lines.append(f"  Carried from / 延续自: {row['event_date']}")
            if row.get("share_url") and row["delivery"]["state"] == "verified":
                lines.append("  " + row["share_url"])
    if not result["results"]:
        lines += ["", "No team-ready outcomes established; this does not mean no work occurred. / 未确认可报告的结果，不表示没有工作。"]
    lines += ["", "Coverage / 来源范围"]
    for owner in result["coverage"]:
        if owner["sources"] is None:
            lines.append(f"- {owner['owner']}: contribution unavailable / 未收到贡献；不表示没有工作。")
        else:
            gaps = [s for s in owner["sources"] if s["status"] == "unavailable"]
            if gaps:
                lines.append(f"- {owner['owner']}: unavailable / 不可用: " + "; ".join(f"{s['en']} / {s['zh']}" for s in gaps))
    lines.append("Scoped reviewed evidence only / 仅限已审核的指定证据。")
    return "\n".join(lines) + "\n"


def shared_brief(result, through_cutoff=None):
    """Reviewed projection only: never copy source maps or private evidence."""
    if through_cutoff is not None:
        stamp(through_cutoff)
    return {"schema": "team-brief-v1", "project": result["project"], "date": result["date"],
            "timezone": result["timezone"], "through_cutoff": through_cutoff,
            "evidence_sha256": digest(result), "coverage": deepcopy(result["coverage"]),
            "items": [{"outcome_id": g["outcome_id"], "artifact_id": g["artifact_id"], "status": g["status"],
                       "variants": [deepcopy(v["outcome"]) for v in g["variants"]]} for g in result["results"]]}


def reentry(brief, receipt, current, owner, at):
    """Readback declarations are supplied by the agent, not authenticated here.

    A current owning-record review is digest-bound to each returned variant.
    Missing, stale or invalid evidence is a nonblocking coverage gap.
    """
    empty = {"items": [], "limitation": "Team evidence unavailable or stale; continue personal orientation."}
    try:
        if brief["schema"] != "team-brief-v1" or brief["project"] != "grace-gems" or brief["through_cutoff"] is None:
            return empty
        now = stamp(at)
        observed = stamp(receipt["observed_at"])
        checked = stamp(current["observed_at"])
        cutoff = stamp(brief["through_cutoff"])
        if not (cutoff <= observed <= now and cutoff <= checked <= now):
            return empty
        if (now-observed).total_seconds() > 86400 or (now-checked).total_seconds() > 86400:
            return empty
        if receipt["brief_sha256"] != digest(brief) or current["brief_sha256"] != digest(brief) or receipt["latest_verified"] is not True:
            return empty
        rows = []
        for item in brief["items"]:
            selected = []
            for row in item["variants"]:
                action = row.get("action")
                if not action:
                    continue
                validate_action(action)
                if owner not in action["relevant_to"] or action["state"] != "open" or row["category"] not in {"decision", "blocker", "next"}:
                    continue
                status = current["items"].get(digest(row))
                if status == "open":
                    selected.append(deepcopy(row))
            if selected:
                # Preserve all variants of a relevant disagreement, without assigning them to the reader.
                rows.append(deepcopy(item) if item["status"] == "unresolved" else {**deepcopy(item), "variants": selected})
        return {"items": rows, "limitation": "Only explicitly relevant, currently reviewed actions; unknown ownership is not assigned."}
    except (KeyError, TypeError, ValueError, AttributeError):
        return empty


def private_folder(output, repo_root):
    folder = Path(output).resolve()
    if not Path(output).is_absolute() or folder.is_relative_to(Path(repo_root).resolve()):
        raise ValueError("Output must be absolute and outside the repository")
    if any((p / ".git").exists() for p in [folder, *folder.parents]):
        raise ValueError("Private outputs must not be inside any Git checkout")
    return folder


def write_files(output, files, repo_root):
    folder = private_folder(output, repo_root)
    folder.mkdir(parents=True, exist_ok=True)
    staged, old = [], {}
    try:
        for name, data in files.items():
            path = folder / name
            if path.is_symlink():
                raise ValueError("Output symlink rejected")
            old[name] = path.read_bytes() if path.exists() else None
            if old[name] == data:
                continue
            if old[name] is not None:
                history = folder / ".history" / hashlib.sha256(old[name]).hexdigest()
                if (folder / ".history").is_symlink() or history.is_symlink():
                    raise ValueError("History symlink rejected")
                history.mkdir(parents=True, exist_ok=True)
                (history / name).write_bytes(old[name])
            with tempfile.NamedTemporaryFile(dir=folder, prefix=".candidate-", delete=False) as stream:
                stream.write(data)
                staged.append((Path(stream.name), path))
        for temporary, path in staged:
            temporary.replace(path)
        for name, data in files.items():
            if (folder / name).read_bytes() != data:
                raise OSError("Output readback mismatch")
    except Exception:
        for name, data in old.items():
            path = folder / name
            if not path.is_symlink():
                if data is None:
                    path.unlink(missing_ok=True)
                elif path.read_bytes() != data:
                    path.write_bytes(data)
        raise
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    return folder


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["export", "compose"])
    parser.add_argument("--input", action="append", type=Path, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--expected-owner", action="append", default=[])
    parser.add_argument("--source-map", type=Path)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--through-cutoff", help="Actual timezone-aware inspected-source cutoff; omit if unknown")
    args = parser.parse_args(argv)
    try:
        packets = [json.loads(p.read_text(encoding="utf-8")) for p in args.input]
        if args.mode == "export":
            if len(packets) != 1:
                raise ValueError("Export exactly one reviewed owner projection")
            packet = validate(packets[0], args.date, args.timezone, args.project)
            if args.source_map is None:
                raise ValueError("Export requires a private source map for current byte verification")
            verify_sources(packet, json.loads(args.source_map.read_text(encoding="utf-8")))
            files = {"current-contribution.json": encoded(packet)}
        else:
            result = compose(packets, business_date=args.date, timezone=args.timezone, project=args.project, expected_owners=args.expected_owner)
            files = {"current-team-email.md": render(result).encode("utf-8"), "current-evidence.json": encoded(result),
                     "current-team-brief.json": encoded(shared_brief(result, args.through_cutoff))}
        folder = write_files(args.output, files, args.repo_root)
        print(f"Verified local {args.mode}: {folder}; nothing sent.")
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"No completed output: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
