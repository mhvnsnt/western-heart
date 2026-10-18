# Lili eye options (owner 2026-10-18)

Per-character eye option library — same pattern as `customization/parts/pantera-eyes/`.
Every variant is swappable Tekken/WWE-style; nothing is overwritten.

## Entries

| id | file | notes |
|----|------|-------|
| `lili-eye-original-bluegray` | `lili-eye-original-bluegray.png` | **Her ORIGINAL eyes**: blue-gray iris, 256x256, extracted from `T_CH_eye_D` in `game/assets/models/lili.glb`. Restore by re-embedding as `T_CH_eye_D`. |
| `eye-yellow-tiger` (universal) | `customization/eye-library/eye-yellow-tiger.png` | Owner's "I like" variant — **currently applied** on the Noir Gala attire (resized to 256). |

## How to swap

1. Pick an eye PNG (this folder or the universal `customization/eye-library/`).
2. Re-embed it as texture `T_CH_eye_D` (material `Modelpart1_eyeball_Material005`)
   in `roster/lili/attires/noir-gala/lili-noir-gala.glb`. Full replace, 256x256.
3. Universal library entries are 128x128 — upscale to 256 with LANCZOS for Lili.
