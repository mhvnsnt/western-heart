# MEGAMI — Attire Slots

**Fighter:** MEGAMI (The Shrine Soul) · **Roster dir:** `roster/parvati/`
**Display order law:** Tripo/SmutBase originals first; Tekken reskins ladder behind
as back-slot attires. (No Tekken reskin exists for Megami yet.)

## Slots

| Slot | Name | Model | Status |
|---|---|---|---|
| A1 | Shrine Regalia (default) | `attires/attire1/model-rigged.glb` | ✅ wired — MODEL_URLS `megami`, `megami-attire1` (fidelity rebuild, 2026-11-05) |
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
