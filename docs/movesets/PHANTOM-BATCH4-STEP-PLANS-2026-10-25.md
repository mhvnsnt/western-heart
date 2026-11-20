# PHANTOM BATCH 4 — STEP PLANS (triples/quads/rest) — 2026-10-25

Phantom Batch 4 is the LAST phantom batch. It completes phantom's string
coverage the way Pantera Batch 4, burger Batch 4, demonio Batch 4, diablo
Batch 4, and kinpo Batch 4 completed theirs, in the locked order
Batch 1 LP1/RP2 → Batch 2 LK3/RK4 → Batch 3 mixed pairs → Batch 4
triples/quads/rest.

Stack: branch from phantom Batch 3's branch
`feat/phantom-batch3-step-plans-20261025` (head eeda14f383da5c4be691ded9f90a59c8ab87772c,
re-verified before branching). Merges AFTER #1123 (after #1122, after #1121,
after #1096). This lane merges nothing itself.

## 1. Universe — derived FIRST, measured, never assumed

Base = phantom Batch 3 branch phantom.json (1019 moves, 191 strings,
320 plans). Re-baselined vs current main (834 moves + 185 quarantined =
1019; 0 main-only moves; 0 Batch 3-branch-only canonicals).

- ALL canonical comma keys in the base file: **321**.
- Batches 1–3: B1 117 + B2 41 + B3 48 = 206, pairwise overlaps 0.
- Batch 4 remainder: **115 canonicals** = **48 triples/quads** (every step
  buttoned, button union 3–4) + **67 rest** (≥1 buttonless step).
- Coverage-complete proof: 206 + 115 = 321; overlap COVERED∩B4 = 0;
  **uncovered [] extra []**. Every canonical comma key in the Batch 3 base
  file is now planned or CSV-audited. The proof would fail otherwise, and
  it does not fail.
- Planned (strike triples/quads): 48. CSV-only: 67, ALL of them rest keys.
  Throw/grapple triples/quads: **0** — no throw-class triple-quad exists in
  this file. The throw-named chain 2+4,1 has move_class string, so it IS
  planned under the narrow label rule (only {PILE_DRIVER, ARM_BREAKER,
  TACKLE} count as grapple labels — stances are NOT grapples), and its steps
  fail strike HARD gates on throw rows 165/425 → unmapped, never wired as
  strikes. That is the brief's case, and it lands exactly as specified.
- Step counts: planned canonicals run 2–10 steps (2: 11, 3: 9, 4: 7, 5: 6,
  6: 4, 7: 2, 8: 3, 9: 2, 10: 4). The four 10-hit strings are all planned:
  1+2,2,1,4,2,2,2,4,1,1; 1+2,2,1,4,4,4,1,1,1,1; 1,2,1,4,2,2,2,4,1,1;
  1,2,1,4,4,4,1,1,1,1. Rest canonicals run 2–6 steps (2: 36, 3: 16, 4: 11,
  5: 3, 6: 1). Rest shapes: 44 buttonless-first, 20 buttonless-last,
  3 buttonless-middle.
- Contexts: planned standing 31 / jump 16 / ws 1 / crouch 0; rest standing
  51 / jump 9 / crouch 7 / ws 0.
- Provenance: 88 in main moves, 27 quarantined-only (live when #988
  merges: (back to wall).b,b,UB; 1+2,P; 3,2,1+2; 3,2,NSS.1+2; 4,4,2,2,1,~1;
  4,4,2,2,NSS.1; 4,4,2,2,NSS.1,~1; FLE.n,FLE.d; NSS.ub+1+3,1+2;
  NSS.ub+1+3,n,1; d+1*(1),n; d+1*(2),n; d+1*(3),n; d+1*(4),n; d+1*(5),n;
  d+1*(6),n; f,F+2,&amp;#58;2; ub+1+3,1+2; ub+1+3,n,1; uf+1+3,b; uf+1+3,d;
  uf+3+4,1; uf+3+4,1,3+4; uf+3+4,1,4; uf+3+4,1,4,1; uf+3+4,1,4,NSS.1;
  ws2,NSS.1,3), 0 Batch 3-branch-only.
- CSV rows: 143 = 115 canonicals + 28 variants (4 planned twins +
  24 rest twins). Plan keys: 52 = 48 planned canonicals + 4 twins
  (2+4,1~t3.yoshimitsu; 4,4,2,2,1~t7.yoshimitsu; u/f+3+4,b+1~t3.yoshimitsu;
  u/f+3+4,b+1,4~t3.yoshimitsu).
