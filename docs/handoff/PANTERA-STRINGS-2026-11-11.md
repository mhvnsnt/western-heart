# Pantera (King T7): what works and what doesn't in strings and grapple chains (2026-11-11)

Owner (2026-11-11): "only the punch combos are working the the kick strings and gravel combos and the other
different a lot of different combos aren't working on Pantera".

## How this was measured
`tools/anim/string_sim_probe.mjs` (new) presses strings at **exact real-time spacing**. It stops the game loop,
simulates `performance.now()`, steps the sim exactly like `game.js _loop` at 60 fps, and presses through the
InputManager. The older key-press probe misreads timing under software WebGL, which runs about 15x slower than the
wall clock.

    NO_REMOTE=1 node tools/anim/string_sim_probe.mjs http://127.0.0.1:8765/game/index.html out.json pantera thor \
      "1,2|1,2,1|3,2|3,2,2|b+1,4|b+2,4|d/f+3,4" 100 40

## Results (presses 70 / 100 / 150 ms apart)
| String | Result |
|---|---|
| 1,2 / 1,2,1 | chain; every step plays King's real T7 clip |
| b+2,4 | chains; T7 clip for both hits |
| b+1,4 / d/f+3,4 | chain, but the **second hit is a generic step-plan stand-in** (`step-plan medium`). King's own T7 string-step rows exist (`b+1,4~t7.king.2` "(b+1), 4", `d/f+3,4~t7.king` "(d/f+3), 4"), but `t7_move_resolve.py --strings` never mapped them, so they are not in `moves.pack.json` |
| 3,2 / 3,2,2 | chain, stand-ins: these are Tekken 3 King strings with no T7 row |
| 3,4 / 4,3 / 1,4 / 2,4 | refused, correctly: not King strings (the 2nd press during a non-string move is ignored, as in Tekken) |

**Input timing is correct.** Two presses under 50 ms apart are one chord by design (`input.js` `CHORD_WINDOW_MS`,
same frame + 2 frames). From 50 ms up, they are a string.

## What makes kick strings and grapple combos look broken
1. **Stand-in follow-up hits.** Wherever a string step has no real T7 clip, the follow-up plays a generic stand-in,
   so the string "does something wrong". The fix is mapping every string step through King's own cancel graph,
   which is what the full-graph runtime does (`?t7graph=1`, `game/js/t7graph.js`) rather than per-row frame
   matching.
2. **Chain throws (the grapple combos).** King's multi-throws are stance-prefixed links after a starter throw:
   `CD.1+3` Arm Breaker, then `AB1.1,1+2` Triple Arm Breaker / `AB1.2,1,1+3` Chicken Wing; `AB2c.1,3,4,2,1+2`
   Rolling Death Cradle; `DHH.2,1,3,4` Giant Swing; and so on (151 throw rows in `pantera.json`). Each link has to
   be input during the previous throw's animation, with thrower and victim pair clips. No multi-throw runtime
   exists yet; the graph runtime marks throws UNSUPPORTED.

## Suggested order
1. Graph-runtime string coverage: every string step from King's cancel graph, with clips from `graph-clips/`
   (already baked: every reachable clip).
2. Throw pairs (attacker + victim clips), then chain-throw input windows (AB1 / AB2* / DHH links).
