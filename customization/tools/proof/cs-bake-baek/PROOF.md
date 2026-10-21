# CS-BAKE SELF-PROOF — Baek master-white (2026-10-20)

Fixture: `roster/baek/attires/master-white/customization.example.json`
(muscle +0.4, shoulders +0.3, eye_size +0.25, eye swap to eye-yellow-tiger via
the `customization/parts/baek-eyes/` mapping). Baked with
`customization/tools/apply_customization.py` under Blender 4.0.2 headless
(`xvfb-run -a`), MPFB2 checkout at `cape-jones/production/tools/mpfb2`.

## Bake result

- Exit 0, no per-item errors. Output: `roster/baek/attires/master-white/model-custom.glb` (579,492 bytes).
- Structure intact: 35 meshes / 35 materials / 35 images, skin 50 joints — same
  counts as the base `baek-master-white-rigged.glb`. No NaN (tool validator).
- Morphs (geometry diff, base vs baked, per-vertex): 887 of 2,883
  index-comparable verts moved, max 13.4 mm; whole-model X span
  1.906 m → 1.933 m (+27 mm shoulders/muscle). 5 meshes differ in vert count
  by +1…+3 (glTF exporter seam re-splitting on re-export, both directions of
  the pipeline show it; geometry otherwise index-identical).
- Eye swap: texture `pek1u_29` (material `mat_21-pek1u_29.jpg`) replaced —
  JPEG 2,935 B (sha256 d7a6df3b…) → PNG 23,309 B (sha256 51f22d37…), the
  eye-yellow-tiger image, full-replace per the baek-eyes manifest.
- Animation check: the base model carries **0 animation clips**, so
  `tools/auto_rig/anim_check.py` has nothing to check (the brief's conditional
  case). Rig itself verified intact (50-joint skin, identical pose in renders).

## Renders (locked method, docs/RENDER-ORIENTATION.md)

Rendered with `docs/tpose-refs/_tools/tpose_render_cycles_faceY.py` (this GLB
faces −Y; the base script's front showed a profile, the faceY variant is the
documented fix), 2048×2048, white background, Cycles.

- `before_front.png` / `after_front.png` — full body fronts.
- `before_head.png` / `after_head.png` — head crops of the same frames.

**Own-eyes verdict (the agent who ran this bake): PASS.**
- AFTER shows visibly broader shoulders/torso and thicker arms than BEFORE;
  belt span widens with the torso. Morphs visible.
- AFTER head crop shows distinct amber/yellow irises; BEFORE shows the
  original dark brown eyes. Eye swap visible.
- Textures full-color and intact in both; pose/rig identical; dobok, trim,
  belt, logos unchanged. A belt-tip fragment floats at head height in BOTH
  frames — pre-existing in the base model + this renderer, not a bake defect.
- Note (owner verdict 2026-10-20 ~19:40 CDT): this fixture's eye swap is the
  legacy eye-*texture*-variant mechanism (Baek's saved option library).
  Production eye design changes are real placeable mesh parts — see
  `customization/CUSTOMIZATION-JSON-SCHEMA.md` "Eyes are mesh parts".

## Game hook smoke (Node)

`node customization/tools/test_game_hook.mjs .` → **SMOKE PASS**:
91 MODEL_URLS keys load; synthetic registry override replaces
`baek-master-white` base URL with `../roster/baek/attires/master-white/model-custom.glb`
and the target file exists; empty registry is an exact no-op.

## Registry emit (end-to-end, scratch copy)

With a real `customization.json` in the attire folder, emit produced:
`'baek-master-white': '../roster/baek/attires/master-white/model-custom.glb'`
— key derived by matching the attire's `base_glb` against `MODEL_URLS` in
`game/js/assets.js`, exactly the key convention the game uses.
