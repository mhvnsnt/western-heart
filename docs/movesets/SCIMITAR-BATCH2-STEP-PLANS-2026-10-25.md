# SCIMITAR BATCH 2 STEP PLANS — LK3/RK4-only strings (2026-10-25)

Stack: branch from the Scimitar Batch 1 branch (`feat/scimitar-batch1-step-plans-20261025`,
PR #1125, head re-verified `a96e53833338f369bb5d66c8df292dfdda1194ad`), which is stacked on
#1096 (`feat/batch1-step-plans-pantera-20261024`, the step-playback engine). This PR merges
AFTER #1125 (after #1096, itself blocked on 12 pre-existing failures / a gate decision owed —
this lane fixes neither and merges nothing itself; merge only when clean + green, never on
mergeable:true alone). Touches nothing else: no fighter.js, pantera.json, burger.json,
demonio.json, diablo.json, kinpo.json, phantom.json. No T8 content touched.

## Method (identical pipeline, scimitar Batch 1 + phantom Batches 1–4 + kinpo Batches 1–4 precedent)

Universe measured first (never assumed). Step table: one verified row per prefix step.
Exact-signature equality for candidate matching. Jumping rows rejected for ground steps.
Current playable bank is T3 rows — T3-row matches are FALLBACK matches logged in
docs/anim/PROCEDURAL_AUDIT.md, never recorded as the correct mapping, to be re-matched to
T7 Shaheen rows when decode lands. Donor retirement is DESIGNED: wiring plans replaces
single-row resolution wholesale, even for CLEAN donors, because one row cannot be correct
for a multi-hit string. GATE NOTE (demonio Batch 1 edge): the gate flags crouch rows for
non-crouch steps, not standing rows for crouch steps. ROW DUAL-ROLE CAUTION (Pantera
Batch 4): a row verified for one string/context is NOT globally verified — every step
gate-checks its own row again. Job 3 fills require exact level + FULL provenance + HARD
gates + SOFT proxy (burger refinement, stricter than Pantera Batch 4's HARD-only fill rule).
Job 4 joins use the CORRECTED join only (scimitar-only, BANK_DIR jin, join iff Job 2 entry
key == step prefix, row == candidate row, step == own); a join NEVER promotes by itself.
SOFT candidates are documented, NEVER wired; no SOFT fill is inherited from #1097
(Pantera-specific, still unapproved, does not transfer to scimitar).

## Bank — JIN, FALLBACK (four-way file evidence, re-verified, not assumed)

- scimitar.json `t3_source` 'jin', `t3_bank` 'moveset_jin.json' on BOTH the Batch 1 branch
  (blob ee9fab63…) and main (blob 64b707f4…); t3/ on main has a `jin` dir (hit_frames +
  rows.pack + skeleton) and NO `shaheen` dir; Job 1 bank jin (220 rows); Job 2 scimitar
  entries ALL bank jin (362); Job 4 jin candidates (47). Scimitar's T7/T8 base is Shaheen
  (tekken_base Shaheen, merge_sources t8/t7 shaheen), Shaheen debuted in Tekken 7 — the
  kinpo pattern (Asuka → jin), not phantom's native bank. Pack dir = bank name (no
  diablo-style split).
- Gap-1 (replicated): jin hit_frames 54b38e63… IDENTICAL + skeleton 26f72eb7… IDENTICAL on
  the Batch 1 branch and current main; main rows.pack 7bafa36a… (226 rows) = Batch 1 branch
  rows.pack 141fbc8d… (220 rows) + exactly the 6 #1109 bake jin rows
  (89/112/247/288/339/357), SUPERSET, 0 removed (same as kinpo Batch 1 and scimitar
  Batch 1). Main bank blobs are identical to scimitar Batch 1's main baseline — no
  phantom-Batch-4-style re-bake signature change. No gate decision changes, no fill
  suspended on bank drift.
