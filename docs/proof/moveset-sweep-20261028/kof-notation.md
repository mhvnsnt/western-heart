# Notation + loadout reachability (ryuji-rock, ryuji, pantera JGS), 2026-10-29

## Root causes (game, game/js/movesets.js)
1. **Loadout motions were never performable.** The moveset editor's loadout can equip a move on any input. `_pressV2` and `_pressLegacy` only scanned `ms._motions`, which is built from the moveset's own keys. So a loadout slot like `qcf+3+4` (shatter), `hcb+1` (nejikomi) or `d/b,d/b+1+2` resolved correctly, but the buffer could not perform it, and the plain button fired instead. Fix: `motionsFor(fighterId, ms)` merges the loadout's motion notations.
2. **Loadout strings could not continue.** A string equipped through the loadout (Rush `1,1,1`) had no entries in `_strPrefixes`, so `1,1` never opened the string cursor. Fix: `strPrefixesHas()` adds the loadout's string prefixes at all three call sites.
3. **Named motions in the head.** `parseMotion` rejected `hcb,f+1`, `qcf,qcf+1` and `d/b,qcf,n,D/B+2+3`; it now expands the named motions.
4. **KOF / T7 list annotations** are now canonicalised to the input the buffer actually emits:
   - `far 1`, `1 (close)`, `1 (Rush)`, `hop u/f+1` → the bare input;
   - `… near`, `… downed`, `(grounded) d+3`, `(knife)`, `(guard)`, `(max)` → the input without the note;
   - `qcb+3 (hold)` → `qcb+3*`;
   - `(BT) 2` → `BT.2`;
   - `…, tap 1x3` → `…,1,1,1`;
   - pantera `JGS, 1` and `JGS* (3 spins), 1` → `JGS.1` (pressed from Jaguar Step).

The test parser (test/e2e/moveset-sweep.page.js) also accepts a named motion as its own step. The physical-input helper in test/input-determinism.test.mjs expands the same mid-string motions as the game.

## Result (same harness)
| fighter | before | after | fixed | regressed | juggles |
|---|---|---|---|---|---|
| ryuji-rock | 59/148 | 135/148 | 76 | 0 | 6 → 6 |
| ryuji | 63/146 | 134/146 | 71 | 0 | 6 → 6 |
| pantera | 598/903 | 675/903 | 77 | 0 | 14 → 14 |
| jin_soul | 770/1041 | 779/1041 | 9 | 0 | 64 → 64 |

Input determinism across 129 fighters: 0 non-string failures. Unit tests: 116/116 pass.

## Design limits (reported, not guessed)
- **far/close N and Rush share one canonical input** with the moveset's own moves (`1`). In a fight the default slot fires; the variants are reachable by equipping them in the moveset editor. Distance-based selection (close vs far) is not modelled.
- **JGS spin counts** (`JGS* (N spins)`) are all the same press from the stance; the spin count is not modelled.
- **System actions** (dash, roll, guard cancel, MAX mode, throw escape, taunt) are not attacks and still report as unparsed or not connecting.
