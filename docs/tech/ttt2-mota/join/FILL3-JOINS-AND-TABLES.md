# FILL 3 — TTT2 joins + bank-1 tables for the remaining roster

Owner fill sequence, his words (2026-11-06): "1, 2, 3, then 4, remember then all til we get em done".
Fill 1 (TK5 DATA0) and Fill 2 (T7 gaps) are complete; this is Fill 3. Fill 4 (Tekken 8) follows.

## What this lands

- **63 new join files** (`docs/tech/ttt2-mota/join/<character>-join.json`, format `ttt2-join/1`,
  same schema as the shipped roger/jun/unknown joins): **125,784 records** across the roster.
  Roger, Jun and Unknown joins are NOT modified.
- **`bank-tables.json` extended** with a `fill3_bank1_tables` map: bank-1 MOTA table offsets +
  counts in data005 for **65 of 66** characters (the 4 previously known included). ANNA is a
  named gap (below).

## Method — specified vs used

Specified (brief): rebuild the census from evidence, then clip extraction, the (bank<<14)|index
joins, and per-character rows in the shipped schema, from held data only; nothing fabricated.

Used, stage 1 (joins): the shipped motbin model (66 blocks in data006, pair-12 movelist section,
0x70-byte records, `anim_ref = (bank << 14) | index`) holds, but the lane found data006's motbins
are **extent-fragmented**: a contiguous pair-12 read derails into neighboring arrays for most
mid-file blocks. Two independent record sources were cross-validated:

1. Pair-12 parses (loose pool bound). Gate: reproduce shipped roger-join (2,180) and jun-join (749)
   record-for-record under the shipped tight bound — passed. (The loose bound adds 14 genuine tail
   records to Roger, i=2183..2196 win-pose moves; shipped roger-join is NOT modified — deviation
   noted here, not landed.)
2. The records' own +0x10 self-index field — (char_id<<16)|(grid_index−23) per RECORD-FIELDS.md —
   forms extent chains in the file. Chain triples agree with Roger's shipped join **2160/2160, zero
   disagreements**, same numbering (i = lo+23). Fragmented blocks were identified by char-specific
   move-name prefixes and anim→ref purity (multi_ref = 0): char26=DEVIL_JIN, 27=RAVEN, 28=FENG,
   29=ARMOR_KING, 30=EMILIE, 41=Ogre, 57=Combot (3,518 records / 1,712 anims — the mimic's full
   block), 61=Zako03, 64=Zako06; 3=KING, 4=YOSHIMITSU, 5=NINA by wide-margin pool resolution.

Merge rule: where a pair-12 parse was genuine (motOrigin at i=4), chain records were merged only
after a shift search aligned them at ≥98% agreement on the overlap — in practice **100% agreement
on 1,400–2,400 overlapping records per block**. Chain-only joins start at i=23: the wrapped +0x10
runs (length == char_id) are an artifact array, not movelist heads, so records i<23 are a
documented head gap for ARMOR_KING, Combot, DEVIL_JIN, FENG, Ogre, RAVEN, VIOLET, Zako03, Zako06.

Used, stage 2 (bank-1 tables): the shipped clip-fingerprint method (type, track count, frame
count, byte size; fingerprint4.py). Gate: Paul-anchor reproduces Jun's table at 35/41 exactly as
published, and Roger's at 68 matches (denominator 87 vs the published 89 because the shipped
roger-join's bank-1 anim set differs by 2 anims from the original triple-scan set). A growing
anchor (located tables join the reference set) located 52 further tables at match fractions
0.63–0.90 with wide margins; Combot, Ogre and P-JACK were settled by count-fit / size-insensitive
fingerprint / size-sensitive tie-break respectively (notes in bank-tables.json); the six Zako
blocks share six content-identical cnt=448 tables, assigned in file order around the independently
located Zako01/Zako02 tables.

## Honestly classed gaps (nothing fabricated)

- **ANNA bank-1 table: not locatable in held data005.** 65 of 66 character tables located; the one
  unassigned big table (@94807636, cnt 648) is a non-character table (42/648 body clips, lacks the
  shared clip library present in every character table). ANNA's join itself is verified correct
  (bank-2 index agreement 910/910 vs Paul). Fallback source: the queued PS3 copy
  (tag `ttt2-ps3-archiveorg-20261106`). Her bank will bake bank-2 slots only until then.
- **Partial joins** (blocker: the block's own string pool is extent-fragmented inside data006, so
  char-specific strings past the contiguous pool chunk do not resolve; all-phase rescans confirm no
  missed subrange; same PS3 fallback): BOB_SATSUMA 602 records, Kunimitsu 852, ZAFINA 1013,
  Zako07 831, EMILIE 835, Lei_Wulong 1507 (his chain extents are contaminated by neighbor arrays —
  83% alignment, not merged), KING 778 (chain only), NINA 861 (chain only), P-JACK 273,
  HWOARANG 323 (chain head extent only), YOSHIMITSU 259.
- **GreenOgre**: join landed as census data (2,139 records). NO bank will be built from it — True
  Ogre has no TTT2 moveset file (ogr = Ancient Ogre only), per the standing ruling.
- Miguel's join carries 10 anims with two refs each and Eleonor's 4 — source-grid quirks; every
  record is individually a validated triple.
- Bank-0-resolved slots remain documented gaps in the banks (shipped tools wire banks 1/2 only),
  and **row 48 stays withheld in every bank** (owner ruling pending), exactly as Roger/Jun shipped.

## Self-check

- [x] Shipped joins untouched; gates reproduced (roger/jun joins record-for-record; Jun bank-1
      fingerprint rate 35/41 exact, Roger 68 matches).
- [x] Every merged join: 100% pair-12↔chain agreement on overlap; every chain-only join:
      anim→ref pure (multi_ref = 0) with char-specific prefixes.
- [x] Per-character counts in the join files themselves (`records` arrays) and in
      `bank-tables.json` (`fill3_bank1_tables`).

## What follows (same lane)

Per-character banks: slot mapping from each character's own join, bake via the shipped
`tools/anim/ttt2_bank_bake.py`, rows via a generalized `ttt2_bank_rows.py` — same
`game/assets/anim/t3/<bank>/` paths and schemas as Roger/Jun. Validation gates before mass
production: Roger's stance re-bakes byte-identical to the shipped `t3_neutral.json`, and the
generalized rows tool reproduces the shipped roger/jun `rows.pack.json` + `hit_frames.json`.
