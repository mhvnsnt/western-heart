# King P2 Attire — official Tekken 7 Player 2 recolor

No downloadable P2 model exists (checked rigmodels.com 2026-10-12 — both Tekken 7
King models there are P1). Since P2 is a texture swap of P1, this pack recolors
the P1 diffuse maps to the official P2 scheme:

- Tights: blue -> black, tribal designs -> bronze
- Trunks: gold -> black, designs/trim -> bronze
- Boots: gold -> black, trim -> dark red, MEXICO text -> red, studs -> bronze
- Belt logo: cyan KING text -> bronze
- Arms/gloves/mask: unchanged (P2 keeps them yellow)

## Contents

- `King_*_P2_D.png` — the 7 recolored diffuse maps
- `King_*_{N,S}.png` + unchanged `King_*_D.png` — rest of the set, unmodified
- `recolor_p1_to_p2.py` — the recolor script (PIL/numpy, HSV-selective)
- `P2-preview.png` — Blender Cycles render proof of the full P2

## Use

Drop the `*_P2_D.png` files over the P1 set (rename to the base names) or point
the texture-swap render script at this folder. Verified in Blender 2026-10-12.
