# romD archive format — Tekken 5 PS2 (TK5DATA2.BIN)

Status: **format CRACKED against real bytes 2026-11-08.** The
file-table mapping is SOLVED: romD uses BDPK containers with a BD
directory (not a LUT). 236/242 Devil Within files extracted and
measured. See `DW-DECODE-LOG.md` for the decode and
`tools/romd_extract_full.py` for the extractor. The PS2 LUT
(TK5DATA1 index) is validated separately in the TK5DATA3 Code blob.

## What the repo's own survey established (2026-10-23)

- `TK5DATA2.BIN`, 244 MB, is the **romD archive**. Magic `romD` at offset 0.
- It holds a **CRLF filename manifest** — 498 `.dat` motion/sound/text
  names, preserved in `t5_motion_manifest.txt` (498 lines, one name per
  line, all ending `.dat`, all prefixed `gym_` / `snd_` / `moj_`).
- **99 `BDPK` containers** (the 2026-10-23 survey said 21 — wrong;
  recount from real bytes is 99). They are the file store, not
  section delimiters; see "BDPK containers + BD directory" below.
- The **file-table → data-offset mapping is SOLVED** (2026-11-08):
  BD directory records inside each BDPK container. See below.
- `TK5DATA0.BIN` (2.07 GB), `TK5DATA1.BIN` (1.30 GB),
  `TK5DATA3.BIN` (423 MB) are proprietary binary with no ASCII filenames.
  DW stage geometry, boss AI, meters, rank thresholds live there, not in
  romD. DW markers: 0 hits in the ASCII scan of TK5DATA0/1/3.

## What the community tools document (Tekken5_Tools)

Public repo `smb123w64gb/Tekken5_Tools` (main, commit
`a1df701812e6b263a773f23e725a2a03d7cc27f5`), read as text 2026-11-08.
These tools document LUT tables for **other** archives — not the romD
table. They are the closest known reference and the candidate layouts
`romd_extract.py` tries first.

### The PS2 LUT — indexes TK5DATA1.BIN (1.30 GB)

`FileTableGetPS2.py` (141 lines) + `TK5AssetRipPS2.py` (72 lines):

- The table lives in a **decompressed overlay from TK5DATA3.BIN**:
  `TK5DATA3.BIN` is parsed as a **PKG** container
  (`package_fmt_pkg.PKG`); `files[5]` is NLZ1-decompressed
  (`decNLZ1.unpack_sc3game`) to a blob called "Code"; the table is read
  from that blob. `TK5DATA1.BIN` is the data blob the table indexes.
- Constants: `TABLESTART = 0x0027B5B0`, `CHECKSTART = 0x0027E838`,
  `TABLECOUNT = 1571`.
- Entry (8 bytes): `offset u32 × 0x800`, `size u32`. Offsets are sector
  numbers; sector size is `0x800` (2048 bytes).
- Checksums: a separate `u32` array at `CHECKSTART`; each entry is
  validated with a word-sum checksum (`compute_word_sum_fast`) and, on
  mismatch, decrypted (see cipher below).
- `unarchive` extracts each entry to `outdir/<name>` — names come from
  the caller, not the table.

### The generic LUT — retail NTSC / beta

`FileTableGet.py` (123 lines):

- Retail NTSC: `TABLESTART = 0x002F82B4`, `TABLECOUNT = 5004`.
  Beta: `TABLESTART = 0x26F63C`, `TABLECOUNT = 3030`.
- Entry (40 bytes, 10 x u32): `offset u32 × 0x800`, `size u32`, `crc[5] u32`,
  `unk0 u32`, `id u32`, `unk1 u32`. Verified by reading `LUT.read` in
  `FileTableGet.py` (it reads 1+1+5+1+1+1 u32 = 40 bytes per entry).
- Entries with `size == 0xFFFFFFFF` are empty slots and are skipped.
- Output files are named `%04i_%04x.bin` (index_id) — the table carries
  no filenames.
- Every entry is decrypted with the sector cipher (seed = entry `id`),
  then passed to `tk5psp_dec.decompress_blob`. Decompress fallback: if
  the decompressed output is shorter than the input, the original
  (decrypted) bytes are written instead; on `IndexError`, the original
  bytes are written.
- Active constants in the file as committed are the **Beta** ones
  (`TABLESTART = 0x26F63C`, `TABLECOUNT = 3030`); the Retail NTSC
  constants (`0x002F82B4`, 5004) are commented out.

