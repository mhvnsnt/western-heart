# SILVERTONGUE — "Spy Debut" (Slot 1 default attire, owner 2026-10-18)

Her REAL default attire — built to the ~30%+ change bar (Pantera Attire 1).
007-villain old-school female honeypot: seductive spy, not formal gown.

Built from `game/assets/models/lili.glb` (main) inside the Creation Suite
pipeline (`packages/creation-suite`, `customization/PARTS-REGISTRY.json`).

## What changed (vs the T7 1P formal base)

**Geometry (real mesh surgery, rig intact):**
- Blonde DRILL ROLLS removed (2 meshes) — new sleek hair silhouette.
- Full formal gown removed: skirt (2), lower frills (2), upper tie frills (2),
  lace trim (2).
- Tiara removed. Corsage flower removed (4).
- 15 meshes deleted total (45 → 30). Nothing else touched.

**Face (007 makeup on the real head diffuse `T_CH_lil_face_D`):**
- Smoky charcoal eyeshadow, winged eyeliner, beauty mark, cheek contour,
  deepened lips. Lip mesh (`T_CH_lil_lip_D`) → deep spy red.
  Brows (`T_CH_lil_eyebrow_D`) → darker, defined.

**Outfit (luminance-preserving retextures — shading/wrinkles kept):**
- Jacket → black leather spy jacket (`T_CH_lil_bdu_1p_old_jacket_D`).
- Blouse front → black silk (`T_CH_xia_bdu_formal_A_D`).
- Bow tie → black silk (`ky_02_00`).
- Shorts → black spy shorts (`T_CH_lil_bdl_1p_old_pants_etc_D`).
- Boots → black patent (`T_CH_lil_bdl_1p_old_boots_D`).
- Gloves → black opera gloves (`T_CH_lil_bdu_1p_old_glove_D`).
- Lace trim → black (`T_CH_lil_bdu_1p_old_lace_D`).
- Hardware → gunmetal (`T_CH_lil_bdu_1p_old_metallic_D`).

**Eyes:** owner's universal "I like" yellow tiger eye applied
(`customization/eye-library/eye-yellow-tiger.png`, upscaled 128→256 LANCZOS
for `T_CH_eye_D`). Original blue-gray saved in `customization/parts/lili-eyes/`.

**Body (MPFB2, real pipeline — cape-jones PR #128):**
- `spy_athletic` morph: slimmer waist (`measure-waist-circ-decr` 0.85),
  toned stomach (`stomach-tone-incr` 0.55, `stomach-navel-in` 0.45),
  slightly taller (height macro 0.35). KD-tree transferred from the MPFB2
  human onto Lili's body + all garments (so clothes follow), baked.

**Face shape (GNM semantics — cape-jones PR #125):**
- Cheekbone definition, nose-bridge narrowing, jaw sharpening as subtle
  parametric transforms (the GNM source pull has an empty shape dir, so the
  rig itself is not fittable to Lili — control semantics honored; see PR
  Deviations).

## Restoring / swapping (nothing overwritten)

Every original is saved as a swap option in
`customization/parts/silvertongue-default/` (MANIFEST.json):
- `face-original.png`, `lip-original.png`, `eyebrow-original.png`
- `hair-original.png` + `drill-hair-tiara-corsage.glb` (restorable meshes)
- `jacket-original.png`, `pants-original.png`, `boots-original.png`,
  `glove-original.png`, `lace-original.png`, `blouse-original.png`,
  `bowtie-original.png`, `metallic-original.png`
- Re-embed any PNG as the named texture, or re-attach the drill GLB, to restore.

## Renders / video

- `docs/tpose-refs/silvertongue-spy-debut/` — front + side, locked
  orientation (front camera -X, ortho, 2048, white). Own-eyes verified.
- `docs/tpose-refs/silvertongue-spy-debut/customization-video.mp4` —
  the customization happening in the pipeline, step by step.
- Picker UI (tap-to-assign, phone-first, no drag-and-drop):
  `packages/creation-suite/proof/silvertongue-picker.html`.

## Source

Built 2026-10-18 from `game/assets/models/lili.glb` (main).
Base model untouched on main — this GLB is an addition, not a replacement.
Tripo generation was not available for this lane — no Tripo model attached;
per registry law a future Tripo main takes Slot 1 and this shifts to Slot 2.

<!-- instruction-gate trigger -->
