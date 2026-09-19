# Brand Palette to CSS

Turn human-selected brand colors into named CSS variables without repeatedly
copying hex values. Declare how each foreground/background pair will be used;
inspect its contrast before exporting the palette.

This bridges a written brand direction and implementation. It does not infer
approved colors from prose. The supplied palette is a fictional demonstration,
not an approved Grace Gems design or a change to its brand system.

## Requirements

An Open Brain / Second_Brain workflow and Python 3.11+, standard library only.
No packages, model, browser service, credentials, or network connection.

## 1. Choose tokens and uses

Copy `example-palette.json` into your working area. Colors accept opaque
six-digit `#RRGGBB` values or aliases such as `{paper}`. Semantic aliases let
`surface`, `text`, and `action` keep stable names when their underlying palette
changes. Unknown references and alias cycles fail explicitly.

For each real use, add a named pair with `foreground`, `background`, and `usage`:

| Usage | Minimum ratio | Intended check |
| --- | --- | --- |
| `text` | 4.5:1 | Ordinary text |
| `large-text` | 3:1 | Text that actually meets the large-text definition |
| `ui` | 3:1 | Relevant non-text UI boundaries or graphics against adjacent colors |

The text thresholds follow [W3C's contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
Large text is at least 18 pt, or 14 pt bold; merely naming a pair `large-text`
does not verify its rendered size. The UI check follows
[non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
Choose the appropriate pair and context; exceptions are not inferred.

**Done when:** every declared pair corresponds to an actual intended use.

## 2. Inspect the report

From the repository root:

```bash
python recipes/brand-palette/palette.py recipes/brand-palette/example-palette.json
```

The JSON report shows resolved tokens, unrounded contrast ratios, minimums,
and pass/fail per pair. It includes a SHA-256 of the canonical input JSON.
Comparisons use full precision; a rounded display value cannot turn a failure
into a pass. There is no numerical rating of aesthetic quality.

**Done when:** the human has reviewed the chosen colors and failed pairs.

## 3. Export CSS

```bash
python recipes/brand-palette/palette.py recipes/brand-palette/example-palette.json --format css
```

Output uses `:root` variables such as `--color-surface`. Save the output as UTF-8
CSS and reference it in your existing implementation. The tool writes only to
standard output and does not edit or deploy a website. Export is held if any
declared pair fails; inspect the report and revise the palette or usage.

Exit codes: 0 for passing declared pairs; 1 for a report with failed pairs;
2 for malformed input or a held CSS export. Shell redirection may create an
empty file on failure, so check the exit status before replacing working CSS.

**Done when:** exported tokens match the selected palette and are tested in
the actual rendered interface.

## Limits and verification

Only opaque sRGB hex colors are supported. No alpha, gradients, photographs,
blend modes, computed styles, font metrics, focus behavior, or unlisted pairs
are checked. Passing this report is not WCAG conformance or brand approval.
Limits: 100 tokens, 200 pairs, 128 KiB input. Names are restricted to lowercase
CSS-safe identifiers; arbitrary CSS values and remote resources are rejected.

```bash
python -m unittest discover -s recipes/brand-palette -p "test_*.py" -v
```

Tests cover known ratios, symmetry, threshold precision, alias resolution,
cycles, unsafe values, duplicate pairs, deterministic output, and fingerprints.
This local companion does not exercise a live Supabase instance.

## Provenance

Original companion for Second_Brain, which builds on
[Open Brain](https://github.com/NateBJones-Projects/OB1) by Nate B. Jones:
[newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Authored with AI assistance by Mira.
