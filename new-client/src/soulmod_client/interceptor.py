"""Delivery-hook intercept runtime.

Model: the game delivers a named script/string value at runtime;
installed common-mod ops swap it. No data.win read, no full load,
no disk write. Rollback = uninstall clears bindings.
"""


class InterceptError(ValueError):
    pass


_ALLOWED_OPS = {"string.replace", "string.add"}


class InterceptRuntime:
    def __init__(self):
        self._by_target = {}
        self.journal = []

    def install(self, ops) -> int:
        if not isinstance(ops, list) or not ops:
            raise InterceptError("ops must be a non-empty list")
        for op in ops:
            name = op.get("target", {}).get("name")
            kind = op.get("operation")
            if not name or kind not in _ALLOWED_OPS:
                raise InterceptError(f"unsupported op: {op.get('id')!r}")
            self._by_target[name] = op
            self.journal.append(f"PREPARE {op['id']}")
        for op in ops:
            self.journal.append(f"COMMIT {op['id']}")
        return len(ops)

    def deliver(self, name: str, current: str) -> str:
        op = self._by_target.get(name)
        if op is None:
            return current
        expected = (op.get("precondition") or {}).get("expectedValue")
        if expected is not None and expected != current:
            return current
        return op["value"]

    def uninstall(self):
        self._by_target.clear()
        self.journal.append("ROLLBACK all")