### The sector cipher — tk5psp_crypt.py (read in full, 60 lines)

`decrypt_sector_data_fast(data, seed, size)`, in place:

- Keystream: 512 `u32` words from an LCG — `key = key * 5 + 3`
  (mod 2^32), starting from `seed`. Packed little-endian (2048 bytes).
- Data is XORed in 2048-byte blocks with the whole keystream; the tail
  (remainder words) uses the first `rem_len` keystream bytes.
- `seed` is the LUT entry's `id`. The cipher is its own inverse
  (encrypt = decrypt).

`romd_extract.py` ports this cipher exactly, credited to Tekken5_Tools.

### PKG + NLZ1 (not yet read — owed)

- `package_fmt_pkg.py` (PKG container) and `decNLZ1.py` (NLZ1
  decompression, `unpack_sc3game`) were listed but **not read** in this
  pass. The PKG layout and the NLZ1 format are owed before the
  TK5DATA3 overlay route can be reproduced. `TK5AssetRipPS2.py` shows
  the shape: PKG parse → `files[5]` → NLZ1 decompress → table.
- `NUDP.hexpat` / `BoneFIle.hexpat` (ImHex patterns for the model
  container and bone data) and `FileTableGet2x6.py` /
  `FileTableGetPS3.py` were listed but not read. They matter for
  decoding `.dat` motion/model contents once files are extracted.

### File headers inside extracted data (TekkenMods tutorial)

From `tekkenmods.com/article/48` (extracting vanilla Tekken 5 assets):

- `NUDP` (`4E554450`) — model container.
- `TIM2` (`54494D32`) — texture.
- `MIF` (`4D4946`) — bone data.
- The tutorial states the retail PS2 version's stages/characters are
  obfuscated and **only the Devil Within data is extractable** because
  it is not encrypted. CAUTION: that claim is about arcade Tekken 5.1
  BIN files (`TK5AC1.BIN`), not the PS2 retail romD archive — do not
  conflate the two. Whether romD's DW `.dat` files are encrypted is
  UNPROVEN until bytes exist.

## What romD's own table is — SOLVED (2026-11-08, real bytes)

romD does NOT use a LUT. It uses **BDPK containers with a BD
directory**. Measured from `TK5DATA2.BIN` (244,426,640 bytes);
extractor: `tools/romd_extract_full.py`.

### BDPK container

```
offset 0:  "BDPK"            (4 bytes)
offset 4:  u32 A             entry count (number of BD records)
offset 8:  u32 B             payload size in bytes
offset 12: payload (B bytes)
```

99 containers; total BDPK payload 167,172,864 bytes. A values
observed: 0, 1, 2, 3, 4, 5, 6, 13, 27, 51, 54, 71, 80, 86, 91, 99,
103, 104, 105, 108, 110, 114, 115, 116, 123, 136, 138, 140, 143,
144, 145, 148, 151, 274. A=0 containers hold no files. One
`BDPK` hit is nested inside another container's payload (a false
hit, not a container). Containers tile the archive with small gaps;
the gaps hold name-list blocks, the offset-16 text file, and the
~74 MB tail (motion data + compressed blobs + textures).

### Payload layout

```
payload+0:    116-byte prefix — a fixed bone/skeleton block
              (first 32 bytes identical across containers:
              ca a5 00 40 58 47 01 40 00 00 00 40 14 f0 ff bf
              a8 a3 07 08 ...)
payload+116:  A × 128-byte BD directory records
payload+116+A*128: file data, in directory order
payload+B-12: 12-byte trailer (content unassigned)
```

### BD directory record (128 bytes)

```
offset 0:   "BD"            (2 bytes)
offset 2:   u16 type        0=gym_ motion, 1=obj_ object, 2=nut_,
                            3=(1 file, unassigned), 4=snd_ sound,
                            5=cap_ font, 8=moj_ stage
offset 4:   u32 X           per-file value, UNRESOLVED (clusters by
                            character group, e.g. amt3 motions
                            X≈12123–12176 — possibly a motion/group ID)
offset 8:   u32 Y           FILE SIZE in bytes
offset 12:  8 bytes         mostly zero (occasionally small values)
offset 20:  filename WITHOUT ".dat", NUL-terminated, zero-padded
            to fill the 128-byte record
```

