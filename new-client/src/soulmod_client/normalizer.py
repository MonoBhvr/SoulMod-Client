"""Legacy strings.json -> common-mod v1 string.replace ops.

Input: flat {"source": "replaced"} map + mod id.
Output: list of v1-shaped op dicts (id, operationVersion, modId,
target, operation, precondition, value, reads, writes).
Fail-closed on malformed input. No file IO here.
"""
import re

MOD_ID_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


class NormalizerError(ValueError):
    pass


def normalize_legacy_strings(mod_id: str, strings: dict) -> list:
    if not isinstance(mod_id, str) or not MOD_ID_RE.match(mod_id):
        raise NormalizerError(f"bad mod id: {mod_id!r}")
    if not isinstance(strings, dict) or not strings:
        raise NormalizerError("strings map must be a non-empty object")
    ops = []
    seen = set()
    for i, (src, dst) in enumerate(strings.items()):
        if not isinstance(src, str) or not src:
            raise NormalizerError(f"entry {i}: bad source key")
        if not isinstance(dst, str) or not dst:
            raise NormalizerError(f"entry {i}: bad value for {src!r}")
        if "/" in src or "\\" in src or ".." in src:
            raise NormalizerError(f"entry {i}: path-like key rejected: {src!r}")
        if src in seen:
            raise NormalizerError(f"duplicate key: {src!r}")
        seen.add(src)
        ops.append({
            "id": f"{mod_id}.str.{i}",
            "operationVersion": 1,
            "modId": mod_id,
            "target": {"type": "string", "name": src},
            "operation": "string.replace",
            "precondition": {"expectedValue": src},
            "value": dst,
            "reads": [f"string:{src}"],
            "writes": [f"string:{src}"],
        })
    ops.sort(key=lambda o: o["target"]["name"])
    return ops
