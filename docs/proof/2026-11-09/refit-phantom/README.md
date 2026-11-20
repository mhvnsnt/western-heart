# Phantom attire 1 re-rig: candidate, not wired (2026-11-09)

Owner (verbatim): "do the skin wait and get the rig and stuff the skeleton in the model and the skin and the weights
and all perfect and then put it on the f****** more upgraded Tekken 7 are taking five f****** bases".

## What this is

`roster/phantom/attires/attire1/model-rerig-refit.glb` is `model-rerig.glb` (the fight model; unchanged, keep-both)
re-rigged by the repo pipeline `tools/auto_rig/refit_rig.py`. Its steps:

1. Template skeleton fitted inside the mesh, then arms, hips, knees, spine, neck and head placed from the mesh's own
   landmarks.
2. Blender bone heat (voxel proxy) re-skin.
3. Head territory.
4. Hair chains for the game's spring bones.
5. Gates.

It ran with `--facing +Z --height 1.8`, both measured from the model by `batch_refit.facing_and_height`.

## Verdict so far

**By eye** (`before-after-upper-stance-hit.png`, `before-after-full-stance-light-medium.png`, made with
`tools/model-audit/weight_compare.mjs`: the game's own loader and retarget, current model left, candidate right):

- **Stance (his T7 stance):** the long hair hangs from his head. Before, it was weighted to the thighs and smeared into
  a flat sheet across his face and raised arm. His face is visible again.
- **Torn vertices** (stretch >= 2x and >= 1 cm):
  - stance 34,937 -> 19,268
  - light 42,282 -> 19,853
  - hit 42,619 -> 13,083
  - medium (kick) 43,888 -> 38,959; the apron still stretches along the kicking leg.
- **Hit clip:** the result still looks wrong on both rigs. His non-stance clips come from the Tekken 3 Yoshimitsu bank,
  whose chest data is tilted about 90 deg even in its stance (the worst of every bank surveyed). That is the old-data
  problem the owner named. The fix is his own T7 actions (task: T7 generic banks; needs the T7 paks, see
  `tools/depot-pull/T7-USER-STEPS.md`), not more rig work.

**Pipeline gates** (`rig_report.json`): validate PASS and seams PASS. The strict stretch gate fails (p99.9 7.24 against a
2.5 bar), as does the official anim_check on the CMU boxing gate clip (3.08). Those numbers include the foot spikes the
pipeline itself notes on every rig.

**Not wired into the game.** It lands next to the original for the owner's by-eye call. Wiring is one line in
`game/js/assets.js` (`phantom:` URL).