**File data:** the files follow the directory in record order,
each exactly Y bytes, back to back. Validation that holds on
every extracted container: record count == A, and the Y values
sum to (data region − 12) exactly (the 12-byte trailer). Some
containers have empty directory slots (all zeros, or zeros + a
stray float −1.857) — those hold no file and contribute Y=0.

### Name-list blocks (NOT a manifest)

97 text blocks in the gaps between containers (5,780 name lines,
1,143 unique names): stage-pack load lists (`bhb_`/`gym_`/`obj_`/
`snd_`/`moj_`/`nut_`/`cap_` names, CRLF-separated). They are load
lists, NOT the archive index — a name in a list does not mean the
file is stored in a container (6 DW names are list-only). 15 of
the 97 blocks are false positives (binary motion data that
happens to contain name-like ASCII).

### The offset-16 text file

Bytes [16, 0x1b30) (6,944 bytes) are a plain-text file:
`snd_c02lei.dat` — Lei's sound-position definitions (`lab_A/B`,
`blu_A/B`, `szk`, ... with 3D coordinates + angles + Shift-JIS
labels) followed by a binary `.evd` event-script section
(NAME/TYPE/MODE/NAME_ID/LOAD_FILENAME/LOAD_TYPE/LOAD_LEVEL,
`TEG_0.01`, `leload_testmap1_1`, `EV_TYPE_LOAD`, `START_BLK`,
`testmap2_001`, `END`). It is stored raw, not in a container.

### No romD table in TK5DATA3 / Code / SLUS

Searched and found absent: no `romD`, no `TK5DATA2`, no `.dat`,
no `gym_` names in the TK5DATA3 Code blob, SLUS_210.59, or
TK5DATA4.BIN. The romD index lives ONLY in the BDPK containers.

## Gym motion format (`gym_*.dat`) — header decoded

Magic `GYM1` at offset 0x40 (64) in every gym file. 32-byte
little-endian u16 header:

| Field | Meaning (measured) |
|---|---|
| [1] | bone count: 35 (fighter motions), 78/111/96 (`init_obj`), 12 (`djin`), 4 (7 special kob2/ozb3 files) |
| [2] | frame count |
| [3] | 276 (motions); = bones×10 (`init_obj`); 108 (`djin`) — UNRESOLVED |
| [5] | 16528 (0x4090) constant; u32 @8 = 0x40900000 = 4.5f |
| [7] | 8192 (0x2000) constant |
| [10] | = bone count × 128 |
| [12] | = frames × bones × 12 (standard subtype: 420 values/frame at 35 bones) |
| [14] | 68 / 180 / 15 — UNRESOLVED |

Each bone carries **12 values per frame**. Two subtypes:
- **Standard:** field12 == frames×bones×12 (per-frame data).
- **Sparse (14 clips):** field12 much smaller (11–135 values/frame)
  — only changed channels recorded. The long/special motions
  (`ozb3_dead` 500f, `ozb3_toujyou` 460f, `kob2_escape` 321f,
  projectile attacks, throws). A retarget must handle both.
- The keyframe stream after the header is a variable-length
  record encoding (`ff ff` separators); the bit-exact packing is
  NOT yet reversed. Frame/bone counts are measured for all 236
  extracted DW files in `dw_measurements.json` (214 motion clips,
  17,553 frames, ~292 s at 60 fps).

## Stage map objects (`moj_stg*.dat`) — geometry, not text

CORRECTION (2026-11-08): `moj_stg*` are stage MAP OBJECT files
(`.moj`), not stage text. Each starts with the dev build path
`C:\temp\mapobj\stgNN.moj`, then effect-archive references
(`stgNN_effnud.arc`, `stgNN_effmif.arc`, `stgNN.efp`,
`stgNN_effnut.arc`), then NUDP model containers + TIM2 textures
+ MIF bone data. Measured: stg00 1,916,672 B (29 NUDP / 29 TIM2 /
56 MIF); stg01 872,320 B (18/18/18); stg02 1,392,384 B (20/20/22);
stg04 200,192 B (3/3/3). `moj_stg03` does not exist. The NUDP/MIF
contents (positions, collision) are NOT yet parsed.

## Sound container (`snd_*.dat`) — P3Dp

17 of 18 `snd_*` files start with magic `P3Dp` (u32 0x70443350).
Header (16 bytes): magic, then u16 fields (0x0A01, a count 8–20,
a second count 8–12, sizes). Entropy ~6.5 (compressed/encoded
audio). Audio payload not decoded. `snd_c02lei.dat` is the
plain-text file above, not P3Dp.

