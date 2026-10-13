# YANM Item-6 Cycle Results — ECD identity probes, base-ID generation fn, anatomical L/R verdict
Measured 2026-10-13 (watchdog continuation cycle). All streamed from ISO
(`WWE Wrestlemania XIX (USA).iso`); probes: `tools/yanm_item6_ecd.py`,
`tools/yanm_item6_ecd2.py`, `tools/yanm_item6_baseid.py`,
`tools/yanm_item6_baseid2.py`, `tools/yanm_item6_lr.py`,
`tools/yanm_item6_lr2.py`. Full 215-clip universe (ringmotion 170,
viewer/motion 37, viewer 3, 2d 4, bg/bs 1).

## ITEM 3 — ECD28978: per-move-variant 2-channel static pose selector, identity still OPEN

### Census (full 215-clip universe)
- ECD track present in **208/215** clips; **0/208 animated within a clip**
  (max intra-clip raw range < 1000). Static per move, always.
- **87 distinct poses** at 1° rounding (119 at 0.1°, 155 raw-distinct) over
  208 clips. Top 1° poses: (1,1)×9, (0,80)×8, (4,76)×8, (−10,76)×7,
  (1,0)×6, (0,0)×6, (80,4)×6, (2,1)×6.
- Channel value sets: ch1 **107** distinct raw s16, ch2 **105** distinct.
  Both channels draw from the **same value vocabulary** (top values
  identical: 32258=79.9°, 31746=75.7°, 2068=3.6°, 32002=77.6°…).
  The earlier "9×9 discrete grid" hypothesis is REJECTED (107/105 values,
  not ~9; chi-square vs independence 13667 on 11024 dof — weak dependence
  only, sparse-cell caveat).
- Mean |pose|: ringmotion 46.4°, viewer/motion 50.2° — no effort gradient
  (face-effort magnitude test INCONCLUSIVE).

### 7 clips lack ECD (all also lack 0C5BF279)
`2d/result_L00.yag`, `2d/result_R00.yag`, `2d/result_L00c.yag`,
`2d/result_R00c.yag` (2D UI, 1–9 tracks), `bg/bs/2_0.yag` (background, 15
tracks), `ringmotion/a033_0a.yag` (14 tracks), `ringmotion/c138_0a.yag`
(degenerate, 0 tracks parsed).

### Slot-entity clip: second-performer hypothesis WEAKENED
`ringmotion/a033_0a.yag` carries **all 7** slot-entity tracks
(00008102/9202/9302/9D02/9E02/D402/D502) — the "7 slots in 7 clips" reading
was wrong; all 7 entities live in this ONE 14-track setup clip — and it has
**NO ECD and NO 0C5BF279**. If ECD were a second-performer selector, the one
clip with 7 performer slots would be the place to find it. It isn't there.

### Variant pairs: ECD is variant-specific (NEW)
Same move, different variant suffix → different ECD pose (3 pairs):
- `c200_0a` (63.0,24.5) vs `c200_1a` (0.9,1.1) vs `c200_2a` (1.8,0.2)
- `c224_0a` (77.6,9.0) vs `c224_1a` (2.5,0.9)
- `c138_0a` (no ECD) vs `c138_0b` (80.2,4.0)
Mirror-selector hypothesis: NOT supported — _1a/_2a poses go to ≈rest
(0–2°), not sign-flipped/swapped (3/3 pairs). ECD pose is authored per
move-variant, not a mirror flag.

### Correlation probes (all ~zero)
- r(ECD ch2, thumb ch2) = **−0.131**, r(ECD ch1, thumb ch1) = **0.070**
  (n=414) — ECD is not thumb-related.
- r(ECD ch1, 0C5BF279 ch1) = **0.072**, r(ch2) = **0.010** (n=206) —
  independent of the per-wrestler detail track.
- Max |r| vs any core track's static pose = 0.27 (prior cycle) — independent
  of body motion.
