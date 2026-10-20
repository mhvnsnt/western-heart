# Keemap wiring proof — CMU lambada -> Scarlett DEF rig (2026-10-20)

**Verdict: the wiring works; vendored Keemap v0.0.9 fails this rig.**
Keemap was loaded from the vendored tree and driven through its own
operators end-to-end on the real production job (details below), and
the output was measured with the repo quality gate and viewed by eye.
It collapses the mesh. This file is the evidence; nothing here is a
Keemap success claim, and no Keemap output ships.

## The job (identical for both paths)

- Source: CMU mocap `lambada_55_02.bvh`, frames 1261..1616 step 5
  @120 fps = exactly the 72 source frames of `lambada_loop.bvh`
  (verified by matching motion lines: loop frame 0 == full-BVH motion
  frame 1260, step 5), retimed to 72 frames @24 fps.
- Target: `scarlett_base.blend`, armature `RIG-SCARLETT` (1111 bones),
  29 mapped bone pairs incl. mechanism-parent followers.
- Baseline: the previous hand-rolled result for the same clip/rig,
  `scarlett_mocap.blend` (action `MocapRetarget`, 72 frames, produced
  by `retarget_def_rig.py` rest-relative math).
- Keemap path: `tools/anim-retarget/keemap_retarget.py` driving
  vendored Keemap (see `tools/open-source/blender-addons/keemap-retargeting/USAGE.md`):
  `wm.keemap_read_file` -> `wm.calc_correct_all_bones` (calibration at
  the CMU bind T-pose, frame 1) -> `wm.perform_animation_transfer`.
  Output action `Lambada_Keemap`, 119 fcurves (29 bones x quaternion +
  root location), saved `.blend` + GLB.
- Gate: `tools/auto_rig/anim_check.py` run on GLBs exported from both
  results with identical exporter settings (Blender 4.0.2, ACTIONS
  mode, force sampling, scene frame range).

## anim_check results (full reports: the two JSONs in this dir)

| Metric (gate) | Baseline (hand-rolled) | Keemap |
|---|---|---|
| Overall pass | **False** | **False** |
| Edge stretch p99.9 (gate <= 2.5) | 14.115 | **65.354** |
| Edge stretch max | 26.76 | 124.557 |
| Bones varying > 2% of rest length | 10 | 1 |
| Worst varying bone | tweak_spine->ORG-spine 1.08e9% (GLB hierarchy artifact, see note) | root->DEF-spine 34.2% (real: root position path) |
| Bones with mean length > 2% off rest | 217 | 229 |
| Vertex tearing max displacement | 0.0936 m | 0.0575 m |
| Tearing spikes | 0 | 0 |
| Root max deviation | 0.0 m | 0.0 m |
| Bones checked / meshes / frames | 1091 / 15 / 72 | 1091 / 15 / 72 |

Note: both exports share structural gate noise from this rig's GLB
hierarchy (disconnected Rigify branches measured as "bones", face-bone
rest deviations ~5000%+). The discriminating metric is edge stretch:
Keemap is ~4.6x worse than the already-failing baseline.

## Own-eyes (frames in this dir, all viewed by the wiring author)

- `keemap_front_f010.png` / `keemap_34_f010.png` — Keemap result,
  frame 10: shattered, streaked geometry; no readable dancer.
- `keemap_singleframe_34.png` — a single Keemap `test_all_bones` at
  source frame 1311 from a fresh scene: mesh bounding box collapsed
  to 0.35 m (rest ~0.9 m); the frame renders empty.
- `baseline_front_f036.png` — hand-rolled baseline, frame 36: a
  readable dancing figure (the baseline has its own known arm-stretch
  defect, visible in the owner lane's check renders and in its
  14.1 edge-stretch score — it is the lesser failure by far).

## Root-cause diagnostic (`diag_output.txt`, `keemap_run.log`)

Calibration self-consistency test: after Keemap's
`calc_correct_all_bones` at frame 1 (the shared T-pose), applying
`test_all_bones` at that SAME frame must reproduce the target's rest
pose. It does not:

- Worst mapped-bone head-position deviation at frame 1: **0.44 m**
  (DEF-hand.L/R). Forearms 0.25 m.
- World-orientation deviations at frame 1 up to ~267 deg
  (DEF-forearm.L), ~185 deg (DEF-shin.L/R), ~189 deg (feet).
- Spine chain is fine (head dev ~0.003 m, corrections 0–5 deg).

Transfer fidelity test: after `test_all_bones` at frame 1311, the
dest-vs-source world-quaternion angle equals the calibrated
correction angle for **all 29 bones** (e.g. thigh 175.2 deg = its
correction; angles >180 read as 360-x). The transfer faithfully
executes the corrections — the corrections themselves are wrong.

Why: `KeeMapBoneOperators.SetBoneRotation` computes a WORLD-space
rotation difference and applies it in POSE space
(`final = pose_quat @ diffWS @ correction`) without conjugating by
the parent bone's world rotation, and the edit-bone
rest-orientation compensation code in that function is commented
out upstream. On rigs whose bone parents sit near world-aligned at
rest this approximates fine; on the Rigify DEF rig (baked bone
rolls; thigh/foot/arm rest orientations 90–179 deg off the BVH
skeleton) calibration measures garbage and the pose collapses.

Keemap's calibrated corrections for this job:
`cmu_to_scarlett_keemap_calibrated.json` (written by Keemap's own
`wm.keemap_save_file`). Full transfer log: `keemap_run.log`
(Keemap loaded, 29 pairs, calibration, transfer 0–100%, action
`Lambada_Keemap` normalized to frames 1..72).

## Artifacts outside this repo dir

Working files (not committed; large): `~/workspace/anim-fix-work/keemap-proof/`
— `run1/scarlett_keemap_lambada.blend` (52 MB), both GLBs (21 MB
each), the driver/run scripts and full logs used above.

## Recommendation

Keep the hand-rolled rest-relative retarget as the production path
for DEF rigs. Re-evaluate Keemap only if upstream restores the
rest-orientation compensation, or for target rigs that are
world-aligned at rest. The driver + this evidence make that
re-evaluation a one-command rerun.
