import json
import re
from pathlib import Path

from soulmod_client.normalizer import MOD_ID_RE, NormalizerError

SKIP_KEYS = frozenset({"date"})


def load_lang(path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise NormalizerError("lang file must be a non-empty object")
    return data


def lang_ops(mod_id: str, mapping: dict) -> tuple:
    if not isinstance(mod_id, str) or not MOD_ID_RE.match(mod_id):
        raise NormalizerError(f"bad mod id: {mod_id!r}")
    ops = []
    skipped = []
    for key in sorted(mapping.keys()):
        if key in SKIP_KEYS:
            skipped.append(key)
            continue
        value = mapping[key]
        if not isinstance(key, str) or not key:
            raise NormalizerError("bad lang key")
        if not isinstance(value, str):
            raise NormalizerError(f"bad lang value for {key!r}")
        if not value.strip():
            skipped.append(key)
            continue
        ops.append({
            "id": f"{mod_id}.lang.{key}",
            "operationVersion": 1,
            "modId": mod_id,
            "target": {"type": "string", "name": key},
            "operation": "string.replace",
            "value": value,
            "reads": [f"string:{key}"],
            "writes": [f"string:{key}"],
        })
    return ops, skipped


def font_ops(mod_id: str, resources: list) -> list:
    if not isinstance(mod_id, str) or not MOD_ID_RE.match(mod_id):
        raise NormalizerError(f"bad mod id: {mod_id!r}")
    ops = []
    for r in resources:
        for field in ("name", "fontSize", "bold", "italic", "rangeFirst", "rangeLast", "atlas"):
            if field not in r:
                raise NormalizerError(f"font entry missing {field}")
        atlas = r["atlas"]
        ops.append({
            "id": f"{mod_id}.font.{r['name']}",
            "operationVersion": 1,
            "modId": mod_id,
            "target": {"type": "font", "name": r["name"]},
            "operation": "font.register",
            "selector": {"size": r["fontSize"], "bold": r["bold"], "italic": r["italic"],
                         "first": r["rangeFirst"], "last": r["rangeLast"]},
            "assetPath": atlas["relativePath"],
            "assetSha256": atlas["sha256"],
            "reads": [f"asset:{atlas['relativePath']}"],
            "writes": [f"font:{r['name']}"],
        })
    return ops


def sprite_ops(mod_id: str, sprites: list) -> list:
    if not isinstance(mod_id, str) or not MOD_ID_RE.match(mod_id):
        raise NormalizerError(f"bad mod id: {mod_id!r}")
    ops = []
    for s in sprites:
        frames = s.get("frames") or []
        if not s.get("name") or not frames:
            raise NormalizerError("sprite entry missing name or frames")
        first = frames[0]
        ops.append({
            "id": f"{mod_id}.sprite.{s['name']}",
            "operationVersion": 1,
            "modId": mod_id,
            "target": {"type": "sprite", "name": s["name"]},
            "operation": "sprite.replace",
            "selector": {"frames": len(frames)},
            "assetPath": first["asset"]["relativePath"],
            "assetSha256": first["asset"]["sha256"],
            "reads": [f"asset:{first['asset']['relativePath']}"],
            "writes": [f"sprite:{s['name']}"],
        })
    return ops


def code_reports(added: list) -> list:
    reports = []
    for c in added:
        if not c.get("name"):
            raise NormalizerError("code entry missing name")
        reports.append({"kind": "ManualReviewRequired", "reason": "RuntimeCodeReplaceUnsupported",
                        "name": c["name"],
                        "fingerprint": {k: c.get(k) for k in ("bytecodeSha256", "instructionCount")}})
    return reports


def audio_reports(entries: list) -> list:
    reports = []
    for a in entries:
        if not a.get("name"):
            raise NormalizerError("audio entry missing name")
        asset = a.get("asset") or {}
        reports.append({"kind": "ManualReviewRequired", "reason": "RuntimeAudioReplaceUnsupported",
                        "name": a["name"],
                        "format": a.get("format"),
                        "baseContentSha256": a.get("baseContentSha256"),
                        "contentSha256": a.get("contentSha256"),
                        "assetPath": asset.get("relativePath"),
                        "assetSha256": asset.get("sha256")})
    return reports
