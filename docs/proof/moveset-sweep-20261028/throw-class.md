# Throws that never reached the victim animation (pantera), 2026-10-29

## Root cause (game/js/fighter.js, move -> attack conversion)
- `isGrab` was set only from `mv.isGrab` or a T3 throw-situation condition row.
- A moveset move classed `move_class: 'throw'` (pantera `d/f+1+2_r17`, `1+3~t3.king`, `2+4~t3.king`, `d+1+3~t3.king`, ...) therefore played as a strike. The victim got a knockdown, and the thrower/victim exec clips never played.
- Fix: `move_class === 'throw'` is now a grab.

## Result (same harness; baseline = the notation batch, sweep-*-notation.json)
| fighter | before | after | fixed | regressed | juggles | throw failures |
|---|---|---|---|---|---|---|
| pantera | 675/903 | 696/903 | 21 | 0 | 14 → 14 | 25 → 4 |
| jin_soul | 779/1041 | 785/1041 | 6 | 0 | 64 → 64 | 1 |
| ryuji | 134/146 | 135/146 | 1 | 0 | 6 → 6 | 0 |

Unit tests: 116/116 pass.

## Known remaining
- **Pantera `1,2,1,2+4` (4 variants):** the string's final 2+4 is a grab, but it arrives while the opponent is still in hitstun from hit 3, and grabs whiff on hitstun. Not changed here: it needs a ruling on whether a string-ending grab may take a hitstunned opponent.
- **"Fired nothing", 5 pantera moves:**
  - STANDING_HEEL_HOLD and SHH1 chain-throw stages (3) are reachable only after the parent throw connects.
  - `f,n,b,d/b,d,f+1` and its `~t3.king` copy (2) are a 6-step motion.
