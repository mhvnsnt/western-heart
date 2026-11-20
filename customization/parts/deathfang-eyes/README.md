# DEATHFANG — eye repair patches (owner Tripo Attire 1)

The owner's Tripo human model (`6486151e`, Attire 1 "prisoner with chains")
shipped with a defect: the open eye had NO eyeball painted — the atlas held a
closed, skin-pink eyelid at the eye's UV island (the other eye is covered by
hair, by design, and was left alone). The werewolf form's eyes are correct and
were not touched.

## The fix (2026-10-20)

A real open eye — white sclera, crimson striated iris, pupil, highlights, dark
lash rim — composited into the 4096×4096 color atlas at the eye island.

- Verified diff region (original atlas vs fixed atlas): x 1707–1782,
  y 3739–3848 px (glTF UV V is top-down: pixel row = v × 4096). Only the eye
  island changed; the GLB geometry is byte-identical to the owner's pull.
- Files here: `eye-patch-before.png` (the defect, texture-space crop) and
  `eye-patch-after.png` (the painted eye, same crop).
- Render proof: `deathfang-eye-fix-closeup-20261020.png` (owner deliverable).

Registered in `customization/eye-library/MANIFEST.json` under
`character_mappings.deathfang` so the eye is a normal customization-library
application, re-appliable if the model is ever re-pulled.
