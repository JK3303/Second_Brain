import copy
from pathlib import Path
import tempfile
import unittest
from packet import build, digest, prepare, MAX_FILE


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "brief.md").write_bytes(b"Human critique: keep the reveal.\n")
        (self.root / "private.md").write_text("Not selected", encoding="utf-8")
        self.spec = {"recipient": "Design reviewer", "purpose": "Discuss alternatives", "files": ["brief.md"]}

    def test_only_selected_exact_text_leaves(self):
        plan, _ = prepare(self.root, self.spec)
        result = build(self.root, self.spec, digest(plan))
        self.assertEqual(result["sources"], [{"path": "brief.md", "text": "Human critique: keep the reveal.\n"}])
        self.assertNotIn(str(self.root), str(result))

    def test_changed_source_invalidates_review(self):
        plan, _ = prepare(self.root, self.spec)
        (self.root / "brief.md").write_text("Changed")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            build(self.root, self.spec, digest(plan))

    def test_recipient_purpose_and_selection_are_bound(self):
        plan, _ = prepare(self.root, self.spec)
        for field, value in [("recipient", "Public"), ("purpose", "Publish"), ("files", ["private.md"])]:
            spec = copy.deepcopy(self.spec)
            spec[field] = value
            with self.assertRaises(ValueError):
                build(self.root, spec, digest(plan))

    def test_no_missing_review(self):
        with self.assertRaises(ValueError):
            build(self.root, self.spec, None)

    def test_unsafe_paths_and_duplicates(self):
        for names in [["../secret.md"], ["C:/secret.md"], [".env"], [".git/config.md"],
                      ["./brief.md"], ["brief.md", "brief.md"], ["*.md"], ["brief.md/"]]:
            with self.subTest(names=names), self.assertRaises(ValueError):
                prepare(self.root, dict(self.spec, files=names))

    def test_link_rejected(self):
        try:
            (self.root / "linked.md").symlink_to(self.root / "private.md")
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        with self.assertRaises(ValueError):
            prepare(self.root, dict(self.spec, files=["linked.md"]))

    def test_binary_size_and_missing_file_fail(self):
        for raw in [b"\x00", b"\xff", b"x" * (MAX_FILE + 1)]:
            (self.root / "brief.md").write_bytes(raw)
            with self.assertRaises(ValueError):
                prepare(self.root, self.spec)
        with self.assertRaises(OSError):
            prepare(self.root, dict(self.spec, files=["absent.md"]))

    def test_bad_spec(self):
        for spec in [[], {}, dict(self.spec, files=[]), dict(self.spec, recipient=""), dict(self.spec, extra=True)]:
            with self.assertRaises(ValueError):
                prepare(self.root, spec)


if __name__ == "__main__":
    unittest.main()
