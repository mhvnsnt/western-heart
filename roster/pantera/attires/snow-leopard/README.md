# Pantera — Attire 3: Snow Leopard colorway (owner 2026-10-17)

Reskin of the **older classic Pantera build** (`../classic/pantera-classic.glb`,
Tekken 7 King P1 source, Mixamo-rigged) into a snow-leopard colorway, per the
owner's exact spec:

- **Tights:** purple → **blue** (panther decal kept black, red claws kept)
- **Head/mask:** black panther → **white** with **snow-leopard rosette spots**
- **Eyes:** yellow → **blue**
- **Nose:** → **pink**

## Method

Texture recolor of the 4 embedded diffuse maps (geometry, rig, and the rest of
the attire untouched — black trunks with red PANTERA, boots, gloves all kept):

| GLB image | Texture | Change |
|-----------|---------|--------|
| 5 | `King_Eye_D` | yellow iris → blue (HSV hue shift, pupil kept black) |
| 11 | `King_DefaultHead_D` | tan fur → white (luminance-preserving), dark rosettes kept, nose → pink |
| 44 | `King_PantsLower_D` | vivid purple → blue (HSV hue shift on saturated purple; black decal untouched) |
| 50 | `King_MaskFur1_D` | near-black → snow-white base + procedural snow-leopard rosettes (broken dark rings + spots, seeded) |

Specular/normal maps untouched. Re-embedded via buffer rebuild (4-byte aligned,
all offsets rewritten; 54 images / 18 materials / 18 meshes verified intact).

The original classic build is untouched in `../classic/` and recoverable from
git history.

## Render proof

`docs/tpose-refs/pantera-snow-leopard/p1_front.png` — T-pose front, locked
orientation method (`docs/RENDER-ORIENTATION.md`, faceY variant: model faces -Y).
Own-eyes verified: blue tights, white spotted head, blue eyes, pink nose.

## Note for future renders

The repo's `tpose_render_cycles_faceY.py` rotates objects BEFORE the T-pose step,
which detaches the arms on this Mixamo rig (side detection reads `head.x ≈ 0`
after rotation). Workaround used here: T-pose in native space FIRST, then apply
Rz(-90°). Rendered with a fixed copy; the repo script is unchanged.
