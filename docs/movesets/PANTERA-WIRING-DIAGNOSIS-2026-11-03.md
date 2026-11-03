# Pantera input→animation wiring diagnosis — 2026-11-03

Owner playtest report (2026-11-03): many of Pantera's animations still don't fire
correctly, many buttons aren't wired up, too many attacks fire GRAPPLE animations
mid-combo, he CANNOT make Pantera do a grapple on purpose, and a lot of attacks
are just wrong.

The prior probe (PR #1487, `docs/movesets/PANTERA-INPUT-COVERAGE-2026-11-01.md`)
counted whether an input FIRED a clip (227/238). This diagnosis checks clip
IDENTITY: for each input, the resolved move's class in Pantera's own data vs the
clip that actually plays (throw-flag from the bank's own decoded hit data) vs
whether a real throw execution occurs. Method: identity-gated stepped probe
(the game boots into a zen-vs-pantera attract fight first; every measurement
below waited for `p1.char.id === 'pantera'` in a real fight), full data audit
of `game/assets/movesets/pantera.json` against
`game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json`, and a full read of
the engine path (`game/js/fighter.js`, `input.js`, `movesets.js`,
`t3-conditions.js`, `game.js`). Line numbers cite pre-fix main.

## Root causes

### RC1 — `isGrab` was derived from throw-SITUATION branch codes (main cause of grapples on strike inputs)
`fighter.js:338` (`getRealMove`): `isGrab: !!mv.isGrab || mv.move_class === 'throw'
|| (mv.t3_condition >= 2 && mv.t3_condition <= 0x17)`. Conditions 2..0x17 are
throw-SITUATION codes (`t3-conditions.js` header: "2-0x13 throw situation,
0x14-0x17 situation pairs") — they mark the execution rows a CONNECTED grab
branches into by the victim's posture/side (`t3-conditions.js` `situation()`
even requires the attacker's own contact within 1.5 s). They do not mean the
move, as an attack, is a throw.
Counted from the movesets themselves: **955 moves repo-wide were grabs by this
term alone; every one is classed `strike` or `special` in its own data, zero
classed `throw`** (Pantera: 51 such moves, 31 strike / 20 special).
Probe proof (unfixed tree, fresh neutral inputs, opponent standing in range):
- `d/b+1` → resolved move `d/b+1_c10` (t3_condition 10), isGrab true, played
  throw row 488, opponent entered `thrownExec`, damage 0. A basic low strike
  executed a no-damage throw.
- `d/f+3+4,1` → isGrab true (condition 2), step row 247 (throw), `thrownExec`, 0.
- `1,1` (his basic two-jab string) is the move record `KING 1,1_c2`
  (move_class `strike`, t3_condition 2, row 584 — the step plan's own reasons
  record "throw flag 1 (row 584)").

### RC2 — the step-plan branch played verified rows with NO strike/throw class guard
The main clip tiers reject a candidate whose decoded type disagrees with the
move (`fits()`, fighter.js:1320-1332). The step-plan branch
(fighter.js:1245-1312) returned the verified step row unchecked. Verified steps
playing THROW rows for non-grab plans in Pantera's data: plan `b+1+2,1+2` step
`b+1+2` row 279; plan `1+3,1` step `1+3` row 127; plan `2+4,1` step `2+4` row
128; plan `1,1` step row 584; plan `f+2,1,1,…` step row 271.

### RC3 — `genericBankAction` was dead code, and its fallback bypassed its own class filter
Its only step-plan call site (fighter.js:1270-1271) read
`this._t3.clips[bank]` — but `this._t3.clips` IS the flat per-bank action map
(keys are action names, never the bank name), so the tier returned null for
every fighter since PR #1458, and unmapped steps actually presented through
`_ownButtonPlan`. Probe proof of the visible symptom: input `b+1+2,1+2`
(step plan unmapped) presented the `1+3` THROW-attempt clip row 127 for a
strike string, dealt 0 damage, opponent merely in hitstun. Inside the function,
the final fallback (`best || (grab ? 'grab' : …)`) also ignored the
`clipIsThrow` filter its own candidate list applies.

### RC4 — deliberate throws are unreachable at human two-finger timing on touch
`input.js`: `CHORD_WINDOW_MS = 50`, strict `<`, timestamp-based. Two thumbs
landing ≥50 ms apart emit two singles, never a chord; the first single starts
its strike at once (queue drains per frame, game.js:536). The fighter-level
chord upgrade (fighter.js:2147+) only rescues an already-EMITTED chord. Throws
are also the only core chords with no direct button (index.html shows direct
chord buttons only for 2+3 HEAT and 1+2 RAGE; the legacy P/K grab buttons are
`display:none`). Probe contrast: injected exactly, `tryAttack('1+3')` at idle
grapples and damages (23.5–24.8 in probe) — the throw itself works; the human
input path is what fails. Connect gates then stack on top (grab reach 1.7 m +
≈0.5 m lunge, 3-frame active window on the T8 throws, standing-posture-only
per `canBeHitBy`).

### RC5 — chain-throw capture (scoped, real but not an initiator)
While `state === 'throwing' | 'throwExec'`, EVERY button press routes to
`_throwChainPress` (fighter.js:2089), which resolves presses as chain-throw
continuations and swallows partials (`return true` on `_strPending`). It cannot
start from a normal attack state, but after any first throw connects, ordinary
combo mashing keeps re-firing grapple stages on the same victim — matching the
owner's "grapples keep firing mid-combo" once a throw has happened. PR #1536
did not change this code (it changed only the stance-audit tool); recorded here
so the record is straight. No change made: this is Tekken's chain-throw design;
the bug was throws STARTING from strikes (RC1–RC3).

### Checked and ruled out
- PR #1535/#1536 as causes: #1535 changed only `stance_after` in 19 movesets
  (pantera.json not among them); #1536 changed only an audit tool.
- The 593 game-wide NO-ENTRY stance prefixes: they gate PREFIXED throws
  (`JGS.…`, `SIDE_L.…`), not neutral `1+3`/`2+4`. Not the neutral-throw cause.
- `_throwChainPress` as an initiator from strike states: unreachable there
  (RC5).

## Per-input audit (identity-gated probe, unfixed tree → verdict)

Full machine output: `docs/proof/2026-11-03/pantera-wiring/probe-before.json`.
Coverage baseline from PR #1487: 238 listed inputs, 227 fired / 11 bind-pose.

| input | resolved move (own data) | clip that played | verdict |
|---|---|---|---|
| 1 / 2 / 3 / 4 | strike | rows 110 / 99 / 264 / 216, strike | correct |
| 1+2 | strike | row 101 strike | correct |
| 1+3 | throw (slot→`1+3~t8.king`; before-fix run resolved the JGS variant) | row 127 throw, thrownExec, dmg ≈24 | correct as injected; unreachable at human timing (RC4) |
| 2+4 | throw (`2+4~t8.king`) | row 128 throw, thrownExec, **dmg 0** | executes, NO DAMAGE — anomaly A1 |
| 1+4 | throw (signature) | row 153 throw, thrownExec, dmg 0 | executes, no damage — anomaly A1 class |
| f+1+3 / f+2+4 | throw | donor rows 127 / 128, thrownExec, dmg 0 | executes, no damage — A1 |
| d/b+1+3 | throw, own row 277 | row 277, thrownExec, dmg 0 | executes, no damage — A1 |
| **d/b+1** | **strike input → `d/b+1_c10`, isGrab via RC1** | **row 488 THROW, thrownExec, dmg 0** | **WRONG — grapple on a strike input** |
| **d/f+3+4,1** | **isGrab via RC1 (cond 2)** | **step row 247 THROW, thrownExec** | **WRONG** |
| **d+1+3** | **no move record resolves (moveKey null)** | **donor row 275 THROW clip as a strike, dmg 43.3** | **WRONG — throw chord plays throw clip with strike mechanics** |
| b+1+3 / b+2+4 | no move record (null) | anim row 35 strike clip, strike dmg | WRONG — throw chords play a jab clip |
| **b+1+2,1+2** | strike string, step plan unmapped | **own-button fallback presented row 127 (1+3 throw attempt), dmg 0** | **WRONG (RC3 path)** |
| 1+3,1 / 2+4,1 | chain-throw follow-ups registered as strings; own rows 415 / 417 are throw rows | step plan unmapped → own `1` clip row 110 | not a grapple as fresh input; only correct inside a throw (RC5 path). Data-model carry C1 |
| b,n,f+1+2,1 | strike string, own row 455 is a throw row | main-path `fits()` REJECTED row 455 (×3 in plan.rejected), donor row 110 played | correct outcome — proof the main-path guard works and the step-plan branch lacked it (RC2) |
| 1,2 / 2,1 / f+2,1 / 1+2,1 | strikes / step plans | strike rows | correct |
| f+2,1,1 | step plan unmapped | own `1` clip row 110 | presents; data gap (dead-slot list) |
| 3,2 / 3,2,2 | UNMAPPED step plans (console-logged) | notation row 264 (the `3`) | presents first hit only — wrong-ish, data gap |

Data-audit counts (pantera.json × king hit_frames): 44 strike-classed moves
carry a throw `t3_row`, but they are branch variants; only 3 are reachable from
slots: `1+3,1` (415), `2+4,1` (417), `b,n,f+1+2,1` (455). Throw-input
inventory: `1+3`/`2+4` slots point at the T8 King throws (isGrab, anim UNMAPPED
— they present via the T3 attempt rows 127/128); the T3 throw moves
(`1+3` r127 / `2+4` r128, isGrab) exist in the same file unslotted as slot
targets; `d+1+3`, `b+1+3`, `b+2+4` resolve to NO throw move at all.

## The fix (this PR, game/js/fighter.js only + tests)

1. `getRealMove`: isGrab no longer derives from `t3_condition`. A move is a
   grab only when its own data says so (`isGrab` flag or `move_class: 'throw'`).
   `t3Condition` still gates when a situation row may fire; situation
   executions stay reachable through the throw pair/branch system.
2. Step-plan branch: a verified step row whose decoded class contradicts the
   move is rejected like an unmapped step — logged, recorded in
   `plan.rejected`, presented via the generic/own-button fallback, never played.
3. `genericBankAction` call site reads the flat clips map (tier alive again),
   and the function's last-resort fallback now passes the same `clipIsThrow`
   class filter as its candidates (a throw with no class-matching generic
   returns null → own-button tier, instead of a strike-typed clip).
4. Two-finger chord rescue in `tryAttack`: a single-button press that lands in
   the first 0.14 s of a just-started single-button attack's startup (no hit
   yet), has NO string continuation and opens NO partial string, and completes
   a chord that exists in the fighter's own moveset, is re-resolved as that
   chord from the pre-attack state — the same rescue the emitted-chord upgrade
   performs. Real strings are never stolen (continuation/partial checks run
   first and return).

## After-fix probe (same identity-gated method, fixed tree)

`docs/proof/2026-11-03/pantera-wiring/probe-after-key.json`:
- `1,1`: grab false; step row 584 REJECTED ("step row 584 is a throw row");
  presents the bank's `light` generic; strike damage 19.8; no throw state.
- `d/b+1`: grab false; own row 488 rejected (throw row); strike row 38 plays;
  damage 23.5; no throw.
- `d/f+3+4,1`: grab false; step row 247 rejected; `medium` generic; damage 32.2.
- `1+3`: still a real grapple — row 127, `thrownExec`, damage 23.5.
- `2+4`: still executes (`thrownExec`) — damage anomaly A1 unchanged (below).

Unit tests: `test/pantera-wiring.test.mjs` (new, 5 tests) passes; existing
`test/attack-anim.test.mjs` (incl. the repo-wide "no strike plays a throw row
and no throw plays a strike row" invariant), `input-timing`, `t3-throw`,
`batch-strings`, `moveset-slot-hijack` pass against the fixed file.

## The 11 dead slots from the coverage doc — disposition

| slot | disposition |
|---|---|
| f+2,1,1 | presents via fallback (own/generic strike clip); step remains unmapped in his own data — DATA GAP carried |
| f+2,1,1,2 | same family — carried |
| 3+4,3,2+3 | FK-gate held (coverage doc) — carried, not a wiring bug |
| b+1+2,1+2 | PRESENTATION FIXED (no longer the 1+3 throw clip — class guard + generic filter); step still unmapped in data — carried as data gap |
| d+1,2 | no candidate row in his data — carried |
| d/b+1+2,3+4 | no step plan in his data — carried |
| 2+4,1 | chain-throw follow-up (rows 128/417 are the throw's own); fresh-input presentation is a strike fallback; correct path is inside a throw via `_throwChainPress` — carried as data-model item C1 |
| 1+3,1 | same as 2+4,1 (rows 127/415) — C1 |
| 10-hit combo A (f+2,1,1,… family) | FK-held steps + unmapped steps — carried |
| 10-hit combo B | no candidate rows for its steps — carried |
| WS+2,2 | stance-entry (WS) reachability class — carried with the NO-ENTRY remainder |

## Carried anomalies (NOT claimed fixed)

- **A1 — most throws deal 0 damage in probe conditions.** Against Zen (who has
  no T3 bank, so every throw takes the legacy lock path), `1+3` damages
  (≈24) but `2+4`, `1+4`, `f+1+3`, `f+2+4`, `d/b+1+3` execute the full throw
  with 0 damage, before and after this fix. Needs its own lane: trace
  `completeThrow` → `_throwSlamDamage` per resolved move (the resolved
  `2+4~t8.king` record vs the JGS/`1+3` records) and the paired path against a
  banked opponent.
- **C1 — chain-throw follow-ups registered as ordinary strings** (`1+3,1`,
  `2+4,1` and the tagged stage families). Correct treatment is a data/model
  decision (move_class or reachability), not an engine guess; left as-is.
- **Throw chords with no move at all** (`d+1+3`, `b+1+3`, `b+2+4` present
  donor/anim clips as strikes). His own T7/T8 data classes `b+1+3` "Arm Whip"
  and `b+2+4` "Spinning Heel Hold" as strikes, so strike mechanics may be
  intended; the presentation (a throw clip for `d+1+3`) is the defect a data
  lane should settle from his move list, not an engine change.
