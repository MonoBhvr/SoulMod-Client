class ConflictError(ValueError):
    pass


def resolve(mod_ops: dict) -> tuple:
    if not isinstance(mod_ops, dict) or not mod_ops:
        raise ConflictError("no mods to resolve")
    plan = []
    seen = {}
    duplicates = []
    conflicts = []
    for mod_id in sorted(mod_ops.keys()):
        ops = mod_ops[mod_id]
        if not isinstance(ops, list) or not ops:
            raise ConflictError(f"bad ops for {mod_id!r}")
        for op in sorted(ops, key=lambda o: (o["target"]["type"], o["target"]["name"])):
            key = (op["target"]["type"], op["target"]["name"], op["operation"])
            if key in seen:
                prev = seen[key]
                if prev["value"] == op["value"]:
                    duplicates.append({"key": list(key), "kept": prev["id"], "dropped": op["id"]})
                    continue
                conflicts.append({"key": list(key), "mods": sorted([prev["modId"], op["modId"]]),
                                  "values": [prev["value"], op["value"]]})
                continue
            seen[key] = op
            plan.append(op)
    if conflicts:
        raise ConflictError(f"direct conflict: {conflicts}")
    plan.sort(key=lambda o: (o["target"]["type"], o["target"]["name"]))
    return plan, {"duplicates": duplicates, "merged": len(plan)}
