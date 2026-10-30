# Diablo Batch 4 — Triples/Quads/Rest Step Plans (2026-10-25)

The LAST diablo batch. Completes diablo string coverage the way Pantera Batch 4,
burger Batch 4, and demonio Batch 4 completed theirs. Stack: #1096 engine →
diablo Batch 1 (#1113) → Batch 2 (#1114) → Batch 3 (#1115) → this Batch 4.
Branch: feat/diablo-batch4-step-plans-20261025, base = diablo Batch 3 branch.
Merges AFTER #1115 (after #1114, after #1113, after #1096). Merges NOTHING itself.

## Universe (derived FIRST)

Base = diablo Batch 3 branch diablo.json: 661 moves / 90 strings / 175 plans.
Batches 1–3 covered every canonical whose steps all carry buttons and whose
button union ≤ 2. Batch 4 = everything else:

- Triples/quads: every step buttoned, button union 3–4 distinct buttons (incl.
  3-button chords + 10-hit strings): 28 canonicals, ALL planned.
- Rest: ≥1 buttonless step (dash/movement/stance-prefix sequences): 74 canonicals,
  CSV-AUDITED ONLY, never planned — planning them needs engine support for
  non-attack prefix steps (future work, named, not guessed).
- Throw-class triple-quads in Batch 4 scope: 0 (no throw-class canonical fell in
  the triples/quads group; the narrow label rule — only {PILE_DRIVER, ARM_BREAKER,
  TACKLE} count as grapple labels, stances are NOT grapples — was applied and
  changed nothing here).

Provenance: 88 in main moves, 14 quarantined-only (live when #988 merges),
0 branch-only. Contexts: standing 74, crouch 26, ws 1, jump 1.
CSV rows: 137 (102 canonicals + 35 source-variant twins). Plan keys: 42
(28 planned canonicals + 14 twins).

## Coverage-complete proof

Canonical comma keys in the Batch 3 base file: 201.
66 (Batch 1) + 11 (Batch 2) + 22 (Batch 3) + 102 (Batch 4) = 201.
Pairwise overlaps between batch universes: 0. Uncovered: []. Extra: [].
Every canonical comma key in the Batch 3 base file is planned or CSV-audited.

## Step tallies

450 steps total = 165 planned + 285 rest.
Planned: 110 verified / 20 review / 35 unmapped.
Unmapped split: 2 suspended-drift + 18 rejected-candidate + 15 no-candidate.
Canonical status (planned only): 1 verified-all, 20 partial, 7 unmapped-all,
0 review-only. Plan-key last-step status: 13 verified / 5 review / 24 unmapped.
Verified rows (21 distinct, all baked in main's heihachi_on_jin pack):
86, 150, 157, 158, 159, 160, 161, 163, 164, 165, 223, 226, 227, 228, 230,
231, 232, 233, 235, 236, 237.

## Planned canonicals — step table (one verified row per prefix step)

- 1,2,4 [standing] -> 1=unmapped | 2=unmapped | 4=unmapped
- 1,b+2,4 [standing] -> 1=unmapped | b+2=unmapped | 4=unmapped
- 2+4,1 [standing] -> 2+4=unmapped | 1=unmapped
- 2,1,2,2,3 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161
- 2,1,2,2,3,4 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161 | 4=review
- 2,1,2,2,3,4,4 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161 | 4=review | 4=row 163
- 2,1,2,2,3,4,4,1 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161 | 4=review | 4=row 163 | 1=row 164
- 2,1,2,2,3,4,4,1,2 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161 | 4=review | 4=row 163 | 1=row 164 | 2=row 165
- 2,1,2,2,3,4,4,1,2,1 [standing] -> 2=row 157 | 1=row 158 | 2=row 159 | 2=row 160 | 3=row 161 | 4=review | 4=row 163 | 1=row 164 | 2=row 165 | 1=unmapped
- WS.3,1+2 [ws] -> WS.3=unmapped | 1+2=unmapped
- d/f+3,2,2,4 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228
- d/f+3,2,2,4,4 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review
- d/f+3,2,2,4,4,1 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230
- d/f+3,2,2,4,4,1,2 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 2=row 235
- d/f+3,2,2,4,4,1,2,1 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 2=row 235 | 1=row 236
- d/f+3,2,2,4,4,1,2,1,2 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 2=row 235 | 1=row 236 | 2=row 237
- d/f+3,2,2,4,4,1,2,1,2,1 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 2=row 235 | 1=row 236 | 2=row 237 | 1=unmapped
- d/f+3,2,2,4,4,1,4 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 4=row 231
- d/f+3,2,2,4,4,1,4,1 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 4=row 231 | 1=row 232
- d/f+3,2,2,4,4,1,4,1,2 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 4=row 231 | 1=row 232 | 2=row 233
- d/f+3,2,2,4,4,1,4,1,2,1 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 4=row 231 | 1=row 232 | 2=row 233 | 1=unmapped
- d/f+3,2,2,4,4,1,4,1,2,4 [crouch] -> d/f+3=unmapped | 2=row 226 | 2=row 227 | 4=row 228 | 4=review | 1=row 230 | 4=row 231 | 1=row 232 | 2=row 233 | 4=unmapped
- df+3,1+2 [crouch] -> df+3=unmapped | 1+2=unmapped
- df+3,1+2,1 [crouch] -> df+3=unmapped | 1+2=unmapped | 1=unmapped
- f+1+2,b+2,4 [standing] -> f+1+2=row 223 | b+2=review | 4=review
- f+1+2,b+2,4,1 [standing] -> f+1+2=row 223 | b+2=review | 4=review | 1=unmapped
- u/f+4,3,1 [jump] -> u/f+4=row 86 | 3=row 150 | 1=unmapped
- ws3,1+2 [standing] -> ws3=unmapped | 1+2=unmapped

## Review holds (20 steps, NOT wired)

- Row 229, SOFT limb-peak proxy fail (window [10.0,14.0], legR peak 0): 11 steps
  (the d/f+3,2,2,4-family second-4 steps). Proxy-fail = review, never false verify.
- Row 162, SOFT limb-peak proxy fail (window [16.5,21.5], legR peak 6): 5 steps
  (the 2,1,2,2,3,4-family 4 steps, prefix-move + recorded-dest).
- Rows 207/214, STANCE-SOFT duck-dip rows for standing-context steps: 2 steps each
  (f+1+2,b+2,4 and f+1+2,b+2,4,1 steps b+2 and 4; Job 4 CANDIDATE, never promoted).

## Rejected candidates (18 steps, gate-failed, NOT wired)

- 2+4,1 step 2+4: row 138 throw flag; step 1: row 342 button 0 ≠ LP1, throw flag,
  airborne row for a standing step.
- 2,1,2,2,3,4,4,1,2,1 step 2: row 166 airborne (stance jump) for a standing step.
- d/f+3,2,2,4-family step d/f+3: row 181 airborne (stance jump) for crouch steps
  (12 steps across the family — the d/f+3 prefix is a jump, not a ground crouch step).
- d/f+3,2,2,4,4,1,4,1,2,1 step 1: row 239 airborne for a crouch step.
- f+1+2,b+2,4,1 step 1: row 215 button 0 ≠ LP1, airborne for a standing step.
- u/f+4,3,1 step 1: row 152 button 12 ≠ LP1, throw flag, ground (downed-foe) row
  for a standing string step.

## No-candidate steps (15 planned steps)

Intermediate prefixes are T8-sourced strings with no T3 row: 1,2,4 steps 2/4;
1,b+2,4 steps b+2/4; WS.3,1+2 both steps; df+3,1+2 both steps; df+3,1+2,1 all
three steps; ws3,1+2 both steps; d/f+3,2,2,4,4,1,2,1,2,1 last step 1;
d/f+3,2,2,4,4,1,4,1,2,4 last step 4. Correct clips come from #988 Step 2
(original T8 refs) or future extraction — never from a T3 row recorded as correct.

## Suspended-drift (2 steps)

- 1,2,4 step 1 and 1,b+2,4 step 1: prefix move 1 ROW-CHANGED 46→None (1096 vs
  current main). Stale candidate row 46 documented, never wired.
- The other 2 row-changed moves (1_r46, u+1,1~t3.heihachi.2) are not Batch 4 step
  prefixes. Drift census (all 661 moves, identical to Batches 1–3): 429 same /
  151 damage-only / 78 anim_ref-changed / 3 ROW-CHANGED; damage differs on 187
  (186 unchanged-row + 1 row-changed). Damage-only drift does NOT suspend.

## Job 3 / Job 4

Job 3 fills wired: 0. Report entries: 4, none wired under the stricter fill rule
(exact level + full provenance + HARD gates + SOFT proxy). one DISAGREES note — f+1+2,b+2,4 and f+1+2,b+2,4,1 step f+1+2: Job 3 exact+FULL candidate row 107 disagrees with wired gate candidate row 223, gate candidate kept (own/recorded row is stronger file evidence). The agreement note fires ONLY for actually-wired gate candidates (demonio Batch 4 fix), and row 223 is wired; no note fires on the suspended 1,2,4 / 1,b+2,4 steps.
Job 4 joins (CORRECTED join only, BANK_DIR heihachi_on_jin, diablo-only): 30 —
23 no-action (step already verified), 4 CANDIDATE-not-wired (rows 207/214 in the
f+1+2,b+2,4 family — a join NEVER promotes), 3 REJECTED (rows 342, 166, 239).
Orphans: heihachi_on_jin rows 90, 96, 201 (same set as Batches 1–3).

## Bank (verified, carried from Batches 1–3 four-way proof)

Diablo's T3 bank is HEIHACHI: moveset/Job 2 `heihachi` ↔ Job 1/Job 4/pack
`heihachi_on_jin` ↔ divmot13 on the jin rig (heihachi191 KMD lacks hip/shoulder
data). Both hit_frames.json are blob a87184616…. game/assets/anim/t3/ on main has
BOTH a `heihachi` dir (hit_frames + skeleton, NO rows.pack.json — known 404 gap)
and a `heihachi_on_jin` dir (hit_frames + rows.pack.json + skeleton). Gap-1
replication: #1096 vs main hit_frames + skeleton blobs IDENTICAL; pack differs
only by the explained #1109 bake (main has MORE rows); cited-row profiles MATCH
Job 1 vs hit_frames for every verified + review row, or the fill would suspend.
Bank-specific rules (never cross-bank): row 35 does NOT EXIST in this bank; row 220
is a JUMP RK4 row here (hit_frames [39,39,88,535,0,8]); heihachi_on_jin row 216 is a
DUCK-DIP row. Rows 205/211/335 exist ONLY via the #1109 bake (pack), absent from
hit_frames + Job 1, so they FAIL the hit_frames gate and are never wired.

## Canonicalization, spelling, corrupted key

CORRECTED rule: strip ONLY a trailing ~t[378]\.[a-z]+(\.\d+)?$ source-variant suffix.
Input-~ canonicals in Batch 4 scope: 4, all rest/CSV-only (1,2,2~1+2,u, 2,2~1+2,u,
b+1,2~1+2,u, f+2~1+2,u) — filed as their own canonicals, never variants of stripped
keys. __main records: 0. Spelling quirks kept as stored keys: WS.3,1+2 vs ws3,1+2
are distinct canonicals (both unmapped-all, different evidence paths); d/f+3 vs df+3
families are distinct canonicals.
Corrupted key df+1,&amp;#58;2* (HTML-escaped colon + hold marker) is NOT Batch 4
scope: it is a Batch 1-scope key (LP1/RP2 union {1,2}), quarantined-only on main.
Same open data-quality follow-up as Batch 1: determine the intended key from source
data in a separate small fix, never guessed.

## Gate-note cases (standing rows for crouch-context steps)

d/f+3,2,2,4-family verified steps with standing rows 226, 227, 230, 231, 232, 235,
236 follow the demonio Batch 1 / diablo Batch 1 / diablo Batch 3 precedent: the
pipeline stance gate flags crouch rows for non-crouch steps, not standing rows for
crouch steps; if the gate is ever tightened these steps must be re-adjudicated.
Rows 228 (crouch), 233 and 237 (duck-dip) pass for crouch context outright — NOT
gate-note cases. Row dual-role caution (Pantera Batch 4): a row verified for one
string/context is NOT globally verified — every step gate-checked its own row again.

## Rest keys (74 canonicals, CSV-audited only, NO plan)

- 1,2,2~1+2,u
- 2,2~1+2,u
- H.2+3,F
- H.b,b,n,3+4
- H.d+1+2,P
- WALL.b,b,u/b
- WAR.f,F+2
- WAR.f,F+3
- WAR.f,f,F+1+2
- WAR.f,n,d,DF+4
- WR.f,f,F
- b+1,2~1+2,u
- b,4
- b,B+1+2
- b,B+3+4
- b,f+2
- b,f+2,1
- b,f+2,2
- b,f+2,3
- d+1,D
- d,1
- d,2
- d,4
- d,4,4
- d,d/b,d,d/b+1+2
- d,d/f
- d,d/f,1
- d,d/f,1,d/f
- d,d/f,d/f
- d,d/f,d/f,1
- f+2~1+2,u
- f,F+1+2
- f,F+2
- f,F+3
- f,f,F
- f,f,F+1+2
- f,f,F+3
- f,f,f+3
- f,f,n,2,1,2,2,3,4,4,1,2,1
- f,n,d,D/F
- f,n,d,D/F+3
- f,n,d,D/F+4,4
- f,n,d,D/F+4,4,1
- f,n,d,D/F+4,4,4
- f,n,d,D/F+4,4,4,1
- f,n,d,DF+4
- f,n,d,DF+4,4
- f,n,d,DF+4,4,4
- f,n,d,DF+4,4,4,1
- f,n,d,DF+4,4,4,3
- f,n,d,DF+4,4,4,n+4
- f,n,d,DF+4,4,4,n+4,4
- f,n,d,d/f+1
- f,n,d,d/f+2
- f,n,d,d/f+3
- f,n,d,d/f+4
- f,n,d,d/f+4,1
- f,n,d,d/f+4,n,4
- f,n,d,d/f+4,n,4,4
- f,n,d,d/f:1
- f,n,d,d/f:2
- f,n,d,df
- f,n,d,df#1
- f,n,d,df#2
- f,n,d,df+1
- f,n,d,df+2
- f,n,d,df+3
- f,n,d,df,UF
- f,n,d/f:1
- f,n,df#1
- n,d,d/b+1+3
- n,d/f,n,d/f+1
- n,f,n,f+1+2
- n,f,n,f+1+2,1

## Tests (file evidence only — NOT play-verified)

Minimal-tree node --test: 45 pass / 0 fail (Batches 1–3 cumulative + 10 Batch 4,
with the B4 count assertions: 217 total, 42 Batch 4 keys, 13 verified-last-step keys).
node --check fighter.js OK. Formatter round-trips the Batch 3 branch file
byte-identically; all non-plan keys identical, all 175 Batches 1–3 plans deep-equal.
Full 200-test suite comparison NOT run — no full current-main checkout on this box;
CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1115 + this PR merge +
deploy + sync, phone portrait)

- 2,1,2,2,3: steps grounded, rows 157/158/159/160/161, all standing.
- 2,1,2,2,3,4,4,1,2,1: steps 157/158/159/160/161, step 4 review (NO row — row 162
  must NOT play), step 4 row 163, step 1 row 164, step 2 row 165, last step 1 NO row.
- f+1+2,b+2,4: step 1 row 223, steps b+2/4 NO row (rows 207/214 held, must NOT play).
- u/f+4,3,1: jump steps rows 86/150, last step 1 NO row (row 152 must NOT play).
- 1,2,4 and 1,b+2,4: NO row any step (stale row 46 must NOT play).
- d/f+3,2,2,4,4,1,2,1,2,1: step 1 NO row (jump row 181 must NOT play), steps
  226/227/228, step 4 review (NO row — row 229 must NOT play), steps 230/235/236/237,
  last step 1 NO row (row 239 must NOT play).
- No step plays row 35 (does not exist in this bank) or row 220 unless genuinely
  airborne per heihachi_on_jin profiles.
- Rest keys unchanged — donor clips, NOT per plan, since rest keys get no plan.
- Diablo Batches 1–3 spot-checks undisturbed (2,1 family 157/158, b+1+2,2 98/99,
  d/f+1+2,2 110/204, u+1,1 step 2 row 40 jump-only, 1,1 step 1 still suspended;
  Batch 2: u/f+4,3 86/150, u/f+4,4 86/195, 3,4 step 1 row 153, d/f+4,4 step 1 row 183,
  d/f+4,4,4 steps 183 / NO row / NO row with review 191 held; Batch 3: d/f+4,2
  verified-all 183/225, 3,2 step 1 row 153, d/f+3,2 step 2 row 226, d/f+3,2,2 steps
  226/227, df+4,2 step 2 row 225, jump lasts 59/74/61/76/60/75).
