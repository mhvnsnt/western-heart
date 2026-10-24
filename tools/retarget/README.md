# tools/retarget — Tekken animation retargeting pipeline

Retarget Tekken 7/8 skeletal animation onto Western Heart rigs. Headless,
batchable, free. No Cascadeur, no paid tiers.

## Key fact

Every Tekken character shares **one base skeleton** (`SKT_CH_base_Skeleton`
in T7; T8's naming is near-identical). Retargeting is 1:1 bone-name matching
through `tekken-bonemap.json` — no per-character presets.

The shared skeleton was verified by intersecting two community skeleton dumps
(King vs Jin from `Ludenous1/TK7_SK_CH`): identical bone names + parents
across characters. Only proportions differ.

## Files

| File | What |
|---|---|
| `tekken-bonemap.json` | T7 bone → WH bone maps (`tekken7_to_wh_canonical` for the 22-bone lab rig, `tekken7_to_mixamo49` for game GLBs like `pantera.glb`) |
| `tekken_skeleton_base.json` | Extracted shared T7 base skeleton: 60 core bones, hierarchy + rest positions (meters, UE Z-up) |
| `retarget_tekken.py` | Headless Blender batch retargeter: FBX/BVH/GLB in → animated GLB out |
| `tekken_hitprops.py` | Hit-feel numbers from Tekken's files → WH moveset patches (damage, startup, pushback→knock, frame advantage) |
| `tests/` | Fixture builder, motion verifier, joint sampler, proof plotter, Blender proof renderer |

## Retarget method

Local-space rest-relative delta, per mapped bone, per frame:

```
delta  = (SP_rest^-1 @ S_rest)^-1 @ (SP_pose^-1 @ S_pose)   # source joint delta vs parent
T_pose = TP_pose @ (TP_rest^-1 @ T_rest) @ delta             # onto target
```

Parent-relative (not armature-space) so unanimated children stay locally
static when the parent moves — no motion leak. Written via `matrix_basis`
(`PoseBone.matrix` is read-only; assigning it is undefined behavior —
verified empirically). Root translation scaled by hip-height ratio, or
zeroed with `--in-place` (the game pins `Hips` anyway).

## Usage

Single clip (T7 FBX → WH game model, in place):
```bash
blender -b --python tools/retarget/retarget_tekken.py -- \
    --source anims/king_punch.fbx \
    --target game/assets/models/pantera.glb \
    --out    game/assets/models/pantera@Punch.glb \
    --map tekken7_to_mixamo49 --in-place
```

Single clip (→ lab canonical rig, built procedurally):
```bash
blender -b --python tools/retarget/retarget_tekken.py -- \
    --source anims/king_punch.fbx --target-canonical \
    --out /tmp/king_punch_wh.glb --map tekken7_to_wh_canonical
```

Overnight batch:
```bash
blender -b --python tools/retarget/retarget_tekken.py -- \
    --batch tools/retarget/batches/king.json
# manifest: {"defaults": {...}, "clips": [{"source","target","out","clip","map","in_place"}]}
# writes <out>.report.json per clip + <manifest>.summary.json
```

Each run prints mapped/dropped bone counts; the report JSON lists every
mapping. Unmapped source helpers (face joints, `*_offset`/`*_null`) are
dropped; map targets missing on a specific rig are warned and skipped
(e.g. `pantera.glb` lacks 3 finger-tip bones).

## Hit properties

```bash
# one fighter (sidecar patch, no moveset change)
python3 tools/retarget/tekken_hitprops.py --fighter armor-king \
    --frame-data docs/t7t8-reference/frame-data-t7/armorking.json \
    --moveset game/assets/movesets/armor-king.json \
    --out /tmp/armor-king.hitprops.json

# whole roster (writes tools/retarget/hitprops/<fighter>.hitprops.json)
python3 tools/retarget/tekken_hitprops.py --all-fighters
# add --apply to write the numbers into the movesets under a "t7" key
```

Source: t7chicken (TekkenBot-extracted, 47 chars / 11,137 moves). Join key is
input notation. When `.tkmvst` extractions land, the TKMovesets
Reactions/Pushback vectors (true knockback vectors, wall splat, screw)
extend the same patch format.

## Validation

`tests/` builds the **real extracted T7 skeleton** in Blender, authors a
synthetic punch clip on it (clearly labeled `TEST_Punch_SYNTHETIC` — no T7
animation bytes exist in the repo yet), retargets to both rig paths, and
verifies the output GLB:

- armature + action present, sane frame range
- every mapped target bone exists
- no NaN transforms
- each animated bone shows its own motion (deg), static bones stay static
- stick-figure proof plots from the output GLB's joint positions

```
blender -b --python tools/retarget/tests/make_test_fixtures.py -- --outdir /tmp/fix
blender -b --python tools/retarget/retarget_tekken.py -- --source /tmp/fix/test_t7_anim.fbx \
    --target-canonical --out /tmp/fix/test_wh_punch.glb --map tekken7_to_wh_canonical --in-place
blender -b --python tools/retarget/tests/verify_motion.py -- --glb /tmp/fix/test_wh_punch.glb \
    --expect-map tools/retarget/tekken-bonemap.json --map-name tekken7_to_wh_canonical \
    --moved-bones Chest RightArm RightForeArm LeftArm Head RightUpLeg --fps 30 --proof-dir /tmp/proof
```

## For future Tekken teardowns

T8's skeleton uses near-identical naming — this pipeline applies directly.
When real T7/T8 animation extractions land (owner acquisition), drop the FBX
files in and run the batch. No code changes needed.
