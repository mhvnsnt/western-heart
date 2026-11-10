# King T7 facing conditions (72/73/80/81) and throw marking (2026-11-10)

Source: the shipping exe, via the same private checkout and method as `docs/proof/2026-11-10/t7-requirements/README.md`. Scan logs are kept privately in `facing-writes.log`, `facing-fn.log` and `yaw-writes.log`.

## What sets the words the evaluator reads

The whole `.text` section was scanned for word writes to `+0x1c2` and `+0x1c4`. The per-frame writer is `0x1406ebfe0`; the others are `0x1423486a0`, which copies the same block, and unrelated structs.

`0x1406ebfe0` does the following:

1. `[+0x1bc]` = bearing to the opponent. This is atan2 of the opponent position (`+0x1440/+0x1448`) minus the own position (`+0x160`), scaled to a 16-bit binary angle.
2. `[+0x1b8]` = own yaw (float, wrapped to [0, 2π)), scaled the same way.
3. **`[+0x1c2]` = own yaw − bearing** (rel, 16-bit). Zero means facing the opponent.
4. `[+0x1c6]` = `[+0x1c0]` − bearing.
5. **`[+0x1c4]` = rel folded**: if rel ≥ 0x8000 then ~rel, so the range is 0..0x7fff.
6. `[+0x740]/[+0x744]` = quadrant indexes taken from a per-stage table (not used by these conditions).

The evaluator cases read these words as follows:

| Condition | Test |
|---|---|
| 72 (backturned) | folded > 0x4000 (signed compare; folded is ≤ 0x7fff) |
| 73 (not backturned) | folded ≤ 0x4000 |
| 80 | (rel − 0x3fff) mod 2^16 ≤ 0x4000 → rel in [0x3fff, 0x7fff] |
| 81 | (rel + 0x8000) mod 2^16 ≤ 0x3fff → rel in [0x8000, 0xbfff] |

So 80 and 81 are the two back half-turns on either side. Which side is left and which is right is not resolved.

## Implemented

- `makeEvalCond` evaluates 72/73/80/81 from an explicit `relHeading16`. `t7FacingFold` reproduces the exe fold.
- **The game supplies no `relHeading16`**, so all four stay UNKNOWN in play. The reason is that the own yaw `[+0x1b8]` has 146 writes across many functions: the move/animation turn, tracking/homing and the round setup were not traced. WH's own `facing` is a ±1 side flag, not the source yaw. Deriving the heading from it would be invented.
- Stance rows gated by a facing condition: 47. Reachable rows with a facing condition: 72 = 1,852, 80 = 911, 81 = 913. Rows can carry several conditions, so these overlap.

## Throws

- The dev label now shows `UNSUPPORTED throw: clip only, NO GRAB` in red while a throw-class source move plays. The count is kept in `throwNoGrab`.
- Throw-class means either:
  - the hit-level word decodes to a throw; or
  - the source hit condition damage is exactly 0x4000. That holds for 43 King moves (`Thrmv*`, `nagexx01_n2`, `tac02xk`, `Co_runtac00`, `Kg_*Thrmv*`, `Kg_Thrside*`, `Kg_wDASH_dbp`) and is never real damage.
- **Fix:** before this, those 43 moves made a HIGH hitbox with 16,384 damage (the 0x4000 value read as damage). They now produce no hitbox. The exe meaning of 0x4000 is not traced; the rule is fail-closed (no hitbox).
- The label also states `posture: standing (source posture undecoded) | facing: unknown (backturn rows skipped)`.

## Tests

`test/t7-graph-adapter-pantera.test.mjs`, 19/19:
- **Exe boundary values** for the fold, 72/73 and 80/81. Without `relHeading16`, each is null.
- **Real Fighter, stance n+1+2:**
  - in the game, source row 280 (`[[72,0]]` → `Kg_Tnrpsp`) is skipped as unknown 72;
  - another row fires and is flagged as fired after an unknown row;
  - an injected backturned heading (test only) fires row 280;
  - an injected facing heading makes 72 known-false.
- **Throw f+1+3 → `ThrmvLB2_00F`:** the clip plays and is marked unsupported, with no hitbox and 43 marked moves.

Node only. No browser, touch or model proof. Not 100%. The graph stays opt-in (`?t7graph=1`).

## Next blocker

The source of own yaw `[+0x1b8]` for the player struct:
- which move or animation fields turn it;
- when tracking re-aims it at the opponent.

Candidate writers are in `0x1406e4be5`, `0x14071892d` and `0x14074afe0` (logged privately). Until that is traced, backturn and posture remain unknown.
