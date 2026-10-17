# Street Fighter EX Plus Alpha — Teardown Report

**Game:** Street Fighter EX Plus Alpha (PS1, Arika/Capcom, 1997)  
**Disc:** 504MB .bin  
**Status:** File extraction 100% complete. Geometry format partially reverse-engineered.  
**Date:** 2026-10-17

## Disc Structure

### Key Directories

| Directory | Contents |
|-----------|----------|
| `PL/` | 26 character PAC files (P00.PAC - P25.PAC) |
| `TMD/` | FDEMO.PAC, GAMEN.LMD, HAPA.LMD, VEGADAMA.LMD (not actual TMD) |
| `TIM/` | Menu/UI textures |
| `TEX/` | Textures |
| `MOV/`, `MUS/`, `SND/` | Movies, music, sound |
| `STG/`, `STG2/` | Stage data |

### Character Files

26 PAC files in `PL/`. SF EX Plus Alpha roster:
Ryu, Ken, Chun-Li, Zangief, Guile, Dhalsim,
Hokuto, Kairi, Allen Snider, Blair Dame, Darun Mister, D. Dark,
Skullomania, Garuda, Pullum Purna, Cracker Jack,
Cycloid-β, Cycloid-γ, plus alternates/bosses

## PAC Format (Arika Custom)

### Header Structure

```
Offset 0x00: u32 header_size (0x2c = 44 bytes)
Offset 0x04: u32 section_offsets[10]
```

11 entries total (header_size / 4). More sections than EX2 Plus (which had 5).

Example from P00.PAC:
```
[0] 0x0000002c (44)        <- header size
[1] 0x0001bca0 (113824)
[2] 0x00025118 (151832)
[3] 0x00026258 (156248)
[4] 0x0002e478 (189560)
[5] 0x00032698 (206488)
[6] 0x000368b8 (223416)
[7] 0x00039958 (235864)
[8] 0x0003ae38 (241208)
[9] 0x0003b038 (241720)
[10] 0x00043258 (275032)
```

File size: 308,344 bytes (P00.PAC)

## Comparison: EX Plus Alpha vs EX2 Plus

| Aspect | EX Plus Alpha | EX2 Plus |
|--------|---------------|----------|
| Character PACs | 26 | 30 |
| Header sections | 11 | 5 |
| Format | Arika custom | Arika custom (evolved) |
| Standard TMD | None found | 1 (boot logo only) |

The format evolved between games but shares the same fundamental structure:
header with section offsets → geometry data → face tables.

## Tools

Same tools as EX2 Plus teardown work for both games.

## Next Steps

Same as EX2 Plus: decode vertex format, map faces to vertices,
identify characters, extract to GLB, wire into roster.
