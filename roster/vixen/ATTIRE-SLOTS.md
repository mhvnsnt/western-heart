# MENAJERII — Attire Slots

**Fighter:** MENAJERII (メナジェリー, The Menagerie Soul) · **Roster dir:** `roster/vixen/`
**Display order law:** Tripo/SmutBase originals first; Tekken reskins ladder behind
as back-slot attires. (No Tekken reskin exists for Menajerii yet.)

## Slots

| Slot | Name | Model | Status |
|---|---|---|---|
| A1 | Menagerie Garb (default) | `attires/attire1/model.glb` | ✅ wired — MODEL_URLS `menajerii`, `menajerii-attire1` |

## Provenance — Attire 1

- **Source:** SmutBase commission "Vixen" intake (landed 2026-10-22;
  `roster/vixen/intake/README.md`). Injustice 2-based, Blender 4.02, fully
  rigged GZM widget rig + body morphs, Genesis-family; 88 objects; clothing as
  separate modeled geometry.
- **Intake GLB:** `vixen-full.glb` (629.7 MB, 29 meshes) — exceeds the git
  blob API limit.
- **In-repo build:** `attires/attire1/model.glb` — meshopt-compressed
  (geometry) + WebP textures capped at 2048px: **629.7 MB → 41.7 MB**,
  validated clean (`gltf-transform validate`). Rig lane: GZM/Genesis-family
  rig — evaluate against the Lily-donor female rig when Blender is available.
- **Original archived:** release [`megami-menajerii-smutbase-20261023`](https://github.com/mhvnsnt/western-heart/releases/tag/megami-menajerii-smutbase-20261023)
  (immutable intake GLB).
- **Parts:** `roster/vixen/PARTS.md` — full 29-mesh inventory with
  creation-suite labels.

## Moveset directive (recorded, owner's saved directive)

Her source game was Injustice 2 — her moveset was built **fresh with TEKKEN
inputs** in `game/assets/movesets/menajerii.json`; the source game's input
system was NOT reused. Moveset source: Roger Jr. (Tekken) kit.

## Canon

`roster/vixen/CANON.md` — MENAJERII, the Menagerie Soul: spirit-walker carrying
beast spirits; sanctuary at Birodo's club; her shadow doesn't always match
her body.
