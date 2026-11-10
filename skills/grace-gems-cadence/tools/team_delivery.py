"""Portable, agent-run participant delivery. No network, credential store or scheduler.

Completion and provider captures are agent declarations, not machine attestation.
Only a matching fresh provider readback can advance the verified baseline.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import team_contributions as team

ZONE = "America/Denver"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def business_date(at):
    local = at.astimezone(ZoneInfo(ZONE))
    return (local - timedelta(days=1) if local.hour < 6 else local).date().isoformat()


def root_for(config):
    return team.private_folder(config["private_root"], Path(__file__).resolve().parent)


def state(root):
    return read(root / "delivery-state.json") if (root / "delivery-state.json").exists() else {"baseline": None, "pending": None}


def save(root, name, value):
    team.write_files(root, {name: team.encoded(value)}, Path(__file__).resolve().parent)


def activation(config, host, at):
    root_for(config)
    if config.get("owner") not in {"hannah", "jon"} or config.get("project") != "grace-gems":
        raise ValueError("Participant/project binding required")
    if not host or host != config.get("host"):
        raise ValueError("Actual host differs from adopted host")
    if config.get("adopted") is not True or team.stamp(config["adopted_at"]) > at:
        raise ValueError("Recorded adoption required")
    evidence_file(config["adoption_evidence"])
    access = config["drive_access"]
    if (access.get("verified") is not True or access.get("account") != config["account"]
            or access.get("folder_id") != config["folder_id"] or access.get("drive_id") != config["drive_id"]):
        raise ValueError("Verified Drive access to the adopted destination required")
    fresh(access["observed_at"], at)
    if not isinstance(config.get("allowed_sources"), dict) or not config["allowed_sources"]:
        raise ValueError("Allowed source identities required")


def fresh(value, at):
    elapsed = at - team.stamp(value)
    if elapsed < timedelta(0) or elapsed > timedelta(minutes=5):
        raise ValueError("Fresh provider evidence required")


def evidence_file(ref):
    path = Path(ref["path"])
    if not path.is_absolute() or not path.is_file() or sha(path.read_bytes()) != team.sha(ref["sha256"]):
        raise ValueError("Completion/adoption evidence missing or changed")


def status(config, host, at):
    try:
        activation(config, host, at)
        return {"status": "ready", "state": state(root_for(config)), "completion_kind": "agent-declaration"}
    except (ValueError, KeyError, OSError) as error:
        return {"status": "blocked", "reason": str(error), "initialization_performed": False}


def prepare(config, completion, packet, source_map, host, at, revision=1):
    activation(config, host, at)
    if (completion.get("status") != "completed" or completion.get("trigger") != "explicit-project-dream"
            or completion.get("host") != host or completion.get("project") != config["project"]
            or completion.get("declaration_kind") != "agent-observed"):
        raise ValueError("Successful explicit personal Dream completion evidence required")
    completed = team.stamp(completion["completed_at"])
    if not team.stamp(config["adopted_at"]) <= completed <= at or at - completed > timedelta(hours=24):
        raise ValueError("Pre-adoption, future or historical close cannot deliver")
    evidence_file(completion["evidence"])
    if not completion.get("invocation_ref"):
        raise ValueError("Explicit user invocation evidence reference required")
    # Native session reference may be absent; record_id is explicitly local.
    team.token(completion["record_id"])
    if packet["basis"] != completion["basis"] or packet["basis"]["observed_at"] != completion["completed_at"]:
        raise ValueError("Contribution must bind the observed completed close")
    if packet["owner"] != config["owner"] or not set(source_map) <= set(config["allowed_sources"]):
        raise ValueError("Contribution exceeds adopted source/owner scope")
    if any(Path(path).resolve() != Path(config['allowed_sources'][identity]).resolve()
           for identity, path in source_map.items()):
        raise ValueError('Source location differs from adopted source map')
    team.validate(packet, business_date(completed), ZONE, config["project"])
    team.verify_sources(packet, source_map)
    if not isinstance(revision, int) or revision < 1:
        raise ValueError("Positive explicit contribution revision required")
    root = root_for(config)
    prior = state(root)
    data = team.encoded(packet)
    intent = {"schema": "participant-upload-intent-v1", "owner": config["owner"],
              "name": config["owner"] + "-current-contribution.json", "mime_type": "application/json",
              "folder_id": config["folder_id"], "drive_id": config["drive_id"], "account": config["account"],
              "host": host, "close_id": completion["basis"]["id"], "date": packet["date"],
              "revision": revision, "sha256": sha(data), "completion_sha256": team.digest(completion),
              "baseline": prior["baseline"]}
    pending = prior["pending"]
    if pending:
        old = read(root / "intents" / (pending + ".json"))
        if old == intent:
            return {"intent": pending, "status": "reconcile-before-write", "export": str(root / "current-contribution.json")}
        raise ValueError("Outstanding upload must be reconciled before a different intent")
    baseline = prior["baseline"]
    if baseline and baseline["close_id"] == intent["close_id"] and baseline["sha256"] != intent["sha256"]:
        if revision <= baseline["revision"]:
            raise ValueError("Changed content requires renewed audience review and explicit higher revision")
    identifier = team.digest(intent)
    intent_path = root / 'intents' / (identifier + '.json')
    if intent_path.exists() and intent_path.read_bytes() != team.encoded(intent):
        raise ValueError('Existing immutable intent differs; preserve and reconcile')
    save(root / "intents", identifier + ".json", intent)
    team.write_files(root, {"current-contribution.json": data}, Path(__file__).resolve().parent)
    save(root, "delivery-state.json", {**prior, "pending": identifier})
    return {"intent": identifier, "status": "reconcile-before-write", "export": str(root / "current-contribution.json")}


def load_intent(config, identifier):
    team.sha(identifier)
    root = root_for(config)
    intent = read(root / "intents" / (identifier + ".json"))
    if team.digest(intent) != identifier:
        raise ValueError("Immutable intent changed")
    for key in ("owner", "account", "host", "folder_id", "drive_id"):
        if intent[key] != config[key]:
            raise ValueError("Activation binding changed after preparation")
    return intent


def check_upload(config, identifier, capture, data, at):
    intent = load_intent(config, identifier)
    if sha((root_for(config) / 'current-contribution.json').read_bytes()) != intent['sha256']:
        raise ValueError('Local export changed after audience review')
    current = state(root_for(config))
    if current["pending"] not in {None, identifier}:
        raise ValueError("Different outstanding intent")
    if capture.get("account") != intent["account"] or capture.get("folder_id") != intent["folder_id"] or capture.get("drive_id") != intent["drive_id"]:
        raise ValueError("Provider identity/destination mismatch")
    fresh(capture["observed_at"], at)
    if capture.get("search_complete") is not True or capture.get("name") != intent["name"]:
        raise ValueError("Complete exact-name folder search required")
    matches = capture["matches"]
    if len(matches) > 1:
        raise ValueError("Duplicate destination names; creation blocked")
    baseline = current["baseline"]
    if not matches:
        if baseline or capture.get("prior_write_outcome") != "not-attempted":
            raise ValueError("Missing bound file or uncertain creation; reconcile without retry")
        return {"action": "create", "name": intent["name"], "intent": identifier}
    metadata = matches[0]
    if (metadata.get("name") != intent["name"] or metadata.get("mime_type") != intent["mime_type"]
            or metadata.get("parent_ids") != [intent["folder_id"]] or metadata.get("drive_id") != intent["drive_id"]
            or metadata.get("trashed") is True or not metadata.get("id") or not metadata.get("version")):
        raise ValueError("File identity, format or location mismatch")
    if capture.get("downloaded_file_id") != metadata["id"] or data is None:
        raise ValueError("Downloaded bytes must identify the matched file")
    if baseline and metadata["id"] != baseline["id"]:
        raise ValueError("Bound file ID changed")
    actual = sha(data)
    if actual == intent["sha256"]:
        return {"action": "verified", "intent": identifier, "baseline": {
            "id": metadata["id"], "version": metadata["version"], "sha256": actual,
            "close_id": intent["close_id"], "revision": intent["revision"], "verified_at": capture["observed_at"]}}
    if baseline is None or baseline["sha256"] != actual or baseline["version"] != metadata["version"]:
        raise ValueError("Independent remote edit or no verified baseline; replacement blocked")
    if capture.get("prior_write_outcome") != "not-attempted":
        raise ValueError("Uncertain update requires reconciliation; no blind retry")
    return {"action": "update", "id": metadata["id"], "required_version": metadata["version"], "intent": identifier}


def record_upload(config, identifier, capture, data, at):
    result = check_upload(config, identifier, capture, data, at)
    if result["action"] != "verified":
        raise ValueError("Matching provider readback required before recording success")
    root = root_for(config)
    current = state(root)
    if current["pending"] is None and current['baseline']:
        fields = ('id', 'version', 'sha256', 'close_id', 'revision')
        if all(current['baseline'][key] == result['baseline'][key] for key in fields):
            return result
    if current["pending"] != identifier:
        raise ValueError("Only the outstanding intent can advance the baseline")
    save(root / "history", identifier + ".json", {"intent": identifier, "readback": capture, "baseline": result["baseline"]})
    save(root, "delivery-state.json", {"baseline": result["baseline"], "pending": None})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["status", "prepare", "check-upload", "record-upload"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--host", required=True)
    for name in ("completion", "packet", "source-map", "capture", "download"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--intent")
    parser.add_argument("--revision", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        config, at = read(args.config), datetime.now(timezone.utc)
        root = root_for(config)
        for path in (args.config, args.completion, args.source_map, args.capture):
            if path and not path.resolve().is_relative_to(root):
                raise ValueError("Configuration and operational records must use designated private storage")
        if args.operation == "status":
            result = status(config, args.host, at)
        elif args.operation == "prepare":
            result = prepare(config, read(args.completion), read(args.packet), read(args.source_map), args.host, at, args.revision)
        else:
            activation(config, args.host, at)
            operation = record_upload if args.operation == "record-upload" else check_upload
            result = operation(config, args.intent, read(args.capture), args.download.read_bytes() if args.download else None, at)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        parser.exit(2, f"Participant delivery blocked: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
