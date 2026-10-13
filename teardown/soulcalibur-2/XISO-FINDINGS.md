# Soulcalibur II — ISO Platform Correction + Filesystem Crack

**Date:** 2026-10-13
**Status:** CRITICAL FINDING — ISO is Xbox, not PS2

## Platform Mismatch

The ISO on GitHub Release `soulcalibur2-ps2-v1` (`Soulcalibur-II.iso`,
1,376,845,824 bytes) is the **Xbox version**, not PS2:

- Archive.org item `soulcalibur-ii` metadata: `"subject": "xbox"`
- ISO sector 32 (0x10000): `MICROSOFT*XBOX*MEDIA` magic (definitive XISO signature)
- ISO9660 PVD at sector 16 is minimal/fake (CD001 magic, zeroed fields,
  root extent 0) — standard for Xbox XISO discs
- Xbox guest character is **Spawn** (PS2 guest is Heihachi Mishima)

The PS2 version was **not found** on Archive.org:
- `soulcalibur-ii-usa` (subject: PS2) contains only cover art — no ISO dump.

**Decision needed:** proceed with Xbox SC2 (same systems/models, Spawn
instead of Heihachi) or source a PS2 ISO elsewhere.

## Filesystem: Xbox XISO (not "Namco proprietary")

The "Namco proprietary filesystem" blocker was a misidentification — the
container is Microsoft's Xbox XISO format, fully parseable. Root listing:

| File | Size | Sector | Format |
|------|------|--------|--------|
| `Default.xbe` | 3,616,768 | 265 | Xbox executable |
| `bgm.afs` | 239,648,768 | 2,031 | CRIWARE AFS (76 files) |
| `movie.afs` | 439,140,352 | 119,047 | CRIWARE AFS |
| `root.olk` | 693,833,728 | 333,471 | Namco OLK archive |

Tool: `~/workspace/agent-ops/scii-extract/scii_fetch.py` (range-fetch from
the GitHub release — no full 1.38GB download needed).

## AFS archives

Standard CRIWARE AFS (`AFS\x00` magic). `bgm.afs`: 76 files, no name table
(anonymous entries with valid offset/size). Same format as Urban Reign's
DVD000/DVD001 AFS — existing parsers apply.

## root.olk — Namco archive

Header (first 128 bytes):
```
0x00: u32 version = 5
0x04: magic 'olnk\x00'
0x08+: entry quads (u32 x4): (offset, size, timestamp, 0)
       timestamps ~0x3eeec598 = June 2003 (matches SC2 dev)
```

- No filenames in first 1MB (index may be name-less or stored later).
- Full index reverse-engineering is open work.
- 693MB — contains the bulk of game data (models, stages, textures).

## Next steps

1. **Owner decision:** Xbox vs source PS2 ISO.
2. If Xbox: reverse OLK index → range-fetch extract all files.
3. If PS2: locate PS2 dump, repeat XISO/AFS/OLK analysis (PS2 likely uses
   ISO9660 + same AFS/OLK internals).
