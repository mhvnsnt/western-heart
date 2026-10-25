# WWE 2K Selective Extraction — Creation Suite Only
**Date:** 2026-10-23  
**Owner directive (verbatim):** "you can probably use that damn thing use the shit where you don't have to pull the whole damn game file but you can only pull like you can just pull everything from the creation suite itself. From those files you can probably do that huh."

## Principle

**DO NOT pull the full 50-60GB game.** Extract ONLY creation suite / CAW related files using selective methods.

## Target File List — Creation Suite Only

### CAW Parts (highest priority)
```
pac/edit/bbtemplate.pac       # Body templates (male/female base)
pac/edit/default.pac          # Default parts
pac/edit/edit.pac             # Edit mode parts
pac/edit/sample.pac           # Sample parts
pac/edit/ch/                  # Character parts (masks, normals)
pac/edit/body/                # Body part meshes
pac/profile/profile_dat.pac   # CAW metadata, hometown data
```

### Face Scan System
```
# Face photo capture system
# - Face texture templates
# - Landmark alignment data
# - Morph target definitions
# Search for: face, scan, photo, capture in filenames
```

### Tattoo Data
```
# Tattoo textures and placement data
# WWF No Mercy already yielded 99 tattoos
# 2K series has expanded tattoo library
```

### UI/Menu Files
```
# Creation suite menu layouts
# - Menu structure definitions
# - UI textures for CAW screens
# - Preview system assets
```

### Parts Library
```
# All categorized parts:
# - Hair (styles + parts)
# - Clothing (all layers)
# - Accessories
# - Face paint / makeup textures
```

## Selective Extraction Methods

### Method 1: File List Download (preferred)
If the archival source supports file listing:
1. Get full file manifest
2. Filter for `pac/edit/`, `*caw*`, `*custom*`, `*face*`, `*tattoo*`
3. Download ONLY matching files
4. Estimated size: 2-5GB (vs 50-60GB full game)

### Method 2: Archive Partial Extraction
For .7z, .zip, .rar archives:
```bash
# List contents first
7z l game.7z | grep -i "pac/edit\|caw\|custom"

# Extract only matching
7z x game.7z "pac/edit/*" "*/caw/*" -o./wwe2k-caw/
```

### Method 3: Torrent Selective Download
If using torrent sources:
1. Open .torrent, deselect all
2. Select ONLY `pac/` directory or creation-related files
3. Download selected files only

### Method 4: HTTP Range Requests
For direct HTTP links with known file structure:
```bash
# Download specific PAC files via range requests
# (requires knowing byte offsets from archive index)
```

## What We Already Have (don't re-pull)

| Data | Source | Location in repo |
|------|--------|-----------------|
| 2K19 CAW breakdown | Documentation | `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md` |
| 2K14 DLC catalog | Teardown | `teardown/wwe-2k/WWE2K14-DLC-CATALOG.md` |
| 99 tattoo textures | No Mercy teardown | `teardown/wwf-no-mercy/textures/rom/tattoo/` |
| WMXIX parts (3,479) | Teardown | `customization/parts/wmxix/` (indexed) |
| No Mercy parts (993) | Teardown | `customization/parts/no-mercy/` (indexed) |

## Extraction Priority Order

1. **Face scan system** — photo templates, landmark data, morph targets
2. **CAW part meshes** — `pac/edit/body/`, `pac/edit/ch/`
3. **Tattoo library** — textures + placement data
4. **UI layouts** — menu structure, preview system
5. **Clothing parts** — all layers, all categories

## Storage

- Extracted files → GitHub Release (not local disk, not repo)
- Documentation → repo (`teardown/wwe-2k/`)
- Indexed parts → `customization/parts/wwe2k/`

## When 2K25/2K26 Hit Archives

1. Check archival source for file listing capability
2. Apply selective extraction (Method 1 or 2)
3. Target ONLY creation suite files (~2-5GB)
4. Skip: match data, arenas, audio, videos, single-player content (~45-55GB)
