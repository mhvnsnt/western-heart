# Demonio Batch 3 step plans — mixed-pair strings (2026-10-25)

Batch 3 of the locked batch order for Demonio (Jin / Devil Jin base):
Batch 1 LP1/RP2-only (PR #1108) → Batch 2 LK3/RK4-only (PR #1110) →
**Batch 3 mixed pairs (this PR)** → Batch 4 triples/quads/rest.

Scope: Demonio strings whose button SET is exactly one punch + one kick
pair — {LP1,LK3}, {LP1,RK4}, {RP2,LK3}, {RP2,RK4} — any directionals,
any contexts (standing/crouch/jump/ws). Measured, not assumed:
**49 canonicals** (47 pure single-button, 2 chord-involved: `1+4,1` and
`1+4,b+1`, whose first step is the LP1+RK4 chord). Pair split: {LP1,LK3}
15, {LP1,RK4} 15, {RP2,RK4} 12, {RP2,LK3} 7. Contexts: standing 28,
crouch 11, jump 7, ws 3. In main moves: 38; quarantined-only: 11
(`CD.DF+4,2`, `FLY.4,1`, `FLY.4,2`, `MCR.4,1`, `MCR.4,2`, `WS.1,3~3`,
`ZEN.1,3`, `b+3,2`, `df+1,4~4`, `df+2,4`, `ws1,3~3`); in-#1096-only: 0.
Throw-class canonicals get NO plan (CSV-audited only); Batch 3 has one
CSV-only key: `ZEN.1,3` (see below).

## Stack

- Base: demonio Batch 2 branch `feat/demonio-batch2-step-plans-20261025`
  (PR #1110, head 373ab858932a9248eb679d31264046b3e113d87f), NOT #1096
  directly and NOT any Pantera or burger plan branch. Plans accumulate:
  84 Batch 1+2 keys + 87 Batch 3 keys = 171.
- Merges AFTER #1110 (which merges after #1108, after #1096, itself
  blocked on 12 pre-existing failures / a gate decision owed — this lane
  does not fix those and does not merge on mergeable:true alone).
- This PR does not touch `fighter.js`, `pantera.json`, or `burger.json`.
- The audit append (`docs/anim/PROCEDURAL_AUDIT.md`) is append-only; if
  the Pantera or burger stacks or demonio Batches 1–2 merge first, the
  audit append rebases after their entries (never overwrites them). If
  #1097 merges first, note its guard-map interaction (demonio has its own
  guard map; Pantera's SOFT decision does not transfer).
- No T8 content touched: `t8_quarantine_20261024` untouched, no
  `UNMAPPED:t7-clip-pending` markers stripped.

## Bank (verified, carried forward — not re-litigated)

Demonio's T3 bank is JIN: `demonio.json` `t3_source: 'jin'`,
`t3_bank: 'moveset_jin.json'` on both #1096 and main; `t3/` contains a
jin dir; Job 1 = 220 jin rows, Job 2 = 764 demonio entries bank jin,
Job 4 = 47 jin candidates. Bank blobs re-verified this lane via the
GitHub API: main jin `hit_frames.json` blob
`54b38e63…` IDENTICAL to the Batch 1 baseline; main `demonio.json` blob
`e938e8d5…` unchanged since Batch 1. Cited-row profiles MATCH Job 1 vs
hit_frames on button/throw/active/hit for all 19 verified rows + 3 review
rows (gap-1 method, replicated).

Jin-bank row rules (Batch 1's documented correction, per-bank evidence,
never a cross-bank blanket ban):

- Jin row 220 is a STANDING RP2 row (hit_frames [12,12,41,1042,0,2],
  Job 1 stance standing, travel 0.216) — NOT king's jumping chord row or
  bryan's button-0 row — so it is NOT blanket-banned; it is
  gate-adjudicated per step like any row. **Batch 3 exercises the rule:
  `2,4` step 1 (standing RP2 step) verifies on row 220.**
- Jin row 35 IS starts-airborne, so the row-35 rejection for ground steps
  stands, and row 35 verifies ONLY in jump context. **No Batch 3 step
  uses row 35 at all.**
- Jin row 216 is a JUMP row (Job 1: y0 1.091, ymax 1.529 vs standingY
  1.027) — NOT king row 216 (dash Konvict Kick). The `1+4,b+1` last-step
  candidate 216 is rejected on button 0 AND on airborne stance for a
  ground step. Bank-specific evidence, never a cross-bank assumption.

## Canonicalization (corrected rule, carried from Batch 2 — not re-litigated)

Only a trailing source-variant suffix `~t[378]\.[a-z]+(\.\d+)?$` is
stripped. A `~` inside the input is Tekken cancel notation, part of the
move. This lane verifies the six strings the Batch 2 finding named as
Batch 3 scope — all six are OWN canonicals here, none forced, none
misfiled:

| Key | Buttons | Batch 3 pair | Status |
|---|---|---|---|
| `1,3~3` | {1},{3} | {LP1,LK3} | own canonical, unmapped-all |
| `1,3~3,d/f+3` | {1},{3},{3} | {LP1,LK3} | own canonical, unmapped-all |
| `WS.1,3~3` | {1},{3} | {LP1,LK3} | own canonical, unmapped-all |
| `ws1,3~3` | {1},{3} | {LP1,LK3} | own canonical, unmapped-all |
| `d/f+1,4~4` | {1},{4} | {LP1,RK4} | own canonical, unmapped-all |
| `df+1,4~4` | {1},{4} | {LP1,RK4} | own canonical, unmapped-all |

Batch 4 carry-forwards are correctly excluded: `2,1,4~4` (union
{1,2,4}) and `4~3,H.1+2` (union {1,2,3,4}) have NO Batch 3 plan key.
Demonio Batch 1 is provably unaffected by the old rule (no input-`~` key
old-canonicalizes into Batch 1's universe); Batch 1's plans stand.

## Tallies

- 49 canonicals = 48 planned + 1 CSV-only (`ZEN.1,3`).
- 87 plan keys = 48 planned canonicals + 39 twins. 90 CSV rows
  (49 canonicals + 41 variants).
- 113 steps total = 111 planned-string steps + 2 CSV-only steps.
- Planned steps: **19 verified / 3 review / 89 unmapped**
  (5 suspended-drift + 22 rejected-candidate + 62 no-candidate).
- Plan-key last-step: 27 verified / 1 review / 59 unmapped.
- Canonical string_status: 17 partial / 31 unmapped-all / 0 verified-all
  / 0 review-only. No canonical verifies all the way through: every
  verified canonical still has an unmapped first step (a T8-sourced
  prefix with no T3 row) or an unmapped last step.
- Suspended-drift steps: 5 (all step-1 prefix `1` — see below).
- Job 3 fills: 0. Job 4 joins: 12, none promoting. Orphans: 2
  (jin rows 85, 91 — same set as Batches 1–2).

## Every wired fill (verified only; jin hit_frames button == step bits, throw 0; T3 FALLBACK logged in the audit)

- `2,4` step 1 (RP2): row 220, prefix-move. Standing RP2 row for a
  standing RP2 step. hit_frames [12,12,41,1042,0,2]. SOFT passed outright
  (no waiver, no gate-note case).
- `3,1` step 1 (LK3): row 195, prefix-move. hit_frames [19,23,61,535,0,4].
  SOFT passed outright. (Job 3 ROW-ONLY rows 92/105 for this prefix are
  documented, not wired — the own row is stronger file evidence.)
- `b+2,4` family RK4 step (prefix `b+2,4`): row 251, prefix-move, in six
  strings (`b+2,4`, `b+2,4,2`, `b+2,4,4`, `b+2,4,4,4`,
  `b+2,4,4,4,4`, `b+2,4,4,4,4,2`).
  hit_frames [22,24,65,1042,0,8]. SOFT passed outright.
- `b+2,4,2` last step (RP2, prefix `b+2,4,2`): row 252, prefix-move.
  hit_frames [10,12,49,535,0,2]. SOFT passed outright.
- `b+2,4,4,4,4,2` last step (RP2, prefix `b+2,4,4,4,4,2`): row 258,
  prefix-move. hit_frames [22,23,55,535,0,2]. SOFT passed outright.
- `f+2,4` step 1 (RP2, prefix `f+2`): row 103, prefix-move. hit_frames
  [17,18,46,535,0,2]. SOFT passed outright.
- Jump lasts (SOFT waived per Batch 1 jump precedent — FK systematically
  silent on jumping rows; waiver noted in each step's reasons):
  `u+1,3` last step row 54 [9,9,52,535,0,4]; `u+1,4` last step row 67
  [8,9,46,535,0,8]; `u/b+1,3` last step row 56 [9,9,52,535,0,4];
  `u/b+1,4` last step row 69 [8,9,46,535,0,8]; `u/f+1,3` last step row 55
  [9,9,52,535,0,4]; `u/f+1,4` last step row 68 [8,9,46,535,0,8].
- `u/f+4,4,1` steps 1–2: rows 80/207 (same rows as Batch 2's `u/f+4,4`,
  jump context, SOFT waived). hit_frames 80 [25,25,66,535,0,8],
  207 [47,47,86,271,0,8].

No Batch 3 verified step uses row 35. No Batch 3 verified step is a
standing row for a crouch-context step (no Batch 1 gate-note case).
No Batch 3 verified step carries a soft flag.

## Every rejected / held candidate (row null, never played)

Review (3):

- `4,1` step 1, candidate 199 (recorded path, jin standing row):
  SOFT limb-peak proxy fail, window [3.5,7.5], legR peak 3 (just
  outside the window — fail is fail under the conservative rule).
- `b+2,4,4,4,4` step 5 and `b+2,4,4,4,4,2` step 5, candidate 257
  (prefix-move, jin duck-dip row): STANCE-SOFT for standing-context
  steps (duck-dip handled like crouch: review, never false verify).

Rejected own/recorded candidates (22 unmapped steps carry one):

- `u/f+4,4,1` last step (LP1), candidate 208 (prefix-move): button 0,
  throw flag 1 — the key's own row is a THROW row, not a strike row for
  the LP1 step. Never wired.
- `1+4,1` last step (LP1), candidate 185 (prefix-move): button 0.
- `1+4,b+1` last step (LP1), candidate 216 (prefix-move): button 0 AND
  jin jump row for a ground step (see the jin-216 note above).
- `4,1` last step (LP1), candidate 184 (recorded path): button 9
  (LP1+RK4 chord row) for a single-LP1 step.
- `1,4` last step (RK4), `d/f+1,4` last step (RK4), `df+1,4` last step
  (RK4), candidates 204 (recorded path/dest): airborne jin jump rows
  for ground steps.
- `b+2,4,4` / `b+2,4,4,4` / `b+2,4,4,4,4` / `b+2,4,4,4,4,2` later RK4
  steps, candidates 254/256 (prefix-move): airborne jin jump rows for
  ground steps.
- `d/f+1,3` / `d/f+1,4` / `d/f+1,4~4` first step (RP2), candidate 179
  (prefix-move), and `d/f+1,3` last step candidate 197 (recorded dest):
  airborne jin jump rows for ground steps.
- `u/b+1,3` / `u/b+1,4` first step (LP1), candidate 34 (prefix-move):
  button 3 (LK3 row) for an LP1 step. `u/f+1,3` / `u/f+1,4` first step
  (LP1), candidate 33 (prefix-move): button 3 for an LP1 step. The jump
  LP1 prefixes' own rows are kick rows — correctly rejected, which is
  why every jump-family string here is partial (last step verified,
  first step unmapped).

Suspended (5): the five step-1 prefixes `1` — `1,3`, `1,3~3`,
`1,3~3,d/f+3`, `1,4`, `1,d+3` — prefix move `1` is ROW-CHANGED 41→None
(base vs current main). Stale row 41 documented, never wired (jin row 41
is starts-airborne, so wiring it would play a jumping clip for ground
strings). The other two row-changed moves (`1_r41`, `u+1,1~t3.jin.2`)
do not fall in Batch 3 scope.

Unmapped with NO candidate (62 planned steps + 2 CSV-only steps): every
such step's reason is "no candidate row (recorded path + prefix move
both absent)". All intermediate prefixes are T8-sourced with no T3 row;
correct clips come from #988 Step 2 or future extraction, never from a
T3 row recorded as correct.

## Job 3 (fills: 0 — the stricter rule is carried but not exercised)

8 report entries, all candidates documented, none wired:

- `1,3` / `1,3~3` / `1,3~3,d/f+3` / `1,4` / `1,d+3` step 1 (prefix `1`):
  rows 92/105, exact level but ROW-ONLY provenance — never wired
  (FULL provenance required). These steps are suspended anyway.
- `1,3` last step (prefix `1,3`): row 101, exact + ROW-ONLY — not wired.
- `3,1` step 1 (prefix `3`): rows 92/105, exact + ROW-ONLY — not wired;
  the gate-verified own row 195 stands.
- `2,4` last step (prefix `2,4`): row 138, soft-filed + FULL — soft is
  never wired, even with FULL provenance.

Fill rule (burger refinement, stricter than Pantera Batch 4's HARD-only
fill rule): a Job 3 fill additionally requires the SOFT proxy to pass.
No Batch 3 candidate reaches that check (all fail exact+FULL first).
No SOFT fill is inherited from #1097 (Pantera-specific, still
unapproved, does not transfer to demonio). Dedupe: prefix vs `__main`
duplicate pass-all rows deduped per the burger Batch 2 cleanup (no
`__main` duplicates among Batch 3 candidates).

## Job 4 (joins: 12, none promoting — corrected join only)

Corrected join only (demonio-only, BANK_DIR jin, join iff Job 2 has a
demonio entry key == step prefix, row == candidate row, step == own).
The naive cross-fighter join on key-prefix equality is INVALID and was
not used. A join NEVER promotes a candidate by itself.

- 1 no-action: `u/f+4,4,1` step 2 row 207 (already verified).
- 11 rejected: `1+4,b+1` last step row 216 (button 0 + airborne);
  `1,4` last step row 204 (airborne); `b+2,4,4,4` / `b+2,4,4,4,4` /
  `b+2,4,4,4,4,2` later steps row 256 (airborne); `d/f+1,3` first step
  row 179 + last step row 197 (airborne); `d/f+1,4` first step row 179
  + last step row 204 (airborne); `d/f+1,4~4` first step row 179
  (airborne); `u/f+4,4,1` last step row 208 (button 0 + throw flag 1).
- Orphans: 2 (jin rows 85, 91 — same set as Batches 1–2).

## CSV-only key

`ZEN.1,3` (throw class in the base file; quarantined-only on main) gets
NO plan, and neither do its twins `ZEN.1,3~t7.jin` /
`ZEN.1,3~t7.jin.2` — the twins carry `string` labels, but they inherit
the throw canonical's steps verbatim, and wiring strike step-plans for a
throw family's steps would be wrong. The label inconsistency is recorded
here, not resolved by wiring. (Batch 1 precedent: TACKLE family + `b+2,1:u/f`
are CSV-only the same way.)

## Drift census (base = Batch 2 branch file vs current main, moves-dict)

Both counts, both true under their definitions (never silently pick one):

- By row/anim_ref status: 517 same / 164 damage-only / 80 anim_ref-changed
  / 3 ROW-CHANGED (`1`, `1_r41`, `u+1,1~t3.jin.2`, all 41→None) —
  IDENTICAL to the Batch 2 census (the base file's moves are #1096's
  moves, unchanged by Batches 1–2, which only add plans).
- Damage differs on 195 moves = 194 unchanged-row + 1 row-changed
  (move `1`, 11→7). Damage-only drift does NOT suspend (damage ≠
  animation); changed moves SUSPENDED (the 5 Batch 3 steps above).

## Tests

Minimal-tree `node --test`: 44 pass / 0 fail (12 Batch 1 cumulative +
13 Batch 2 cumulative + 19 Batch 3). `node --check fighter.js` OK.
Batch 1 + Batch 2 CONTENT assertions preserved verbatim — only the
counts (84→171) and extra-keys assertions changed (burger test-evolution
rule; Pantera's latent break NOT copied). Batch 3 test asserts all 87
keys, the 27 verified-last-step keys, the single review-last-step key
(`b+2,4,4,4,4`), every flagship above, the ZEN throw family + Batch 4
carry-forwards having no plan, and the fighter.js step-plan markers.

Limitation (stated in the PR body, not hidden): the full 200-test suite
comparison was NOT run (no full current-main checkout on this box) —
CI must cover before merge. NO lane play-verified anything; playing is
the parent's step after merge + deploy.

## Per-string step rows (canonicals; twins inherit verbatim)

- `1+4,1` [unmapped-all]: 1+4=unmapped | 1=unmapped (cand 185 rejected, button 0)
- `1+4,b+1` [unmapped-all]: 1+4=unmapped | b+1=unmapped (cand 216 rejected, button 0 + jump row)
- `1,3` [unmapped-all]: 1=unmapped (SUSPENDED, stale 41) | 3=unmapped
- `1,3~3` [unmapped-all]: 1=unmapped (SUSPENDED, stale 41) | 3~3=unmapped
- `1,3~3,d/f+3` [unmapped-all]: 1=unmapped (SUSPENDED, stale 41) | 3~3=unmapped | d/f+3=unmapped
- `1,4` [unmapped-all]: 1=unmapped (SUSPENDED, stale 41) | 4=unmapped (cand 204 rejected, jump row)
- `1,d+3` [unmapped-all]: 1=unmapped (SUSPENDED, stale 41) | d+3=unmapped
- `2,4` [partial]: 2=row 220 | 4=unmapped
- `3,1` [partial]: 3=row 195 | 1=unmapped
- `4,1` [partial]: 4=review (cand 199, SOFT fail) | 1=unmapped (cand 184 rejected, button 9)
- `CD.DF+4,2` [unmapped-all]: CD.DF+4=unmapped | 2=unmapped
- `FLY.4,1` [unmapped-all]: FLY.4=unmapped | 1=unmapped
- `FLY.4,2` [unmapped-all]: FLY.4=unmapped | 2=unmapped
- `MCR.4,1` [unmapped-all]: MCR.4=unmapped | 1=unmapped
- `MCR.4,2` [unmapped-all]: MCR.4=unmapped | 2=unmapped
- `WS.1,3` [unmapped-all]: WS.1=unmapped | 3=unmapped
- `WS.1,3~3` [unmapped-all]: WS.1=unmapped | 3~3=unmapped
- `WS.1,4` [unmapped-all]: WS.1=unmapped | 4=unmapped
- `ZEN.1,3` [CSV-ONLY, throw]: no plan
- `b+2,3` [unmapped-all]: b+2=unmapped | 3=unmapped
- `b+2,4` [partial]: b+2=unmapped | 4=row 251
- `b+2,4,2` [partial]: b+2=unmapped | 4=row 251 | 2=row 252
- `b+2,4,4` [partial]: b+2=unmapped | 4=row 251 | 4=unmapped (cand 254 rejected, jump row)
- `b+2,4,4,4` [partial]: b+2=unmapped | 4=row 251 | 4=unmapped (cand 254 rejected) | 4=unmapped (cand 256 rejected, jump row)
- `b+2,4,4,4,4` [partial]: b+2=unmapped | 4=row 251 | 4=unmapped (cand 254) | 4=unmapped (cand 256) | 4=review (cand 257, STANCE-SOFT duck-dip)
- `b+2,4,4,4,4,2` [partial]: b+2=unmapped | 4=row 251 | 4=unmapped (cand 254) | 4=unmapped (cand 256) | 4=review (cand 257) | 2=row 258
- `b+3,2` [unmapped-all]: b+3=unmapped | 2=unmapped
- `d/b+2,2,3` [unmapped-all]: d/b+2=unmapped | 2=unmapped | 3=unmapped
- `d/b+2,3` [unmapped-all]: d/b+2=unmapped | 3=unmapped
- `d/f+1,3` [unmapped-all]: d/f+1=unmapped (cand 179 rejected, jump row) | 3=unmapped (cand 197 rejected, jump row)
- `d/f+1,4` [unmapped-all]: d/f+1=unmapped (cand 179 rejected) | 4=unmapped (cand 204 rejected, jump row)
- `d/f+1,4~4` [unmapped-all]: d/f+1=unmapped (cand 179 rejected) | 4~4=unmapped
- `d/f+3,2` [unmapped-all]: d/f+3=unmapped | 2=unmapped
- `db+2,2,3` [unmapped-all]: db+2=unmapped | 2=unmapped | 3=unmapped
- `db+2,3` [unmapped-all]: db+2=unmapped | 3=unmapped
- `df+1,4` [unmapped-all]: df+1=unmapped | 4=unmapped (cand 204 rejected, jump row)
- `df+1,4~4` [unmapped-all]: df+1=unmapped | 4~4=unmapped
- `df+2,4` [unmapped-all]: df+2=unmapped | 4=unmapped
- `f+2,4` [partial]: f+2=row 103 | 4=unmapped
- `f+3,1` [unmapped-all]: f+3=unmapped | 1=unmapped
- `u+1,3` [partial]: u+1=unmapped | 3=row 54 (SOFT waived, jump)
- `u+1,4` [partial]: u+1=unmapped | 4=row 67 (SOFT waived, jump)
- `u/b+1,3` [partial]: u/b+1=unmapped (cand 34 rejected, button 3) | 3=row 56 (SOFT waived, jump)
- `u/b+1,4` [partial]: u/b+1=unmapped (cand 34 rejected, button 3) | 4=row 69 (SOFT waived, jump)
- `u/f+1,3` [partial]: u/f+1=unmapped (cand 33 rejected, button 3) | 3=row 55 (SOFT waived, jump)
- `u/f+1,4` [partial]: u/f+1=unmapped (cand 33 rejected, button 3) | 4=row 68 (SOFT waived, jump)
- `u/f+4,4,1` [partial]: u/f+4=row 80 (SOFT waived, jump) | 4=row 207 (SOFT waived, jump) | 1=unmapped (cand 208 rejected, throw row)
- `ws1,3` [unmapped-all]: ws1=unmapped | 3=unmapped
- `ws1,3~3` [unmapped-all]: ws1=unmapped | 3~3=unmapped

## Play-verify checklist (parent browser delegation, after #1108 + #1110 + this PR merge + deploy + sync, phone portrait)

- `2,4`: step 1 plays jin row 220 (standing RP2, grounded — NOT a jump
  clip), step 2 UNMAPPED (no row 138 soft-filed clip).
- `3,1`: step 1 plays row 195 (grounded LK3), step 2 UNMAPPED (no rows
  92/105 ROW-ONLY clips).
- `b+2,4` family: RK4 step plays row 251 (grounded); `b+2,4,2` last step
  row 252; `b+2,4,4,4,4,2` last step row 258; later RK4 steps UNMAPPED
  (no jump rows 254/256, no duck-dip row 257 for standing steps).
- `f+2,4`: step 1 plays row 103 (grounded RP2), step 2 UNMAPPED.
- Jump family `u+1,3` / `u+1,4` / `u/b+1,3` / `u/b+1,4` / `u/f+1,3` /
  `u/f+1,4`: last steps play rows 54/67/56/69/55/68 (airborne, correct
  for jump strings); first steps UNMAPPED (no LK3 rows 33/34 for LP1
  steps).
- `u/f+4,4,1`: first two steps play rows 80/207 (jump, same as Batch 2
  `u/f+4,4`); last step UNMAPPED (no throw row 208 for an LP1 step).
- `4,1`: step 1 UNMAPPED (no row 199 on SOFT fail); `1,3` family step 1
  UNMAPPED (no stale row 41 jumping clip for ground strings).
- No Batch 3 step plays row 35 (ground or otherwise); no Batch 3 step
  plays a jumping row for a ground step.
- Demonio Batches 1–2 spot-checks undisturbed: `2,1` family 220/221,
  `d+1+2,2` 92/93, `u+1,1` step 2 row 35 jump-only, `1,1` step 1 still
  suspended, `u+4,4` 79/209, `u/f+4,3` 80/193, `u/f+4,4` 80/207,
  `d/f+4,4` step 1 row 205 / step 2 UNMAPPED.

## Workspace

`~/workspace/demonio-batch3/` (CSV, step table, universe, plans, wired
demonio.json (171 plans), Batch 3 test, Batch 1 + Batch 2 cumulative
tests, audit append).
