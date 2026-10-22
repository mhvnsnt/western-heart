# Urban Reign — Job 3 name mapping: assessment (Phase 3, Attempt 6)

Tool: `teardown/urban-reign/tools/ur_motdat_info.py`.
Data: `motdat-info-tables.json` (same folder) — full parsed tables.

## Inputs verified against the AFS first

All 10 scratch files from attempt 2 (`~/workspace/ur-phase3-work/
scratch/motdat/`) size-match their DVD000 AFS entries **exactly**:

| Scratch file | AFS entry | Size |
|---|---|---|
| motion_test_motdatGnrl.info | motion/test/motdatGnrl.info | 18820 |
| motion_test_motdatP1.info / .bin | motion/test/motdatP1.info / .bin | 2244 / 253728 |
| motion_test_motdatP42.info | motion/test/motdatP42.info | 3524 |
| motion_test30_motdatGnrl.info | motion/test30/motdatGnrl.info | 16452 |
| motion_wptest_motdatGnrl.info | motion/wptest/motdatGnrl.info | 2820 |
| motion_wptest_motdatP44.info / .bin | motion/wptest/motdatP44.* | 68 / 5256 |
| motion_wptest_motdatP55.info / .bin | motion/wptest/motdatP55.* | 196 / 30512 |

(Content identity beyond size rests on attempt 2's extraction
provenance; the AFS holds 76 motdat .info files and 41+ .bin files in
test/test30/wptest — only these 10 were extracted.)

## The .info format — CRACKED (all 7 held files, zero bad records)

`[u32 count N][N × u32 table][N × 60-byte records]`, total size
`4 + 64·N` — satisfied **exactly** by all 7 files. Table entry k =
k·60. Record = `[u32 index][32 B name][20 B date][00 01 02 03]`.
Record indices run 0..N−1 sequentially with no gaps or repeats in
every file: **ordering inside each list is proven by the file's own
bytes**, not assumed.

Parsed lists (689 records total; full names+dates in the JSON):

| List | N | Prefix mix (archetypes) |
|---|---|---|
| test Gnrl | 294 | cbco 180, moco 86, haco 23, itco 4, habx 1 |
| test30 Gnrl | 257 | cbco 161, moco 48, itco 33, haco 15 |
| test P1 | 35 | moco 22, cbco 8, mohr 3, hahr 2 |
| test P42 | 55 | moco 33, cbco 14, cbtd 4, haco 2, hatd 2 |
| wptest Gnrl | 44 | cbco 27, moco 16, cbwp 1 |
| wptest P44 | 1 | haam 1 |
| wptest P55 | 3 | moco 2, cbcb 1 |

## Bank alignment — NOT proven (and the naive theory is disproven)

Ordering/count evidence only, per the job rules:

- Bank motion counts (Phase-2 converted banks, verified this attempt
  from `game/assets/anim/ur-general-*/clips.json` on the base
  branch): normal **342**, 30frame **373**, weapon **114**.
- **No held list count equals any bank count** (294, 257, 44, 55, 35,
  3, 1 vs 342/373/114). A 1:1 "list position = bank motion index"
  reading is therefore impossible for every list.
- The lists are **not** subsets of one master list either: wptest
  Gnrl (44) ⊄ test Gnrl (294); test30 Gnrl (257) ⊄ test Gnrl;
  P1 (35) ⊄ Gnrl; P42 (55) ⊄ Gnrl; no ordered-subsequence relation
  holds. They share a vocabulary (668 unique names across the five
  main lists; P1∩P42 = 17 names) but each list is its own
  context-specific selection/order (test vs test30 vs wptest =
  different motion-test scenarios; P-lists = per-player move sets).
- gyuindex.bin (base branch, re-verified this attempt): 37
  `pmotNNN.gyu ↔ pmotIDNNN` pairs + 10 tmot pairs in fixed order —
  the pmotID side remains the un-decoded bridge.

**Conclusion: zero names are assigned to bank indices by this
attempt, deliberately.** The correlation must come from the companion
`.bin` records (motdatP1.bin = 253,728 B is held; its records
presumably carry per-move motion indices/parameters that the .info
table's k·60 offsets point into — the .info table stepping by 60
while its own records are also 60 B is the lead to test first:
hypothesis, not proof). Next steps, in order: (1) decode
motdatP1.bin record structure against the P1 .info offsets;
(2) cross-check any motion-index field against pmot001's 56-motion
.gyu bank and the general banks; (3) only then assign the entries
that verify, per fighter, with per-character isolation.
