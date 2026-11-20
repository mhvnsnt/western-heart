# Universal Eye Library

Owner directive 2026-10-18: every eye variant is saved as a swappable option,
WWE/Tekken-style — no variant is ever overwritten or discarded.

## The universal format

Each entry is a square RGBA eye-iris diffuse texture (`MANIFEST.json` → `entries`).
To make an entry usable on a character, add a `character_mappings` entry for that
character: which texture it replaces (`replaces_texture`), the material, and the
pixel rect to composite into. Full-texture replace for simple rigs; rect
compositing for characters whose eye diffuse carries other detail.

No geometry changes — texture swap only. That is what makes it universal.

## Entries

| id | name | status |
|---|---|---|
| `eye-yellow-tiger` | Yellow tiger eye | **Owner's "I like" variant — universal.** Realistic amber iris, radial striations, vertical slit pupil, dark limbal ring. Currently applied on Pantera Attire 3. |
| `eye-blue-snow-leopard` | Snow leopard blue eye | Saved default for the Attire 3 snow-leopard look. |
| `eye-classic-original` | Classic original eye (King gold) | King's original golden eyes, pre-reskin. |

## Adding a new character

1. Extract that character's eye diffuse texture.
2. Add a `character_mappings` entry (see `pantera` for the template).
3. Every entry PNG now works on them — no new art needed.
