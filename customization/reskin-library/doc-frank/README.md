# Doc Frank — "Machine Shop" reskin library

Doc Frank's **first custom look** (owner 2026-10-18). The Builder Soul's
machine-shop workwear: the white lab coat goes to the shop — oil-stained
charcoal coat, brass/copper tie, dark brown workwear.

## What's here

| File | What it is |
|---|---|
| `doc-jacket-shopworn.png` | Coat: white→oil-stained charcoal (replaces `jacket_d`, GLB image 7) |
| `doc-shirt-workwear.png` | Shirt: teal→dark brown (replaces `shirt_d`, GLB image 14) |
| `doc-tie-copper.png` | Tie: rust→brass/copper metallic (replaces `tie_d`, GLB image 3) |
| `doc-pants-workwear.png` | Pants: green→dark brown, belt kept (replaces `pants_d`, GLB image 13) |
| `doc-shoes-shopworn.png` | Shoes→shopworn boots (replaces `shoes_d`, GLB image 15) |
| `*-original.png` | Byte-identical originals from `game/assets/models/doc-frank.glb` — restore points |
| `MANIFEST.json` | Parameterized placements, GLB image indices, swap procedure |

## The reskinned model

`roster/doc-frank/attires/machine-shop/doc-frank-machine-shop.glb` — texture
work only, no rig/geometry changes. T-pose renders (own-eyes verified):
`roster/doc-frank/doc-frank-machine-shop-front.jpg`,
`roster/doc-frank/doc-frank-machine-shop-side.jpg`.

## Eyes

Defaults untouched. The yellow tiger eye (owner's universal "I like" variant)
is a swappable option in `customization/parts/doc-frank-eyes/` — tiger iris
composited onto Doc Frank's native eye texture, drop-in 128x128 for `eyes_d`.
