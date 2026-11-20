# Tekken 7 system coverage matrix (2026-10-28)

Method: `git grep` over `origin/main` @ `8d65ec16` (game/js, game/lib, game/netplay, test, tools). Status: **present** = implemented in live game code; **partial** = exists but incomplete, only in tools/data, or not on the live path; **missing** = no implementation found. Grep-based first pass; each row is re-verified in-engine when its top-10 item is wired.

| # | T7 system | Status | WH refs | Top-10 item |
|---|---|---|---|---|
| 1 | Hit levels high/mid/low/special-mid | present | combat-core.js, hitdetect.js | 1 |
| 2 | Frame data (startup/on-block/on-hit/on-CH) | partial | t7-frame-data-loader.js, frame-tables.js, ai/frame-data.js | 1 |
| 3 | Counter hit | present | combat-systems.js, ai/combat-state.js | 1 |
| 4 | Clean hit / sweet spot | missing | only tools/retarget/hitprops/torch.hitprops.json | 1 |
| 5 | Hit reactions table (stagger/crumple/spin/knockdowns) | partial | t3-reaction-select.js, combat-systems.js, fighter.js | 1 |
| 6 | Hitstun / blockstun | present | fighter.js, ai/combat-state.js | 2 |
| 7 | Hitstop | present | combat-systems.js, fighter.js, brawler.js | 2 |
| 8 | Pushback on hit/block | partial | netplay/sim/fighter-sim.js only | 2 |
| 9 | Chip / recoverable (grey) health | present | combat-core.js, fighter.js | 2 |
| 10 | Damage scaling in combos | present | combat-systems.js, fighter.js | 1 |
| 11 | Juggles / launchers | present | combat-core.js, combat-systems.js | 1 |
| 12 | Bound / Screw / Tailspin | partial | combat-core.js, fighter.js (tailspin) | 1 |
| 13 | Wall splat | present | combat-core.js, combat-systems.js | 1 |
| 14 | Wall bound | missing | data only: tools/retarget/hitprops/zui.hitprops.json | 1 |
| 15 | Wall break / balcony break | present | combat-core.js, destruction.js, fighter.js | 1 |
| 16 | Floor break | present | stagebreaks.js, stage-levels.js | 1 |
| 17 | Ground hits / OTG | partial | combat-systems.js, ai/grapple-chains.js | 1 |
| 18 | Tech roll / ukemi / wake-up options | partial | ai/*, team-battle.js | 1 |
| 19 | Throws 1/2/1+2 breaks | present | t3-throw.js, ai/reversal-logic.js, brawler.js | 1 |
| 20 | Command throws / chain throws | partial | t3-throw.js, ai/grapple-chains.js | 1 |
| 21 | Ground throws | missing | none | 1 |
| 22 | Reversals / parries | present | fighter.js, ai/reversal-logic.js | 1 |
| 23 | Low parry | partial | fighter.js only | 1 |
| 24 | Chicken (reversal counter) | missing | data/tools only (fetch_t7chicken_framedata.py) | 1 |
| 25 | Power crush (armor) | present | combat-core.js, fighter.js | 1 |
| 26 | Homing attacks | partial | brawler.js only | 1 |
| 27 | Sidestep / sidewalk | present | fighter.js, ai.js | 4 |
| 28 | Backdash / KBD | present | fighter.js, movesets.js | 4 |
| 29 | Crouch dash / wavedash (Mishima) | missing | data only in moveset-library.js | 4 |
| 30 | Just frames (EWGF etc.) | partial | input.js | 4 |
| 31 | Input buffer | present | input.js, fighter.js, game.js | 4 |
| 32 | Stances | present | stance-aim.js, movesets.js | 4 |
| 33 | Strings / natural combos | present | combat-core.js, full-movelist.js | 4 |
| 34 | Hitboxes / hurtboxes (swept) | present | hitdetect.js (bvh), hitbox.js | 5 |
| 35 | Rage mode | present | rage.js | 1 |
| 36 | Rage Art | present | combat-core.js, fighter.js | 1 |
| 37 | Rage Drive | present | fighter.js, movesets.js | 1 |
| 38 | Unblockables | present | combat-core.js, combat-systems.js | 1 |
| 39 | Guard break | partial | combat-systems.js only | 1 |
| 40 | Ki charge | present | fighter.js, fighter-depth.js | 1 |
| 41 | Side switch / 3D axis | partial | game.js | 3 |
| 42 | Rounds / timer / KO / time out | present | game.js, ai.js | 3 |
| 43 | Ragdoll KO | partial | ragdoll.js (Rapier) | 6 |
| 44 | Rollback netcode | partial | netplay/rollback.js, lite-rollback | 3 |
| 45 | Replays / frame step | present | replay.js, main.js | 3 |
| 46 | Training mode (frame display, punish trainer) | present | training.js, punishment-training.js | 10 |
| 47 | CPU AI | present | ai.js, ai/* (Yuka, MCTS) | 9 |
| 48 | Move list UI | present | movelist-ui.js, full-movelist.js | 10 |
| 49 | Customization | partial | attires.js, creation-suite | 7 |
| 50 | Motion blending / reaction exits | missing | none | 8 |

## Totals (50 systems)
- **present: 29**
- **partial: 15**
- **missing: 6**
