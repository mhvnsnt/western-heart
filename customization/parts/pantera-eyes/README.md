# Pantera Eye Options

Interchangeable eye variants for Pantera, Tekken/WWE-style. Every variant is
saved here and never overwritten — the game UI (or a re-embed) can swap
between them at any time, snapping back to any saved look exactly.

## The options

| File | What it is |
|------|-----------|
| `eye-yellow-tiger.png` | **Currently applied on Attire 3.** Realistic golden-yellow tiger / snow-leopard eyes: radial iris fibers, dark limbal ring, amber ring around a round black pupil (round pupils are accurate for tigers and snow leopards), specular highlight. Owner order 2026-10-18. |
| `eye-snow-leopard-blue.png` | The blue eyes from the 2026-10-17 snow-leopard reskin. Saved as the snow-leopard **blue default option** per owner 2026-10-18. |
| `eye-original-classic.png` | Pantera's original classic yellow eyes (pre-reskin), from `roster/pantera/attires/classic/pantera-classic.glb`. Byte-identical to the Attire 1 (pantera-t7king) eyes. |

## How swapping works

Both eye meshes share the full `King_Eye_D` texture (`Modeleyes_Material003`
baseColor, 128×128): the iris is centered, the pupil sits at the texture
center. Any option PNG is a drop-in 128×128 replacement for image 5 in
`roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb` — one PNG covers
both eyes. See `MANIFEST.json` for the parameterized placement and the exact
swap steps.