- Finger-animating clips: ECD non-(0,0) in 30/33 (91%) vs 125/175 (71%)
  static — weak co-occurrence only; top shared pose (−10.4,75.7).
- ECD in **0/8** scanned wrestler `.ymg` files and 0/175 `.ycg` — it exists
  ONLY in `.yag` clips (no model-side binding record, unlike 0C5BF279 which
  has the ymg table slot).

### Verdict
ECD28978 = **per-move-variant 2-channel static pose selector**, 87 distinct
poses, both channels sharing one value vocabulary, fully independent of
body/finger/thumb/0C5B motion, absent only in non-wrestler clips.
**Identity still OPEN.** Leading hypothesis remains **face-bone driver**
(20 face bone names in ymg: Eeye/Eface/Emouth/Etooth, l_/r_ eyes/lips;
fits static-per-move + ±80° extremes + variant-specificity + full
independence) — but NOT provable headless; needs mesh/FK or visual.
Rejected/weakened: 9×9 discrete grid, thumb-related, 0C5B-related,
second-performer-via-slot-entities, mirror selector.

## ITEM 4 — base-ID generation function: narrowed, still OPEN

### Universe correction (full 215 clips, not ringmotion-only)
- **472 distinct track hashes** (was 97 ringmotion-only), **24 side pairs**
  (was 16), **445 distinct base IDs**.
- Side-code census (full): `0x7800`×6, `0x1E000000`×5, `0xF0`×5, `0xA00`×3,
  `0x0F`×3, `0x780`×1, `0xA0`×1. No new codes vs ringmotion.
- Base IDs split: **28 entities** (< 0x10000) + **417 joint/system tracks**.

### Entities: (slot<<8)|0x02 CONFIRMED, 25 slots
25 entity slots across clips: 0,1,2,129,130,131,133,138,143,149,157,158,
161,168,185,191,197,209,212,215,238,239,241,244,255 (+3 non-slot small IDs:
00000000, 0000000E, 0000007F). The earlier "7 slots" were the ringmotion
subset; all 7 co-occur in the single `a033_0a` setup clip.

### Hypothesis tests (joint/system tracks only, n=417)
- **H1 fixed-key XOR** (`base = index XOR K`): REJECTED. Best K=0x01000000
  covers only 7/417 — and those 7 are the `010000xx` family cluster
  (00,02,08,10,26,2E,36), i.e. a family, not a global key.
- **H2 nibble-permutation of small int**: REJECTED. 25/417 hits, all with
  high16 ≤ 0x0010 (small IDs trivially qualify) — no permutation structure
  in real joint IDs.
- **H3 entity relation**: joint tracks do NOT relate to entity IDs (only the
  28 small bases do, by construction).
- **H4 base-ID order vs ycg record order**: WEAK (spearman 0.433, n=42) —
  not a clean bone-index encoding.
- **H5 verbatim base-ID table in model files**: NEGATIVE. 000_0.ycg hits
  (6865B2C0×3, 64DB300F×2, 7CC9B660×2, 347D3654×2, 099CD766×1, 095CD669×1)
  are just the ycg records' own hash slots (the known track↔group link);
  ymg hits are only 0C5BF279 (table slot) + padding. No independent ID
  table exists.
- **H6 DDF67B-run relation**: REJECTED. Min popcount(base XOR runword) = 9;
  0 pairs with popcount ≤ 8. The 045 ID-block run is unrelated to yag base
  IDs.
- **H7 poly/additive hash of small ints** (0–4999, big+little endian):
  REJECTED. 1 hit: i=317 → 0x00010002 (a small family ID, not a joint).
  Combined with prior 26-function + ~200-name batteries: IDs are
  **assigned, not derived**, by every tested function family.

