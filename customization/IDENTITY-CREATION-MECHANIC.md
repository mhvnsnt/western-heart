# Identity Creation Mechanic — creation suite wiring

**What this is:** the in-game side of the face/body creation system that
is built and proven in the Physique Lab repo. One system, two homes,
shared data formats (`face-params/v1`). Naming in this repo is
in-universe only.

## The mechanic

1. **Photo/video → face.** Landmark tracking (MediaPipe Face Landmarker,
   Apache-2.0) → parametric measurement (`face-params/v1`, 23 named face
   parameters) → shape keys on the target head. The fit is judged on a
   matched camera plus the owner's at-a-glance test (see
   MODEL-TWEAKING-PRINCIPLES.md #5).
2. **Full manual customization.** Every measured face region plus the
   full body parameter set (leg length as the height carrier, torso,
   shoulders, hips, waist, bust, glutes, muscle, mass) as named sliders
   in the creation suite UI — the same parameter names as the schema.
3. **Export.** GLB + morph data in the customization formats already
   used by this repo (`customization/CUSTOMIZATION-JSON-SCHEMA.md`).
5. **Expression & motion signature.** Likeness includes how the person
   moves: mouth shapes through speech, brow/eye movement, characteristic
   expressions, head motion while talking. Tracked video (the same
   licence-clean landmark chain) is mapped into the parametric
   expression space and stored as a per-character expression/talk
   animation set. Expression data stays separate from the neutral
   identity fit and is never flattened into it.

4. **Licence rule.** The measurement/fit chain is licence-clean only:
   MediaPipe + a house shape basis built from this project's own roster
   heads + Blender. FLAME / SMPL / BFM / DECA-family components are
   banned anywhere in the chain, including as a measurement front-end —
   the full evidence table lives with the face-from-photo plan in the
   Physique Lab repo.

## Wiring state in this repo (2026-11-08)

- WIRED: measurement engine (`customization/face-measure/`), the
  face-params/v1 schema, the model-tweaking principles.
- NOT BUILT: the parametric fitter, the expression-signature mapper,
  the
  matched-camera gate harness, the creation-suite identity slider UI,
  GLB/morph export from the panel. These are logged gaps in the
  Physique Lab survey doc; no hand-tooled substitute stands in for any
  of them.
