"""Trace file changes through human-declared project dependencies."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

FIELDS = {"id", "path", "kind", "depends_on", "rationale"}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def validate_graph(spec):
    if not isinstance(spec, dict) or set(spec) != {"nodes"} or not isinstance(spec["nodes"], list):
        raise ValueError("Map needs a nodes list")
    if not 1 <= len(spec["nodes"]) <= 200:
        raise ValueError("Map must have 1–200 nodes")
    nodes = {}
    for node in spec["nodes"]:
        if not isinstance(node, dict) or set(node) != FIELDS:
            raise ValueError("Node fields must match the example exactly")
        if any(not isinstance(node[key], str) for key in FIELDS - {"depends_on"}):
            raise ValueError("Node fields must be strings")
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", node["id"]) or node["id"] in nodes:
            raise ValueError("Node IDs must be unique lowercase identifiers")
        if node["kind"] not in {"source", "decision", "artifact"} or not node["rationale"].strip() or len(node["rationale"]) > 4000:
            raise ValueError("Provide kind and a human-written dependency rationale")
        name = node["path"]
        rel = PurePosixPath(name)
        if (not name or str(rel) != name or rel.is_absolute() or any(c in name for c in '\\:*?[]')
                or any(p.startswith(".") for p in rel.parts)):
            raise ValueError("Paths must be exact visible project-relative files")
        deps = node["depends_on"]
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps) or len(set(deps)) != len(deps):
            raise ValueError("Dependencies must be unique node IDs")
        nodes[node["id"]] = dict(node, depends_on=sorted(deps))
    done, active = set(), set()

    def visit(key):
        if key not in nodes:
            raise ValueError(f"Unknown dependency: {key}")
        if key in active:
            raise ValueError(f"Dependency cycle through {key}")
        if key in done:
            return
        active.add(key)
        for dep in nodes[key]["depends_on"]:
            visit(dep)
        active.remove(key)
        done.add(key)
    for key in nodes:
        visit(key)
    return nodes


def snapshot(root, spec):
    nodes = validate_graph(spec)
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Root must be a directory")
    records, total = [], 0
    for key, node in sorted(nodes.items()):
        path = root
        for part in PurePosixPath(node["path"]).parts:
            path = path / part
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError("Dependency file links are unsupported")
        sha = None
        if path.exists():
            if not path.is_file() or not path.resolve().is_relative_to(root):
                raise ValueError("Dependency must be a contained file")
            with path.open("rb") as stream:
                raw = stream.read(2 * 1024 * 1024 + 1)
            total += len(raw)
            if len(raw) > 2 * 1024 * 1024 or total > 16 * 1024 * 1024:
                raise ValueError("Map exceeds 2 MiB per file or 16 MiB total")
            sha = hashlib.sha256(raw).hexdigest()
        records.append(dict(node, sha256=sha))
    payload = {"version": 1, "nodes": records}
    return dict(payload, digest=fingerprint(payload))


def validate_snapshot(value):
    if not isinstance(value, dict) or set(value) != {"version", "nodes", "digest"} or type(value["version"]) is not int or value["version"] != 1:
        raise ValueError("Invalid snapshot shape or version")
    if not isinstance(value["nodes"], list):
        raise ValueError("Invalid snapshot nodes")
    graph = []
    for row in value["nodes"]:
        if not isinstance(row, dict) or set(row) != FIELDS | {"sha256"}:
            raise ValueError("Invalid snapshot node")
        if row["sha256"] is not None and (not isinstance(row["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", row["sha256"])):
            raise ValueError("Invalid snapshot hash")
        graph.append({key: row[key] for key in FIELDS})
    validate_graph({"nodes": graph})
    if value["digest"] != fingerprint({"version": 1, "nodes": value["nodes"]}):
        raise ValueError("Snapshot digest mismatch")
    return {row["id"]: row for row in value["nodes"]}


def compare(before, after):
    old, new = validate_snapshot(before), validate_snapshot(after)
    changed = sorted(key for key in old.keys() | new.keys() if old.get(key) != new.get(key))
    downstream = {}
    for rows in (old, new):
        for key, row in rows.items():
            for dep in row["depends_on"]:
                downstream.setdefault(dep, set()).add(key)
    affected = {}
    for trigger in changed:
        queue, visited = deque([(trigger, [trigger])]), {trigger}
        while queue:
            key, chain = queue.popleft()
            for child in sorted(downstream.get(key, set())):
                if child in visited:
                    continue
                visited.add(child)
                route = chain + [child]
                affected.setdefault(child, []).append({"trigger": trigger, "chain": route})
                queue.append((child, route))
    reviews = []
    for key in sorted(affected):
        node = new.get(key, old.get(key))
        reviews.append({"id": key, "kind": node["kind"], "path": node["path"],
                        "rationale": node["rationale"], "present_in_current_map": key in new,
                        "routes": affected[key]})
    return {"changed": changed, "review_candidates": reviews,
            "missing_current_files": sorted(key for key, node in new.items() if node["sha256"] is None),
            "before_digest": before["digest"], "after_digest": after["digest"],
            "notice": "Review candidates from declared dependencies, not automatic invalidation or execution authority."}


def read_json(name):
    with Path(name).open("rb") as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("Input JSON exceeds 2 MiB")
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["snapshot", "compare"])
    parser.add_argument("--root", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--before")
    args = parser.parse_args()
    try:
        current = snapshot(args.root, read_json(args.map))
        if args.mode == "compare":
            if not args.before:
                raise ValueError("Compare requires --before SNAPSHOT.json")
            result = compare(read_json(args.before), current)
            attention = bool(result["changed"] or result["missing_current_files"])
        else:
            result = current
            attention = any(row["sha256"] is None for row in current["nodes"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if attention else 0
    except (OSError, ValueError) as exc:
        print(f"impact: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
