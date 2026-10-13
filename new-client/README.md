# new-client — SoulMod rewrite skeleton (reference: old tree, no old pipelines)

Common-mod normalize → script-delivery intercept → multi-game registry → manager stub.
Rules: never touch data.win, never full-load it, fail closed.

## Layout
- `src/soulmod_client/normalizer.py` — legacy `strings.json` → common v1 ops
- `src/soulmod_client/registry.py` — UT/DR game matrix
- `src/soulmod_client/interceptor.py` — delivery-hook runtime (no file IO)
- `src/soulmod_client/manager.py` — install/enable/disable/profile stub
- `cli.py` — `normalize` / `apply-demo` for real-surface proof
- `tests/test_vertical_slice.py` — C1-C4
