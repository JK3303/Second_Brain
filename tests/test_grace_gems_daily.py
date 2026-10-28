import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location("daily", Path(__file__).resolve().parents[1] / "tools/grace_gems_daily.py")
daily = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daily)


class DailyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "work.md").write_text("Fictional brief uploaded and read back.", encoding="utf-8")
        self.packet = {"version": 1, "date": "2026-10-28", "timezone": "America/Denver",
            "coverage": [{"kind": kind, "status": "checked" if kind == "repository" else "unavailable",
                          "en": "Fictional test source only.", "zh": "仅为虚构测试来源。"}
                         for kind in ["session", "repository", "email", "drive"]],
            "sources": [{"id": "s1", "kind": "repo_file", "ref": "work.md",
                         "retrieved_at": "2026-10-28T20:00:00+00:00",
                         "sha256": daily.digest((self.root / "work.md").read_bytes())}],
            "facts": [{"id": "f1", "category": "progress", "evidence": "verified",
                       "audience": "grace-gems-team", "event_date": "2026-10-28",
                       "source_ids": ["s1"], "en": "Fictional brief uploaded and read back.",
                       "zh": "虚构制作单已上传并回读。"}]}

    def valid(self, packet=None):
        return daily.validate(packet or self.packet, "2026-10-28", "America/Denver", self.root)

    def test_bilingual_output_preserves_coverage_and_unsent_state(self):
        text = daily.render(self.valid())
        self.assertIn("Fictional brief uploaded", text)
        self.assertIn("虚构制作单", text)
        self.assertIn("email [unavailable]", text)
        self.assertIn("NOT SENT", text)
        self.assertNotIn("work.md", text)  # Private source refs stay out of email.

    def test_changed_source_stops_before_replacing_current_outputs(self):
        out = self.root / "out"
        daily.write_outputs(self.valid(), out)
        before = (out / "current-team-email.md").read_bytes()
        (self.root / "work.md").write_text("Changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.valid()
        self.assertEqual((out / "current-team-email.md").read_bytes(), before)

    def test_paths_cannot_escape_repository(self):
        for ref in ["../work.md", "/work.md", "C:/private/work.md", "folder\\work.md"]:
            p = copy.deepcopy(self.packet)
            p["sources"][0]["ref"] = ref
            with self.assertRaises((ValueError, OSError)):
                self.valid(p)

    def test_old_and_future_progress_rejected_but_old_blocker_labeled(self):
        for day in ["2026-10-27", "2026-10-29"]:
            p = copy.deepcopy(self.packet)
            p["facts"][0]["event_date"] = day
            with self.assertRaises(ValueError):
                self.valid(p)
        p["facts"][0].update(event_date="2026-10-27", category="blocker", carry_forward=True)
        self.assertIn("carried from 2026-10-27", daily.render(self.valid(p)))

    def test_dates_timezones_and_retrieval_dates_are_explicit(self):
        p = copy.deepcopy(self.packet)
        p["timezone"] = "Asia/Shanghai"
        with self.assertRaises(ValueError):
            self.valid(p)
        p = copy.deepcopy(self.packet)
        p["sources"][0]["retrieved_at"] = "2026-10-28T01:00:00+00:00"  # Still Oct 27 in Denver.
        with self.assertRaises(ValueError):
            self.valid(p)
        p["sources"][0]["retrieved_at"] = "2026-10-28T20:00:00"
        with self.assertRaises(ValueError):
            self.valid(p)

    def test_audience_and_provenance_required(self):
        for field, value in [("audience", "personal"), ("source_ids", []), ("source_ids", ["missing"])]:
            p = copy.deepcopy(self.packet)
            p["facts"][0][field] = value
            with self.assertRaises(ValueError):
                self.valid(p)

    def test_reported_progress_and_proposed_decision_keep_labels(self):
        p = copy.deepcopy(self.packet)
        p["facts"][0]["evidence"] = "reported"
        self.assertIn("reported / 据报", daily.render(self.valid(p)))
        p["facts"][0]["evidence"] = "proposed"
        with self.assertRaises(ValueError):
            self.valid(p)
        p["facts"][0]["category"] = "decision"
        self.assertIn("proposed / 建议", daily.render(self.valid(p)))

    def test_duplicate_mentions_collapse(self):
        p = copy.deepcopy(self.packet)
        p["facts"].append({**p["facts"][0], "id": "f2"})
        self.assertEqual(len(self.valid(p)["facts"]), 1)

    def test_empty_evidence_does_not_claim_no_work(self):
        p = copy.deepcopy(self.packet)
        p["facts"] = []
        text = daily.render(self.valid(p))
        self.assertIn("does not mean no work occurred", text)
        self.assertNotIn("Progress / 进展", text)

    def test_stable_outputs_idempotency_and_recoverable_revision(self):
        out = self.root / "out"
        daily.write_outputs(self.valid(), out)
        original = (out / "current-team-email.md").read_bytes()
        daily.write_outputs(self.valid(), out)
        self.assertFalse((out / ".history").exists())
        p = copy.deepcopy(self.packet)
        p["facts"][0]["en"] = "Corrected fictional brief verified."
        daily.write_outputs(self.valid(p), out)
        history = out / ".history" / daily.digest(original) / "current-team-email.md"
        self.assertEqual(history.read_bytes(), original)
        self.assertEqual(json.loads((out / "current-evidence.json").read_text(encoding="utf-8"))["facts"][0]["en"], p["facts"][0]["en"])

    def test_external_links_need_https_and_no_credentials(self):
        for url in ["http://example.com", "https://user:password@example.com", "https://example.com?token=private", "file:///private/order"]:
            p = copy.deepcopy(self.packet)
            p["facts"][0]["share_url"] = url
            with self.assertRaises(ValueError):
                self.valid(p)

    def test_missing_coverage_cannot_appear_complete(self):
        p = copy.deepcopy(self.packet)
        p["coverage"].pop()
        with self.assertRaises(ValueError):
            self.valid(p)

    def test_cli_rejects_private_outputs_inside_public_checkout(self):
        packet = self.root / "packet.json"
        packet.write_text(json.dumps(self.packet), encoding="utf-8")
        output = self.root / "out"
        result = subprocess.run([sys.executable, str(Path(daily.__file__)),
            "--date", "2026-10-28", "--timezone", "America/Denver",
            "--evidence", str(packet), "--repo-root", str(self.root),
            "--output", str(output)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"outside this public repository", result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
