# Creative Review Workbench

```text
Objective -> distinct directions -> exact human critique -> recorded round
                    revision -> next round -> inspect what changed
                          JSON export/import keeps the work local
```

## What it does

A local browser workspace for Second_Brain's human-led creative practice. Compare
directions using qualitative lenses, preserve the reviewer's words, and see exactly
what changed between recorded rounds. No numerical ranking or automatic winner is
imposed: the [Artistic Director rubric](../../projects/artistic-director/ai/critique-rubric.md)
is a lens, not a scorecard.

The workbench follows the existing
[collaboration loop](../../projects/artistic-director/ai/collaboration-loop.md).
It offers a usable review surface without altering project memory or historical logs.

## Prerequisites

- A modern browser (Chrome, Edge, Firefox, or Safari).
- A Second_Brain/Open Brain checkout containing this directory.
- No build, package installation, API key, database connection, or hosting account.
- Node.js 22+ only if you want to run the data-model tests.

## Step-by-step instructions

1. Open `index.html` in a browser. Keep `core.js`, `app.js`, and `style.css` beside it.
   If your browser blocks local scripts, serve this folder on loopback instead:

   ```bash
   python -m http.server 8765 --bind 127.0.0.1 --directory dashboards/creative-review
   ```

   Then open `http://127.0.0.1:8765`. This optional fallback requires Python 3.

2. Enter the objective, reviewer, and two or more materially different directions.
   Use the lenses that matter: audience effect, what to protect, what to change,
   unresolved questions, evidence/rights, exact critique, and revision response.
   Leave an unknown field empty rather than inventing an answer.

3. Add a round note and choose **Record this round** before revising. You may mark
   a direction for revision, hold it, or reject it. These are creative dispositions,
   not permission to publish, spend, contact a client, or promote a lesson.

4. Revise the current cards and record another round. Expand the history to read
   exact prior critiques and a before/after field comparison. Removing a current
   direction does not remove it from recorded rounds.

5. Choose **Export review JSON** before closing and verify that the download was
   saved. Import the file next time. The export includes current drafts, an
   unrecorded round note, and recorded history. Keep sensitive reviews private.
   If the browser blocks downloads, choose **Show JSON backup**, copy the selected
   text into a private `.json` file, and import that file next time. Click the backup
   button again after edits to refresh its snapshot.

## Expected outcome

A responsive side-by-side review workspace with up to eight directions, thirty
recorded rounds, and portable JSON persistence. Blank, rejected, and held states
remain distinct. Historical critique survives current edits. No automatic memory
promotion, AI call, tracking, upload, or browser storage occurs.

## Data and privacy

The page keeps data in memory only. Refreshing or closing without a verified export
can lose work. A leave-page warning helps but is not guaranteed by all browsers.
Imports are validated before replacement; replacing edited work needs confirmation.
Files are limited to 512 KB, fields to 6000 characters, and invalid IDs/states/history
are rejected. Text is rendered as text, never as HTML. A content security policy
blocks network requests and third-party resources. Footer links open only when clicked.

Snapshots preserve history inside the app, but exported JSON is user-editable.
They are not signatures, authenticated approvals, or tamper-proof evidence. The
workbench does not verify rights or claims; it keeps those questions visible.

## Validation

```bash
node --test dashboards/creative-review/core.test.cjs
```

Tests cover exact critique retention, immutable prior rounds, rejected and held
options, input requirements, import round-trips, invalid states/IDs/history,
size limits, change comparison, and markup as plain data. No cloud instance is
used; this is a local companion to the existing creative practice.

## Troubleshooting

- **Record is blocked:** supply the objective, reviewer, direction names, and note.
- **Lost work after closing:** the page does not autosave. Import the last export.
- **Import fails:** use an exported version-1 review under 512 KB; unknown fields
  are discarded, but malformed known fields are rejected.
- **Review reaches its limit:** export the existing review before starting a separate
  one. Do not treat a browser download request as proof the file was saved.

## Provenance

Built on Second_Brain's Artistic Director collaboration loop and critique rubric,
within [Nate B. Jones's Open Brain](https://github.com/NateBJones-Projects/OB1)
ecosystem. More practical systems: [Nate's writing](https://substack.com/@natesnewsletter)
and [website](https://natebjones.com).
