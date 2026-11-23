# KoC2 file 02010 + file 01999 format notes

Reverse-engineered 2026-11-19, lane W2 (VPW2 + KoC2 RE). Tools:
`tools/koc2_file02010.py`, `tools/koc2_file01999.py`;
data: `data/koc2-file02010-records.json`, `data/koc2-file01999-survey.json`.

## 1. File 02010 is the string/metadata table, NOT the wrestler-data store

Correction to the original task premise: file 02010's binary region is a
**per-string metadata table** (one 32-byte record per string). It holds
names, enums, flags, and small ratings — but no movesets, no full stats,
no COM Logic. The real per-wrestler data (movesets, stats, finishers,
costumes) lives in **file 01999, the `WrestlerData` chunk** (§3 below),
which the ELF's data loader (0x1164d0) loads by file id 0x7CF = 1999,
next to `PartyData` (file 2000) and `TeamData` (file 2001).

## 2. File 02010 layout (197,125 bytes) — CRACKED, fully verified

```
0x0000  header: u32 category_count (= 25),
               u32 total_logical_strings (= 4021),
               u32 string_table_bytes (= 68237)
0x0010  category index: 25 x (u16 id, u16 count, u32 first_logical_index)
0x00D8  record table: 4021 x 32 bytes
0x1F778 string table: 68,237 bytes of NUL-terminated Shift-JIS
```

### 2.1 Logical vs physical strings

The physical string table holds **4023** strings, but the game's logical
numbering has 4021: two empty physical strings (indices **581** and
**1354**) are skipped. A third empty string (physical 2285) IS a logical
entry (logical 2283, the last entry of category 14, costume feet).

```
logical i -> physical i       (i < 581)
logical i -> physical i + 1   (581 <= i < 1353)
logical i -> physical i + 2   (i >= 1353)
```

Category boundaries in the header are in LOGICAL numbering. (This also
explains the earlier confusion about category 15: logical 2284 is
physical 2286 = 藤波 辰爾, the first wrestler name; physical 2284 is a
shoe that belongs to category 14.)

### 2.2 The 32-byte record (one per logical string, in order)

Verified against all 4021 records:

| Offset | Field | Verification |
|--------|-------|--------------|
| 0x00 | u32 string offset (into the physical string table) | 4021/4021 match |
| 0x04 | u16 `person_id` (cat 0; see §2.3) / per-category value | — |
| 0x06 | u8 category index (0–24) | 4021/4021 match |
| 0x07 | u8 federation (cat 0; see §2.3) / per-category value | — |
| 0x08 | u32: 0xFFF for wrestlers, 0 for staff (cat 0) | 402 wrestlers / 27 staff |
| 0x0C | u8 0xFF (cat 0, all records) | — |
| 0x0D | u8, mostly 0 (cat 0; 8 records have 110–113, sequential pairs) | — |
| 0x0E | u8: 1 for cat 0, 0 for cat 15, 0/3 elsewhere | — |
| 0x0F | u8 small enum (cat 0: 0–11, modes 11/3) | — |
| 0x10 | u16 bitfield (cat 0: 0, 2, 7, 0xFF, 0x2FF, ...) | — |
| 0x12 | u16 bitfield (cat 0: 0xFFFF for 363 records) | — |
| 0x14–0x18 | five bytes, 0–9 each (cat 0; byte @0x16 is only 4/5) | — |
| 0x19 | u8 0 (cat 0) | — |
| 0x1A | u8: 0 (242), 2 (28), else a sequential id 60+ (cat 0) | — |
| 0x1B | u8 0/1 (cat 0) | — |
| 0x1C | u16 index within category | 4021/4021 match |

Note: byte @0x1C alone equals the index only for the first 256 entries
of a category; the full index is the u16 at 0x1C (low byte @0x1C, high
byte @0x1D).

### 2.3 Category 0 (wrestler names): cracked fields

- **byte @0x07 = federation.** Eight clean contiguous runs, matching the
  FAQ's federation organization:
  - 0 = NJPW (records 0–80, 81 entries)
  - 1 = NOAH (81–127, 47)
  - 2 = AJPW (128–177, 50)
  - 3 = ZERO-ONE (178–212, 35)
  - 4 = WJ (213–219, 7)
  - 5 = Pancrase (416–428, 13 — Funaki, Suzuki, Kondo, ...)
  - 6 = FREE + officials (220–248, 29 — Takayama, Tenryu, Sasaki, plus
    referees Wada, Tiger Hattori, Red Shoes Umino and staff)
  - 7 = ORIGINALS (249–415, 167 fictional wrestlers)
- **u16 @0x04 = person id.** A permutation of 0..427 over the 429
  records, with exactly one duplicate: records 310/311 are both
  室田 鉄彦 (the same person listed twice) and share id 364. So there
  are 428 distinct persons in the 429 entries. The target ordering
  (what list the ids index) is still open — it is NOT the file-01999
  record order and NOT the file-01999 distinct-wrestler order.
- **u32 @0x08 = 0xFFF vs 0.** The 27 records with 0 are the
  non-wrestlers (referees/staff: Wada, Hattori, Umino, ...).
