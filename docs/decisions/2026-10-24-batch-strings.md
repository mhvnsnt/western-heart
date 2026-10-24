# Batch string fix — decision log (2026-10-24)

## User report
Longest combo doable was 1-2 (LP1,RP2). 3+ hit strings broke. Wrong animations on many moves.

## Root causes (found from repo files, not guessed)
1. **Shadow keys broke chaining (main bug).** `slots['1'] = '1~t8.king'` (MOD damage
   delivery) made `lastMove = '1~t8.king'` after a jab, so continuation tried
   `'1~t8.king,2'` (nonexistent) instead of `'1,2'`. The user got two separate jabs,
   never the Palm Strike string. Same for every single-button starter.
2. **Timing too tight for touch.** String grace 200ms, continuation window 800ms.
   Phone taps are slower than stick inputs.
3. **Queued string hit dropped when recovery skipped.** Short moves can jump
   active->done in one tick; `_tickState` only fired `_queuedNext` during recovery,
   so the queued hit was lost on completion.

## Fixes (engine level — benefits ALL characters, not Pantera-only)
- `game/js/movesets.js` `continuation()`: try stripped base too (`'1~t8.king'` -> `'1'`).
- `game/js/movesets.js` `_pressV2`: stripped bases for `_strPath` and `lastMove`.
- `game/js/movesets.js`: `STRING_PENDING` 800 -> 1500ms; both `contOk` windows use it.
- `game/js/fighter.js`: string grace 200 -> 500ms; `_queuedNext` fires on completion.

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
