# tools/script-adapter — SCRIPT integration contract (prototype)

**Status:** research-stage prototype. SCRIPT (arXiv:2605.22894) has no public
code as of 2026-10-23. This directory is the **integration contract as code**:
the exact I/O shapes, the canon-safe prompt builder, the SMPL→WH retarget
interface, and the inference-service REST client — all CPU-testable on
synthetic data. When the weights drop, only the service URL changes.

Design doc: `docs/research/SCRIPT-INTEGRATION-2026-10-23.md`

## Layout

| File | Purpose |
|------|---------|
| `script_contract.py` | `ScriptState` (R^358) / `ScriptAction` (R^69) / `TextConditioning` (CLIP) / `ScriptRequest` / `ScriptTrajectory` + validators; `make_synthetic_trajectory()` for tests |
| `prompt_builder.py` | `build_script_prompt()` — move description → canonical prompt + job spec; `canon_filter()` — rejects minors / sexual content / real-person names; `STYLE_HINTS` per moveset source |
| `smpl_to_wh.py` | SMPL 69-dim → WH skeleton: `axis_angle_to_quat()`, `load_bone_map()` (same JSON convention as `tools/mocap/`), `trajectory_to_keyframes()` (resample to 60fps), `keyframes_to_wh_anim_dict()` (wh-anim/1 envelope, defaults to `"set": "SHOW"`) |
| `client.py` | `ScriptClient` — implements the REST contract; `StubScriptServer` — same contract, synthetic trajectories, for offline tests |
| `tests/test_script_contract.py` | 20 contract tests, all synthetic data |

## Run the tests

```bash
python3 tools/script-adapter/tests/test_script_contract.py
# or
python3 -m pytest tools/script-adapter/tests/ -q
```

Requires: Python 3.10+, numpy. No torch, no GPU.

## The inference-service REST contract (spec)

The future GPU service implements exactly what `client.py` speaks:

- `POST /v1/generate` `{prompt, style_hints, seed, duration_s, fps, model, constraints, archetype}` → `202 {job_id, status}`
- `GET /v1/jobs/{id}` → `{status, artifacts, metrics}`
- `GET /v1/jobs/{id}/trajectory` → `.npz` with `states` (H×358), `actions` (H×69), `fps`, `prompt`, `seed`, `model`, `metrics`

## When the SCRIPT code drops — runbook

1. **Read the license first.** Nothing is vendored until the release terms are evaluated.
2. **Confirm the 69-dim joint ordering** against their env; flip `LAYOUT_CONFIRMED = True` in `smpl_to_wh.py` (warns loudly until then).
3. **Map the state-stream layout** (358 dims: which indices are root height / per-joint 6D rotations / velocities) — needed to bake keyframes from states instead of actions (higher fidelity at contacts).
4. **Stand up the service** on a cloud GPU box implementing the REST contract above; point `ScriptClient` at it.
5. **Run the 10 canonical prompts** (jab, cross, roundhouse, throw, stance, sweep, uppercut, elbow, knee, taunt) through `generate_trajectory` → `trajectory_to_keyframes` → `keyframes_to_wh_anim_dict`.
6. **Frame-data anchoring** (spec in the design doc §4.4): contact events → startup/active/recovery; damage from archetype tables.
7. **Gate + bank:** `wh-anim/1` clips tagged `"set": "SHOW"` by default → `tools/mocap/gate_check.py` → `game/assets/anim/` → played verification via `tools/proof-harness/fight.mjs`.

## What this prototype does NOT do

- No model weights, no inference, no real motion — the stub returns seeded synthetic trajectories.
- No game UI changes (menus come from teardown rebuilds per owner law, never hand-tooled).
- No `game/` changes at all. Research lane only.
