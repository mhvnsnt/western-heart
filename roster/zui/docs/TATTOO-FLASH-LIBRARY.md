# ZUI Tattoo Flash Library

Saved 2026-10-14. The 12 sketchbook tattoo designs + the 9 canonical placements from the Zui rework v2 (Attire 2). Reusable on any Zui attire or other fighter.

## Flash designs

Location: `zui_flash/` (transparent PNGs, bold black outlines, saturated colors, alpha verified).

| File | Design |
|------|--------|
| `tiger.png` | Tiger — chest piece |
| `koi.png` | Koi fish — forearm |
| `dragon.png` | Dragon (smooth serpent ribbon) — forearm |
| `skull.png` | Skull — forearm |
| `torii.png` | Torii gate — forearm |
| `temple.png` | Burning temple — forearm |
| `wave.png` | Wave — forearm |
| `flames.png` | Flames — neck |
| `crane.png` | Crane — cheek |
| `lotus.png` | Lotus (unused in v2, in library) |
| `oni.png` | Oni mask (unused in v2, in library) |
| `sake.png` | Sake bottle (unused in v2, in library) |

Canon: each tattoo is a temple he burned or a night he survived. Random placement is intentional — "sketchbook" body. The LEFT shoulder blade stays BLANK ("for the night he hasn't survived yet").

## Canonical placements (Zui rework v2 / Attire 2)

Method: subdivided plane (3 cuts) → shrinkwrap (NEAREST_SURFACEPOINT, offset 0.004) onto target mesh → material with flash PNG (Color→Base Color, Alpha→Alpha, blend BLEND, backface culling ON) → APPLY the shrinkwrap to bake. Decals are STATIC (not bone-parented) — they hold for T-pose/showcase renders; re-bake if the rig is re-posed.

Bone mirror note: on the Steve Fox base, bone "LeftArm" sits at world −X = anatomical RIGHT. Anatomical left = +X.

| Tattoo | PNG | Position (x, y, z) | Target mesh | Size |
|--------|-----|-------------------|-------------|------|
| Tiger (chest V) | `tiger.png` | (0.0, −0.10, 1.42) | ModelTorso | 0.32 |
| Koi (forearm) | `koi.png` | (−0.50, −0.10, 1.49) | ModelArms | 0.16 |
| Dragon (forearm) | `dragon.png` | (−0.58, −0.10, 1.48) | ModelArms | 0.16 |
| Skull (forearm) | `skull.png` | (−0.66, −0.10, 1.47) | ModelArms | 0.16 |
| Torii (forearm) | `torii.png` | (0.50, −0.10, 1.49) | ModelArms | 0.16 |
| Temple (forearm) | `temple.png` | (0.58, −0.10, 1.48) | ModelArms | 0.16 |
| Wave (forearm) | `wave.png` | (0.66, −0.10, 1.47) | ModelArms | 0.16 |
| Flames (neck) | `flames.png` | (0.0, −0.12, 1.52) | ModelNeck | 0.24 |
| Crane (cheek) | `crane.png` | (−0.085, −0.075, 1.60) | ModelFace | 0.10 |

Generator: `~/workspace/zui_tattoos.py` (PIL). Build script: `~/workspace/zui_stage5.py` (`add_tattoo`).

## Applying to a new attire

1. Import the attire GLB.
2. Identify the skin meshes (torso/arms/neck/face equivalents).
3. Run `add_tattoo` per row above, adjusting positions to the new mesh's proportions.
4. Keep the left shoulder blade blank.
5. Render front/side/back 2048 white and verify limb-by-limb before showing.
