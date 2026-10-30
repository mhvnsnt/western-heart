# Gyou Spirit Body — Archive Manifest

**Archived:** 2026-10-22 (worker 84)
**PR branch:** `archive/gyou-spirit-body-20261022`
**Restore tag:** `gyou-spirit-body-original` (annotated; message: "Restore point: these bytes never change")
**Auto-archive standing directive:** archive-only, NOT wired into MODEL_URLS
  (unrigged static — rig/anim lanes pick it up from this folder).

## Source files (byte-identical to Tripo intake)

| File | Bytes | SHA-256 |
|------|-------|---------|
| `source/fiery_humanoid_3d_model.glb` | 26875868 | `a1bd1432bee1bf2c969a8914338c0e3a2517c4c007dd0ca15b555fb55d5114df` |
| `source/fiery_humanoid_3d_model.manifest.json` | 1477 | (Tripo staging manifest, copied verbatim) |

## Tripo origin

- **Project:** fiery humanoid 3d model (`fiery_humanoid_3d_model`)
- **Project UUID:** `ea370b21-78eb-4cc4-a5a6-4c4452243182`
- **Share URL:** https://studio.tripo3d.ai/3d-model/ea370b21-78eb-4cc4-a5a6-4c4452243182
- **Owner:** `deeroyal1468`
- **Resolved via:** public-api
- **Staging path:** `/home/hatch/workspace/tripo-staging/gyou/spirit-body/fiery_humanoid_3d_model.glb`

## Verification

- Magic: `glTF` (ASCII glTF at offset 0), 26,875,868 bytes staged and archived.
- SHA-256 re-verified at archive time (see table above).
- Structure: unchecked at archive (pygltflib not installed on VM) — same
  as the staging manifest recorded.

## Canon context

- Gyou = one of the two unvesseled Nine Souls (selectable spirit fighter,
  per the 2026-10-22 23:02 Nine Souls redesign).
- Canon: **Flame Lord (Flaming Angel)**.
- This is the **spirit body**; it archives alongside the existing
  `roster/gyou/attires/spirit-form/` (spirit form attire) as the fighter's
  spirit-body source.
- Future lanes (documented in `SPEC.md`, not built): aggressive/sporadic
  spirit-float behind the spirit body (Zen-like setup, Gyou intensity);
  various transformations; giant Susanoo form with levels/transformations.

## Usage rule

These bytes are immutable. Any rig/anim derivative goes in a NEW file
(e.g. `model-rigged.glb`) — never overwrite `source/`.
