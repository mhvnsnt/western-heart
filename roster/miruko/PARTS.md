# TOBI — Parts Documentation

**Model:** `roster/miruko/attires/attire1/model.glb` (5.6 MB, SmutBase Mirko/Rumi Usagiyama intake → WH name TOBI)
**Status:** unrigged static (0 skins, 0 animations in GLB) — rig queued, same path as other SmutBase intakes.
**Coordinate note:** Z-up in this GLB; character ~8 units tall (feet z≈0, ears z≈9.4). T-pose (arms along ±x).
**Naming note:** mesh names are a mix of Blender defaults and Source-engine rip names (`puppershupper_…_dmx_*`). Categories below are assigned by bounding-region analysis against the body mesh; confidence is noted per part. This is the foundation for the creation-suite clothing system.

## Part list

| # | Mesh name | Prims | Verts | Category | Swappable | Description |
|---|-----------|-------|-------|----------|-----------|-------------|
| 1 | `Mirko` | 2 | 91,906 | full-body | No (base) | Main body mesh — full figure, head to feet (z 0.02–8.09). Materials: `Body`, `belt`. The foundation everything layers over. |
| 2 | `puppershupper_My_Hero_All_s_Justice_Mirko_mdl_Ears_Ears_dmx_MESH` | 1 | 5,232 | headwear | Yes | Rabbit ears (z 7.16–9.37, above head). Very high confidence — name + position. Tobi's signature silhouette. |
| 3 | `Plane` | 1 | 7,476 | hair | Yes | Long hair fall (z 3.79–6.84, x ±0.86 — down the back from head to mid-torso). High confidence. |
| 4 | `Torus` | 1 | 2,304 | accessories | Yes | Head ring (z 6.77–7.06, ring x ±0.36 around head-top). High confidence — hair-tie/headband ring. |
| 5 | `puppershupper_…_Mirko_Mirko_dmx_ME` | 1 | 7,512 | full-body | No | Torso/bust overlay mesh (z 4.73–5.27, upper chest). Treat as part of the body base, not separable clothing. Medium confidence. |
| 6 | `Mirko_001` | 1 | 12,498 | accessories | Yes | Waist sash/scarf — long flowing piece (x ±1.2, z 3.31–8.19, material `belt`). High confidence — the courier's sash; canon: the satchel strap region. |
| 7 | `Mirko_002` | 524 | 15,072 | bottoms | Yes | Lower-body costume (z 0–3.25, x ±1.24) — heavily fragmented by material (524 prims alternating `belt`/`Body`). Legwear + boots as one logical part. Medium-high confidence. |
| 8 | `Mirko_003` | 3 | 11,112 | gloves | Yes | Arm meshes in T-pose (x ±4.03, z 5.98–6.61 — the outstretched arms). Glove/gauntlet region. Medium confidence. |
| 9 | `Cube_001` | 1 | 2,080 | accessories | Yes | Collar (z 5.07–5.36, x ±0.65 — shoulder/neck zone). Medium confidence. |
| 10 | `Mesh0000_002` | 1 | 30,708 | tops | Yes | Bodysuit torso, front (x ±0.42, front y −2.10…−0.40, z 3.19–4.31). Medium-high confidence. |
| 11 | `Mesh0000_003` | 1 | 24,852 | tops | Yes | Bodysuit torso, second layer (z 3.18–4.39 — wraps torso with the previous mesh). Medium confidence. |

## Layer order (outer → inner)

1. Ears (`…_Ears_…`), `Torus` (head)
2. `Plane` (hair)
3. `Mirko_001` (sash), `Cube_001` (collar)
4. `Mesh0000_002`, `Mesh0000_003` (tops), `Mirko_002` (bottoms), `Mirko_003` (gloves)
5. `Mirko` + `…_dmx_ME` (body base)

## Materials

Two materials in the GLB: `Body`, `belt`. Full texture set archived alongside the source at `roster/miruko/intake/` (`Mirko body.png`, `Mirko face.png`, `mirko-belt_Base_color.png`, …).

## Creation-suite notes

- 8 of 11 meshes are swappable; `Mirko` + `…_dmx_ME` form the fixed body base.
- The rabbit ears are Tobi's signature — flagged as a protected signature part (canon: never removed).
- The sash (`Mirko_001`) is the satchel-strap region — canon says her left hand never leaves it; the strap mesh should stay bound to the left-hand rig when rigging lands.
- `Mirko_002` (524 prims) must be treated as ONE logical part (bottoms) in the suite UI despite fragmentation.
- No underwear meshes separately modeled in this GLB.
- Headwear category = the ears (no separate hat/cap mesh).
