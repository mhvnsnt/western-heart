# SCIMITAR BATCH 3 — MIXED-PAIR STEP PLANS (2026-10-25)

Stack: #1096 engine → scimitar Batch 1 (PR #1125) → scimitar Batch 2 (PR #1126)
→ this Batch 3. This PR merges AFTER #1126 (after #1125, after #1096, itself
blocked on 12 pre-existing failures / a gate decision owed — this lane fixes
neither and merges nothing itself). It does not touch fighter.js, pantera.json,
burger.json, demonio.json, diablo.json, kinpo.json, or phantom.json. No T8
content touched.

## Universe (measured first, never assumed)

- **11 canonicals, ALL pure single-button, 0 chord-involved; ALL 11 planned
  (strike), 0 CSV-only.** 23 CSV rows (11 + 12 variants) → **23 plan keys**.
- Pair split: {LP1,RK4} 4, {RP2,RK4} 3, {LP1,LK3} 2, {RP2,LK3} 2.
- Contexts: standing 6, crouch 5, jump 0, ws 0.
- Provenance: 8 main moves, 3 quarantined-only (FC.df+4,1; SNK.df+1,3; df+4,1 —
  live when #988 merges), 0 Batch 2-branch-only.
- Overlap vs Batches 1–2 universe/plans: [].
- Canonicals: 2,3; 4,1; FC.df+4,1; R.d/b+2,4; SNK.df+1,3; d/f+1,3; d/f+1,4;
  df+4,1; f+2,3; f+2,4; f+2,4,4.
- Variants (12): 2,3~t7.shaheen, 2,3~t7.shaheen.2; 4,1~t7.shaheen,
  4,1~t7.shaheen.2; R.d/b+2,4~t7.shaheen; f+2,3~t7.shaheen, f+2,3~t7.shaheen.2;
  f+2,4~t7.shaheen, f+2,4~t7.shaheen.2; f+2,4,4~t7.shaheen, f+2,4,4~t7.shaheen.2,
  f+2,4,4~t7.shaheen.3.

## Bank — JIN, FALLBACK (re-verified four-way, not re-assumed)

scimitar.json t3_source 'jin', t3_bank 'moveset_jin.json' on BOTH the Batch 2
branch and main; t3/ has jin dir, NO shaheen dir; Job 1 jin 220 rows; Job 2
scimitar entries ALL bank jin (362); Job 4 jin candidates 47. Pack dir = bank
name (no diablo-style split). Scimitar's T7/T8 base is Shaheen (tekken_base
Shaheen, merge_sources t8/t7 shaheen); Shaheen debuted in Tekken 7 — the kinpo
pattern (Asuka → jin), not phantom's native bank.

Gap-1: jin hit_frames 54b38e63… + skeleton 26f72eb7… IDENTICAL on the Batch 2
branch and main; main rows.pack 7bafa36a… (226 rows) = Batch 2 branch
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

Drift census (both ways, identical to Batches 1–2 — no new main drift):
220 same / 84 damage-only / 57 anim_ref-changed / 1 ROW-CHANGED (1: 184→None).
Damage differs on 116 (84 damage-only + 32 gap). Damage-only drift does NOT
suspend.

## Steps: 23, all planned: 1 verified / 1 review / 21 unmapped

- **Verified (1):** 2,3 step 1 ← row 220 (standing RP2, prefix-move,
  damage-only drift; hit_frames [12,12,41,1042,0,2]; SOFT window [4.0,8.0]
  armR peak 6 — passes). Row 220 verified present in the current main jin pack
  at wire time. No step carries a soft flag. No GATE-NOTE arises (the verified
  step is standing-context on a standing row).
