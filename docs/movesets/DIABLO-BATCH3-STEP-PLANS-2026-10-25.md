# Diablo Batch 3 — Mixed-Pair String Step Plans (2026-10-25)

Stack: `feat/diablo-batch3-step-plans-20261025`, branched from diablo Batch 2's
branch `feat/diablo-batch2-step-plans-20261025` (PR #1114). Merges AFTER #1114
(which merges after #1113, after #1096, itself blocked on 12 pre-existing
failures / a gate decision owed — this lane does not fix those and does not
merge on mergeable:true alone). This PR merges NOTHING itself and does not
touch `fighter.js`, `pantera.json`, `burger.json`, or `demonio.json`.

## Scope

Diablo strings whose button SET is exactly one punch + one kick pair —
{LP1,LK3}, {LP1,RK4}, {RP2,LK3}, {RP2,RK4} — any directionals, any contexts
(standing/crouch/jump/ws). Measured explicitly first, never assumed.

**Universe: 22 canonicals (19 pure single-button + 3 chord-involved), ALL
planned, 0 CSV-only.** Twins: 21, so **43 plan keys** (132 Batch 1+2 + 43 = 175).

Pair split (button-set digits, LP1=1, RP2=2, LK3=3, RK4=4):

- {LP1,RK4} (1,4) — 8: b+1,4, d/f+4,1, f+1+4,1, f+1+4,1,1, u+1,4, u/b+1,4,
  u/f+1,4, uf+4,H.1
- {RP2,LK3} (2,3) — 7: 3,2, b+3,2, b+3,3,H.2, d+3,H.2, d/f+3,2, d/f+3,2,2, f+2,3
- {LP1,LK3} (1,3) — 4: 1+3,1, u+1,3, u/b+1,3, u/f+1,3
- {RP2,RK4} (2,4) — 3: b+2,4, d/f+4,2, df+4,2

Contexts: standing 9 / jump 7 / crouch 6 / ws 0.
Provenance: 16 in main moves / 6 quarantined-only (3,2, b+1,4, b+3,3,H.2,
d+3,H.2, df+4,2, uf+4,H.1 — live when #988 merges) / 0 branch-only.

**Canonicalization (CORRECTED rule, mandatory):** strip ONLY a trailing
`~t[378]\.[a-z]+(\.\d+)?$` source-variant suffix. A `~` inside the input is
Tekken cancel notation, part of the move. **Input-~ canonicals in Batch 3
scope: 0** (diablo's cancel notation lives in LP1/RP2 strings, as Batch 1
proved and Batch 2 confirmed for kick strings). **__main records: 0.**
**Spelling quirks kept as stored keys:** d/f+4,2 vs df+4,2 are distinct
canonicals with different step-1 evidence (d/f+4,2 step 1 row 183 verified;
df+4,2 step 1 no candidate) — not merged, not smoothed over (diablo Batch 2
precedent: u/f+3,4 vs uf+3,4).

## Step tally

**47 steps = 15 verified / 3 review / 29 unmapped / 0 suspended-drift.**
Unmapped split: **14 rejected-candidate + 15 no-candidate.**
Canonical status: 1 verified-all (d/f+4,2) / 13 partial / 7 unmapped-all /
1 review-only (b+2,4).

## Verified fills (15 steps, 11 distinct rows, all T3 FALLBACK)

All verified rows are gate-verified (exact-signature equality, button ==
step bits, throw flag 0, stance gate passed or SOFT-waived for jump context).
No Job 3 fill is wired in Batch 3. Every row is baked in main's
heihachi_on_jin pack (198 rows). All T3 FALLBACK, never recorded as correct —
to be re-matched to T7 Heihachi rows when decode lands.

| String | Step | Row | Source | Context | Button | Notes |
|---|---|---|---|---|---|---|
| 3,2 | 3 | 153 | prefix-move | standing | LK3 (4) | standing LK3; prefix 3 damage-only drift, does not suspend |
| d/f+3,2 | 2 | 226 | prefix-move | crouch | RP2 (2) | **standing row for a crouch step — gate-note case (see below)** |
| d/f+3,2,2 | 2 | 226 | prefix-move | crouch | RP2 (2) | **standing row for a crouch step — gate-note case** |
| d/f+3,2,2 | 2 | 227 | prefix-move | crouch | RP2 (2) | **standing row for a crouch step — gate-note case** |
| d/f+4,1 | d/f+4 | 183 | prefix-move | crouch | RK4 (8) | crouch RK4 |
| d/f+4,2 | d/f+4 | 183 | prefix-move | crouch | RK4 (8) | crouch RK4 |
| d/f+4,2 | 2 | 225 | recorded-dest | crouch | RP2 (2) | duck-dip row — passes for crouch outright, NOT a gate-note case |
| df+4,2 | 2 | 225 | recorded-dest | crouch | RP2 (2) | duck-dip row — passes for crouch outright, NOT a gate-note case |
| u+1,3 | 3 | 59 | prefix-move | jump | LK3 (4) | jump LK3; SOFT waived (jump context, Batch 1 precedent) |
| u+1,4 | 4 | 74 | prefix-move | jump | RK4 (8) | starts-airborne RK4; SOFT waived |
| u/b+1,3 | 3 | 61 | prefix-move | jump | LK3 (4) | jump LK3; SOFT waived |
| u/b+1,4 | 4 | 76 | prefix-move | jump | RK4 (8) | starts-airborne RK4; SOFT waived |
| u/f+1,3 | 3 | 60 | prefix-move | jump | LK3 (4) | jump LK3; SOFT waived |
| u/f+1,4 | 4 | 75 | prefix-move | jump | RK4 (8) | starts-airborne RK4; SOFT waived |
| uf+4,H.1 | uf+4 | 74 | prefix-move | jump | RK4 (8) | starts-airborne RK4; SOFT waived |

**Gate-note cases (demonio Batch 1 / diablo Batch 1 precedent):** the
pipeline stance gate flags crouch rows for non-crouch steps, NOT standing
rows for crouch steps. d/f+3,2 step 2 (row 226) and d/f+3,2,2 steps 2–3
(rows 226/227) are standing rows verified for crouch-context steps. If the
gate is ever tightened, these three steps must be re-adjudicated. Row 225
(duck-dip) is NOT a gate-note case: duck-dip passes for crouch context
outright, per diablo Batch 1's row 204 precedent. SOFT proxy passes outright
on rows 226 (armR peak 10 in window [7.5,11.5]) and 227 (armR peak 8 in window
[6.5,10.5]).

## Review steps (3, row null, never wired)

- **b+2,4 step b+2** — candidate row 207 (prefix-move, duck-dip RP2,
  hit_frames [22,22,65,535,0,2]) — STANCE-SOFT: duck-dip row for a
  standing-context step. Held, never wired.
- **b+2,4 step 4** — candidate row 214 (recorded-dest, duck-dip RK4,
  hit_frames [22,22,65,535,0,8]) — STANCE-SOFT: duck-dip row for a
  standing-context step. Held, never wired. Job 4 also joins row 214 as a
  CANDIDATE (passes HARD gates) — a join never promotes, consistent with the
  review hold.
- **f+2,3 step f+2** — candidate row 178 (prefix-move, standing RP2,
  hit_frames [13,14,60,535,0,2]) — SOFT limb-peak proxy fail: window
  [4.5,9.0], armR peak 10. Held, never wired.

## Rejected candidates (14 steps, row null)

- 1+3,1 step 1+3: row 137 — throw flag 1 (throw row, not a strike).
- 1+3,1 step 1: row 340 — button 0 ≠ step bits 1 AND throw flag 1.
- d/f+3,2 step d/f+3: row 181 — airborne row (stance jump) for a crouch step.
- d/f+3,2,2 step d/f+3: row 181 — airborne row for a crouch step.
- d/f+4,1 step 1: row 175 — airborne row (stance jump) for a crouch step.
  (Row 175 is d/f+4,1's own whole-string pick — a jump clip for a ground
  string; retired as a step row.)
- f+1+4,1 step f+1+4: row 246 — throw flag 1.
- f+1+4,1 step 1: row 356 — button 0 ≠ step bits 1 AND throw flag 1.
- f+1+4,1,1 step f+1+4: row 246 — throw flag 1.
- f+1+4,1,1 step 1 (prefix f+1+4,1): row 356 — button 0 ≠ step bits 1 AND
  throw flag 1.
- f+1+4,1,1 step 1 (prefix f+1+4,1,1): row 358 — button 0 ≠ step bits 1.
- u/b+1,3 step u/b+1: row 39 — button 3 ≠ step bits 1.
- u/b+1,4 step u/b+1: row 39 — button 3 ≠ step bits 1.
- u/f+1,3 step u/f+1: row 38 — button 3 ≠ step bits 1.
- u/f+1,4 step u/f+1: row 38 — button 3 ≠ step bits 1.

## Unmapped, no candidate (15 steps)

T8-sourced or stance prefixes with no T3 row; correct clips come from #988
Step 2 or future extraction, never from a T3 row recorded as correct:

- 3,2 step 2; b+1,4 steps 1–2; b+3,2 steps 1–2; b+3,3,H.2 steps 1–3;
  d+3,H.2 steps 1–2; df+4,2 step df+4; f+2,3 step 3; u+1,3 step u+1;
  u+1,4 step u+1; uf+4,H.1 step H.1.

Note: u+1 first steps have NO candidate because prefix u+1 is a no-1096-move
(Batch 1 finding, still holds). The b+1,4 step b+1 entry carries Job 3
candidate notes (see below) but no gate candidate.

## Job 3 candidate fills (0 wired)

One report entry, zero fills, zero DISAGREES notes:

- **b+1,4 step b+1** — candidates row 98 (exact, ROW-ONLY), row 107 (exact,
  ROW-ONLY), row 133 (soft-filed, FULL). Under the stricter fill rule
  (burger refinement: a Job 3 fill additionally requires the SOFT proxy to
  pass, and requires exact + FULL), none wires: 98/107 are ROW-ONLY
  (provenance short), 133 is soft-filed (exactness short). The agreement
  note fires ONLY for actually-wired gate candidates (demonio Batch 4 fix)
  — no verified Batch 3 step has an exact+FULL Job 3 candidate disagreeing
  with its wired gate candidate, so no agreement note fires anywhere in
  Batch 3. Dedupe prefix vs `__main` duplicate pass-all rows: no duplicates
  in scope (no `__main` records in Batch 3).

## Job 4 joins (4, corrected join only, none promoting)

diablo-only, BANK_DIR heihachi_on_jin, join iff Job 2 diablo entry key ==
step prefix, row == candidate row, step == own. The naive cross-fighter
join on key-prefix equality is INVALID and was never used.

- 3,2 step 1 row 153: no-action (already verified).
- b+2,4 step b+2 row 207: CANDIDATE-not-wired (passes HARD gates; a join
  never promotes; consistent with the STANCE-SOFT review hold).
- b+2,4 step 4 row 214: CANDIDATE-not-wired (same).
- d/f+4,1 step 1 row 175: REJECTED (airborne row — consistent with the
  step's unmapped status on the same row).

## Orphans

heihachi_on_jin rows 90, 96, 201 — the same set as diablo Batches 1–2
(unmatched in Job 1's own clip set, present in Job 4's list).

## Drift census (re-baselined vs current main)

**Full census (all 661 base-file moves):** 429 same / 151 damage-only /
78 anim_ref-changed / 3 ROW-CHANGED — identical to Batches 1–2 (main
diablo.json blob ad22b2d8… unchanged since Batch 1).
**Damage-differs-plus-unchanged-row count: 186. Damage-only count: 151.**
Both true under their definitions (186 = 151 damage-only + 35
anim_ref-changed-with-damage-differs; damage differs on 187 total: 186
unchanged-row + 1 row-changed move 1, 11→7). Never silently pick one.
Damage-only drift does NOT suspend (damage ≠ animation); changed moves
SUSPENDED.

**Step-prefix census (38 Batch 3 prefixes):** same 25 / damage-only 6 /
anim_ref-changed 6 / ROW-CHANGED 0 / no-base-move 1 (prefix u+1, a
no-1096-move — its first steps stay unmapped, not suspended).

**Row-change re-check (all 3):** move 1 (46→None) is LP1 scope — no Batch 3
string starts with bare LP1 (1+3,1 starts with chord 1+3); 1_r46 is not a
step prefix (Batches 1–2 finding, re-verified); u+1,1~t3.heihachi.2 is a twin
key whose canonical u+1,1 is Batch 1 scope (twins inherit canonical steps).
**Suspended-drift: 0.**

## Bank verification (gap-1, re-checked for Batch 3)

- Main heihachi hit_frames blob a87184616…, heihachi_on_jin rows.pack blob
  9e59dfe5… (= #1109 baked pack), heihachi_on_jin skeleton blob 7fa83b40…,
  main diablo.json blob ad22b2d8… — all identical to the Batch 1 baseline.
- Cited-row profiles MATCH Job 1 vs hit_frames for every verified + review
  row (153, 183, 225, 226, 227, 59, 60, 61, 74, 75, 76, 178, 207, 214), or the
  fill would have suspended. All 14 are baked in main's pack.
- Rows 205/211/335 exist ONLY via the #1109 bake (pack) — absent from
  hit_frames + Job 1, so they FAIL this lane's hit_frames gate (not wired;
  the gate requires hit_frames profiles). Row 35 does NOT exist in this
  bank; row 220 is a JUMP RK4 row here and no Batch 3 step uses it.

## Donor retirement (DESIGNED)

Wiring plans replaces single-row resolution wholesale, even for CLEAN
donors, because one row cannot be correct for a multi-hit string. CSV
43 rows: donor 9 / own 34. Donor rows retired: standing row 157 for 3,2,
b+1,4, b+3,2, b+3,3,H.2, d+3,H.2, df+4,2 (7 keys — row 157 is RP2 row 157
standing, verified as a Batch 1 step row but not as a whole-string clip for
these strings); standing row 153 for f+2,3 and f+2,3~t7.heihachi (row 153 IS
verified as the step-1 row for 3,2, but as a whole-string clip it cannot
represent f+2,3's two steps); starts-airborne row 46 for uf+4,H.1. HARD-flagged
whole-string picks retired: b+2,4 (HARD stance), d+3,H.2 (HARD stance),
d/f+3,2 + d/f+3,2,2 (HARD stance), d/f+4,1 (jump-clip-for-ground),
d/f+4,1~t3.heihachi (HARD limb), f+1+4,1,1 (HARD limb).

## Twins (21)

Twins inherit their canonical's steps (twin_move_class carried in the plan):

- 1+3,1~t3.heihachi ← 1+3,1; d/f+4,1~t3.heihachi ← d/f+4,1;
  f+2,3~t7.heihachi ← f+2,3;
- u+1,3~t3.heihachi / .2 / .3 ← u+1,3; u+1,4~t3.heihachi / .2 / .3 ← u+1,4;
  u/b+1,3~t3.heihachi / .2 / .3 ← u/b+1,3; u/b+1,4~t3.heihachi / .2 / .3 ←
  u/b+1,4; u/f+1,3~t3.heihachi / .2 / .3 ← u/f+1,3; u/f+1,4~t3.heihachi /
  .2 / .3 ← u/f+1,4.

## Tests (file evidence only — no play verification by this lane)

- Minimal-tree node --test: **35 pass / 0 fail** (13 Batch 1 cumulative +
  11 Batch 2 + 11 Batch 3); node --check fighter.js OK.
- Batch 1 test diff proves every Batch 1 CONTENT assertion preserved
  verbatim — only the count (132→175), extra-keys assertion (B2 → B2+B3),
  a B3 const addition, and a header cumulative note changed. Batch 2 test
  diff: only the count (132→175), non-Batch-2 key count (111→154), and a
  header cumulative note changed (burger test-evolution rule; Pantera's
  latent break NOT copied).
- Formatter round-trips the Batch 2 branch file byte-identically;
  structural diff: all non-plan keys identical, all 132 Batch 1+2 plans
  deep-equal, moves 661 / strings 90 unchanged.
- Limitation (stated in PR body): full 200-test suite comparison NOT run —
  no full current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1114 + this PR merge + deploy + sync, phone portrait)

- d/f+4,2: steps rows 183 (crouch RK4) then 225 (duck-dip RP2) — both
  grounded, no jumping row.
- d/f+3,2: step 1 NO row (old jump row 181 must NOT play), step 2 row 226
  (standing RP2 for a crouch step — gate-note case, plays as filed).
- d/f+3,2,2: step 1 NO row, steps 2–3 rows 226/227.
- d/f+4,1: step 1 row 183 (crouch RK4), step 2 NO row (own jump row 175 must
  NOT play).
- df+4,2: step 1 NO row (old donor row 157 must NOT appear as a
  whole-string clip), step 2 row 225.
- 3,2: step 1 row 153 (standing LK3), step 2 NO row (old donor row 157 must
  NOT appear as a whole-string clip).
- u+1,3 / u+1,4 / u/b+1,3 / u/b+1,4 / u/f+1,3 / u/f+1,4: first step NO row
  (u+1 / u/b+1 / u/f+1 prefix rows 38/39 must NOT play — button 3 ≠ LP1),
  last step rows 59 / 74 / 61 / 76 / 60 / 75, jump context.
- uf+4,H.1: step 1 row 74 (starts-airborne RK4, jump context), step 2 NO row
  (old donor row 46 must NOT appear as a whole-string clip).
- b+2,4: NO row any step (review rows 207/214 held, must NOT play).
- f+2,3: NO row any step (review row 178 held, must NOT play).
- Unmapped-all strings (b+1,4, b+3,2, b+3,3,H.2, d+3,H.2, 1+3,1, f+1+4,1,
  f+1+4,1,1): NO row any step — old donor/throw rows 137/157/246/340/356/358
  must NOT play.
- No step plays row 35 (does not exist in this bank) or row 220 unless
  genuinely airborne per heihachi_on_jin profiles.
- Diablo Batches 1–2 spot-checks undisturbed (2,1 family 157/158, b+1+2,2
  98/99, d/f+1+2,2 110/204, u+1,1 step 2 row 40 jump-only, 1,1 step 1 still
  suspended; Batch 2: u/f+4,3 rows 86/150, u/f+4,4 rows 86/195, 3,4 step 1
  row 153, d/f+4,4 step 1 row 183, d/f+4,4,4 steps 183 / NO row / NO row
  (review row 191 held, must NOT play), u/f+3,4 step 1 row 60, uf+3,4 step 2
  row 74).

## Running tally (Batches 1–3)

99 canonicals / 175 plan keys (B1: 66/111; B2: 11/21; B3: 22/43).
