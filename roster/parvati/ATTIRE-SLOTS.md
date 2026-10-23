# MEGAMI — Attire Slots

**Fighter:** MEGAMI (The Shrine Soul) · **Roster dir:** `roster/parvati/`
**Display order law:** Tripo/SmutBase originals first; Tekken reskins ladder behind
as back-slot attires. (No Tekken reskin exists for Megami yet.)

## Slots

| Slot | Name | Model | Status |
|---|---|---|---|
| A1 | Shrine Regalia (default) | `attires/attire1/model.glb` | ✅ wired — MODEL_URLS `megami`, `megami-attire1` |

## Provenance — Attire 1

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
