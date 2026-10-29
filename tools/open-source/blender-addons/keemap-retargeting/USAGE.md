# Keemap — USAGE in Western Heart (production wiring)

Keemap (nkeeline, GPL-3.0) lives vendored at
`tools/open-source/blender-addons/keemap-retargeting/` (`Source/SourceFiles/`).
It is the retarget engine of `tools/anim-retarget/keemap_retarget.py` —
mocap BVH in, animated DEF-rig `.blend` + GLB out, fully headless.
Verified on Blender 4.0.2 with the real Scarlett rig + CMU mocap
(see "Proof run" at the bottom).

## How Keemap actually works (from its source, not the GUI)

- Settings live in `scene.keemap_settings` (a `KeeMapSettings`
  PropertyGroup, `KeeMapSettings.py`): `source_rig_name`,
  `destination_rig_name`, `start_frame_to_apply`,
  `number_of_frames_to_apply`, `keyframe_every_n_frames`,
  `bone_mapping_file`, `bone_rotation_mode` (`EULER` / `QUATERNION`),
  `keyframe_test`.
- The bone map lives in `scene.keemap_bone_mapping_list`, a collection of
  `KeeMapBoneMappingListItem` (`KeeMapBoneSettings.py`). It round-trips
  through a JSON file via Keemap's own operators
  `wm.keemap_read_file` / `wm.keemap_save_file` (`KeeMapBoneList.py`) —
  the driver feeds it `tools/anim-retarget/bone_maps/cmu_to_scarlett_keemap.json`
  and can write the calibrated map back out with `--save-map`.
- Transfer math (`KeeMapBoneOperators.SetBoneRotation`): for each mapped
  bone, Keemap takes the source bone's WORLD-space quaternion and sets
  the destination bone's world rotation to match, then right-multiplies
  the pose quaternion by a per-bone correction quaternion
  (`QuatCorrectionFactor`, or `CorrectionFactor` euler in EULER mode):
  `final = pose @ (destWS.rotation_difference(sourceWS)) @ correction`.
  Because it works in world space, entries are independent — one source
  bone may drive several destination bones (we map CMU `Spine1` to
  `DEF-spine.004` AND the followers `ORG-shoulder.L/R`, `MCH-breast.L/R`,
  the mechanism parents the DEF deform bones hang from).
- List order matters (the Keemap panel says it outright): parents before
  children; the transfer walks the list in order. The driver sorts the
  map by destination-bone depth.
- Position is separate and opt-in per bone (`set_bone_position`,
  `SINGLE_BONE_OFFSET` type): Keemap sets the destination bone's world
  position to the source bone's world position, then applies
  `location = (location + position_correction_factor) * position_gain`.
  We enable it on the root pair only (`Hips -> DEF-spine`).
- Corrections are CALIBRATED, not guessed: with both rigs in a shared
  pose, `wm.calc_correct_all_bones` ("CALC ALL ROTLOC CORRECTIONS") runs
  `CalcRotationOffset` + `CalcLocationOffset` per bone — it applies an
  identity transfer, measures how far the destination bone's world
  rotation/position moved from where it started, stores the difference
  as that bone's correction, and restores the destination pose.
- The transfer itself is one operator call:
  `bpy.ops.wm.perform_animation_transfer()` — it steps the timeline
  from `start_frame_to_apply` by `keyframe_every_n_frames` for
  `number_of_frames_to_apply` frames and calls `wm.test_all_bones`
  (keyframe=True) on each step.

## Loading Keemap from a script (no GUI, no install)

Follow Keemap's own `Source/Code Load.py` pattern:

1. Append `Source/SourceFiles` to `sys.path`.
2. Append `"DEBUG_MODE"` to `sys.argv` (so `__init__.py` imports its
   modules as top-level names instead of a package path).
3. `exec(compile(open(__init__.py).read(), __init__.py, "exec"),
   {"__name__": "__main__", ...})` — `__init__`'s `register()` then
   registers all classes: `scene.keemap_settings`,
   `scene.keemap_bone_mapping_list`, and the `wm.*` operators.

