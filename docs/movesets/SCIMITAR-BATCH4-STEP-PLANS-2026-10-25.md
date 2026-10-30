# SCIMITAR BATCH 4 — TRIPLES/QUADS/REST STEP PLANS (2026-10-25)

Stack: #1096 engine → scimitar Batch 1 (PR #1125) → scimitar Batch 2
(PR #1126) → scimitar Batch 3 (PR #1127) → this Batch 4, the LAST scimitar
batch. This PR merges AFTER #1127 (after #1126, after #1125, after #1096,
itself blocked on 12 pre-existing failures / a gate decision owed — this lane
fixes neither and merges nothing itself). It does not touch fighter.js,
pantera.json, burger.json, demonio.json, diablo.json, kinpo.json, or
phantom.json. No T8 content touched.

## Universe (measured first, never assumed)

- **37 canonicals = 10 triples/quads + 27 rest.** 49 CSV rows (37 + 12
  variants) → **16 plan keys** (10 planned canonicals + 6 variants: 1,2,3 ×3
  twins, 1,2,4 ×3 twins).
- Triples/quads (all steps buttoned, union 3–4): 1,2,3; 1,2,4; 2,1,2,2,3;
  2,1,2,2,3,4; 2,1,4; 2,1,4,1,3,3,3,3+4,4; 2,1,4,4; 2,1,4,4,2; 2,1,4,4,2,4;
  df+4,1,3. 9 pure single-button + 1 chord-involved (2,1,4,1,3,3,3,3+4,4
  carries a 3+4 chord step). ALL 10 planned (strike); 0 throw/grapple
  triples/quads (no Batch 4 triple/quad carries a {PILE_DRIVER, ARM_BREAKER,
  TACKLE} grapple label under the narrow label rule — stances are NOT
  grapples).
- Rest (≥1 buttonless step, CSV-audited only, never planned — planning them
  needs engine support for non-attack prefix steps, future work, named, not
  guessed): (back to wall).b,b,UB; 1,2,3,D/F; 3,D/F; D*,u+2; FC.d/f,d,D/F+3;
  FC.df,d,DF; FC.df,d,DF+3; H.D*,u+2; R.d/b+2,4,D/F; WALL.b,b,u/b; b+1,D;
  d+3,D/F; d,d/b,d,d/b+1+2; d/b+2,D/F; d/b,n,f+2; d/f,D/F; f+2,4,D/F; f+3+4,D/F;
  f,F+3; f,F+4; f,b+2; f,f,F; f,f,F+2; f,f,f+2; n,b,n,f+2; n,d/f,n,d/f+1;
  uf,n,4. Rest variants (6): f,b+2~t7.shaheen; f,F+3~t7.shaheen,
  f,F+3~t7.shaheen.2; 1,2,3,D/F~t7.shaheen, 1,2,3,D/F~t7.shaheen.2;
  f+2,4,D/F~t7.shaheen. Note: d,d/b,d,d/b+1+2, d/b,n,f+2, n,d/f,n,d/f+1 carry
  throw-class own moves in the CSV — they are rest keys, CSV-only regardless.
- Contexts: standing 27, crouch 9, jump 1 (uf,n,4, rest).
- Provenance: 31 main moves, 6 quarantined-only (live when #988 merges:
  (back to wall).b,b,UB; D*,u+2; FC.df,d,DF; H.D*,u+2; df+4,1,3; uf,n,4),
  0 Batch 3-branch-only.
- Overlap vs Batches 1–3 universe/plans: [].

## Bank — JIN, FALLBACK (re-verified four-way, not re-assumed)

scimitar.json t3_source 'jin', t3_bank 'moveset_jin.json' on BOTH the Batch 3
branch and main; t3/ has jin dir, NO shaheen dir; Job 1 jin 220 rows; Job 2
scimitar entries ALL bank jin (362); Job 4 jin candidates 47. Pack dir = bank
name (no diablo-style split). Scimitar's T7/T8 base is Shaheen (tekken_base
Shaheen, merge_sources t8/t7 shaheen); Shaheen debuted in Tekken 7 — the kinpo
pattern (Asuka → jin), not phantom's native bank.

Gap-1: jin hit_frames 54b38e63… + skeleton 26f72eb7… IDENTICAL on the Batch 3
branch and main; main rows.pack 7bafa36a… (226 rows) = Batch 3 branch
141fbc8d… (220 rows) + exactly the 6 #1109 bake jin rows (89/112/247/288/339/357),
SUPERSET, 0 removed. Main bank blobs identical to Batch 1's main baseline — no
phantom-Batch-4-style re-bake signature change. No gate decision changes, no
fill suspended on bank drift.

Jin row identities (per-bank evidence, re-derived here): row 35 EXISTS,
starts-airborne LP1 ([11,12,39,535,0,1], ground-rejected); row 220 STANDING RP2
([12,12,41,1042,0,2], NOT king's jumping chord row / bryan's button-0 row /
heihachi's jump RK4 row); row 216 JUMP row ([63,64,117,1543,0,0], button 0,
fails every single-button gate); row 41 starts-airborne LP1; duck-dip rows (16):
123, 189, 192, 210, 211, 212, 213, 235, 257, 367, 377, 381, 385, 387, 389, 397.

