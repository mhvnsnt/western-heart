# Phantom Batch 3 — mixed-pair step plans (2026-10-25)

Phantom strings whose steps are ALL buttoned and whose button union is exactly 2
with one punch button and one kick button: {LP1,LK3}, {LP1,RK4}, {RP2,LK3},
{RP2,RK4} (any directionals, any contexts). Pure first, then chord-involved.
Stack: #1096 engine → phantom Batch 1 (#1121) → phantom Batch 2 (#1122) →
this Batch 3. This PR merges AFTER #1122 (after #1121, after #1096).

## Universe (measured first, never assumed)

- **48 canonicals: 36 pure single-button + 12 chord-involved. ALL 48 planned,
  0 CSV-only.** 37 variants → **85 CSV rows = 85 plan keys.**
- Pair split: {LP1,LK3} 17, {LP1,RK4} 17, {RP2,LK3} 7, {RP2,RK4} 7.
- Contexts: standing 21, crouch 17, jump 6, ws 4.
- Provenance: 40 in main moves, 8 quarantined-only (live when #988 merges:
  3,1; 3,NSS.1; 4,4,2; 4,4,2,2; DGF.2,4; b+1,1,db+3; b+1,1,db+3,3; df+3,NSS.1),
  0 Batch 2-branch-only.
- Overlap vs Batches 1–2 plan keys: [] (canonicals and full universe keys).
- Canonical status: **4 verified-all / 16 partial / 28 unmapped-all /
  0 review-only.**
- Plan-key last-step: 26 verified / 4 review / 55 unmapped.

## Bank (verified four ways, not assumed)

Phantom's T3 bank is YOSHIMITSU — NATIVE, not a fallback (phantom.json
t3_source 'yoshimitsu', t3_bank 'moveset_yoshimitsu.json' on BOTH the Batch 2
branch and main; t3/ has a yoshimitsu dir with hit_frames + rows.pack +
skeleton; Job 1 bank yoshimitsu, 215 rows; Job 2 phantom entries 1019, ALL bank
yoshimitsu; Job 4 yoshimitsu candidates 47). Pack dir does NOT differ from the
moveset bank name (no diablo-style split).

Gap-1: ZERO bank drift — hit_frames blob dfc15d71…, rows.pack blob cb2a81f…
(215 rows), skeleton blob 82d2546e… identical on the Batch 2 branch and current
main. Main phantom.json blob 4afcf4d2… unchanged since Batch 1.

Bank-specific row rules (never cross-bank): rows 35 and 220 do NOT EXIST in this
bank (absent from hit_frames AND Job 1) — no row-35/row-220 rule applies at all.
Row 216 is a STANDING LP1 row here ([11,11,26,1042,0,1], Job 1 standing) — NOT
king row 216's dash Konvict Kick, NOT jin row 216's jump row. Row 243 is a CHORD
row (button 9 = LP1+RK4) failing every single-button gate.

## Drift census (both ways — both figures true under their definitions)

Full-file census, Batch 2 branch vs current main, 1019 keys: 670 same /
218 damage-only / 126 anim_ref-changed / 5 ROW-CHANGED (1: 62→None,
1_r62: 62→None, 2: 307→None, 4: 243→None, u+1,1~t3.yoshimitsu.2: 62→None);
damage differs on 281 moves (218 damage-only + 63 gap). Damage-only drift does
NOT suspend; row-changed moves SUSPEND.

Row-change re-check vs Batch 3 scope: TWO row-changed moves ARE Batch 3 step
prefixes (see Suspended-drift below). The other three (1, 1_r62,
u+1,1~t3.yoshimitsu.2) are NOT Batch 3 step prefixes.

## Canonicalization (corrected rule, mandatory)

Strip ONLY a trailing source-variant suffix `~t[378]\.[a-z]+(\.\d+)?$`. A `~`
INSIDE the input is Tekken cancel notation, part of the move. Batch 3 contains
**ZERO input-~ canonicals**. The file's old-vs-corrected diffs are all OUTSIDE
Batch 3 scope and were scope-checked, never variants: `3~4,U` (rest key,
buttonless U step), `4,4,2,2,1,~1` and `4,4,2,2,NSS.1,~1` (triples, union
{1,2,4} → Batch 4 scope). All stay their own keys for later batches.

