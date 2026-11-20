# Known Issue: Extra Arm Part Offset — FIXED 2026-10-16

## Symptom (was)
Extra arm parts (DX_xarm_*) rendered offset ~127mm from their bones, while main
arm parts (DX_arm_*) rendered correctly. (In fact ALL bone-parented parts were
shifted — mains too — but the extra arms showed it most clearly.)

## Root Cause (found 2026-10-16, bone-roll hypothesis RULED OUT)
**Blender 4.0.2 parents objects to the bone TAIL — not the head — when
`parent_type='BONE'` is set via RNA.** The pipeline's `parent_to_bone()` used
the RNA sequence (`ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone =
...; ob.matrix_parent_inverse = ...`), so the depsgraph AND the renderer used
effective parent matrix `X = T(posed_tail) @ Rot(pose_bone)`.

The pipeline computed `matrix_parent_inverse = (rig.matrix_world @
matrix_local)^-1` — the HEAD-based inverse. Head-based Pinv + tail-based
runtime = every part rendered shifted by exactly one bone-vector toward the
tail in every frame. A pure positional offset with perfect rigid follow, which
is why `P_rest @ Pinv = I` verified yet renders were wrong.

Proven with minimal repros (blender-4.0.2, xvfb):
- RNA `parent_type='BONE'` => tail-based, regardless of RNA assignment order.
- `bpy.ops.object.parent_set(type='BONE')` => head-based (correct/documented).
- RNA `parent_type='OBJECT'` => correct (no quirk).

Bone roll was investigated first: `matrix_local` rotation components compared
between 02b-repaired (extra) and unrepaired (main) bones — no anomalous roll;
`(R@M)@Pinv = I` to 1e-7 for all parts. Roll is NOT the cause.

## Fix (applied 2026-10-16)
Recompute Pinv against the TRUE runtime parent matrix (approach (a):
recompute Pinv — the evidence refuted the roll hypothesis and confirmed the
parenting quirk):
`Pinv = (rig.matrix_world @ T(tail_local) @ Rot(matrix_local))^-1`.
Validated: exact rigid follow (<0.001mm vs head-based formula) across poses.
- `scripts/03_build_body.py` `parent_to_bone()` — fixed.
- `scripts/04_states_demo.py` — `eval_bone_parent_X()` / `pinv_for_bone()`
  helpers; `true_world_of()` now uses the tail-based X (the old head-based
  formula measured a fantasy: sub-micron deltas while renders were shifted);
  `parent_to_bone()` reattach uses X/Pinv consistently; identity-basis key at
  f167 so pre-switch frames render rigid on-bone.
- Pipeline re-run: 03 → 04 → 05a. Measurements PASS with the true formula
  (detach/reattach < 0.001mm). All 9 QC stills re-rendered and eyes-checked
  limb-by-limb: extra arms assembled in attached / growing / detached-floating
  states. `hide_render` workaround kept working.

## Verified Facts (corrected)
- P_rest(head-based) @ Pinv(old) = I — true but IRRELEVANT; runtime is tail-based.
- Bone constraints are muted (pure FK) — still true.
- Measurements PASS with the TRUE formula: detach/reattach deltas < 1mm.
- Object scale does not render on bone-parented objects in Blender 4.0.2
  headless — still true; hide_render workaround in place and working.

## TODO (pre-existing, NOT this defect — reported separately)
- Leg DEF chains have 5 segments (thigh→thigh.001→shin→shin.001→foot) but parts
  exist only for 3 → 268mm/226mm visual gaps in the legs. Separate defect.
- Detach/reattach uses structural reparenting which is not keyframable: in
  playback f168–240 the parts do not follow the gyro (they stay near the
  socket). The switch math itself is exact (<0.001mm). Separate defect.
