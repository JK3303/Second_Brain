import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from resume import build_packet, markdown, MAX_BYTES


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "handoff").mkdir()
        (self.root / "manifest.md").write_text(
            "Project: Example\nState: held\nExternal-action rule: no launch without approval\n"
            "Current entry point: handoff/current-state.md\nNext review: owner approval\n", encoding="utf-8")
        (self.root / "handoff/current-state.md").write_text(
            "# State\n\n## Status\nReady to launch\n\n## Open issues\nApproval pending\n", encoding="utf-8")

    def test_conflicting_claims_preserved_with_lines(self):
        result = build_packet(self.root)
        self.assertEqual(result["manifest_fields"]["State"]["value"], "held")
        self.assertEqual(result["entry_sections"][0]["text"], "Ready to launch")
        self.assertEqual(result["entry_sections"][0]["line"], 3)
        self.assertEqual(result["authority_effect"], "none")
        self.assertIn("Reconcile", markdown(result))

    def test_byte_change_detected_even_when_same_length(self):
        old = build_packet(self.root)
        self.assertEqual(build_packet(self.root, old)["comparison"]["status"], "unchanged")
        path = self.root / "handoff/current-state.md"
        path.write_text(path.read_text().replace("Ready", "Never"))
        self.assertEqual(build_packet(self.root, old)["comparison"]["changed_paths"], ["handoff/current-state.md"])

    def test_deleted_source_is_visible(self):
        old = build_packet(self.root)
        (self.root / "handoff/current-state.md").unlink()
        result = build_packet(self.root, old)
        self.assertIn("Missing source: handoff/current-state.md", result["attention"])
        self.assertEqual(result["comparison"]["status"], "changed")

    def test_external_path_rejected(self):
        for path in ("../private.md", "/private.md", "C:/private.md"):
            with self.subTest(path=path):
                (self.root / "manifest.md").write_text(f"Current entry point: {path}\n")
                with self.assertRaises(ValueError):
                    build_packet(self.root)

    def test_oversized_and_invalid_utf8_rejected(self):
        path = self.root / "handoff/current-state.md"
        for raw in (b"x" * (MAX_BYTES + 1), b"\xff"):
            path.write_bytes(raw)
            with self.assertRaises((ValueError, UnicodeError)):
                build_packet(self.root)

    def test_duplicate_manifest_key_rejected(self):
        with (self.root / "manifest.md").open("a") as handle:
            handle.write("State: approved\n")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_packet(self.root)

    def test_previous_packet_cannot_silently_change_project(self):
        old = build_packet(self.root)
        old["project"] = "Unrelated"
        with self.assertRaisesRegex(ValueError, "different project"):
            build_packet(self.root, old)

    def test_corrupt_baseline_rejected(self):
        old = build_packet(self.root)
        altered = copy.deepcopy(old)
        altered["sources"][0]["sha256"] = "incorrect"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            build_packet(self.root, altered)

    def test_invalid_source_types_rejected(self):
        old = build_packet(self.root)
        for field, value in (("status", []), ("sha256", {})):
            altered = copy.deepcopy(old)
            altered["sources"][0][field] = value
            with self.assertRaises(ValueError):
                build_packet(self.root, altered)

    def test_cli_round_trip_without_source_mutation(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        command = [sys.executable, str(Path(__file__).with_name("resume.py")), str(self.root), "--format", "json"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["project"], "Example")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_cli_failure_is_not_a_partial_report(self):
        (self.root / "manifest.md").unlink()
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("resume.py")), str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