## What the index-level decode found (2026-11-08)

`dw-motion-index.json` — 242 Devil Within files inventoried from the
manifest by name, with romaji glosses and confidence per file:

| Group | Files | Assignment |
|---|---|---|
| `gym_ikdv_*` | 52 | Devil Jin's DW brawler kit (beams, punches, kicks, throws, turns, breakfalls) |
| `gym_kmb1_*` | 39 | Modified Gun Jack — stage 1 boss (machinegun, shotgun, charge shots) |
| `gym_kob2_*` | 29 | True Ogre — stage 3 boss, INFERENCE (fly, fire, horn, tail, snake) |
| `gym_ozb3_*` | 36 | Monstrous Ogre — stage 5 boss, INFERENCE (whirlwind `tatumaki`, stomp `fumi`, burn) |
| `gym_oz_extra` (ozt4/ozhe/oznj) | 6 | Ogre-family extras, boss unassigned |
| `gym_ikt5_*` | 26 | UNRESOLVED gun/fly kit, base + `_mon` monster variants |
| `gym_init_obj_*` | 21 | Boss init 1/2/3/5 (boss4 ABSENT), Jin, devil, monster archetypes power/speed/standard/tricky, 3 test characters |
| `gym_djin_newhane00-03` | 4 | Devil Jin transform — wings/feathers |
| `gym_dw_*` singles | 7 | Face (`dwfkao`), wave (`dwhadoh`), power-up (`dwup`, `dwup_hei`), 3 opaque |
| `moj_stg00/01/02/04` | 4 | Stage MAP OBJECTS (`.moj` geometry: NUDP models + TIM2 textures + MIF bones), NOT text; `moj_stg03` absent |
| `snd_*` | 18 | Lab / Egyptian / blue themes; Lei/Jin/Heihachi/JACK/Devil Jin voices (anchors c02/c10/c15/c21/c30); ogre, ruins, boss, monster, system sounds |

Confidence: 155 high, 56 medium, 31 opaque (tokens not translated).

**Corrections found in this pass:** (1) there are NO plain `stg*.dat`
stage-geometry files in the romD manifest at all — only `moj_stg*`
map objects. An earlier draft said `stg00/01/02/04.dat` exist; that was
wrong. (2) `ikdv` is 52 files including `jump_k` / `jump_p`, which an
earlier enumeration missed. (3) The manifest is 498 single-spaced
lines, not 996. (4) `moj_stg*` are stage map objects (geometry), NOT
stage text — corrected 2026-11-08 from real bytes. (5) `BDPK` count
is 99, not 21. (6) The romD file-table mapping is the BD directory,
not a LUT — solved 2026-11-08.

## Still blocked — exact missing data (revised 2026-11-08)

- `TK5DATA2.BIN` (244 MB) — FETCHED + EXTRACTED (236/242 DW files).
- `TK5DATA3.BIN` (423 MB) — FETCHED, PKG parsed, Code blob saved
  (`TK5DATA3_code.bin` on disk only); the BIN itself was deleted
  2026-11-08 to free quota (SHA-256 `74a50b9843f88c34d817e5737aacc8f09f8de22d810c03ec38e0346e6b83fb79`;
  re-fetchable from the archive item, extent 1646501). PKG
  `files[7]` mask.bin + `files[9]` table NOT extracted.
- `TK5DATA0.BIN` (2.07 GB) — NOT fetched (disk quota).
- `TK5DATA1.BIN` (1.30 GB) — NOT fetched (disk quota); PS2 LUT
  validated in the Code blob, entries tile 99.9% of it.
- `SLUS_210.59` (689 KB bootloader ELF) — FETCHED.
- Recorded source: Internet Archive item `slus-210.59.-tekken-5`
  (md5 `5bce17ccabacea46d621d195c4600ebb`, sha1
  `97ca517151229bc1c6a58396ccf470f91676f047`), per
  `teardown/tekken5/INVENTORY.md`. Jay authorized the pull
  2026-11-07 ~20:15. Full-ISO md5/sha1 NOT verifiable (quota-forced
  range-fetch of individual BINs; see `DW-DECODE-LOG.md`).
- Next steps: range-fetch / stream-scan TK5DATA0/1 for meter, gem,
  Force, rank, symbol, and AI tables; reverse the gym keyframe
  stream packing and the NUDP/MIF stage formats; decode P3Dp audio.
