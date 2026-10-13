import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from soulmod_client.normalizer import normalize_legacy_strings, NormalizerError
from soulmod_client.registry import resolve, UnknownGame
from soulmod_client.interceptor import InterceptRuntime, InterceptError
from soulmod_client.manager import Manager, ManagerError
from soulmod_client.resolver import ConflictError


class VerticalSlice(unittest.TestCase):
    def test_c1_normalize(self):
        ops = normalize_legacy_strings("test.mod", {"A": "가", "B": "나"})
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0]["operation"], "string.replace")
        self.assertEqual(ops[0]["operationVersion"], 1)

    def test_c2_intercept_no_touch(self):
        ops = normalize_legacy_strings("test.mod", {"HELLO": "안녕"})
        rt = InterceptRuntime()
        rt.install(ops)
        self.assertEqual(rt.deliver("HELLO", "HELLO"), "안녕")
        self.assertEqual(rt.deliver("OTHER", "OTHER"), "OTHER")
        rt.uninstall()
        self.assertEqual(rt.deliver("HELLO", "HELLO"), "HELLO")

    def test_c3_registry(self):
        self.assertEqual(resolve("undertale")["mode"], "single")
        self.assertEqual(resolve("deltarune.chapter1")["mode"], "chapter1")
        with self.assertRaises(UnknownGame):
            resolve("nope")

    def test_c4_fail_closed(self):
        with self.assertRaises(NormalizerError):
            normalize_legacy_strings("test.mod", {})
        with self.assertRaises(NormalizerError):
            normalize_legacy_strings("bad id!", {"A": "B"})
        with self.assertRaises(NormalizerError):
            normalize_legacy_strings("test.mod", {"../x": "B"})
        rt = InterceptRuntime()
        with self.assertRaises(InterceptError):
            rt.install([])
        mgr = Manager()
        mgr.install("a", normalize_legacy_strings("a", {"K": "V"}))
        with self.assertRaises(ManagerError):
            mgr.install("a", normalize_legacy_strings("a", {"K": "V"}))


class MultiMod(unittest.TestCase):
    def test_disjoint_merge(self):
        mgr = Manager()
        mgr.install("a", normalize_legacy_strings("a", {"K1": "V1"}))
        mgr.install("b", normalize_legacy_strings("b", {"K2": "V2"}))
        plan, report = mgr.resolved()
        self.assertEqual(len(plan), 2)
        self.assertEqual(report["duplicates"], [])
        rt = InterceptRuntime()
        rt.install(plan)
        self.assertEqual(rt.deliver("K1", "K1"), "V1")
        self.assertEqual(rt.deliver("K2", "K2"), "V2")

    def test_duplicate_dedup(self):
        mgr = Manager()
        mgr.install("a", normalize_legacy_strings("a", {"K": "V"}))
        mgr.install("b", normalize_legacy_strings("b", {"K": "V"}))
        plan, report = mgr.resolved()
        self.assertEqual(len(plan), 1)
        self.assertEqual(len(report["duplicates"]), 1)

    def test_direct_conflict_fails_closed(self):
        mgr = Manager()
        mgr.install("a", normalize_legacy_strings("a", {"K": "V1"}))
        mgr.install("b", normalize_legacy_strings("b", {"K": "V2"}))
        with self.assertRaises(ConflictError):
            mgr.resolved()

    def test_deterministic_order(self):
        def build():
            mgr = Manager()
            mgr.install("b", normalize_legacy_strings("b", {"K2": "V2"}))
            mgr.install("a", normalize_legacy_strings("a", {"K1": "V1"}))
            plan, _ = mgr.resolved()
            return [o["id"] for o in plan]
        self.assertEqual(build(), build())


if __name__ == "__main__":
    unittest.main()
