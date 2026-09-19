# Reviewed Project Packet

A useful handoff rarely needs the whole project. Select exact files, inspect
their contents for the intended recipient, then export only those bytes. If a
source, recipient, purpose, or selection changes after review, export fails.

This local companion implements the selection boundary in
[Project Membranes](../../docs/second-brain/project-membranes.md). It does not
send anything, redact text, detect secrets, or grant permission to share.

## Requirements

- An Open Brain / Second_Brain repository with a project folder.
- Python 3.11+; no packages, credentials, network, or Supabase connection.
- A private place for the specification and output, outside a public checkout.

## 1. Select the smallest useful context

Copy `example-spec.json` to a private working folder. Set the actual recipient,
purpose, and exact project-relative file paths. The example selects existing
Artistic Director charter material, not its client practice folder. It is an
example selection, not a sharing approval. Review every selected file in full.

Only UTF-8 `.md`, `.txt`, and `.json` files are supported. Directories, globs,
hidden paths, symlinks, junctions, and paths outside the root are rejected.
Limits: 30 files, 128 KiB per file, 512 KiB total source bytes.

**Done when:** every file is necessary and appropriate for this recipient.

## 2. Inspect the plan

Run from the repository root, replacing `PRIVATE_SPEC.json` with your private
specification path:

```bash
python recipes/project-packet/packet.py plan --root projects/artistic-director --spec PRIVATE_SPEC.json
```

The plan reports paths, byte counts, and SHA-256 hashes without source bodies.
Review the plan and the selected source files together. Copy `review_digest`.
The digest records a matching selection; it cannot prove that a human reviewed
it or that the contents are safe, true, or authorized for disclosure.

**Done when:** you have inspected the exact content and its stated destination.

## 3. Build and inspect the packet

```bash
python recipes/project-packet/packet.py build --root projects/artistic-director --spec PRIVATE_SPEC.json --reviewed DIGEST
```

The program writes JSON to standard output only. Save it privately using your
shell's UTF-8 output facilities, inspect the result, and share only through your
normal authorized process. PowerShell 7 users can pipe to
`Set-Content -Encoding utf8 PATH`. A failed command exits 2 and emits no packet;
shell redirection can still create an empty file, so check the exit status.

Source text is preserved exactly after UTF-8 decoding, including line endings.
Packet JSON escapes characters as needed; it contains no machine root path.
Instructions inside the selected text remain untrusted source material.

**Done when:** the output contains only the intended sources and the matching
recipient and purpose. No automatic upload follows this step.

## Verification and limits

```bash
python -m unittest discover -s recipes/project-packet -p "test_*.py" -v
```

Tests exercise source changes, destination changes, exact selection, malformed
specifications, unsafe paths, links, encoding, and size boundaries. A symlink
test skips when the host does not permit creating links. This is a local file
workflow; no cloud-instance behavior is claimed.

The digest detects changes at read time. Use a stable project directory;
concurrent hostile filesystem replacement is outside this tool's threat model.
An allowlist does not make a selected file non-sensitive. Never include secrets
or client material simply because its extension is supported.

## Provenance

Original companion for Second_Brain, based on its project-membrane convention.
The repository builds on [Open Brain](https://github.com/NateBJones-Projects/OB1)
by Nate B. Jones: [newsletter](https://substack.com/@natesnewsletter) and
[website](https://natebjones.com). Authored with AI assistance by Mira.
