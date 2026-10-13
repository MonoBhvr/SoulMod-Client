import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soulmod_client.dtkr import lang_ops, font_ops, sprite_ops, code_reports
from soulmod_client.normalizer import NormalizerError


class DtkrBuilders(unittest.TestCase):
    def test_lang_ops_skip_date(self):
        ops = lang_ops("dtkr.ch1", {"date": "123", "B": "나", "A": "가"})
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0]["target"]["name"], "A")
        self.assertEqual(ops[0]["operation"], "string.replace")
        self.assertNotIn("precondition", ops[0])

    def test_lang_fail_closed(self):
        with self.assertRaises(NormalizerError):
            lang_ops("bad id!", {"A": "B"})
        with self.assertRaises(NormalizerError):
            lang_ops("m", {"date": "1"})
        with self.assertRaises(NormalizerError):
            lang_ops("m", {"A": ""})

    def test_font_ops_shape(self):
        ops = font_ops("m", [{"name": "fnt_ja_main", "fontSize": 26, "bold": False,
                              "italic": False, "rangeFirst": 32, "rangeLast": 55203,
                              "atlas": {"relativePath": "a.png", "sha256": "s"}}])
        self.assertEqual(ops[0]["operation"], "font.register")
        self.assertEqual(ops[0]["selector"]["last"], 55203)

    def test_sprite_ops_shape(self):
        ops = sprite_ops("m", [{"name": "spr_x", "frames": [
            {"frameIndex": 0, "asset": {"relativePath": "f0.png", "sha256": "a"}},
            {"frameIndex": 1, "asset": {"relativePath": "f1.png", "sha256": "b"}}]}])
        self.assertEqual(ops[0]["selector"]["frames"], 2)
        self.assertEqual(ops[0]["assetPath"], "f0.png")

    def test_code_reports_review_only(self):
        reps = code_reports([{"name": "scr_x", "bytecodeSha256": "h", "instructionCount": 5}])
        self.assertEqual(reps[0]["kind"], "ManualReviewRequired")
        with self.assertRaises(NormalizerError):
            code_reports([{}])


if __name__ == "__main__":
    unittest.main()
