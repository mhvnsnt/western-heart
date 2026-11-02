# Transfer: Fire Pro teardown -> Western Heart wrestling systems — 2026-11-02

Source of truth for this lane: `docs/handoffs/TOOLS-AUDIT-20261102.md`
(PR #1506, main `497b12f4`). Source docs read via the GitHub API:
`mhvnsnt/teardown-fire-pro` — README, TEARDOWN, TRANSFER-MAP, WIRING-PLAN.
The source game is named here only as docs provenance about pulling
its data. No source-game wrestler, promotion, part, move, logo or
music is in this PR, and no source-game character or promotion name
appears in any player-facing UI string in this PR.

## What this PR wires (code the game can actually read)

| Transfer | Wired here | How it is read |
|---|---|---|
| F1 CPU logic tables | `game/js/ai/cpu-logic-tables.js` (`validateCpuTable`, `resolveCpuPick`, `phaseOf`) | Position x damage-phase (small/medium/large/critical) percentage tables. Phase escalation is data-driven: the critical column's top pick in the example is the finisher. Complements `game/js/ai/cpu-personality.js`, which it does not modify. |
| F2 personality sliders | Same module (`validateSliders`, `normalizeSliders`) | Showmanship / Discretion / Flexibility / Ukemi, 0-100. Showmanship scales taunt weight; ukemi is returned as a reversal tendency for the caller. |
| F3 priority attacks | Same module (`validatePriorityChains`, `resolvePriority`) | Up to 10 chains, trigger -> follow-up with per-phase percentages. A 100% chain always follows up, a 0% chain never does (tested). |
| F5 moveset-by-position | Same module (`validateMovesetSlots`, `moveForSlot`) + example record | Standing, front/back grapple by class, ground at head/legs, corner, diving, running, counter, finisher slots. |
| F6 family ratings | Same module (`validateFamilyRatings`, `familyMultiplier`) | Paired offense/defense per move family (punch/kick/throw/joint/stretch/power/flying/agility/arm/body). |
| F7 stamina/spirit + part endurance | Same module (`createResources`, `applyResourceDelta`, `damagePart`) | Stamina (breath) and spirit as separate resources; per-part endurance with an exhausted state. Affinity grades scale stamina cost (WH tuning multipliers; the source docs grade the cost, not the numbers). |
| F8 traits | Same module (`validateTrait`) | One point-bought passive per fighter, trigger/effect shapes, cost validated 15-35. WH-authored trait names only. |
| F9 critical-spike event | Same module (`criticalChance`) | Caller-supplied base rate only (no base rate is documented, so none is invented); generic trait multipliers + low-stamina-reversal doubling, clamped to [0,1]. A rolled critical sets the opponent phase to `critical` via `phaseOf(..., true)`, which the F1 tables read. |
| F12 one-record fighter file | Same module (`validateFighterRecord`) + `game/data/wrestling-sim-example.json` | Profile / appearance / parameters / moveset / cpuLogic in one record, validated end to end. |
| Tests | `test/cpu-logic-tables.test.mjs` (15 assertions) | Run by the existing `game-checks` game-unit-tests job. Includes a deterministic CPU-vs-CPU sequence that escalates to the finisher — the shape `game/js/sim-match.js` consumes. |

## Explicitly NOT claimed here (still owed, with reasons)

- **Sim-mode presentation pass (F4): OWED.** `game/js/sim-match.js`
  already exists and is marked partial in SYSTEMS-COVERAGE; this PR
  gives it a resolver it can import, but does not rewrite it or add
  a watch-mode presentation pass. That is a follow-up PR, not claimed
  as done here.
- **Move Forge editor (F11): OWED, not-wired in SYSTEMS-COVERAGE.**
  This PR lands the move-assembly *data shape* (position-class slots
  + property flags via the slot table and trait shapes); the editor
  UI and preview are separate lane work.
- **Ring / entrance editing (F13): OWED.** Ring-as-data and entrance
  sequences ride the stage/match-flow seam in `game/js/stages.js`;
  not touched here.
- **Exact damage / reversal / critical base formulas: BLOCKED on
  owner files** (the source game's compiled logic assembly, on the
  owner's PC only, per the teardown README). Production tuning stands
  in, marked as WH tuning in the module header — never presented as
  extracted values.
- **Layered-parts scale in the creation suite (F10): OWED.** The
  example record carries per-part scale as data; wiring it into
  `game/js/customization-consumer.js` is creation-suite lane work.
- **No raw commercial files, no deploy.** This PR adds only
  `.js` / `.json` / `.md` files. No file is deleted or modified.

## A doc-only PR would not count here

This PR is not doc-only: the module above is imported and asserted
by `test/cpu-logic-tables.test.mjs`, and the example fighter record
is parsed and validated by that test. The doc in this file is the
transfer record, not the deliverable.
