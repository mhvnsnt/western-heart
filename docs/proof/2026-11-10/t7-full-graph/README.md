# King T7 full-graph import + runtime interpreter (2026-11-10, owner t388u method correction)

This replaces per-move handpicking with one source-driven, whole-bank path. Every King T7 move, cancel, group cancel,
input sequence, requirement, alias, hit datum and animation reference is imported from the motbin, and source
identifiers are kept.

## Pipeline (reusable for any straight-source T7 fighter: change `--code`)
1. **Import:** `tools/anim/t7_graph_import.py --mothead <mothead> --code kin --out game/assets/anim/t7/king/graph.json --coverage game/assets/anim/t7/king/graph.coverage.json`.
   - Deterministic: two runs give byte-identical output. Graph sha256 `72ea8576…`, 2.55 MB.
2. **Bake:** `T7_EXE=<exe> tools/anim/t7_graph_bake.py --graph … --coverage … --cache <dir>`.
   - Covers every reachable clip through the existing community path (`t7_c8_stance_bake.py`: the game's sampler for 0x64, Kiloutre applier, Koenji mannequin, FK check).
   - One cached file per source clip, resumable, never re-bakes a cached clip, and records failures rather than substituting.
3. **Runtime:** `game/js/t7graph.js` `stepCancel(graph, move, ctx)` walks the move's cancels in **source priority order**:
   - press-edge chords vs held buttons vs button-less direction-state links;
   - windows and AUTO ends;
   - input sequences matched in their own window;
   - requirements evaluated through `makeEvalCond`. An unknown condition makes the cancel **skipped and reported**, never satisfied.

## Decoding sources (community, reused rather than re-derived)
- **Command layout:** TKMovesets2 `Editor_t7_Commands.cpp` @a1b1917a.
  - Direction bits 1–9, button bits 0–3 plus RA bit 4.
  - 0x8000 AUTO; 0x800D–0x8FFF = input sequence.
  - Raw button word bit 0x40000000 = press, verified on King: every attack link carries it, and the dash → run state link does not.
- **Alias table:** TekkenMovesetExtractor `motbinExport.py` T7 layout, u16[148] at 0x28. Verified: 0x8001 → `Kg_sKAM00_`, 0x8002 → `cKAM__00_`.
- **Requirement labels:** TKMovesets2 `editor_t7_requirements.txt` @a1b1917a (GPL-3.0). It is kept in the private sources dir and not vendored; only the condition ids and their cited meaning are used.

## Measured completeness (King, from `game/assets/anim/t7/king/graph.coverage.json`)
| Measure | Value |
|---|---:|
| moves in source | 2,787 |
| cancel rows (groups inlined) | 42,621 |
| input sequences | 259 |
| distinct requirement lists / conditions | 868 / 225 |
| conditions with a community label | 90 / 225 |
| moves reachable from stance + aliases (any requirement) | 1,196 |
| reachable using requirement-free links only | 277 |
| not reached by cancels/transitions (reaction, throw-receiver, other-character data) | 1,591 |
| unique clips the reachable moves use | 772 (1,082 moves on 0x64, 114 on 0xC8) |

The interpreter reproduces every behavior verified earlier, now from the graph alone (`test/t7-graph-king.test.mjs`, 10/10):
- dash → run only at frame 12;
- dash f+1 / n+2 / f+3+4;
- real run-state f+3 / f+4 / b;
- KBD crouch cancel;
- jab and d/f+1;
- the half-circle throw sequence.

## Blockers to full fidelity (named, with evidence)
1. **Requirement semantics.** 135 of 225 conditions have no community label: 80/81 on most attack links (they also gate `sTRN_L/R`, so likely side or turn state), plus 124, 128, 254, 640 and others. Until they're decoded those branches are skipped and reported. Decoding needs the game's requirement evaluator: the exe's requirement switch, which can be read with the same Unicorn/capstone setup (`T7_EXE`).
2. **Character-ID conditions (217/218/221–224).** The label table lists 217 and 221 both as "Player character ID", and the T7 character numbering isn't in any source on hand.
3. **Distance units.** Conditions 35/36 take T7 units, and no metre scale is established, so the evaluator needs `oppDistT7`.
4. **`cancel_extradata`** (64 values, about 68% of cancels) and the cancel option stay raw; their meaning isn't decoded by the community tools I read.
5. **Throws.** `throws` / `throw_extras` (header 0x260–0x278) are not in the JSON export. The JSON converter must read them before paired throws can be imported.
6. **Not traversed:** reactions (hit_conditions → reactions → defender moves).

## Exact next implementation
- **Fighter adapter:** Pantera's attack/locomotion state becomes the source move id plus frame. Each frame, build `ctx` from the stick (direction bit), button edges and holds, and the input history; `stepCancel` picks the next move, which plays `graph.moves[to]` through the cached clip `<bank>_<clip>.json`. Unknown-requirement skips go to a debug overlay.
- **Clips:** ship the cache as one pack. Size is checked against the Pages cap first.
- **Moveset rows:** the frontend rows become a generated view of the graph (no handwritten T3 fallback for T7 fighters).
