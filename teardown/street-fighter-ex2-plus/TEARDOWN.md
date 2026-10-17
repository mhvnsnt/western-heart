# Street Fighter EX2 Plus — Teardown Report

**Game:** Street Fighter EX2 Plus (PS1, Arika/Capcom, 1999)  
**Disc:** SLUS_011.05, 98MB  
**Status:** File extraction 100% complete. Geometry format partially reverse-engineered.  
**Date:** 2026-10-17

## Disc Structure

Extracted via custom ISO9660 parser (`iso_extract.py`). 83MB of files.

### Key Directories

| Directory | Contents | Notes |
|-----------|----------|-------|
| `PL/` | 30 character PAC files (P00X.PAC - P1EX.PAC) | One per fighter |
| `PL2/` | BAS.PAC, P1D2X.PAC, P1DX.PAC | Additional player data |
| `PLTEX/` | KAO_*.DP (face textures) | KAO = "face" in Japanese |
| `PLNMD/` | NEZUMI.NMD, RENGA.NMD, VEGADAMA.LMD | Model-related |
| `TIM/` | Menu/UI textures (.TIM, .PAC) | Standard PS1 TIM format |
| `OVL/`, `OVL2/`, `OVL3/` | Overlay files | Code overlays |
| `STG2/` | Stage data | Backgrounds |
| `SND3/`, `PLSND/`, `PLWSND/` | Sound data | |

### Character Files

30 PAC files in `PL/`, ranging from 114KB to 215KB:
- P00X.PAC (126K), P01X.PAC (151K), P02X.PAC (200K), P03X.PAC (156K)...
- P05X.PAC (215K) largest — likely a complex character
- P15X.PAC (114K) smallest

SF EX2 Plus roster (26 fighters + bosses):
Ryu, Ken, Chun-Li, Zangief, Guile, Dhalsim, Blanka, Vega, Sagat,
Hokuto, Kairi, Allen, Blair, Darun, D.Dark, Skullomania, Garuda, Pullum, Cracker Jack,
Nanase, Sharon, Hayate, Shadow Geist, Area, Cycloid-β, Cycloid-γ

## PAC Format (Arika Custom)

**Not standard TMD.** Only 1 TMD found on entire disc (337 verts, boot logo).

### Header Structure

```
Offset 0x00: u32 header_size (0x14 = 20 bytes)
Offset 0x04: u32 section_offsets[5]
```

5 sections identified via entropy and structure analysis:

| Section | Offset | Size | Entropy | Likely Contents |
|---------|--------|------|---------|-----------------|
| 0 | 0x0030b4 | 5,440 | 1.81 | Bone/part metadata, structured |
| 1 | 0x0045f4 | 512 | 1.30 | Unknown, tiny structured data |
| 2 | 0x0047f4 | 86,616 | 6.44 | Vertex/geometry data |
| 3 | 0x019a4c | 23,620 | 5.56 | Face index table |
| 4 | 0x052903 | — | — | Beyond EOF (decompressed size marker?) |

### Section 3: Face Index Table

```
Offset 0x00: u32 field1 (14656)
Offset 0x04: u32 field2 (23620 = section size)
Offset 0x08: u32 face_offsets[] (variable length)
```

Each offset points to a face definition within section 3.

### Face Structure (16 bytes)

```
Offset 0x00: u32 flags/type
Offset 0x04: u16 v0, u16 pad0
Offset 0x08: u16 v1, u16 pad1  
Offset 0x0C: u16 v2, u16 pad2
```

Example (Face 3 at offset 0x1318):
```
40 08 00 00  <- flags 0x0840
2a 00 00 00  <- v0=42, pad=0
46 00 1c 00  <- v1=70, pad=28
09 00 89 02  <- v2=9, pad=649
```

The pad values may be UV coordinates, normal indices, or color data.

### Section 2: Vertex Data (INCOMPLETE)

86,616 bytes. Format not yet fully decoded.

Observations:
- Data shows pattern of (value, 0) pairs suggesting 32-bit values
- Values increase monotonically in first bytes: 264, 760, 1144, 1776...
- Does NOT match standard s16 x,y,z triplets
- May be bone-relative coordinates, compressed, or interleaved with other data

**BLOCKER:** Vertex format needs further RE. Possible approaches:
1. Ghidra analysis of SLUS_011.05 to find PAC loading code
2. PCSX-Redux VRAM dump while game runs
3. Compare multiple character PACs to find common patterns

## Tools Created

All in `~/workspace/sfex-teardown/`:
- `iso_extract.py` — PS1 .bin ISO9660 extractor
- `tmd_extract.py` — TMD scanner (found only boot logo TMD)
- `pac_parse.py` — Arika PAC header/face table parser
- `tim_extract.py` — TIM texture extractor (partial)
- `obj2glb.py` — Blender OBJ→GLB converter
- `render_char.py` — White-void character renderer

## Next Steps

1. **Decode section 2 vertex format** — highest priority blocker
2. **Map face vertex indices to section 2** — once vertices decoded
3. **Identify character-to-file mapping** — via textures or file order
4. **Extract all 30 characters** → OBJ → GLB
5. **Wire into western-heart roster** (`game/js/roster-full.js`)
6. **Generate white-void renders** for Tripo pipeline
7. **Repeat for EX Plus Alpha and EX3**

## Files

- Disc image: GitHub release `sf-ex2-plus-v1` (mhvnsnt/western-heart)
- Extracted files: `~/workspace/sfex-teardown/work/ex2-extracted/` (transient)
- This report: `teardown/street-fighter-ex2-plus/TEARDOWN.md`
