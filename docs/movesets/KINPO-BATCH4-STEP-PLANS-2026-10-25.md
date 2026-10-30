# KINPO BATCH 4 STEP PLANS — triples/quads + rest (2026-10-25)

Stack: kinpo Batch 4 (LAST kinpo batch), stacked on kinpo Batch 3 (PR
#1119), which stacks on kinpo Batch 2 (PR #1118), which stacks on kinpo
Batch 1 (PR #1117), which stacks on #1096 (the step-playback engine).
Merges AFTER #1119 (after #1118, after #1117, after #1096 — itself
blocked on 12 pre-existing failures / a gate decision owed; this lane
fixes neither and merges nothing itself). This PR does not touch
fighter.js, pantera.json, burger.json, demonio.json, or diablo.json.
Nothing touches `t8_quarantine_20261024`. No T8 removals anywhere in
this lane.

## Scope

EVERYTHING NOT COVERED BY BATCHES 1–3. Batches 1–3 covered every
canonical whose steps all carry buttons and whose button union has size
≤ 2 (B1: LP1/RP2-only; B2: LK3/RK4-only; B3: mixed pairs). Batch 4 is
everything else, in two groups (LP1 = Left Punch = Tekken 1, RP2 = Right
Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick =
Tekken 4):

- (a) **Triples/quads** — every step buttoned, button union size 3–4
  (incl. 3-button chords + 10-hit strings) — PLANNED unless
  throw/grapple class or narrow grapple label (CSV-only then).
- (b) **Rest** — ≥ 1 buttonless step (dash/movement/stance-prefix
  sequences, measured from the file: `f,F+1`, `f,f,F+3`, `WALL.b,b,u/b`,
  `FC.d/f,d,d/f+1+2`, `NWG.f,F+1+2`, `n,d/f,n,d/f+1`, `3~4,D/F`, …) —
  CSV-AUDITED ONLY, never planned. Planning them needs engine support
  for non-attack prefix steps — future work, named, not guessed.

Throw-class triple-quads get NO plan (CSV-audited only) under the narrow
label rule (only {PILE_DRIVER, ARM_BREAKER, TACKLE} count as grapple
labels — stances are NOT grapples). Other throw-named chains with
move_class string ARE planned under the narrow label rule, but their
steps fail strike HARD gates (throw flag) → unmapped, never wired as
strikes. (Batch 4 has exactly one throw-class triple-quad:
`CHARGE.d/f+3+4,3+4,1+2`, move_class throw in both the Batch 3 branch
and main — CSV-only, no plan.)

## Bank (verified, not assumed)

Kinpo's T3 bank is JIN, four-way file evidence (kinpo Batches 1–3
re-verified, not re-assumed): kinpo.json `t3_source: 'jin'`,
`t3_bank: 'moveset_jin.json'` on BOTH the Batch 3 branch and current
main; `game/assets/anim/t3/` on main contains a `jin` dir (hit_frames +
rows.pack + skeleton) and NO `asuka` dir; Job 1 bank jin (220 rows);
Job 2 kinpo entries all bank jin (525); Job 4 jin candidates (47).
Kinpo's T7/T8 base IS Asuka (`tekken_base` Asuka, merge_sources t8/t7
asuka), but Asuka debuted in Tekken 5 and has NO T3 bank in this repo,
so the file's T3 fallback bank is jin, consistently applied everywhere
(`t3_source`, `t3_bank`, every `anim_ref` `t3:jin:row:N`, every move name
like `KINPO 2 (T3 jin r220)`, Job 2 bank) — the burger pattern (Bob →
bryan). The T7-Asuka re-match is future work; this batch adjudicates
against jin as the file declares. The pack dir does NOT differ from the
moveset bank name here (unlike diablo's heihachi/heihachi_on_jin split).

Bank-specific row rules (per-bank evidence, never a cross-bank blanket
ban): row 35 EXISTS here (hit_frames [11,12,39,535,0,1], Job 1 stance
starts-airborne) — not blanket-banned by number, but the stance gate
rejects it for ground steps; kinpo's own LP1 move `1` carries `t3_row`
35. Row 220 is a STANDING RP2 row here (hit_frames [12,12,41,1042,0,2],
Job 1 standing) — gate-adjudicated, NOT king's jumping chord row, NOT
bryan's button-0 row, NOT heihachi's jump RK4 row. Jin row 216 is a JUMP
row, NOT king row 216's dash Konvict Kick (it appears only as a Job 4
orphan in Batches 1–4).

