import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("team_preflight", Path(__file__).parents[1] / "scripts/preflight.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateInspection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        for name in ("candidate.txt", "test.txt", "unrelated.txt"):
            (self.root / name).write_text("original\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True).stdout

    def test_dirty_candidate_and_unrelated_are_bounded(self):
        (self.root / "candidate.txt").write_text("new\n")
        (self.root / "unrelated.txt").write_text("private unrelated\n")
        before = (self.root / ".git/index").read_bytes()
        report = module.inspect(self.root, ["candidate.txt"], ["test.txt"])
        self.assertEqual(report["status"], "eligible")
        self.assertEqual(report["changed_count"], 2)
        self.assertNotIn("unrelated.txt", report["input_hashes"])
        self.assertFalse(report["validation_passed"])
        self.assertEqual(before, (self.root / ".git/index").read_bytes())

    def test_changed_test_requires_candidate_inclusion(self):
        (self.root / "test.txt").write_text("changed test\n")
        self.assertEqual(module.inspect(self.root, [], ["test.txt"])["blocked_inputs"], ["test.txt"])
        self.assertEqual(module.inspect(self.root, ["test.txt"], ["test.txt"])["status"], "eligible")

    def test_dependency_changes_fingerprint(self):
        before = module.inspect(self.root, ["test.txt"])["fingerprint"]
        (self.root / "test.txt").write_text("changed\n")
        self.assertNotEqual(before, module.inspect(self.root, ["test.txt"])["fingerprint"])

    def test_missing_file_blocks(self):
        with self.assertRaises(ValueError):
            module.inspect(self.root, ["missing.txt"])

    def test_escape_blocks(self):
        with self.assertRaises(ValueError):
            module.inspect(self.root, ["../outside.txt"])

    def test_absolute_path_blocks(self):
        with self.assertRaises(ValueError):
            module.inspect(self.root, [str(self.root / "test.txt")])

    def test_nested_root_blocks(self):
        nested = self.root / "nested"
        nested.mkdir()
        with self.assertRaises(ValueError):
            module.inspect(nested)

    def test_rename_counts_both_paths(self):
        self.git("mv", "candidate.txt", "renamed.txt")
        self.assertEqual(module.changed_paths(self.root), {"candidate.txt", "renamed.txt"})


if __name__ == "__main__":
    unittest.main()
