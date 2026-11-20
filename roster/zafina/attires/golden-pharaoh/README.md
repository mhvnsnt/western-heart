# ZAFINA — "Golden Pharaoh" (Attire 1, owner 2026-10-18)

Custom colorway reskin of Zafina's Tekken 6 outfit
(`game/assets/models/zafina.glb`, 2 meshes / 38 materials / 101 embedded images).

## What changed (texture-only — rig and geometry untouched)

- **Butterfly top pink/magenta → metallic gold** (`butterfly_d`): wing fill
  remapped to gold preserving luminance; navy base deepened to rich black.
  Purple accent dots kept as lapis-style contrast.
- **Kept**: teal sheer scarf (Egyptian faience accent), pale-blue shoulder roses,
  black shorts, gold ring belt, white thigh-high boots with black rose vines,
  red earring jewels, belly-chain with red drop, black hair, skin.
- **Eyes**: owner's universal "I like" yellow tiger eye applied
  (`customization/eye-library/eye-yellow-tiger.png`, native 128).
  Her original dark-brown eyes saved as a swap option in
  `customization/parts/zafina-eyes/`.

The palette — gold + lapis blue + faience teal + black — is the classic
Egyptian royal combination, fitting her Egyptian theme.

## Swapping back / options

- Original pink butterfly texture: `customization/decal-library/zafina/`
  (`top-pink-original.png`, `replaces_texture: butterfly_d`).
- Eye options: `customization/parts/zafina-eyes/` (original dark brown) and the
  universal `customization/eye-library/` (yellow tiger applied).
- Re-embed any option PNG as the named texture in this GLB — no geometry change.

## Renders

`docs/tpose-refs/zafina-golden-pharaoh/` — front + side, locked orientation
(model authored facing -Y; rendered with the faceY variant so front faces -X,
ortho, 2048, white). Verified with own eyes 2026-10-18.

## Source

Built 2026-10-18 from `game/assets/models/zafina.glb` (main).
Base model untouched on main — this GLB is an addition, not a replacement.