Gap-1 (diablo method, re-verified): main jin hit_frames blob
`54b38e63…` and skeleton blob `26f72eb7…` are IDENTICAL on the Batch 3
branch and current main; main jin rows.pack blob `7bafa36a…` (226 rows)
differs from the Batch 3 branch's `141fbc8d…` (220 rows) — EXPLAINED:
the 6 extra rows are exactly the #1109 bake's jin rows
(89/112/247/288/339/357); main's pack is a SUPERSET (0 removed).
Cited-row profiles MATCH Job 1 vs hit_frames for every verified +
review row (92/186/199/220/221/222/223/224/225/230/232/233). Every wired
row is present in BOTH packs (verified at wire time). Main kinpo.json
blob `614c1e0a…` UNCHANGED since the Batch 1 baseline.

## Universe (measured first) + COVERAGE-COMPLETE PROOF

Base = Batch 3 branch kinpo.json: 525 moves / 101 strings / 115 plans.
Batch 3 branch moves == #1096 moves exactly (verified); strings
identical. Current main: 482 moves + 43 quarantined = 525, 0 main-only
moves, strings 101/101.

- **70 canonicals** (29 triples/quads + 41 rest); 28 planned + 42
  CSV-only; 120 CSV rows (70 canonicals + 50 twins); **62 plan keys**
  (28 planned canonicals + 34 variants).
- Triples/quads planned (28): `1+2+3+4,1+2`, `1+4,2`, `1+4,2,1`,
  `1+4,2,4`, `1+4,2,d+4`, `1+4,3`, `1,2,3`, `1,2,4`, `2,1,2,2,3`,
  `2,1,2,2,3,4`, `2,1,4`, `2,1,4,4`, `2,1,4,4,2`, `2,1,4,4,2,4`,
  `4,1,2`, `WS.2,1,1,1,2,1+4,1,3+4`, `WS.2,1,1,1,2,1,4,3,3+4`,
  `WS.2,1,1,3`, `b+1+4,3`, `b+2,1+2,4`, `b+4,2,3`,
  `ws2,1,1,1,2,1+4`, `ws2,1,1,1,2,1+4,1`,
  `ws2,1,1,1,2,1+4,1,3+4`, `ws2,1,1,1,2,1,4`,
  `ws2,1,1,1,2,1,4,3`, `ws2,1,1,1,2,1,4,3,3+4`, `ws2,1,1,3`.
  Pure single-button: 14; chord-involved: 56 (across all 70).
- Rest (41, CSV-only): `(Back to wall).b,b,UB`, `1+4,3,B`, `1,2,3*,B`,
  `1,4,D`, `3+4,D`, `3~4,D/F`, `FC.3+4,3,D`, `FC.3+4,D`,
  `FC.d/f,d,d/f+1+2`, `NWG.f,F+1+2`, `NWG.f,f,F+1+2`, `R.f,F+1+2`,
  `WALL.b,b,u/b`, `WS.1+2,D`, `b+2,1+2,D`, `b+2,4,D`, `b+3,2,D/F`,
  `d,d/b,d,d/b+1+2`, `d/b+4,4,4,D`, `d/b+4,4,D`, `d/b+4,D`,
  `f+1,d+4,D/B`, `f+2,D`, `f+3*,B`, `f,F+1`, `f,F+1+2`, `f,F+2`,
  `f,F+2,1`, `f,F+2,1+2`, `f,F+2,3`, `f,F+3`, `f,F+4`, `f,f,F`,
  `f,f,F+1+2`, `f,f,F+3`, `f,f,f+3`, `n,b,n,f+2`, `n,d/f,n,d/f+1`,
  `n,f,n,f+1+2`, `u/b,b`, `ub,b`.
