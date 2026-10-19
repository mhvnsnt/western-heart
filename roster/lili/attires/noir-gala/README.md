# LILI — "Noir Gala" (Attire 1, owner 2026-10-18)

Custom colorway reskin of Lili's Tekken 7 1P formal outfit
(`game/assets/models/lili.glb`, 45 meshes / 45 materials / 73 embedded images).

## What changed (texture-only — rig and geometry untouched)

- **Dress white/cream → deep black**: jacket, skirt, frills, lace, underskirt
  (`T_CH_lil_bdu_1p_old_jacket_D`, `T_CH_lil_bdl_1p_old_skirt_D`,
  `T_CH_lil_bdl_1p_old_frill_D`, `T_CH_lil_bdu_1p_old_lace_D`,
  `T_CH_lil_bdl_1p_old_pants_etc_D`, `T_CH_xia_bdl_formal_B_D`).
  Wrinkle shading and stitching preserved — only near-white fabric pixels remapped.
- **Boots + gloves white → black** (`T_CH_lil_bdl_1p_old_boots_D`,
  `T_CH_lil_bdu_1p_old_glove_D`).
- **Kept**: red diamond-check bow tie, red boot/glove trim, gold buckles,
  silver tiara + medallion, pearl necklace, purple corsage flower,
  blonde drill hair, skin.
- **Eyes**: owner's universal "I like" yellow tiger eye applied
  (`customization/eye-library/eye-yellow-tiger.png`, resized to 256).
  Her original blue-gray eyes saved as a swap option in
  `customization/parts/lili-eyes/`.

## Swapping back / options

- Full original white dress textures: `customization/decal-library/lili/`
  (each noir texture has a `dress-white-original-*` restore counterpart).
- Eye options: `customization/parts/lili-eyes/` (original blue-gray) and the
  universal `customization/eye-library/` (yellow tiger + others).
- Re-embed any option PNG as the named texture in this GLB — no geometry change.

## Renders

`docs/tpose-refs/lili-noir-gala/` — front + side, locked orientation
(front camera -X, ortho, 2048, white). Verified with own eyes 2026-10-18.

## Source

Built 2026-10-18 from `game/assets/models/lili.glb` (main).
Base model untouched on main — this GLB is an addition, not a replacement.
