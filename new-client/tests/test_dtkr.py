import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soulmod_client.dtkr import lang_ops, font_ops, sprite_ops, code_reports, audio_reports
from soulmod_client.normalizer import NormalizerError
from soulmod_client.registry import resolve, UnknownGame


class DtkrBuilders(unittest.TestCase):
    def test_lang_ops_skip_date_empty_whitespace(self):
        ops, skipped = lang_ops("dtkr.ch1", {"date": "123", "B": "나", "A": "가",
                                                "E": "", "W": "   "})
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0]["target"]["name"], "A")
        self.assertEqual(ops[0]["operation"], "string.replace")
        self.assertNotIn("precondition", ops[0])
        self.assertEqual(sorted(skipped), ["E", "W", "date"])

    def test_lang_fail_closed(self):
        with self.assertRaises(NormalizerError):
            lang_ops("bad id!", {"A": "B"})
        with self.assertRaises(NormalizerError):
            lang_ops("m", {"A": 1})

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

    def test_audio_reports_review_only(self):
        reps = audio_reports([{"name": "snd_x", "format": ".wav",
                               "baseContentSha256": "b", "contentSha256": "c",
                               "asset": {"relativePath": "a.bin", "sha256": "c"}}])
        self.assertEqual(reps[0]["reason"], "RuntimeAudioReplaceUnsupported")
        self.assertEqual(audio_reports([]), [])
        with self.assertRaises(NormalizerError):
            audio_reports([{}])

    def test_registry_chapter5_and_launcher(self):
        self.assertEqual(resolve("deltarune.chapter5")["mode"], "chapter5")
        self.assertEqual(resolve("deltarune.launcher")["mode"], "launcher")
        with self.assertRaises(UnknownGame):
            resolve("nope")


if __name__ == "__main__":
    unittest.main()
