# Pantera-first wiring + roster videos — handoff (2026-11-03)

## What landed on main

- **PR #1548** (squash `a2efb22cd8c02f58e733b765788d3b9462611a39`): diagnosis doc `docs/movesets/PANTERA-WIRING-DIAGNOSIS-2026-11-03.md` + the `game/js/fighter.js` fix (RC1–RC4 below) + `test/pantera-wiring.test.mjs` + before/after probe evidence under `docs/proof/2026-11-03/pantera-wiring/`. CI 14/14 green incl. instruction-gate, no-deletion guard, game-unit-tests.
- **PR #1551** (squash `eb55d3695ab69f35de9d09bacb89605e71cdc948`): Pantera fight video `docs/proof/2026-11-03/pantera-wiring/pantera-fight-proof-20261103-fixed2.mp4` + phase log + VIDEO-README. Copy for the owner's phone: `~/workspace/your_files/pantera-proof/`.

## Root causes (full evidence in the diagnosis doc)

- **RC1 (grapples mid-combo, main cause):** `getRealMove` derived `isGrab` from Tekken-3 `t3_condition` situation codes 2..0x17. Those codes gate which execution a CONNECTED grab branches into — they are not "this move is a throw". 955 moves repo-wide were misclassed as grabs (Pantera: 51), so ordinary strikes played throw executions and dealt 0 damage. Fix: isGrab comes only from the move's own `isGrab` / `move_class === 'throw'`.
- **RC2:** the step-plan branch of `_attackClipPlan` returned combo-step rows with no strike/throw class guard. Fix: a step row whose class disagrees with the move is rejected, logged `[WH-STEP-PLAN]`, and the input falls through to class-checked tiers.
- **RC3:** `genericBankAction` was dead since PR #1458 (wrong clips indexing), so unmapped inputs fell to a donor tier that presented the 1+3 throw-attempt clip for a strike string. Fix: indexing corrected + the generic tier's last-resort pick is class-checked.
- **RC4 (couldn't grapple on purpose):** `CHORD_WINDOW_MS = 50` with a strict `<` — two thumbs ≥50 ms apart never form the 1+3/2+4 chord, and the first single press starts its own strike immediately. Throws have no direct on-screen button. Fix (engine side): a two-finger chord rescue in `tryAttack` — a second single-button press within 0.14 s of sim time during the first press's startup upgrades to the chord move when that chord exists; real strings are never stolen (the rescue sits after the continuation/string checks and restores state on failure). Proven on camera: pressing 1 then 3 converts to the 1+3 throw.
- **RC5 (scoped, unchanged):** `_throwChainPress` captures presses during throw states as chain-throw continuations — Tekken chain-throw design; it cannot start a throw from a strike state.

## Probe numbers (identity-gated stepped probe, clip identity per input)

Before the fix (unfixed tree, 45 suspect inputs): basics and simple strings correct; `d/b+1` and `d/f+3+4,1` played throw executions for 0 damage (RC1); `b+1+2,1+2` presented the 1+3 throw-attempt clip (RC3); `d+1+3` presented a donor throw clip as a strike; `b+1+3`/`b+2+4` presented a jab clip; `1+3,1`/`2+4,1` fell back to a plain jab row.
After the fix (fixed tree): every re-probed wrong/dead input presents a class-correct strike with real damage (`1,1` step row 584 rejected as a throw row → 19.8 dmg strike; `d/b+1` → strike row 38, 23.5 dmg; `d/f+3+4,1` → 32.2 dmg); deliberate `1+3` throws for 23.5 dmg. Unit tests: new pantera-wiring suite 5/5; regressions attack-anim, input-timing, t3-throw, batch-strings, moveset-slot-hijack all pass (38/38 with the fix).

## Carried anomalies (NOT fixed here — do not lose)

- **A1:** vs Zen (no T3 bank → legacy throw lock path), `2+4` / `1+4` / `f+1+3` / `f+2+4` / `d/b+1+3` execute full throws but deal 0 damage, before and after the fix; `1+3` damages (~24). Needs its own lane: trace `completeThrow` → `_throwSlamDamage` per resolved move, plus the paired path vs a banked opponent.
- **C1:** chain-throw follow-ups (`1+3,1`, `2+4,1`, tagged stage families) are registered as ordinary strings in the data model. Data-model decision, left as-is.
- **Dead slots carried with reasons** (from PANTERA-INPUT-COVERAGE-2026-11-01): `f+2,1,1` / `f+2,1,1,2` (data gaps), `3+4,3,2+3` (FK-held), `d+1,2`, `d/b+1+2,3+4`, the two 10-hit strings, `WS+2,2` (stance-entry). `b+1+2,1+2` presentation is fixed.

## Video method (proven on this VM — reuse it)

Local serve of the game tree → headless Chromium → identity gate (`p1.char.id` + `roundState === 'fight'`; the game boots into a zen-vs-pantera attract fight first, so ungated runs measure the wrong fighter) → pause + deterministic stepping (`_update(1/120)`, capture every 6 steps = 20 fps) → each frame rendered by the game's own `arena.renderer.render(scene, camera)` and read from the renderer canvas.
**GL backend is decisive:** SwiftShader costs 40–160 s per presented frame on this VM and the compositor paths (CDP screencast, captureScreenshot) effectively never present. Use Mesa/llvmpipe: run under `xvfb-run -a` with `--use-angle=gl` → ~3 s per frame at 320×240. Scripts: `~/workspace/_pantera-wiring-20261103/video_pantera9.py` (Pantera) and `roster_full.py` (per-fighter probe + short video, resumable, banks `roster-full.jsonl` + `roster-videos/<id>-fight-20261103.mp4` per fighter).

## Roster verdicts (game roster order; BASICS probe: 1, 2, 3, 4, 1+2, d/f+1, d+1, d/f+2, u/f+4, 1+3)

Pantera: COMPLETE — see the diagnosis doc + video above. All strike/string/combo phases throw-free; deliberate 1+3 grapple damages (23.5).

- **rin** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **byou** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **tou**: not yet probed (roster pass in progress).
- **sha**: not yet probed (roster pass in progress).
- **kai**: not yet probed (roster pass in progress).
- **retsu**: not yet probed (roster pass in progress).
- **zen**: not yet probed (roster pass in progress).
- **gyou**: not yet probed (roster pass in progress).
- **demonio** (P1): correct: 1 (6.1 dmg), 2 (7.9 dmg), 3 (16.6 dmg), 4 (15.8 dmg), 1+2 (4.4 dmg), d/f+1 (8.8 dmg), d/f+2 (10.5 dmg), u/f+4 (11.4 dmg), 1+3 (throw ✓ 0 dmg) · WRONG: d+1 (grab-class move on this input in his data — data suspect) [video: roster-videos/demonio-fight-20261103.mp4]
- **phantom** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **diablo** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **skull**: not yet probed (roster pass in progress).
- **samura1**: not yet probed (roster pass in progress).
- **sakura**: not yet probed (roster pass in progress).
- **zui**: not yet probed (roster pass in progress).
- **kinpo**: not yet probed (roster pass in progress).
- **waterfall**: not yet probed (roster pass in progress).
- **kingtyrant**: not yet probed (roster pass in progress).
- **burger**: not yet probed (roster pass in progress).
- **awapop**: not yet probed (roster pass in progress).
- **scimitar**: not yet probed (roster pass in progress).
- **purplerain**: not yet probed (roster pass in progress).
- **nightwolf**: not yet probed (roster pass in progress).
- **dio**: not yet probed (roster pass in progress).
- **cyborgx**: not yet probed (roster pass in progress).
- **michiko**: not yet probed (roster pass in progress).
- **star**: not yet probed (roster pass in progress).
- **torch**: not yet probed (roster pass in progress).
- **bruno**: not yet probed (roster pass in progress).
- **negativo**: not yet probed (roster pass in progress).
- **thor**: not yet probed (roster pass in progress).
- **yukihyo**: not yet probed (roster pass in progress).
- **slice**: not yet probed (roster pass in progress).
- **docfrank**: not yet probed (roster pass in progress).
- **baek-master-white**: not yet probed (roster pass in progress).
- **mariposa-monarch**: not yet probed (roster pass in progress).
- **dxmmii-patchwork**: not yet probed (roster pass in progress).
- **charger**: not yet probed (roster pass in progress).
- **dorowani**: not yet probed (roster pass in progress).
- **chatur**: not yet probed (roster pass in progress).
- **pond**: not yet probed (roster pass in progress).
- **ryusan**: not yet probed (roster pass in progress).
- **tobi**: not yet probed (roster pass in progress).
- **megami**: not yet probed (roster pass in progress).
- **menajerii**: not yet probed (roster pass in progress).
- **kronos**: not yet probed (roster pass in progress).
- **deathfang**: not yet probed (roster pass in progress).
- **ryuji**: not yet probed (roster pass in progress).
- **ryuji-rock**: not yet probed (roster pass in progress).
- **koreshi**: not yet probed (roster pass in progress).
- **rave**: not yet probed (roster pass in progress).
- **buffalo-bill**: not yet probed (roster pass in progress).
- **vainabel**: not yet probed (roster pass in progress).
- **cainelias**: not yet probed (roster pass in progress).
- **chordz**: not yet probed (roster pass in progress).
- **gashadokuro**: not yet probed (roster pass in progress).
- **aotsuki**: not yet probed (roster pass in progress).
- **silvertongue**: not yet probed (roster pass in progress).

Notes on cannot-instance verdicts: rin/byou (and the other select-hidden originals tou, sha, kai, retsu, gyou, plus ryuji) cannot be instanced as P1 via quick-start — probe them as P2 with `roster_p2.py`. phantom (`model-rerig.glb`) and diablo (`model-rigged.glb`) 404 in the local serve snapshot — their models are bucket-only, so this is a snapshot gap, not a game defect; instance them from the deployed build or a bucket-synced tree. zen has no bank by owner decision (2026-10-24) — pose-only. pond/ryusan banks are produced by the T7 lane; chatur/menajerii real banks by the TTT2 lane; megami is governed by the outfit-not-the-gate rule (skin/eyes/hair are the criteria) — include her when her no-outfit variant lands.

## Resume commands

```
cd ~/workspace/_pantera-wiring-20261103
python3 -m http.server 8791 --bind 127.0.0.1 --directory serve-fix   # if not running
xvfb-run -a python3 -u roster_full.py <remaining ids>   # P1 mode, skips banked fighters
xvfb-run -a python3 -u roster_p2.py rin byou tou sha kai retsu zen gyou ryuji   # hidden set as P2
python3 gen_handoff.py   # regenerate this verdict table from the JSONL
```
