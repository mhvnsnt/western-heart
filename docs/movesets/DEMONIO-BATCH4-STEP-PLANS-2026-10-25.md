# Demonio Batch 4 step plans — triples/quads/rest (2026-10-25)

Demonio Batch 4 is the LAST demonio batch. It completes demonio's string
coverage the way Pantera Batch 4 and burger Batch 4 completed theirs:
every canonical comma key in the Batch 3 base file is now planned or
CSV-audited. "Complete" means classified with file evidence per step —
it does NOT mean every step plays a verified row. The next mapping work
is filling unmapped steps from real clips (via #988 Step 2 original T8
refs + future extraction), not re-classifying strings.

Method: same verified pipeline as demonio Batches 1–3 + Pantera Batches
1–4 + burger Batches 1–4. Step-plans (one verified row per prefix step)
via #1096's continuation path; exact-signature equality; jumping rows
rejected for ground steps; T3-row matches are FALLBACK matches logged in
docs/anim/PROCEDURAL_AUDIT.md, never recorded as the correct mapping,
re-matched to T7 Jin rows when decode lands. Job 3 fills re-baselined
vs current main (gap-1: bank hashes + cited-row profiles verified
identical before wiring; damage-only drift does NOT suspend, changed
moves SUSPENDED). Job 4 joins ONLY via the corrected join
(fighter-only, BANK_DIR jin, join iff Job 2 entry key == step prefix,
row == candidate row, step == own — a join NEVER promotes by itself;
naive cross-fighter join INVALID). SOFT candidates documented, NEVER
wired without user approval (no SOFT inheritance from #1097).
SOFT proxy (validated 13/13 on Pantera Batch 1 verified steps)
conservative: proxy-fail = review, never false verify. Burger
refinement carried forward: Job 3 fills additionally require the SOFT
proxy to pass (stricter than Pantera Batch 4's HARD-only fill rule).
Job 3 dedupe prefix vs __main duplicates (burger Batch 2 cleanup).
Donor retirement is DESIGNED (wiring plans replaces single-row
resolution wholesale, even for CLEAN donors). Surgical diffs via
json.dumps(indent=2, ensure_ascii=False) + "\n" (round-trips base
byte-identically). Minimal-tree node --test pass + node --check
fighter.js OK. Full 200-test suite comparison NOT run by this lane
(no full current-main checkout on this box — stated as a limitation in
the PR body; CI must cover before merge). NO batch lane play-verified
anything (parent browser delegation after merge + deploy). NO T8
content touched by this lane.

## Stack

Branch from demonio Batch 3's branch
feat/demonio-batch3-step-plans-20261025 (PR #1111). Demonio plans
accumulate: #1096 engine → demonio Batch 1 (#1108) → Batch 2 (#1110) →
Batch 3 (#1111) → this Batch 4. Merges AFTER #1111 (after #1110, after
#1108, after #1096, itself blocked on 12 pre-existing failures / a gate
decision owed — this lane fixes none of those and merges nothing
itself). The audit append (docs/anim/PROCEDURAL_AUDIT.md) is shared —
append-only; if the Pantera or burger stacks or demonio Batches 1–3
merge first, rebase the audit append after their entries (never
overwrite them). If #1097 merges first, note its guard-map interaction
(demonio has its own guard map; Pantera's SOFT decision does not
transfer). This PR does not touch fighter.js, pantera.json, or
burger.json.

## Bank (verified, carried forward — not re-litigated)

Demonio's T3 bank is JIN (demonio.json t3_source: 'jin', t3_bank:
'moveset_jin.json' on BOTH the Batch 3 branch file and current main;
game/assets/anim/t3/ on main contains a jin dir (22 banks); Job 1 =
220 jin rows, Job 2 = 764 demonio entries bank jin, Job 4 = 47 jin
candidates). Jin exists in Tekken 3, so no substitution (unlike
burger's bryan fallback).

JIN-BANK RULES (Batch 1's documented correction, carried forward):
jin row 220 is a STANDING RP2 row (hit_frames [12,12,41,1042,0,2],
Job 1 stance standing, travel 0.216) — NOT blanket-banned;
gate-adjudicated per step. Jin row 35 IS starts-airborne, so the
row-35 rejection for ground steps stands, and row 35 verifies ONLY in
jump context. No Batch 4 verified step uses row 35 at all. Jin row 216
is a JUMP row (Batch 3 proved it for 1+4,b+1's last step) — NOT king
row 216 dash Konvict Kick; never cite king's row-216 identity for a
jin row. No Batch 4 verified step uses row 216 either. Jin Job 1
carries a duck-dip stance (16 rows), handled like crouch: STANCE-SOFT
(review) for non-crouch contexts.

Gap-1 re-verification: main jin bank blobs identical to the Batch 1
baseline (hit_frames 54b38e63…, rows.pack 141fbc8d…, skeleton
26f72eb7…, API-confirmed); main demonio.json blob e938e8d5…
unchanged since Batch 1. Cited-row profiles MATCH Job 1 vs hit_frames
for all 26 verified rows + all review rows.

## Canonicalization (corrected rule, carried from Batches 2–3 — not re-litigated)

Strip ONLY a trailing source-variant suffix
~t[378]\.[a-z]+(\.\d+)?$ (~t3.jin, ~t7.jin[.N], ~t8.jin). A ~ INSIDE
the input is Tekken cancel notation, part of the move, not a variant
marker. Batch 4 carry-forwards 2,1,4~4 and 4~3,H.1+2 are OWN Batch 4
canonicals, not variants of 2,1,4 or 4.

CORRECTION to Batch 3's parenthetical: 2,1,4~4's button union is
{1,2,4} (steps 2 / 1 / 4~4 = RP2 / LP1 / RK4-cancel-RK4) — a TRIPLE,
not a quad. 4~3,H.1+2's union is {1,2,3,4} (steps 4~3 = RK4-cancel-LK3,
H.1+2 = LP1+RP2) — a quad. Both are Batch 4 scope (union size >= 3)
either way; the correction changes no filing, only the label.

The __main duplicate key 2,1,4__main is its OWN canonical, NOT a twin
of 2,1,4: __main is not a source-variant suffix under the corrected
rule, and the __main entry is a distinct record (branch: damage 36,
anim_ref t8:jin:jin-2,1,4; main: damage 9, anim_ref
UNMAPPED:t7-clip-pending; both t3_row None) vs plain 2,1,4 (t3_row
230). Its plan is partial [220, 221, None] — the shared 2,1 prefix rows
verify, the __main last step has no T3 row of its own and does NOT
inherit row 230 from plain 2,1,4 (identity the file does not assert).
The other four __main keys in demonio moves (1+2__main, f+4__main,
u/f+3__main, qcb+1+3__main) are single moves, not strings, so they
enter no batch universe.

Batch 1 old-rule proof re-verified in this lane: 26 keys where the old
canonical() (strip at first ~) differs from the corrected rule; NONE
of their old-canonicals lands in Batch 1's universe — Batch 1
unaffected, again. (The Pantera/burger canonicalization audit,
separately reported, found NO misfiling there: neither inventory
contains cancel-notation ~ at all. Future lanes — diablo, kinpo,
phantom, scimitar, skull — MUST still use the corrected rule; their
inventories are unchecked.)

## Tallies

- 164 canonicals = 68 planned + 96 CSV-only.
  - 69 triples/quads (every step buttoned, union size 3–4, incl.
    3-button chords) + 95 rest (at least one buttonless step:
    dash/movement/stance-prefix sequences).
  - Planned: 68 triple/quad strike canonicals. CSV-only: 96 = 95 rest
    keys + 1 throw triple-quad (u/f+3+4,H.1+2, move_class throw).
- 100 plan keys = 68 planned canonicals + 32 twins. 214 CSV rows
  (164 canonicals + 50 variants).
- 677 steps total = 318 planned-string steps + 359 CSV-only steps.
- Planned steps: **133 verified / 26 review / 159 unmapped**
  (120 no-candidate + 31 rejected-candidate + 8 suspended-drift).
- Plan-key last-step: 25 verified / 10 review / 65 unmapped.
- Canonical string_status (planned only): 5 verified-all / 37 partial
  / 26 unmapped-all / 0 review-only.
- Suspended-drift steps: 8 (all step-1 prefix `1` — see below).
- Job 3 fills: 6 step-records, 1 distinct prefix step (2,1,4,4 step 4
  <- row 114, applied in 6 strings). Job 4 joins: 33, none promoting.
  Orphans: 2 (jin rows 85, 91 — same set as Batches 1–3).
- Provenance: 137 canonicals in main moves, 27 quarantined-only
  (live when #988 merges), 0 in-#1096-only.
- Contexts: standing 138, crouch 13, jump 8, ws 5.

## Every wired fill (verified only; jin hit_frames button == step bits, throw 0; T3 FALLBACK logged in the audit)

Gate-verified own/recorded rows (127 steps). Flagships:

- `2,1,2,2,3` verified-all: rows 220/221/222/223/224.
  hit_frames 220 [12,12,41,1042,0,2] (RP2), 221 [14,14,43,1042,0,1]
  (LP1), 222 [10,10,39,1042,0,2] (RP2), 223 [17,17,60,1042,0,2] (RP2),
  224 [18,18,62,535,0,4] (LK3). All SOFT passed outright.
- `2,1,4` verified-all: rows 220/221/230. Row 230 [17,18,52,535,0,8]
  (RK4). SOFT passed outright.
- `2,1,4,4,2,4` verified-all: rows 220/221/230/114/232/233. Row 232
  [23,23,68,271,0,2] (RP2), row 233 [16,17,51,535,0,8] (RK4). SOFT
  passed outright.
- `1+4,2` family RP2 step (prefix `1+4,2`): row 186 [27,27,64,1042,0,2],
  in five strings. SOFT passed outright.
- `3,1,2` / `3,1,4` family LK3 step (prefix `3,1`): row 195
  [19,23,61,535,0,4] (same row Batch 3 verified for `3,1` step 1).
  SOFT passed outright.
- `b+1+2,2,3` family: RP2 step row 94 [10,10,39,1042,0,2], LK3 step
  row 196 [25,31,69,535,0,4]. SOFT passed outright.
- `b+2,4,2,1` family RK4 step (prefix `b+2,4`): row 251
  [22,24,65,1042,0,8] (same row Batch 3 verified for the `b+2,4`
  family RK4 step); RP2 step row 252 [10,12,49,535,0,2]. SOFT passed
  outright.
- `b+2,4,4,4,4,2,1+4` family: RK4 step row 251, RP2 step row 258
  [22,23,55,535,0,2], LP1+RK4 chord step row 259 [23,24,75,271,0,9]
  (button 9 == bits 9). SOFT passed outright.
- `b+3+4,2` family RP2 step: row 239 [14,14,58,1042,0,2]. SOFT passed
  outright.
- `2,1,2,2,3,4,4` family RK4 steps: row 226 [22,22,66,271,0,8].
  SOFT passed outright. LP1 step row 227 [27,27,56,1042,0,1], RP2
  step row 228 [17,19,49,535,0,2], LK3 step row 237 [28,29,73,271,0,4],
  RP2 step row 238 [25,26,63,535,0,2]. SOFT passed outright.
- Jump lasts (SOFT waived per Batch 1 jump precedent — FK
  systematically silent on jumping rows; waiver noted in each step's
  reasons): `u+1,2+4` last step row 170 [57,59,128,535,0,10] (LP1+RK4
  chord, button 10 == bits 10); `u/b+1,2+4` last step row 172
  [57,59,128,535,0,10]. (`u/f+1,2+4` does NOT verify: its first step
  candidate 33 is a button-3 LK3 row for an LP1 step, and its last
  step candidate 171 is a button-12 LK3+RK4 chord row for the
  LP1+RK4 step (bits 10) — both rejected on buttons, jump context
  notwithstanding.)

Job 3 fill (1 distinct prefix step, 6 strings):

- `2,1,4,4` step 4 (RK4, prefix `2,1,4,4`): row 114, in `2,1,4,4`,
  `2,1,4,4,2`, `2,1,4,4,2,4`, `2,1,4,4,2,4,3`, `2,1,4,4,2,4,3,2`,
  `2,1,4,4,2,4,3,2,1`. The gate candidate row 231 (the prefix move's
  own row) FAILED the button gate: hit_frames [15,16,49,535,0,12] —
  button 12 (LK3+RK4 chord row) for a single-RK4 step (bits 8). The
  fill was therefore judged on its own merits: row 114 exact level
  (filed m / played m), FULL provenance
  ['moveset_demonio:4~t3.jin(RK)'], timing 1.2; HARD gates pass
  (button 8 == bits 8, throw 0, standing row for a standing step);
  SOFT proxy passes (window [4.0,8.0], legR peakF 5). Exact ROW-ONLY
  also-rans 115/125/126 documented, not picked. WORDING FIX vs Batch
  3: the old Job 3 agreement note claimed a gate candidate was "kept"
  even when it had just failed HARD gates; the note now fires only
  for actually-wired gate candidates (zero such disagreements remain
  in Batch 4 — no verified step carries a DISAGREES note).

No Batch 4 verified step uses row 35 or row 216. No Batch 4 verified
step is a standing row for a crouch-context step (no Batch 1
gate-note case — zero crouch-context verified steps, zero
ws-context verified steps; 131 standing + 2 jump). No Batch 4 step
carries a soft flag (the row-114 fill is exact+FULL with the SOFT
proxy passed — a verified fill, not a soft fill).

## Every rejected / held candidate (row null, never played)

Review (26): 16 SOFT-fail + 10 STANCE-SOFT.

- SOFT limb-peak proxy fails (window, peak outside — fail is fail
  under the conservative rule): `1+4,2,1,4` step 4 candidate 188
  (prefix-move) window [8.5,13.5] legR peak 3;
  `2,1,2,2,3,4`-family step 6 candidate 225 (recorded-dest /
  prefix-move) window [16.5,21.5] legR peak 6, in seven strings;
  `4,1,2` step 1 candidate 199 (recorded path) window [3.5,7.5]
  legR peak 3 (same evidence as Batch 3's `4,1` step 1);
  `b+1+2,2,3,4` step 4 candidate 203 window [16.0,20.5] legR peak 6;
  `b+1+2,2,3,f+4` step 4 candidate 214 window [13.0,18.0] legR peak 3
  (same evidence as Batch 2's `f+4,3` step 1);
  `b+2,4,2,1` step 4 candidate 253 window [4.5,9.5] armL peak 25;
  `b+2,4,4,4,4,2,1+4,1,2`-family step 9 candidate 261 window
  [7.5,11.5] armR peak 0, in three strings;
  `b+3+4,2,1,4` step 4 candidate 241 window [5.5,10.0] legR peak 2.
- STANCE-SOFT (crouch/duck-dip rows for standing steps — review,
  never false verify): `2,1,4,4,2,4,3`-family step 7 candidate 234
  (crouch row) in three strings; step 8 candidate 235 (duck-dip
  row) in two strings; `b+2,4,4,4,4`-family step 5 candidate 257
  (duck-dip row, same evidence as Batch 3) in five strings.

Rejected own/recorded candidates (31 unmapped steps carry one):
14 button-mismatch + 16 airborne-for-ground + 1 throw-row.

- Button mismatches (14): `1+4,2,1` / `1+4,2,1,4` last step (LP1),
  candidate 187 (prefix-move): button 2 (RP2 row) for an LP1 step.
  `4,1,2` step 2 (LP1), candidate 184 (recorded path): button 9
  (LP1+RK4 chord row) for a single-LP1 step (same evidence as Batch
  3's `4,1` last step). `b+2,4,4,4,4,2,1+4`-family step 8 (LP1),
  candidate 260 (prefix-move): button 0, in four strings.
  `b+3+4,2,1` / `b+3+4,2,1,4` last step (LP1), candidate 240
  (prefix-move): button 0. `u/b+1,2+4` step 1 (LP1), candidate 34
  (prefix-move): button 3 (LK3 row) — the jump LP1 prefixes' own
  rows are kick rows (same pattern as Batch 3's `u/b+1,3` /
  `u/f+1,3`). `u/f+1,2+4` step 1 (LP1), candidate 33: button 3; step
  2 (LP1+RK4 chord, bits 10), candidate 171: button 12 (LK3+RK4
  chord row). `d+3+4,1` step 2 (LP1), candidate 272: button 0 AND
  airborne (counted here, button first). `u/f+2+4,1` step 2 (LP1),
  candidate 371: button 0 AND throw flag (counted here, button
  first).
- Airborne jin jump rows for ground steps (16): `2,1,2,2,3,4,4,1,2,1`
  last step, candidate 229; `2,1,4,4,2,4,3,2,1` last step, candidate
  236; the `b+2,4,4`-family RK4 steps, candidates 254/256 (in
  `b+2,4,4,1+2+3` steps 3–4 and the `b+2,4,4,4,4,2,1+4` family steps
  3–4 across five strings); `b+2,4,4,4,4,2,1+4,1,2,1` last step,
  candidate 250; `b+2,4,4,4,4,2,1+4,1,2,3+4` last step (LK3+RK4
  chord), candidate 262. Each documented per step in the step table
  with its y0/ymax vs standingY 1.027.
- Throw row (1): `u/f+2+4,1` step 1 (chord token), candidate 370
  (prefix-move): throw flag 1 — the chord step's own row is a throw
  row, not a strike row. Never wired. (The throw-class canonical
  `u/f+3+4,H.1+2` is CSV-only, not in this list.)

Suspended (8): the eight step-1 prefixes `1` — `1,2,3`, `1,2,3,4`,
`1,2,4`, `1,3,2`, `1,3,2,1`, `1,3,2,1,4`, `1,3,4`, `1,d+3,d+4` —
prefix move `1` is ROW-CHANGED 41→None (base vs current main).
Stale row 41 documented, never wired (jin row 41 is starts-airborne,
so wiring it would play a jumping clip for ground strings). The other
two row-changed moves (`1_r41`, `u+1,1~t3.jin.2`) do not fall in
Batch 4 scope.

Unmapped with NO candidate (120 planned steps + 359 CSV-only steps):
every such step's reason is "no candidate row (recorded path + prefix
move both absent)" (planned steps) or the rest-key / throw-class note
(CSV-only steps). All intermediate prefixes are T8-sourced with no T3
row; correct clips come from #988 Step 2 or future extraction, never
from a T3 row recorded as correct.

## Job 3 (fills: 6 step-records, 1 distinct prefix step)

35 report entries (29 unmapped steps + 6 verified fill steps), 7
distinct prefixes. Only row 114 is exact+FULL; everything else is
ROW-ONLY (exact or soft-nofiled) and never wired:

- Prefix `1` (12 entries, all suspended anyway): rows 92/105, exact
  + ROW-ONLY, timing 1.0 — never wired (FULL provenance required).
- Prefix `1,3` (6 entries): row 101, exact + ROW-ONLY — not wired.
- Prefix `2,1,4,4` (6 entries, all verified): row 114 exact + FULL
  (WIRED — see above); rows 115/125/126 exact + ROW-ONLY — not picked.
- Prefix `3,1` (4 entries): rows 92/105, exact + ROW-ONLY, timing
  1.4 — not wired.
- Prefix `b,f+2,1` (5 entries, rest keys): rows 92/105, exact +
  ROW-ONLY, timing 1.5 — not wired (rest keys get no plan anyway).
- Prefixes `d/f+3,3,B` / `d/f+3,3,F` (rest keys): rows 108/122
  exact + ROW-ONLY and 108/111/122 soft-nofiled + ROW-ONLY — not
  wired.

Fill rule (burger refinement, stricter than Pantera Batch 4's
HARD-only fill rule): a Job 3 fill additionally requires the SOFT
proxy to pass. Row 114 passes it (window [4.0,8.0], legR peakF 5).
No SOFT fill is inherited from #1097 (Pantera-specific, still
unapproved, does not transfer to demonio). Dedupe: prefix vs `__main`
duplicate pass-all rows deduped per the burger Batch 2 cleanup (no
`__main` duplicates among Batch 4 candidates — the `2,1,4__main`
key is a moves-dict duplicate, not a Job 3 target duplicate).

## Job 4 (joins: 33, none promoting — corrected join only)

Corrected join only (demonio-only, BANK_DIR jin, join iff Job 2 has a
demonio entry key == step prefix, row == candidate row, step == own).
The naive cross-fighter join on key-prefix equality is INVALID and was
not used. A join NEVER promotes a candidate by itself.

- 16 no-action: joined rows on already-verified steps (e.g.
  `2,1,2,2,3,4,4`-family step 4 row 226; `2,1,4,4,2` step 2 row 232).
- 11 rejected: airborne rows for ground steps (e.g.
  `2,1,2,2,3,4,4,1,2,1` step 1 row 229, jump stance) and throw rows.
- 2 CANDIDATE (pass HARD gates, NOT wired — a join never promotes):
  `b+1+2,2,3,4` step 4 row 203 (review step — the join does not
  upgrade review to verified); `u/f+3+4,H.1+2` step `u/f+3+4` row 52
  (CSV-only throw family — no plan either way).
- 4 rest-documented-only: `b+1,2,B` step `b+1` row 216;
  `d,d/b,b+1+3,1` step 1 row 377; `d/b,n,f+2,1` step 1 row 381;
  `d/f+1,2,f,F` step `d/f+1` row 179 — documented, rest keys get no
  plan.
- Orphans: 2 (jin rows 85, 91 — same set as Batches 1–3).

## CSV-only keys

95 rest keys (dash/movement/stance-prefix sequences — full list in the
universe JSON; flagships: `f,F+2`, `f,F+3`, `f,f,n,2`,
`f,f,n,2,1,2,2,3,4,4,1,2,1` (13 steps, the longest Batch 4 key),
`WALL.b,b,u/b`, `uf,n,4`, `u+4,U`, `SS.2,U`, `WR.f,f,F`) are
CSV-audited only, never planned. Their current in-game clips stand
(donor rows, documented per key in the CSV with HARD/jump-clip flags),
not fixed — the unblock is engine support for non-attack prefix steps,
not a plan. 1 throw triple-quad (`u/f+3+4,H.1+2`, move_class throw)
is CSV-only the same way (Batch 1 TACKLE precedent). Note the CSV
also flags two rest keys whose own move_class is throw
(`n,d/f,n,d/f+1`, `n,f,n,f+1+2`) — CSV-only on both grounds.

## Drift census (base = Batch 3 branch file vs current main, moves-dict)

Both counts, both true under their definitions (never silently pick one):

- Partition (764 moves): 517 same / 164 damage-only / 80
  anim_ref-changed / 3 ROW-CHANGED (identical to Batches 1–3's
  census — the base file's moves are identical to #1096's).
- Damage differs on 195 moves = 194 unchanged-row + 1 row-changed
  (`1`, 11→7).
- Damage-only drift does NOT suspend (damage is not animation).
  Row-changed moves: `1` (41→None), `1_r41` (41→None),
  `u+1,1~t3.jin.2` (41→None). Only `1` falls in Batch 4 scope (8
  suspended steps above); the other two suspend nothing here.

## Tests

Minimal-tree node --test: **60 pass / 0 fail** (12 Batch 1 cumulative
+ 13 Batch 2 cumulative + 20 Batch 3 cumulative + 15 Batch 4);
node --check fighter.js OK. Batch 1 + Batch 2 + Batch 3 CONTENT
assertions preserved verbatim — only counts (171→271) and extra-keys
assertions changed (burger test-evolution rule; Pantera's latent
break NOT copied). ONE exception, documented not hidden: Batch 3's
forward-scope guard asserted `2,1,4~4` and `4~3,H.1+2` had NO plan
because they were Batch 4 scope. Batch 4 is now filed, so those keys
DO have plans — the guard is retired in the Batch 3 cumulative test
(ZEN lines preserved verbatim) and the keys are asserted in the Batch
4 test (2,1,4~4 partial, 4~3,H.1+2 unmapped-all). Retiring the guard
is not a content change: every Batch 3 content assertion (its 87
keys, verified steps, flagships) is preserved verbatim.
Limitation (stated in PR body, not hidden): full 200-test suite
comparison NOT run (no full current-main checkout on this box) — CI
must cover before merge.

## Per-string step rows (canonicals; twins inherit verbatim)

- `1+4,2` [standing] -> partial: 1+4=unmapped | 2=row 186
- `1+4,2,1` [standing] -> partial: 1+4=unmapped | 2=row 186 | 1=unmapped
- `1+4,2,1,4` [standing] -> partial: 1+4=unmapped | 2=row 186 | 1=unmapped | 4=review
- `1+4,2,4` [standing] -> partial: 1+4=unmapped | 2=row 186 | 4=unmapped
- `1+4,2,d+4` [standing] -> partial: 1+4=unmapped | 2=row 186 | d+4=unmapped
- `1,2,3` [standing] -> unmapped-all: 1=unmapped | 2=unmapped | 3=unmapped
- `1,2,3,4` [standing] -> unmapped-all: 1=unmapped | 2=unmapped | 3=unmapped | 4=unmapped
- `1,2,4` [standing] -> unmapped-all: 1=unmapped | 2=unmapped | 4=unmapped
- `1,3,2` [standing] -> unmapped-all: 1=unmapped | 3=unmapped | 2=unmapped
- `1,3,2,1` [standing] -> unmapped-all: 1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped
- `1,3,2,1,4` [standing] -> unmapped-all: 1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 4=unmapped
- `1,3,4` [standing] -> unmapped-all: 1=unmapped | 3=unmapped | 4=unmapped
- `1,d+3,d+4` [standing] -> unmapped-all: 1=unmapped | d+3=unmapped | d+4=unmapped
- `2,1,2,2,3` [standing] -> verified-all: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224
- `2,1,2,2,3,4` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review
- `2,1,2,2,3,4,4` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226
- `2,1,2,2,3,4,4,1` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226 | 1=row 227
- `2,1,2,2,3,4,4,1,2` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226 | 1=row 227 | 2=row 228
- `2,1,2,2,3,4,4,1,2,1` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226 | 1=row 227 | 2=row 228 | 1=unmapped
- `2,1,2,2,3,4,4,3` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226 | 3=row 237
- `2,1,2,2,3,4,4,3,2` [standing] -> partial: 2=row 220 | 1=row 221 | 2=row 222 | 2=row 223 | 3=row 224 | 4=review | 4=row 226 | 3=row 237 | 2=row 238
- `2,1,4` [standing] -> verified-all: 2=row 220 | 1=row 221 | 4=row 230
- `2,1,4,4` [standing] -> verified-all: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114
- `2,1,4,4,2` [standing] -> verified-all: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114 | 2=row 232
- `2,1,4,4,2,4` [standing] -> verified-all: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114 | 2=row 232 | 4=row 233
- `2,1,4,4,2,4,3` [standing] -> partial: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114 | 2=row 232 | 4=row 233 | 3=review
- `2,1,4,4,2,4,3,2` [standing] -> partial: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114 | 2=row 232 | 4=row 233 | 3=review | 2=review
- `2,1,4,4,2,4,3,2,1` [standing] -> partial: 2=row 220 | 1=row 221 | 4=row 230 | 4=row 114 | 2=row 232 | 4=row 233 | 3=review | 2=review | 1=unmapped
- `2,1,4__main` [standing] -> partial: 2=row 220 | 1=row 221 | 4__main=unmapped
- `2,1,4~4` [standing] -> partial: 2=row 220 | 1=row 221 | 4~4=unmapped
- `3,1,2` [standing] -> partial: 3=row 195 | 1=unmapped | 2=unmapped
- `3,1,4` [standing] -> partial: 3=row 195 | 1=unmapped | 4=unmapped
- `3,2,4,3,1+4,1,2,1,2` [standing] -> partial: 3=row 195 | 2=unmapped | 4=unmapped | 3=unmapped | 1+4=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped
- `4,1,2` [standing] -> partial: 4=review | 1=unmapped | 2=row 186
- `4~3,H.1+2` [standing] -> unmapped-all: 4~3=unmapped | H.1+2=unmapped
- `FLY.4,2,1` [standing] -> unmapped-all: FLY.4=unmapped | 2=unmapped | 1=unmapped
- `FLY.4,2,1+2` [standing] -> unmapped-all: FLY.4=unmapped | 2=unmapped | 1+2=unmapped
- `H.2+3,4` [standing] -> unmapped-all: H.2+3=unmapped | 4=unmapped
- `MCR.4,2,1` [standing] -> unmapped-all: MCR.4=unmapped | 2=unmapped | 1=unmapped
- `MCR.4,2,1+2` [standing] -> unmapped-all: MCR.4=unmapped | 2=unmapped | 1+2=unmapped
- `WS.1,3,2` [ws] -> unmapped-all: WS.1=unmapped | 3=unmapped | 2=unmapped
- `WS.1,3,2,1` [ws] -> unmapped-all: WS.1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped
- `WS.1,3,2,1,4` [ws] -> unmapped-all: WS.1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 4=unmapped
- `WS.1,3,2,1,4,2` [ws] -> unmapped-all: WS.1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 4=unmapped | 2=unmapped
- `b+1+2,2,3` [standing] -> partial: b+1+2=unmapped | 2=row 94 | 3=row 196
- `b+1+2,2,3,4` [standing] -> partial: b+1+2=unmapped | 2=row 94 | 3=row 196 | 4=review
- `b+1+2,2,3,f+4` [standing] -> partial: b+1+2=unmapped | 2=row 94 | 3=row 196 | f+4=review
- `b+2,4,2,1` [standing] -> partial: b+2=unmapped | 4=row 251 | 2=row 252 | 1=review
- `b+2,4,4,1+2+3` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 1+2+3=unmapped
- `b+2,4,4,4,4,2,1+4` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 4=unmapped | 4=review | 2=row 258 | 1+4=row 259
- `b+2,4,4,4,4,2,1+4,1` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 4=unmapped | 4=review | 2=row 258 | 1+4=row 259 | 1=unmapped
- `b+2,4,4,4,4,2,1+4,1,2` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 4=unmapped | 4=review | 2=row 258 | 1+4=row 259 | 1=unmapped | 2=review
- `b+2,4,4,4,4,2,1+4,1,2,1` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 4=unmapped | 4=review | 2=row 258 | 1+4=row 259 | 1=unmapped | 2=review | 1=unmapped
- `b+2,4,4,4,4,2,1+4,1,2,3+4` [standing] -> partial: b+2=unmapped | 4=row 251 | 4=unmapped | 4=unmapped | 4=review | 2=row 258 | 1+4=row 259 | 1=unmapped | 2=review | 3+4=unmapped
- `b+3+4,2` [standing] -> partial: b+3+4=unmapped | 2=row 239
- `b+3+4,2,1` [standing] -> partial: b+3+4=unmapped | 2=row 239 | 1=unmapped
- `b+3+4,2,1,4` [standing] -> partial: b+3+4=unmapped | 2=row 239 | 1=unmapped | 4=review
- `d+3+4,1` [crouch] -> unmapped-all: d+3+4=unmapped | 1=unmapped
- `d/f+3,2,4` [crouch] -> unmapped-all: d/f+3=unmapped | 2=unmapped | 4=unmapped
- `f+2,3,3,3,2,1,2,3,4,2` [standing] -> partial: f+2=row 103 | 3=unmapped | 3=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 2=unmapped | 3=unmapped | 4=unmapped | 2=unmapped
- `u+1,2+4` [jump] -> partial: u+1=unmapped | 2+4=row 170
- `u/b+1,2+4` [jump] -> partial: u/b+1=unmapped | 2+4=row 172
- `u/f+1,2+4` [jump] -> unmapped-all: u/f+1=unmapped | 2+4=unmapped
- `u/f+2+4,1` [jump] -> unmapped-all: u/f+2+4=unmapped | 1=unmapped
- `ws1,3,2` [standing] -> unmapped-all: ws1=unmapped | 3=unmapped | 2=unmapped
- `ws1,3,2,1` [standing] -> unmapped-all: ws1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped
- `ws1,3,2,1,4` [standing] -> unmapped-all: ws1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 4=unmapped
- `ws1,3,2,1,4,2` [standing] -> unmapped-all: ws1=unmapped | 3=unmapped | 2=unmapped | 1=unmapped | 4=unmapped | 2=unmapped

## Play-verify checklist (parent browser delegation, after #1096 + #1108 + #1110 + #1111 + this PR merge + deploy + sync, phone portrait)

- `2,1,4`: rows 220/221/230, all grounded, verified-all; old
  whole-string donors must NOT appear as whole-string clips.
- `2,1,4,4`: rows 220/221/230/114 — step 4 plays row 114 (single
  RK4), NOT the chord row 231 (LK3+RK4) the string used to resolve to.
- `2,1,4,4,2,4`: rows 220/221/230/114/232/233, verified-all.
- `2,1,2,2,3`: rows 220/221/222/223/224, verified-all.
- `2,1,4__main`: rows 220/221, last step NO row (NOT row 230 — the
  __main duplicate does not inherit plain 2,1,4's last step).
- `2,1,4~4`: rows 220/221, last step NO row (cancel step has no T3 row).
- `4~3,H.1+2`: NO row any step (quarantined-only; per plan ONLY after
  #988 merges).
- `1,2,3` family step 1: NO row (suspended — stale row 41 must NOT play).
- `u+1,2+4` / `u/b+1,2+4`: step 1 NO row, last step rows 170/172
  (airborne chord enders).
- `u/f+3+4,H.1+2`: NO plan (throw class) — unchanged behavior.
- Rest keys unchanged: `f,F+2`, `f,f,n,2`, `WALL.b,b,u/b`, `uf,n,4`
  behave as before (donor clips, NOT per plan).
- No Batch 4 step plays row 35 or row 216; no Batch 4 step plays a
  jumping row for a ground step.
- Demonio Batches 1–3 spot-checks undisturbed: `2,1` family 220/221,
  `d+1+2,2` 92/93, `u+1,1` step 2 row 35 jump-only, `1,1` step 1 still
  suspended, `u+4,4` 79/209, `u/f+4,3` 80/193, `u/f+4,4` 80/207,
  `d/f+4,4` step 1 row 205 / step 2 UNMAPPED, `2,4` step 1 row 220 /
  step 2 UNMAPPED, `3,1` step 1 row 195 / step 2 UNMAPPED, `b+2,4`
  family RK4 step row 251, `u/f+4,4,1` steps 80/207/None.

## Workspace

- CSV (214 rows): demonio_batch4_triples_quads_rest.csv
- Step table (677 steps): demonio_batch4_step_table.json
- Universe (164 canonicals): demonio_batch4_universe.json
- Plans (100 keys): demonio_batch4_plans.json
- Wired demonio.json (271 plans): pr/demonio.json
- Tests: test-b4.mjs (new), test-b1-cumulative.mjs,
  test-b2-cumulative.mjs, test-b3-cumulative.mjs (cumulative updates)
- Audit append: pr/PROCEDURAL_AUDIT.md (append-only)