- Overlap vs Batches 1–3: [] (the partition is exhaustive by construction
  and verified empirically — any all-buttoned key with union ≤ 2 would have
  raised a COVERAGE GAP abort; none did).

## 2. Canonicalization — corrected rule, Batch 4 scope check

- Input-~ canonicals in Batch 4 scope: EXACTLY THREE, all filed as their
  own keys, never variants: `3~4,U` (rest, buttonless U step, CSV-audited
  only, NOT a variant of `3` — the Batch 4 test asserts it has no plan and
  no plan key carries it as twin_of); `4,4,2,2,1,~1` and
  `4,4,2,2,NSS.1,~1` (triples, union {1,2,4}, planned). The file's full
  old-vs-corrected diff set is exactly these three keys (each listed twice
  because moves + quarantine both carry them).
- __main canonicals in Batch 4 scope: 0. The __main filing rule was checked:
  no Batch 4 canonical ends in __main, and no Batch 4 step prefix has a
  non-empty __main pass-all list in Job 3 (the one __main target with
  pass-all rows in the log, d+1+2__main, is not a Batch 4 step prefix).
  Job 3 dedupe fires zero times (as in phantom Batches 1–3).
- Corrupted keys in Batch 4 scope: ONE — `f,F+2,&amp;#58;2` (double-escaped
  colon: `&amp;#58;` = literal `&#58;` after one unescape; diablo Batch 1's
  `df+1,&#58;2` precedent). Filed verbatim, unmapped, NO plan. Open
  data-quality follow-up: determine the intended key from source data in a
  separate small fix, never guessed here. Its clean twin `f,F+2:2` is a
  separate rest canonical, also CSV-audited only.
- Spelling quirks kept distinct (phantom Batches 1–3 precedent): f,n,d,d/f+1
  vs f,n,d,df+1; f,n,d,d/f+2 vs f,n,d,df+2; f,F+2:2 vs
  f,F+2,&amp;#58;2; u/f+1+2 vs uf+1+3 families. WS-context fix (kinpo
  Batch 1): lowercase no-dot `ws2,NSS.1,3` is WS context, not standing —
  changes no wiring.

## 3. Bank — verified, carried forward, gap-1 replicated

Phantom's T3 bank is YOSHIMITSU — NATIVE, not a fallback (phantom.json
t3_source 'yoshimitsu', t3_bank 'moveset_yoshimitsu.json' on BOTH the
Batch 3 branch and current main; game/assets/anim/t3/ on main contains a
yoshimitsu dir; Job 1 bank yoshimitsu 215 rows; Job 2 phantom entries
1019, ALL bank yoshimitsu; Job 4 yoshimitsu candidates 47; pack dir =
bank name, no diablo-style split).

Gap-1 replication vs the Batch 3 baseline:
- hit_frames: IDENTICAL (blob dfc15d71… on both). Gates use hit_frames +
  Job 1 profiles, so gate decisions are unaffected by anything below.
- rows.pack: row SET identical (215 rows, same slots, stream_frames,
  used_by, source hashes kmd/divmot/SLUS/glb all identical) — but the blob
  differs (Batch 3 baseline cb2a81f… → current main 4bae70a8…). Cause,
  from file evidence: the 2026-10-22 facing-fix re-bake — L/R bone order
  swapped in the bones list, quaternion streams re-encoded, skeleton rest
  pose mirrored (skeleton note carries the facing-fix annotation; foot_tip
  Left/Right swapped with X negated). This is a re-encode of the same
  source data, not new animation content. The wire script's pack check is
  row-presence, and all 7 wired rows are present in the current main pack.
- skeleton: differs only by the facing-fix mirror (see above).
- Conclusion: ZERO bank drift in any gate-relevant sense. No fill suspended
  on bank drift. The blob difference is reported here honestly, not hidden
  behind "zero drift" shorthand.

Bank-specific row rules (never cross-bank): rows 35 and 220 do NOT EXIST
in this bank (absent from hit_frames AND Job 1) — no row-35/row-220 rule
applies at all. Row 216 is a STANDING LP1 row here ([11,11,26,1042,0,1],
Job 1 standing) — NOT king row 216's dash Konvict Kick, NOT jin row 216's
jump row. Row 243 is a CHORD row (button 9 = LP1+RK4) failing every
single-button gate.

## 4. Step tallies