Scimitar basics: LP1 move 1 carries t3_row 184 on #1096 (hit_frames
[12,13,64,799,0,9], button 9 = LP1+RK4 chord) and IS row-changed on main
(184→None, anim_ref None) — the file's ONLY row-changed move; RP2 move 2 carries
t3_row 220 both files (damage-only drift 4→10, NOT suspending).

Drift census (both ways, identical to Batches 1–3 — no new main drift):
220 same / 84 damage-only / 57 anim_ref-changed / 1 ROW-CHANGED (1: 184→None).
Damage differs on 116 (84 damage-only + 32 gap). Damage-only drift does NOT
suspend.

## Steps: 121 total = 47 planned + 74 CSV-only; planned: 30 verified / 1 review / 16 unmapped

- **Verified (30):** 2,1,2,2,3 [220,221,222,223,224] verified-all; 2,1,4
  [220,221,230] verified-all; 1,2,3 step 2 ← 186 (standing RP2) and 1,2,4 step 2
  ← 186 (same row, per-step gate-checked — row dual-role caution: a row
  verified for one string/context is NOT globally verified); 2,1,4,1,3,3,3,3+4,4
  steps 1–3 ← 220/221/230; 2,1,4,4 steps 1–3 ← 220/221/230; 2,1,4,4,2 steps 1–3
  ← 220/221/230 + step 5 ← 232 (standing RP2, Job 2 own row, hit_frames
  [23,23,68,271,0,2]); 2,1,4,4,2,4 steps 1–3 ← 220/221/230 + steps 5–6 ← 232/233
  (233 standing RK4, hit_frames [16,17,51,535,0,8]); 2,1,2,2,3,4 steps 1–5 ←
  220/221/222/223/224. All verified rows present in the current main jin pack
  (226 rows) at wire time: 186, 220, 221, 222, 223, 224, 230, 232, 233. No step
  carries a soft flag. No GATE-NOTE arises (zero crouch planned strings
  verified on standing rows; the only crouch planned string, df+4,1,3, is
  unmapped-all). No SOFT waiver arises (no jump planned strings; the sole jump
  canonical, uf,n,4, is rest).
- **Review (1):** 2,1,2,2,3,4 step 6 — candidate row 225 SOFT fail (window
  [16.5,21.5], legR peak 6 — same row/result as kinpo Batch 4's 2,1,2,2,3,4
  hold, independently re-derived). Proxy-fail = review, never false verify.
- **Rejected-candidate (3):** 2,1,4,4 step 4, 2,1,4,4,2 step 4, 2,1,4,4,2,4
  step 4 — row 231, button 12 != step bits 8 (same row/result as demonio
  Batch 4's and kinpo Batch 4's 2,1,4,4 step-4 failures, independently
  re-derived).
- **Suspended-drift (2):** 1,2,3 step 1 and 1,2,4 step 1 — prefix move 1 is the
  file's ONLY row-changed move (184→None); stale row 184 documented, never
  wired. (Row 184 would fail the LP1 button gate regardless, button 9 !=
  bits 1 — but the suspension reason is the drift, stated as such.) This is
  the check that mattered in Batch 4: Batch 2's strings were LK3/RK4-only and
  Batch 3's never started with plain 1, but Batch 4 strings CAN contain LP1 —
  and two do, as step 1.
- **No-candidate (11):** 1,2,3 step 3; 1,2,4 step 3; 2,1,4,1,3,3,3,3+4,4 steps
  4–9 (6); df+4,1,3 steps 1–3 (3). Their prefixes are T8-sourced with no T3
  row; correct clips come from #988 Step 2 (original T8 refs) or future
  extraction, never from a T3 row recorded as correct.
- Canonical status (planned): 2 verified-all (2,1,2,2,3; 2,1,4) / 7 partial /
  1 unmapped-all (df+4,1,3) / 0 review-only. Plan-key last-step: 4 verified /
  1 review / 11 unmapped.
- CSV-only steps (74): all 27 rest keys' steps, audited in the CSV, no plan.

## Job 3: 0 fills wired, 6 report entries

- 1,2,3 step 1 and 1,2,4 step 1: rows 92/105 exact ROW-ONLY (target 1) —
  documented, NOT wired (ROW-ONLY provenance never wires under the stricter
  fill rule; both steps are suspended-drift anyway).
- 1,2,3,D/F step 1 (rest key): rows 92/105 exact ROW-ONLY — rest-key step,
  never fill-eligible.
- d/b+2,D/F step d/b+2 (rest key): rows 108/122 soft-filed ROW-ONLY —
  rest-key step, never fill-eligible.
- f+3+4,D/F step f+3+4 (rest key): rows 101/116/131/132 soft-nofiled,
  including FULL rows with demonio provenance — cross-fighter provenance,
  never wired; rest-key step anyway.
