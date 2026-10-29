# Tekken 6 Item-Table Search — Documented Search Report (2026-10-20)

Creation-suite gap-fill, gap #5 of `customization/CREATION-SUITE-WIRING-AUDIT-2026-10-20.md`:
Tekken customization had slot SCHEMAS only (`tekken7-slot-catalog.json`,
`tekken6-slot-catalog.json`, `ttt2-slot-catalog.json`) with no item data, and the
audit named a Tekken 6 item-table search as the next step. This report is that
search, with its coverage stated file by file.

## Result

**Item NAME tables: FOUND (prior lane, documented on main). Item DEFINITION
array: NOT located — that is the remaining named gap.**

- The tekken-mining lane (2026-10-16) found and format-decoded the item name
  tables inside the decrypted DATA401 bulk, and documented it on main in
  `teardown/tekken6-customization-research.md`: **10,495 validated name
  records** — format `u32 rec_size` + `u8 item_idx` + null-padded ASCII name —
  in per-language tables, plus **120 NTXL string tables** carrying the
  customization slot categories and the shop/equip UI strings. Sample English
  names, the NTXL header sketch, and the slot categories are carried into
  `customization/parts/tekken/tekken6-item-catalog.json` with attribution.
- What no held file contains: the **`sbcustomize_item_t` definition array**
  (per item: slot/category, price, character eligibility, model-pack
  reference). The name records' `item_idx` byte is the join key to it. Until
  it is located, names cannot be honestly assigned slots, prices, or
  characters — so `tekken6-item-catalog.json` emits no per-item rows rather
  than guessing them.
- The decrypted bulk the tables live in is **not on main**. It survives in
  release `tekken6-recon-20261016` (`t6-recon-backup.tar`, SHA-256
  `2c738b24f46395960e463fd03c637b038a0942590c0055b9ef3fe1bc9d77afcc`,
  `tekken6/work/decrypt3/bulk_decrypted.bin` inside the tar). The mining
  lane's scan output (`/tmp/item_tables.json`) was local-only and is not on
  any store — so this search re-extracted the tables from the bulk itself
  (§1.5) and shipped the extraction as
  `customization/parts/tekken/tekken6-item-names.json`.
- This search's own EBOOT work (this lane, 2026-10-20) independently
  corroborates the mining lane's §1 and adds the offsets: pack formats
  `CUSTOMIZEPACK%d_%d` / `HAIRCUSTOMIZEPACK%d` / `DEFAULTPACK%d`, the
  `sbcustomize_item_t` RTTI, customize-mode classes, and the 12
  `tcb_kkItemMotionTick*` item-move handlers (catalog, with file offsets).
