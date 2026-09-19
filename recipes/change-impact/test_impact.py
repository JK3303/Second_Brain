import copy
from pathlib import Path
import tempfile
import unittest
from impact import snapshot, compare, validate_graph


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = {"nodes": [
            dict(id="source", path="source.md", kind="source", depends_on=[], rationale="Observed input"),
            dict(id="decision", path="decision.md", kind="decision", depends_on=["source"], rationale="Depends on source"),
            dict(id="artifact", path="artifact.md", kind="artifact", depends_on=["decision"], rationale="Implements decision"),
            dict(id="unrelated", path="other.md", kind="artifact", depends_on=[], rationale="Separate work")
        ]}
        for node in self.spec["nodes"]:
            (self.root / node["path"]).write_text(node["id"])
        self.before = snapshot(self.root, self.spec)

    def test_unchanged(self):
        self.assertEqual(compare(self.before, snapshot(self.root, self.spec))["changed"], [])

    def test_transitive_routes_and_unrelated_exclusion(self):
        (self.root / "source.md").write_text("New evidence")
        report = compare(self.before, snapshot(self.root, self.spec))
        self.assertEqual(report["changed"], ["source"])
        self.assertEqual([row["id"] for row in report["review_candidates"]], ["artifact", "decision"])
        self.assertEqual(report["review_candidates"][0]["routes"][0]["chain"], ["source", "decision", "artifact"])

    def test_missing_source_remains_visible(self):
        (self.root / "source.md").unlink()
        current = snapshot(self.root, self.spec)
        self.assertEqual(compare(current, current)["missing_current_files"], ["source"])
        self.assertEqual(len(compare(self.before, current)["review_candidates"]), 2)

    def test_changed_dependency_map_is_a_change(self):
        self.spec["nodes"][1]["depends_on"] = []
        report = compare(self.before, snapshot(self.root, self.spec))
        self.assertIn("decision", report["changed"])
        self.assertEqual(report["review_candidates"][0]["id"], "artifact")

    def test_removed_node_traces_previous_dependencies(self):
        self.spec["nodes"].pop(0)
        self.spec["nodes"][0]["depends_on"] = []
        report = compare(self.before, snapshot(self.root, self.spec))
        self.assertIn("source", report["changed"])
        self.assertIn("artifact", [row["id"] for row in report["review_candidates"]])

    def test_cycles_and_unknown_dependencies(self):
        for deps in [["artifact"], ["absent"]]:
            self.spec["nodes"][0]["depends_on"] = deps
            with self.assertRaises(ValueError):
                validate_graph(self.spec)

    def test_tampered_or_malformed_baseline_rejected(self):
        bad = copy.deepcopy(self.before)
        bad["nodes"][0]["sha256"] = "0" * 64
        for baseline in [bad, {}, dict(self.before, nodes=[{}])]:
            with self.assertRaises(ValueError):
                compare(baseline, self.before)

    def test_paths_rejected(self):
        for name in ["../source.md", "C:/source.md", ".env", "./source.md", "x/*.md"]:
            self.spec["nodes"][0]["path"] = name
            with self.assertRaises(ValueError):
                snapshot(self.root, self.spec)

    def test_new_node_is_reported(self):
        self.spec["nodes"].append(dict(id="new", path="new.md", kind="artifact", depends_on=["decision"], rationale="New derivative"))
        report = compare(self.before, snapshot(self.root, self.spec))
        self.assertEqual(report["changed"], ["new"])
        self.assertEqual(report["missing_current_files"], ["new"])


if __name__ == "__main__":
    unittest.main()
