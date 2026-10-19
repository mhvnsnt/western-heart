# Mariposa — Butterfly Default (Tekken-wire attire, slot 5+)

Real pipeline-built Mariposa attire (proprietary name; "Zafina" retired).
Built 2026-10-19 inside the wired customization pipeline.

## Slotting (canon per #277, owner 2026-10-18 ~21:57 CDT)

Tekken-wire attires ladder at **slot 5+**, behind all custom Tripo-based
attires (1 Tripo default, 2 Monarch, 3 Blue Morpho, 4 Luna Moth). Canonical slot
map: `roster/mariposa/ATTIRE-SLOTS.md` (canon lane owns it — this README does
not duplicate it). This attire sits with the other Tekken-wire attires in
`roster/zafina/attires/` (Golden Pharaoh etc.), untouched by the canon merge.

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
  eyespots. Gold ring belt untouched.
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
  (suite_slots `hair`, `top`, `scarf` added), `morph_definitions`.
- `customization/decal-library/mariposa/` — swappable textures + MANIFEST.
- `customization/parts/mariposa-default/` — originals + morph definitions + MANIFEST.
- `customization/parts/tekken/tekken7-slot-catalog.json` — Mariposa attire slot entry.
- Render proofs: `docs/tpose-refs/mariposa-butterfly-default/` (front/side, locked
  orientation, own-eyes verified). Pipeline video: same dir (`pipeline.mp4`).

## Method notes (deviations from the brief)

- MPFB2/GNM: the pulled MPFB2 addon (cape-jones #128) authors targets for MPFB2 base
  meshes and GNM-shape (cape-jones #125) fits a PCA head model — neither binds
  to a Tekken Tekken-wired mesh. The morphs here are the equivalent parametric
  implementations on the real Tekken parts (same control philosophy),
  parameters recorded in the registry for suite re-application.
- Hair donor: the quaternius `Hair_Long.glb` staged by the prior lane is a broken
  GLB (texture images declared with no data → renders magenta); the new silhouette
  is built from the real T6 hair parts instead.
- Donor clothes: teardown/tekken7, tekken6, TTT2 carry no Zafina costume donor
  meshes on main — the "new clothes" are the real T6 Zafina costume parts
  reshaped/retextured (real parts, no hand-modeled guesses).
- Renders: 1024 (not 2048) — the VM (7GB RAM, load ~19, 11 concurrent Blender
  lanes) OOM-killed the 2048 renders twice; `RENDER_RES=2048` is one env var away.
  Front = lane-tool −Y convention (the wired model's facing; same as the merged
  Golden Pharaoh lane).