- No agreement note fires (the note fires ONLY for actually-wired gate
  candidates). Dedupe fires zero times. No SOFT fill inherited from #1097.
  No exact+FULL Job 3 candidate exists for any verified step.

## Job 4 (corrected join only): 3 joins, none promoting

- 2,1,4,4,2 step 2 row 232 joined — no action, step already verified.
- 2,1,4,4,2,4 step 2 row 232 joined — no action, step already verified.
- b+1,D step b+1 row 216 joined — rest key, join NOT adjudicated (row 216 is
  the jin JUMP row; it is never wired for a ground step). A join never
  promotes by itself.
- Orphans: 15 (85, 91, 99, 100, 104, 127, 170, 171, 172, 209, 226, 239, 250,
  256, 262 — same bank-level set as Batches 1–3).

## Canonicalization / filing

- ZERO input-~ canonicals in Batch 4 scope; scimitar INERT file-wide
  (old == corrected for all 114 comma keys — Batch 4 checked its own scope,
  did not copy Batches 1–3's claim). __main canonicals: 0. Corrupted keys: 0.
- Spelling quirks kept distinct (Batch 1–3 precedent applied; no new Batch 4
  spelling pair required adjudication beyond the filed keys).
- WS-context fix applied (no wiring change; Batch 4 has no ws-context
  canonicals — the ws-context keys in scope are rest keys, CSV-only).

## Tests

Minimal-tree `node --test`: **47/47 pass** (11 Batch 1 cumulative + 12 Batch 2
cumulative + 11 Batch 3 cumulative + 13 Batch 4); `node --check fighter.js` OK. Formatter round-trips
the Batch 3 branch file byte-identically; all non-plan keys identical; all 62
Batches 1–3 plans deep-equal; Batches 1–3 content assertions preserved verbatim
(diff-verified: each earlier test file changes ONLY header note, B4 const,
count 62→78, rule-2 count line, extra-keys assertion). **Limitation:** full
200-test suite comparison NOT run — no full current-main checkout on this box;
CI must cover before merge.

## COVERAGE-COMPLETE PROOF

Total canonical comma keys in the Batch 3 base file: **74 = B1 14 + B2 12 +
B3 11 + B4 37**, pairwise overlaps 0, uncovered [] extra []. Plan keys total:
**78 = 21 + 18 + 23 + 16**. CSV-only count: **30 canonicals** (3 Batch 1
TACKLE-family keys + 27 Batch 4 rest keys; Batches 2–3 had 0 CSV-only).
Every scimitar canonical is planned or CSV-audited. Scimitar string coverage
is COMPLETE.

Running tally: 74 canonicals / 78 plan keys (B1: 14/21; B2: 12/18; B3: 11/23;
B4: 37/16).

## Play-verify checklist (parent browser delegation, after #1096 + #1125 + #1126 + #1127 + this PR merge + deploy + sync, phone portrait)

- 2,1,2,2,3 [220,221,222,223,224] — all five steps grounded, no jumping row.
- 2,1,4 [220,221,230] — all three steps grounded.
- 1,2,3 / 1,2,4 — step 1 NO row (suspended-drift; stale row 184 must NOT
  play); step 2 row 186 grounded RP2; step 3 NO row.
- 2,1,2,2,3,4 — steps 1–5 grounded [220,221,222,223,224]; step 6 NO row
  (review row 225 held, must NOT play).
- 2,1,4,1,3,3,3,3+4,4 — steps 1–3 grounded [220,221,230]; steps 4–9 NO row.
- 2,1,4,4 — steps 1–3 grounded [220,221,230]; step 4 NO row (row 231 button
  mismatch must NOT play).
- 2,1,4,4,2 — steps 1–3 grounded [220,221,230]; step 4 NO row; step 5 row 232
  grounded RP2.
- 2,1,4,4,2,4 — steps 1–3 grounded [220,221,230]; step 4 NO row; steps 5–6
  rows 232/233 grounded.
- df+4,1,3 — NO row any step (quarantined-only; behaves per plan ONLY after
  #988 merges).
- Rest keys unchanged — donor clips, NOT per plan, since rest keys get no
  plan (incl. b+1,D: jump row 216 must NOT play for a ground step).
- No step plays a jin airborne/jump row (35/216/41) for a ground step. No step
  plays a row from another bank.
- Batches 1–3 spot-checks undisturbed (2,1 [220,221], 2,1,2,2 [220,221,222,223],
  d+1+2,2 [92,93], 1,2 [NO row,186], d+1+2,1 [92,NO row]; u/f+4,3 [80,193],
  u/f+4,4 [80,207], d/f+4,4 [205,NO row], 4,3/4,4 NO row; 2,3 [220,NO row],
  4,1 [review,NO row], d/f+1,3 / d/f+1,4 NO row).
- Quarantined-only strings behave per plan ONLY after #988 merges (Batch 4:
  df+4,1,3 planned; rest keys (back to wall).b,b,UB; D*,u+2; FC.df,d,DF;
  H.D*,u+2; uf,n,4 CSV-only).
- **No play verification is claimed** — tests + file evidence only; playing is
  the parent's step after merge + deploy.
