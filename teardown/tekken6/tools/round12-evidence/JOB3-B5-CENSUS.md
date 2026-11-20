# Tekken 6 PSP — ROUND 12 JOB 3 (B5): the 16B-record census on the CORRECTED page grid — the "pages" are 40 embedded NTPP sections; field map + record-class verdict

Date: 2026-10-22, round 12. Scripts: `round12-evidence/j3_b5_census.py`;
field map JSON: `round12-evidence/r12_b5_fieldmap.json`;
payload view (VIEWED): `round12-evidence/r12_b5_payload_44x48.png`.
Data: idx24 slot 9 (88,768 B) from the retained decoded76 set.

## Grid correction (the census's foundation — rounds 10/11 used a shifted grid)

Slot 9 = a 448 B head + **40 pages of 2,208 B tiling exactly to EOF**
(448 + 40×2,208 = 88,768, zero remainder). On this grid, **every page
opens with the same 7 records (112 B)**: an NTPP section header —
records 0–5 byte-identical across all 40 pages, record 6 zero:

```
rec0  4e545050 01000100 00000000 00000000   "NTPP", version 0x00010001
rec1  90080000 40000000 00080000 50001000   +16=0x890, +20=0x40, +24=0x800, +28=0x100050
rec2  00010384 40004000 00000000 00000000   +32=0x84030100 (template field), +36=0x00400040
rec3  all zero
rec4  65587400 20000000 10000000 00000000   "Text" chunk name, 0x20, 0x10
rec5  47494458 10000000 00000000 00000000   "GIDX", 0x10
```

The rounds 10/11 extraction (offsets from the BE page table at
+0x78: 2,544 + 2,208k) is shifted +2,096 B against this grid, its
40th entry is offset 0 (a terminator, not a page), and the
"embedded NTPP @+0x1c0" of rounds 8–10 is simply page 0's header
at 448 = 0x1c0. The table itself is real (40 × (0x8a0, offset)
pairs) but its offsets are +2,096 against the section grid —
recorded as measured; the section grid is proven by the identical
headers + exact tiling.

**The 0x800 anchor, resolved (brief's premise corrected):** the
constant is the NTPP header field at section +24 (LE 0x00000800,
record 1 bytes 8–11) — present in **40/40 pages**, a header
constant, not a per-record field. The rounds 10/11 sighting
("page offset 52", 36–37/40) was this library's second constant
seen through the shifted grid: on the true grid it is a BE u32
0x00000800 at in-page offset 2,148 (record 134, bytes 4–7),
present in 37/40 pages — a near-constant payload field, reported
with its true coordinates.

## Directory correlation

The BE 0x20 B directory in the head agrees with the census:
record 3 = [1, 0x10, 0x15a50, 0, **0x28**, 0x150, **0x8a0**, 0x9f0]
carries the page count 0x28 = 40 and the page size 0x8a0 = 2,208
exactly; record 0 carries 0x15a60 = slot size − 64. Count/offset
agreement: CONFIRMED for count + size (the table's +2,096 offset
shift is the one disagreement, recorded above).

## Field census (data records 7–137; 131/page, 5,240 records; header records excluded)

Per-byte-position entropy + alphabet (full table in
`r12_b5_fieldmap.json`; census script reproduces it):

| pos | entropy (bits) | distinct | top values |
|---|---|---|---|
| 0 | 1.40 | 159 | 0 (86%), 0x11, 0x10, 0x01 |
| 4 | 1.73 | 183 | 0 (83%), 0x10, 0x11, 0x01 |
| 6 | 2.20 | 192 | 0 (78%), 0x11, 0x10, 0x21 |
| 8 | 2.68 | 208 | 0 (72%), 0x11, 0x10, 0x21 |
| 9 | 2.73 | 203 | 0 (71%), 0x11, 0x01, 0x10 |
| 10 | 2.41 | 207 | 0 (74%), 0x01, 0x11, 0x12 |
| 15 | 1.41 | 187 | 0 (87%), 0x11, 0x12, 0x22 |

(All 16 positions: entropy 1.4–2.7 bits, 159–208 distinct values,
0x00 dominant at 71–87%, then small values 0x01/0x10/0x11/0x12/
0x21/0x22.) Populated data records: 2,451/5,280 incl. record 6
(46%); distinct full data records: 2,236 (most common after the
zero record: single-flag records like `01 00…`, `…00 11`).
Record data is right-weighted: values appear first in the tail
bytes of each record (records 9–12 of page 0 grow `…0011`,
`…1011`, `…1042`, `…10111182`).

## Hypothesis verdicts (as briefed — each stated)

1. **Per-record = (id/enum, offset, size) index entries? REJECTED.**
   No byte position carries an offset/size-like distribution: no
   field takes values in a page/section offset range with ladder
   structure, no two fields co-vary as (offset, size) pairs, and
   every position is zero-dominated with a small-enum head. The
   only true (count, size) index in slot 9 is the head directory
   itself (above).
2. **Instance placements without floats (fixed-point)? REJECTED.**
   No 2–4 B field has the spread or continuity of fixed-point
   coordinates (top value everywhere is 0 at 71–87%; non-zero
   values cluster ≤ 0x42 in the head of each alphabet). No
   position field proves out → **no stage GLB** (per brief).
3. **Material/texture references into the embedded NTPP @+0x1c0?
   SUPERSEDED BY STRUCTURE.** The records do not reference an
   NTPP section — **each page IS one NTPP section** (header at
   record 0, first-block size field +16 = 0x890, GIDX block tag
   at record 5). The mapping runs the other way: the head
   directory's 40×0x8a0 table enumerates the sections. The pages
   are the stage package's texture sections, and the record data
   is the sections' payload (GIDX-block content), not geometry
   and not an external index.

## First decoded record class (with proof)

**The NTPP section-header record class (records 0–5) is fully
decoded** — proof: byte-identical across all 40 sections, and its
fields match the EBOOT template object's field pattern
(rounds 8/11: 0x100050, 0x84030100, "Text", GIDX) with
section-specific values (+16 = 0x890 first-block size vs
template 0x110; +24 = 0x800 vs template 0x80). The payload
records (7–137) are classified as the sections' GIDX-block
payload records: sparse, right-weighted small-value fields —
consistent with indexed/banked payload data, NOT proven to be
pixels at any geometry: the one render test run (page payloads
0–3 as 44×48 8bpp, `r12_b5_payload_44x48.png`, VIEWED) shows
sparse streaks on black — the 16 B record structure showing
through, not a coherent image — and its width autocorrelation
peaks at 16 (r = 0.808), reconfirming the record period over
any raster width. No pixel claim is made from it. B5's
geometry question is closed: **stage geometry is not in these
pages in any record form tested; the pages are texture
sections.** The residual is the same NTPP pixel-format
question as Job 2, in its stage-package instance.
