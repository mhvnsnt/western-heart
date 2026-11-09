# MEGAMI — Attire Slots

**Fighter:** MEGAMI (The Shrine Soul) · **Roster dir:** `roster/parvati/`
**Display order law:** Tripo/SmutBase originals first; Tekken reskins ladder behind
as back-slot attires. (No Tekken reskin exists for Megami yet.)

## Slots

| Slot | Name | Model | Status |
|---|---|---|---|
| A1 | Shrine Regalia | `attires/attire1/model-rigged.glb` | ✅ wired — MODEL_URLS `megami-attire1` (fidelity rebuild, 2026-11-05) |
| A2 | Roses & Bows default (BASE DEFAULT — owner pick 2026-11-08) | composed via `customization/profiles/megami.json` | ✅ pieces + Flora registered individually (library `megami-default`); composed single-GLB export pending a quiet-VM window — see Provenance A2 |
| A1-alt | No-outfit variant (WH #1549) | `attires/attire1/model-rigged-nooutfit.glb` | on disk as a named option — not wired |
| A1-master | Blend master (not a playable slot) | `attires/attire1/model-blend-master.glb` | full rig + all objects from the source blend |

## Provenance — Attire 1 (fidelity rebuild, 2026-11-05)

- **Rebuilt from the recovered commission blend**
  (`ParvatiCommission.blend`, byte-identical to the lost original;
  recovery WH #1575) by `tools/anim/export_megami_fidelity.py`:
  full 469-bone GZM rig, all 474 shape keys as morph targets, her
  textured steampunk outfit as authored in the blend. The blend's
  view layer excludes the author's alternate wardrobe collections
  (Wearables 1/2/3, Hair 2, Public Hair) — those 17 objects ship
  in the master only, per the author-hidden precedent.
- **The 2026-10-23 note below predates the rebuild:** the
  "textureless outfit" verdict described the stripped conversion,
  not the source — in the blend the outfit is fully textured.
  Full detail: `docs/handoffs/SMUTBASE6-FIDELITY-2026-11-04.md`
  (MEGAMI REBUILD section). Full-res master on release
  `megami-menajerii-smutbase-20261023` (`megami-master-packed.glb`).

## Provenance — Attire 1 (2026-10-23 intake, superseded)

- **Source:** SmutBase commission "Parvati" intake (landed 2026-10-22;
  `roster/parvati/intake/README.md`). Blender 4.02, GZM widget rig,
  Genesis-family; 90 objects; clothing as separate modeled geometry.
- **Intake GLB:** `parvati-full.glb` (191.6 MB, 25 meshes) — exceeds the git
  blob API limit.
- **In-repo build:** `attires/attire1/model.glb` — meshopt-compressed
  (geometry) + WebP textures capped at 2048px: **191.6 MB → 23.5 MB**,
  validated clean (`gltf-transform validate`). Rig lane: GZM/Genesis-family
  rig — evaluate against the Lily-donor female rig when Blender is available.
- **Original archived:** release [`megami-menajerii-smutbase-20261023`](https://github.com/mhvnsnt/western-heart/releases/tag/megami-menajerii-smutbase-20261023)
  (immutable intake GLB).
- **Parts:** `roster/parvati/PARTS.md` — full 25-mesh inventory with
  creation-suite labels.
- **Parvati UDIM quirk:** Torso-3 UVs at U 1.03–2.67 (unbaked UDIM) —
  invisible under the bodystocking; noted for the texture lane.

## Canon

`roster/parvati/CANON.md` — MEGAMI, the Shrine Soul: temple guardian of a
sealed door; trained Chatur; grief in motion.
*"The shrine was here before you. It will be here after."*

## Provenance — Attire 2 (owner-picked base default, 2026-11-08)

- **Owner decision (2026-11-08):** the composed look in
  `parvati-look-rosesbows-nobra-choker-flora-gauntletblack-20261108.png`
  (workspace `_parvati-redress-20261107`) IS her base default attire:
  Roses & Bows **Pantie 3 + garter Belt + Stocking (bra REMOVED by owner
  order)**, **Sugar choker**, **Flora hair** (her main default hairstyle,
  confirmed 2026-11-08), **black-panel gauntlets**, on the fixed v4
  base/skin. Shoe slot open (owner picking). Eyes: yellow tiger (owner
  pick 2026-11-08, registered as `megami-eye-yellow-tiger`).
- **Pieces landed individually** (all-items order) under
  `customization/parts/megami-default/` — Flora (23-joint rig: neck/head +
  19 hair bones, 10 spring-bone chains), pantie, garter belt, stockings,
  choker, gauntlets — each exported from the fixed blend
  (`Parvati-basefix.blend`), registered in PARTS-REGISTRY + suite catalog
  + create-fighter index, and composed by `customization/profiles/megami.json`.
- **Pending:** the composed one-file `attires/attire2/model-rigged.glb`
  export OOMs on this 8 GB VM (474 shape keys; two attempts killed) —
  until it lands in a quiet window, MODEL_URLS `megami` stays on attire1
  and A2 is carried by the profile composition above. Not a silent gap:
  tracked in `customization/HAIR-WIRING-STATUS-2026-11-08.md`.
