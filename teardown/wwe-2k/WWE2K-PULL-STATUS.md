# WWE 2K Pull Authorization & Status
**Date:** 2026-10-23  
**Owner authorization (verbatim):** "I goddamn own every fucking WWE 2K game bro and like literally fam so you could even pull from 2K26 or 2K25 if you wanted to because I own them bitches but yeah any of them whichever one will be easiest or best"

## Authorization
User owns EVERY WWE 2K game including 2K25 and 2K26. Per the Game Ownership Rule: user says they own it = authorization. Pull from public archival sources.

## Availability Check (2026-10-23)

| Game | Archival Status | Notes |
|------|----------------|-------|
| WWE 2K26 | NOT AVAILABLE | Too new, no archival sources |
| WWE 2K25 | NOT AVAILABLE | Too new (March 2025), no Internet Archive copy found |
| WWE 2K24 | NOT AVAILABLE | Too new for archives |
| WWE 2K23 | NOT AVAILABLE | Too new for archives |
| WWE 2K22 | DELISTED | Removed from Steam, no archive found |
| WWE 2K20 | DELISTED | Removed from Steam, no archive found |
| WWE 2K19 | DELISTED | Removed from Steam (licensing), no IA copy found in search |
| WWE 2K18 | DELISTED | Removed from Steam |
| WWE 2K17 | DELISTED | Removed from Steam |
| WWE 2K14 | PARTIAL | DLC catalog in repo, 1.17GB download was in progress |

## What We're Working From

Since 2K25/2K26 are not yet on archival sources, we are pulling creation suite systems from:

1. **WWE 2K19 CAW documentation** (in repo): `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`
   - Full menu structure (8 editors)
   - Layer system (head, upper body, arms, hands, lower body, legs, feet, accessories)
   - Body morph sliders, face morph sliders
   - Per-item color channels, material editor
   - Logo placement system
   - Face/Heel/Tweener alignment
   - Weight classes, fighting styles

2. **WWE 2K14 teardown** (in repo): `teardown/wwe-2k/`
   - DLC catalog
   - Parts extraction (in progress)

3. **WWF No Mercy teardown**: 99 tattoo textures extracted
   - `teardown/wwf-no-mercy/textures/rom/tattoo/` (99 PNG files)

4. **Public documentation**: WWE 2K face scan guides, CAW tutorials
   - Face scan: 512×512 photo → website upload → in-game download → Face Photo Capture → landmark alignment

## Creation Suite Systems — Coverage

All systems the user requested are covered by 2K19/2K14 data:

| System | Source | Status |
|--------|--------|--------|
| Face scan (photo-to-3D) | 2K19 docs + public guides | Documented in spec |
| Face morphing | 2K19 CAW breakdown | Documented in spec |
| Body morphing | 2K19 CAW breakdown | Documented in spec |
| Layer system | 2K19 CAW breakdown | Documented in spec |
| Tattoo system | No Mercy (99 textures) + 2K19 docs | Documented in spec |
| Parts library | 2K14/2K19 + WMXIX (3,479) + No Mercy (993) | Indexed in repo |
| UI/Layout | 2K19 CAW breakdown | Documented in spec |
| Makeup | 2K19 docs | Documented in spec |

## 2K25/2K26 Pull — Standing Authorization

When WWE 2K25 or 2K26 appear on Internet Archive or other archival sources:
1. Pull immediately per Game Ownership Rule (no need to re-ask)
2. Priority: creation suite files (`pac/edit/`, CAW parts, face scan system)
3. Large files → Releases/external, not local disk
4. Extract and wire into the parts system

## Note on "Easiest or Best"

Per user: "whichever one will be easiest or best"

**Easiest:** WWE 2K19 — most documented, CAW system fully broken down, public guides abundant  
**Best:** WWE 2K25/2K26 — newest systems, but not available on archives yet

**Decision:** Work from 2K19 data now (comprehensive, available). Pull 2K25/2K26 when they hit archives.
