# Workspace GitHub

## What it does

This skill carries GitHub reviews and authorized Git changes through a scoped,
verified workflow. Its read-only helper summarizes dirty state and checks
declared candidate/test inputs without modifying Git or Open Brain data.

## Prerequisites

- A working Open Brain installation as this contribution's host context.
- Git and Python 3.9 or newer for the optional inspector.
- An authenticated GitHub CLI or provider for remote operations.

Open Brain hosts the workflow; the inspector itself has no database dependency.

## Supported Clients

Agents able to load Markdown skills, including Codex and Claude Code. Automatic
discovery depends on the client's configuration; manual loading also works.

## Installation

1. Place this folder at skills/workspace-github in your Second Brain checkout.
2. Load [SKILL.md](SKILL.md) and [the workspace adapter](references/workspace.md)
   through your client's supported skill mechanism.
3. Preserve root instructions and supply your existing account/approval context.

## Trigger Conditions

Use for GitHub PR or issue inspection, reviews, checks and explicitly authorized
Git publication. Ordinary file edits do not activate publication.

## Step-by-step instructions

1. Name the requested endpoint and exact repository/candidate.
2. Read the workspace adapter and current repository controls.
3. Optionally run python skills/workspace-github/scripts/preflight.py --repo
   YOUR_ABSOLUTE_REPO_ROOT --candidate YOUR_FILE --input YOUR_TEST.
   Keep that command on one line and repeat flags for additional files.
4. Validate the scoped change, execute only authorized transitions, then freshly
   verify remote state and checks for the expected SHA.

For helper tests, run python -m unittest discover -s
skills/workspace-github/tests on one line from the checkout root.

## Expected outcome

A review with source locations, or the requested Git terminal state with exact
scope and destination evidence. The helper's eligible result is not a test pass,
approval, owner adoption or evidence of hosted success.

## Troubleshooting

- Root/path blocked: use the exact Git root and selected relative files.
  A deletion must name a tracked file; required test inputs must exist.
- Changed input blocked: include the changed test/dependency deliberately or
  choose evidence applicable to the candidate.
- Remote/account failure: diagnose authenticated access before retrying; never
  print secrets or substitute another account without authority.

## Open Brain context

Explore Nate B. Jones's [Open Brain guidance](https://natesnewsletter.substack.com/)
and [work](https://natebjones.com/) for the surrounding ecosystem.

## Content and Git context

The helper retains --repo, --candidate and --input. It reports selected-content
and Git-context fingerprints separately, plus bounded staged counts. An eligible
candidate may still have unrelated staged files; inspect the commit unit before
committing. Tracked deletion candidates have null content hashes. No GitHub or
Open Brain action is performed by the inspector.

Changes to this package require its helper tests and repository contribution
checks. Live Open Brain testing remains a separate owner readiness requirement;
synthetic Git fixtures do not establish it. Skill inclusion is not automatic loading.
