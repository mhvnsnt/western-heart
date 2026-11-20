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

## Fidelity rebuild (2026-11-05, SmutBase 6 fidelity order)

- **A1 model replaced in place:** `attires/attire1/model-rigged-noplane.glb`
  is now the rebuild from the recovered commission blend
  (`VixenCommission.blend`, sha256
  085d914c6539e0bef89f881ba6887336a1d93115ee6bef792161ec737c375670):
  the full 450-bone GZM rig by modifier reference, 932 shape keys in
  the authored-look set, her cheetah suit + hair + necklace as the
  blend's view layer saves them. The #780 crew file
  (`model-rigged.glb`) and the intake build (`model.glb`) stay on
  disk untouched as the earlier named options.
- **Master:** the full blend export (451 joints incl. the
  exporter's neutral_bone, all 2,509 shape keys, every
  polygon-bearing object) exceeds GitHub's 100 MB per-file limit
  even with textures capped at 1024 px (114,293,416 B), so both
  master builds live on release
  [`megami-menajerii-smutbase-20261023`](https://github.com/mhvnsnt/western-heart/releases/tag/megami-menajerii-smutbase-20261023):
  `menajerii-master-capped1024.glb` (114,293,416 B, sha256
  07b5428ea31f09c457825e5910f85128420012ec70eaba81c9443b171333bb20)
  and `menajerii-master-packed.glb` (493,068,228 B, uncapped
  textures, sha256
  e4a425cc2ccc4260d730ccf39095a13803bcd4a550a85757e5af916c0248526e).
  The source blend remains the full record, on the same release
  as parts (recovery #1575).
