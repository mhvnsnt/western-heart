# Anatomy layers — proof (diablo)

Generated 2026-10-31 by `tools/anatomy/generate_layers.py`.

## What was generated
Five separable volumetric layers from the rigged GLB's skeleton, stored as
unions of analytic SDF primitives in `anatomy-layers.json`.
Renders in `renders/`: `layer_bone.png`, `layer_muscle.png`, `layer_organ.png`,
`layer_fat.png`, `layer_skin.png`.

## Morph proof — `muscle_biceps_L`: 0.0 -> 1.0
- biceps.L capsule radius: 0.052 m -> 0.0806 m (delta 0.0286 m)
- biceps.L volume: 0.001272 m^3 -> 0.003835 m^3 (+201.41%)
- baked skin displacement (whole mesh): mean 0.00042 m, max 0.0286 m
- baked skin displacement (left arm region): mean 0.01055 m, max 0.0286 m
- renders: `renders/morph_biceps_0.png` vs `renders/morph_biceps_1.png`

## Validation
- mesh<->skeleton Y rectification: 270 deg (rig front [0.0, 0.0, -1.0])
- joints inside bone layer: 14/53 (bone volumes must contain their joints)
- organs inside body: 7/7 (organ primitive centers must sit inside the body: wrapped in muscle or cradled by bone)
- morph params registered: 44