- **Review (1):** 4,1 step 1 — candidate row 199 SOFT fail (window [3.5,7.5],
  legR peak 3 — same row/result as kinpo Batch 3's 4,1 hold and scimitar
  Batch 2's 4,3/4,4 holds, independently re-derived).
- **Rejected-candidate (4):** d/f+1,3 step 1 row 179 airborne (stance jump;
  y0 0.943 ymax 1.519 vs standingY 1.027); d/f+1,3 step 2 row 197 airborne
  (recorded-dest; y0 0.943 ymax 1.525); d/f+1,4 step 1 row 179 airborne;
  d/f+1,4 step 2 row 204 airborne (recorded-dest; y0 0.943 ymax 1.531). Same rows
  as kinpo Batch 3's d/f+1,3 / d/f+1,4 rejections, independently re-derived.
- **No-candidate (17):** 2,3 step 2; 4,1 step 2; FC.df+4,1 steps 1–2; R.d/b+2,4
  steps 1–2; SNK.df+1,3 steps 1–2; df+4,1 steps 1–2; f+2,3 steps 1–2; f+2,4
  steps 1–2; f+2,4,4 steps 1–3. Their prefixes are T8-sourced with no T3 row;
  correct clips come from #988 Step 2 (original T8 refs) or future extraction,
  never from a T3 row recorded as correct.
- **Suspended-drift (0):** the file's ONLY row-changed move (1, 184→None) is NOT
  a Batch 3 step prefix — no Batch 3 string starts with plain 1; step prefixes
  are 2, 4, FC.df+4, R.d/b+2, SNK.df+1, d/f+1, df+4, f+2 and their extensions.
  Stated explicitly after re-checking.
- Canonical status: 2 partial (2,3; 4,1) / 9 unmapped-all / 0 verified-all /
  0 review-only. Plan-key last-step: 0 verified / 0 review / 23 unmapped.
- Donor rows documented, never wired: 195 (standing LK3, whole-string donor
  for 2,3 / SNK.df+1,3 / f+2,3), 199 (standing RK4, whole-string donor for
  R.d/b+2,4 / f+2,4 / f+2,4,4 — and the held review candidate for 4,1 step 1),
  184 (HARD string-ender-on-chord donor for 4,1 / FC.df+4,1 / df+4,1).

## Job 3: 0 fills wired, 1 report entry

- 4,1 step 2: rows 92/105 exact ROW-ONLY (target 4,1) — documented, NOT wired
  (ROW-ONLY provenance never wires under the stricter fill rule).
- No agreement note fires (no exact+FULL Job 3 candidate exists for any
  verified step). Dedupe fires zero times (no Batch 3 step prefix has a __main
  Job 3 target at all). No SOFT fill inherited from #1097.

## Job 4 (corrected join only): 4 joins, none promoting

- d/f+1,3 step 1 row 179 REJECTED (airborne); d/f+1,3 step 2 row 197 REJECTED
  (airborne); d/f+1,4 step 1 row 179 REJECTED (airborne); d/f+1,4 step 2
  row 204 REJECTED (airborne). A join never promotes by itself.
- Orphans: 15 (85, 91, 99, 100, 104, 127, 170, 171, 172, 209, 226, 239, 250,
  256, 262 — same bank-level set as Batches 1–2).

## Canonicalization / filing

- ZERO input-~ canonicals in Batch 3 scope; scimitar INERT file-wide
  (old == corrected for all 114 comma keys — Batch 3 checked its own scope,
  did not copy Batches 1–2's claim). __main canonicals: 0. Corrupted keys: 0.
- Spelling quirks kept distinct: d/f+1,4 (step-1 candidate row 179
  airborne-rejected) vs df+4,1 (quarantined-only, no candidate) — distinct
  canonicals with different step-1 evidence; d/f+1,3 vs d/f+1,4 share the
  d/f+1 prefix (row 179 airborne-rejected) but are distinct canonicals.
  WS-context fix applied (no wiring change; Batch 3 has no ws-context
  canonicals).

## Tests

Minimal-tree `node --test`: **34/34 pass** (11 Batch 1 cumulative + 12 Batch 2
cumulative + 11 Batch 3); `node --check fighter.js` OK. Formatter round-trips
the Batch 2 branch file byte-identically; all non-plan keys identical; all 39
Batches 1–2 plans deep-equal; Batches 1–2 content assertions preserved verbatim
(diff-verified: Batch 1 test changes ONLY header note, B3 const, count 39→62,
extra-keys assertion; Batch 2 test changes ONLY header note, B3 const, count
39→62, extra-keys assertion). **Limitation:** full 200-test suite comparison
NOT run — no full current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + #1125 + #1126 + this PR merge + deploy + sync, phone portrait)

- 2,3 [220, NO row] — grounded standing RP2 first step; step 2 NO row.
- 4,1: NO row any step (review row 199 held, must NOT play; Job 3 rows 92/105
  must NOT play as whole-string clips).
- d/f+1,3 / d/f+1,4: NO row any step (airborne rows 179/197/204 must NOT play).
- FC.df+4,1 / R.d/b+2,4 / SNK.df+1,3 / df+4,1 / f+2,3 / f+2,4 / f+2,4,4:
  NO row any step (donor rows 195/199/184 must NOT appear as whole-string clips).
- No step plays a jin airborne/jump row (35/216/41) for a ground step. No step
  plays a row from another bank.
- Batches 1–2 spot-checks undisturbed (2,1 [220,221], 2,1,2,2 [220,221,222,223],
  d+1+2,2 [92,93], 1,2 [NO row,186], d+1+2,1 [92,NO row]; u/f+4,3 [80,193],
  u/f+4,4 [80,207], d/f+4,4 [205,NO row], 4,3/4,4 NO row).
- Quarantined-only strings behave per plan ONLY after #988 merges (Batch 3:
  FC.df+4,1; SNK.df+1,3; df+4,1).
- **No play verification is claimed** — tests + file evidence only; playing is
  the parent's step after merge + deploy.