`__main` canonicals in Batch 3 scope: 0. Corrupted keys in Batch 3 scope: 0
(no diablo-style `df+1,&#58;2` key).

Spelling quirks KEPT (distinct canonicals, never merged): d/f+3,1 vs df+3,1
(different step evidence: d/f+3,1 step 1 review row 252 vs df+3,1
no-candidate); d/f+1,4 vs df+1,4 (d/f+1,4 step 1 verified row 223 vs df+1,4
unmapped-all); WS.3,2 vs ws3,2 (both unmapped-all, distinct canonicals);
B+1 vs b+1 families (d+1+4,B+1 vs d+1+4,b+1 — different step evidence: ground
rows 285/286/287/288/289/290 across the families). WS-context fix applied
(lowercase no-dot while-standing spellings are WS context, not standing);
it changes NO wiring.

## Steps: 135 planned = 18 verified / 17 review / 100 unmapped

Unmapped split: **60 no-candidate + 35 rejected-candidate + 5 suspended-drift.**

### Verified (18 steps, 12 distinct rows — all gate-verified prefix-move own rows, T3 FALLBACK)

| Step | Row | hit_frames [start,hit,end,?,throw,button] | Note |
|---|---|---|---|
| 3,1 / 3,2 / 3,NSS.1 step 1 (3) | 123 | [10,10,54,1042,0,4] | standing LK3 |
| b+2,3 step 2 (3) | 173 | [22,22,66,1042,0,4] | standing LK3 |
| d/f+1,4 step 1 (d/f+1) | 223 | [14,15,68,535,0,1] | GATE-NOTE: standing row for a crouch-context step (demonio Batch 1 / diablo Batch 1 / kinpo Batch 1 / phantom Batch 1 precedent — re-adjudicate if the gate is ever tightened) |
| f+4,4,2 / f+4,4,2,2 / f+4,4,2,2,4 step 3 (2) | 301 | [26,26,55,535,0,2] | standing RP2 |
| u+1,3 step 2 (3) | 73 | [9,9,52,535,0,4] | jump LK3, SOFT waived (jump context) |
| u+1,4 step 2 (4) | 88 | [8,9,46,535,0,8] | jump RK4, SOFT waived |
| u/b+1,3 steps 1–2 | 55, 75 | [18,18,52,535,0,1] / [9,9,52,535,0,4] | verified-all, SOFT waived |
| u/b+1,4 steps 1–2 | 55, 90 | [18,18,52,535,0,1] / [8,9,46,535,0,8] | verified-all, SOFT waived |
| u/f+1,3 steps 1–2 | 66, 74 | [18,18,52,535,0,1] / [9,9,52,535,0,4] | verified-all, SOFT waived |
| u/f+1,4 steps 1–2 | 66, 89 | [18,18,52,535,0,1] / [8,9,46,535,0,8] | verified-all, SOFT waived |

All 12 wired rows verified present in current main's yoshimitsu pack (215 rows)
at wire time. No gate-note cases besides d/f+1,4 step 1 (all other verified
steps are standing-context on standing rows or jump-context on jump rows).
Row dual-role caution observed: row 123 is verified for 3-family step 1s only —
it is NOT wired for 2,3 (whose whole-string donor is also row 123, a
class-incorrect LK3 clip for an RP2-first string; donor retirement is designed).

Verified-all canonicals (4): u/b+1,3; u/b+1,4; u/f+1,3; u/f+1,4.
Partial canonicals (16): 2,2,4; 3,1; 3,2; 3,NSS.1; b+1,d/b+3; b+1,d/b+3,d/b+3;
b+1,d/b+3,d/b+3,d/b+3; b+2,3; d/f+1,4; d/f+3,1; f+4,1; f+4,4,2; f+4,4,2,2;
f+4,4,2,2,4; u+1,3; u+1,4.
Verified-last-step plan keys (26): b+2,3; f+4,4,2; u+1,3 + 3 twins; u+1,4 +
3 twins; u/b+1,3 + 3 twins; u/b+1,4 + 3 twins; u/f+1,3 + 3 twins; u/f+1,4 +
3 twins.
Review-last-step plan keys (4): b+1,d/b+3; b+1,d/b+3,d/b+3; f+4,4,2,2;
f+4,4,2,2,4.