- Jin row identities (per-bank evidence, re-derived here — same bank demonio/kinpo
  adjudicated independently):
  - Row 35 EXISTS: hit_frames [11,12,39,535,0,1]; Job 1 starts-airborne (y0 1.769 vs
    standingY 1.027, armL, level m) — ground-rejected, jump-context only.
  - Row 220 is a STANDING RP2 row: hit_frames [12,12,41,1042,0,2]; Job 1 standing (armR,
    level h) — NOT king's jumping chord row, NOT bryan's button-0 row, NOT heihachi's
    jump RK4 row.
  - Row 216 is a JUMP row: hit_frames [63,64,117,1543,0,0]; Job 1 jump, button 0, level u
    — fails every single-button gate.
  - Row 41 is a starts-airborne LP1 row: hit_frames [7,7,35,535,0,1]; Job 1
    starts-airborne (y0 1.695) — ground-rejected, jump-context only.
  - Jin duck-dip rows (16): 123, 189, 192, 210, 211, 212, 213, 235, 257, 367, 377, 381,
    385, 387, 389, 397 — handled like crouch: STANCE-SOFT (review) for non-crouch contexts.
- Scimitar's own basics (Batch 1, from file evidence): LP1 move `1` carries t3_row 184 on
  the Batch 1 branch (standing LP1 row; hit_frames [12,13,64,799,0,9], button 9 = LP1+RK4
  chord) and IS row-changed on main (184→None, anim_ref None) — the file's ONLY
  row-changed move; RP2 move `2` carries t3_row 220 both files (damage-only drift 4→10,
  NOT suspending). Move `1` is an LP1 move, so it is NOT a Batch 2 step prefix (Batch 2
  strings are LK3/RK4-only) — Batch 2 has ZERO suspended-drift steps.

## Universe (measured first, never assumed)

- **12 canonicals: 12 pure + 0 chord-involved. ALL 12 planned (strike), 0 CSV-only.**
  6 variants → **18 CSV rows = 18 plan keys.**
- Contexts: standing 2 (4,3; 4,4), crouch 4 (d/b+3,4; d/f+4,4; db+3,4; df+4,3), jump 4
  (u/f+4,3; u/f+4,4; u/f+4,4,4; u/f+4,4,4,4), ws 2 (WS.3,3; ws3,3).
