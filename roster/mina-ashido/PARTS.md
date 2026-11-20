# RYUSAN — Parts Documentation

**Model:** `roster/mina-ashido/attires/attire1/model.glb` (4.4 MB, SmutBase Mina Ashido intake → WH name RYUSAN)
**Status:** unrigged static (0 skins, 0 animations in GLB) — rig queued, same path as other SmutBase intakes.
**Coordinate note:** Z-up in this GLB; character ~6 units tall (feet z≈0, head z≈6).
**Naming note:** mesh names are Blender defaults from the source rip (`Circle`, `Cube`, `Fur`…). Categories below are assigned by bounding-region analysis against the body mesh; confidence is noted per part. This is the foundation for the creation-suite clothing system — every swappable part is separable geometry.

## Part list

| # | Mesh name | Prims | Verts | Category | Swappable | Description |
|---|-----------|-------|-------|----------|-----------|-------------|
| 1 | `mina` | 1 | 88,176 | full-body | No (base) | Main body mesh — torso, arms, legs, head base. The skin/body foundation everything else layers over. |
| 2 | `Hair` | 1 | 15,642 | hair | Yes | Hair mass (head-top region, z 5.15–6.32). High confidence — position + volume match the head. |
| 3 | `horns` | 1 | 1,104 | accessories | Yes | Head horns (z 5.94–6.27, top of head). High confidence. |
| 4 | `Fur` | 29 | ~13,700 | accessories | Yes | Fluffy trim pieces across torso/arms (collar + cuffs). 29 primitives, two materials (`body`/`eyes`). Medium-high confidence — matches the hero outfit's fluffy trim. |
| 5 | `Circle` | 4 | 4,152 | accessories | Yes | Neck collar ring (z 4.21–5.15, x ±0.72 — neck height). Medium confidence — ring geometry at the neck. |
| 6 | `Cube` | 24 | ~3,000 | footwear | Yes | Boots — 24 mirrored primitives at leg height (z 0.07–1.10, mirrored ±x pairs). High confidence — mirrored leg-region placement. |
| 7 | `Mesh0000_000` | 1 | 30,708 | tops | Yes | Hero top, front torso panel (x ±0.25, front y −1.38…−0.42, z 2.70–3.32). Medium confidence — torso-front overlay region. |
| 8 | `Plane_001` | 1 | 15,836 | bottoms | Yes | Lower-body garment region (x ±0.96, z 0.92–4.72, waist-to-chest span). Medium confidence — covers hip/waist zone. |

## Layer order (outer → inner)

1. `horns`, `Hair` (head)
2. `Circle` (neck), `Fur` (trim)
3. `Mesh0000_000` (top), `Plane_001` (bottoms)
4. `Cube` (boots)
5. `mina` (body base)

## Materials

Two materials in the GLB: `body`, `eyes`. Full PBR texture set archived alongside the source at `roster/mina-ashido/intake/` (`Mina-hero-outfit_*`, `mina body.png`).

## Creation-suite notes

- 7 of 8 meshes are swappable clothing/accessory/hair parts; only `mina` (body base) is fixed.
- No underwear meshes are separately modeled in this GLB — underwear would need to be authored or derived from the body base.
- Gloves: none separately modeled (hands are part of the `mina` body mesh).
- Headwear: none (horns are accessories, not headwear).
- The `Fur` trim (29 prims) should be treated as ONE logical accessory part in the suite UI, not 29 pieces.
