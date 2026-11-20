# Diablo Batch 2 step plans (LK3/RK4-only strings, 2026-10-25)

Stack: #1096 engine → diablo Batch 1 (PR #1113) → this Batch 2. Branch
`feat/diablo-batch2-step-plans-20261025` from diablo Batch 1's branch
`feat/diablo-batch1-step-plans-20261025` (head d76f8188…, verified before
branching). Merges AFTER #1113 (after #1096, itself blocked on 12
pre-existing failures / a gate decision owed — this lane fixes none of those
and merges nothing itself). This PR does not touch fighter.js, pantera.json,
burger.json, or demonio.json. No T8 removals: t8_quarantine_20261024 untouched,
no UNMAPPED:t7-clip-pending markers stripped.

## Universe (measured, not assumed)

11 canonical LK3/RK4-only strings (every step buttoned, button union subset
of {3,4}): 11 pure single-button, 0 chord-involved — measured, not assumed
from Batch 1's 45 pure + 21 chord. 21 plan keys (11 planned canonicals +
10 twins); 21 CSV rows; 0 CSV-only keys (Batch 2 has zero throw/grapple
canonicals). Contexts: standing 4, crouch 2, jump 4, ws 1. Provenance: 10 in
main moves, 1 quarantined-only (FUJ.3,4 — live when #988 merges), 0 in the
Batch 1 branch only. Base moves 661 = main moves 595 + quarantine 66.

Canonicals: 3,4 · FUJ.3,4 · WS.4,4 · b+3,3 · d/f+4,4 · d/f+4,4,4 ·
u/f+3,4 · u/f+4,3 · u/f+4,4 · uf+3,4 · ws4,4.
Twins: 3,4~t7.heihachi · WS.4,4~t7.heihachi · b+3,3~t7.heihachi ·
b+3,3~t7.heihachi.2 · u/f+3,4~t3.heihachi · u/f+3,4~t3.heihachi.2 ·
u/f+3,4~t3.heihachi.3 · u/f+4,3~t3.heihachi · u/f+4,4~t3.heihachi ·
u/f+4,4~t3.heihachi.2.

## Bank (verified, carried from Batch 1's four-way proof — not re-assumed)

diablo's T3 bank is HEIHACHI: diablo.json t3_source 'heihachi', t3_bank
'moveset_heihachi.json' on BOTH the Batch 1 branch and main; t3/ on main
contains a heihachi dir (hit_frames + skeleton, NO rows.pack.json — the known
404 gap) and a heihachi_on_jin dir (hit_frames + rows.pack.json + skeleton);
the two hit_frames.json are the SAME blob a87184616… (bank
teardown/tekken3/animations/divmot13_heihachi.bin); Job 1 bank
heihachi_on_jin (195 rows), Job 2 bank heihachi (661 entries), Job 4 bank
heihachi_on_jin (49 candidates). Resolution: moveset/Job 2 heihachi ↔ Job 1 /
Job 4 / pack heihachi_on_jin ↔ divmot13 on the jin rig (heihachi191 KMD
lacks hip/shoulder data).

Bank-specific rules, never cross-bank: row 35 does NOT EXIST in this bank
(absent from hit_frames + Job 1) — no row-35 rule applies; row 220 is a JUMP
RK4 row here (hit_frames [39,39,88,535,0,8]), NOT jin's standing RP2 row,
NOT king's jumping chord row, NOT bryan's button-0 row; heihachi_on_jin row
216 is a DUCK-DIP row, NOT jin's jump row or king's dash Konvict Kick.
Diablo's own LP1 row 46 is STARTS-AIRBORNE (same class as Pantera LP1→king
row 38); RP2 own row 157 is standing (clean). Rows 205/211/335 exist ONLY
via the #1109 bake (pack) — absent from hit_frames + Job 1, so they FAIL
this lane's hit_frames gate and are never wired.

