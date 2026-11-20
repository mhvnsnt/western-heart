# Creation Suite — Pipeline Wiring (2026-10-18)

How every system plugs into Western Heart's Create Fighter suite. Additive; nothing existing is touched.

## 1. Parts library (wired)

| Source | Count | Status |
|---|---|---|
| wm xix / no-mercy teardown wearables | 1,102 | `customization/PARTS-REGISTRY.json` (geometryPending — ymg/no-mercy binaries decode to GLB before in-engine use) |
| Universal CC0 hair | 9 | `customization/parts/hair/cc0/` — real GLB/glTF, Quaternius CC0-1.0 + tiko479 CC0 |
| Eye/decal/superhero libraries | 17 | already on main |
| **Total registry parts** | **1,128** | |

Every mesh part carries `socket` + `bone_aliases` + `offset/rotation/scale` + `editable`
per `customization/CUSTOMIZATION-LIBRARY-LAYOUT.md` (the universal format:
texture-swap parts composite into a rect; mesh parts attach at bone sockets).
Indexes: `customization/parts/PARTS-INDEX.json` (3,398) and the UI copy at
`customization/create-fighter/data/PARTS-INDEX.json` (3,398).

## 2. Slot schemas (Tekken 6 + TTT2 + T7)

- `customization/parts/tekken/tekken6-slot-catalog.json` — 4 slots
  (Head / Upper Body / Lower Body / Other), from the on-disk T6 TEARDOWN.md
  research doc (PSP archives still encrypted; slot design is public-doc sourced).
- `customization/parts/tekken/ttt2-slot-catalog.json` — extends T6 (120+ attires,
  Combot reference); both carry `t7_slot_map` cross-compat to the T7 schema.
- `customization/parts/tekken/tekken7-slot-catalog.json` (on main) — 17 slots.

## 3. Body morphs — MPFB2

`customization/body-morphs/MANIFEST.json` — 13 macro morphs (height, bulk, muscle,
fat, shoulders, belly, limbs, chest, waist, hips, neck, hands, feet) + 12 face-shape
morphs (eyes/nose/mouth/face shapes), each mapped to real MPFB2 target paths.

- Upstream: `makehumancommunity/mpfb2` v2.0.18, pulled into
  `mhvnsnt/cape-jones` `production/tools/mpfb2` (PR #128 merged); code GPL-3.0,
  targets/data CC0-1.0. Headless recipe: `production/tools/mpfb2/WIRING.md`.
- Bake: `customization/body-morphs/apply_mpfb_morphs.py` (headless Blender) —
  transfers MPFB target deltas onto any suite GLB via KD-tree nearest-surface
  mapping (same transfer as `mpfb_wire_cj.py`), baking `MPFB_<id>` shape keys.
- Front end: `packages/creation-suite/src/morphs.js` (`BODY_MORPHS`,
  `FACE_SHAPE_MORPHS`, `blendMorphs`, `applyMorphProxies`).

## 4. Face morphs — GNM

`customization/face-morphs/MANIFEST.json` — 20 semantic params
(eyes/brows/mouth/tongue/iris) + 21 presets, ported verbatim from
`mhvnsnt/cape-jones` `3d-assets/face-rig/cj_face_presets.py` (PR #125 merged).

- Upstream: Google GNM Head (Apache-2.0): 383-param expression basis
  (100/eye, 150 lower face, 32 tongue, 1 iris) + CVAE semantic sampler;
  GNM ships no brow basis — brows are our add-on.
- Front end: `packages/creation-suite/src/facemorphs.js`
  (`FACE_PARAMS`, `FACE_PRESETS`, `presetVector`, `blendPresets`,
  `applyFaceParams`).

## 5. Layering rules — WWE 2K CAW

`packages/creation-suite/src/layering.js` — WWE 2K19 CAW rules from the on-disk
plan (`customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`; 2K19/2K18 game files are
NOT on disk, so the layering is pipeline rules, not extracted assets):
layer order, per-region multi-stack, left/right independence, mirror-attire,
per-item color channels, Tekken slot-conflict merge.

## 6. Front end

`customization/create-fighter/` — Tekken-style pickers (category tabs, item
grids, color swatches, slot conflict rules). **TAP-TO-ASSIGN**: tap/scroll the
library and tap to assign. **NEVER drag-and-drop.** Phone-first. Live preview
(`preview3d.js`) wired to the pipeline swap functions.

## 7. Proof

Video render of the pipeline in action (browse → tap-to-assign → morphs →
character transforming), own-eyes verified before shipping.
