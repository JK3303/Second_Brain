import copy
import unittest
from palette import compile_palette, contrast, css


class PaletteTests(unittest.TestCase):
    def setUp(self):
        self.spec = {"colors": {"ink": "#000000", "paper": "#ffffff", "text": "{ink}"},
                     "pairs": [{"name": "body", "foreground": "text", "background": "paper", "usage": "text"}]}

    def test_known_ratios_and_symmetry(self):
        self.assertEqual(contrast("#000000", "#ffffff"), 21)
        self.assertEqual(contrast("#123456", "#123456"), 1)
        self.assertAlmostEqual(contrast("#123456", "#eeeeee"), contrast("#eeeeee", "#123456"))

    def test_alias_export(self):
        report = compile_palette(self.spec)
        self.assertIn("--color-text: #000000;", css(report))
        self.assertIn(report["source_sha256"], css(report))

    def test_do_not_round_into_passing(self):
        self.spec["colors"]["ink"] = "#777777"
        report = compile_palette(self.spec)
        self.assertGreater(report["checks"][0]["ratio"], 4.47)
        self.assertFalse(report["checks"][0]["passes"])
        with self.assertRaises(ValueError):
            css(report)

    def test_large_text_threshold(self):
        self.spec["colors"]["ink"] = "#777777"
        self.spec["pairs"][0]["usage"] = "large-text"
        self.assertTrue(compile_palette(self.spec)["checks"][0]["passes"])

    def test_alias_cycle_and_missing(self):
        for value in ["{text}", "{absent}"]:
            self.spec["colors"]["ink"] = value
            with self.assertRaises(ValueError):
                compile_palette(self.spec)

    def test_injection_and_unsupported_color(self):
        for value in ["red", "#fff", "#ffffff00", "url(remote)", "#fff;}body{display:none}"]:
            self.spec["colors"]["ink"] = value
            with self.assertRaises(ValueError):
                compile_palette(self.spec)
        self.spec["colors"] = {"bad;name": "#000000"}
        with self.assertRaises(ValueError):
            compile_palette(self.spec)

    def test_bad_pairs(self):
        for pairs in [[], [{}], [self.spec["pairs"][0]] * 2]:
            with self.assertRaises(ValueError):
                compile_palette(dict(self.spec, pairs=pairs))

    def test_deterministic_and_changes_traced(self):
        first = compile_palette(self.spec)
        changed = copy.deepcopy(self.spec)
        changed["colors"]["ink"] = "#111111"
        self.assertEqual(first, compile_palette(self.spec))
        self.assertNotEqual(first["source_sha256"], compile_palette(changed)["source_sha256"])


if __name__ == "__main__":
    unittest.main()
