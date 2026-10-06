from pathlib import Path
import tempfile
import unittest
from context import retrieve


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "memory").mkdir()

    def put(self, name, text):
        (self.root / "memory" / name).write_text(text, encoding="utf-8")

    def test_conditions_and_provenance_retained(self):
        self.put("accepted-lessons.md", "# Lessons\n\n## Reveal\nRule: protect negative space\nDoes not apply when: a plain wordmark is required\nScope: project only\n")
        result = retrieve(self.root, "negative space")
        row = result["accepted"][0]
        self.assertIn("Does not apply when", row["text"])
        self.assertIn("Scope: project only", row["text"])
        self.assertEqual(row["start_line"], 3)
        self.assertEqual(row["source"], "memory/accepted-lessons.md")
        self.assertEqual(row["matched_terms"], ["negative", "space"])

    def test_rejected_and_unrelated_questions_survive(self):
        self.put("rejected-lessons.md", "## Tech\nAvoid: circuit motifs\nInstead: warmth\n")
        self.put("open-questions.md", "# Questions\nWho owns the decision?")
        result = retrieve(self.root, "circuit")
        self.assertIn("Instead: warmth", result["rejected"][0]["text"])
        self.assertIn("Who owns", result["unresolved"][0]["text"])

    def test_missing_is_not_no_matches(self):
        self.put("accepted-lessons.md", "## Reveal\nNegative space")
        result = retrieve(self.root, "photography")
        self.assertEqual(result["accepted"], [])
        self.assertEqual([r["state"] for r in result["sources"]], ["present", "missing", "missing"])

    def test_limit_reports_omissions_and_stable_ties(self):
        self.put("accepted-lessons.md", "## A\nWarm\n## B\nWarm\n")
        result = retrieve(self.root, "warm", 1)
        self.assertEqual(result["accepted"][0]["title"], "A")
        self.assertEqual(result["sources"][0]["omitted_matches"], 1)

    def test_unicode_casefold(self):
        self.put("accepted-lessons.md", "## Café\nÉmotion et couleur")
        self.assertEqual(retrieve(self.root, "ÉMOTION")["accepted"][0]["matched_terms"], ["émotion"])

    def test_source_change_changes_hash(self):
        self.put("accepted-lessons.md", "## A\nWarm")
        before = retrieve(self.root, "warm")["sources"][0]["sha256"]
        self.put("accepted-lessons.md", "## A\nWarm but restrained")
        self.assertNotEqual(before, retrieve(self.root, "warm")["sources"][0]["sha256"])

    def test_limits_and_bad_content(self):
        for brief, limit in [("", 3), ("x", 0), ("x", 11), ("x" * 12001, 3)]:
            with self.assertRaises(ValueError):
                retrieve(self.root, brief, limit)
        self.put("accepted-lessons.md", "x" * 131073)
        with self.assertRaises(ValueError):
            retrieve(self.root, "x")


if __name__ == "__main__":
    unittest.main()
