# Local Markdown Link Check

Find broken file references before handing a project to another reader.
Choose exact Markdown inputs and a repository root; the checker parses links
and images, reports missing files and case mismatches, and points to the source
block containing each reference. It never follows network links.

## Requirements

An Open Brain / Second_Brain repository, Node.js 22+, and npm. This local
companion uses pinned `markdown-it` to parse Markdown rather than treating
links inside code examples as real references. Installation requires npm
registry access; checking has no network behavior or credentials.

## 1. Install

From this recipe folder:

```bash
npm ci --ignore-scripts
npm test
```

**Done when:** the tests pass and dependencies are installed locally.

## 2. Check selected documents

From the repository root:

```bash
node recipes/local-link-check/check.cjs --root . projects/artistic-director/README.md projects/artistic-director/manifest.md
```

Inputs are exact paths relative to `--root`, with no automatic recursive scan.
Ordinary relative links resolve from the source file's directory. A link
starting with `/` resolves from the explicitly supplied repository root.

**Done when:** the JSON lists the selected file count and reference results.

## 3. Repair or explain broken references

| State | Meaning |
| --- | --- |
| `file-exists` | Local target exists; contents are not validated |
| `directory-exists` | Directory target exists; no index file is assumed |
| `missing-file` | A path component or target is missing |
| `path-case-mismatch` | Spelling differs in case, including on Windows |
| `outside-root` | Target would leave the declared repository |
| `link-unsupported` | Target traverses a symlink or junction |
| `unsupported-path` | Backslash, colon, or NUL in a local path |
| `invalid-url-encoding` | URL path cannot be decoded |
| `external-unchecked` | Scheme or network destination; never fetched |

Source line ranges are inclusive and identify the **containing Markdown
block**, not necessarily the exact line within a multiline paragraph.
Reference-style links and image paths are included; code blocks and inline
code are excluded by the parser.

Exit codes: 0 no detected local path failures; 1 local path failures; 2 invalid
inputs or unreadable files. No result implies that a project is complete,
approved, or ready to publish. Fixes remain deliberate human edits.

**Done when:** reported broken references have been corrected or explicitly
accounted for in the handoff.

## Coverage limits

Fragments are marked `fragment_unchecked`: a real file can still have a broken
heading link. Raw HTML is counted in `skipped_html`, not parsed for URLs.
Unresolved reference definitions and malformed Markdown may be parsed as plain
text and are not diagnosed. External URLs, GitHub issue routes, dynamic site
routes, templates, and renderer-specific anchor rules are outside this check.

Choose the root that matches your link semantics. A root of one project will
correctly reject links leaving that project; a repository root permits links
to shared repository docs. No content is uploaded or modified. Limits: 100
input documents, 512 KiB per document. Use a stable filesystem during checks.

## Verification and provenance

Tests cover real Markdown parsing, encoded paths, source ranges, reference
links, image paths, code exclusion, containment, casing, raw HTML reporting,
and explicit unchecked states. No live Supabase behavior is claimed.

Original companion for Second_Brain, built on
[Open Brain](https://github.com/NateBJones-Projects/OB1) by Nate B. Jones:
[newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Authored with AI assistance by Mira.
Markdown parsing uses [markdown-it](https://github.com/markdown-it/markdown-it)
under its MIT license.
