# Anatomy layers — proof (vega)

Generated 2026-10-31 by `tools/anatomy/generate_layers.py`.

## What was generated
Five separable volumetric layers from the rigged GLB's skeleton, stored as
unions of analytic SDF primitives in `anatomy-layers.json`.
Renders in `renders/`: `layer_bone.png`, `layer_muscle.png`, `layer_organ.png`,
`layer_fat.png`, `layer_skin.png`.

## Morph proof — `muscle_biceps_L`: 0.0 -> 1.0
- biceps.L capsule radius: 0.0565 m -> 0.08758 m (delta 0.03108 m)
- biceps.L volume: 0.003818 m^3 -> 0.010173 m^3 (+166.43%)
- baked skin displacement (whole mesh): mean 0.00091 m, max 0.03108 m
- baked skin displacement (left arm region): mean 0.00542 m, max 0.03108 m
- renders: `renders/morph_biceps_0.png` vs `renders/morph_biceps_1.png`

## Validation
- mesh<->skeleton Y rectification: 0 deg (rig front [0.0, 0.0, -1.0])
- joints inside bone layer: 218/364 (bone volumes must contain their joints)
- organs inside body: 7/7 (organ primitive centers must sit inside the body: wrapped in muscle or cradled by bone)
- morph params registered: 44
