# Mariposa — Butterfly Default (Slot 1)

Real default attire for Mariposa (proprietary name; "Zafina" retired).
Built 2026-10-19 inside the wired customization pipeline.

## What changed (~30%+ like Pantera's Attire 1)

- **Hair:** new dark silhouette — the real T6 hair parts reshaped
  (`hair_butterfly_silhouette`: hairtop volumized, fringe swept, sides widened,
  back swept); the long ponytail + head roses REMOVED (saved as
  `customization/parts/mariposa-default/mariposa-hair-original-opt.glb`).
  Hair repainted near-black with blue iridescent sheen + butterfly eyespots.
- **Face:** butterfly wing eyeshadow swept from the eye sockets toward the
  temples, painted on the real head diffuse; plum lips; GNM-class parametric
  face morphs baked (eyes widened, nose bridge refined, lips fuller, jaw softened).
- **Eyes:** owner's universal yellow tiger variant
  (`customization/eye-library/eye-yellow-tiger.png` → `eyes_d` 128x128).
  Original brown saved in `customization/parts/mariposa-default/`.
- **Outfit:** near-black bustier with iridescent blue/violet butterfly wings +
  eyespots (full repaint of `butterfly_d`, gold trim kept); indigo/violet
  butterfly scarf; shorts morphed into a flared mini-skirt silhouette
  (`skirt_flare`) with wing-trim hem; gloves/boots darkened with butterfly
  eyespots. Gold ring belt untouched (ties the attires together).
- **Body:** MPFB2-class parametric morph baked
  (`mpfb2_body_curvy`: hips +8.5%, waist −6%, bust +5%, height +2%;
  all 36 meshes + 246 armature bones moved by the same function so the bind
  pose stays consistent).

## Files

- `mariposa-butterfly-default.glb` — the attire (36 prims, 1 skin, rig intact)
- `README.md` — this file

## Pipeline wiring

- `customization/PARTS-REGISTRY.json` → `character_mappings.mariposa`,
  libraries `decal-library-mariposa` + `mariposa-default`, new `parts[]` entries
  (suite_slots `hair`, `top`, `scarf` added).
- `customization/decal-library/mariposa/` — swappable textures + MANIFEST.
- `customization/parts/mariposa-default/` — originals + morph definitions + MANIFEST.
- `customization/parts/tekken/tekken7-slot-catalog.json` — Mariposa attire slot entry.
- Render proofs: `docs/tpose-refs/mariposa-butterfly-default/` (front/side, locked
  orientation, own-eyes verified). Pipeline video: same dir (`pipeline.mp4`).

## Method notes (deviations from the brief)

- MPFB2/GNM: the pulled MPFB2 addon (cape-jones #128) targets MPFB2 base
  meshes and GNM-shape (cape-jones #125) fits a PCA head model — neither binds
  to a Tekken Tekken-wired mesh. The morphs here are the equivalent parametric
  implementations on the real Tekken parts (same control philosophy:
  MPFB2 bands for body, GNM-style eye/nose/mouth/face controls), with
  parameters recorded in the registry for suite re-application.
- Hair donor: the quaternius `Hair_Long.glb` the prior lane staged is a broken
  GLB (texture images declared with no data → magenta) and a cartoon part that
  clashes with the Tekken aesthetic; the new silhouette is built from the real
  T6 hair parts instead (repaired donor GLB kept in the work dir for the record).
- Renders face +Z (the wired model's facing, same as the merged Golden Pharaoh
  lane) — the "front −X" in the brief is the RigModels-rip convention, which
  the wired `zafina.glb` base does not follow.
