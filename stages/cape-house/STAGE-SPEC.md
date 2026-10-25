# Stage: Cape's House (western-heart) — spec v1 (2026-10-23, Grok Bot)

Status: **spec only**. Not yet wired into stage select (that touches `game/` files other agents own — do it in a separate claimed PR).

## Source of truth (build from existing assets, no hand-tooling)
| Piece | Source (existing repo work) |
|---|---|
| Living room geometry, colorway, LED wash | `mhvnsnt/cape-jones:3d-assets/living_room.blend` + `3d-assets/living-room/SCENE-CANON.md` (owner-LOCKED palette) |
| Furniture layout | `cape-jones:3d-assets/living_room_layout.json`, `3d-assets/living-room/furniture_positions.json` |
| CRT TV (portal prop) | `cape-jones:3d-assets/living-room/tv/`, `tools/crt-tv/` |
| House exterior, kitchen, bedroom, neighborhood | `cape-jones:docs/environments/HOUSE-DESIGN.md` (single-story ranch, beach suburb) — **no 3D yet; gap** |
| Stage rules (ring-out, walls, floor) | WH stage format: `game/assets/stages/*/stages.json`; T6/TTT2 wall/floor-break behavior from the teardowns |

## Variants
1. `living-room` — closed walls (WallBack/Left/Right = wall-splat walls), 7.0 x 6.0 m room; coffee table + sofa get pushed to the edges for fight space (layout variant, not an edit of the canon .blend).
2. `cape-bedroom` — also the base for **heart-and-mind** inner-space scenes.
3. `front-yard / street` — open stage (neighborhood). Gap: needs a teardown street stage or existing repo street kit as base.

## Export path (pending)
`blender -b living_room.blend` → export GLB to `stages/cape-house/living-room.glb` (new file) → stage-select entry in a separate PR. Never save over `living_room.blend`.

## Canon constraints
- Palette is owner-locked (SCENE-CANON.md). Recliner stays empty in the canon .blend until the light-flicker gag rig lands — proof renders import fighters in-memory and never save the .blend.
