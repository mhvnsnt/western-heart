# Tekken 6 PSP DATA401.IDX — MAPPING SOLVED (2026-10-24, Lane D)

Supersedes the "IDX contested" status in the teardown audit (PR #1047 §18) and the
Oct 15 decrypt3 32-byte reading. The IDX is decrypted, the file map tiles exactly,
and the bulk splits into 2,093 files. This is NOT T6 100%: voice attribution,
the GZIP second layer, moveset wiring, and playing verification are still owed
(see Open items). Nothing here claims them.

## Solved mapping (verified, reproducible with `tools/t6_idx_solve.py`)
- Cipher: EBOOT `0x8AA2CA8` stream-cipher model, keyset A from EBOOT `0x8898404`:
  K1=`0xe11cf772`, K2=`0xa0dc9eb4`, applied per 1024-byte block with
  t0 = block byte offset within IDX, t1 = 0.
  Single-call and per-2048-sector variants FAIL (first divergence at byte 1024).
- Entry: 12 bytes, little-endian: `(sector_offset_u32, size_u32, tag_u32)`.
  `sector_offset` is in 2048-byte sectors relative to the DATA401 region start
  (ISO sector 230256; relative sector 0 is the key sector, data starts at 1).
  `size` is in bytes. `size == 0xFFFFFFFF` with `tag == 0` is a sentinel:
  0 sectors, shares the next entry's offset. `size == 0` is an empty file.
- DINF cross-check: `26028 / 12 = 2169` = the DINF entries field exactly.

## Proof (all reproduced 2026-10-24)
- Sentinel-aware tiling: **0 fails over 2,169 entries** (a file's next offset
  always equals its offset + ceil(size/2048), sentinels contributing 0).
- Region fill: first offset 1, last end **187525** = DINF `data_bytes / 2048`
  (384,051,200 / 2048) exactly — the map covers the whole region end to end.
- Bulk cross-check: file starts land on real container magics in
  `bulk_decrypted.bin` (global bulk keys `0x24cfa8a4/0x564928df`, per-sector
  t0 = bulk-relative byte offset): first 100 real starts hit 13 NTPP + 1 MOTA;
  first 500 hit 24 NTPP + 1 MOTA. Random offsets would hit ~0.
- Keyset B (DINF keys) on IDX: 6/2169 plausible, tiling fails — not the IDX key.
- Prior "89/2169 plausible" for keyset A was the first ~85 entries decrypting
  correctly under the wrong (single-call) framing plus chance hits; the
  per-1024/t0=byte-offset framing turns those 85 into all 2,169.

## Why the Oct 15 32-byte reading is not the layout
- The 32-byte parse needs a phantom 12-byte header (`12 + 813 x 32 = 26028`)
  and contradicts DINF's 2,169 count; the 12-byte parse needs no header.
- Its "H1 chaining" (108/108) is entailed by the 12-byte tiling: a 32-byte
  window over tiling triples satisfies the same two chaining equations
  wherever it aligns to triple boundaries. Its "KEY entries" are the
  windows that do not align. Both readings describe one byte stream; only
  the 12-byte reading matches the entry count and tiles with 0 fails.
- IDX field 3 (`tag`) is NOT crc32/adler32/md5-first-word of file content
  (tested on 14 entries). It repeats for same-size duplicate pairs
  (entries 8/9; 250/2098 share tag and size), consistent with a name/path
  hash or logical-file id. Extraction needs only offset + size.

## Census of the split bulk (CPU baseline 98.5s, VM 2026-10-24)
- 2,169 entries = 2,093 real (238 empty) + 76 sentinels; real bytes 381,988,891
  (remainder to 384,051,200 is per-file sector padding).
- Kinds at file starts: MOTA 1, NTPP 139, NTXL 120, GZIP 130, GZIP+prefix16 86,
  other 1,378, ASCII 1. Entry 0 (2,234,188 bytes) is MOTA — motion data.
- Largest file: entry 2150, 42,993,400 bytes, entropy 6.805, table-headed
  (unidentified container — not claimed as anything).

## Voice banks (inventory: `T6-VOICE-BANK-INVENTORY-2026-10-24.json`)
- Bank container: header `[0x00010201, 0, group, nstreams, data_start,
  data_size, 32, first_rec_off, offset table...]`; at3 records
  `(tag 'at3', group, pos, 3, 0, size, data_off, 64)`; `pos` = stream index
  (sparse — gaps between recorded streams hold unrecorded streams).
- 117 at3 banks, **338 recorded streams with exact cue ranges**
  (file offset + size from records, never invented), 46 gap regions holding
  115 gap streams (byte-exact regions; internal split TBD by AT3-frame /
  validated-RIFF decode — RIFF bytes inside payloads mean RIFF-scan splits
  alone are NOT claimed).
- 40 character pairs: entries 1983–2022 (groups 23, 25, …, 101) paired with
  entries 2050–2089 (groups 24, 26, …, 102). BGM: groups 0–18
  (entries 2023–2043; 2037/2038 are sentinels). Single-stream banks
  (groups 108–124 etc.) include music-length files.
- The same `0x00010201` magic also heads non-audio containers (entries
  66–69, 258–259, 767+, with header stream counts up to 194 and no at3
  records) — those are cataloged separately, not voice banks.

## GPU jobs (`gpu-jobs/`, prepared for Kaggle T4 x2 — NOT run here)
- Local VM has no GPU (no nvidia-smi, no torch). Jobs 1–3 + coordinator
  sheet are prepared for the coordinator's browser lane; no GPU run, timing,
  or speedup is claimed in this PR. Measured CPU baselines: IDX grid
  ~1.6s/20 combos, census 98.5s, audio tag scan 3.1s (first 256KB x 2,093).

## Open items (active paths, not resting places)
1. **King pair attribution (blocks Pantera voice lock):** pairs are indexed
   0–39 by entry/group only. NO pair is claimed as King. Paths: (a) PS3
   `TEKKEN.psarc` filenames (parts ad–aj still to download; parts aa–ac
   local but headerless — container unidentified); (b) owner ear-check of
   decoded clips. Stage sounds/music/SFX are never presented as dialogue.
2. **GZIP second layer:** 216 GZIP/GZIP+prefix16 files bulk-decrypt to a
   GZIP header whose zlib body fails decompression (Oct 15 finding).
   Needs the per-file key derivation or custom decompressor from EBOOT.
3. **Moveset/animation wiring + playing verification:** MOTA/NTPP/NTXL
   decode and wire-in belong to the moveset/audio lanes with this map;
   nothing is wired or played in this PR. T6 is NOT 100% until that work
   is merged, deployed, and verified by playing.
4. **Non-audio `0x00010201` containers** (entries 66–69, 258–259, 767+):
   format TBD; not voice, not claimed otherwise.

## Files in this PR (docs/tools only — no raw game bytes, no audio)
- `teardown/tekken6/T6-IDX-SOLVED-2026-10-24.md` (this doc)
- `teardown/tekken6/tools/t6_idx_solve.py` (solver + verifier, self-contained)
- `teardown/tekken6/tools/t6_bank_inventory.py` (bank inventory builder)
- `teardown/tekken6/T6-VOICE-BANK-INVENTORY-2026-10-24.json` (offsets/sizes only)
- `teardown/tekken6/gpu-jobs/job1_idx_grid.py`, `job2_bulk_census.py`,
  `job3_audio_split.py`, `COORDINATOR-SHEET.md`
