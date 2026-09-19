import hashlib
from pathlib import Path
import tempfile
import unittest
from preflight import check


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "caption.txt").write_bytes(b"Original caption")
        self.record = dict(id="caption", path="caption.txt", sha256=hashlib.sha256(b"Original caption").hexdigest(),
                           status="documented", uses=["website"], reviewer="Human reviewer",
                           evidence="Internal record A", credit="No credit required per record A", expires="none")

    def run_check(self, **changes):
        return check(self.root, [dict(self.record, **changes)], "website", "2026-09-19")

    def test_complete_record(self):
        self.assertEqual(self.run_check()["record_gaps"], 0)

    def test_changed_asset_preserves_expected_boundary(self):
        (self.root / "caption.txt").write_bytes(b"Changed caption")
        self.assertIn("asset-changed-since-record", self.run_check()["assets"][0]["findings"])

    def test_unknown_and_wrong_use(self):
        findings = self.run_check(status="unknown", uses=["internal"])["assets"][0]["findings"]
        self.assertIn("usage-record-unresolved", findings)
        self.assertIn("requested-use-not-recorded", findings)

    def test_expiry_inclusive_and_reproducible(self):
        self.assertEqual(self.run_check(expires="2026-09-19")["record_gaps"], 0)
        self.assertIn("record-expired", self.run_check(expires="2026-09-18")["assets"][0]["findings"])
        with self.assertRaises(ValueError):
            self.run_check(expires="tomorrow")

    def test_missing_fields_are_actionable(self):
        findings = self.run_check(reviewer="", evidence="", credit="", expires="", sha256="")["assets"][0]["findings"]
        self.assertEqual(len(findings), 5)

    def test_missing_asset(self):
        self.assertIn("missing-file", self.run_check(path="absent.jpg")["assets"][0]["findings"])

    def test_bad_and_duplicate_records(self):
        for records in [[], [self.record, self.record], [{}], [dict(self.record, uses="website")]]:
            with self.assertRaises(ValueError):
                check(self.root, records, "website", "2026-09-19")

    def test_paths_cannot_escape(self):
        for path in ["../caption.txt", "/caption.txt", "C:/caption.txt", ".env", "x/./caption.txt", "*.jpg"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.run_check(path=path)


if __name__ == "__main__":
    unittest.main()