Gap-1 re-verification (replicated): main heihachi hit_frames blob
a87184616…, heihachi_on_jin rows.pack blob 9e59dfe5… (= #1109's baked pack),
heihachi_on_jin skeleton blob 7fa83b40…, main diablo.json blob ad22b2d8… —
all IDENTICAL to the Batch 1 baseline. Cited-row profiles MATCH Job 1 vs
hit_frames for all 7 distinct verified rows + the review row + the rejected
row. All cited rows are baked in main's heihachi_on_jin pack (198 rows).

## Tallies

23 steps = 9 verified / 1 review / 13 unmapped (11 no-candidate +
2 rejected-candidate + 0 suspended-drift). Canonical status: 2
verified-all / 5 partial / 4 unmapped-all / 0 review-only. Plan-key
last-step: 6 verified / 1 review / 14 unmapped. Job 3 fills wired: 0.
Job 4 joins: 4, none promoting. Orphans: heihachi_on_jin rows 90, 96, 201
(same set as Batch 1).

## Every wired fill (verified only; jin hit_frames button == step bits, throw 0; T3 FALLBACK logged in the audit)

- u/f+4,3 verified-all: rows 86/150 (jump context, SOFT waived per Batch 1
  precedent). Step 1 row 86 = prefix-move u/f+4 (hit_frames [24,26,81,535,0,8],
  Job 1 stance jump). Step 2 row 150 = recorded-dest (hit_frames
  [35,37,65,535,0,4], Job 1 stance jump).
- u/f+4,4 verified-all: rows 86/195 (jump context, SOFT waived). Step 2 row
  195 = recorded-dest (hit_frames [45,48,80,271,0,8], Job 1 stance jump).
- 3,4 step 1 → row 153 (prefix-move; standing LK3, hit_frames
  [19,23,61,535,0,4], SOFT window [7.5,13.5] legL peakF 10 passes outright).
  Step 2 unmapped (no candidate).
- d/f+4,4 step 1 → row 183 (prefix-move; crouch RK4, hit_frames
  [16,16,62,799,0,8], SOFT window [6.0,10.0] legR peakF 8 passes outright).
  Step 2 unmapped (rejected candidate below).
- d/f+4,4,4 step 1 → row 183 (same prefix-move evidence as d/f+4,4).
  Step 2 unmapped (rejected candidate below). Step 3 review (below).
- u/f+3,4 step 1 → row 60 (prefix-move; jump LK3, hit_frames
  [9,9,52,535,0,4], SOFT waived). Step 2 unmapped (no candidate).
- uf+3,4 step 2 → row 74 (prefix-move; starts-airborne RK4, hit_frames
  [8,9,46,535,0,8], jump context, SOFT waived). Step 1 unmapped (no
  candidate).

No verified step uses row 35 (does not exist in this bank) or row 220. No
verified step is a standing row for a crouch-context step (no Batch 1
gate-note case: row 183 is crouch for crouch steps, row 153 is standing for
a standing step). No step carries a soft flag. All verified rows are T3
FALLBACK, never recorded as correct.

## Every rejected / held candidate (row null, never played)

- Review (1): d/f+4,4,4 step 3, candidate row 191 (recorded-dest, standing
  RK4, hit_frames [15,16,51,535,0,8]) — SOFT limb-peak proxy fail: window
  [5.5,10.0], legR peakF 20. Held, never wired.
- Rejected (2): d/f+4,4 step 2 candidate row 190 (recorded-dest) and
  d/f+4,4,4 step 2 candidate row 190 (prefix-move) — button 12 (LK3+RK4
  chord row, hit_frames [24,25,59,535,0,12], Job 1 stance standing) ≠ step
  bits 8 for single-RK4 steps. Row 190 is the whole-string own pick for
  d/f+4,4 — correctly retired as a step row.
- Unmapped with NO candidate (11): 3,4 step 2; FUJ.3,4 steps 1–2; WS.4,4
  steps 1–2; b+3,3 steps 1–2; u/f+3,4 step 2; uf+3,4 step 1; ws4,4 steps 1–2.
  Every one has no recorded path and no prefix-move row (T8-sourced or
  stance prefixes with no T3 row); correct clips come from #988 Step 2 or
  future extraction, never from a T3 row recorded as correct.
- Suspended-drift (0): none of the 3 row-changed moves (1, 1_r46,
  u+1,1~t3.heihachi.2, all 46→None) is a Batch 2 step prefix — 1 is LP1 scope,
  1_r46 is not a step prefix, u+1,1~t3.heihachi.2 is a twin key whose
  canonical u+1,1 is Batch 1 scope. Verified, not assumed.
- Job 3 (0 fills): 3 Batch 2 prefixes appear in job3.log (d/f+4,4,
  d/f+4,4,4, uf+3), ALL with EMPTY pass-all lists; the other 17 prefixes
  absent entirely — 0 candidates, so the burger-refinement SOFT-proxy fill
  rule is carried but not exercised. No SOFT fill inherited from #1097.
- Job 4 (4 joins, corrected join only, none promoting): 3 no-action on
  already-verified steps (3,4 step 1 row 153; u/f+4,3 step 2 row 150;
  u/f+4,4 step 2 row 195); 1 CANDIDATE-not-wired (d/f+4,4,4 step 3 row 191 —
  passes HARD gates, NOT wired, a join never promotes; consistent with the
  SOFT-fail hold on the same row).
- Orphans: heihachi_on_jin rows 90, 96, 201 (no diablo Job 2 move carries
  them, any step).

## Drift census (both ways)

Full census over all 661 base-file moves (Batch 1 branch file vs current
main): 429 same / 151 damage-only / 78 anim_ref-changed / 3 ROW-CHANGED
(1, 1_r46, u+1,1~t3.heihachi.2, all 46→None) — identical to Batch 1's census,
as expected (main diablo.json blob ad22b2d8… unchanged since Batch 1).
Damage differs on 187 moves (186 unchanged-row + 1 row-changed 1, 11→7).
Damage-only drift noted, NOT suspending (damage ≠ animation).
Step-prefix census (20 Batch 2 prefixes): same 9 / damage-only 6 /
anim_ref-changed 5 / ROW-CHANGED 0 / no-base-move 0.

## Canonicalization (corrected rule, carried from Batch 1)

Strip ONLY a trailing source-variant suffix ~t[378]\.[a-z]+(\.\d+)?$; a ~
inside the input is Tekken cancel notation, part of the move. Batch 2
contains NO input-~ canonicals and NO __main records — unlike Batch 1's 6
input-~ own canonicals, diablo's cancel notation lives in LP1/RP2 strings,
not kick strings. (The full-moves-list diagnostic still shows Batch 1's
input-~ keys — e.g. 1,2,2~1, 2,2~1+2, b+1,2~1+2, f+2~1,1+2 — because the
check runs over all moves keys; none falls in Batch 2 scope.)

## Spelling quirks (kept as stored keys, not merged)

u/f+3,4 vs uf+3,4 are distinct canonicals: u/f+3,4 step 1 verifies row 60
while uf+3,4 step 1 has no candidate; uf+3,4 step 2 verifies row 74 while
u/f+3,4 step 2 has no candidate. Same logical string, different stored
spellings, different own rows — kept separate per the burger Batch 2
precedent (db+ vs d/b+, ws3 vs WS.3), not smoothed over.

## Donor retirement (designed, not a regression)

CSV 21 rows: today's picks donor 9 / own 11 / notation 1; HARD-flagged 2;
jump-clip-for-ground 0 (Batch 2 has no jumping whole-string donor for a
ground string, unlike Batch 1's sharpest cases). Donor rows retired by
plans: standing row 104 as the whole-string clip for 3,4 family, FUJ.3,4,
WS.4,4 family, ws4,4 (6 keys) and standing row 153 as the whole-string clip
for the b+3,3 family (3 keys) — row 153 IS verified as the step-1 row for
3,4, but as a whole-string clip it cannot represent b+3,3's two steps.
Notation pick retired: u/f+3,4's whole-string notation row 74 (the same row
that verifies as uf+3,4's step 2 — per-step verification, not global).
HARD-flagged whole-string picks: d/f+4,4 own row 190 (HARD stance — standing
legL chord row for a crouch RK4 string) and d/f+4,4,4 own row 191 (HARD
limb) — both correctly retired as step rows (190 rejected on button, 191
held on SOFT).

## Tests (file evidence only — no play verification by this lane)

Minimal-tree node --test: 24 pass / 0 fail (13 Batch 1 cumulative + 11
Batch 2); node --check fighter.js OK. Batch 1 test diff proves every Batch 1
CONTENT assertion preserved verbatim — only the count (111→132),
extra-keys assertion ([] → the 21 Batch 2 keys), a B2 const addition, and a
header cumulative note changed (burger test-evolution rule; Pantera's latent
break NOT copied). Formatter round-trips the Batch 1 branch file
byte-identically; structural diff: all non-plan keys identical, all 111
Batch 1 plans deep-equal, moves 661 / strings 90 unchanged.
Limitation (stated in the PR body): full 200-test suite comparison NOT run
(no full current-main checkout on this box) — CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1113 + this PR merge + deploy + sync, phone portrait)

- u/f+4,3: rows 86/150, jump context; u/f+4,4: rows 86/195, jump context.
- 3,4: step 1 row 153 (grounded LK3), step 2 NO row (old donor 104 must NOT
  appear as a whole-string clip).
- d/f+4,4: step 1 row 183 (crouch RK4), step 2 NO row (chord row 190 must NOT
  play as a step row); d/f+4,4,4: steps 1/2/3 = 183 / NO row / NO row
  (review row 191 held, must NOT play).
- u/f+3,4: step 1 row 60 (jump), step 2 NO row; uf+3,4: step 1 NO row,
  step 2 row 74 (jump).
- Unmapped-all strings (FUJ.3,4, WS.4,4, b+3,3, ws4,4): NO row any step —
  old donor rows 104/153 must NOT appear as whole-string clips.
- No step plays row 35 (does not exist in this bank) or row 220 unless
  genuinely airborne per heihachi_on_jin profiles.
- Diablo Batch 1 spot-checks undisturbed (2,1 family 157/158, b+1+2,2 98/99,
  d/f+1+2,2 110/204, u+1,1 step 2 row 40 jump-only, 1,1 step 1 still suspended).
- Quarantined-only strings (FUJ.3,4) behave per plan ONLY after #988 merges.
