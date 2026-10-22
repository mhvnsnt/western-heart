# Research: Fatal Fury — Wild Ambition (PS1) teardown notes (worker 69, 2026-10-22)

Target: Raiden / Big Bear 3D moveset for Titan (his only 3D playable appearance).

## Acquisition chain (all verified)
1. IA `fatal-fury-wild-ambition-usa_202503` -> `Fatal Fury - Wild Ambition (USA).chd`
   (448,135,229 bytes, md5 `557b9d20a2d0b9682ac089cbda13a51e` MATCH).
2. `chdman extractcd` -> `ffwa-usa.bin` (693,830,592 bytes, 2352-byte sectors) + `.cue`.
3. `bchunk` -> `ffwa-iso01.iso` (604,151,808 bytes, 2048-byte sectors, ISO9660
   `SLUS-01001`, SNK, 1999-09-23). (`7z` cannot read PS1 2352-byte `.bin`
   directly; the `.cue` alone is not an archive.)

## Disc layout
| File | Size | Notes |
|---|---|---|
| `DUMMY.DAT` | 30.7MB | padding |
| `GAME.DAT` | 91.6MB | character/stage data archive (the prize) |
| `MENU.BIN` | 125KB | menu data |
| `SLUS_010.01` | 616KB | game executable |
| `STR/` | ~70MB | ending videos (STR/END*.STR) |

## GAME.DAT forensics
- 91,615,232 bytes. First u32 LE = 542, followed by 542 8-byte entries
  (offsets `aebe`, `74748`, `4d780`, `458b8`... with small companions
  `3`, `ec`, `187`, `213`...). Naive (offset,size) reading gives implausible
  tiny sizes; the table stride/field order is not yet understood.
- Data at candidate offsets is high-entropy (no TIM/TMD headers in the clear).
- Full scan: **3,631 zlib signatures** (`78 01/9c/da`), **17,266 TIM
  signatures** (`10 00 00 00`) — archive of compressed chunks + PS1 textures.
- Strings: no `RAIDEN`/`BEAR`/`BIGBEAR`; coincidental `JOE` @3,617,466 and
  `RYO` @14,492,341 only. Character data is compressed or indexed by ID.

## Next steps for the binary RE
1. Determine the 542-entry table format (try: (id, offset, size) 12-byte;
   offset relative to table end; size-prefix per chunk).
2. Inflate the zlib streams; look for TMD model headers and SEQ animation data.
3. Cross-reference with `SLUS_010.01` (load addresses, overlay table).
4. Raiden's chunk identification: likely by character ID order (roster order
   in the FAQ: Terry=1 ... Raiden=10).

## Moveset status (not blocked on the RE)
Doc-sourced from the verified FAQ: `federation/kof3d/ffwa-raiden.json`
(17 moves, Tekken notation). The binary RE upgrades animations/models later.

## Local-disk note
Per the user's large-file rule: CHD/BIN/ISO live in `~/workspace/w59/wild-ambition/`
(worker staging, NOT the repo). Only the extracted moveset JSON + this report
go in the repo. The 694MB `.bin` and 604MB `.iso` are intermediate and can be
deleted once GAME.DAT's table format is cracked (GAME.DAT itself is kept until
the RE completes).
