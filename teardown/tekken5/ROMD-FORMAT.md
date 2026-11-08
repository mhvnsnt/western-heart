# romD archive format — Tekken 5 PS2 (TK5DATA2.BIN)

Status: **format documented from survey + community tools; table layout
UNVALIDATED against real bytes.** No `TK5DATA2.BIN` exists in the repo or
on disk anywhere found (2026-11-08). The ISO was deleted after the
2026-10-23 survey; only the 498-name manifest survives. See
`DW-DECODE-LOG.md` for the blocker and `tools/romd_extract.py` for the
reader that runs the moment bytes exist.

## What the repo's own survey established (2026-10-23)

- `TK5DATA2.BIN`, 244 MB, is the **romD archive**. Magic `romD` at offset 0.
- It holds a **CRLF filename manifest** — 498 `.dat` motion/sound/text
  names, preserved in `t5_motion_manifest.txt` (498 lines, one name per
  line, all ending `.dat`, all prefixed `gym_` / `snd_` / `moj_`).
- **21 `BDPK` markers** inside the archive. Purpose unknown — possibly
  section delimiters. Their offsets were never recorded; the scanner in
  `romd_extract.py` lists them when bytes exist.
- The **file-table → data-offset mapping was never reversed**. That is
  the blocker this decode ran into: names are known, offsets/sizes are not.
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

## What romD's own table is — UNKNOWN

- Neither documented LUT is proven to be the romD table. The romD
  manifest gives 498 names; the PS2 LUT has 1571 entries (indexes
  TK5DATA1, not romD); the generic LUT has 5004 (retail) / 3030 (beta)
  entries. None of those counts is 498.
- Working hypothesis (UNPROVEN): romD follows the same Namco LUT
  pattern — a table of (sector, size) entries in the same entry shapes,
  with the 498-name manifest order matching table order (typical for
  these archives). `romd_extract.py --scan` hunts for candidate tables
  by that shape and reports them; extraction needs a confirmed table.
- The 21 `BDPK` markers may delimit 21 sections (motions / sounds /
  text / stages …) — unproven.

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
| `moj_stg00/01/02/04` | 4 | Stage text/messages (NOT geometry); `moj_stg03` absent |
| `snd_*` | 18 | Lab / Egyptian / blue themes; Lei/Jin/Heihachi/JACK/Devil Jin voices (anchors c02/c10/c15/c21/c30); ogre, ruins, boss, monster, system sounds |

Confidence: 155 high, 56 medium, 31 opaque (tokens not translated).

**Corrections found in this pass:** (1) there are NO plain `stg*.dat`
stage-geometry files in the romD manifest at all — only `moj_stg*`
text. An earlier draft said `stg00/01/02/04.dat` exist; that was
wrong. Stage geometry lives in TK5DATA0/1/3. (2) `ikdv` is 52 files
including `jump_k` / `jump_p`, which an earlier enumeration missed.
(3) The manifest is 498 single-spaced lines, not 996.

## Still blocked — exact missing data

- `TK5DATA2.BIN` (244 MB) — the 498 named files themselves.
- `TK5DATA0.BIN` (2.07 GB) — stage geometry, boss AI, meters, rank thresholds.
- `TK5DATA1.BIN` (1.30 GB) + `TK5DATA3.BIN` (423 MB) — data/code archives.
- `SLUS_210.59` (689 KB bootloader ELF).
- Recorded source: Internet Archive item `slus-210.59.-tekken-5`
  (md5 `5bce17ccabacea46d621d195c4600ebb`, sha1
  `97ca517151229bc1c6a58396ccf470f91676f047`), per
  `teardown/tekken5/INVENTORY.md`. Re-supply must come from Jay's own
  disc or that item — do NOT download a Tekken 5 ISO from the internet
  without Jay supplying it.
- When bytes exist: run `tools/romd_extract.py` (`--scan`, then
  `--extract` with a confirmed table), then decode the `.dat` contents
  (motion format, stage geometry, boss/enemy tables, meter and rank
  numbers) against the `NUDP` / `TIM2` / `MIF` headers and the ImHex
  patterns.