412 total steps = 227 planned + 185 CSV-only (rest).
- Planned: **32 verified / 69 review / 126 unmapped**.
  - Unmapped split: 96 no-candidate + 22 rejected-candidate + 8
    suspended-drift. (The 2 review-status steps on 4,4,2,2,1 / 4,4,2,2,1,~1
    step 5s are counted in review, not here; see §6.)
  - Canonical status (planned only): 27 partial / 21 unmapped-all /
    0 verified-all / 0 review-only. No Batch 4 canonical is verified-all —
    honest: every planned canonical has at least one unmapped or review
    step (most often the chord first step, e.g. 1+2 in the 1+2,2,1,4 family,
    which has no candidate row at all).
  - Plan-key last-step: 4 verified / 13 review / 35 unmapped.
- CSV-only steps (185): rest keys, no gate adjudication beyond recording
  the rest reason; Job 4 joins on rest steps are recorded as "not
  adjudicated (no plan)", never gated on nonsense bits.

## 5. Wired fills — all VERIFIED, gate-verified prefix-move own rows (7 rows)

All are T3 FALLBACK matches (logged in docs/anim/PROCEDURAL_AUDIT.md),
never recorded as the correct mapping, to be re-matched to T7 Yoshimitsu
rows when decode lands. All 7 rows present in the current main yoshimitsu
pack. No Job 3 fills wired (§6).

- Row 294 (standing RK4, hit_frames [29,29,73,1042,0,8]): 1+2,2,1,4 family
  step 4, in every family member (1+2,2,1,4; 1+2,2,1,4,2; 1+2,2,1,4,2,2;
  1+2,2,1,4,2,2,2; 1+2,2,1,4,2,2,2,4; 1+2,2,1,4,2,2,2,4,1;
  1+2,2,1,4,2,2,2,4,1,1; 1+2,2,1,4,4; 1+2,2,1,4,4,4; 1+2,2,1,4,4,4,1;
  1+2,2,1,4,4,4,1,1; 1+2,2,1,4,4,4,1,1,1; 1+2,2,1,4,4,4,1,1,1,1;
  1+2,2,1,4,4,4,1,3+4). Prefix-move own row, SOFT proxy passes.
- Row 306 (standing RP2, [23,26,26,535,0,2]): 1+2,2,1,4,2 family step 5
  (1+2,2,1,4,2; 1+2,2,1,4,2,2; 1+2,2,1,4,2,2,2; 1+2,2,1,4,2,2,2,4;
  1+2,2,1,4,2,2,2,4,1; 1+2,2,1,4,2,2,2,4,1,1). Prefix-move own row.
- Row 298 (standing LP1, [23,24,57,1543,0,1]): 1+2,2,1,4,4,4,1,1 step 8
  (and its 1,1,1 / 1,1,1,1 extensions). Prefix-move own row.
- Row 123 (standing LK3, [10,10,54,1042,0,4]): 3,2,1+2 step 1 and
  3,2,NSS.1+2 step 1. Batch 3 row (3,1 / 3,2 / 3,NSS.1 step 1) re-verified
  in this context per the row dual-role caution — a row verified for one
  string/context is NOT globally verified; this step gate-checked its own
  row again and passed.
- Row 301 (standing RP2, [26,26,55,535,0,2]): f+4,4,2,2,1 step 3. Batch 3
  row (f+4,4,2 family step 3) re-verified in this context, same caution.
- Row 237 (jump LP1, [20,105,146,1543,0,1]): u+2+3,1 step 2, recorded-dest
  source, SOFT waived (jump context, Batch 1 precedent).
- Row 291 (jump LK3+RK4 chord, [31,35,87,535,0,12]): u/f+3+4,1 step 1 and
  the whole u/f+3+4,b+1 family step 1 (u/f+3+4,b+1; u/f+3+4,b+1,3+4;
  u/f+3+4,b+1,4; u/f+3+4,b+1,4,d+1). Batch 2 row (u/f+3+4,3+4 /
  u/f+3+4,u+3+4 step 1) re-verified in this context, SOFT waived.

## 6. Job 3 — 0 fills wired

