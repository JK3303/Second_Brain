"""Fictional, observable regressions; run directly using an installed Python."""
import importlib.util
import json
import subprocess
import sys
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "money_tools.py"
spec = importlib.util.spec_from_file_location("money_tools", SCRIPT)
money = importlib.util.module_from_spec(spec)
spec.loader.exec_module(money)


def fact(value="100", **changes):
    return {"value": value, "entity": "Fictional Co", "currency": "USD", "unit": "currency",
            "period_start": "2026-10-01", "period_end": "2026-10-31", "basis": "cash-operating",
            "source_refs": ["fictional:ledger"], **changes}


def record(source_id="T1", **changes):
    return {"entity": "Fictional Co", "account": "Bank", "source": "statement", "source_id": source_id,
            "currency": "USD", "date": "2026-10-10", "amount": "25.00", "description": "Supplies", **changes}


class MoneyTests(unittest.TestCase):
    def preview(self, **changes):
        return money.import_preview({"entity": "Fictional Co", "account": "Bank", "source": "statement",
            "currency": "USD", "date_format": "iso", "sign_convention": "signed",
            "mapping": {"date": "Date", "amount": "Amount", "source_id": "ID"},
            "rows": [{"Date": "2026-10-01", "Amount": "500.00", "ID": "CAP1"}], **changes})

    def test_funding_is_signed_and_unclassified(self):
        result = self.preview()
        self.assertEqual(result["rows"][0]["amount"], Decimal(500))
        self.assertEqual(result["rows"][0]["classification"], "unresolved")
        self.assertEqual(result["rows"][0]["source_row"]["ID"], "CAP1")

    def test_ambiguous_date_requires_convention(self):
        row = [{"Date": "03/04/2026", "Amount": "5"}]
        self.assertEqual(len(self.preview(rows=row)["exceptions"]), 1)
        self.assertEqual(self.preview(rows=row, date_format="day-first")["rows"][0]["date"], "2026-04-03")
        self.assertEqual(self.preview(rows=row, date_format="month-first")["rows"][0]["date"], "2026-03-04")

    def test_invalid_amounts_and_precision(self):
        for value in ["", "NaN", "Infinity", "1.001", "$10", "1,00.00"]:
            with self.subTest(value=value):
                self.assertTrue(self.preview(rows=[{"Date": "2026-10-01", "Amount": value}], thousands_separator=",")["exceptions"])
        self.assertEqual(self.preview(rows=[{"Date": "2026-10-01", "Amount": "(1,200.50)"}], thousands_separator=",")["rows"][0]["amount"], Decimal("-1200.50"))

    def test_debit_credit(self):
        result = self.preview(sign_convention="debit-credit", mapping={"date": "Date", "debit": "D", "credit": "C"},
                              rows=[{"Date": "2026-10-01", "D": "20", "C": ""}, {"Date": "2026-10-02", "D": "2", "C": "2"}])
        self.assertEqual(result["rows"][0]["amount"], Decimal(-20))
        self.assertEqual(len(result["exceptions"]), 1)

    def test_repeat_correction_and_account_scope(self):
        result = money.identity_review({"existing": [record()], "incoming": [record(), record(amount="26"), record(account="Other")]})
        self.assertEqual([r["state"] for r in result["reviews"]], ["exact_repeat", "correction_conflict", "new"])
        self.assertEqual(result["mutations"], [])

    def test_identical_legitimate_purchases_preserved(self):
        result = money.identity_review({"existing": [record()], "incoming": [record("T2")]})
        self.assertEqual(result["reviews"][0]["state"], "new")
        candidate = money.identity_review({"existing": [record()], "incoming": [record(None)]})
        self.assertEqual(candidate["reviews"][0]["state"], "possible_duplicate")

    def test_cross_source_similarity_does_not_merge(self):
        result = money.identity_review({"existing": [record()], "incoming": [record(source="receipt")]})
        self.assertEqual(result["reviews"][0]["state"], "possible_duplicate")
        self.assertFalse(result["automatic_merge"])

    def reconcile(self, **changes):
        return money.reconcile({"entity": "Fictional Co", "currency": "USD", "basis": "cash", "source_refs": ["fictional:statement"], **changes})

    def test_end_to_end_bank_and_reimbursement(self):
        movements = [{"id": "CAP", "date": "2026-10-01", "amount": "500"},
                     {"id": "SET", "date": "2026-10-10", "amount": "291"},
                     {"id": "OPEX", "date": "2026-10-20", "amount": "-100"},
                     {"id": "EQ", "date": "2026-10-31", "amount": "-200"}]
        result = self.reconcile(accounts=[{"id": "Bank", "opening_date": "2026-09-30", "closing_date": "2026-10-31",
            "opening": "1000", "closing": "1491", "coverage": "complete", "movements": movements}],
            settlements=[{"id": "S1", "components": [{"id": "COL", "amount": "300"}, {"id": "FEE", "amount": "-9"}],
                          "bank": "291", "pending": "0", "restricted": "0"}],
            obligations=[{"id": "R1", "original": "900", "repayments": [{"id": "P1", "amount": "200"}, {"id": "P2", "amount": "150"}]}],
            invoices=[{"id": "I1", "amount": "400"}], payments=[{"id": "C1", "amount": "300"}],
            allocations=[{"id": "A1", "invoice_id": "I1", "payment_id": "C1", "amount": "300"}])
        self.assertEqual(result["exceptions"], [])
        self.assertEqual(result["checks"][0]["expected"], Decimal(1491))
        self.assertEqual(next(c for c in result["checks"] if c["kind"] == "obligation")["outstanding"], Decimal(550))
        self.assertEqual(next(c for c in result["checks"] if c["kind"] == "invoice")["outstanding"], Decimal(100))
        operating = money.comparable_calculations({"kind": "contribution", "left": fact("300"), "right": fact("109")})
        self.assertEqual(operating["amount"], Decimal(191))

    def test_opening_history_not_added_again(self):
        result = self.reconcile(accounts=[{"id": "Bank", "opening_date": "2026-10-01", "closing_date": "2026-10-31",
            "opening": "1000", "closing": "1000", "coverage": "complete", "movements": [{"id": "OLD", "date": "2026-10-01", "amount": "1000"}]}])
        self.assertEqual(result["checks"][0]["expected"], Decimal(1000))
        self.assertEqual(result["exceptions"][0]["code"], "outside_cutover_coverage")

    def test_refund_and_pending_settlement(self):
        result = self.reconcile(settlements=[{"id": "S2", "components": [{"id": "COL", "amount": "100"},
            {"id": "REF", "amount": "-20"}, {"id": "FEE", "amount": "-3"}], "bank": "0", "pending": "77", "restricted": "0"}])
        self.assertEqual(result["checks"][0]["status"], "consistent")

    def test_many_to_many_allocations_and_unapplied(self):
        result = self.reconcile(invoices=[{"id": "I1", "amount": "100"}, {"id": "I2", "amount": "100"}],
            payments=[{"id": "P1", "amount": "150"}, {"id": "P2", "amount": "70"}],
            allocations=[{"id": "A1", "invoice_id": "I1", "payment_id": "P1", "amount": "100"},
                         {"id": "A2", "invoice_id": "I2", "payment_id": "P1", "amount": "50"},
                         {"id": "A3", "invoice_id": "I2", "payment_id": "P2", "amount": "50"}])
        self.assertEqual([c["outstanding"] for c in result["checks"] if c["kind"] == "invoice"], [Decimal(0), Decimal(0)])
        self.assertEqual(result["exceptions"][0]["amount"], Decimal(20))

    def test_linked_refund_and_excess_reversal(self):
        allocations = [{"id": "A", "invoice_id": "I", "payment_id": "P", "amount": "100"},
                       {"id": "R", "invoice_id": "I", "payment_id": "P", "amount": "-20", "reverses": "A"}]
        inputs = {"invoices": [{"id": "I", "amount": "100"}], "payments": [{"id": "P", "amount": "100"}], "allocations": allocations}
        self.assertEqual(self.reconcile(**inputs)["checks"][0]["outstanding"], Decimal(20))
        inputs["allocations"].append({"id": "R2", "invoice_id": "I", "payment_id": "P", "amount": "-90", "reverses": "A"})
        self.assertIn("refund_exceeds_original_allocation", [e["code"] for e in self.reconcile(**inputs)["exceptions"]])

    def test_invoice_allocation_inherits_payment_scope(self):
        payload = {"invoices": [{"id": "I", "amount": "100", "source": "invoicing"}],
            "payments": [{"id": "P", "amount": "100", "account": "Bank A", "source": "statement"}],
            "allocations": [{"id": "A", "invoice_id": "I", "payment_id": "P", "amount": "100"}]}
        saved = deepcopy(payload)
        self.assertEqual(self.reconcile(**payload)["exceptions"], [])
        self.assertEqual(payload, saved)
        for dimension, matching, conflicting in [("account", "Bank A", "Bank B"),
                                                   ("source", "statement", "another-provider")]:
            with self.subTest(dimension=dimension):
                candidate = deepcopy(payload)
                candidate["allocations"][0][dimension] = matching
                self.assertEqual(self.reconcile(**candidate)["exceptions"], [])
                candidate["allocations"][0][dimension] = conflicting
                with self.assertRaises(money.InputError):
                    self.reconcile(**candidate)
                candidate = deepcopy(payload)
                candidate["allocations"].append({"id": "R", "invoice_id": "I", "payment_id": "P",
                    "amount": "-10", "reverses": "A", dimension: conflicting})
                with self.assertRaises(money.InputError):
                    self.reconcile(**candidate)

    def test_duplicate_movements_rejected(self):
        request = {"operation": "reconcile", "payload": {"entity": "Fictional", "currency": "USD", "basis": "cash", "source_refs": ["fictional"],
            "obligations": [{"id": "R", "original": "900", "repayments": [{"id": "P", "amount": "200"}, {"id": "P", "amount": "200"}]}]}}
        self.assertEqual(money.run(request)["status"], "invalid")

    def test_period_currency_basis_and_entity_mismatch(self):
        for changes in [{"period_start": "2026-07-01"}, {"currency": "EUR"}, {"basis": "accrual"}, {"entity": "Another"}, {"unit": "shares"}]:
            with self.subTest(changes=changes):
                result = money.comparable_calculations({"kind": "margin", "left": fact("10", **changes), "right": fact()})
                self.assertEqual(result["status"], "unavailable")

    def test_nested_reconciliation_scope_rejected(self):
        parents = [
            ("accounts", "movements", {"id": "Bank", "opening_date": "2026-10-01", "closing_date": "2026-10-02",
                "opening": "0", "closing": "100", "coverage": "complete"}),
            ("settlements", "components", {"id": "S", "account": "Bank", "source": "processor",
                "bank": "100", "pending": "0", "restricted": "0"}),
            ("obligations", "repayments", {"id": "O", "account": "Bank", "source": "bank", "original": "100"}),
            ("obligations", "credits", {"id": "O", "account": "Bank", "source": "bank", "original": "100"}),
        ]
        for register, children, parent in parents:
            dimensions = {"entity": "Another Co", "currency": "EUR", "basis": "accrual", "account": "Other Bank"}
            if "source" in parent:
                dimensions["source"] = "other-provider"
            for dimension, value in dimensions.items():
                with self.subTest(register=register, children=children, dimension=dimension):
                    child = {"id": "E", "date": "2026-10-02", "amount": "100", dimension: value}
                    payload = {"entity": "Fictional Co", "currency": "USD", "basis": "cash", "source_refs": ["fictional"],
                               register: [{**parent, children: [child]}]}
                    saved = deepcopy(payload)
                    self.assertEqual(money.run({"operation": "reconcile", "payload": payload})["status"], "invalid")
                    self.assertEqual(payload, saved)

    def test_forecast_event_scope_rejected(self):
        payload = {"kind": "cash_scenario", "entity": "Fictional Co", "currency": "USD", "basis": "cash",
            "account": "Bank", "source_refs": ["fictional"], "as_of": "2026-10-01", "opening": "100",
            "restricted": "0", "end_date": "2026-10-02"}
        for dimension, value in {"entity": "Another Co", "currency": "EUR", "basis": "accrual", "account": "Other"}.items():
            with self.subTest(dimension=dimension):
                request = {"operation": "comparable_calculations", "payload": {**payload,
                    "events": [{"id": "E", "date": "2026-10-02", "amount": "100", dimension: value}]}}
                self.assertEqual(money.run(request)["status"], "invalid")

    def test_repayment_reuse_across_obligations_and_credits_rejected(self):
        for kind in ("repayments", "credits"):
            with self.subTest(kind=kind), self.assertRaises(money.InputError):
                self.reconcile(obligations=[
                    {"id": "O1", "original": "100", "repayments": [{"id": "P", "amount": "100"}]},
                    {"id": "O2", "original": "100", kind: [{"id": "P", "amount": "100"}]}])

    def test_repayment_identity_preserves_account_and_source_scope(self):
        for dimension in ("account", "source"):
            with self.subTest(dimension=dimension):
                result = self.reconcile(obligations=[
                    {"id": "O1", dimension: "One", "original": "100", "repayments": [{"id": "P", "amount": "100"}]},
                    {"id": "O2", dimension: "Two", "original": "100", "repayments": [{"id": "P", "amount": "100"}]}])
                self.assertEqual(result["exceptions"], [])
                self.assertEqual([c["outstanding"] for c in result["checks"]], [Decimal(0), Decimal(0)])

    def test_split_repayment_is_bounded_by_one_payment(self):
        payload = {"obligations": [
            {"id": "O1", "original": "100", "repayments": [{"id": "A1", "payment_id": "P", "amount": "60"}]},
            {"id": "O2", "original": "100", "repayments": [{"id": "A2", "payment_id": "P", "amount": "40"}]}],
            "payments": [{"id": "P", "amount": "100"}]}
        saved = deepcopy(payload)
        result = self.reconcile(**payload)
        self.assertEqual(result["exceptions"], [])
        self.assertEqual([c["outstanding"] for c in result["checks"] if c["kind"] == "obligation"], [Decimal(40), Decimal(60)])
        self.assertEqual(next(c for c in result["checks"] if c["kind"] == "payment")["unapplied"], Decimal(0))
        self.assertEqual(payload, saved)
        payload["obligations"][1]["repayments"][0]["amount"] = "50"
        self.assertIn("invalid_payment_allocation", [e["code"] for e in self.reconcile(**payload)["exceptions"]])
        payload["obligations"][1]["repayments"][0]["payment_id"] = "UNKNOWN"
        with self.assertRaises(money.InputError):
            self.reconcile(**payload)
        payload = saved
        payload["payments"][0]["account"] = "Other Bank"
        payload["obligations"][0]["account"] = "Bank"
        with self.assertRaises(money.InputError):
            self.reconcile(**payload)

    def test_repayment_and_invoice_cannot_reuse_payment_capacity(self):
        result = self.reconcile(payments=[{"id": "P", "amount": "100"}],
            obligations=[{"id": "O", "original": "100", "repayments": [{"id": "R", "payment_id": "P", "amount": "100"}]}],
            invoices=[{"id": "I", "amount": "100"}],
            allocations=[{"id": "A", "invoice_id": "I", "payment_id": "P", "amount": "100"}])
        self.assertIn("invalid_payment_allocation", [e["code"] for e in result["exceptions"]])
        with self.assertRaises(money.InputError):
            self.reconcile(payments=[{"id": "P", "amount": "100"}],
                obligations=[{"id": "O", "original": "100", "repayments": [{"id": "P", "amount": "100"}]}])

    def test_variance_zero_and_missing(self):
        result = money.comparable_calculations({"kind": "variance", "left": fact("191"), "right": fact("250")})
        self.assertEqual(result["amount"], Decimal(-59))
        self.assertEqual(result["ratio"], Decimal("-0.236"))
        self.assertIsNone(money.comparable_calculations({"kind": "margin", "left": fact("10"), "right": fact("0")})["ratio"])
        self.assertEqual(money.comparable_calculations({"kind": "variance", "left": fact(None), "right": fact()})["status"], "unavailable")

    def test_decimal_arithmetic(self):
        result = money.comparable_calculations({"kind": "contribution", "left": fact("0.3"), "right": fact("0.1")})
        self.assertEqual(result["amount"], Decimal("0.2"))

    def test_dated_scenario_restricted_funds_and_refresh(self):
        inputs = {"kind": "cash_scenario", "entity": "Fictional", "currency": "USD", "basis": "cash", "source_refs": ["fictional"],
            "as_of": "2026-10-31", "opening": "1491", "restricted": "200", "end_date": "2026-12-31",
            "events": [{"id": "PAY", "date": "2026-11-01", "amount": "-1400"}, {"id": "REC", "date": "2026-11-02", "amount": "100"},
                       {"id": "DEC", "date": "2026-12-15", "amount": "-50"}]}
        saved = deepcopy(inputs)
        result = money.comparable_calculations(inputs)
        self.assertEqual(result["minimum_available"], Decimal(-109))
        self.assertEqual(inputs, saved)
        inputs.update(as_of="2026-11-30", opening="1591", restricted="0")
        self.assertEqual(money.comparable_calculations(inputs)["closing_available"], Decimal(1541))

    def test_same_day_does_not_invent_intraday_order(self):
        result = money.comparable_calculations({"kind": "cash_scenario", "entity": "Fictional", "currency": "USD", "basis": "cash", "source_refs": ["fictional"],
            "as_of": "2026-10-31", "opening": "100", "restricted": "0", "end_date": "2026-11-01",
            "events": [{"id": "A", "date": "2026-11-01", "amount": "-200"}, {"id": "B", "date": "2026-11-01", "amount": "200"}]})
        self.assertEqual(result["minimum_available"], Decimal(100))

    def test_json_cli_no_persistence(self):
        request = {"operation": "comparable_calculations", "payload": {"kind": "margin", "left": fact("10"), "right": fact()}}
        completed = subprocess.run([sys.executable, "-B", str(SCRIPT)], input=json.dumps(request), text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["result"]["ratio"], "0.1")
        bad = subprocess.run([sys.executable, "-B", str(SCRIPT)], input="not JSON", text=True, capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(json.loads(bad.stdout)["status"], "invalid")
        nonfinite = subprocess.run([sys.executable, "-B", str(SCRIPT)], input='{"amount": NaN}', text=True, capture_output=True)
        self.assertEqual(nonfinite.returncode, 2)
        self.assertEqual(json.loads(nonfinite.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
