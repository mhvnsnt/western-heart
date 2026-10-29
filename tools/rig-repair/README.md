# Rig Repair Tools

Universal pipeline-level tools for fixing rig defects. These are NOT per-model
one-offs — they implement general policies that apply to any model.

## Tools

### finger_symmetry.py
Detects and fixes finger bone asymmetry vs the Tekken 7 convention.

T7 convention (CORRECT, do not "fix"):
- 3-segment thumbs, index, middle, ring fingers
- 2-segment pinkies (this is intentional, not a defect)
- Symmetric L/R (the TRUE defect is asymmetry, e.g., LeftHandThumb3 missing)

Usage:
```bash
# detect only (exit 1 if asymmetry found)
python3 finger_symmetry.py model.glb

# detect and fix (adds missing bones, mirrors weights)
python3 finger_symmetry.py model.glb --fix -o fixed.glb
```

### weight_validate.py
Flags cross-region weight violations (hand/arm↔leg, hand↔tail, L↔R limb bleed).
Also checks 4-influence cap and normalization.

Universal repair policy (`--fix`):
- A vert's "home region" is determined by its dominant bone's region.
- Any other influence >0.12 in a SUSPICIOUS region-pair gets moved to the
  dominant bone, then renormalize + enforce 4-influence cap.
- Suspicious pairs are SYMMETRIC (arm↔leg, arm↔tail, leg↔tail, armL↔armR,
  core↔tail) EXCEPT legitimate boundary blends:
  - arm↔core at the shoulder (anatomical)
  - leg↔core at the hip (anatomical)
  - tail-root↔body (tail grows from pelvis; tail root = tail joint whose
    parent isn't a tail joint)

Usage:
```bash
# validate only (exit 1 if violations found)
python3 weight_validate.py model.glb

# validate and fix
python3 weight_validate.py model.glb --fix -o fixed.glb
```

### limb_mirror.py
Adds bones + weights for a duplicate limb (e.g., a second pair of arms).
Mirrors the source chain's structure and (optionally) geometry.

The tool:
1. Creates new bones mirroring the source chain (names: `<Side>Lower<Rest>`,
   e.g., `LeftLowerShoulder`).
2. Places them via PCA on the duplicate limb's verts (or explicit `--positions`).
3. Assigns weights via geometric skinning (proximity to new bone segments).
4. Replicates finger sub-chains.

Key options:
- `--src-chain`: source bones to mirror (e.g., `LeftShoulder,LeftArm,...`)
- `--donors`: bones whose weights to reassign (e.g., `Spine,Spine1,...`)
- `--positions`: explicit bone positions (overrides PCA); format
  `"x1,y1,z1;x2,y2,z2;..."` (Left side, x-mirrored for Right)
- `--xmin`, `--tube-r`, `--ymin`, `--ymax`: selection bounds for the limb verts

The tool aborts unless the model's IBMs equal inv(joint world matrices)
(i.e., the mesh is in bind pose). This is a safety check — the geometric
skinng assumes bind-pose vertex positions.

### verify_render.py
Renders front-view + posed verification images via three.js + headless Chromium.

Usage:
```bash
python3 verify_render.py verify_spec.json output_dir/
```

The spec JSON lists models with their slug, file path, facing, and poses.
Poses use `bone.rotateX/Y/Z()` (NOT direct euler assignment, which corrupts
three.js bone orientations).

## Design principles

1. **Universal, not per-model.** Every fix is a general policy or algorithm.
   No hardcoded model names, no per-model special cases.

2. **Pure-Python GLB surgery.** Weight edits rewrite accessor bytes in place
   (no JSON changes). Bone additions append nodes/skin-joints/IBMs. No Blender
   round-trip (avoids re-export artifacts).

3. **Validate before and after.** Every tool validates its input and
   re-validates after fixing. Zero residual violations is the bar.

4. **Render proof.** Every fix is verified with front-view renders (no
   Y-rotation) + posed motion checks. The bind pose must be pixel-perfect;
   the posed result must articulate without tearing.
