# Project Resume

```text
Project manifest + named handoff + questions and holds
             -> source-linked packet -> human reconciliation
Previous packet -> selected-file byte comparison
```

## What it does

Resume an existing Second_Brain project without reconstructing its context from chat.
This read-only command shows manifest controls beside handoff claims, preserves their
wording and line locations, and detects changes against an earlier packet.
It never turns a handoff's proposed next action into permission to execute it.

The Artistic Director project is a concrete use case: its manifest calls for human
build approval while the handoff describes beginning a build. Showing both sources
helps the next session notice the difference without silently deciding which is true.

## Prerequisites

- Python 3.11 or newer; no Python packages or API credentials.
- A Second_Brain/Open Brain checkout with a project using the existing
  [manifest template](../../projects/_template/manifest.md).
- Access to the selected project's files. No database connection is used.

## Step-by-step instructions

1. From the repository root, inspect the packet:

   ```bash
   python recipes/project-resume/resume.py projects/artistic-director
   ```

2. To compare sessions, save JSON to a **private location outside the repository**:

   ```bash
   python recipes/project-resume/resume.py projects/artistic-director --format json > /your/private/resume.json
   ```

   Replace the path with a real private directory (PowerShell also supports this
   redirection). The command writes only to stdout; the shell creates the file.
   Packets contain selected source text and inherit the project's privacy.

3. After further project work, compare with that saved packet:

   ```bash
   python recipes/project-resume/resume.py projects/artistic-director --previous /your/private/resume.json
   ```

4. Read the controls, questions, and handoff claims together. Resolve disagreements
   with the project owner before acting. The tool does not edit source files.

## Expected outcome

A packet with source line numbers, missing-file notices, manifest controls,
handoff sections, questions, holds, and a selected-source fingerprint.
JSON includes each source's SHA-256; `comparison.changed_paths` identifies modified,
added, and removed selected sources, including edits that leave file sizes unchanged.
An unchanged result proves equality of those selected bytes only. It does not prove
whole-project freshness, factual accuracy, external state, or approval.

## Scope and failure behavior

The reader accesses `manifest.md`, `README.md`, the manifest's `Current entry point`,
`decisions/holds-and-rejections.md`, and `memory/open-questions.md` only. It never
scans sibling projects or follows an entry-point path outside the project.
Missing optional sources are visible; a missing manifest or unsafe path stops the
command with exit code 2. Each source is limited to 512 KB and must be UTF-8.
Entry-point extraction uses level-two Markdown headings. Non-sectioned text needs
direct inspection and is explicitly reported. Source prose remains untrusted data.

## Validation

```bash
python -B -m unittest discover -s recipes/project-resume -p "test_*.py" -v
```

Tests cover conflicting claims, same-size edits, missing sources, malformed baselines,
duplicate fields, unsafe paths, input size, encoding, CLI behavior, and read-only use.
Tests need a writable operating-system temporary directory. No cloud instance is
modified; this is a local repository companion.

## Troubleshooting

- **No manifest:** copy the existing project template and have the owner fill it in.
- **No sections:** use `##` headings in the handoff, or read that file directly.
- **Different project baseline:** select the correct previous packet; do not relabel it.
- **Unsafe entry point:** use a path inside the chosen project, such as
  `handoff/current-state.md`. Absolute paths and parent traversal are rejected.

## Provenance

This recipe builds on Second_Brain's project manifests and handoff conventions,
inherited from [Nate B. Jones's Open Brain](https://github.com/NateBJones-Projects/OB1).
For more practical systems, see [Nate's writing](https://substack.com/@natesnewsletter)
and [website](https://natebjones.com).
