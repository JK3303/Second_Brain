"""Compile explicit color tokens and check declared opaque sRGB color pairs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

NAME = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")
THRESHOLDS = {"text": 4.5, "large-text": 3.0, "ui": 3.0}


def luminance(color):
    values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in values]
    return sum(x * weight for x, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    first, second = sorted((luminance(foreground), luminance(background)))
    return (second + 0.05) / (first + 0.05)


def compile_palette(spec):
    if not isinstance(spec, dict) or set(spec) != {"colors", "pairs"}:
        raise ValueError("Specification needs exactly colors and pairs")
    colors, pairs = spec["colors"], spec["pairs"]
    if not isinstance(colors, dict) or not 1 <= len(colors) <= 100:
        raise ValueError("Provide 1–100 named colors")
    if any(not isinstance(k, str) or not NAME.fullmatch(k) or not isinstance(v, str) for k, v in colors.items()):
        raise ValueError("Color names must be lowercase CSS-safe identifiers")
    resolved = {}

    def resolve(name, stack):
        if name in resolved:
            return resolved[name]
        if name in stack:
            raise ValueError("Color alias cycle: " + " -> ".join(stack + [name]))
        if name not in colors:
            raise ValueError(f"Unknown color: {name}")
        value = colors[name]
        if HEX.fullmatch(value):
            resolved[name] = value.lower()
        elif re.fullmatch(r"\{[a-z][a-z0-9-]{0,63}\}", value):
            resolved[name] = resolve(value[1:-1], stack + [name])
        else:
            raise ValueError(f"Color {name} must be #RRGGBB or a {{token-name}} alias")
        return resolved[name]

    for name in sorted(colors):
        resolve(name, [])
    if not isinstance(pairs, list) or not 1 <= len(pairs) <= 200:
        raise ValueError("Declare 1–200 usage pairs; an empty check is unsupported")
    labels, checks = set(), []
    for pair in pairs:
        if not isinstance(pair, dict) or set(pair) != {"name", "foreground", "background", "usage"}:
            raise ValueError("Pair needs name, foreground, background, usage")
        if any(not isinstance(v, str) for v in pair.values()):
            raise ValueError("Pair fields must be strings")
        if not NAME.fullmatch(pair["name"]) or pair["name"] in labels:
            raise ValueError("Pair names must be unique lowercase identifiers")
        labels.add(pair["name"])
        if pair["usage"] not in THRESHOLDS:
            raise ValueError("Usage must be text, large-text, or ui")
        fg, bg = resolve(pair["foreground"], []), resolve(pair["background"], [])
        ratio = contrast(fg, bg)
        minimum = THRESHOLDS[pair["usage"]]
        checks.append(dict(pair, ratio=ratio, minimum=minimum, passes=ratio >= minimum))
    fingerprint = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"source_sha256": fingerprint, "colors": dict(sorted(resolved.items())), "checks": checks,
            "notice": "Declared opaque color pairs only; not a complete accessibility audit or brand approval."}


def css(report):
    if any(not row["passes"] for row in report["checks"]):
        raise ValueError("CSS export held: inspect and resolve the failed declared pairs")
    return (f"/* Palette source SHA-256: {report['source_sha256']} */\n:root {{\n"
            + "".join(f"  --color-{key}: {value};\n" for key, value in report["colors"].items()) + "}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec")
    parser.add_argument("--format", choices=["report", "css"], default="report")
    args = parser.parse_args()
    try:
        with Path(args.spec).open("rb") as stream:
            raw = stream.read(131073)
        if len(raw) > 131072:
            raise ValueError("Specification exceeds 128 KiB")
        report = compile_palette(json.loads(raw))
        if args.format == "css":
            sys.stdout.write(css(report))
        else:
            print(json.dumps(report, indent=2))
        return 1 if any(not row["passes"] for row in report["checks"]) else 0
    except (OSError, ValueError) as exc:
        print(f"palette: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