### Review holds (17 steps, row null, NOT wired)

- STANCE-SOFT crouch rows for standing-context steps (6): 2,2,4 step 2 cand 308
  (recorded-path); b+1,d/b+3 step 2 cand 251; b+1,d/b+3,d/b+3 steps 2–3 cands
  251/249; b+1,d/b+3,d/b+3,d/b+3 steps 2–3 cands 251/249 (all prefix-move).
- SOFT limb-peak proxy fails (11): d/f+3,1 step 1 cand 252 (window [7.0,11.0],
  legL peak 29); f+4,1 step 1 + f+4,4,2 step 1 + f+4,4,2,2 step 1 + f+4,4,2,2,4
  step 1 cand 258 (window [1.5,6.0], legR peak 10); f+4,4,2 step 2 + f+4,4,2,2
  step 2 + f+4,4,2,2,4 step 2 cand 255 (window [14.5,18.5], legR peak 38);
  f+4,4,2,2 step 4 + f+4,4,2,2,4 step 4 cand 302 (window [9.0,13.5], armR
  peak 26); f+4,4,2,2,4 step 5 cand 303 (window [14.5,18.5], legR peak 39).
  (Same rows, same results as phantom Batch 2's f+4 family review holds:
  258/255/256/254 — the f+4 family is the same file evidence re-derived in a
  new batch scope, not copied.)

### Suspended-drift (5 steps, row null, stale candidate documented, never wired)

- Prefix move 2 ROW-CHANGED 307→None (stale crouch row 307): 2,2,4 step 1
  (recorded-path candidate 307); 2,3 step 1 (prefix-move candidate 307);
  2,d+3 step 1 (prefix-move candidate 307).
- Prefix move 4 ROW-CHANGED 243→None (stale chord row 243, button 9 = LP1+RK4,
  fails every single-button gate regardless): 4,4,2 step 1; 4,4,2,2 step 1
  (both prefix-move candidate 243).

### Rejected-candidate (35 steps, row null, never wired)

- 1+3,1 step 1 (1+3): row 164, throw flag 1 (throw row for a strike step).
- 1+3,1 step 2 (1): row 431, button 0 ≠ step bits 1 + throw flag 1 + airborne
  jump row.
- 2,2,4 step 3 (4): row 309, airborne jump row for a standing step.
- b+1 family step 1s (5 strings: b+1,1,db+3; b+1,1,db+3,3; b+1,d/b+3;
  b+1,d/b+3,d/b+3; b+1,d/b+3,d/b+3,d/b+3): row 286, ground row (downed-foe)
  for standing steps. Job 3 b+1 candidates (154/157/160/162/237/299, all
  ROW-ONLY) NOT wired — ROW-ONLY is not a fill under the stricter fill rule.
- b+1,d/b+3,d/b+3,d/b+3 step 4 (d/b+3): row 250, ground row for a standing step.
- d+1+4 family step 1s (5 B+1 strings + 5 b+1 strings = 10 step-1s):
  row 285, ground row for standing/crouch steps.
- d+1+4,b+1 family step 2+ (b+1 steps): rows 286/287/288/289/290, ground rows
  (d+1+4,b+1 step 2; d+1+4,b+1,b+1 steps 2–3; d+1+4,b+1,b+1,b+1 steps 2–4;
  d+1+4,b+1,b+1,b+1,b+1 steps 2–5; d+1+4,b+1,b+1,b+1,b+1,b+1 steps 2–6).
- f+4,1 step 2 (1): row 259, button 0 ≠ step bits 1.

### No-candidate (60 steps — the honest majority)

