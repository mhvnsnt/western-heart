# Western Heart WATCH / SIMULATE mode + CPU AI spec (Fire Pro–derived)

Updated 2026-10-28 by Grok. Owner priority #1 (see `docs/plans/STEAM-LIBRARY-FOR-WESTERN-HEART.md`).
Reference data: private `mhvnsnt/game-reverse-engineering` `teardown/firepro/data/csv-utf8/` (tables) and `teardown/firepro/decompiled/` (AIParam.cs, AIOpt_*.cs, PlayerController_AI.cs). This doc holds WH's own design and numbers only; no Fire Pro files ship here. TEKKEN-style combat stays the base; this layers on top.

## Mode
- **WATCH / SIMULATE:** pick any fighters (from the Creation Suite), rules, arena, CPU level per side; the match runs fully AI vs AI using WH's normal combat and inputs (the AI presses WH inputs through the same input buffer a player uses, so no separate "sim" combat path).
- Speed: 1x / 2x / 4x / instant result (headless tick). Instant uses the same tick loop with rendering off, so results match watched ones.
- Post-match: rating (0–100), move log, meter graphs.

## Hidden meters (from Fire Pro match engine, renamed to canon)
| WH meter | Role | Reference table |
|---|---|---|
| Stamina | drains on moves taken/given; tiers set reaction speed and move access | `StaminaTable` (tiers: small ≥60–75 %, large ≥18–36 %, critical below) |
| Spirit | momentum; fills on landed moves/taunts; gates Spirit Actions (魂 ACTION) and Nine-Soul Release | match engine spirit value |
| Limb damage per body part | debuffs, submission chance | `FP_ProbabilityTbl` (joint condition points 0/3/10/20/20) |
| Condition (good/normal/bad) | match-start modifier | `FP_ProbabilityTbl` (20/3/0) |

## CPU levels 1–10 (WH tuning starts from these Fire Pro values)
| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| input timing latest (frames) | 60 | 30 | 20 | 18 | 10 | 8 | 6 | 4 | 2 | 0 |
| input timing earliest (frames) | 15 | 10 | 8 | 6 | 4 | 2 | 2 | 0 | 0 | 0 |
| mash min / max (per window) | 1/5 | 1/5 | 2/6 | 3/7 | 4/8 | 5/9 | 6/10 | 7/11 | 9/13 | 11/15 |
| struggle-trigger chance % | 100 | 100 | 100 | 100 | 80 | 65 | 50 | 35 | 20 | 5 |
| playing-possum chance % | 1 | 1 | 2 | 3 | 4 | 5 | 7 | 8 | 9 | 10 |
(source `COMLevel` table)

## AI decision model
- **Situation tables:** one weighted action table per situation (far, near, grapple, back grapple, opponent down centre/near corner, opponent stunned, leaning on corner, opponent out of ring, guard position, performance/taunt), mirroring `AIOpt_*`. Each entry = action category + weight (0–100).
- **Priority acts:** override list checked first (e.g. finish when opponent critical + Spirit full), mirroring `AIPriorityAct`.
- **Psychology sliders per fighter** (Creation Suite, editable by the owner): aggression, technique vs power, taunt rate, risk (top-rope / Spirit Action use), comeback tendency, reversal focus. Sliders scale the situation-table weights.
- **Timing:** each chosen action is fed as WH inputs with the level's timing window above, so CPU 10 is frame-perfect and CPU 1 is late and sloppy.
- **Match rating:** style × rule satisfaction matrix (`MatchEvaluationData`): rewards variety, momentum swings, near-falls; style presets (showman, strong-style, shoot) map to WH fighter archetypes.

## Wiring plan (separate PRs)
1. `src/ai/` situation-table runner + priority acts + slider scaling (data in JSON).
2. Hidden meters in fighter state; HUD hidden in Watch mode, shown in debug overlay.
3. Watch/Simulate menu entry under the existing menu theme (mirrored pink heart, white labels with black outline).
4. Headless instant-sim + rating screen; tests: same seed → same result watched vs instant.
