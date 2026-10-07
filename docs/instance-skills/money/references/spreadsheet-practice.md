# Spreadsheet practice

Google Sheets and XLSX are core Money capabilities. Use the available connected
Sheets or standalone spreadsheet skill for actual APIs, file lifecycle and runtime.
Discover callable capabilities and exact file access; an installed skill is not
proof of either. Do not hardcode a vendor runtime, copy its manual, install tools,
switch accounts, or substitute a different destination without authorization.
Live Excel application control is outside this version.

## Inspect and preserve

Before proposing edits, inspect relevant tabs, headers, instructions, reporting
basis, formulas and effective values, native tables, validation and dependencies.
Use bounded reads but include dependent outputs. Dates, units, signs, period
coverage and category definitions must be understood before interpretation.
Blank, zero, unknown and not applicable are distinct. Cached values alone do not
establish successful recalculation. Treat the existing workbook as the reference.

Make targeted edits and preserve unrelated formulas, formatting, validations,
tables, named ranges, annotations, links, protection and historical periods.
If the selected tool cannot preserve a consequential native feature, withhold the
dependent edit and explain the limitation; do not flatten it for convenience.
Copy a template when requested or required by its lifecycle, preserving the source.
Keep a previous working local version until replacement validates successfully.

## Build and calculate

Use the simplest structure that separates inputs, calculations and outputs enough
to audit the decision. These roles do not require separate tabs. Label editable
assumptions, source dates, units, reporting basis and material exclusions. Store
typed numbers and dates; formatting is not data conversion. Use proportionate
category validation and readable formats following the template/provider guidance.

Keep derived outputs formula-driven. Use bounded compatible ranges, appropriate
absolute/relative references, stable lookup keys and consistent date boundaries.
Quote cross-sheet names. Check month-end dates, signs and copied formulas. A
missing opening balance must not become zero; zero denominators need a meaningful
unavailable result. Do not conceal unexpected errors with blanket error-to-zero
wrappers. Keep checks independent enough to catch a wrong aggregation.

Reconcile account cash, settlements and outstanding obligations separately. Keep
capital, loans, transfers, distributions, equipment and third-party movements out
of operating results where the established basis requires it. Do not lose these
movements from cash. Apply bookkeeping-basis.md and operating-finance.md for meaning.

## Refresh and roll forward

Before a consequential write, freshly compare the affected inputs, formulas and
dependencies with the state used to prepare the change. Use provider revision
preconditions where supported; otherwise report the residual concurrency limit.
If another person changed relevant content, reconcile the change before writing.
Fresh readback after writing cannot by itself prevent lost concurrent edits.

After a timeout or uncertain save, inspect the actual destination before retrying.
Identify which rows/ranges landed, compare stable IDs and intended content, and
retry only the missing authorized portion. Do not repeat an append blindly or
restore a whole workbook over someone else's edits. If the destination cannot
be inspected, withhold the dependent retry and report the uncertainty. Multi-step
changes report each completed, failed or uncertain step separately.

Preserve raw/source evidence and its as-of date. Append or merge by stable business
or transaction IDs and period; detect overlapping imports and duplicate events.
If keys are absent, disclose the ambiguity and propose a reviewable matching rule
rather than silently deleting similar purchases. A changed record with the same
ID is a correction to inspect, not a second transaction or automatic overwrite.

Keep actual history intact. Advance the actual/forecast cutoff only through valid
complete coverage or an explicit partial-period label. Future adjustments belong
to absolute dated periods, not shifting column positions. Extend formulas,
validations and affected native ranges deliberately. Test a new actual period
and a future adjustment in a disposable local copy when roll-forward is material.

## Verify and report

Recalculate through an available calculation engine. Inspect formula errors and
independently compute decision-critical expected results from source inputs.
Test consequential blank/zero/date and representative copy cases. Check preserved
features and the affected view visually when layout or interpretation requires it.

Before external content writes, verify identity and the authorized parent folder
or workspace. After Sheets edits, freshly read back formulas, effective values,
affected validations/features, identity and destination. Creation/edit success
alone is insufficient. After XLSX export, reopen the saved file and verify formulas,
recalculated results and the features relevant to the edit. Report local files,
externally saved records, approvals and payments as separate completion states.

Record dated capability evidence in the local adapter's money-capability.json:
contract validation, XLSX execution, and native Sheets execution are separate
claims. Do not mark another workspace tested from a Core run or infer a successful
Sheets edit from an XLSX result. If a calculation engine, access or authorized
destination is unavailable, identify only the unsupported operation and continue
independent supported work. Never report cached inspection as an executed refresh.

Package correctness and operational readiness are separate. An owner may adopt
supported analysis while Sheets editing remains unavailable pending its own
authorized destination test. An abnormal calculation-engine process exit remains
an execution limitation even when assertions finished. Reuse shared validation
only for matching content/runtime fingerprints; validate each workspace's actual
provider access, routing and permitted destinations independently.
