import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate import audit, parse_receipt, MAX_BYTES

BASE = """Decision ID: D-1
Project: Demo
Status: review-ready
Source: Supplied sketches
Decision owner: Example owner
Evidence: Sketch A and sketch B
Alternatives considered: A and B
Uncertainty: Audience response unknown
Authority or approval: None
Reversible: yes
Next action: Human review
"""


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, text, name="receipt.md"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_canonical_format_and_multiline_evidence(self):
        text = "# Receipt\n\n```text\n" + BASE.replace("Evidence: Sketch A and sketch B", "Evidence: Sketch A\n  Sketch B") + "```\n"
        result = audit([self.write(text)])
        self.assertTrue(result["valid"])
        self.assertIn("Sketch B", result["receipts"][0]["fields"]["Evidence"]["value"])
        self.assertEqual(result["authority_effect"], "none")

    def test_duplicate_field_and_unknown_field_are_not_silent(self):
        for extra in ("Status: approved\n", "Evidnce: typo\n"):
            self.assertFalse(audit([self.write(BASE + extra)])["valid"])

    def test_approval_requires_recorded_authority(self):
        for status in ("approved", "executing", "delivered", "published", "complete"):
            self.assertFalse(audit([self.write(BASE.replace("review-ready", status))])["valid"])
        self.assertTrue(audit([self.write(BASE.replace("review-ready", "approved").replace("approval: None", "approval: Owner selected A in review R-1"))])["valid"])

    def test_hold_needs_named_missing_item_reason_and_supplier(self):
        held = BASE.replace("review-ready", "held")
        self.assertFalse(audit([self.write(held)])["valid"])
        self.assertTrue(audit([self.write(held + "Missing item: Review\nWhy it matters: Direction unresolved\nNeeded from: Owner\n")])["valid"])

    def test_duplicate_ids_reported_on_both_receipts(self):
        result = audit([self.write(BASE, "a.md"), self.write(BASE, "b.md")])
        self.assertTrue(all(any("Duplicate Decision ID" in e for e in r["errors"]) for r in result["receipts"]))

    def test_supersession_cycle_and_missing_target(self):
        first = BASE.replace("review-ready", "superseded") + "Reconsider when: New evidence\nSuperseded by: D-2\n"
        second = first.replace("D-1", "TEMP").replace("D-2", "D-1").replace("TEMP", "D-2")
        a, b = self.write(first, "a.md"), self.write(second, "b.md")
        result = audit([a, b])
        self.assertTrue(all(any("cycle" in e for e in r["errors"]) for r in result["receipts"]))
        self.assertFalse(audit([a])["valid"])

    def test_replacement_must_belong_to_same_project(self):
        a = self.write(BASE.replace("review-ready", "superseded") + "Reconsider when: Evidence\nSuperseded by: D-2\n")
        b = self.write(BASE.replace("D-1", "D-2").replace("Demo", "Other"), "other.md")
        self.assertFalse(audit([a, b])["valid"])

    def test_valid_supersession_chain(self):
        a = self.write(BASE.replace("review-ready", "superseded") + "Reconsider when: Evidence\nSuperseded by: D-2\n")
        b = self.write(BASE.replace("D-1", "D-2"), "b.md")
        self.assertTrue(audit([a, b])["valid"])

    def test_placeholder_and_unknown_state(self):
        for change in (BASE.replace("review-ready", "ready-ish"), BASE.replace("Evidence: Sketch A and sketch B", "Evidence: TBD")):
            self.assertFalse(audit([self.write(change)])["valid"])

    def test_multiple_receipts_and_unclosed_fence(self):
        for text in ("```\n" + BASE, "```\n" + BASE + "```\n```\n" + BASE + "```\n"):
            with self.assertRaises(ValueError):
                parse_receipt(text)

    def test_oversized_and_duplicate_inputs(self):
        with self.assertRaises(ValueError):
            audit([])
        with self.assertRaises(ValueError):
            audit([self.write("x" * (MAX_BYTES + 1))])
        path = self.write(BASE)
        with self.assertRaises(ValueError):
            audit([path, path])

    def test_cli_and_no_source_changes(self):
        path = self.write(BASE)
        before = path.read_bytes()
        command = [sys.executable, str(Path(__file__).with_name("validate.py")), str(path), "--format", "json"]
        process = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue(json.loads(process.stdout)["valid"])
        self.assertEqual(path.read_bytes(), before)
        path.write_text(BASE.replace("Evidence: Sketch A and sketch B", "Evidence: TBD"))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        path.write_bytes(b"\xff")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        path.unlink()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
