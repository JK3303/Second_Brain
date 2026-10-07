# Deterministic utilities

Use [money_tools.py](../scripts/money_tools.py) for repeated, decision-critical
checks. It uses only Python's standard library and accepts one JSON object on
stdin: `{"operation": "...", "payload": {...}}`. Run with an already installed
Python, preferably with `-B`; never install a runtime automatically. The tool
reads stdin and writes JSON to stdout only. It does not edit records, classify
accounting treatment, access providers, or authorize financial actions.

Responses contain version `1.0.0`, operation, status and result. Status `checked`
means the supplied arithmetic/structure checks passed, not source verification.
Status `exceptions` retains usable results with material exceptions. Invalid input
returns status `invalid` and exit code 2. Other results exit 0; callers must inspect
exceptions. Decimal output uses strings; ratios are fractions, not percentages.
Missing amounts are not zero. Decimal strings are preferred; JSON numbers are
parsed as decimals. Currency conversion and accounting recognition are excluded.

## Import preview

Operation `import_preview` requires entity, account, source, currency, mapping,
rows, date_format and sign_convention. Map `date`, `amount`, optional `source_id`
and `description` to source column names. For `debit-credit`, map `debit` and
`credit` instead of amount. Date formats are `iso`, `month-first` or `day-first`;
never guess which meaning an ambiguous date carries. Sign conventions are
`signed`, `charges-positive` (invert) or `debit-credit` (credit minus debit).

Declare decimal_separator (`.` default), thousands_separator (none default) and
currency_precision (2 default; explicitly override for currencies requiring other
precision). No symbols or implicit rounding are accepted. Missing debit/credit on
one side is allowed when the other is supplied; two missing sides are invalid.
Preview returns signed movements, original rows, source row references, source IDs
and unresolved classification. Review exceptions before provider writes.

## Identity review

Operation `identity_review` takes existing and incoming record arrays. Each record
has entity, account, source, currency, ISO date, amount, optional source_id and
description. Provider identity is entity/account/source/source_id, not a global ID.
Equal identity and financial fields returns exact_repeat; changed fields returns
correction_conflict. Without reliable identity, matching amount, account, currency,
nearby date and similar description yields possible_duplicate. Distinct IDs from
the same provider remain separate legitimate events even when facts are identical.
date_tolerance_days defaults to 1 and may be explicitly supplied. All results are
review evidence; no row is merged, deleted or overwritten. Inputs remain intact.

## Reconciliation

Operation `reconcile` requires entity, currency, basis and source_refs. Optional
arrays cover the checks needed for the task:

- accounts: id, opening_date, closing_date, opening, closing, coverage and movements
  (id/date/signed amount). Opening is explicitly end-of-day. Movement IDs must be
  unique; movements outside coverage are flagged and excluded. coverage `complete`
  is a supplied assertion, not independently established by this tool.
- settlements: id, unique signed components (id/amount), bank, pending and
  restricted. Component sum must equal these three destinations. Preserve gross
  collections and negative fees/refunds, without adding bank settlement as revenue.
- obligations: id, original, repayments and optional credits (unique id/amount).
  Positive repayments/credits reduce outstanding; overpayment stays an exception.
  Repayment/credit identity is scoped by entity/account/source across all obligations;
  repeated identities are invalid, including a repayment repeated as a credit.
  Omitted scope inherits the obligation and request; distinct accounts/providers
  may legitimately reuse provider IDs. For one payment split across obligations,
  include one payments record and give each repayment a distinct allocation id and
  its payment_id. Combined repayment and invoice allocations must not exceed that
  payment. Unknown payment links are invalid; unlinked repayments must not also
  appear in payments. Credits cannot use payment_id.
- invoices and payments: unique id/amount; allocations: unique id, invoice_id,
  payment_id and signed amount. Negative reversal requires `reverses`, referencing
  an original positive allocation to the same invoice/payment. Check outstanding,
  unapplied cash and excess allocations. Refund cash evidence remains separate.
  Allocations inherit the linked payment's scope and reject explicit conflicts,
  including account/source; the invoice may originate in a different source system.

Collections, settlements and allocation results do not establish provider state,
accounting recognition, payment permission or professional approval. Mixed-currency
amounts cannot be consolidated by this utility. Partition inputs by their actual
entity, currency and established basis before checking.
Nested movements, components, repayments and credits inherit omitted scope but
reject explicit conflicting entity, currency, basis and any known account/source.
An account's account field defaults to its id for its movements. Scopes without
account/source evidence cannot establish provider identity; do not invent them.

## Comparable calculations

Operation `comparable_calculations` supports variance, margin, contribution and
cash_scenario. For the first three, left/right facts require value, entity,
currency, unit, period_start, period_end, basis and source_refs. Both start and end
dates must match, as must the other dimensions. Missing value returns unavailable.
Variance returns left minus right and a ratio against the absolute right amount;
favorability is not inferred. Contribution is left minus right; supply comparable
revenue/variable-cost facts or per-unit price/cost facts, not incompatible units.
Margin is left divided by right. Zero denominator produces an explicit exception.

cash_scenario requires entity/currency/basis/source_refs, as_of, opening,
restricted, end_date and unique events (id/date/signed amount). Opening is the
dated end-of-day balance. Dated events after as_of through end_date roll forward
available cash after restricted funds. The resolution is end-of-day; same-day
events are grouped, and intraday payment ordering is not invented. Scenarios
remain conditional on supplied receipts, obligations and coverage.
Events also reject explicit scope that conflicts with the supplied scenario.

## Provenance and validation

The small import-mapping and merge-eligibility adaptations draw on MIT sources:
[nullbook CSV parser](https://github.com/jfornear/nullbook/blob/c561db5a78dc14ffbc4a008fc5f8b710a657604c/backend/imports/parsers/csv_parser.py)
and [Actual merge guards](https://github.com/actualbudget/actual/blob/1ad8477abdc432f318be27dc2fde25dde6ab0720/packages/loot-core/src/shared/merge.ts).
Changes remove application dependencies, enforce explicit dates/number conventions,
preserve signed movements, add business/account/currency scope, and return review
results without mutation. See [source notices](../THIRD_PARTY_NOTICES.md).

Finlynq's account-scoped identity, staged reconciliation and preview-before-write
patterns informed independent implementation; no AGPL code is included. Financial
facts and evidence remain separate from calculations. The SEC margin counterexamples
in the tests reject mixed units and unequal durations even when end dates match.

Run [fictional utility tests](../tests/test_money_tools.py) with an installed Python
and `-B`. They exercise arithmetic, scope, imports and preservation, not live tools
or independent agent competence. Runtime evidence must identify the actual tested
workspace and package fingerprint. Python availability is not Sheets readiness.
