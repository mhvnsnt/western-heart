# Skeleton Variant System — Implementation Spec 2026-10-23

**Owner directive:** Some fighters have non-human skeletons (extra arms, different skulls, etc.). Build a variant skeleton system — base human skeleton + modular additions.

**Base:** WH-Canonical-22 (22 bones, from `lab/skeleton/canonical_skeleton.json`)

## Module catalog

| Module | Root joint | Bones added | Used by |
|--------|-----------|-------------|---------|
| QUADARM | Chest | `Shoulder2.L/R → Arm2.L/R → ForeArm2.L/R → Hand2.L/R` | Chatur, DXMMII |
| JAW | Head | `Jaw` | Dorowani |
| TAIL | Hips | `Tail1 → Tail2 → Tail3 → TailTip` | Dorowani |
| WING | Chest | `WingRoot.L/R` + 3-4 digit chains per wing | Demonio |
| BATHAND | Hand.L/R | `ExtraPalm` + 3 fingers × 3 segments | Demonio |
| TENTACLE | Spine (top) | Per-tentacle chain ×N | Zen |
| SPINESEGS | Hips | Segmented vertebrae (replaces single Spine) | Gashadokuro |

## Naming convention

`WH-Canonical-22+<MODULES>` — e.g.:
- Chatur: `WH-Canonical-22+QUADARM`
- Dorowani: `WH-Canonical-22+JAW+TAIL`
- Demonio (winged): `WH-Canonical-22+WING+BATHAND`

## Anatomy layer generation for variants

`tools/anatomy/generate_layers.py` positions primitives from rig joints (no hand-tooled coordinates). For variants:

### QUADARM (extra arms)
- Generate arm bone capsules for `Arm2`, `ForeArm2` chains
- Generate arm muscle groups (biceps2, triceps2, forearm2)
- Position from the extra shoulder/arm joint positions

### JAW (Dorowani)
- Generate jaw bone (mandible) as ellipsoid positioned from Jaw joint
- Jaw muscle (masseter) as capsule

### TAIL (Dorowani)
- Generate tail bone capsules for `Tail1→Tail2→Tail3→TailTip`
- Generate tail muscle as tapered capsules

### WING (Demonio)
- Generate wing bone structure (elongated digit chains)
- Wing membrane as thin ellipsoid (or skip — membrane is skin-level)

### TENTACLE (Zen)
- Per-tentacle: generate as flexible capsule chain
- Count N determined at rig stage

## X-ray integration

The X-ray system (`game/js/xray.js`) reads `anatomy-layers.json` which includes the skeleton. Variant skeletons automatically work because:
1. `generate_layers.py` generates primitives from actual joint positions
2. `parseAnatomyLayers()` reads whatever primitives exist
3. No hardcoded bone names in the X-ray renderer

## Implementation status

- [x] Variant spec (this doc)
- [x] Module catalog
- [ ] `generate_layers.py` variant support (next PR)
- [ ] Per-fighter variant layer generation (after rigs land)
- [ ] X-ray verification with variant skeletons

## Validation

Every variant must pass existing gates:
- Base `required_for_rig_check` bones present
- `anim_check.py`: bone-var <2%, no tearing, edge-stretch p99.9 <2.5x
- Module chains validated additively
