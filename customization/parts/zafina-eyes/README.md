# Zafina eye options (owner 2026-10-18)

Per-character eye option library — same pattern as `customization/parts/pantera-eyes/`.
Every variant is swappable Tekken/WWE-style; nothing is overwritten.

## Entries

| id | file | notes |
|----|------|-------|
| `zafina-eye-original-brown` | `zafina-eye-original-brown.png` | **Her ORIGINAL eyes**: dark brown iris, 128x128, extracted from `eyes_d` in `game/assets/models/zafina.glb`. Restore by re-embedding as `eyes_d`. |
| `eye-yellow-tiger` (universal) | `customization/eye-library/eye-yellow-tiger.png` | Owner's "I like" variant — **currently applied** on the Golden Pharaoh attire (native 128, drop-in). |

## How to swap

1. Pick an eye PNG (this folder or the universal `customization/eye-library/`).
2. Re-embed it as texture `eyes_d` (material `24_eyes_1_16_16`)
   in `roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb`.
   Full replace, 128x128 — universal entries drop in with no resize.