Intermediate prefixes are T8-sourced strings with no T3 row; correct clips come
from #988 Step 2 (original T8 refs) or future extraction — never from a T3 row
recorded as correct. Full list: 2,3 step 2; 2,d+3 step 2; 3,1 step 2; 3,2 step 2;
3,NSS.1 step 2; 4,4,2 steps 2–3; 4,4,2,2 steps 2–4; BT.1,3 steps 1–2; DGF.2,4
steps 1–2; NSS.d/f+3,1 steps 1–2; WS.1,1,b+3 steps 1–3; WS.1,1,b+4 steps 1–3;
WS.3,2 steps 1–2; b+1,1,db+3 steps 2–3; b+1,1,db+3,3 steps 2–4; b+2,3 step 1;
d+1+4,B+1 step 2; d+1+4,B+1,1 steps 2–3; d+1+4,B+1,1,1 steps 2–4;
d+1+4,B+1,1,1,1 steps 2–5; d+1+4,B+1,1,1,1,1 steps 2–6; d+2,2,2+3 steps 1–3;
d/f+1,4 step 2; d/f+3,1 step 2; df+1,4 steps 1–2; df+3,1 steps 1–2; df+3,NSS.1
steps 1–2; u+1,3 step 1; u+1,4 step 1; ws3,2 steps 1–2.

Donor rows documented in the CSV, never wired as whole-string clips: 121, 123,
236, 286, 307 (stale, row-changed), 309 (jump clip for ground strings), 62
(stale, row-changed). Donor retirement is DESIGNED: wiring plans replaces
single-row resolution wholesale, even for CLEAN donors, because one row cannot
be correct for a multi-hit string.

## Job 3 fills: 0 wired (10 report entries, all documented, never wired)

Stricter fill rule (burger refinement): a Job 3 fill additionally requires the
SOFT proxy to pass. No entry passes it with exact+FULL provenance, so nothing
wires.

- 2,2,4 / 2,3 / 2,d+3 step 2: rows 115/124 exact ROW-ONLY, rows 159/175
  soft-filed ROW-ONLY (target `2`) — ROW-ONLY is not a fill.
- b+1,1,db+3 / b+1,1,db+3,3 / b+1,d/b+3 / b+1,d/b+3,d/b+3 /
  b+1,d/b+3,d/b+3,d/b+3 step b+1: rows 154/157/160/162/237/299, all ROW-ONLY
  (162 exact, rest unknown-not-in-top10) — not fills.
- b+2,3 step b+2: rows 159/175 exact ROW-ONLY — not fills.
- d/f+1,4 step d/f+1 (verified row 223): rows 134/147 soft-filed ROW-ONLY —
  no agreement note fires (the note fires ONLY for actually-wired gate
  candidates disagreeing with an exact+FULL Job 3 candidate, and no exact+FULL
  Job 3 candidate exists for any verified step).

Dedupe fires zero times: the three Batch 3 step prefixes with a `__main` Job 3
target (d/f+3, f+4, u+1) all have EMPTY pass-all lists for both the plain and
the `__main` target — nothing to dedupe.

## Job 4 joins (CORRECTED join only, BANK_DIR yoshimitsu): 16, none promoting

- REJECTED (12): row 431 on 1+3,1 step 1 (button 0 + throw + airborne);
  row 309 on 2,2,4 step 4 (airborne); rows 287/288/289/290 on d+1+4,b+1-family
  b+1 steps (ground rows).
- CANDIDATE-not-wired (4): row 255 on f+4,4,2 / f+4,4,2,2 / f+4,4,2,2,4 step 4
  (passes HARD gates, NOT wired — a join never promotes by itself); row 303 on
  f+4,4,2,2,4 step 5 (same).
- Orphans: 0 (all 47 yoshimitsu Job 4 candidates carried by some phantom
  Job 2 move).

## Tests

Minimal-tree node --test: **36/36 pass** (12 Batch 1 cumulative + 11 Batch 2
cumulative + 13 Batch 3). node --check fighter.js OK. Formatter round-trips the
Batch 2 branch file byte-identically. Batches 1–2 content assertions preserved
verbatim (diff-verified: cumulative updates changed only the header note, the
plan count 235→320, the extra-keys assertion, and the added B3 const).

Limitation (stated in PR body): full 200-test suite comparison NOT run — no
full current-main checkout on this box; CI must cover before merge.

## What this PR does NOT do

- No fighter.js, pantera.json, burger.json, demonio.json, diablo.json, or
  kinpo.json changes. No T8 content touched (no t8_quarantine_20261024 changes,
  no UNMAPPED:t7-clip-pending markers stripped).
- No SOFT fill is wired or inherited from #1097 (Pantera-specific, still
  unapproved, does not transfer to phantom).
- No play verification is claimed — tests + file evidence only; playing is the
  parent's step after merge + deploy (checklist in the PR body).
