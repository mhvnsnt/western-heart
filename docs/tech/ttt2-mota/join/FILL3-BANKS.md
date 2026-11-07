# Fill 3 (TTT2) — the remaining character banks

Owner instruction (verbatim): "1, 2, 3, then 4, remember then all til we
get em done" — owner, 2026-11-06. Fill 3 of 4: build the remaining TTT2
character banks from held data (Fill 1 TK5 and Fill 2 T7, #1618, are
complete; Fill 4 Tekken 8 follows). Roger and Jun were already shipped
(#1558/#1561/#1581) and are NOT redone; True Ogre (GreenOgre) has no
TTT2 moveset file in existence (ogr = Ancient Ogre only) and gets no
bank — its join (#1621) is census data only.

## What landed

- **63 joins + bank-1 tables** — #1621 (`FILL3-JOINS-AND-TABLES.md` in
  this folder): 125,784 records; bank-1 tables for 65/66 characters.
- **63 banks** in `game/assets/anim/t3/<bank>/` (this series of PRs):
  per bank, the 20 FIGHT slots baked from the character's own join
  picks (clips that passed the production gates), `skeleton.json`
  (the shared ttt2-mannequin skeleton), `rows.pack.json`
  (`wh-anim-pack/1`) and `hit_frames.json` (`wh-hitframes/1`) in the
  exact Roger/Jun schemas, with grid row 48 withheld in every bank
  (owner ruling pending, following the shipped pattern).
- **Tools**: `tools/anim/ttt2_bank_rows.py` generalized (below) and
  `tools/anim/ttt2_slot_mapper.py` (new).

## Method specified vs used

Specified: clip extraction, the (bank<<14)|index joins, and
per-character rows in the same schema Roger/Jun landed with; nothing
fabricated — no decodable data = a named gap.

Used, per stage:

1. **Joins** (#1621): pair-12 motbin parses cross-validated against the
   records' own +0x10 self-index extent chains; merged only at 100%
   overlap agreement.
2. **Bank-1 tables** (#1621): shipped clip-fingerprint method,
   growing-anchor search; gates reproduce Jun's published table
   exactly and Roger's at 68 matches.
3. **Slot mapping** (`ttt2_slot_mapper.py`): the 20 FIGHT slots mapped
   from each join by the roster's naming dialects. Validation: against
   the shipped Roger bank's clip provenance it reproduces **15/15**
   shipped picks exactly, including production's t3_light gap (a
   cross-character Ak_lp00 never substitutes). ko and hit_launch have
   no identified slot source in any join — standing gaps, matching
   the shipped banks.
4. **Bake** (`tools/anim/ttt2_bank_bake.py`, production tool): two
   recorded changes, both gate-proven below — a batched
   `unwrap_rotations` (identical choices, ~6x faster) and a guard so a
   decoder-variant stance entry (Steve_Fox) falls back to the
   unanchored unwrap instead of crashing the bank.
5. **Rows** (`tools/anim/ttt2_bank_rows.py`, generalized): the shipped
   tool re-parsed two hardcoded motbin grids; the generalized version
   reads any character's join plus a record-offsets sidecar (each
   record's raw 0x70 struct window in data006, located by the stage-5
   locator at 99.7% coverage and re-verified in-tool against the join
   triple). Field semantics (+0x40/+0x44/+0x5C), row set, gates,
   buttons, and the rel-0 unmapped quirk are the shipped ones.

## Validation gates (all byte-exact)

- Roger slot bake: shipped `t3_neutral.json` reproduced byte-for-byte
  (the only delta vs a bare bake is the `move_row` stamp the rows
  stage adds).
- Roger rows: `rows.pack.json` (5,673,599 B) and `hit_frames.json`
  reproduced **byte-for-byte** by the generalized tool.
- Jun rows: `rows.pack.json` (2,785,318 B) and `hit_frames.json`
  reproduced **byte-for-byte**.
- Skeleton: every bank's baked skeleton joints are identical to the
  shipped Roger/Jun skeleton (same rest/calibration inputs); the
  `source_skeleton` provenance block is the shipped one (the original
  Koenji blend is archive-only and the bake tool only hashes it).

## Honest gaps (nothing fabricated)

- **ANNA bank-1 table**: not locatable in held data005 (evidence in
  `bank-tables.json`). Her bank ships bank-2/shared slots and rows
  only; her bank-1-sourced rows are classed missing with the reason.
- **Partial joins** (pool fragmentation in data006): BOB_SATSUMA,
  EMILIE, HWOARANG, KING, Kunimitsu, Lei_Wulong, NINA, P-JACK,
  YOSHIMITSU, ZAFINA, Zako07 — fewer records, hence fewer slots/rows.
  Fallback for all of these: the queued archive.org PS3 copy
  (tag ttt2-ps3-archiveorg-20261106), per the lane brief.
- **Chain-only joins** (9 blocks) start at grid index 23; head records
  i<23 (incl. motOrigin) are a documented gap.
- **Bank-0-resolved slots** are gaps everywhere: the shipped tooling
  never wired the per-character data006 MOTA tables (bank 0).
- **ko / hit_launch**: no slot source identified for any character,
  shipped banks included.
- Per-bank gate skips (plausibility: non-upright starts, floor
  penetration at mannequin proportions) and decode-variant rows are
  itemized in each bank's reports under
  `docs/proof/2026-11-07/fill3-ttt2/`.
- Row 48 withheld in all banks (owner ruling pending).

## Directory naming / collision rule

`game/assets/anim/t3/` already holds Tekken 3 banks at several
character names (anna, bryan, eddy, jin, julia, kuma, law, nina, ogre,
paul, yoshimitsu, bosconovitch, heihachi, hwoarang, armorking) — live,
bound, complete banks the game serves today. A TTT2 bank never
overwrites one: where the lowercase block name collides with an
existing bank dir, the TTT2 bank lands inert at `<name>_ttt2/`
(unbound; binding a fighter to it is a separate step, as it was for
roger/jun). ANNA's TTT2 bank therefore lands as `anna_ttt2` in a later
batch — her incomplete pack (bank-1 table gap) must not replace the
complete T3 anna bank that serves Torch (game-unit-tests caught
exactly this in batch 1's first CI run: 347 torch-referenced rows).

## Per-bank counts

| bank | clips baked | clips skipped (gate) | slot gaps | pack rows | hit rows | rows missing |
|---|---|---|---|---|---|---|
| alex | 12 | 5 | 3 | 320 | 332 | 35 |
| alisa | 14 | 4 | 2 | 463 | 468 | 30 |
| angel | 13 | 5 | 2 | 290 | 288 | 31 |
| armor_king | 12 | 6 | 2 | 342 | 345 | 24 |
| asuka | 13 | 5 | 2 | 319 | 330 | 35 |
| bob_satsuma | 4 | 2 | 14 | 36 | 38 | 6 |
| anna | 5 | 4 | 11 | 78 | 77 | 302 |
| baek_doo_san | 13 | 4 | 3 | 315 | 318 | 32 |
| bosconovitch | 14 | 3 | 3 | 270 | 270 | 22 |
| bruce | 11 | 6 | 3 | 328 | 336 | 28 |
| bryan | 13 | 5 | 2 | 354 | 363 | 34 |
| christie | 9 | 5 | 6 | 374 | 397 | 46 |
| combot | 14 | 3 | 3 | 792 | 809 | 40 |
| devil_jin | 12 | 5 | 3 | 363 | 365 | 26 |
| dragunov | 8 | 9 | 3 | 310 | 318 | 27 |
| eddy | 9 | 5 | 6 | 379 | 393 | 40 |
| eleonor | 11 | 6 | 3 | 316 | 323 | 35 |
| emilie | 4 | 3 | 13 | 36 | 38 | 6 |
| feng | 11 | 6 | 3 | 328 | 336 | 27 |
| forest | 12 | 5 | 3 | 403 | 401 | 19 |
| ganryu | 8 | 8 | 4 | 322 | 328 | 26 |
| heihachi | 12 | 5 | 3 | 338 | 342 | 27 |
| hwoarang | 3 | 2 | 15 | 36 | 36 | 3 |
| jack | 7 | 10 | 3 | 387 | 404 | 35 |
| jin | 11 | 5 | 4 | 327 | 334 | 34 |
| jinpachi | 12 | 5 | 3 | 304 | 302 | 18 |
| kazuya | 12 | 5 | 3 | 333 | 331 | 19 |
| julia | 11 | 7 | 2 | 397 | 402 | 26 |
| king | 5 | 2 | 13 | 110 | 112 | 7 |
| kuma | 12 | 5 | 3 | 348 | 353 | 28 |
| kunimitsu | 4 | 3 | 13 | 108 | 113 | 11 |
| lars | 7 | 10 | 3 | 309 | 313 | 21 |
| law | 12 | 5 | 3 | 395 | 396 | 26 |
| lee | 13 | 4 | 3 | 347 | 347 | 24 |
| lei_wulong | 4 | 2 | 14 | 112 | 116 | 8 |
| lin_xiaoyu | 10 | 8 | 2 | 409 | 417 | 28 |
| marduk | 13 | 5 | 2 | 312 | 316 | 24 |
| michelle | 12 | 6 | 2 | 359 | 361 | 35 |
| miguel | 12 | 5 | 3 | 304 | 300 | 28 |
| miharu | 10 | 8 | 2 | 409 | 420 | 31 |
| nina | 5 | 3 | 12 | 119 | 119 | 8 |
| ogre | 10 | 7 | 3 | 296 | 305 | 30 |
| p-jack | 4 | 1 | 15 | 30 | 32 | 6 |
| panda | 12 | 5 | 3 | 341 | 353 | 35 |
| paul | 14 | 3 | 3 | 315 | 311 | 26 |
| raven | 8 | 9 | 3 | 339 | 343 | 32 |
| sebastian | 13 | 4 | 3 | 310 | 323 | 35 |
| slimbob | 10 | 8 | 2 | 381 | 385 | 28 |
| steve_fox | 8 | 10 | 2 | 309 | 316 | 26 |
| tiger | 10 | 4 | 6 | 366 | 400 | 54 |
| unknown | 9 | 2 | 9 | 159 | 157 | 16 |
| violet | 13 | 4 | 3 | 350 | 352 | 23 |
| wang | 7 | 9 | 4 | 302 | 311 | 27 |
| yoshimitsu | 3 | 1 | 16 | 32 | 32 | 3 |
| zafina | 5 | 3 | 12 | 112 | 114 | 8 |
| zako00 | 15 | 2 | 3 | 310 | 303 | 15 |
| zako01 | 15 | 2 | 3 | 296 | 300 | 31 |
| zako02 | 14 | 3 | 3 | 339 | 332 | 24 |
| zako03 | 15 | 2 | 3 | 311 | 303 | 14 |
| zako04 | 15 | 2 | 3 | 303 | 295 | 22 |
| zako05 | 15 | 2 | 3 | 309 | 301 | 16 |
| zako06 | 15 | 2 | 3 | 307 | 301 | 18 |
| zako07 | 4 | 2 | 14 | 107 | 109 | 10 |
| **ALL 63 BANKS** | **643** | **296** | **321** | **18425** | **18685** | **1811** |

Batch 1 = PR #1625 (alex, alisa, angel, armor_king, asuka, bob_satsuma).
Batch 2 = PR #1627 (anna, baek_doo_san, bosconovitch, bruce, bryan, christie).
Batch 3 = PR #1628 (combot, devil_jin, dragunov, eddy, eleonor).
Batch 4 = PR #1629 (emilie, feng, forest, ganryu, heihachi, hwoarang).
Batch 5 = PR #1630 (jack, jin, jinpachi, kazuya).
Batch 6 = PR #1631 (julia, king, kuma, kunimitsu, lars).
Batch 7 = PR #1632 (law, lee, lei_wulong, lin_xiaoyu, marduk).
Batch 8 = PR #1634 (michelle, miguel, miharu, nina, ogre).
Batch 9 = PR #1635 (p-jack, panda, paul, raven, sebastian, slimbob, steve_fox).
Batch 10 = PR (batch 10 PR) (tiger, unknown, violet, wang, yoshimitsu, zafina, zako00, zako01, zako02, zako03, zako04, zako05, zako06, zako07).
Collider banks land at <name>_ttt2 (see the naming rule above). The batch series is complete with batch 10: all 63 producible TTT2 banks are on main (GreenOgre excluded by ruling — no TTT2 moveset bank exists for True Ogre).
