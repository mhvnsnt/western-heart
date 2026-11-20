# tools/anatomy — Procedural anatomical layers

Generates the four separable volumetric anatomy layers (BONE / MUSCLE / FAT /
SKIN) for a character from their rigged GLB + skeleton. Spec:
`docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md`.

## generate_layers.py

Deps: Python 3, numpy, pygltflib. No Blender.

```bash
# generate layers for a fighter
python3 tools/anatomy/generate_layers.py \
  --glb roster/pantera/pantera_rigged.glb \
  --fighter pantera \
  --glb-relpath roster/pantera/pantera_rigged.glb \
  --out roster/pantera/anatomy

# with proof renders + numeric validation
python3 tools/anatomy/generate_layers.py --glb ... --fighter ... \
  --out ... --render-proof

# apply morph values, dump morphed layers
python3 tools/anatomy/generate_layers.py --glb ... --fighter ... \
  --out ... --morph '{"muscle_biceps_L":1.0,"fat_thickness":0.3}'
```

Outputs in `<out>/`:
- `anatomy-layers.json` — the four layers + morph parameter registry
  (`wh.anatomy-layers/1` schema)
- `renders/` — sphere-traced front-view PNGs per layer + morph comparison
  (with `--render-proof`)
- `proof.json`, `PROOF.md` — numeric validation (with `--render-proof`)
- `anatomy-layers.morphed.json` — layers after `--morph` values

## Library use

```python
from tools.anatomy.generate_layers import (
    generate, apply_morphs, bake_displacement, eval_layer_sdf)

layers, aux = generate('pantera_rigged.glb', 'pantera',
                       'roster/pantera/pantera_rigged.glb')
morphed = apply_morphs(layers['layers'], {'muscle_biceps_L': 1.0})
disp_vec, disp_s = bake_displacement(aux['pos'], aux['normals'],
                                     aux['regions'], layers['layers'], morphed)
new_pos = aux['pos'] + disp_vec   # skin rides the muscle
```

## Morph parameters

- `muscle_<group>` (e.g. `muscle_biceps_L`, `muscle_quadriceps_R`): bulk per
  muscle group, range [-1, 1]; radius `*= 1 + 0.55*v`.
- `fat_<region>` / `fat_thickness`: regional/global fat, range [-1, 1];
  thickness `*= 1 + 0.8*v`.
- `bone_scale_<limbs|spine|skull|ribcage|pelvis>`: bone scale, range [-1, 1];
  radii `*= 1 + 0.25*v`.

The creation-suite UI consumes these via `ANATOMY_LAYER_MORPHS` in
`packages/creation-suite/src/morphs.js`.

## Notes

- Layers are unions of analytic SDF primitives (capsule/ellipsoid/sphere) —
  tiny JSON, closed-form evaluation, trivially morphable.
- The pipeline auto-rectifies mesh<->skeleton Y-rotation and facing from
  bilateral joint naming; see the spec §3. Recorded in the JSON `source`.
- Proof: `roster/pantera/anatomy/` (Pantera, 2026-10-23).
