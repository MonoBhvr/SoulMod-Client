"""Multi-game registry: UT + Deltarune chapters/modes.

Game id -> {targetFile, mode}. Unknown ids are typed rejects (KeyError
with message). No fingerprints here; fingerprints pin per-build later.
"""


class UnknownGame(KeyError):
    pass


GAMES = {
    "undertale": {"targetFile": "data.win", "mode": "single"},
    "deltarune.chapter1": {"targetFile": "data.win", "mode": "chapter1"},
    "deltarune.chapter2": {"targetFile": "data.win", "mode": "chapter2"},
    "deltarune.chapter3": {"targetFile": "data.win", "mode": "chapter3"},
    "deltarune.chapter4": {"targetFile": "data.win", "mode": "chapter4"},
    "deltarune.launcher": {"targetFile": "data.win", "mode": "launcher"},
}


def resolve(game_id: str) -> dict:
    try:
        entry = GAMES[game_id]
    except KeyError:
        raise UnknownGame(f"unknown game: {game_id!r}")
    return {"id": game_id, **entry}