25 report entries. All candidates are ROW-ONLY, soft-filed, soft-nofiled,
or unknown (not in top10) — never wired under the stricter fill rule
(HARD gates + SOFT proxy + exact level + FULL provenance). The single
exact+FULL candidate, row 160 for 4,4,2,2,1 step 5 (and its ~1 twin's step
5), is HELD at review: SOFT limb-peak proxy fail (window [4.0,8.5], armL
peak 2) — not wired. Other exact+FULL-adjacent candidates documented, not
wired: rows 154/157 (exact, ROW-ONLY) and 237/299 (soft-filed, FULL) for the
same step. No agreement note fires — the note fires ONLY for actually-wired
gate candidates, and no exact+FULL Job 3 candidate exists for any verified
step. Rest-key Job 3 entries (2,1,B; b+1,1,b,B; b+2,d/b; f,F+2;
f,F+2,&amp;#58;2; f,F+2:2; f,F+4; f,n,d,d/f+2; u/f+1+2,d) are
documentation only — no fill was attempted for rest keys.

## 7. Job 4 — 47 joins, none promoting

CORRECTED join only (phantom-only, BANK_DIR yoshimitsu, join iff Job 2 has
a phantom entry key == step prefix, row == candidate row, step == own).
- 19 verified no-action joins (row already verified for the step).
- 18 REJECTED: airborne rows 309/310/260/279/280 (jump/starts-airborne for
  standing steps), ground row 277, throw rows 165/425 (via 2+4,1), button
  mismatches 236 (button 1 vs bits 6) and 200 (button 12 vs bits 1).
- 5 CANDIDATE-not-wired (pass HARD gates, a join never promotes by itself):
  row 299 (1+2,2,1,4,4,4,1,1,1,1 step 9 family), row 305
  (1+2,2,1,4,4,4,1,3+4 step 8), row 255 (f+4,4,2,2,1 step 2), row 304
  (f+4,4,2,2,1 step 5).
- 5 rest-key joins not adjudicated (3+4,d/b ×2, f,F_r283, n,d,d/b,b+1+2,1,
  u/b+1+2,n,1).
- Orphans: 0 (all 47 yoshimitsu Job 4 candidates carried by some phantom
  Job 2 move).

## 8. Review holds — 69, row null, NOT wired

- STANCE-SOFT crouch/duck-dip rows for standing-context steps (21):
  crouch rows 307 (×5) and 308 (×6) — the 2,2,4,1 family step 2s and the
  1+2,2,1,4,2,2,2 family step 6s/7s; duck-dip rows 297 (×5), 311 (×2), 300
  (×1), 305 (×1), 304 (×1) — the 1+2,2,1,4,4,4 family step 7s/8s/10 and
  f+4,4,2,2,1 step 5. Note: row 307 here is phantom's own RP2 row, carried
  by the longer-string prefix moves — it is review here (stance-soft),
  which is distinct from its suspended role as the row-changed prefix move
  2's stale row (§9). Both facts are true in their own steps.
- SOFT limb-peak proxy fails (48): rows 292 (×14) and 293 (×14) — the
  1+2,2,1,4 family step 2s/3s (peaks 1 vs windows [5.5,10.5]/[9.0,14.0]);
  rows 295 (×7) and 296 (×6) — family step 5s/6s (legR peak 38 vs window
  [14.5,18.5]); row 299 (×2) — family step 9s (armL peak 18 vs [5.5,10.0]);
  rows 258/255/302 (×1 each) — f+4,4,2,2,1 steps 1/2/4, matching Batch 3's
  f+4 holds (same windows/peaks, independently re-derived); plus the 2
  Job 3-held step 5s (§6). Proxy-fail = review, never false verify.

## 9. Suspended-drift — 8 steps, stale rows documented, never wired

All three row-changed moves the brief flagged ARE Batch 4 step prefixes:
- Prefix 1 ROW-CHANGED 62→None: 1,2,1,4,2,2,2,4,1,1 step 1 and
  1,2,1,4,4,4,1,1,1,1 step 1 (stale starts-airborne row 62).
- Prefix 2 ROW-CHANGED 307→None: 2,2,4,1 step 1 and 2,2,4,1,1 step 1
  (stale crouch row 307).
- Prefix 4 ROW-CHANGED 243→None: 4,4,2,2,1; 4,4,2,2,1,~1; 4,4,2,2,NSS.1;
  4,4,2,2,NSS.1,~1 step 1s (stale chord row 243).
The other row-changed moves (1_r62, u+1,1~t3.yoshimitsu.2) are NOT Batch 4
step prefixes. Full-file drift census (B3 branch vs current main, both
ways): 670 same / 218 damage-only / 126 anim_ref-changed / 5 ROW-CHANGED;
damage differs on 281 moves (218 damage-only + 63 gap where damage differs
alongside a row/anim_ref change). Damage-only drift does NOT suspend.

## 10. Rejected candidates — 22 (non-suspended, non-review)

- Jump rows for standing steps: 309 (1+2,2,1,4,2,2,2,4 family step 8s;
  2,2,4,1 family step 3s), 310 (1+2,2,1,4,2,2,2,4,1,1 family step 9s;
  2,2,4,1 family step 4s), 260 (3+4,1+2 family step 2s), 279 (3+4,1+2,3+4
  family step 3s), 280 (3+4,1+2,3+4,1 step 4, also button 0).
- Ground row 277 (3+4,1+2 family step 1s, downed-foe row).
- Throw rows: 165 (2+4,1 step 1, button 5 vs bits 10, throw flag 1) and 425
  (2+4,1 step 2, button 0 vs bits 1, throw flag 1) — the throw-named chain
  case, unmapped, never wired as strikes.
- Button mismatches: 236 (u+2+3,1 step 1, button 1 vs bits 6 — the chord's
  own row is an LP1 row, not the RP2+LK3 chord) and 200 (u/f+3+4,1 step 2,
  button 12 vs bits 1 — a chord row for an LP1 step).

## 11. No-candidate steps — 96 planned steps

Dominated by the T8-sourced long families (1,2,1,4,2,2,2,4,1,1 and
1,2,1,4,4,4,1,1,1,1 interiors; 2+4,1's chord step 1 has a candidate but see
§10; the 1+2,2,1,4 family step 1s — the 1+2 chord has no prefix move and no
recorded path), the 4,4,2,2,NSS.1 family interiors, KIN.4,1+2, SS.4,1+2,
NSS.u/f+3+4,b+1 family interiors, NSS.ub+1+3,1+2, ub+1+3,1+2, uf+3+4 family
interiors, and ws2,NSS.1,3. Correct clips come from #988 Step 2 (original
T8 refs) or future extraction — never from a T3 row recorded as correct.