- Provenance: 11 main moves, 1 quarantined-only (df+4,3 — live when #988 merges),
  0 Batch 1-branch-only. Baseline: main moves 329 + quarantine 33 = 362 = Batch 1 branch
  moves; strings lists identical (50/50); 0 main-only moves.
- Overlap vs Batch 1 universe/plans: [] (Batch 1 was LP1/RP2-only; Batch 2 is LK3/RK4-only).
- Variants: 4,3 → 4,3~t7.shaheen, 4,3~t7.shaheen.2; 4,4 → 4,4~t7.shaheen,
  4,4~t7.shaheen.2; WS.3,3 → WS.3,3~t7.shaheen; d/b+3,4 → d/b+3,4~t7.shaheen.
- Scimitar Batch 2 is ALL-pure, like demonio Batch 2 (17 pure, 0 chord) and diablo
  Batch 2 (all pure) — a measured property, not an assumption.

## Steps: 27 = 9 verified / 6 review / 12 unmapped (12 no-candidate + 0 rejected + 0 suspended)

Canonical status (planned): 2 verified-all / 5 partial / 5 unmapped-all / 0 review-only.
Plan-key last-step: 2 verified / 3 review / 13 unmapped.

### Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK; all 4 rows present in the current main jin pack; SOFT waived for jump context, SOFT passes outright for the crouch step)

- u/f+4,3 verified-all [80, 193] — jump context, SOFT waived. Row 80: jump RK4,
  hf [25,25,66,535,0,8], Job 1 jump, legR, level m. Row 193: jump LK3,
  hf [35,37,65,535,0,4], Job 1 jump, legL, level m.
- u/f+4,4 verified-all [80, 207] — jump context, SOFT waived. Row 207: jump RK4,
  hf [47,47,86,271,0,8], Job 1 jump, legR, level l.
- u/f+4,4,4 steps 1–2 ← 80/207 (verified); u/f+4,4,4,4 steps 1–2 ← 80/207 (verified) —
  same rows, same evidence, own step prefixes.
- d/f+4,4 step 1 ← 205 (verified) — crouch row for crouch context, passes outright
  (no GATE-NOTE: this is a crouch row for a crouch step, not standing-for-crouch).
  Row 205: hf [16,16,62,271,0,8], Job 1 crouch, legR, level l; SOFT window [6,10],
  legR peak 8 — passes outright.
- No GATE-NOTE arises in Batch 2 (zero crouch planned steps verified on standing rows).
- No step carries a soft flag. No Job 3 fill is wired (see below).
- Cross-batch consistency (same jin bank, independently re-derived, not copied):
  the u/f+4 family (80/193/207/210/211) matches demonio Batch 2 and kinpo Batch 2
  row-for-row; d/f+4,4 [205, review-212] matches demonio Batch 2 and kinpo Batch 2;
  the 4,3/4,4 step-1 candidate 199 SOFT fail ([3.5,7.5], legR peak 3) matches kinpo
  Batch 3's 4,1 hold exactly.

### Review holds (6, row null, NOT wired)

- 4,3 step 1 + 4,4 step 1 — candidate row 199 (standing RK4, hf [11,11,49,535,0,8],
  Job 1 standing, legR, level m): SOFT limb-peak proxy fail, window [3.5,7.5],
  legR peak 3 (just outside the window).
- d/f+4,4 step 2 — candidate row 212 (recorded-dest; also the whole-string own row):
  duck-dip RK4, hf [13,13,70,271,0,8], Job 1 duck-dip, legR, level l: SOFT fail,
  window [4.5,8.5], legR peak 12 (outside the window).
- u/f+4,4,4 step 3 — candidate row 210 (recorded-dest; also the whole-string own row):
  duck-dip RK4, hf [24,24,70,271,0,8]: STANCE-SOFT (duck-dip row for jump-context step).
- u/f+4,4,4,4 steps 3–4 — candidate rows 210 (prefix-move) / 211 (recorded-dest; also
  the whole-string own row): STANCE-SOFT (duck-dip rows for jump-context steps).
  Row 211: hf [22,22,70,535,0,8], Job 1 duck-dip, legR, level m.

### Unmapped (12, ALL no-candidate — zero rejected-candidate, zero suspended-drift)

- 4,3 step 2 + 4,4 step 2 — prefixes 4,3 / 4,4 are T8-sourced, no T3 row in either file.
- WS.3,3 steps 1–2 + ws3,3 steps 1–2 — ws prefixes, no T3 row in either file.
- d/b+3,4 steps 1–2 + db+3,4 steps 1–2 + df+4,3 steps 1–2 — crouch prefixes, no T3 row
  in either file (df+4,3 is quarantined-only).
- Correct clips come from #988 Step 2 (original T8 refs) or future extraction — never
  from a T3 row recorded as correct.
- Donor rows documented, never wired: 195 (standing LK3, hf [19,23,61,535,0,4],
  whole-string donor for 4,3 / WS.3,3 / ws3,3 / df+4,3), 199 (standing RK4,
  whole-string donor for 4,4 / d/b+3,4 / db+3,4 — and the review candidate for the
  4,3/4,4 step 1s, held, never wired).

### Job 3: 0 fills wired, 0 report entries with pass-all rows (honestly empty)

- The only Batch 2 step prefixes with match_search entries — d/b+3,4, u/f+4,4,4,
  u/f+4,4,4,4 — all carry EMPTY pass-all lists in job3.log, so no candidates exist to
  report (kinpo Batch 2 precedent: honestly empty, not a lookup gap — verified by
  direct grep of match_search + job3.log).
- No agreement note fires (no exact+FULL Job 3 candidate exists for any verified step).
- Dedupe fires zero times: no Batch 2 step prefix has a pass-all row in either its
  plain or __main Job 3 target — in fact no Batch 2 step prefix has a __main Job 3
  target at all. No SOFT fill inherited from #1097.

### Job 4 (corrected join only): 4 joins, none promoting

- u/f+4,3 step 2 → row 193; u/f+4,4 step 2 → row 207; u/f+4,4,4 step 2 → row 207;
  u/f+4,4,4,4 step 2 → row 207 — all no-action (steps already verified). A join NEVER
  promotes by itself.
- Orphans (15): jin Job 4 candidates no scimitar Job 2 move carries (any step): 85, 91,
  99, 100, 104, 127, 170, 171, 172, 209, 226, 239, 250, 256, 262 — the same bank-level
  set as Batch 1 (orphans are batch-independent by construction).

## Drift census (both ways — identical to Batch 1, no new main drift)

Full census over all 362 Batch 1 branch moves: 220 same / 84 damage-only /
57 anim_ref-changed / 1 ROW-CHANGED (1: 184→None). Damage differs on 116 moves
(84 damage-only + 32 gap). Damage-only drift noted, NOT suspending (damage ≠ animation).
Step-prefix census: only move 1 is row-changed and it is NOT a Batch 2 step prefix
(0 suspended steps).

## Canonicalization / filing (corrected rule, demonio Batch 2)

- ZERO input-~ canonicals in Batch 2 scope. Scimitar is INERT file-wide on this axis:
  every ~ in the file is a trailing source-variant suffix (~t7.shaheen / ~t8.shaheen,
  with .2/.3), so old canonical == corrected canonical for all 114 comma keys — no
  input-~ canonical exists in ANY scimitar batch scope (contrast phantom Batch 4's 3
  input-~ canonicals). Batch 2 checked its own scope; it did not copy Batch 1's claim.
- __main canonicals in Batch 2 scope: 0. Corrupted keys in Batch 2 scope: 0.
- Spelling quirks kept distinct (never merged/smoothed): d/b+3,4 vs db+3,4 (both
  unmapped-all, different step-1 drift evidence: damage-only vs anim_ref-changed);
  WS.3,3 vs ws3,3 (both unmapped-all, WS-context spelling twins). WS-context fix
  applied (lowercase no-dot ws spellings are WS context, not standing — changes NO wiring;
  Batch 2 has 2 ws-context canonicals, both unmapped-all either way).

## Tests

Minimal-tree `node --test`: **23/23 pass** (11 Batch 1 cumulative + 12 Batch 2);
`node --check fighter.js` OK. Formatter round-trips the Batch 1 branch file
byte-identically. Structural diff: all non-plan keys identical, all 21 Batch 1 plans
deep-equal, Batch 1 law string preserved verbatim as a prefix, 18 new Batch 2 keys
appended (39 total). Batch 1 test cumulative update diff-verified: ONLY the header note,
the B2 const, the plan count (21→39), the rule-2 count line, and the extra-keys assertion
changed; every Batch 1 content assertion preserved verbatim. **Limitation (stated in PR
body):** full 200-test suite comparison NOT run — no full current-main checkout on this
box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + #1125 + this PR merge + deploy + sync, phone portrait)

- u/f+4,3 [80,193], u/f+4,4 [80,207] — jump context, airborne rows correct.
- u/f+4,4,4 [80,207,NO row], u/f+4,4,4,4 [80,207,NO row,NO row] — steps 3–4 NO row
  (duck-dip rows 210/211 held, must NOT play).
- d/f+4,4 [205,NO row] — crouch context, grounded crouch row 205 correct; review row
  212 must NOT play.
- 4,3 / 4,4: NO row any step (review row 199 held, must NOT play; step 2s NO row).
- WS.3,3 / ws3,3 / d/b+3,4 / db+3,4 / df+4,3: NO row any step (donor rows 195/199 must
  NOT appear as whole-string clips).
- No step plays a jin airborne/jump row (35/216/41) for a ground step. No step plays a
  row from another bank.
- Scimitar Batch 1 spot-checks undisturbed (2,1 [220,221], 2,1,2,2 [220,221,222,223],
  d+1+2,2 [92,93], 1,2 [NO row,186], d+1+2,1 [92,NO row]).
- Quarantined-only strings behave per plan ONLY after #988 merges (Batch 2: df+4,3).
- **No play verification is claimed** — tests + file evidence only; playing is the
  parent's step after merge + deploy.

## Workspace

~/workspace/scimitar-batch2/ — fetch/fetch_bank scripts, derive/build/wire scripts,
universe/step_table/Job 3/Job 4/drift JSONs, Batch 2 CSV (18 rows), plans (18 keys),
minimal-tree test run, adjudication doc, wired scimitar.json, both tests, audit append,
filing/commit.json + pr.json.