- Contexts: standing 49, ws 11, crouch 8, jump 2.
- Provenance: 64 in main moves, 6 quarantined-only ((Back to
  wall).b,b,UB; 1+2+3+4,1+2; ws2,1,1,1,2,1+4; ws2,1,1,1,2,1+4,1;
  ws2,1,1,1,2,1,4; ws2,1,1,1,2,1,4,3 — live when #988 merges),
  0 Batch 3-branch-only.
- Overlap vs Batch 1 universe: []. Overlap vs Batch 2 universe: [].
  Overlap vs Batch 3 universe: [].
- **COVERAGE-COMPLETE PROOF:** total canonical comma keys in the Batch 3
  base file (moves + strings, corrected canonicalization) = **135 =
  32 (Batch 1) + 12 (Batch 2) + 21 (Batch 3) + 70 (Batch 4)**.
  Uncovered: []. Extra (in a batch universe but not in the base file):
  []. Plan keys total: **177** (47 + 20 + 48 + 62). Every canonical
  comma key in the base file is planned or CSV-audited.
- Input-~ canonicals in Batch 4 scope: **exactly 1 — `3~4,D/F`**, the
  file's ONLY old-vs-corrected diff, filed as its own rest canonical
  with NO plan (never a variant of `3`; asserted in the Batch 4 test).
  Under the old rule it would collapse to a bogus single `3`. __main
  records: 0. Corrupted keys: 0.
- Spelling quirks kept: `WS.2,1,1,1,2,…` vs `ws2,1,1,1,2,…` families
  are distinct canonicals (same union, different stored spelling —
  WS-context fix from Batch 1 applies to both: lowercase no-dot
  while-standing spellings are WS context, not standing; changes NO
  wiring); `u/b,b` vs `ub,b` are distinct rest canonicals; `d/f` vs
  `df` spellings are distinct canonicals — not merged, not smoothed
  over.

## Step tallies

247 steps = 131 planned + 3 throw-CSV-only + 113 rest. Planned:
**27 verified / 2 review / 102 unmapped**.

Unmapped split (planned): **2 suspended-drift + 6 rejected-candidate
+ 96 no-candidate**. (The 6 rejected = 2 suspended-drift steps, which
carry a stale candidate row, + 4 gate-rejected steps.)

Canonical status (planned): 2 verified-all (`2,1,2,2,3`; `2,1,4`) /
6 partial (`4,1,2`; `2,1,4,4`; `2,1,4,4,2`; `2,1,2,2,3,4`;
`2,1,4,4,2,4`; `b+2,1+2,4`) / 20 unmapped-all / 0 review-only.
Plan-key last-step: **5 verified / 1 review / 56 unmapped**.
Verified-last-step keys exactly: `2,1,2,2,3`, `2,1,4`, `2,1,4,4,2`,
`2,1,4,4,2,4`, `4,1,2`. Review last-step key exactly: `2,1,2,2,3,4`.

Verified rows (10 distinct, all baked in main's jin pack AND the Batch 3
branch pack): 92, 186, 220, 221, 222, 223, 224, 230, 232, 233. All 27
verified steps are standing-context steps on standing rows — NO
gate-note cases this batch (no standing-row-for-crouch-step
verification). Verified sources: prefix-move 21, recorded-dest 4,
recorded-path 1, Job 3 fill 1.

## Every wired fill (verified only, T3 FALLBACK)

- `2,1,2,2,3` (verified-all): **220 / 221 / 222 / 223 / 224**
  (prefix-move own rows for steps 1–4; step 5 recorded-dest row 224,
  standing LK3, hit_frames [18,18,62,535,0,4], SOFT window [7,11] legL
  peak 9). Row 220: standing RP2, hit_frames [12,12,41,1042,0,2], SOFT
  window [4,8] armR peak 6. Row 221: standing LP1, hit_frames
  [14,14,43,1042,0,1], SOFT window [5,9] armL peak 7. Row 222: standing
  RP2, hit_frames [10,10,39,1042,0,2], SOFT window [3,7] armR peak 5.
  Row 223: standing RP2, hit_frames [17,17,60,1042,0,2], SOFT window
  [6.5,10.5] armR peak 8.
- `2,1,4` (verified-all): **220 / 221 / 230** (step 3 recorded-dest row
  230, standing RK4, hit_frames [17,18,52,535,0,8], SOFT window
  [6.5,11] legR peak 10).
- `2,1,4,4` (partial): **220 / 221 / 230 / NO row** (step 4 candidate
  231 rejected — button 12 != step bits 8, see below).
- `2,1,4,4,2` (partial): **220 / 221 / 230 / NO row / 232** (step 5
  recorded-dest row 232, standing RP2, hit_frames [23,23,68,271,0,2],
  SOFT window [9.5,13.5] armR peak 12; also Job 4-joined, no action).
  Note: row 232 is also `2,1,4,4,2`'s own Job 2 pick (own:row:232) — the
  step plan wires all five steps individually; the last step happening
  to equal the whole-string own pick is coincidence, not a single-row
  fix.
- `2,1,4,4,2,4` (partial): **220 / 221 / 230 / NO row / 232 / 233**
  (step 6 recorded-dest row 233, standing RK4, hit_frames
  [16,17,51,535,0,8], SOFT window [6,10.5] legR peak 10). Note: row 233
  is also `2,1,4,4,2,4`'s own Job 2 pick (own:row:233) — same note as
  above; the plan still wires all six steps individually.
- `2,1,2,2,3,4` (partial): **220 / 221 / 222 / 223 / 224 / review**
  (last step candidate 225 held — see Review holds).
- `4,1,2` (partial): **review / NO row / 186** (step 3 recorded-path
  row 186, standing RP2, hit_frames [27,27,64,1042,0,2], SOFT window
  [11.5,15.5] armR peak 13).
- `b+2,1+2,4` (partial): **NO row / 92 / NO row** — step 1+2 is the
  batch's ONLY Job 3 fill (see Job 3 / Job 4).
- Twins inherit canonical steps verbatim (Batch 1 twin precedent).

## Review holds (2 steps, row null, NOT wired)

- `2,1,2,2,3,4` step 4 (last step): candidate **225** (recorded-dest,
  standing RK4, hit_frames [37,39,76,535,0,8]) passes HARD for
  standing, then SOFT limb-peak proxy FAILS (window [16.5,21.5], legR
  peak 6) — held at review, never wired.
- `4,1,2` step 1: candidate **199** (recorded-path, Job 2 CLEAN own row
  for move `4`, standing RK4, hit_frames [11,11,49,535,0,8]) passes
  HARD for standing, then SOFT limb-peak proxy FAILS (window [3.5,7.5],
  legR peak 3) — held at review, never wired. Same row, same result as
  Batch 3's `4,1` step 1 hold. Note: row 199 is also the whole-string
  donor row for the `4,1` family in the CSV; the step-plan correctly
  does NOT wire it as a verified row.

## Suspended-drift (2 steps, row null, never wired)

- `1,2,3` step 1, `1,2,4` step 1 — prefix move `1` is the file's ONLY
  row-changed move (35→None, Batch 3 branch vs current main). Stale row
  35 documented, never wired (it would fail the stance gate for ground
  steps regardless — starts-airborne per jin Job 1).

## Rejected-candidate (4 gate steps, row null)

- `2,1,4,4` step 4, `2,1,4,4,2` step 4, `2,1,4,4,2,4` step 4: row **231**
  (recorded-dest for `2,1,4,4`; prefix-move for the longer strings) —
  button 12 != step bits 8 (a kick-chord row, LK3+RK4, for a single RK4
  step). Same row, same result as demonio Batch 4's `2,1,4,4` step 4
  gate failure (demonio's gate candidate 231 FAILED the button gate as
  a chord row and was superseded there by the Job 3 fill row 114; here
  no fill exists for the step, so it stays unmapped).
- `4,1,2` step 1: row **184** (recorded-path) — button 9 != step bits 1
  (a chord row, LP1+RK4, for a single LP1 step; Job 2 verdict HARD
  string-ender-on-chord, consistent). Same row, same result as Batch
  3's `4,1` step 2 rejection.

## No-candidate (96 planned steps)

`1+2+3+4,1+2` steps 1–2; `1+4,2` steps 1–2; `1+4,2,1` steps 1–3;
`1+4,2,4` steps 1–3; `1+4,2,d+4` steps 1–3; `1+4,3` steps 1–2;
`1,2,3` steps 2–3; `1,2,4` steps 2–3; `WS.2,1,1,1,2,1+4,1,3+4` steps
1–8; `WS.2,1,1,1,2,1,4,3,3+4` steps 1–9; `WS.2,1,1,3` steps 1–4;
`b+1+4,3` steps 1–2; `b+2,1+2,4` steps 1 + 3; `b+4,2,3` steps 1–3;
`ws2,1,1,1,2,1+4` steps 1–6; `ws2,1,1,1,2,1+4,1` steps 1–7;
`ws2,1,1,1,2,1+4,1,3+4` steps 1–8; `ws2,1,1,1,2,1,4` steps 1–7;
`ws2,1,1,1,2,1,4,3` steps 1–8; `ws2,1,1,1,2,1,4,3,3+4` steps 1–9;
`ws2,1,1,3` steps 1–4.
Recorded path + prefix move both absent — T8-sourced prefixes with no
T3 row; correct clips come from #988 Step 2 (original T8 refs) or
future extraction. Whole-string donor rows documented in the CSV, never
wired: row 195 (`1,2,3` / `b+1+4,3` / `b+4,2,3` / `WS.2,1,1,3` /
`ws2,1,1,3` / `ws2,1,1,1,2,1,4,3` families), row 220 (`1+4,2` family),
row 32 (`1+2+3+4,1+2` family — jump row, HARD stance), row 199
(`ws2,1,1,1,2,1+4` / `ws2,1,1,1,2,1,4` families), row 35
(`ws2,1,1,1,2,1+4,1` family — starts-airborne, HARD stance), row 51
(`ws2,1,1,1,2,1+4,1,3+4` / `ws2,1,1,1,2,1,4,3,3+4` /
`WS.2,1,1,1,2,1+4,1,3+4` / `WS.2,1,1,1,2,1,4,3,3+4` families — jump
row, HARD stance).

## Job 3 / Job 4

- Job 3 fills wired: **1**. Report entries: 13. `b+2,1+2,4` step 1+2
  ← **row 92** (target `b+2,1+2`, exact level h==h, FULL provenance
  incl. `moveset_kinpo:d+1+2(2+LP+RP)` — plus demonio/scimitar
  provenance strings — timing 1.5, HARD + SOFT proxy pass window
  [3.0,7.0] peaks armL 5 / armR 3). This is the SAME row 92 as kinpo
  Batch 1's `b+2,1+2` fill (target `b+2,1+2`) — consistent, not
  cross-target inheritance: the target here IS `b+2,1+2` as a step
  prefix of `b+2,1+2,4`. Row 105 (exact, ROW-ONLY, same target)
  documented, not wired. No agreement note fires: the note fires ONLY
  for actually-wired gate candidates disagreeing with an exact+FULL
  Job 3 candidate, and the only exact+FULL Job 3 candidate in scope
  (row 92) IS the fill — no wired gate candidate faces a disagreeing
  exact+FULL candidate. Dedupe fires zero times (no prefix__main
  duplicate pass-all rows in scope). Other report entries (not wired):
  `1+4,2,1` step 1, `1,2,3` / `1,2,4` step 1, `ws2,1,1,1,2,1+4` /
  `ws2,1,1,1,2,1+4,1` / `ws2,1,1,1,2,1,4` / `ws2,1,1,1,2,1,4,3` /
  `ws2,1,1,3` step 1 — rows 92/105 exact ROW-ONLY (targets `1+4,2,1` /
  `1` / `ws2,1`); the `1`-target entries additionally sit behind the
  suspension; `ws2,1,1,1,2,1+4,1,3+4` + `ws2,1,1,1,2,1,4,3,3+4` last
  steps — rows 101/116/131/132 soft-nofiled (FULL and ROW-ONLY mixed).
  SOFT and ROW-ONLY candidates are documented, NEVER wired.
- Job 4 joins (CORRECTED join only, BANK_DIR jin): **2, both no-action**
  on already-verified steps (row 232 joined on `2,1,4,4,2` step 2 and
  `2,1,4,4,2,4` step 2 — peaks armL 2 / armR 1 / legL 0 / legR 0), 0
  promoting. Orphans: jin rows 85, 91, 99, 100, 104, 127, 170, 171,
  172, 209, 216, 226, 239, 250, 256, 262 (same set as Batches 1–3,
  independently re-derived). Row 216 is jin's jump row, NOT king row
  216's dash Konvict Kick.

## Drift census (both ways — identical to Batches 1–3)

Full file (525 keys, Batch 3 branch vs current main): 253 same /
168 damage-only / 103 anim_ref-changed / 1 row-changed (`1`: 35→None).
Damage differs on 227 moves (all-status) vs 168 damage-only — both true
under their definitions; the 59 gap = damage differs AND row/anim_ref
also changed. Damage-only drift does NOT suspend. Step-prefix census
(59 distinct planned prefixes): same 24 / damage-only 4 /
anim_ref-changed 22 / ROW-CHANGED 1 (`1`) / no-Batch-3-branch-move 8.
Only `1` is row-changed and it IS a Batch 4 step prefix (the step-1s of
`1,2,3` / `1,2,4`) — 2 suspended-drift steps.

## Tests (file evidence only — NOT play-verified)

Minimal-tree `node --test`: **48 pass / 0 fail** (13 Batch 1 cumulative +
11 Batch 2 + 11 Batch 3 + 13 Batch 4). `node --check fighter.js` OK.
Formatter round-trips the Batch 3 branch file byte-identically; all
non-plan keys identical; all 115 Batches 1–3 plans deep-equal; moves 525
/ strings 101 unchanged. Batch 1 + Batch 2 + Batch 3 test diffs prove
every CONTENT assertion preserved verbatim (only counts,
extra-keys/complement counts, const additions, header notes changed —
the burger Batches 2–4 fix; Pantera's latent break NOT copied).

**Limitation (honest):** full 200-test suite comparison NOT run — no
full current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + #1117
+ #1118 + #1119 + this PR merge + deploy + sync, phone portrait)

- `2,1,2,2,3`: grounded, rows 220/221/222/223/224, all standing.
- `2,1,4`: grounded, rows 220/221/230, all standing.
- `2,1,4,4`: 220/221/230, last step NO row (row 231 must NOT play —
  kick-chord row for a single RK4 step).
- `2,1,4,4,2`: 220/221/230, NO row, 232 (row 231 must NOT play).
- `2,1,4,4,2,4`: 220/221/230, NO row, 232, 233 (row 231 must NOT play).
- `2,1,2,2,3,4`: 220/221/222/223/224, last step NO row (row 225 must NOT
  play — SOFT-held).
- `4,1,2`: NO row, NO row, 186 (rows 199/184 must NOT play — SOFT-held
  and chord-rejected respectively).
- `b+2,1+2,4` + twins: NO row, 92, NO row (donor rows must NOT appear
  as whole-string clips).
- `1,2,3` / `1,2,4` + twins: NO row any step (stale row 35 must NOT
  play).
- `1+4,2` / `1+4,2,1` / `1+4,2,4` / `1+4,2,d+4` / `1+4,3` + twins,
  `b+1+4,3` + twins, `b+4,2,3` + twins, `WS.2,1,1,3`, `WS.2,1,1,1,2,…`
  families, `ws2,1,1,3`, `ws2,1,1,1,2,…` families, `1+2+3+4,1+2`:
  NO row any step (donor rows 195/220/32/199/35/51 must NOT appear as
  whole-string clips).
- No step plays row 35 for a ground step (starts-airborne per jin Job
  1). Row 220 plays ONLY for RP2 steps (standing RP2 row in this bank
  — grounded, not airborne). No step plays a row from another bank.
- Rest keys unchanged — donor clips, NOT per plan, since rest keys get
  no plan.
- Kinpo Batches 1–3 spot-checks undisturbed (2,1 [220,221], 2,1,2,2
  [220,221,222,223], d+1+2,2 [92,93], b+2,1+2 last step 92, 1,1 step 1
  still suspended; u/f+4,3 [80,193], u/f+4,4 [80,207], d/f+4,4 [205, NO
  row] with review 212 held, u/f+4,4,4 [80,207, NO row] with review 210
  held; 2,3 [220, NO row], 3,1 [195, NO row], 4,1 [review, NO row] with
  review 199 held, 1,3 step 1 still suspended). Quarantined-only strings
  behave per plan ONLY after #988 merges (Batch 4: (Back to
  wall).b,b,UB, 1+2+3+4,1+2, ws2,1,1,1,2,1+4, ws2,1,1,1,2,1+4,1,
  ws2,1,1,1,2,1,4, ws2,1,1,1,2,1,4,3).

**No play verification is claimed here** — tests + file evidence only;
playing is the parent's step after merge + deploy.
