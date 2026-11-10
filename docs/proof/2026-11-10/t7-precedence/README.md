# King T7 cancel selection: exe list semantics and STRICT precedence (2026-11-10)

## Source evidence

The exe's requirement-list loop is `0x1406f4750`, with inline copies at `0x140716fa4` and `0x140721634`. It works like this:
- `acc = 1`;
- for each 8-byte entry until id `0x371`: if `acc` is still true, `acc = eval(entry)`;
- the opponent passed in is `[self+0x1548]`.

So a list is a plain **AND**:
- any known-false entry makes it false, even when it comes after an unknown one;
- otherwise it is true only when every entry is true;
- else it is UNKNOWN.

The old runtime stopped at the first unknown entry. It now applies the AND, so `[[609,146],[72,0]]` is false when facing.

The evaluator `0x1406f5490` returns 1 before its switch for any id with bit 0x8000 (`0x1406f54d9`). Such entries (for example 0x8106, 0x8414) are now true.

## Strict precedence

The cancel walk takes the first row whose input, window and requirements hold. When a row's input, window and frame all match and only its requirement truth is UNKNOWN, the source might take it. Nothing below it may be shown as the source's choice.

- **STRICT** is the default under `?t7graph=1`.
  - `stepCancel` returns `ambiguous` and nothing fires.
  - At the clip end the move holds rather than falling through to `transition`, because the fall-through is not certain either. This counts as a stall.
  - The dev label shows `BLOCKED: row #N needs unknown cond …` in red.
- **PERMISSIVE** (`?t7graph=permissive`) is a labelled diagnostic: "precedence UNVERIFIED". A lower row may fire, and it is flagged with the outranking unknown conditions.

## Actual state under STRICT (the honest result)

**Nothing fires from King's stance `Kg_sKAM00_`.** Its row #0 (any direction, no button → `Kg_jprk00F`) has requirements `[[809,15],[33812,0],[361,100]]`:
- 809 = `[self+0x938] == param` (exe `0x1406f7849`; community label "prop 0x8414");
- 361 = `[self+0x964] == param` (exe `0x1406f7e2c`; label "prop 0x80ed").

These are player variables set by move extra properties. Those are not imported and their exe handler is not decoded, so both stay UNKNOWN and row #0 blocks every lower row on every frame without a press. On press frames, rows gated by the facing conditions 80/81 (row #306 for 1) block instead. In practice Pantera holds the stance with no moves under STRICT. That is fail-closed by design, and it is not a working moveset.

| Static command map (rows' own requirements; precedence NOT applied) | Count |
|---|---|
| evaluable | 8,614 |
| unknown | 13,412 |
| known-false | 15,035 |
| timing | 151 |
| special | 134 |
| seq-mode | 73 |

"Evaluable" means the row's own list is known and true. Under strict precedence that is not enough to fire.

## Reuse research

For the next import, TekkenMovesetExtractor `motbinExport.py` (T7 layout) gives:
- `extra_move_properties_ptr/size` at header 0x1e0/0x1e8 (struct 0xC);
- `throw_extras_ptr/size` at 0x260/0x268 (0xC);
- `throws_ptr` at 0x270 (0x8).

The graph importer reads the same motbin, so these tables can be imported systematically. Their semantics still need the exe:
- the property handler that writes `[+0x938]` / `[+0x964]`;
- the throw resolution.

Throws stay UNSUPPORTED.

## Tests

`test/t7-graph-adapter-pantera.test.mjs`, 22/22:
- AND semantics and the 0x8000 ids;
- through the real Fighter in STRICT, for n+1, f, d/f, 3+4 and f+1+3: no cancel fires, the fighter stays in the stance, the block is recorded on row #0 (809, 361), the move holds and there is no hitbox;
- PERMISSIVE: 1 → `Kg_lp00F`, flagged with [80, 81].

The input→row→clip mechanics tests run in the labelled permissive mode.

Node only. No browser, touch or model proof. Not 100%.
