# Fight-load recovery v2: proof (2026-11-01)

Owner: "it keeps kicking me back out to the arena select menu and then I have to end up reloading the game ...
that needs to be fixed 100%".

`tools/proof-harness/fight_load_recovery_probe.mjs` (local build, Pantera vs Negativo, Shrine) breaks a versus fight
load three ways in a real browser and checks the game gets into the fight with no tap and no manual reload:

| scenario | what breaks | result | page loads |
|---|---|---|---|
| model | the player's model download (every request aborted until the first failed load) | **FIGHT** in 47 s (automatic retry) | 1 |
| module | the fight start fails with the browser's failed-module-import error (a deploy landed while the tab was open) | **FIGHT** in 59.6 s (one automatic reload straight back into the same versus fight) | 2 |
| build | the fight fails to build once (`game.startMatch` throws) | **FIGHT** in 33.4 s (automatic rebuild in SAFE LOAD) | 1 |

`ALL PASS module=PASS build=PASS model=PASS` — `fight_load_recovery.json` has every event; `module.png` is the fight
running after the automatic reload, `model.png` after the automatic retry.

`live_fight_entry.json`: `tools/proof-harness/fight_entry_probe.mjs` on the live site (phone viewport, real menu flow
VERSUS -> 1V1 -> Pantera / Negativo -> stage -> CONFIRM): CONFIRM -> fight in 20.2 s, no bounce.
