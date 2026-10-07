"""Money 1.0.0: deterministic, read-only JSON financial checks (stdlib only).

Run with an installed Python: money_tools.py < request.json. See utility-practice.md.
No persistence, provider APIs, network, or accounting classification occurs here.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from typing import Any

VERSION = "1.0.0"


class InputError(ValueError):
    pass


def number(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise InputError("Amounts must be decimal strings or integers; missing is not zero.")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise InputError("Invalid decimal amount.") from exc
    if not result.is_finite():
        raise InputError("Nonfinite amount is invalid, not zero.")
    return result


def iso(value: Any) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise InputError("Date must be YYYY-MM-DD.")
    try:
        result = date.fromisoformat(value)
    except ValueError as exc:
        raise InputError("Invalid ISO date.") from exc
    if result.isoformat() != value:
        raise InputError("Date must be YYYY-MM-DD.")
    return result


def required(obj: dict, keys: tuple[str, ...]) -> None:
    if any(obj.get(key) is None or obj.get(key) == "" for key in keys):
        raise InputError("Missing required fields: " + ", ".join(keys))


def unique(rows: list[dict], label: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(key, str) or not key for key in ids) or len(ids) != len(set(ids)):
        raise InputError(label + " requires distinct nonempty string IDs.")


def total(rows: list[dict], field: str = "amount") -> Decimal:
    return sum((number(row.get(field)) for row in rows), Decimal(0))


def scoped(row: dict, parent: dict) -> dict:
    """Inherit omitted scope, but reject explicit contradictory dimensions."""
    result = {key: parent[key] for key in ("entity", "currency", "basis", "account", "source") if key in parent}
    for key in ("entity", "currency", "basis", "account", "source"):
        if key in row:
            if not isinstance(row[key], str) or not row[key]:
                raise InputError("Scope fields require nonempty strings: " + key + ".")
            if key in result and row[key] != result[key]:
                raise InputError("Record does not match supplied " + key + ".")
            result[key] = row[key]
    return result


def exception(code: str, **details: Any) -> dict:
    return {"code": code, **details}


def import_preview(p: dict) -> dict:
    required(p, ("entity", "account", "source", "currency", "date_format", "sign_convention", "mapping", "rows"))
    if not isinstance(p["rows"], list):
        raise InputError("rows must be an array.")
    formats = {"iso": "%Y-%m-%d", "month-first": "%m/%d/%Y", "day-first": "%d/%m/%Y"}
    if p["date_format"] not in formats:
        raise InputError("Explicit date_format must be iso, month-first, or day-first.")
    convention = p["sign_convention"]
    if convention not in {"signed", "charges-positive", "debit-credit"}:
        raise InputError("Unknown sign convention.")
    mapping = p["mapping"]
    required(mapping, ("date", "debit", "credit") if convention == "debit-credit" else ("date", "amount"))
    sep = p.get("decimal_separator", ".")
    thousands = p.get("thousands_separator", "")
    precision = p.get("currency_precision", 2)
    if sep not in {".", ","} or thousands not in {"", ",", ".", " "} or sep == thousands:
        raise InputError("Conflicting or unsupported number separators.")
    if type(precision) is not int or not 0 <= precision <= 8:
        raise InputError("currency_precision must be an integer from 0 to 8.")

    def amount(value: Any) -> Decimal:
        if not isinstance(value, str):
            result = number(value)
        else:
            text = value.strip()
            if text.startswith("(") and text.endswith(")"):
                text = "-" + text[1:-1]
            if thousands:
                unsigned = text.lstrip("+-")
                integer = unsigned.split(sep)[0]
                if thousands in integer and not re.fullmatch(r"\d{1,3}(?:" + re.escape(thousands) + r"\d{3})+", integer):
                    raise InputError("Invalid thousands grouping.")
                if thousands in unsigned.partition(sep)[2]:
                    raise InputError("Thousands separator occurs in fractional amount.")
                text = text.replace(thousands, "")
            if not re.fullmatch(r"[+-]?\d+(?:" + re.escape(sep) + r"\d+)?", text):
                raise InputError("Amount must use the declared decimal convention.")
            result = number(text.replace(sep, "."))
        if result != result.quantize(Decimal(1).scaleb(-precision)):
            raise InputError("Amount exceeds declared currency precision; no implicit rounding.")
        return result

    accepted, errors = [], []
    for index, row in enumerate(p.get("rows", []), 1):
        try:
            raw_date = row.get(mapping["date"])
            if p["date_format"] == "iso":
                parsed = iso(raw_date)
            else:
                parsed = datetime.strptime(raw_date, formats[p["date_format"]]).date()
            if convention == "debit-credit":
                debit_raw, credit_raw = row.get(mapping["debit"]), row.get(mapping["credit"])
                if debit_raw in (None, "") and credit_raw in (None, ""):
                    raise InputError("Both debit and credit are missing.")
                debit = Decimal(0) if debit_raw in (None, "") else amount(debit_raw)
                credit = Decimal(0) if credit_raw in (None, "") else amount(credit_raw)
                if debit < 0 or credit < 0 or (debit and credit):
                    raise InputError("Debit/credit columns require nonnegative amounts on one side only.")
                signed = credit - debit
            else:
                signed = amount(row.get(mapping["amount"]))
                if convention == "charges-positive":
                    signed = -signed
            accepted.append({"entity": p["entity"], "account": p["account"], "source": p["source"],
                             "currency": p["currency"], "date": parsed.isoformat(), "amount": signed,
                             "source_id": row.get(mapping.get("source_id", "")),
                             "description": row.get(mapping.get("description", ""), ""),
                             "source_refs": [{"source": p["source"], "row": index}],
                             "source_row": row, "classification": "unresolved"})
        except (ValueError, TypeError, AttributeError, KeyError, InvalidOperation) as exc:
            errors.append(exception("invalid_row", row=index, reason=str(exc), source_row=row))
    return {"rows": accepted, "exceptions": errors, "input_rows": len(p.get("rows", [])),
            "classification_inferred": False}


def identity_review(p: dict) -> dict:
    required(p, ("existing", "incoming"))
    pool = list(p.get("existing", []))
    incoming = p.get("incoming", [])
    for row in pool + incoming:
        required(row, ("entity", "account", "source", "currency", "date", "amount"))
        iso(row["date"])
        number(row["amount"])
    result = []
    tolerance = p.get("date_tolerance_days", 1)
    if type(tolerance) is not int or tolerance < 0:
        raise InputError("date_tolerance_days must be a nonnegative integer.")

    def scope(row):
        return tuple(row[key] for key in ("entity", "account", "source"))

    def facts(row):
        return (row["date"], number(row["amount"]), row["currency"], row.get("description", ""))

    for index, row in enumerate(incoming, 1):
        same_id = [old for old in pool if scope(old) == scope(row) and row.get("source_id")
                   and old.get("source_id") == row["source_id"]]
        if same_id:
            state = "exact_repeat" if all(facts(old) == facts(row) for old in same_id) else "correction_conflict"
            candidates = same_id
        else:
            candidates = []
            for old in pool:
                if (old["entity"], old["account"], old["currency"]) != (row["entity"], row["account"], row["currency"]):
                    continue
                # Distinct IDs from the same source can identify legitimate identical purchases.
                if old["source"] == row["source"] and old.get("source_id") and row.get("source_id"):
                    continue
                if number(old["amount"]) != number(row["amount"]):
                    continue
                if abs((iso(old["date"]) - iso(row["date"])).days) > tolerance:
                    continue
                left, right = str(old.get("description", "")).casefold(), str(row.get("description", "")).casefold()
                if left == right or SequenceMatcher(None, left, right).ratio() >= Decimal("0.8"):
                    candidates.append(old)
            state = "possible_duplicate" if candidates else "new"
        result.append({"incoming_row": index, "state": state, "candidates": candidates,
                       "record": row, "reason": "Scoped provider identity" if same_id else "Review similarity only"})
        pool.append(row)
    return {"reviews": result, "mutations": [], "exceptions": [], "automatic_merge": False}


def reconcile(p: dict) -> dict:
    required(p, ("entity", "currency", "basis", "source_refs"))
    checks, errors = [], []
    if not any(p.get(key) for key in ("accounts", "settlements", "obligations", "invoices", "payments")):
        raise InputError("Supply at least one reconciliation register.")
    for key in ("accounts", "settlements", "obligations"):
        unique(p.get(key, []), key)
    for key in ("accounts", "settlements", "obligations", "invoices", "payments", "allocations"):
        for row in p.get(key, []):
            scoped(row, p)
    unique(p.get("payments", []), "Payments")
    payment_records = {row["id"]: row for row in p.get("payments", [])}
    repayment_allocated = dict.fromkeys(payment_records, Decimal(0))
    obligation_effects = set()

    def check(kind, ident, expected, observed, **details):
        difference = observed - expected
        checks.append({"kind": kind, "id": ident, "expected": expected, "observed": observed,
                       "difference": difference, "status": "consistent" if difference == 0 else "unmatched", **details})
        if difference:
            errors.append(exception("unmatched", kind=kind, id=ident, difference=difference))

    for account in p.get("accounts", []):
        required(account, ("id", "opening_date", "closing_date", "opening", "closing", "movements"))
        opening_date, closing_date = iso(account["opening_date"]), iso(account["closing_date"])
        if closing_date < opening_date:
            raise InputError("Closing date precedes opening date.")
        unique(account["movements"], "Account movements")
        account_scope = scoped(account, p)
        account_scope.setdefault("account", account["id"])
        included = []
        for row in account["movements"]:
            when = iso(row.get("date"))
            scoped(row, account_scope)
            if not opening_date < when <= closing_date:
                errors.append(exception("outside_cutover_coverage", account=account["id"], movement=row["id"]))
            else:
                included.append(row)
        check("account", account["id"], number(account["opening"]) + total(included), number(account["closing"]),
              coverage=account.get("coverage", "unspecified"), opening="end-of-day")
        if account.get("coverage") != "complete":
            errors.append(exception("incomplete_coverage", account=account["id"]))

    for settlement in p.get("settlements", []):
        required(settlement, ("id", "components", "bank", "pending", "restricted"))
        unique(settlement["components"], "Settlement components")
        for component in settlement["components"]:
            scoped(component, scoped(settlement, p))
        accounted = sum((number(settlement[key]) for key in ("bank", "pending", "restricted")), Decimal(0))
        check("settlement", settlement["id"], total(settlement["components"]), accounted,
              components=settlement["components"])

    for obligation in p.get("obligations", []):
        unique(obligation.get("repayments", []), "Repayments")
        unique(obligation.get("credits", []), "Obligation credits")
        for kind in ("repayments", "credits"):
            for row in obligation.get(kind, []):
                scope = scoped(row, scoped(obligation, p))
                identity = tuple(scope.get(key, "") for key in ("entity", "account", "source")) + (row["id"],)
                if identity in obligation_effects:
                    raise InputError("Reused obligation effect ID; one payment needs distinct linked allocations.")
                obligation_effects.add(identity)
                if "payment_id" in row:
                    if kind != "repayments" or row["payment_id"] not in payment_records:
                        raise InputError("Repayment allocation requires a known payment_id; credits are not payments.")
                    payment = payment_records[row["payment_id"]]
                    scoped(payment, scope)
                    scoped(row, scoped(payment, p))
                    repayment_allocated[row["payment_id"]] += number(row.get("amount"))
                elif kind == "repayments" and row["id"] in payment_records:
                    payment_scope = scoped(payment_records[row["id"]], p)
                    distinct = any(key in scope and key in payment_scope and scope[key] != payment_scope[key]
                                   for key in ("account", "source"))
                    if not distinct:
                        raise InputError("Repayment also appears in payments; link with payment_id rather than recount it.")
        original, repaid = number(obligation.get("original")), total(obligation.get("repayments", []))
        credits = total(obligation.get("credits", []))
        if original < 0 or any(number(r["amount"]) < 0 for r in obligation.get("repayments", []) + obligation.get("credits", [])):
            raise InputError("Obligation amounts require nonnegative values.")
        remaining = original - repaid - credits
        checks.append({"kind": "obligation", "id": obligation.get("id"), "original": original,
                       "repaid": repaid, "credits": credits, "outstanding": remaining})
        if remaining < 0:
            errors.append(exception("overpayment", id=obligation.get("id"), amount=-remaining))

    invoices, payments, allocations = p.get("invoices", []), p.get("payments", []), p.get("allocations", [])
    unique(invoices, "Invoices")
    unique(payments, "Payments")
    unique(allocations, "Allocations")
    due = {row["id"]: number(row.get("amount")) for row in invoices}
    available = {row["id"]: number(row.get("amount")) for row in payments}
    if any(v < 0 for v in list(due.values()) + list(available.values())):
        raise InputError("Invoice and payment totals must be nonnegative; refunds use linked signed allocations.")
    applied_invoice = dict.fromkeys(due, Decimal(0))
    applied_payment = repayment_allocated.copy()
    reversed_totals = {}
    for row in allocations:
        invoice, payment = row.get("invoice_id"), row.get("payment_id")
        if invoice not in due or payment not in available:
            errors.append(exception("unknown_allocation_target", id=row["id"]))
            continue
        # Allocation scope describes the linked cash payment, not the invoice's
        # potentially different source system. Omitted fields inherit that scope.
        scoped(row, scoped(payment_records[payment], p))
        value = number(row.get("amount"))
        if value < 0 and not row.get("reverses"):
            errors.append(exception("refund_requires_original_allocation", id=row["id"]))
            continue
        if value < 0:
            original = next((a for a in allocations if a["id"] == row["reverses"]), None)
            if not original or original.get("invoice_id") != invoice or original.get("payment_id") != payment or number(original["amount"]) <= 0:
                errors.append(exception("invalid_refund_link", id=row["id"]))
                continue
            refunded = reversed_totals.get(original["id"], Decimal(0)) - value
            if refunded > number(original["amount"]):
                errors.append(exception("refund_exceeds_original_allocation", id=row["id"]))
                continue
            reversed_totals[original["id"]] = refunded
        applied_invoice[invoice] += value
        applied_payment[payment] += value
    for ident, amount in due.items():
        remaining = amount - applied_invoice[ident]
        checks.append({"kind": "invoice", "id": ident, "outstanding": remaining, "allocated": applied_invoice[ident]})
        if remaining < 0 or applied_invoice[ident] < 0:
            errors.append(exception("invalid_invoice_allocation", id=ident))
    for ident, amount in available.items():
        unapplied = amount - applied_payment[ident]
        checks.append({"kind": "payment", "id": ident, "unapplied": unapplied, "allocated": applied_payment[ident]})
        if unapplied < 0 or applied_payment[ident] < 0:
            errors.append(exception("invalid_payment_allocation", id=ident))
        elif unapplied:
            errors.append(exception("unapplied_payment", id=ident, amount=unapplied))
    return {"checks": checks, "exceptions": errors, "verification": "arithmetic-consistency-only",
            "source_refs": p["source_refs"], "basis": p["basis"]}


def comparable_calculations(p: dict) -> dict:
    kind = p.get("kind")
    if kind == "cash_scenario":
        required(p, ("entity", "currency", "basis", "source_refs", "as_of", "opening", "restricted", "end_date", "events"))
        start, end = iso(p["as_of"]), iso(p["end_date"])
        if end < start:
            raise InputError("Scenario end precedes starting balance.")
        balance = number(p["opening"]) - number(p["restricted"])
        if number(p["restricted"]) < 0:
            raise InputError("Restricted funds must be nonnegative.")
        minimum, events, errors = balance, [], []
        daily = {}
        unique(p["events"], "Scenario events")
        for row in sorted(p["events"], key=lambda item: (iso(item.get("date")), item["id"])):
            scoped(row, p)
            if not start < iso(row["date"]) <= end:
                errors.append(exception("outside_scenario_period", id=row["id"]))
                continue
            daily.setdefault(row["date"], []).append(row)
        for when, rows in daily.items():
            balance += total(rows)
            minimum = min(minimum, balance)
            events.append({"date": when, "components": rows, "closing_available": balance})
        return {"closing_available": balance, "minimum_available": minimum, "events": events,
                "exceptions": errors, "source_refs": p["source_refs"], "basis": p["basis"],
                "resolution": "end-of-day; intraday order not inferred"}
    if kind not in {"variance", "margin", "contribution"}:
        raise InputError("Unknown calculation kind.")
    left, right = p.get("left", {}), p.get("right", {})
    dimensions = ("entity", "currency", "unit", "period_start", "period_end", "basis")
    required(left, dimensions + ("source_refs",))
    required(right, dimensions + ("source_refs",))
    for fact in (left, right):
        if iso(fact["period_end"]) < iso(fact["period_start"]):
            raise InputError("Invalid fact period.")
    mismatch = [key for key in dimensions if left[key] != right[key]]
    evidence = {"left": left, "right": right}
    if mismatch:
        return {"status": "unavailable", "exceptions": [exception("incomparable_facts", fields=mismatch)], "inputs": evidence}
    if left.get("value") is None or right.get("value") is None:
        return {"status": "unavailable", "exceptions": [exception("missing_value")], "inputs": evidence}
    a, b = number(left["value"]), number(right["value"])
    if kind == "variance":
        return {"status": "calculated", "amount": a-b, "ratio": (a-b)/abs(b) if b else None,
                "exceptions": [] if b else [exception("zero_denominator")], "inputs": evidence,
                "favorable_direction": "not-inferred"}
    if kind == "contribution":
        return {"status": "calculated", "amount": a-b, "exceptions": [], "inputs": evidence}
    if b == 0:
        return {"status": "unavailable", "ratio": None, "exceptions": [exception("zero_denominator")], "inputs": evidence}
    return {"status": "calculated", "ratio": a/b, "exceptions": [], "inputs": evidence}


OPERATIONS = {"import_preview": import_preview, "identity_review": identity_review,
              "reconcile": reconcile, "comparable_calculations": comparable_calculations}


def run(request: dict) -> dict:
    try:
        operation = request.get("operation")
        if operation not in OPERATIONS or not isinstance(request.get("payload"), dict):
            raise InputError("Supply a supported operation and an object payload.")
        result = OPERATIONS[operation](request["payload"])
        return {"version": VERSION, "operation": operation, "status": "exceptions" if result.get("exceptions") else "checked", "result": result}
    except (ValueError, TypeError, KeyError, AttributeError, ArithmeticError) as exc:
        return {"version": VERSION, "status": "invalid", "exceptions": [exception("invalid_input", reason=str(exc))]}


def serialize(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    raise TypeError("Unsupported JSON output value.")


def main() -> int:
    try:
        def invalid_constant(value):
            raise InputError("Nonfinite JSON constant: " + value)
        request = json.load(sys.stdin, parse_float=Decimal, parse_constant=invalid_constant)
        result = run(request)
    except (ValueError, TypeError) as exc:
        result = {"version": VERSION, "status": "invalid", "exceptions": [exception("invalid_json", reason=str(exc))]}
    print(json.dumps(result, default=serialize, allow_nan=False))
    return 2 if result["status"] == "invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
