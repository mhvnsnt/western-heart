# No T-pose: proof (2026-11-02)

Owner: "Pantera ... his animations are falling back to T pose ... need to get solved for all the characters".

| run | what | result |
|---|---|---|
| `pantera_before_fallback_coverage.json` | `tools/anim/move_coverage_probe.mjs`: all 238 neutral inputs, game time stepped (before the last-resort tier, before #1487's data fix) | 201 OK, **37 TPOSE**, every one a string follow-up / chain-throw step with no clip (`kind: step-plan`, `name: null`, bindFrac 1.0) |
| `pantera_after_fallback_coverage.json` | the same run with `fighter.js` `_ownButtonPlan` (PR #1491) | **238 / 238 OK, 0 TPOSE, 0 NOFIRE** |
| `soak_pantera_vs_negativo.*` | `tools/anim/tpose_soak_probe.mjs`: both fighters CPU-driven for 180 s, every pose sampled | 2,220 fighter samples (attack, walk, sidestep, hitstun, jump, V-shift, block, idle): **0 T-pose** |

Roster-wide (Node, the game's own planner): `docs/movesets/MOVE-CLIP-COVERAGE-2026-11-02.md`.
- Every fighter with an animation bank (53) has 0 moves without a clip.
- Six fighters have no animation bank yet (Vain Abel, Ryuji, Ryusan, Pond, Zen, Megami).