### Family clustering (the real structure)
Non-joint systems use `(family<<16)|member` — measured families:
`4AAF____`×9 (3560/3563/3660/3663/36E0/36E3/3760/37E0/37E3),
`F7AB____`×5, `5D9B19__`/`5D9B1A__`/`5D9B1B__`×7, `579B__50`×5 (thumb
family), `A4955E6A/6C/6D/6F` (finger sub-tracks), `010000__`×7,
`0200__`, `59__`/`5A__`, `C6F1____`, `7AAFEC__`. Viewer/menu clips carry
their own families — the "random" joint IDs are the ringmotion body/joint
set.

### Correction
Family delta `613B7507 ^ 637B7003` = **0x02400504**, not 0x02400544 as
written in YANM-ITEM3-ITEM4-CYCLE.md (last-byte typo; recomputed
byte-wise). `60F8F507 ^ 6198F405 = 0x01600102` confirmed.

### Verdict
Generation function **OPEN but narrowed**: joint base IDs are
tool-assigned opaque IDs (no recoverable function among XOR-key,
nibble-permutation, index-hash, entity-relation, order-correlation, or
verbatim-table hypotheses — all rejected with counts above). Family
structure is real but only for non-joint systems. For retargeting, the
side-pairing (exact-XOR) is the usable structure; base IDs themselves need
no decoding.

## ITEM 2 — anatomical L/R: bridge unachievable headless, provisional stays LOW

### What is SOLID
- Side-bit → ycg-y: `0x04000000`-bit SET ↔ ycg **y<0**, 6/6 on
  64D45E02/7AD45E02; BD5B2A59/BD5B5259 (LEG, XOR 0x7800) and finger/toe
  pairs consistent. ycg records are mirror-symmetric (only y flips sign
  between pair members; x/z identical).
- ymg anatomical: `Bip R Thigh` local (−0.14, **+10.40**, 0),
  `Bip L Thigh` (−0.14, **−10.40**, 0) → ymg frame R=+y, L=−y.
- Same-side groupings (independent of frames): (A4955E6E, 579B8E50) one
  hand; (BA955E6E, 579B89D0) the other (contingency 0/149+0/154 perfect).

### The bridge failed (measured)
- **Euler alignment**: all 6 euler orders fail to place ymg R bones at
  y>0 (best: 1/26); mean ycg→ymg-world nearest distance 102 units.
- **Nearest-neighbor by local position**: ycg pos ≈ ymg local pos at mean
  2.5 — but the matches are WRONG bones (ycg rig offsets collide with ymg
  finger/small-bone offsets). Side agreement: **15 agree / 7 disagree /
  20 abstain** — MIXED, not decisive. The ycg 42-joint rig is a different
  scale/proportion rig than the ymg 70-bone rig (ymg thigh len 44.81 vs
  ycg max segment ~17; no ycg record near y=±10.4).
- **Root cause**: the ycg bind pose is mirror-symmetric → contains ZERO
  intrinsic L/R information. The only L/R ground truth (ymg bone names)
  lives in a different rig/frame with no reliable headless correspondence.

### Verdict
Provisional mapping **stays LOW confidence**: A4955E6E = LEFT hand,
BA955E6E = RIGHT hand, 579B8E50 = LEFT thumb, 579B89D0 = RIGHT thumb,
007FD58C = RIGHT toes, 1E7FD58C = LEFT toes (via y<0=L IF frames agree).
**For the chimera build**: map side-bits CONSISTENTLY (all SET→one side,
all CLEAR→other). The result is correct up to a global mirror, which is
visually undetectable without the original game as reference — the
provisional mapping is safe to use with that caveat. Resolving the final
bit needs either YOBJ mesh assembly (mesh shares the ymg frame) or visual
reference.

## STOPPED HERE (next cycle)
1. ECD28978 identity — needs mesh/FK or visual (face-bone driver hypothesis).
2. Base-ID generation fn — open; usable structure is the exact-XOR pairing.
3. Anatomical L/R final bit — needs YOBJ full-model assembly or visual.
4. ID-block semantics + byte-ramp curves (from ITEM3-ITEM4 doc).
5. CAW `.gci` — blocked headless (needs parent Dolphin task with KNOWN CAW values).
