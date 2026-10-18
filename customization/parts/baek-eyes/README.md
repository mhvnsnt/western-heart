# Baek eye options (owner 2026-10-18)

Per-character eye option library — same pattern as `customization/parts/lili-eyes/`.
Every variant is swappable Tekken/WWE-style; nothing is overwritten.

## Entries

| id | file | notes |
|----|------|-------|
| `baek-eye-original-brown` | `baek-eye-original-brown.png` | **His ORIGINAL eyes** (default, currently on the model): brown iris, 128x128, extracted from `pek1u_29` in `game/assets/models/baek.glb`. Restore by re-embedding as `pek1u_29`. |
| `eye-yellow-tiger` (universal) | `eye-yellow-tiger.png` | Owner's "I like" variant — **option only, NOT applied**. Copy of `customization/eye-library/eye-yellow-tiger.png` (already 128x128, drop-in for Baek). |

## How to swap

1. Pick an eye PNG (this folder or the universal `customization/eye-library/`).
2. Re-embed it as texture `pek1u_29` (material `mat_21-pek1u_29.jpg`)
   in `roster/baek/attires/master-white/baek-master-white.glb`. Full replace, 128x128.
3. Universal library entries are 128x128 — same size as Baek's eye, no resize needed.

## Universal mapping (pending)

The `character_mappings.baek` entry for `customization/eye-library/MANIFEST.json`
is specified in `MANIFEST.json` → `universal_mapping`. It is recorded here (not
yet applied to the universal file) to avoid a merge conflict with open PR #262,
which is also editing that file. Fold it in once #262 merges.
