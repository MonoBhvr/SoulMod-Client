"""Manager stub: install/enable/disable/profile. In-memory only."""


class ManagerError(ValueError):
    pass


class Manager:
    def __init__(self):
        self._mods = {}

    def install(self, mod_id: str, ops) -> str:
        if not mod_id or not isinstance(ops, list) or not ops:
            raise ManagerError("bad install args")
        if mod_id in self._mods:
            raise ManagerError(f"duplicate mod: {mod_id!r}")
        self._mods[mod_id] = {"ops": ops, "enabled": True}
        return mod_id

    def enable(self, mod_id: str):
        self._mods[mod_id]["enabled"] = True

    def disable(self, mod_id: str):
        self._mods[mod_id]["enabled"] = False

    def remove(self, mod_id: str):
        del self._mods[mod_id]

    def profile(self) -> list:
        return sorted(m for m, v in self._mods.items() if v["enabled"])

    def active_ops(self) -> list:
        ops = []
        for m in self.profile():
            ops.extend(self._mods[m]["ops"])
        return ops

    def resolved(self):
        from soulmod_client.resolver import resolve
        return resolve({m: self._mods[m]["ops"] for m in self.profile()})