## 12. Tests

Minimal-tree node --test: **52/52 pass** (12 B1 cumulative + 11 B2 cumulative
+ 13 B3 + 16 B4). node --check fighter.js OK. Formatter round-trips the
Batch 3 branch file byte-identically. All 320 Batches 1–3 plans deep-equal.
Batches 1–3 CONTENT assertions preserved verbatim — diff-verified against
the Batch 3-branch originals: only the header note, the count 320→372, the
extra-keys assertion, and the B4 const changed in each of the three older
test files. Limitation (stated in the PR body): full 200-test suite
comparison NOT run — no full current-main checkout on this box; CI must
cover before merge.

## 13. Files

- ~/workspace/phantom-batch4/derive_phantom_batch4.py (universe + step table
  + Job 3/4 + drift)
- ~/workspace/phantom-batch4/phantom_batch4_universe.json (115 canonicals)
- ~/workspace/phantom-batch4/phantom_batch4_step_table.json (412 steps)
- ~/workspace/phantom-batch4/phantom_batch4_job3.json (25 entries)
- ~/workspace/phantom-batch4/phantom_batch4_job4.json (47 joins)
- ~/workspace/phantom-batch4/phantom_batch4_job4_orphans.json (0 orphans)
- ~/workspace/phantom-batch4/phantom_batch4_drift.json
- ~/workspace/phantom-batch4/phantom_batch4_triples_rest.csv (143 rows)
- ~/workspace/phantom-batch4/phantom_batch4_plans.json (52 keys)
- ~/workspace/phantom-batch4/pr/phantom.json (wired, 372 plans)
- ~/workspace/phantom-batch4/pr/phantom-batch{1,2,3,4}-step-plans.test.mjs
- ~/workspace/phantom-batch4/pr/PHANTOM-BATCH4-STEP-PLANS-2026-10-25.md (this doc)
- ~/workspace/phantom-batch4/pr/PROCEDURAL_AUDIT.md (audit append, §14)

## 14. Audit append

docs/anim/PROCEDURAL_AUDIT.md is shared — append-only. The Batch 4 append
lists the 7 wired rows as T3 FALLBACK matches (never the correct mapping),
the 52 plan keys, and the coverage-complete proof. If the Pantera, burger,
demonio, diablo, or kinpo stacks merge first, the append rebases after
their entries (never overwrites them). If #1097 merges first, note its
guard-map interaction: phantom has its own guard map; Pantera's SOFT
decision does not transfer.

## 15. What Batch 4 does NOT do

- No rest key gets a plan (67 keys, CSV-audited only). Planning them needs
  engine support for non-attack prefix steps — future work, named here, not
  guessed.
- No SOFT candidate is wired. No Job 3 fill is wired. No T8 content touched
  (t8_quarantine_20261024 untouched; no UNMAPPED:t7-clip-pending markers
  stripped).
- fighter.js, pantera.json, burger.json, demonio.json, diablo.json,
  kinpo.json untouched.
- No play verification claimed by this lane — tests + file evidence only.
  Playing is the parent's step after merge + deploy (checklist in the PR
  body).
