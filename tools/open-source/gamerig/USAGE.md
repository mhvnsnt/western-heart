# GameRig — usage notes (Western Heart)

GameRig (by Arminando) is a **Rigify feature set** that turns a fitted
Rigify metarig into a game-engine-ready deform rig: its `game.*` rig
types subclass the stock Rigify rigs but generate DEF bones in a
**single clean hierarchy** (no bendy bones, no deform/control split
branches), which is what game engines (and our glTF pipeline) want.

Vendored at `tools/open-source/gamerig/` (targets Blender 4.5.4/5.0;
we run it on Blender 4.0.2 — see the shim note below). Production
driver: `tools/auto_rig/backends/gamerig_backend.py`, wired into the
unified CLI as `--backend gamerig`. Worked example with proof:
`tools/auto_rig/examples/gamerig-baek/`.

## The workflow (what the driver does, headless)

1. **Install as a Rigify feature set.** Copy this directory into
   `<bpy.utils.script_path_user()>/rigify/gamerig`, enable the `rigify`
   addon, then `prefs.refresh_installed_feature_sets()` and
   `prefs.update_external_rigs()` so the `pose.gamerig_generate`
   operator and the 27 `game.*` rig types register.
2. **Import the static GLB** and refuse if it already has an armature
   (GameRig rigs from scratch; it is not a re-rigger).
3. **Normalize.** Tripo exports arrive miniature (~2.3 cm, object scale
   0.01) in arbitrary orientation. Uniform-scale to the target height
   (default 1.8 m), feet on z=0, centered, and yaw so the character
   faces -Y. Facing is detected from the feet-vs-shins centroid offset
   and verified against renders — do not trust any single axis guess.
4. **Add the stock human metarig** and fit it (below). Strip the face
   subtree (92 of 159 bones): WH skeletons have no face bones.
5. **Generate**: `bpy.ops.pose.gamerig_generate()`. It converts the
   metarig's stock rig types to their `game.*` equivalents and builds
   the full control+deform rig (~410 bones, 73 of them DEF).
6. **Strip to deform.** The exported game skeleton is the 73 DEF bones
   only. This step is required, not cosmetic: DEF bones in the
   generated rig are constraint-driven, so they cannot be keyframed
   directly. Deleting every non-DEF bone (in edit mode) bakes the DEF
   hierarchy into a plain FK skeleton that exporters and engines read
   directly. The driver verifies first that every DEF bone's parent is
   another DEF bone or None — GameRig's core promise — and fails
   loudly otherwise.
7. **Skin** with Blender bone-heat (`armature_parent_set` with
   `ARMATURE_AUTO`), then assign any unweighted vertices to their
   nearest bone (heat leaves disconnected islands unweighted, and
   unweighted vertices crash the glTF exporter).
8. **Optional proof clip** (below), then **export GLB** with
   `export_def_bones`-style settings (only the stripped armature
   remains, so the skin is exactly the DEF set).
9. **Canonical rename** (post-export, JSON chunk only): DEF names are
   rewritten to WH canonical names (`DEF-spine` -> `Hips`,
   `DEF-upper_arm.L` -> `LeftArm`, `DEF-f_pinky.03.R` ->
   `RightHandPinky3`, ...) so the output passes validate.py's bone
   gate. Unit-tested in `tools/auto_rig/tests/test_gamerig_rename.py`.

## Metarig fitting notes

- Fit order: uniform scale to mesh height first, then **arm-chain
  stretch** (shoulder->wrist length ratio mesh vs template, applied
  along X) and **leg stretch** (from hip-band width), both clamped.
  Game characters are wider than the stock metarig; an un-stretched
  fit puts elbows inside the torso and ruins the heat weights.
- **Never flatten the arms to a perfectly straight T.** Rigify's limb
  rigs compute a pole direction from the elbow bend; a zero-bend chain
  makes generation fail with
  `Vector.angle(other): zero length vectors have no valid angle`.
  The driver keeps 15% of the template's natural elbow droop.
- Palm/finger subtrees are translated rigidly by the hand's fitted
  delta after the arm stretch, instead of being re-fitted joint by
  joint — fingers stay proportional.

## Blender 4.0.2 compatibility shim (important)

