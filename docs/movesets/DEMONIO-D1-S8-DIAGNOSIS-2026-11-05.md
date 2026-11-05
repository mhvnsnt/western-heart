# Demonio d+1 — S8 data diagnosis (2026-11-05)

Roster-100 Wave 1, lane S8. Question: the #1559 roster pass recorded
Demonio `d+1` as WRONG-throw-on-strike-input (a strike input producing
throw behavior, damage 21, throw seen). #1560 deliberately excluded
Demonio from its dead-d+1 repairs because his d+1 *fires* — the defect
is what it fires. This document answers, from Demonio's own data first:
what his data says d+1 is, what is actually bound, and where the
divergence entered. Base: main `108024c5` (after #1584).

## The data answer

**What d+1 is, per every source layer Demonio's file was built from:**

1. **T7 Jin frame data** (`docs/t7t8-reference/frame-data-t7/jin.json`):
   Jin `d+1` = "Corpse Thrust" — a mid **strike**, damage 24 [28],
   i21, on block −7, on hit KND. No throw property.
2. **T8 Jin frame data** (`docs/t7t8-reference/frame-data-t8-full/jin.json`):
   Jin `d+1` = "Corpse Thrust > Black Wing Flash" — target `m,t`,
   damage `21,10`, on block −13, notes "Transition to attack throw on
   standing hit." A blockable strike whose standing-hit follow-up is an
   attack throw — not a grab, not unblockable, no throw break.
3. **T3 Jin bank** (`teardown/tekken3/movesets/moveset_jin.json`, row
   188): strike, damage 21, active frames 21–23, throw flag 0, attack
   word 535. Row 188's `used_by` in `rows.pack.json` includes Demonio's
   forms. The bank's throw-flagged row the shipped binding points at
   instead (row 139) is a `common_anim` generic row, damage 0, throw
   flag 1, and its `used_by` does **not** include Demonio.

**What is actually bound (all four Demonio files):** `slots['d+1']`
points at the plain key `d+1`, whose move record is the T8-derived
entry — name "Black Wing Flash" (base / human / winged) or "Corpse
Thrust > Black Wing Flash" (ember) — reclassed as `move_class: throw`,
`isGrab: true`, `unblockable`, `throw_break: "1"`. None of those four
properties exist in either source dataset for this move.

**His own strike record sits unslotted beside it in every file:**
`moves['d+1~t7.jin']` "Corpse Thrust" (base, ember, winged) and
`moves['d+1~donor.demonio']` "Corpse Thrust" (human, inherited from the
base file by merge) — `move_class: strike`, `anim_ref: t7:jin:jin_95`,
`anim_t3` Jin row 188, hit word 535. Exactly the T7 strike, exactly the
T3 bank row his forms are recorded as using.

## Where the divergence entered

- **2026-10-21 source merge** (commit `16e1057b`, "Moveset source
  merge: T8 + T7 + fixed T3"; `merge_sources` recorded in demonio.json):
  the merge fused the T8 and T7 Jin records, gave the T8 record the
  plain `d+1` key, and flattened its `m,t` target + "transition to
  attack throw on standing hit" into `move_class: throw` + `isGrab` +
  `unblockable` + `throw_break`. The T7 strike record survived only
  under the suffixed key `d+1~t7.jin`, bound to no slot.
- **2026-10-23 batch-4 pull** (`b339a7e5` / `4f72a251`, 658 → 764
  moves) and the **2026-10-23/24 anim-fix** (`fc60ef93`, `dc879294`)
  then stamped the throw-classed entry to T3 Jin row 139 with match
  note "true-map class-only (anim-fix 2026-10-23)" — cementing the
  wrong class into the animation layer. (Ember's copy carries row 117
  with an "approximate" match note; same class error, different stamp.)
- Because `game/js/movesets.js` `_prepare` builds the playable slot
  table from the file's `slots` first and only lets move keys fill
  *free* slots, the suffixed strike could never surface: the table
  wins, so `d+1` executed the throw record. This is the same slotting
  class S1 repaired (a correct record present in the fighter's own
  file, bound to no playable input / bound behind a wrong record).

Contrast: Vain Abel's `1+2` throw class is NOT-A-BUG (his DOA source
itself classes it a throw). Demonio's sources class d+1 a strike in
all three games (T3, T7, T8). The throw class here is a merge
artifact, not source data.

## The fix (same-class, his own data only)

One line per file — re-point `slots['d+1']` at the file's own Corpse
Thrust strike record. No fight datum is created, changed, or deleted;
the throw record stays in `moves` untouched (it remains the record of
the T8 attack-throw transition, see deviation 1).

| File | slots['d+1'] before | after |
|---|---|---|
| demonio.json | `d+1` (throw, dmg 24, row 139) | `d+1~t7.jin` (strike, dmg 24, row 188) |
| demonio-bloodline-ember.json | `d+1` (throw, dmg 17, row 117) | `d+1~t7.jin` (strike, dmg 14, row 188) |
| demonio-human.json | `d+1` (throw, dmg 31, row 139) | `d+1~donor.demonio` (strike, dmg 14, row 188) |
| demonio-winged.json | `d+1` (throw, dmg 31, row 139) | `d+1~t7.jin` (strike, dmg 14, row 188) |

## Proof

- **Engine trace** (real `game/js/movesets.js` at main `108024c5` in
  Node, `registerMoveset` → `resolveMoveKey`): before, d+1 resolves to
  the throw record in all four files; after, to the strike record.
  `docs/proof/2026-11-05/demonio-d1-s8/trace-verdicts-s8-20261105.json`.
- **Neighbour sweep**: 80 probed inputs (20 × 4 files) before/after —
  exactly 4 diffs, all of them the intended d+1 re-point. No BASICS or
  other slot changed.
- **Full-registry slot diff**: prepared `_slots` dumped for all 163
  moveset files before/after — exactly 4 slot changes in the whole
  registry, all Demonio d+1. Per-character isolation holds.
- **Browser fight probe** (Demonio vs Pantera, frozen AI, real
  keyboard input, 0.75 m spacing, defender HP sampled over a 4 s
  window): **before** — `d+1` fires "Black Wing Flash" (key `d+1`,
  hit word 2048, anim Jin row 139) and Pantera passes through
  `thrownExec`: a strike input executing a throw, 21 damage — the
  #1559 verdict reproduced. **After** — `d+1` fires Corpse Thrust
  (key `d+1~t7.jin`, hit word 535, anim Jin row 188), 21 damage (the
  bank row's own damage), defender never in a throw state. Neighbour
  `1` (Jab, 6.1) is identical in both runs; `1+3` resolves to the
  same Double Face Kick throw record in both (defender entered
  thrown/thrownExec in both; its damage registered 16.6 in the after
  run and had not landed inside the window in the before run — a
  throw-timing variance in the harness, not a data difference).
  `docs/proof/2026-11-05/demonio-d1-s8/fight-before/results.json`,
  `fight-after/results.json` (+ console logs).
- **Regression test**: `test/demonio-d1-s8.test.mjs` pins the strike
  resolution, the untouched throw record, and neighbour slots
  (9/9 pass locally).

Harness limitations, stated honestly: the fight probe stubs the
arena renderer under SwiftShader (software GL cannot draw the stage
at a usable rate in this container — the same limitation S1
recorded); the game logic, input path, and damage are the real
engine's. Per-case screenshots were dropped from the final proof:
forcing an arena render crashed the headless page on two of five
probe runs, so the shipped proof is the numeric engine trace
(results.json) rather than renders. One earlier probe run also hit a
one-off stage-floor-break event (a stage physics artifact unrelated
to moveset data); the quoted before/after runs are the clean pair
with no such event in their logs.

## Deviations

1. **The T8 attack-throw transition is not modeled.** In T8, Corpse
   Thrust transitions to the Black Wing Flash attack throw (+10) on
   standing hit. The engine has no strike→attack-throw transition
   mechanic, so after this fix d+1 is the plain strike in all four
   files. The T8-derived record remains in `moves` (unslotted) as the
   data of record for that transition; modeling the transition is an
   engine feature, not a data repair, and is out of S8 scope.
2. **Stale `specials[]` summaries left untouched.** `demonio.json` and
   `demonio-winged.json` carry a `specials[]` entry `{input: d+1,
   damage: 31, throw: true}` — a merge-era summary, not the execution
   path (execution resolves through `slots`/`moves`, proven by the
   trace). Documented here; not edited, per per-character data
   minimalism and because no consumer of `specials[]` was found in
   the press path.
3. **Ember's throw record carries a different anim stamp** (row 117,
   "approximate") than the other three files (row 139, "class-only").
   Noted as provenance variance in the same merge artifact; the fix
   does not depend on it and the record itself is untouched.
