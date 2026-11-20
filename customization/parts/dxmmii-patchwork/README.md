# DXMMII "Patchwork DJ" — Option Library

**Character:** DXMMII — The Rebuilt Soul (Western Heart, Mokujin base)
**Variant:** Patchwork DJ — first custom look (owner 2026-10-18)

## What this is

An amplified patchwork crash-test-dummy DJ colorway, following the Pantera Attire-3 option-library pattern. Texture work only — no geometry, rig, or deletion changes.

## The look

- **Multi-colored vibrant panels:** blue/green limb segments, red head, magenta feet, purple/teal strips, orange ring
- **Crash-test target symbol** painted on the chest (into the torso texture at UV u 0.58–0.91)
- **X-eyes preserved** (black, owner-locked — separate geometry, not a texture)
- **Kept:** pink flower, carved back plaque, vinyl-record hands, wood joint pegs

## Files

- `textures_original/` — 21 original JPEGs (byte-identical extracts from game/assets/models/dxmmii.glb)
- `textures_patchwork/` — 21 reskin JPEGs (vibrant colorize)
- `MANIFEST.json` — parameterized placements + eye-mapping note
- `dxmmii-patchwork.glb` — the reskin GLB (in roster/dxmmii/attires/patchwork-dj/)
- Front/side renders (2048×2048, ortho, white)

## Eye mapping

DXMMII keeps his X eyes (owner-locked). The X-eyes are separate black geometry — not a texture — so no eye-library UV mapping applies. Yellow tiger eyes are NOT applied to DXMMII per the owner instruction.

## Restore

To restore the original: replace any `textures_patchwork/` file with its `textures_original/` counterpart and re-embed, or use the base GLB at game/assets/models/dxmmii.glb.
