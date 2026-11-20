# Urban Reign — UI Assets (AI Generation Templates)

Extracted UI assets from Urban Reign (PlayStation 2, 2005).
These serve as TEMPLATES for AI-generating Western Heart UI in the same style.

## Directory Structure

- `title-screens/` — Title screen art
  - `title_US.vgs` (304KB) — US title screen
- `menus/` — Menu screens and UI
  - `menu.vgs` (310KB) — Main menu
- `character-select/` — Character select screen assets
  - `face.vgs` (116KB) — Character faces/portraits
  - `select.ppk` (108KB) — Character select screen data (PPK archive)

## Format Notes

- `.vgs` — Namco proprietary archive format (header: `03 08 04 00`...)
  - Contains textures and layout data for UI screens
  - Further RE needed to extract individual images
- `.ppk` — Namco PPK archive (magic: `ppk\0`)
  - See `../PPK-FORMAT.md` for format details
  - Use `../tools/ppk_probe.py` to inspect contents

## Usage

Per the owner's directive: "since our models are the base of their characters,
their art can be the base of our art." Use these as img2img bases or style
references when generating Western Heart UI.

## Extraction

Range-fetched from GitHub Release `urban-reign-iso-v1` (DVD000.AFS):
- `data/kageTest/vgs/title_US.vgs` @ AFS offset 0x6325000
- `data/kageTest/vgs/face.vgs` @ AFS offset 0x6BA0000
- `data/rt/menu.vgs` @ AFS offset 0x78BA000
- `afs/safe/ppk/select.ppk` @ AFS offset 0xA2D3000
