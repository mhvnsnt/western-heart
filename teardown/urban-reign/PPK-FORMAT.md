# URBAN REIGN — PPK + Motion Format Notes (2026-10-13)

Probed from raw extractions (surgical range-fetch from GitHub Release
`urban-reign-iso-v1`; no local ISO needed). Deep binary RE of geometry/
texture payloads is still open work.

## PPK container (Namco proprietary)

Applies to `afs/safe/ppk/stage*.ppk`, `char*.ppk`, `mission*.ppk`.

| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Magic `ppk\0` (`0x70706B00`) |
| 4 | 4 | Total size (LE32; = file size − 8) |
| 8 | 4 | `0x200` (512) — data offset; header is 512 bytes |
| 12 | 500 | Header fields + sub-file offset table (TBD) |

**Stage PPK** (e.g. `stage028.ppk`): header words after magic are
`(10095625, 328194, 6553748, 47984, 1485136, 1491584, 640, 11604)` —
meaning unknown. At data+48 there is a strictly increasing offset table
(146 entries in stage028, e.g. `640, 652, 664, 676, 688, 704, …`),
4-byte-aligned sub-chunk offsets relative to the data start.
No embedded TIM2/texture or nested-PPK signatures — geometry/textures
are Namco inline formats (full chunk decode still open).

**Char PPK** (e.g. `char001.ppk`): header words `(57, 0, 0, 6, 1584, 8, 1648, 9)`.
Embedded regions are float-heavy (identity quats `1.0f` at 1584/1648).
No readable fighter names found in ASCII scan (names are hashed or in
another table). 72 char PPKs = full 60+ fighter roster + alternates.

## Motion / moveset (`tec/motion/`)

| File | Size | Notes |
|------|------|-------|
| `gyuindex.bin` | 8,284 | Magic `pmot001.` — per-character motion index: `pmotNNN` / `pmotIDNNN` name entries mapping character slots to the shared pools |
| `gyuindex_ppk.bin` | 3,467 | Same index in PPK-packaged form |
| `normal/general.gyu` | 1,532,848 | Shared normal-stance move pool. Header words `(114, 23, 0, 1)` |
| `30frame/general.gyu` | 1,788,924 | Shared 30fps move pool |
| `weapon/general.gyu` | 587,372 | Shared weapon move pool |
| `gyu_debug.gyu` | 4,016 | Debug motion sample |

The `.gyu` pools hold the actual animation data; `gyuindex.bin`
is the lookup from a fighter's `pmotNNN` slot into the pool.
Per-move keyframe decode is open work.

## Stage lighting

`data/light/stage/bg*.lit` (8 files: bg01, bg02, bg03, bg11, bg13,
bg39, bg40, bg60) — per-stage lighting rigs. Not yet extracted.

## What's reachable next (surgical, no ISO download)

`afs-map/dvd000_afs_map.json` has all 2,431 DVD000 entries with byte
offsets. Any file can be pulled with one HTTP Range request against the
release parts. Remaining targets: `mission*.ppk` (~100 files, ~10MB each,
~1GB total — fetch selectively), `data/light/stage/bg*.lit`,
`data/kageTest/vgs/mc_stage*.vgs` test stages, `tec/demo/` cutscene data.

## Char PPK inner structure (2026-10-13 probe)

### Header (char001.ppk, 776,960 bytes)
| Offset | Field |
|--------|-------|
| 0 | Magic `ppk\0` |
| 4 | Total size (LE32) |
| 8 | Data offset (LE32; **128** for char PPKs, not 512) |
| 0x10 | Tag `ccnf` (Namco chunk type) |
| 0x14 | 0x47 (71) — count? |
| 0x18 | 0x00080000 |
| 0x1c | 0x00050005 |
| 0x20 | 0x80012971 — [u16 type=0x8001][u16 offset=0x2971] |
| 0x24 | 0xa0000a4f — [u16 type=0xa000][u16 offset=0x0a4f] |
| 0x28 | 0xae00017d — [u16 type=0xae00][u16 offset=0x017d] |

**Offset encoding**: high u16 = type tag, low u16 = offset. Types seen:
- `0x8001` → data buffer (s16 quantized? at 0x2971)
- `0xa000` → zero-filled region (at 0x0a4f)
- `0xae00` → index/bone data (small integers at 0x017d)

### Data regions
- **0x017d**: byte/integer sequences (01 03 03 00 patterns) — likely bone indices or strip headers
- **0x2971**: s16 data in range ±30000 — likely quantized vertex positions (scale unknown)
- **0x0660**: identity quaternions (1.0, 0, 0, 0) — bone bind poses

### Open
Vertex scale/stride, index buffer format, UV/normal layout. The s16 quantization
scale factor is the key unknown. Compare against known Urban Reign model dimensions.