- **Category 15 (wrestler_names_2)** is a near-copy of category 0:
  352/429 records differ only in byte @0x0E (1 in cat 0, 0 in cat 15);
  52 differ in bytes @0x0F/@0x10 as well (mostly version entries).
- **Still open (cat 0):** byte @0x0F enum (0–11), byte @0x1E enum
  (modes 1/5/2), the five 0–9 bytes @0x14–0x18 (ratings? — byte @0x16
  is only ever 4 or 5, so not five plain ratings), the @0x10/@0x12
  bitfields, byte @0x1A sequential ids, byte @0x0D sequential pairs,
  and the u16 @0x04 target ordering.

## 3. File 01999 — the WrestlerData store (1,252,521 bytes) — SURVEYED

The ELF loader at 0x1164d0 loads file 1999 and resolves the
`WrestlerData` chunk (the chunk names `WrestlerData`/`PartyData`/
`TeamData`/`MoveBase`/`MotionBase`/… live in `.rodata` at 0x3A8B70+;
xrefs found by scanning for `lui 0x3B` + `addiu` pairs — note the
compiler uses hi+1 when the low half is ≥ 0x8000).

```
0x0000  header: u32 group_count (= 255), u32 ??? (= 541), u32 0, u32 0
0x0010  move-group table: 255 x 64 bytes
0x3FD0  wrestler records: 441 x 2285 bytes
0xFA015 tail: 228,500 bytes, sparse (mostly zero)
```

### 3.1 Move-group table (255 x 64 bytes)

Record i starts with u16 i, then 4 move/motion IDs (usually 4
consecutive IDs: record 0 = 0,1,2,3; record 1 = 4,5,6,7; …), u16 count
(= 4), u16 ???, u16 flags (0x0204 common). 104 records have the
alternate shape (u16@10 = 0x2801, u16@14 = 1). The rest of each record
is zero except at most one nonzero byte. 255 groups x 4 moves = 1020
move slots.

### 3.2 Wrestler records (441 x 2285 bytes)

One record per wrestler COSTUME: 190 distinct (family, given, nickname)
triples, 1–4 records each (45 wrestlers x1, 75 x2, 34 x3, 36 x4 —
"up to 4 costume sets per wrestler"). The last 4 records (437–440) are
the generic trainees (練習生, 練習生２号, ３号, ４号). The record order
is federation-grouped like category 0 but is its own ordering
(190 wrestlers here vs 363 distinct in the name list — referees,
staff, and many originals have no record in this file).

Located fields (offsets within the 2285-byte record):

| Offset | Field | Example (record 0, Fujinami) |
|--------|-------|------------------------------|
| +0x00 | u32 ??? (record 0: 0x06000000; record 4: 1; record 8: 2) | — |
| +0x04 | family name, Shift-JIS (12 bytes) | 藤波 |
| +0x13 | given name, Shift-JIS | 辰爾 |
| +0x28 | nickname, Shift-JIS (32 bytes) | 炎の飛龍 |
| +0x49 | finisher name, Shift-JIS | ドラゴンスリーパー |
| +0x80 | stat bytes (0–12) + u16 tables (0–8) | — |
| +0x118 | move IDs / flags region | — |

Verified examples: Chono → Ｓ・Ｔ・Ｆ, Nagata → ナガタロックⅢ
(nickname 新日本プロレスのエース), Liger (record 81) →
骨法流浴びせ蹴り, Morishima → ハイアングルバックドロップ.

**Still open:** the interior layout of the 2285-byte record (stats,
moveset slots, COM Logic, costume data) — the biggest remaining KoC2
RE job. The stat/move regions are located (+0x80, +0x118) but not
decoded. Cross-checks available: the Jerrold Ng FAQ's per-wrestler
movelists, and the ELF's `MoveBase`/`MotionBase` loaders (xrefs at
0x118994 / 0x1189B8).

## 4. ELF notes (SLPM_656.02, MIPS-III, stripped but with section headers)

- `.text` 0x100000–0x322A74, `.data` 0x323D80, `.rodata` 0x3A5000,
  `.sdata` 0x3E4A80, `.bss` 0x3E5F00–0x426A70.
- Data loader at 0x1164d0: loads files 1999/2000/2001, resolves
  `WrestlerData`/`PartyData`/`TeamData` chunks, stores pointers at
  0x3FF300 (+0/+4/+8) plus a 4th pointer (+0xC, arg 0x118).
- Chunk-name xrefs: WrestlerData 0x1164F8, PartyData 0x11654C,
  TeamData 0x11659C, PartyOrder 0x116B64, MoveBase 0x118994,
  MotionBase 0x1189B8, BasicMotion 0x118AE0, ExtraMotion 0x118D98,
  PilonData 0x11905C.
- No immediate 0x7DA (2010) anywhere in `.text` — file 02010 is not
  loaded by index the way 1999–2001 are (it may be loaded by name, or
  the index is computed).
- A bit-unpacking routine at 0x114F80 (285-byte nibble table at
  $s0+0x130, flag ORs 0x1000/0x2000/0x6000/0xC000 into indexed u16s)
  is NOT the wrestler reader — the 0x1AD there is a buffer offset.