`keemap_retarget.py:load_keemap()` does exactly this. Installing the
addon through Blender preferences is NOT needed (and the vendored tree
is not a standard addon zip — do not try; see README's install notes).

## The production workflow (what the driver does)

```
xvfb-run -a env -u PYTHONPATH <blender-4.0.2> -b <target.blend> --python \
  tools/anim-retarget/keemap_retarget.py -- \
  --source <clip.bvh> --target-arm RIG-SCARLETT \
  --bonemap tools/anim-retarget/bone_maps/cmu_to_scarlett_keemap.json \
  --out <out.blend> [--glb-out <out.glb>] [--save-map <calibrated.json>] \
  [--start-frame N] [--num-frames N] [--keyframe-every K] [--out-fps 24]
```

1. Opens the target blend, clears any existing action on the target
   armature (per-character isolation: only this rig's file is touched).
2. Imports the BVH at the scene fps matching the BVH (parsed from its
   `Frame Time:`) so source frames are 1:1 with Blender frames.
3. HIP-PROPORTION FIRST (the stretch fix): uniformly scales the SOURCE
   armature object by the leg-length ratio
   `len(DEF-spine->DEF-thigh.L->DEF-shin.L->DEF-foot.L) /
    len(Hips->LeftUpLeg->LeftLeg->LeftFoot)`, so Keemap's world-space
   position transfer is meaningful and `position_gain` stays 1.0.
   (Rotation transfer is scale-invariant; position is not.)
4. Reads the bone map through `wm.keemap_read_file`, then sets rig
   names + `bone_rotation_mode=QUATERNION` (read_file overwrites
   settings from the file — set them after the read).
5. Calibrates at the shared pose: frame 1 of a CMU BVH is the bind
   T-pose (all rotation channels are zero) and the target is at rest;
   runs `wm.calc_correct_all_bones`.
6. Sets transfer settings and runs `wm.perform_animation_transfer`.
7. Renames the action `Lambada_Keemap`, remaps keyframe x-coordinates
   onto the output timeline (`1 + (x - first) * out_fps / src_fps`),
   removes the source rig AND its action, saves the `.blend`,
   optionally exports an animated GLB (whole scene minus stray non-rig
   meshes; `ACTIONS` mode, force sampling) for the
   `tools/auto_rig/anim_check.py` gate.

## Gotchas found driving it headless on Blender 4.0.2

- `CalcRotationOffset` / `CalcLocationOffset` reference `self.report`
  in their error branches although they are module-level functions —
  they only survive because those branches are never taken when rig and
  bone names are all valid. Keep every mapped name valid (the driver
  validates and drops unresolvable pairs before calibrating).
- `wm.keemap_read_file` overwrites ALL settings from the JSON,
  including rig names and the mapping-file path — apply your settings
  after reading, and re-set `bone_mapping_file` before saving.
- Keemap's save format only writes `scale_secondary_bone_name` and
  `bone_scale_application_axis` under its `set_bone_scale` read quirk —
  keep those keys in the JSON (our map does).
- The key in the format is spelled `postion_type` (sic) — do not
  "fix" it; Keemap reads exactly that.
- Leaving the imported BVH's action in the file makes the glTF
  exporter (`ACTIONS` mode) try to sample the whole BVH action onto
  the target rig — warnings, huge exports, failed writes. The driver
  deletes every action except the Keemap result before saving.
- Headless object selection is unreliable in this Blender build, so
  the GLB export does not use `use_selection`; it deletes stray
  non-rig meshes in memory AFTER the `.blend` is saved and exports
  the scene.
- `export_animation_mode` on 4.0.2 is `"ACTIONS"` (not `"ACTION"`).
- Keemap keys only the sampled frames; between keys the pose is
  interpolated. Sampling every 5th frame of a 120 fps CMU clip and
  re-timing to 24 fps reproduces the 72-frame loop the hand-rolled
  lane shipped, with identical source frames.
- Keemap does NOT key scale (except its Rigify finger-scale mode,
  unused here) and never touches unmapped bones — face bones and the
  jiggle chains (`DEF-breast.*.001`, `Butt_*`) stay unkeyed, same as
  the hand-rolled path. A jiggle pass can be layered afterwards.

## Proof run (2026-10-20)

- Clip: CMU `lambada_55_02.bvh` frames 1261..1616 step 5 @120 fps —
  exactly the source frames of `lambada_loop.bvh` (verified by matching
  motion lines: loop frame 0 == full-BVH frame 1260, step 5), the clip
  of the hand-rolled baseline (`scarlett_mocap.blend`, action
  `MocapRetarget`, 72 frames).
- Target: `scarlett_base.blend`, armature `RIG-SCARLETT` (1111 bones),
  29 mapped pairs incl. followers.
- RESULT: **Keemap v0.0.9 as vendored FAILS on this rig.** The wiring
  above works end-to-end (Keemap's own operators load, calibrate,
  transfer, keyframe, save), but the retargeted mesh collapses —
  rendered proof frames show a shattered/streaked figure, and a
  single-frame test collapses the mesh to a 0.35 m bounding box.
  Root cause, proven by the diagnostic in
  `tools/anim-retarget/proof/keemap-lambada/` (METRICS.md + diag log):
  Keemap's calibration is not self-consistent on the Rigify DEF rig.
  At the calibration frame itself, after `calc_correct_all_bones` +
  `test_all_bones`, mapped bones' world orientations deviate from
  rest by up to ~267 deg and head positions by up to 0.44 m (hands).
  The transfer is faithful to those corrections (post-transfer
  dest-vs-source world angles equal the correction angles for all 29
  bones), so the defect is inside Keemap: `SetBoneRotation` applies a
  WORLD-space rotation difference directly in POSE space
  (`pose @ diff @ corr`, no conjugation by the parent's world
  rotation), and the edit-bone rest-orientation compensation that
  would account for Rigify's baked bone rolls is commented out in
  `KeeMapBoneOperators.py`. Keemap works on rigs whose parents are
  near world-aligned at rest (spine chain here calibrated fine:
  corrections 0–5 deg, head deviation ~0.003 m); it breaks on
  rolled-bone chains (thighs/feet ~173–179 deg, arms up to ~177 deg).
  Do NOT ship Keemap output for DEF rigs; the hand-rolled
  rest-relative path remains the production retarget for Scarlett.
  Metrics for both paths: `tools/anim-retarget/proof/keemap-lambada/`.
