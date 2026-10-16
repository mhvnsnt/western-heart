# Tekken 6 (PSP) — Customization Research

**Lane:** tekken-mining (2026-10-16)
**Source:** `tekken6-psp.iso` (855,638,016 bytes / 816MB, PSP USA)
**Local:** `~/workspace/game-reverse-engineering/tekken6/`
**Status:** MAJOR FINDINGS — item name tables + slot categories located and format-decoded.
Item definition structs (slot/price/model-ref) and item 3D models still locked.

Prior lane context (not duplicated here): sector cipher fully reversed
(`tools/SECTOR-CIPHER-REVERSED.md`), K1/K2 derivation solved
(`docs/K1K2-CALL-SITE-ANALYSIS.md`), 384MB decrypted bulk + 478-file manifest
(`work/decrypt3/`), custom-inflate work ACTIVE 2026-10-16
(`work/decrypt6/DYNAMIC-BLOCKER-2026-10-16.md` — do not duplicate; this lane stayed read-only).

---

## 1. Customization type system (from decrypted EBOOT)

`decrypted/EBOOT.DECRYPTED.ELF` string table contains the game's own type names:

- `sbcustomize_item_t` — the item record type (definition struct — location TBD, §5)
- `tcb_CustomizePSP_Manager`, `tcb_customize_mode_t`, `tcb_gamemode_customize_t`
- Pack filename patterns (how item model packs are loaded):
  - `CUSTOMIZEPACK%d_%d`
  - `HAIRCUSTOMIZEPACK%d`
  - `DEFAULTPACK%d`

## 2. Item NAME tables — FOUND (this lane)

**Where:** inside the 384MB decrypted bulk (`work/decrypt3/bulk_decrypted.bin`),
in regions the 478-entry manifest does not cover (manifest maps 195MB of 384MB).

**Record format** (verified across 10,495 records via full-bulk scan):
```
u32  rec_size        # total record bytes (stride to next record)
u8   item_idx        # item index byte
char name[rec_size-5] # ASCII, null-padded
```

**Tables:** per-language copies (English, Italian, French, German, …).
Sample English records (bulk offset ~66.3MB):
`Sledgehammer`, `Japanese Sword`, `Broadsword`, `Tonfa`, `Chinese Sword`,
`Leather Pants`, `Army Pants`, `Cargo Pants`, `Kung Fu Pants`, `Police Pants`,
`1P Bottom`, `2P Bottom`, `Long Jin Bangs`, `Wild Curled-Out`, `Twisted Braid`,
`Ducktail`, `Topknot`, `Samurai`, `Ki (Pink)`, `Aura (Red)`, `Ki (Red)`,
`Default Effect`, `Effect (Gold/Blue/Green/Red)`, `Comic Effect (English/Japanese)`,
`SP Rage (Lightning/Ice/Fire/White/Black/Yellow)`, `Default Rage`

German table (~74.9MB): `Tanktop`, `Shirt mit weitem Kragen`, …
Italian table (~102.8MB): `Ciuffo all'infuori (D)`, `Coda lunga (bassa)`, `Treccia a spirale`, …
French strings: `Veste matelassée`, `Torse nu`, `Veste biker`

**Scan method:** `/tmp/scan_tables2.py` (regex candidate scan in 48MB slices +
strict record validation + consecutive-run clustering). Results: `/tmp/item_tables.json`
(top runs; clustering is conservative — logical tables are longer than the 31–32-record
fragments reported).

## 3. Slot categories + UI strings — FOUND (NTXL string tables)

**Container:** `NTXL` magic — 120 valid tables in the bulk (~10KB each, per-language copies).
51 of them are in the 478-entry manifest (magics `bin_e6.3`/`bin_e7.8`); the rest sit in
unmapped bulk regions.

**NTXL header sketch** (entry 82, English, 6832 bytes):
```
+0:  "NTXL"
+4:  u16 version (=2), u16 lang_id (3 = English)
+8:  u32 total_size
+12: u32 table_offset (=0x30)
+16..: (u32 msg_id, u32 str_offset) entries — exact mapping TBD
```

**Customization slot categories confirmed** (entry 82 strings):
- `Hair - Back`, `Hair - Front (Right)`, `Face - Other`
- (full category list spans multiple NTXL tables; enumerate all 120 for completeness)

**Customization UI strings** (entry 82, English): `Select item to equip.`,
`This item is already equipped.`, `Purchase item?`, `Equip item?`, `Sell item?`,
`Purchased item.`, `Equipped item.`, `Item sold.`,
`The hair item must be removed to equip this item.`,
`There are 1,500 items in your inventory.`, …

## 4. Item 3D models — format known, extraction in progress (other lane)

- Container: `NDPP` magic, 20-byte header (`NDPP` + u32 size/count + u32 flags + 8 reserved),
  raw float vertex data (positions/normals verified as unit vectors)
- Locations: the 81MB character archive (entry 87, likely 40 characters × ~2MB),
  56 GZIP dynamic files (inflate lane active), plaintext NDPP sections
- Textures: `NTPP` (52 files); animations: `MOTA`
- **Not pushed to this repo** (proprietary Namco geometry — documented here only, per lane rule)

## 5. Still locked

1. **`sbcustomize_item_t` definition array** — the struct holding slot/category, price,
   character eligibility, and model-pack reference per item. Not yet located; candidates:
   EBOOT data segment, or a binary table adjacent to the name tables (2KB pre-table region
   captured at `/tmp/t6_items_pre.bin` for analysis).
2. **Full item counts per category** — name-table cluster boundaries need the definition
   array to resolve (item_idx byte is the join key).
3. **Item NDPP models** — blocked on the custom-inflate lane (56 dynamic GZIP files);
   coordinate with `work/decrypt6/` owner before duplicating.
4. **NTXL (msg_id → string) table mapping** — header parsed, entry layout TBD.

## 6. Repro

```bash
# ISO file listing (pycdlib, LGPL-2.1+)
python3 -c "
import pycdlib
iso = pycdlib.PyCdlib(); iso.open('tekken6-psp.iso')
for d, dl, fl in iso.walk(iso_path='/'):
    for f in fl: print(d + '/' + f)
iso.close()"
# EBOOT customization symbols
strings -n 6 decrypted/EBOOT.DECRYPTED.ELF | grep -i custom
# Item name records: scan bulk_decrypted.bin for [u32 size 6..64][u8][ASCII\0][zero pad]
```
