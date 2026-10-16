# PULL-REST — Tekken 7 Batch 1 Report (2026-10-16)

Coordinator: pull-rest worker. Owner order 2026-10-16 ~02:31 EDT: pull the rest
of the fighters into Western Heart as model assets.

## Source
15 FBX zips downloaded 2026-10-14 via rigmodels (see
`game-reverse-engineering/tekken7/models/RIGMODELS-BATCH-2026-10-14.md`).
Staging: `~/workspace/pull-rest/staging/tekken7-batch1/`.

## Verification (TEARDOWN-COMPLETION LAW)
Every FBX imported in Blender 4.0.2 headless, bbox/humanoid check, GLB export,
front render. Pipeline: `~/workspace/pull-rest/verify_render_batch.py`
(adapted from the proven `docs/tpose-refs/_tools/tpose_render_cycles.py`;
RigModels T7 FBX rips face -X, import scale x100 cm→m).

| Fighter | FBX verts | Verdict | Landed? |
|---|---|---|---|
| Negan | 23,151 | PASS | already on main as `n3g4tiv0.glb` (exact dup) |
| Lili | 29,645 | PASS | already on main as `lili.glb` (exact dup) |
| Ganryu (5276) | 3,354 | PASS | **NEW → `thor_alt1.glb` (this PR)** |
| Ganryu (5168 anim) | 3,370 | PASS | already on main as `thor.glb` (exact dup) |
| Xiaoyu (35355) | 23,998 | PASS | already on main as `saku-ra.glb` (exact dup) |
| Zafina (butterfly) | 20,399 | PASS* | already on main as `zafina.glb` (exact dup) |
| Josie (diva) | 17,350 | PASS | already on main as `waterfall.glb` (exact dup) |
| Julia | 17,919 | PASS | already on main as `nightwolf.glb` (exact dup) |
| Nina | 4,746 | PASS | already on main as `awa-pop.glb` (exact dup) |
| Lei | 11,255 | PASS | already on main as `rave.glb` (exact dup) |
| Bryan | 4,688 | PASS | already on main as `skull.glb` (exact dup) |
| Yoshimitsu | 3,620 | PASS* | already on main as `phantom.glb` (exact dup) |
| Baek | 3,962 | PASS | already on main as `baek.glb` (exact dup) |
| Lee | 4,303 | PASS | already on main as `purple-rain.glb` (exact dup) |
| Mokujin | 4,437 | PASS* | already on main as `dxmmii.glb` (exact dup) |

\* Zafina faces -Y (XPS-derived, not -X like the rigmodels rips) — verified via
true-front render. Yoshimitsu/Mokujin tripped the auto h/w-ratio gate (wide
armor/armspan) — both own-eyes verified as complete working humanoids.

Dedupe method: pygltflib POSITION accessor counts on landed GLBs vs
freshly-exported GLBs — all 14 matched exactly (verts + mesh counts).

## This PR
- `game/assets/models/thor_alt1.glb` — Ganryu second variant (3,354 verts,
  30 meshes, textured, T-pose). New: not on main in any form.
- `docs/pull-rest/tekken7/thor_alt1_front.png` — front approval render
  (white void, ortho) for the render lane / owner approval gate.

Models land AS ASSETS ONLY — no hookup/integration/gameplay edits (gate).
