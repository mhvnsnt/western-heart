# TORCH BATCH 1 — STEP PLANS (LP1/RP2-only strings, 2026-10-25)

Torch's FIRST batch in the full-roster queue (roster inventory:
`~/workspace/roster-inventory/INVENTORY.md`). Torch follows the 8 done
fighters (Pantera → burger → demonio → diablo → kinpo → phantom →
scimitar → skull) as the FIRST fighter after them — the first T7-block
fighter not named in the original user-specified batch order, and the
only dual-bank fighter among the 10 T7-block files.

Scope: strings whose steps are ALL buttoned and whose button union is a
subset of {LP1, RP2} (any directionals, any contexts:
standing/crouch/jump/ws). Pure single-button strings first, then
chord-involved strings (chords containing only LP1/RP2 buttons).

Button names, standing law: LP1 = Left Punch = Tekken 1, RP2 = Right
Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Bank — VERIFIED, not assumed (dual-bank evidence)

Torch is the pipeline's FIRST dual-bank fighter. File evidence, both
files (#1096 and current main 956d6a1d):

1. **torch.json t3_source + t3_bank on BOTH #1096 and main:** `jin` /
   `moveset_jin.json` on both files. tekken_base `Anna`; merge_sources
   t8/t7/t3 all `anna`; T8 Anna coverage 165/165, T7 Anna rows 354/354.
   The file-level bank is jin — but it is NEVER assumed for all moves.
2. **Per-move t3_source counts (both files, identical):** jin 145,
   anna 224, none 523 (T8/T7-sourced, no T3 row). Every move that
   carries a t3_row also carries a t3_source, and all 369 agree with
   the move's anim_ref bank (t3:jin:row:N / t3:anna:row:N) — 369/369
   agree, 0 disagree, 0 row-without-source. Bank resolution per step:
   prefix move's t3_source, else first-step move's t3_source (the
   latter only matters for recorded-path candidates; see below).
3. **t3/ directory presence:** `game/assets/anim/t3/jin/` AND
   `game/assets/anim/t3/anna/` both exist with `hit_frames.json` +
   `rows.pack.json` + `skeleton.json` (+ reactions.pack). Pack dir =
   bank name for BOTH banks (no diablo-style heihachi/heihachi_on_jin
   split — checked: no alias dir is involved for either bank).
   Pack banks: jin `teardown/tekken3/animations/divmot09_jin.bin`,
   anna `teardown/tekken3/animations/divmot17_anna.bin`.
4. **Job 1 row counts for the resolved banks:** jin 220 rows (of 277
   hit_frames rows), anna 213 rows (of 305 hit_frames rows).
5. **Job 2 / Job 3 torch coverage: ZERO.** Job 2 torch entries 0,
   Job 3 torch entries 0, job3.log torch lines 0 (verified by direct
   count). Job 4 bank-level candidates exist (jin 47, anna 45) but
   cannot join without Job 2 torch entries — and a join never
   promotes anyway. This batch is GATE-ONLY (see below).
6. **No TheBigTuna t7-anna overlay exists** (t7/INDEX
   t7_missing_fighters) — irrelevant to T3-fallback batching, which
   uses T3 banks. Torch's T7 re-match awaits decode, like the other 9.

### Bound bank — the engine fact that shapes this batch

Torch's in-game bound bank is **ANNA**: fighter.js #1096
`FIGHTER_BANK` override `torch: 'anna'` ("CANON: Torch base = Anna
Williams") and moveset `anim_bank: 'anna'`. The #1096 step-plan branch
(`_resolveStepPlan` → `_attackClipPlan`) resolves `row:N` against the
fighter's bound bank clips (`this._t3.clips`) with NO per-step bank
guard — unlike `_ownRow` / `_rowDonor`, which refuse another bank's
rows outright (`(SOURCE_TO_BANK[src] || src) !== bank → skip`).

Consequence, decided in this lane and flagged for the coordinator
(see "BANK-BLOCKED decision" below): jin-bank gate-verified steps are
recorded as BANK-BLOCKED review (status review, row null,
`bank_verified_row` preserved on the step + in reasons). Wiring them
as verified would play anna row N — a wrong-bank clip — which the
engine's own rules forbid elsewhere and which the play-verify
checklist forbids ("no step playing a row from the WRONG torch
bank"). Anna-bank gate-verified steps wire normally (verified + row)
and ARE playable via the #1096 engine path.

### Jin-bank row rules (freshly derived here, never copied)

Jin Job 1: 220 rows of 277 hit_frames rows. Stances: standing 115,
jump 43, starts-airborne 30, duck-dip 16, crouch 10, ground 6.

- **Row 35 EXISTS** (starts-airborne, btn 1, hf [11,12,39,535,0,1],
  level m, Job 1 armL peakF 6, active [11,12]). Airborne: fails every
  ground-context step, passes jump-context steps. It is NOT kinpo's
  LP1 basic in any usable sense here — kinpo's move 1 IS jin r35, and
  kinpo Batch 1 never verified it for a ground step (it was suspended
  on drift there); torch has no Batch 1 step candidate citing jin 35.
- **Row 220 EXISTS** (standing RP2, btn 2, hf [12,12,41,1042,0,2],
  level h, Job 1 armR peakF 6, active [12,12]). Torch RP2 move 2's own
  row. It is NOT bryan's button-0 row 220, NOT king's jumping chord
  row, NOT heihachi's jump RK4 row — bank-specific identity only.
- **Row 216 EXISTS** (jump, btn 0, hf [63,64,117,1543,0,0], level u,
  no btn_limb). Fails every single-button gate (button 0) and has an
  airborne stance. It is NOT king row 216's dash Konvict Kick, NOT
  yoshimitsu row 216's standing LP1 row.
- **Row 248 (torch LP1 move 1's own row) is STANDING but button 12**
  (multi-button clip, hf [13,15,51,535,0,12], Job 1 armL peakF 25,
  active [13,15]). It FAILS every single-LP1 step under
  exact-equality (demonio row 177 btn-12 + scimitar row 184 btn-9
  precedent: chord/multi-button rows are rejected for single-button
  steps). Torch's LP1 basic therefore has NO verifiable LP1 step in
  this batch — every string starting with step 1 has step 1 unmapped
  on this rejection (6 strings: 1,2 family). The row is documented,
  never wired, never smoothed over.
- **Row 184 (btn 9)** likewise fails single-LP1 steps (scimitar
  precedent: scimitar's own LP1 row 184 would fail the same gate).
- **Row 177 (btn 12)** likewise fails single-LP1 steps (demonio +
  kinpo precedent, same row, same rejection).
- **Row 179 (jump, btn 1, hf [22,25,67,535,0,1])** is airborne: fails
  ground steps (kinpo precedent, same row).
- **Rows 33/34 (btn 3, hf [18,18,52,535,0,3])** are chord rows: fail
  single-button steps (demonio precedent, same rows).
- **Duck-dip rows (Job 1, 16)** are handled like crouch: STANCE-SOFT
  (review) for non-crouch contexts. Jin duck-dip rows are not cited
  by any Batch 1 candidate.

### Anna-bank row rules (first-ever anna adjudication)

Anna Job 1: 213 rows of 305 hit_frames rows. Stances: standing 127,
starts-airborne 30, jump 28, duck-dip 18, crouch 5, ground 5.

- **Row 35 EXISTS** (starts-airborne, btn 1, hf [9,9,37,535,0,1],
  level m, Job 1 armL peakF 5, active [9,9]). Airborne: fails every
  ground-context step. It is NOT jin row 35's clip — same number,
  different bank, different motion (anna's starts-airborne LP1 vs
  jin's). No Batch 1 step cites anna 35 as a candidate except as a
  variant whole-string row (u+1,1~t3.anna carries own row 35 — a
  variant record, not a step candidate; variants inherit canonical
  steps, see below).
- **Row 220 EXISTS in hit_frames ([19,24,74,535,0,0], button 0) but
  is ABSENT from Job 1.** It fails every single-button gate
  (button 0) and has no stance profile. It is NOT jin's standing RP2
  row 220. No Batch 1 step cites anna 220.
- **Row 216 EXISTS in hit_frames ([14,14,58,271,0,0], button 0) but
  is ABSENT from Job 1.** Same treatment: fails every
  single-button gate, no stance profile. No Batch 1 step cites
  anna 216.
- **Duck-dip rows (Job 1, 18)** handled like crouch: STANCE-SOFT
  (review) for non-crouch contexts. Anna row 175 (duck-dip, btn 3)
  is the f+2,f+1+2 chord step's candidate — held at review on
  exactly this rule.
- A candidate row present in hit_frames but absent from Job 1 is
  documented as such (no stance profile), never assumed standing.

### Torch's own basics (file evidence, both files)

- LP1 move `1` → jin r248, damage 7, "TORCH 1 (T3 jin r248)" —
  UNCHANGED #1096 vs main. Row 248 fails LP1 steps (button 12, above).
- RP2 move `2` → jin r220, damage 10, "TORCH 2 (T3 jin r220)" —
  UNCHANGED. Standing RP2 row; gate-verified wherever cited, but
  BANK-BLOCKED (jin bank, bound bank anna).
- LK3 move `3` → jin r195, damage 14, "TORCH 3 (T3 jin r195)" —
  UNCHANGED (standing LK3, btn 4). Batch 2's scope, recorded here
  because the brief asked for it: NO drift, NOT suspended.
- RK4 move `4` → jin r199, damage 15, "TORCH 4 (T3 jin r199)" —
  UNCHANGED (standing RK4, btn 8). Batch 2's scope, same note.
- Drift status for all four basics: same row, same damage, same
  anim_ref on both files. Zero drift.

## Re-baseline (#1096 vs current main)

- Moves deep-equal: True (892/892). Strings deep-equal: True
  (155/155). Only top-level diff: main adds a `t7_motbin` section
  (16 entries) — no move, string, or plan-relevant field differs.
- Full-file drift census (892 keys): same 892. Row-changed 0.
  Damage-only 0. Damage differs (any row status) 0. Anim_ref-changed 0.
- Step-prefix census: 0 row-changed moves affect Batch 1 scope →
  **suspended-drift steps 0.** No stale row is wired anywhere.
- Torch was NEVER purged by #1039: `t8_quarantine_20261024` key
  ABSENT on both files (verified, not assumed). No #988 dependency
  for torch batches. All moves are live on main.

## Gap-1 (bank blobs, #1096 vs main)

- **Jin:** hit_frames IDENTICAL (54b38e635bb815db00b764cc10675a6bffb489d0),
  skeleton IDENTICAL (26f72eb7e31d4047596d043e832c02ee6dba83ed),
  rows.pack DRIFT (b1096 141fbc8db374ef3031fe408ba8a597054abeb249 →
  main 7bafa36a76ce1bc89d46ebd3c13efd0a6260f192) — but row-content
  comparison shows the drift is ADDITIVE-ONLY: all 220 b1096 rows
  present unchanged on main; main ADDS 6 rows (89, 112, 247, 288,
  339, 357); 0 rows changed, 0 rows removed. Affected fills =
  fills using changed/removed rows = 0. No Batch 1 candidate is a
  main-only pack row (checked: 0 MAIN-ONLY-PACK flags). Gates use
  hit_frames (identical) + Job 1, and every wired row is verified
  present in the current main pack at wire time (the game plays
  from the pack).
- **Anna:** all three blobs IDENTICAL (hit_frames
  30406bd4776e2eba158cc982483b3e7f740f34dd, rows.pack
  63464f90e3a19dd0082c7bfe8b4856831659a39c, skeleton
  37ee237ebe7f9965e6cb4b36ca9c138487f3b240). Zero drift.

## Universe (measured, not assumed)

46 canonicals — exactly the inventory estimate (B1 46), derived
fresh from current main re-baselined vs #1096:

- 35 pure single-button + 11 chord-involved.
- 43 planned (strike/string/special class) + 3 CSV-only
  (throw/grapple): TACKLE.1,1 / TACKLE.1,1,1 / TACKLE.1,1,1,1 (narrow
  grapple label TACKLE; strike clips excluded; throw-row
  verification owed separately, not a step-plan).
- 79 plan keys = 43 planned canonicals + 36 variants (variants
  inherit canonical steps verbatim, canonical prefixes, Batch 1 twin
  precedent, plus twin_of + twin_move_class). Variant own rows
  (e.g. 2,1~t3.anna row 344 anna, b+2,2~t3.anna rows 365/367 anna,
  u+1,1~t3.anna rows 35/38/41 anna) are whole-string variant records,
  NOT step candidates — steps adjudicate on canonical prefixes only.
  No variant carries throw/grapple class, so no variant is excluded.
- 82 CSV rows = 46 canonicals + 36 variants.
- Contexts: standing 30, crouch 8, jump 7, ws 1 (ws1,2 — lowercase
  no-dot while-standing spelling, WS context per the kinpo Batch 1
  fix, not standing).
- Strings-list recorded paths: 22/155 entries carry t3_rows. All 22
  are jin-bank (first-step move bank jin in every case, verified).
  Batch 1 recorded-path steps: 1,2 [248,249], 2,1 [220,221],
  2,1,2 [220,221,222]; recorded-dest steps: 2,1,2,2 → 223,
  d+1+2,1 → 177, d+1+2,1,2 → 183, d+1+2,2 → 93. Recorded-vs-prefix
  disagreements: 0 (every recorded row agrees with its prefix
  move's row where both exist).
- Strings list carries 0/155 entries with input_lp (the brief's
  cosmetic note, confirmed) — button sets derive from input notation
  with the skull-lane step_buttons rule (last '.' segment, digit
  chars 1-4).

## Tallies

110 steps = 101 planned + 9 CSV-only.

- Planned steps: **11 verified / 25 review / 65 unmapped.**
- Planned unmapped split: **45 no-candidate / 20 rejected-candidate /
  0 suspended / 0 ambiguous-bank.** (An earlier draft labeled the
  32 no-candidate T8-sourced steps AMBIGUOUS-BANK; that was wrong
  and was corrected before filing — with no candidate row there is
  nothing to gate, and the bank is moot. Every t3_row-carrying move
  also carries t3_source, so a no-candidate step's prefix move is
  T8/T7-sourced with no T3 row at all.)
- Planned review split: **22 BANK-BLOCKED / 2 SOFT-fail /
  1 STANCE-SOFT.**
- Canonical status (43 planned): 23 partial / 16 unmapped-all /
  4 review-only / **0 verified-all.** No Batch 1 string is fully
  playable yet — every string's first step is unmapped or
  bank-blocked, or a later step is. This is honest, not a failure:
  the 11 verified steps are real, playable anna steps, and the 22
  bank-blocked steps are real, gate-verified jin steps awaiting a
  playback path.
- Plan-key last-step: 19 verified / 15 review / 45 unmapped.
- Job 3 fills wired: **0** (no torch Job 3 data exists — expected,
  not a failure). Job 4 joins: **0** (no Job 2 torch entries).
  Bank-level Job 4 candidates jin 47 / anna 45 are documented as
  unjoinable, never promoted.
- Wired rows (10 distinct, all anna): 32, 33, 34, 44, 45, 46, 171,
  174, 355, 356 — all present in the current main anna pack
  (213 rows).
- Bank-verified jin rows (8 distinct, NOT wired): 92, 93, 183, 220,
  221, 222, 223, 249 — all present in the current main jin pack
  (226 rows), preserved as bank_verified_row for promotion.

## Verified steps (anna bank, playable via #1096 engine path)

All pass HARD gates (button == step bits in the anna bank, throw 0,
stance) + SOFT limb-peak proxy (except jump context, waived). T3
FALLBACK, never recorded as the correct mapping — to be re-matched
to T7 Anna rows when decode lands.

| String / step | Prefix | Row | Profile (hf [a0,a1,stream,atk,thr,btn]; Job 1) |
|---|---|---|---|
| b+1+2,1 step 1 | b+1+2,1 | 355 | hf [21,22,60,1042,0,1] standing armL h; window [8.5,13], armL peak 10 |
| b+1+2,1,1 step 1 | b+1+2,1 | 355 | same as above (shared step) |
| b+1+2,1,1 step 1 | b+1+2,1,1 | 356 | hf [19,22,63,535,0,1] standing armL m; window [7.5,13], armL peak 11 |
| d/f+1+2,2 step 2 | d/f+1+2,2 | 174 | hf [16,16,45,1042,0,2] standing armR h; window [6,10], armR peak 9; GATE-NOTE (standing row, crouch context) |
| f+2,1,2 step 2 | f+2,1,2 | 171 | hf [16,16,45,1042,0,2] standing armR h; window [6,10], armR peak 9 |
| u+1,1 step 1 | u+1,1 | 32 | hf [11,12,39,535,0,1] starts-airborne armL m; jump context, SOFT waived |
| u+1,2 step 2 | u+1,2 | 44 | hf [11,13,53,535,0,2] starts-airborne armR m; jump context, SOFT waived |
| u/b+1,1 step 1 | u/b+1,1 | 34 | hf [11,12,39,535,0,1] starts-airborne armL m; jump context, SOFT waived |
| u/b+1,2 step 2 | u/b+1,2 | 46 | hf [11,13,53,535,0,2] starts-airborne armR m; jump context, SOFT waived |
| u/f+1,1 step 1 | u/f+1,1 | 33 | hf [11,12,39,535,0,1] starts-airborne armL m; jump context, SOFT waived |
| u/f+1,2 step 2 | u/f+1,2 | 45 | hf [11,13,53,535,0,2] starts-airborne armR m; jump context, SOFT waived |

Note on the jump rows: anna rows 32/33/34/44/45/46 are
starts-airborne rows verified ONLY for jump-context steps (SOFT
waived per Batch 1 precedent). They are never used for ground steps.
No verified step uses an anna airborne/jump row for a ground step.
No verified step uses anna row 220, 216, or 35.

## BANK-BLOCKED steps (jin bank, gate-verified, NOT wired)

22 steps pass HARD + SOFT gates in the jin bank but carry row null,
because torch's bound bank is anna and the #1096 engine would play
anna row N for a wired jin row N. Each step preserves its jin row as
`bank_verified_row` + a BANK-BLOCKED reason. Promotion needs
per-step-bank engine support — then these flip to verified
mechanically, no re-adjudication. They must NEVER be played as anna
rows of the same number in the meantime.

| Strings | Jin rows (gate-verified) |
|---|---|
| 2,1 / 2,1,2 / 2,1,2,2 (+ twins) | 220 (standing RP2, window [4,8], armR peak 6), 221 (standing LP1, window [5,9], armL peak 7), 222 (standing RP2, window [3,7], armR peak 5), 223 (standing RP2, window [6.5,10.5], armR peak 8) |
| 1,2 family (1,2 / 1,2,1 / 1,2,1,2 / 1,2,1,H.2 / 1,2,2 / 1,2,uf+1+2 + twins) | 249 (standing RP2, hf [18,19,56,535,0,2], window [7,11.5], armR peak 11) — step 2 only; every step 1 is unmapped (row 248 button-12 rejection) |
| 2,2 / 2,uf+1+2 (+ twins where applicable) | 220 (step 1 only; later steps unmapped) |
| d+1+2,1 / d+1+2,1,2 / d+1+2,2 | 92 (standing chord btn 3, hf [10,10,39,1042,0,3], window [3,7], armL peak 5; GATE-NOTE: standing row, crouch context), 93 (standing RP2, window [3,7], armR peak 5; GATE-NOTE), 183 (standing RP2, hf [13,13,60,535,0,2], window [4.5,8.5], armR peak 6; GATE-NOTE) |

Review-only strings (all steps review, all bank-blocked): 2,1 /
2,1,2 / 2,1,2,2 / d+1+2,2.

### BANK-BLOCKED decision — stated plainly for the coordinator

This lane chose NOT to wire jin-verified rows as verified, even
though the task brief's "wire VERIFIED fills" wording could be read
that way. Reasons: (1) the #1096 engine path cannot play them
correctly for torch (bound bank anna); (2) the engine's own
`_ownRow`/`_rowDonor` rules refuse other-bank rows outright, so
wiring jin rows through the unguarded step-plan branch would
violate the engine's own bank discipline; (3) the play-verify
checklist forbids any step playing a row from the WRONG torch bank,
and a wired jin row N WOULD play anna row N on first play. The
alternative — wiring them verified and letting play-verify catch
the wrong-bank plays — ships known-wrong playback. The
BANK-BLOCKED recording keeps the verification (rows, profiles,
SOFT results, GATE-NOTEs) in the shipped plan file itself, so the
coordinator's per-step-bank engine change promotes these 22 steps
without redoing this lane. If the coordinator instead decides jin
rows SHOULD wire as verified (e.g. a torch bank rebind to jin is
planned), that is a one-line status flip per step from evidence
already in the file — but it must NOT happen silently, because the
current engine would mis-play them.

## Review steps (non-blocked, row null)

- b+2,b+2 step b+2 — candidate anna 368 (standing RP2, hf
  [27,28,70,1042,0,2]): SOFT limb-peak proxy fail, window
  [11.5,16.0], armR peakF 1 outside. Held at review, never wired
  (stricter-than-Pantera-Batch-4 fill rule applied to gate
  candidates as well: a SOFT-failing row is not verified).
- b+2,f+2 step f+2 — candidate anna 369 (same profile as 368):
  SOFT fail, same window/peaks. Held at review.
- f+2,f+1+2 step f+1+2 — candidate anna 175 (duck-dip, btn 3, hf
  [23,23,70,535,0,3]): STANCE-SOFT duck-dip row for a
  standing-context step. Held at review.

## Rejected candidates (20 planned steps)

- 1,2 family step 1 (×6 strings) — jin 248, button 12 != step bits
  1 (recorded-path for 1,2; prefix-move for the rest). Torch's own
  LP1 row is a multi-button clip, rejected for single-LP1 steps.
- b+1,2 / b+1,2,2 step b+1 — jin 216, button 0 != bits 1 AND
  airborne (jump; y0 1.091 ymax 1.529 vs standingY 1.027).
- d+1+2,1 step 1 / d+1+2,1,2 step 1 — jin 177, button 12 != bits 1
  (recorded-dest / prefix-move; demonio + kinpo precedent, same row).
- d/f+1+2,2 step d/f+1+2 — jin 117, throw flag 1 (row is a throw
  row, hf [26,26,20,535,1,3]) for a strike step.
- d/f+1,2 step d/f+1 — jin 179, airborne (jump; y0 0.943 ymax 1.519
  vs standingY 1.027; kinpo precedent, same row).
- f+1+2,1 step 1 — anna 358, button 0 != bits 1.
- f+2,1 step 1 / f+2,1,2 step 1 — anna 321, button 0 != bits 1 AND
  throw flag 1 (hf [0,0,3,2048,1,0]).
- u/b+1,1 / u/b+1,2 step u/b+1 — jin 34, button 3 != bits 1
  (chord row for a single-LP1 step; demonio precedent, same row).
- u/f+1,1 / u/f+1,2 step u/f+1 — jin 33, button 3 != bits 1
  (same precedent).
- u/f+1+2,1 step 1 — anna 506, button 0 != bits 1 AND throw flag 1
  (hf [0,0,176,2048,1,0]).

## No-candidate steps (45 planned)

The expected pattern (all prior lanes): intermediate prefixes are
T8-sourced strings with no T3 row. Their correct clips come from
#988 Step 2 (original T8 refs) or future extraction — never from a
T3 row recorded as correct. Notable families: CJM.2,1; FC.df+2,H.1;
HAM.2,1 family; b+1+2 step 1 (the chord opener has no row — its
later anna steps verify); b+2 step 1; db+1,2 / df+1,2 (crouch LP1
openers, no rows); f+2 step 1 (T8 Anna f+2, no row — its later anna
steps verify); qcf+2,1; u+1 step 1 (jump opener, no row — its later
anna steps verify); u/f+1+2 step 1 (T7 Anna, no row); ws1,2 (both
steps, no rows).

## CSV-only (3 canonicals, 9 steps, audited, never planned)

TACKLE.1,1 / TACKLE.1,1,1 / TACKLE.1,1,1,1 — narrow grapple label
(TACKLE); strike clips excluded; throw-row verification owed
separately. Same CSV-only family shape as skull Batch 1 (and
Pantera/burger/demonio/diablo/kinpo/phantom/scimitar precedent).

## GATE-ONLY (Job 3 / Job 4)

- Job 3 fills: 0. Reason: no Job 3 torch entries exist in the
  verified GPU pack (match_search.json torch 0, job3.log torch
  lines 0). This is NOT a lane failure and no torch Job 3 data was
  hunted or invented. The stricter fill rule (SOFT proxy required,
  burger refinement), Job 3 dedupe, and agreement-note wording
  (fires only for actually-wired gate candidates) apply formally
  and are vacuous for this batch. No SOFT fill inherited from #1097
  (Pantera-specific, still unapproved, does not transfer to torch).
- Job 4 joins: 0. Reason: the corrected join requires Job 2 torch
  entries (key == step prefix, row == candidate row, step == own),
  and Job 2 torch entries = 0. Bank-level candidates jin 47 /
  anna 45 exist but cannot join; a join never promotes anyway.
  The naive cross-fighter join was NOT used.
- Note for the coordinator: future batches for fighters outside
  the 8 are gate-only unless new GPU jobs extend Job 2 / Job 3
  coverage.

## Canonicalization, spelling, corrupted keys, __main

- CORRECTED rule applied (strip ONLY a trailing ~t[378] source
  suffix, then trailing '*'). Batch 1 scope: ZERO input-~
  canonicals.
- File-wide ~ audit (all comma keys, moves + strings): suffix
  forms ~t7.anna (148), ~t7.anna.2 (90), ~t3.anna (56), ~t7.anna.3
  (32), ~t3.anna.2 (32), ~t3.anna.3 (22), ~t7.anna.4 (8), ~t3.anna.4
  (6), ~t8.anna (2) — and exactly ONE input-~ comma key: `d+4,1~4`
  (T8 Anna "Sudden Severe Drop", input_lp d+RK4,LP1~RK4, buttons
  LP1+RK4 — Batch 3/4 scope, NOT Batch 1). Under the corrected rule
  it is its OWN canonical, never a variant of `d+4,1`. Old
  canonical == corrected canonical for every Batch 1 key. No
  Batch 1 plan is affected; no filing arises in this batch, but
  later torch batches must keep `d+4,1~4` as its own canonical.
- __main canonicals in Batch 1 scope: 0. (The demonio Batch 4
  __main filing subtlety was checked and does not arise here.)
- Corrupted keys in Batch 1 scope: 0 (no diablo-style
  df+1,&#58;2 key, no phantom-style f,F+2,&amp;#58;2 key). No
  corrupted-key filing arises here.
- Spelling quirks kept as distinct canonicals (never merged or
  smoothed): no Batch 1 spelling-pair collisions were found that
  change wiring; all 46 canonicals are stored spellings.

## GATE-NOTE steps (standing row, crouch context)

Demonio Batch 1 precedent (gate flags crouch rows for non-crouch
steps, NOT standing rows for crouch steps) — documented with the
re-adjudication note, re-adjudicate if the gate is ever tightened:

- d/f+1+2,2 step 2 — anna 174, VERIFIED (playable).
- d+1+2,1 step d+1+2 — jin 92, BANK-BLOCKED.
- d+1+2,1,2 step d+1+2 — jin 92, BANK-BLOCKED.
- d+1+2,1,2 step 2 — jin 183, BANK-BLOCKED.
- d+1+2,2 step d+1+2 — jin 92, BANK-BLOCKED.
- d+1+2,2 step 2 — jin 93, BANK-BLOCKED.

## ROW DUAL-ROLE CAUTION (observed, not assumed away)

Anna rows 32/33/34/44/45/46 verify ONLY for their jump-context
steps; jin rows 220/221/222/223/249 verify ONLY for their
standing-context steps in their own strings. A row verified for
one string/context is NOT globally verified — every step
gate-checks its own row again, in its own bank. (Concrete
instance: jin row 220 verifies as RP2 move 2's row and as the
2,1-family step-1 row, but it does NOT verify the 1,2-family step
1 — that step is LP1, and its candidate is 248, not 220.)

## Tests

Minimal-tree `node --test` **12 pass / 0 fail** (counts 892/155/79;
Batch 1 keys exactly the 79; verified rows non-null with anna
buttons and throw 0, review/unmapped row null; no soft flags;
verified steps anna-bank only; BANK-BLOCKED steps review with
bank_verified_row present in jin hit_frames; jin row 248 button-12
guard; flagships 2,1 / b+1+2,1 / u+1,1 / d/f+1+2,2 / 1,2; TACKLE
family gains no plan; verified-last-step set exactly the 19;
fighter.js step-plan markers present). `node --check fighter.js`
OK. This is torch's BASELINE test file — later torch batches
accumulate cumulatively with every Batch 1 CONTENT assertion
preserved verbatim (TEST-EVOLUTION RULE; Pantera's latent break
NOT copied).

LIMITATION (honest): full 200-test suite comparison vs pristine
main NOT run — no full current-main checkout exists on this box.
Blast radius is confined by construction: no engine changes, no
moves/strings changes, no prior-plan changes (torch had none), doc
+ test + audit-append only. The suite comparison must be run before
merge (CI will also cover it). NOT play-verified: no fight played.
Nothing here is 'fixed' until the user plays it.

## Stack

Branch from #1096's engine branch
feat/batch1-step-plans-pantera-20261024 (head re-verified before
branching: e2ae41432a — unchanged from inventory time). Torch plans
accumulate: #1096 engine → torch B1 → B2 → B3 → B4. Merges AFTER
#1096 (itself blocked on 12 pre-existing failures / a gate decision
owed — this lane does not fix those and does not merge on
mergeable:true alone). The audit append is append-only vs the #1096
base — rebase after any other stacks' audit entries if they merge
first, never overwrite them. This PR does not touch fighter.js,
pantera.json, burger.json, demonio.json, diablo.json, kinpo.json,
phantom.json, scimitar.json, or skull.json. This lane MERGES NOTHING
itself.

## Formatter deviation (stated, not hidden)

The generic pipeline prescription (json.dumps(indent=2,
ensure_ascii=False) + "\n") does NOT reproduce torch-1096.json
byte-identically: torch's file was written with ensure_ascii=True
(\u2014 / \u2192 escapes) and no trailing newline. Forcing the
generic formatter would rewrite the whole file (every escape +
trailing newline) — a clobber-style diff. This lane uses the file's
own formatter, json.dumps(indent=2) with no trailing newline,
which reproduces torch-1096.json byte-identically (979,107 bytes,
verified by assertion in the wire script), so the committed diff is
exactly 1 addition: string_step_plans. All non-plan top-level keys
deep-equal the input.
