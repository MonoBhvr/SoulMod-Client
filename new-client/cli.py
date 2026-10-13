import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from soulmod_client.normalizer import normalize_legacy_strings, NormalizerError
from soulmod_client.registry import resolve, UnknownGame
from soulmod_client.interceptor import InterceptRuntime
from soulmod_client.manager import Manager


def cmd_normalize(strings_path, mod_id, out_path):
    strings = json.loads(Path(strings_path).read_text(encoding="utf-8"))
    ops = normalize_legacy_strings(mod_id, strings)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(ops, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"NORMALIZED {len(ops)} -> {out_path}")


def cmd_apply_demo(strings_path, mod_id, game_id, datawin_path, evidence_dir):
    ev = Path(evidence_dir)
    ev.mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(Path(datawin_path).read_bytes()).hexdigest()
    strings = json.loads(Path(strings_path).read_text(encoding="utf-8"))
    ops = normalize_legacy_strings(mod_id, strings)
    game = resolve(game_id)
    mgr = Manager()
    mgr.install(mod_id, ops)
    rt = InterceptRuntime()
    rt.install(mgr.active_ops())
    first_key = sorted(strings.keys())[0]
    got = rt.deliver(first_key, first_key)
    assert got == strings[first_key], "intercept must swap delivered value"
    assert rt.deliver("__missing__", "X") == "X"
    after = hashlib.sha256(Path(datawin_path).read_bytes()).hexdigest()
    assert before == after, "data.win must be untouched"
    (ev / "ops.json").write_text(json.dumps(ops, ensure_ascii=False, indent=2), encoding="utf-8")
    (ev / "receipt.json").write_text(json.dumps({
        "game": game, "profile": mgr.profile(),
        "delivered": first_key, "got": got,
        "datawinSha256": after, "untouched": before == after,
        "journal": rt.journal,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rt.uninstall()
    print(f"APPLY-DEMO OK game={game_id} ops={len(ops)} untouched={before == after}")


def cmd_multi_demo(strings_a, mod_a, strings_b, mod_b, game_id, datawin_path, evidence_dir):
    ev = Path(evidence_dir)
    ev.mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(Path(datawin_path).read_bytes()).hexdigest()
    map_a = json.loads(Path(strings_a).read_text(encoding="utf-8"))
    map_b = json.loads(Path(strings_b).read_text(encoding="utf-8"))
    game = resolve(game_id)
    mgr = Manager()
    mgr.install(mod_a, normalize_legacy_strings(mod_a, map_a))
    mgr.install(mod_b, normalize_legacy_strings(mod_b, map_b))
    plan, report = mgr.resolved()
    rt = InterceptRuntime()
    rt.install(plan)
    ka = sorted(map_a.keys())[0]
    kb = sorted(map_b.keys())[0]
    assert rt.deliver(ka, ka) == map_a[ka]
    assert rt.deliver(kb, kb) == map_b[kb]
    after = hashlib.sha256(Path(datawin_path).read_bytes()).hexdigest()
    assert before == after
    (ev / "multi-receipt.json").write_text(json.dumps({
        "game": game, "profile": mgr.profile(),
        "plan": len(plan), "report": report,
        "datawinSha256": after, "untouched": before == after,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    rt.uninstall()
    print(f"MULTI-DEMO OK game={game_id} plan={len(plan)} untouched={before == after}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "normalize":
        cmd_normalize(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "apply-demo":
        cmd_apply_demo(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif cmd == "multi-demo":
        cmd_multi_demo(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    else:
        raise SystemExit(f"unknown cmd: {cmd}")
