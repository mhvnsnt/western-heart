# Batch string fix — decision log (2026-10-24)

## User report
Longest combo doable was 1-2 (LP1,RP2). 3+ hit strings broke. Wrong animations on many moves.

## Root causes (found from repo files, not guessed)
1. **Timing too tight for touch (main bug).** String grace 200ms, continuation
   window 800ms. Phone taps are slower than stick inputs, so 3rd+ hits landed
   after the windows expired and fired as fresh singles instead of string steps.
   The user got 1-2 (two singles) instead of 1,2,1 (a string).
2. **Queued string hit dropped when recovery skipped.** Short moves can jump
   active->done in one tick; `_tickState` only fired `_queuedNext` during recovery,
   so the queued hit was lost on completion.
3. **Defensive shadow-strip (NOT the root cause).** `_pressV2` records clean
   notation (`p + input`), so `lastMove` is already clean in normal flow.
   But if any path ever records a `~shadow` key, continuation now also tries
   the stripped base, so chaining cannot break that way. Safety net, not fix.

## Fixes (engine level — benefits ALL characters, not Pantera-only)
- `game/js/fighter.js`: string grace 200 -> 500ms; `_queuedNext` fires on completion.
- `game/js/movesets.js`: `STRING_PENDING` 800 -> 1500ms; both `contOk` windows use it.
- `game/js/movesets.js` `continuation()` + `_pressV2`: also try stripped `~shadow`
  bases (defensive safety net; normal flow already records clean notation).

## What this does NOT fix (honest gaps)
- T7-only string animations (e.g. `'1,2,1'` Palm Strike Uppercut) have NO T3 row and
  only a T8 ref the game cannot play. They fire with correct damage but play fallback
  (donor/button/generic) animations until T7 extraction lands (Grok's box / live memory).
  Marked UNMAPPED in verification output, never presented as correct.
- Singles ('1' -> `'1~t8.king'`) DO get correct T3 animations via notation match
  (`byInput['1']` -> row 110), verified in `_attackRowIndex` logic.

## Verification
- `test/batch-strings.test.mjs`: timing constants, shadow-strip code presence,
  Pantera chains resolve to TRUE STRING keys (`'1,2'`, `'1,2,1'`, `'1,2,1,2+4'`),
  no string maps to a chord row, batch mapped fighters have moves + strings + LP1/RP2 display.
- Chain simulation (pre-PR): all 7 key Pantera chains resolve to string keys after fix
  (before fix they resolved to separate singles).

## Batch scope
Engine fixes apply to all characters using the same resolver/fighter (all 35 T7
characters, all 157 moveset files). Data conversion (MOD damage) was already batched
in PR #1000 + #1002. This PR does NOT rewrite moveset data — it fixes the engine
that reads it. Per-character canon extras, stances, and quirks remain per-character
lanes (PR #1016 stances, Zui mix, Zen base decision).
