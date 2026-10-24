# Animation targeting failure — Scarlett/Star test rig (2026-10-19)

Owner complaint: the twerk test showed mesh stretching/deformation; only the breasts
moved; the body barely animated; looked like hand-tooled procedural keys.

## Verdict

**The model is not the problem.** The Scarlett mesh's skinning is production quality:
all weights normalized, max 4 influences, max distance from any influenced vert to its
bone 0.04–0.25 m — no cross-body strays. The entire failure was in animation targeting.

## Root causes (verified in `~/workspace/star-rig-work/star_bound.blend`)

1. **The rig's control layer is hollow.** RIG-SCARLETT has 1111 bones and
   **0 (zero) constraints**. A generated Rigify rig has hundreds. The FK/IK/MCH
   control bones have `use_deform=False` and no vertex groups.

2. **The old test keyed the wrong bones.** `build_twerk.py` animated Rigify FK
   control bones (`torso`, `spine_fk*`, `thigh_fk*`, `shin_fk*`, `upper_arm_fk*`,
   …). Leg/arm FK chains live in branches the DEF bones are not parented to, so
   those keys did *literally nothing*. The 22 "bounce" keys on the `hips` bone
   were also void: no deform bones sit in its subtree (`DEF-spine` hangs off
   `root`, not `hips`).

3. **Only directly keyed DEF bones moved.** The mesh only responds to DEF bones
   (and a few named anatomy bones). The jiggle script keyed `DEF-breast.*`
   directly — that's why the breasts jiggled beautifully and nothing else moved.

4. **Partial motion stretched the silhouette.** Torso/spine lean propagated to the
   DEF-spine chain through *parenting side effects* while legs stayed at rest →
   sheared geometry that read as "weight stretching".

5. **Hand-authored motion, not captured.** Sine-wave keys can't be called targeting;
   there was no mocap and no retargeting anywhere in the chain.

## The fix (this branch)

- Real mocap: CMU lambada dance BVH (highest hip-energy 3 s window, 120→24 fps),
  via the open mirror `una-dinosauria/cmu-mocap` (BVH converted by B. Gane,
  MotionBuilder naming, frame 0 = T-pose).
- `tools/anim-retarget/retarget_def_rig.py`: retargets onto the **DEF skeleton**
  directly with production local-rest-relative math
  (`M = P_tgt @ P_tgt_rest⁻¹ @ T_rest @ (P_src_rest⁻¹ @ S_rest)⁻¹ @ (P_src_pose⁻¹ @ S_pose)`),
  in target-depth order with self-tracked parent matrices — never the stale
  depsgraph (the naive `pose_bone.matrix = M` pattern exploded the pose).
- Mechanism parents (`ORG-spine`, `ORG-shoulder.*`, `MCH-breast.*`, `MCH-ROT-head`)
  are driven as FOLLOWERS of the mocap bones they must track (own rest
  matrices), otherwise thighs/arms/breasts/head detach from the body.
- Root: rotation relative to bind; translation = in-place displacement from the
  first frame's pose (Z only, scaled by leg-length ratio) — the dancer's floor
  travel never leaks into the target.
- Jiggle: verlet-spring pass (solver family from `jiggle-work/`
  `star_jiggle_bake_fixed.py`) on `DEF-breast.*` + `Butt_*` chains, driven by the
  *baked mocap* parent motion. Full-body jiggle (breasts kept, glutes added,
  whole body dancing); face bones never keyed.
- Pipeline note for future rigs: retargeting to the DEF layer is correct for any
  rig whose control layer is hollow; the bone map lives in
  `tools/anim-retarget/bone_maps/cmu_to_scarlett_def.json`.
