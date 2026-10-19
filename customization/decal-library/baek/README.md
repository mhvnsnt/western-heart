# Baek dobok option library (owner 2026-10-18)

Texture-swap library for Baek's dobok — same pattern as `customization/decal-library/lili/`
and the Pantera tights entries. Every variant is a full-texture replace, swappable
Tekken/WWE-style; nothing is overwritten.

## Variants

| variant | prefix | status |
|---------|--------|--------|
| **Master's White** | `dobok-masterwhite-*` | **CURRENTLY APPLIED** on `roster/baek/attires/master-white/baek-master-white.glb` — crisp white dobok, Western Heart dark-red trim (collar, cuffs, jacket hem, tabs), black belt kept |
| **Fallen Master** | `dobok-fallenmaster-*` | OPTION (not applied) — near-black dobok, oxblood trim, red KOREA kept, han in silver |
| **Original** | `dobok-original-*` | Restore set — the pre-reskin textures from `game/assets/models/baek.glb` |

## What was recolored (Master's White)

| GLB texture | part | change |
|-------------|------|--------|
| `pek1u_1`, `pek1u_25` | trim (collar, cuffs, hem, tabs) | black → WH dark red |
| `pek1u_0/30/10/9/4` | dobok fabric | cream → crisp white |
| `pek1u_8/6/5` | dobok back | cream → white (red KOREA + black han kept) |
| `pek1u_32/27` | collar red lining | → WH dark red |
| `pek1u_3/28` | **belt** | **kept black** — a master's black belt is not recolored |

The belt textures were identified with a diagnostic solid-color render
(`pek1u_3` = belt band, `pek1u_28` = belt tips) and deliberately excluded from
both recolor variants.

## How to swap

See `MANIFEST.json` → `how_to_swap`. Full-texture replace at the entry's
`replaces_texture` name and `size_px`.
