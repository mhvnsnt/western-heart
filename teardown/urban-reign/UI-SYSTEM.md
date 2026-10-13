# URBAN REIGN — UI/Menu System Documentation

**Extracted 2026-10-13** via surgical range-fetch from GitHub Release `urban-reign-iso-v1`.
All files in `teardown/urban-reign/ui/`, `missions/`, `animations/motion-packs/`, `cutscenes/`.

## UI File Inventory

| Category | Location | Count | Size | Contents |
|----------|----------|-------|------|----------|
| Screen layouts | `ui/screens/` | 54 | ~19MB | Title, mode select, options, char profile, etc. (VGS format) |
| Menu data | `ui/menus/` | 18 | ~2MB | Menu layouts, pause screen, frames, progress (VGS/DCM/VMD) |
| Menu PPKs | `animations/motion-packs/` | 4 | — | `select.ppk`, `main.ppk`, `main_in.ppk`, `mainx.ppk` |
| Mission definitions | `missions/definitions/` | 256 | 2MB | Per-mission `.bin` data files |
| Mission packages | `missions/ppks/` | 100 | 821MB | Per-mission PPK containers |
| Motion packs | `animations/motion-packs/` | 42 | 21MB | `pmot*.ppk` (30), `tmot*.ppk` (10), `weapon.ppk` |
| Cutscene data | `cutscenes/` | 35 | 12MB | `demo_data*.ppk` |

## VGS Format — UI Texture Atlas (Namco Proprietary)

VGS files are Namco's UI screen format. Every menu screen, title card, mode
select, and HUD element is a `.vgs` file.

### Header Structure

| Offset | Size | Field |
|--------|------|-------|
| 0 | 2 | Magic `03 08` |
| 2 | 2 | Format type `04 00` |
| 4 | 2 | Grid width (tiles) |
| 6 | 2 | Grid height (tiles) |
| 8 | ... | Offset/size table, then tile data |

### How It Works

Each VGS is a **grid of texture tiles** that compose a UI screen:
- `title.vgs`: 5×5 grid (303KB) — the title screen
- `charaprofile.v`: 10×10 grid (483KB) — character profile/select art
- `face.vgs`: 4×4 grid (115KB) — face/character portraits
- `menu.vgs`: 1×11 grid (309KB) — vertical menu (11 items)
- `modesel.vgs`: mode select screen
- `option.vgs`: options menu

To rebuild a screen: decode each tile in grid order, composite left-to-right,
top-to-bottom. Tile data after the header is Namco's inline texture format
(full decode still open — no TIM2/PNG signatures, proprietary encoding).

### Screen List (all in `ui/screens/`)

**System screens:** `title.vgs`, `title_US.vgs`, `title_wide.vgs`,
`title_wide_US.vgs`, `namco.vgs`, `namco_wide.vgs`, `cri.vgs`, `cri_wide.vgs`
(CRI Middleware logo), `memcard.vgs` (memory card), `common.vgs` (shared UI)

**Mode select:** `modesel.vgs`, `single_mode_*.vgs`, `multi_mode.vgs`,
`free_mode.vgs`, `challenge_mode`, `practice_mode`, `tutorial.vgs`

**Character:** `charaprofile.v` (character profiles), `face.vgs` (portraits)

**Game flow:** `option.vgs`, `win_icon.vgs`, `cong00`-`cong12.vgs` + `congCommon.vgs`
(congratulations/victory), `end_challenge_*`, `end_free_mode.*`, `end_single_mod*`
(end screens), `unlockMoveSS.v*`, `unlockOtherSS.*` (unlock notifications)

**Stages:** `mc_stage00`-`mc_stage06.vgs` (mission stage art)

## DCM Format — UI Layout Tables

`.dcm` files are UI layout/position data:
- `dcm_pause.dcm` (17KB): pause menu layout — starts with a table of
  increasing 16-bit offsets (0x04ac, 0x04c1, 0x04d4...), likely widget positions
- `dc_info.dcm`, `dc_mess.dcm`, `dcm_progress.dcm`: info/message/progress layouts

## PPK Menu Containers

- `select.ppk` (108KB): character select screen data (PPK container, no embedded
  textures — references texture IDs resolved at runtime)
- `main.ppk`, `main_in.ppk`, `mainx.ppk`: main menu variants

## Mission System

256 mission definition files (`missions/definitions/mission000`-`mission255.bin`,
2MB total) + 100 mission PPK packages (`missions/ppks/mission001`-`mission100.ppk`,
821MB total). Each mission has a `.bin` definition and a `.ppk` asset package.

## Motion/Animation Packs

- `pmot001`-`pmot072.ppk` (30 files): per-character motion packs
- `tmot001`-`tmot010.ppk` (10 files): team/tag motion packs
- `weapon.ppk` (888KB): weapon animation data
- Cross-reference with `motion/` directory (already extracted): `gyuindex.bin`
  maps character slots to shared `.gyu` animation pools

## How to Build Custom Menus/HUDs (for Western Heart)

### Approach 1: VGS as Template
1. Decode VGS tile grids (format documented above)
2. Replace tile textures with Western Heart art (AI-generated from templates)
3. Keep the grid layout — positions and sizes are already game-tested

### Approach 2: DCM Layout Reference
1. Parse DCM offset tables for widget positions
2. Use as layout reference for Godot/HTML UI implementation
3. Pause menu (`dcm_pause.dcm`) is the simplest starting point

### Approach 3: PPK Structure
1. PPK containers hold menu logic + asset references
2. `select.ppk` shows how character select is structured
3. Adapt the container pattern for Western Heart's character select

## What's NOT Yet Decoded

- VGS tile texture payload (proprietary Namco encoding, no standard signatures)
- DCM widget field semantics (offsets identified, field meanings TBD)
- PPK sub-chunk structure for menu PPKs (geometry/texture chunks are Namco inline)
- Per-mission `.bin` field layout

## Related

- `PPK-FORMAT.md`: PPK container specification
- `TEARDOWN.md`: full game teardown inventory
- `afs-map/dvd000_afs_map.json`: all 2,431 DVD000 file offsets
- `tools/ppk_probe.py`: PPK inspection tool
- `~/workspace/agent-ops/ur-extract/ur_fetch.py`: surgical range-fetch tool