GameRig targets Blender 4.5.4+. On 4.0.2 exactly one method is
incompatible: GameRig's `Generator_gamerig.__create_root_bone` predates
4.0.2's `noparent_bones` bookkeeping and would parent the generated
root bone to itself. The driver substitutes the stock 4.0.2
implementation for that one method
(`Generator_gamerig._Generator__create_root_bone =
rigify.generate.Generator._Generator__create_root_bone`) and runs all
`game.*` deform modules unmodified. A benign double-registration
traceback for `POSE_OT_gamerig_upgrade_game_face` can appear in the
log during install; the driver treats registration as successful only
if the operator and the `game.*` types are actually present. Drop the
shim when the repo's Blender is upgraded past 4.5.

## Baking a proof clip (donor transfer)

`--donor` accepts a GLB with embedded clips or a **CMU BVH** (the
proven path — `assets/free-pull-1/cmu-mocap/fighting/*.bvh`). The
transfer is a **world-space rotation-delta FK bake**:

- per mapped bone, `R_delta = R_pose @ R_rest^-1` in world space,
  applied to the target's rest world rotation; positions are then
  recomputed down the target hierarchy from rest offsets, root pinned
  (WH clips are in-place). Unmapped bones (pelvis, breast, palms,
  leaf segments) inherit their parent's delta and follow rigidly.
- World space is not optional: the armature-space local delta used by
  classic retargeters assumes both skeletons share bone-roll
  conventions. A glTF/BVH donor and a Rigify rig do not, and the local
  form visibly corkscrews limbs (verified on this model).
- Bake via `matrix_basis` computed from your own FK matrices.
  Assigning `pose_bone.matrix` in a loop reads the parent's
  **previous** evaluated matrix — the setter lags one depsgraph tick —
  which scrambles the first frames of the bake (also verified).
- GLB donors: mute all NLA tracks before evaluating (importers stack
  every clip as a track), and delete the donor's actions before
  export or the exporter ships them alongside the baked clip.
- CMU BVH: the WH spine chain sits one link lower in CMU layout
  (`LowerBack` = WH `Spine`, CMU `Spine` = WH `Spine1`, CMU `Spine1`
  = WH `Spine2`); thumbs are single bones (`LThumb`/`RThumb`). The
  driver maps both. Use `--clip-start/--clip-frames/--clip-step` to
  cut a window (CMU is 120 fps; step 4 = 30 fps output).

### Warning: WH game GLBs are poor Blender-side donors

`game/assets/models/pantera.glb`'s embedded clips are authored for
the game's three.js runtime and **do not evaluate correctly in
Blender** (their Hips translation channel sits ~8 m from bind —
`anim_check.py` reports the root wandering 8.21 m and edge stretch
p99.9 of 11.27 on the unmodified production file). The rig itself is
fine; use CMU BVH (or another Blender-native source) for proof clips
until those clips are re-exported.

## Validation notes (read before "fixing" checker output)

- `validate.py`'s height probe reads only `meshes[0].primitives[0]`.
  On multi-part Tripo GLBs (35 parts) that is an accessory piece, so
  `height_ok` can fail on a correctly-sized model. The backend
  enforces the true full-body height itself (metrics JSON); the
  example output measures 1.80 m.
- `anim_check.py` flags `Hips->LeftPelvis/RightPelvis` bone-length
  variance on any GameRig/Rigify output: DEF pelvis bones are
  zero-offset helpers whose heads coincide with the Hips joint
  (their glTF translation channel is a constant (0,0,0) — verified in
  the example's `anim_check_report.json` against the raw channels),
  and the checker's relative-variance formula divides by that ~zero
  rest length. It is a checker artifact, not stretch.
- The same report's tearing spikes on the example are a single fast
  mocap instant (max vertex displacement 0.32 m, below the 0.35 m
  absolute threshold; edge-stretch p99.9 = 1.59, passing). Compare
  the production pantera control above before treating either as a
  regression.

## Reproduce the example

```bash
python3 tools/auto_rig/auto_rig.py \
    --in roster/baek/attires/master-white/baek-master-white.glb \
    --out baek-master-white_gamerig.glb --backend gamerig \
    --donor assets/free-pull-1/cmu-mocap/fighting/135_04.bvh \
    --clip CMU135_04_boxing --clip-start 240 --clip-frames 72 \
    --clip-step 4
```

Output is deterministic: three runs of this command produced
byte-identical GLBs (md5 c2698b6bd70184b59e6edd904ebc8ae5).
