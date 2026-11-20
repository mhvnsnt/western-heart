# BAEK — "Master's White" (Attire 1, owner 2026-10-18)

Custom colorway reskin of Baek's dobok (`game/assets/models/baek.glb`,
35 meshes / 35 materials / 35 embedded JPEG images). Baek's FIRST custom
Western Heart look — **The Master Soul** in a crisp white dobok with
Western Heart dark-red trim.

## What changed (texture-only — rig and geometry untouched)

- **Dobok cream → crisp white**: all dobok body fabric (`pek1u_0/30/10/9/4`)
  and dobok back panels (`pek1u_8/6/5`). Wrinkle shading preserved —
  luminance remap only.
- **Trim black → Western Heart dark red**: collar trim, sleeve cuffs, jacket
  hem, jacket front tabs (`pek1u_1`, `pek1u_25`), and the red collar lining
  (`pek1u_32`, `pek1u_27`).
- **Kept**: the master's **black belt** (`pek1u_3` band, `pek1u_28` tips —
  identified with a diagnostic solid-color render and deliberately excluded
  from the recolor), red KOREA chest/back logos, black han character, skin,
  hair, teeth.
- **Eyes**: default brown eyes kept. The owner's universal "I like" yellow
  tiger eye is saved as a swap **option** (not applied) in
  `customization/parts/baek-eyes/`.

## Swapping / options

- Full option library: `customization/decal-library/baek/` — every recolored
  texture has a `dobok-original-*` restore counterpart, plus the
  **Fallen Master** option set (`dobok-fallenmaster-*`: near-black dobok,
  oxblood trim, silver han).
- Eye options: `customization/parts/baek-eyes/` (original brown + universal
  yellow tiger).
- Re-embed any option PNG as the named texture in this GLB — no geometry change.

## Method

Luminance-preserving colorize per texture (shading/wrinkles kept), re-embedded
via buffer rebuild (4-byte aligned, all offsets rewritten; 35 images /
35 materials / 35 meshes verified intact).

The original build is untouched at `game/assets/models/baek.glb` (also in
git history).

## Render proof

`docs/tpose-refs/baek-master-white/front.png` + `side.png` — T-pose front/side,
locked orientation method (`docs/RENDER-ORIENTATION.md`: front camera on -X,
ortho, 2048x2048, white background, ortho_scale = 1.12 x max(span)).
Own-eyes verified: white dobok, dark-red trim, black belt, han readable,
face front.
