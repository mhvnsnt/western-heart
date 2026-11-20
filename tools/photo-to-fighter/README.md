# tools/photo-to-fighter — photo-to-3D pipeline contracts (prototype)

**Status:** research-stage prototype. Neither AdaHuman nor GAIA has public
code as of 2026-10-23. This directory is the **pipeline as code**: stage
I/O contracts, the likeness/consent/adult gates, and an orchestrator with
injectable backends — all CPU-testable on synthetic data. Real GPU services
swap in without changing the orchestration.

Design doc: `docs/research/PHOTO-TO-FIGHTER-2026-10-23.md`
Companion (face lane, wired now): `docs/research/FACE-SCAN-PHOTO-TO-3D-2026-10-23.md`

## Layout

| File | Purpose |
|------|---------|
| `stages.py` | Stage I/O contracts: `IntakeSpec` → `SplatAvatar` → `GameMesh` → `RiggedFighter` → `TexturedFighter` → `PhotoFighter` (+ optional `GaiaHeadPass`); per-stage `validate()` |
| `likeness_policy.py` | Gates as code: `check_consent()`, `check_adult()`, `check_no_famous_face()`, `log_likeness_record()` — failures raise, never warn |
| `pipeline.py` | `PhotoToFighterPipeline` orchestrator; backend interfaces (`AdaHumanBackend`, `MeshBackend`, `RigBackend`, `TextureBackend`, `GaiaHeadBackend`) + stub implementations |
| `tests/test_pipeline_contract.py` | 15 contract tests: gates, stage validation, happy-path pipeline, GAIA head pass |

## Run the tests

```bash
python3 tools/photo-to-fighter/tests/test_pipeline_contract.py
# or
python3 -m pytest tools/photo-to-fighter/tests/ -q
```

Requires: Python 3.10+, numpy. No torch, no GPU.

## The future GPU service contracts (spec)

When the models release, these services implement the stub interfaces:

- `POST /v1/avatars` `{photo, pose: "a-pose", refine: true}` → job → `{splat_ply_url, preview_views[], metrics}`
  (AdaHuman — NVIDIA 24GB+ GPU, cloud/workstation)
- `POST /v1/mesh` `{splat_ply_url, method: "sugar"|"2dgs"|"gof"}` → job → `{mesh_glb_url, watertight, vertex_count}`
- Rig: `tools/auto_rig/` (UniRig, MIT — already vendored, PR #273) + `validate.py` playable gate
- Texture: `tools/texture-pipe/` — WWE-style photo→UV projection + PBR bake
- `POST /v1/head` `{head_crop, identity_latent_id?}` → `{expression_library[], blendshape_params}` (GAIA — Phase 3)

## When the AdaHuman code drops — runbook

1. **Read the license first.** Expect NVIDIA SCL-NC (research/evaluation only). Nothing vendored until terms are evaluated; NC code never enters `game/`.
2. **Stand up the avatar service** on a cloud GPU box per the contract above.
3. **Head-to-head the §3 meshing options** (SuGaR / 2DGS / GOF) on 5 consented-adult crew photos; measure hands/face fidelity, watertight rate, time. Publish the comparison.
4. **Wire the real backends** into `PhotoToFighterPipeline` (subclass the interfaces in `pipeline.py`).
5. **Pilot:** one photo → one test-slot fighter → T-pose/idle renders viewed → proof-harness fight. Photo-fighter enters as a *user attire*, never a default.
6. **GAIA (when/if released):** latent-inversion spike → `GaiaHeadPass` for real → expression library (SHOW-set; show-animation lock governs playback).

## What this prototype does NOT do

- No model weights, no inference, no real avatars — stubs synthesize stage outputs.
- No game UI changes (menus come from teardown rebuilds per owner law, never hand-tooled).
- No `game/` changes at all. Research lane only.
- The likeness gates are enforced in code, but the *photo capture UI* (where consent is collected) belongs to the menus lane.