- This supersedes the earlier undocumented checkpoint one-liner ("T6 item
  tables: none in extracted files") — that claim was wrong about the name
  tables and right only about the still-missing definition array.

## 1. Coverage — exactly what was searched

### 1.1 mhvnsnt/western-heart, `teardown/tekken6/` (main, tree 787ec8613bdb)

69 blobs, 8,799,187 bytes total:

| Set | Files | Bytes | How searched |
|---|---|---|---|
| `decrypted/EBOOT.DECRYPTED.ELF` | 1 | 4,158,144 | Full binary string + pattern search (section 2). Downloaded via git blob API; git blob SHA `02c40bdaa6a81b51f00f9c6638670d727ebb9ca0` verified byte-identical. |
| Text/code: `DATA401-RE-NOTES.md`, `TEARDOWN.md`, `PPSSPP-LIVE-RUN-GUIDE.md`, `decrypted/README.md`, `docs/` (3), `tools/SECTOR-CIPHER-REVERSED.md`, `ui/README.md`, `videos/README.md`, `models/NDPP-FORMAT.md`, `tools/*.py`, `tools/*.c`, `models/tools/*.py` | 21 | 83,876 | Full-text grep for `item`, `custom`, `equip`, `shop`, `price` + read in full where hits existed. Hits only in `TEARDOWN.md`, `DATA401-RE-NOTES.md`, `decrypted/README.md`, `ui/README.md` — all stating the game data is encrypted. The other 17 files: 0 hits for all five keywords. |
| `models/ndpp_bounding_volumes.glb` | 1 | 282,532 | Blob-SHA verified (`22ff999a9b08ca75116dd32969c68b06c7b0a841`); parsed glTF: 220 nodes / 220 meshes, all named `section_NNN` (bounding volumes); ASCII string scan — 0 `item`/`custom`/`equip` strings. |
| `ref_frames/*.jpg` (42), `ui/*.png` (2), `models/previews/*.png` (2) | 46 images | 4,274,635 | Ending frames / icon art — inventoried; not table-bearing formats. |

Plus, outside that directory (found by full-tree listing):
`teardown/tekken6-customization-research.md` (5,435 B — the mining lane's
findings doc, §Result above; read in full) and
`teardown/tekken7/models/king-variants/tekken6-psp/README.md` (King outfit
names from wiki research only — no item data).

### 1.2 mhvnsnt/game-reverse-engineering, `tekken6/` (main)

18 blobs, 4,256,257 bytes total:

| Set | Files | Bytes | How searched |
|---|---|---|---|
| `decrypted/EBOOT.DECRYPTED.ELF` | 1 | 4,158,144 | Same file as 1.1 (the western-heart copy was hash-verified and searched). |
| `extracted/DATA401.IDX` | 1 | 26,028 | Git blob SHA `99783e48cb9643a790d9da13088848e55cea7be0` verified byte-identical. Entropy + plain/XOR string scans (2.4). Still encrypted — the file map the (lost) decrypt lanes were working on; DINF (below) confirms 2,169 entries × 12 bytes. |
| `extracted/DINF_400.BIN` | 1 | 120 | Git blob SHA `a12a4ebdfa5dcf3d1dd016265b9f972c96e4bcfc` verified byte-identical. Same scans (2.4). Its decrypted plaintext is documented on branch `t6-bulk-decrypt` (`DINF-400-DECRYPTED.md`, restored locally 2026-10-20): a pack manifest — magic `DINF`, 2,169 entries, data size 384,051,200 B, build path `hdd65/psp/DATA401/20091109_092921/` — no keys, no item data. |
| Text/code: `TEARDOWN.md`, `PPSSPP-LIVE-RUN-GUIDE.md`, `docs/K1K2-CALL-SITE-ANALYSIS.md`, `tools/` (9) | 12 | 43,901 | Server-side code search (GitHub code search, `path:tekken6`): `customize` 0 files, `item` 0 files, `equip` 0 files, `shop` 0 files. |

Server-side code search over western-heart `path:teardown/tekken6` agrees
with the local grep: `customize` in 2 files (`TEARDOWN.md`,
`decrypted/README.md`), `item` in 2 files (`TEARDOWN.md`,
`DATA401-RE-NOTES.md`), `equip` in 0 files, `shop` in 0 files.

### 1.3 Releases

- `western-heart` release `tekken6-recon-20261016`: `t6-recon-backup.tar`
  (1,131,284,480 B reassembled; SHA-256
  `2c738b24f46395960e463fd03c637b038a0942590c0055b9ef3fe1bc9d77afcc`)
  contains the full local `tekken6/` tree of 2026-10-16 — 5,323 files
  including `work/decrypt3/` (the decrypted bulk + 478-entry manifest).
  This is the store copy of the name tables' source data (§Result).
- `western-heart` release `tekken6-ps3-full-v1`: TEKKEN.psarc split into
  10 parts (524,288,000 B × 9 + 112,901,723 B) + manifest (reassembled
  psarc SHA-256 `c98fb02602d58564ef4e80d386310cb3c48634566990a5050ef20ef2a4afd340`)
  + one 524,288,000 B tar part. **Not searched**: two download attempts from
  this environment failed — `gh api` asset download of part_aa returned
  23 MB of non-tar, non-PSAR bytes against the expected 524,288,000 B, and
  a ranged request returned 0 bytes. The PS3 set is an explicitly UNCOVERED
  set, listed here rather than silently skipped.
- `western-heart` releases `tekken6-psp-v1` (ISO, 855,638,016 B) and
  `tekken6-endings-v1` (46 PMF videos), and `game-reverse-engineering`
  release `tekken6-psp-v1` (same ISO): the ISO's filesystem contents are
  exactly the sets in 1.1/1.2 per the ISO map in `TEARDOWN.md` (EBOOT →
  decrypted, searched; IDX/DINF → searched; 46 PMF videos → video data) plus
  the 384 MB raw-sector region whose decrypted form is the bulk in the
  recon tar. The PMF videos were not re-downloaded: video streams cannot
  contain an item table, and their reference frames are already in 1.1.

### 1.4 Local disk (this machine, checked 2026-10-20)

`~/workspace/game-reverse-engineering/tekken6/` holds only the skeleton
restored 2026-10-20 from GitHub (`RESTORE-NOTE-2026-10-20.md`): **no
`work/` directory** — `work/decrypt3/` and `work/decrypt6/` are not in that
tree (decrypt6's files are recorded as lost in that note; decrypt3 survives
in the recon tar, §1.3). A filesystem-wide find for `item_tables.json`
returned no file. For `bulk_decrypted.bin` the find located one further
copy in another lane's transient scratch
(`~/workspace/_t6r3-scratch/work/tekken6/work/decrypt3/bulk_decrypted.bin`,
present during the search on 2026-10-20 and cleared by its lane shortly
after; correction added the same day). That copy was not used: every
extraction in §1.5 was made from the SHA-256-verified recon tar (§1.3).

### 1.5 First-hand validation on the bulk (this lane, 2026-10-20)

The recon tar was downloaded (parts 524,288,000 + 524,288,000 + 82,708,480 B,
all exact), reassembled, and **SHA-256 verified byte-identical**
(`2c738b24…afcc`). From it, `tekken6/work/decrypt3/` was extracted:
`bulk_decrypted.bin` (384,073,728 B), `manifest.json` (478 entries),
`IDX-FORMAT.md`, and the decrypt3 scripts. On the bulk:

- **Name records re-validated**: the record at bulk offset `0x3F3AA13`
  parses as rec_size 32, item_idx 104, name `Sledgehammer` — the research
  doc's first sample. Chaining forward from it yields 14 consecutive valid
  records (Japanese Sword 101, Broadsword 102, Tonfa 103, Chinese Sword
  100, Default Effect 18/19, Effect (Blue/Red/White/Black) 20–23, Comic
  Effect (English/Japanese) 24/25, SP Rage (Lightning) 15).
- **Full-bulk re-scan** (prefix scan for u32 rec_size 6..64, strict
  validation — printable ASCII name, null-only padding — run chaining):
  **11,053 valid record starts; 9,440 records in 768 runs of ≥ 4; largest
  run 32 records** (matching the research doc's 31–32-record fragments);
  item_idx range **1–160** (160 distinct values — the index is per-table /
  per-category). The mining lane's 10,495 count used looser clustering;
  both scans agree on format, run size, and samples. All 9,440 records
  (bulk_offset + item_idx + name, all language tables — the tables
  interleave in unmapped bulk regions, so per-record language attribution
  is not claimed) are shipped in `tekken6-item-names.json`.
- **NTXL spot-check**: the table at bulk offset `0x1AB2000` has header
  bytes `4E54584C 0200 0300 B01A0000 30000000` = NTXL, version 2,
  lang_id 3 (English), total_size **6832**, table_offset 0x30 —
  byte-identical to the research doc's entry-82 sketch — and its strings
  verify in place (`Select item to equip.`, `Purchase item?`, `Sell item?`,
  `Not enough money.`, `Display items in the "Hair - Back" category.`, …).
  Raw `NTXL` magic occurrences in the bulk: 1,328 (the research doc's 120
  is the count of *valid* tables after header checks).
- **Definition array**: not found by this lane either. No
  slot/price-shaped binary array was identified adjacent to the name-table
  runs scanned; a dedicated hunt (EBOOT data segment + the pre-table
  regions) remains the unblock step (§4). No candidate is claimed here —
  the scan above covered name records and NTXL only.

## 2. Patterns used (this lane, on the decrypted EBOOT unless stated)

The shape item data would take is the Tekken 7 item CSV spec in
`tekken7-slot-catalog.json` (21 fields: ShopID, packageIndex, CCI_Reference,
Unknown_D, charId, slotId, Unknown_G, NameByID, ItemName, Unknown_J,
SlotGroupID, Unknown_L, PlayerCusID, SlotColors, Unknown_O, Rarity,
packageId, ItemCost, Unknown_S, AdditionalText, Unknown_U).

1. **ASCII strings ≥ 4 chars**: 15,912 strings extracted. Keyword counts:
   `equip` 0, `shop` 0, `buy` 0, `sell` 0, `price` 0, `aura` 0, `helmet` 0,
   `glasses` 0, `item` 30 (all C++ type names — `tcb_kkItemMotion*`, see
   catalog), `custom*` 19 (type names / pack formats / the `CUSTOMIZE` menu
   string), `gold` 9 (all Gold Rush mode, not item currency).
2. **T7 CSV row shape** (regex `\d+,-1,<ref>,\d+,\d+,\d+`): **0 matches.**
   **Item-name pattern** (`[A-Z]{3}_CUS_\d+`): **0 matches.** Any `*_CUS_*`
   code: **0 matches.** (Expected in hindsight: T6 predates the T7 CSV/asset
   scheme — its name data is the binary record format in §Result.)
3. **UTF-16LE strings ≥ 4 chars**: 34 candidates, all false-positive byte
   patterns — no readable names.
4. **Shift-JIS scan** (double-byte + kana ranges, ≥ 8 units): 204 candidates
   in the code range, 130 in the data range ≥ file offset 0x380000 — every
   candidate is gibberish fragments of code/binary tables; **0 readable
   Japanese words**. (T6 PSP's text lives in the bulk's NTXL tables, not in
   the EBOOT — consistent with the mining lane's find.)
5. **DATA401.IDX / DINF_400.BIN**: IDX Shannon entropy **7.993** (26,028 B);
   plain ASCII runs ≥ 6 chars: 41, all random; under the EBOOT's known
   XOR-0xA5 string cipher: 46 runs, all gibberish. DINF (120 B): entropy
   6.444, 93 unique byte values; 0 ASCII runs plain or XOR-0xA5. Both files
   are encrypted in their stored form (DINF's decrypt is documented on the
   `t6-bulk-decrypt` branch — manifest only, §1.2).
6. **Filename/format-string scan**: the only customization data references
   in the EBOOT are `CUSTOMIZEPACK%d_%d` (file offset 0x38F080, vaddr
   0x8B92080), `HAIRCUSTOMIZEPACK%d` (0x38F05C / 0x8B9205C), `DEFAULTPACK%d`
   (0x38F070 / 0x8B92070). Vaddr conversion `vaddr = file_offset + 0x8803000`
   validated against two independently documented strings: `openPac` at
   file 0x3CB704 → 0x8BCE704 and `ktRead` at file 0x3CB73C → 0x8BCE73C,
   both matching `DATA401-RE-NOTES.md`.

## 3. What was recovered (in tekken6-item-catalog.json)

- Item name tables: record format, validated record count (10,495),
  per-language layout, bulk offsets per language, 26 sample English names —
  all from `teardown/tekken6-customization-research.md` §2, attributed.
- NTXL string tables: container sketch, confirmed slot categories
  (`Hair - Back`, `Hair - Front (Right)`, `Face - Other` — finer-grained
  than the 4-slot schema in `tekken6-slot-catalog.json`), and 10
  customization UI strings including `Purchase item?`, `Sell item?`,
  `Select item to equip.` — research doc §3, attributed.
- EBOOT evidence (this lane): 3 pack formats with offsets/vaddrs, the
  `sbcustomize_item_t` RTTI (6 strings), 8 customize-mode/manager strings,
  and the 12 `tcb_kkItemMotionTick*` handlers at file offsets
  0x3871B0–0x38739C (Simple, AnnaSyringe, Sake, PakuPakuPanda, Cannon,
  Koara, Toad, BobPigeon, BryanShotgun, LeiHandgun, BonusParts,
  BonusMissilePod). Character names inside handler names are recorded as
  name-implied only.

## 4. Named gap + unblock path

**Gap `T6-ITEM-DEFINITIONS`**: the `sbcustomize_item_t` definition array
(slot/category, price, character eligibility, model-pack reference per
item). Candidates per the research doc: the EBOOT data segment, or a binary
table adjacent to the name tables (a 2 KB pre-table region was captured by
the mining lane). Unblock steps, in order:
1. ~~Re-extract the full name tables from `bulk_decrypted.bin`~~ — DONE by
   this search (§1.5): 9,440 records shipped in `tekken6-item-names.json`.
2. Scan the bulk regions adjacent to the name tables (and the EBOOT data
   segment) for the definition array, joining on `item_idx`.
3. Enumerate all 120 NTXL tables for the full slot-category list (updates
   the 4-slot schema in `tekken6-slot-catalog.json`).
The PS3 `TEKKEN.psarc` set (§1.3, uncovered) is a second source for the
same tables once a working download path exists.
