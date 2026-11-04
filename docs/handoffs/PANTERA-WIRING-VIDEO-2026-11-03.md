# Pantera-first wiring + roster videos — handoff (2026-11-03)

## What landed on main

- **PR #1548** (squash `392352ed6d9ac88bbc9115a576c91f70b546a80b`): diagnosis doc `docs/movesets/PANTERA-WIRING-DIAGNOSIS-2026-11-03.md` + the `game/js/fighter.js` fix (RC1–RC4 below) + `test/pantera-wiring.test.mjs` + before/after probe evidence under `docs/proof/2026-11-03/pantera-wiring/`. CI 14/14 green incl. instruction-gate, no-deletion guard, game-unit-tests.
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
- **tou**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original: model is null (modelPending) in the game roster data — no model wired at all. Cannot instance as P1 or P2 (probed as P2 per handoff note).
- **sha**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original: model is null (modelPending) in the game roster data — no model wired at all. Cannot instance as P1 or P2 (probed as P2 per handoff note).
- **kai**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original: model is null (modelPending) in the game roster data — no model wired at all. Cannot instance as P1 or P2 (probed as P2 per handoff note).
- **retsu**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original: model is null (modelPending) in the game roster data — no model wired at all. Cannot instance as P1 or P2 (probed as P2 per handoff note).
- **zen**: No bank by owner decision 2026-10-24 — pose-only video, never probed for attacks. video: roster-videos/zen-fight-20261103.mp4 (50 frames captured).
- **gyou**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original: model is null (modelPending) in the game roster data — no model wired at all. Cannot instance as P1 or P2 (probed as P2 per handoff note).
- **demonio** (P1): correct: 1 (6.1 dmg), 2 (7.9 dmg), 3 (16.6 dmg), 4 (15.8 dmg), 1+2 (4.4 dmg), d/f+1 (8.8 dmg), d/f+2 (10.5 dmg), u/f+4 (11.4 dmg), 1+3 (throw ✓ 0 dmg) · WRONG: d+1 (grab-class move on this input in his data — data suspect) [video: roster-videos/demonio-fight-20261103.mp4]
- **phantom** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **diablo** (P1): CANNOT INSTANCE — gate-failed (cannot instance) [no video]
- **skull**: probe: correct ×7, fires-no-damage ×1, dead ×1, throw connects (damage) ×1. dead inputs: d+1. fires but 0 damage: d/f+1. video: roster-videos/skull-fight-20261103.mp4 (99 frames captured).
- **samura1**: probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 1+2. video: roster-videos/samura1-fight-20261103.mp4 (98 frames captured).
- **sakura**: probe: correct ×7, fires-no-damage ×2, throw connects (damage) ×1. fires but 0 damage: 4, 1+2. video: roster-videos/sakura-fight-20261103.mp4 (97 frames captured).
- **zui**: probe: correct ×7, fires-no-damage ×3. fires but 0 damage: 3, 4, 1+3. video: roster-videos/zui-fight-20261103.mp4 (115 frames captured).
- **kinpo**: probe: correct ×7, fires-no-damage ×1, dead ×1, throw connects (damage) ×1. dead inputs: d+1. fires but 0 damage: 1+2. video: roster-videos/kinpo-fight-20261103.mp4 (106 frames captured).
- **waterfall**: probe: correct ×5, fires-no-damage ×5. fires but 0 damage: 1+2, d/f+1, d+1, d/f+2, 1+3. video: roster-videos/waterfall-fight-20261103.mp4 (91 frames captured).
- **kingtyrant**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Blocked by the game's own MATERIAL GATE — diag captured the verbatim error '[WH] material gate: king-tyrant-attire1 blocked (1 untextured)'; GLB inspection confirms exactly 1 of his 24 materials has no baseColorTexture. He IS rigged (skin, 50 joints). His model was also absent from the game-requested path roster/king-tyrant/attires/attire1/model.glb in the repo snapshot (it lives at game/assets/models/king-tyrant.glb, 25,643,940 B) — placed locally to reach the gate. Fix belongs to the model lane: bake the missing texture, and put the file at the requested roster path.
- **burger**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/burger-fight-20261103.mp4 (122 frames captured).
- **awapop**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/awapop-fight-20261103.mp4 (115 frames captured).
- **scimitar**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/scimitar-fight-20261103.mp4 (103 frames captured).
- **purplerain**: probe: correct ×8, dead ×1, throw connects (damage) ×1. dead inputs: d+1. video: roster-videos/purplerain-fight-20261103.mp4 (99 frames captured).
- **nightwolf**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Blocked by the game's MATERIAL GATE class: model serves 200 at the game-requested path roster/nightwolf/attires/attire1/model.glb (verified in server log; file lives at game/assets/models/nightwolf.glb in the repo) and his moveset loads, yet quick-start never spawns him; GLB inspection shows 2 of his 37 materials have no baseColorTexture (the gate's block condition — cf. kingtyrant's captured gate error). He IS rigged (skin, 50 joints). Fix belongs to the model lane: bake the missing textures.
- **dio**: probe: correct ×8, fires-no-damage ×2. fires but 0 damage: 2, 4. video: roster-videos/dio-fight-20261103.mp4 (91 frames captured).
- **cyborgx**: RESCUED in the local tree: the game requests roster/cyborg-x/attires/attire1/model.glb but the repo stores his model as model-rigged.glb in the same folder; probed + videoed with the repo's own GLB placed at the requested path. Repo wiring gap: the deployed build 404s his model until the file is renamed/placed as model.glb. (First video capture missed the fighters entirely — transient camera miss; the redo capture is the shipped one, frames verified.) probe: correct ×6, fires-no-damage ×3, throw connects (damage) ×1. fires but 0 damage: 1+2, d/f+1, d+1. video: roster-videos/cyborgx-fight-20261103.mp4 (101 frames captured).
- **michiko**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Blocked by the game's MATERIAL GATE class: the game requests roster/michiko/attires/attire1/model-rigged.glb (note: -rigged filename); with the repo GLB (game/assets/models/michiko.glb, 1,163,716 B) placed there it serves 200 and her moveset loads, yet quick-start never spawns her; GLB inspection shows her ONLY material (1 of 1) has no baseColorTexture — the gate's block condition. She IS rigged (skin, 33 joints). Fix belongs to the model lane: bake the missing texture.
- **star**: probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 1+2. video: roster-videos/star-fight-20261103.mp4 (101 frames captured).
- **torch**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/torch-fight-20261103.mp4 (100 frames captured).
- **bruno**: probe: correct ×8, dead ×1, fires-no-damage ×1. dead inputs: d+1. fires but 0 damage: 1+3. video: roster-videos/bruno-fight-20261103.mp4 (132 frames captured).
- **negativo**: probe: correct ×9, dead ×1. dead inputs: d+1. video: roster-videos/negativo-fight-20261103.mp4 (91 frames captured).
- **thor**: RESCUED in the local tree: the game requests roster/thor/attires/attire1/model.glb but the repo stores his model as model-rerig.glb in the same folder; probed + videoed with the repo's own GLB (30,869,328 B) placed at the requested path. PERFECT probe. Repo wiring gap: the deployed build 404s his model until the file is renamed/placed as model.glb. probe: correct ×9, throw connects (damage) ×1. video: roster-videos/thor-fight-20261103.mp4 (109 frames captured).
- **yukihyo**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/yukihyo-fight-20261103.mp4 (89 frames captured).
- **slice**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/slice-fight-20261103.mp4 (89 frames captured).
- **docfrank**: probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 1+2. video: roster-videos/docfrank-fight-20261103.mp4 (157 frames captured).
- **baek-master-white**: probe: correct ×6, fires-no-damage ×2, dead ×1, throw connects (damage) ×1. dead inputs: d+1. fires but 0 damage: 4, 1+2. video: roster-videos/baek-master-white-fight-20261103.mp4 (107 frames captured).
- **mariposa-monarch**: RESCUED in the local tree: her model lives in the repo at roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb (5,840,076 B, Zafina-base Monarch reskin); probed + videoed with it placed at the game-requested roster/mariposa-monarch/attires/attire1/model.glb. Repo wiring gap: the deployed build cannot reach her model at the requested path. (First video capture had the camera under the stage — transient; the redo capture is the shipped one, frames verified.) probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 1+2. video: roster-videos/mariposa-monarch-fight-20261103.mp4 (89 frames captured).
- **dxmmii-patchwork**: probe: correct ×7, fires-no-damage ×1, dead ×1, throw connects (damage) ×1. dead inputs: d+1. fires but 0 damage: 1+2. video: roster-videos/dxmmii-patchwork-fight-20261103.mp4 (107 frames captured).
- **charger**: probe: correct ×7, dead ×2, throw connects (damage) ×1. dead inputs: d/f+1, d/f+2. video: roster-videos/charger-fight-20261103.mp4 (90 frames captured).
- **dorowani**: probe: correct ×7, dead ×2, throw connects (damage) ×1. dead inputs: d/f+2, u/f+4. video: roster-videos/dorowani-fight-20261103.mp4 (118 frames captured).
- **chatur**: No bank yet (TTT2 lane: True Ogre has no TTT2 moveset file; only Ancient Ogre) — pose-only video. video: roster-videos/chatur-fight-20261103.mp4 (50 frames captured).
- **pond**: Real T7 Raven bank merged in PR #1550; confirmation probe only — proof video already delivered by the T7 lane. probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: d/f+1.
- **ryusan**: Real T7 Lucky Chloe bank merged in PR #1550; confirmation probe only — proof video already delivered by the T7 lane. probe: correct ×9, throw connects (damage) ×1.
- **tobi**: Hwoarang bank. probe: correct ×7, fires-no-damage ×2, throw connects (damage) ×1. fires but 0 damage: 1+2, u/f+4. video: roster-videos/tobi-fight-20261103.mp4 (87 frames captured).
- **megami**: Probed on the merged no-outfit variant (PR #1549, outfit-not-the-gate rule); UNBANKED — awaits the Jun bank from the TTT2 lane. probe: correct ×8, dead ×1, throw connects (damage) ×1. dead inputs: d+1. video: roster-videos/megami-fight-20261103.mp4 (85 frames captured).
- **menajerii**: Fights on the kuma STAND-IN bank (own Roger Jr. bank blocked on the TTT2 XEX lane). probe: correct ×7, dead ×2, throw connects (damage) ×1. dead inputs: d+1, u/f+4. video: roster-videos/menajerii-fight-20261103.mp4 (85 frames captured).
- **kronos**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/kronos-fight-20261103.mp4 (107 frames captured).
- **deathfang**: probe: correct ×8, dead ×1, throw connects (damage) ×1. dead inputs: d/f+1. video: roster-videos/deathfang-fight-20261103.mp4 (154 frames captured).
- **ryuji**: CANNOT INSTANCE — gate-failed (cannot instance). No substitute video (never fabricated). Select-hidden original; hybrid by design (evidence-closed 2026-11-03). Probed as P2.
- **ryuji-rock**: probe: correct ×7, dead ×2, throw connects (damage) ×1. dead inputs: d/f+1, d/f+2. video: roster-videos/ryuji-rock-fight-20261103.mp4 (91 frames captured).
- **koreshi**: probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 1+2. video: roster-videos/koreshi-fight-20261103.mp4 (100 frames captured).
- **rave**: Renders untextured white in the local tree (his texture pack is bucket-served and was not vendored); wiring probe unaffected. His wide-armed stance silhouette is his Lei-style rig at capture resolution. probe: correct ×6, fires-no-damage ×2, dead ×1, throw connects (damage) ×1. dead inputs: d+1. fires but 0 damage: 2, 3. video: roster-videos/rave-fight-20261103.mp4 (91 frames captured).
- **buffalo-bill**: RESCUED in the local tree: the game requests roster/buffalo-bill/attires/attire3/model.glb but the repo stores his model as model-rigged.glb in the same folder; probed + videoed with the repo's own GLB (30,836,224 B) placed at the requested path. Repo wiring gap: the deployed build 404s his model until the file is renamed/placed as model.glb. probe: correct ×7, fires-no-damage ×2, throw connects (damage) ×1. fires but 0 damage: 1+2, u/f+4. video: roster-videos/buffalo-bill-fight-20261103.mp4 (87 frames captured).
- **vainabel**: The pass's one clear WRONG: his 1+2 fires a THROW (grab-class clip, 22.9 dmg) on a strike input, and his 1+3 throw animates but deals 0 damage — his throw/strike wiring is crossed (see probe rows). probe: correct ×8, WRONG-throw-on-strike-input ×1, throw animates, 0 damage ×1. WRONG inputs: 1+2 fired a grab-class clip (1+2). video: roster-videos/vainabel-fight-20261103.mp4 (115 frames captured).
- **cainelias**: MODEL DEFECT (for the rig lane): his model renders at MINIATURE scale from spawn (a tiny figure beside full-size opponents in every frame) — the wiring probe is fully functional (9 damaging + throw), but the model's scale is broken. The shipped video is the honest proof of the defect. probe: correct ×8, dead ×1, throw connects (damage) ×1. dead inputs: d+1. video: roster-videos/cainelias-fight-20261103.mp4 (112 frames captured).
- **chordz**: probe: correct ×7, fires-no-damage ×2, dead ×1. dead inputs: d+1. fires but 0 damage: 1+2, 1+3. video: roster-videos/chordz-fight-20261103.mp4 (133 frames captured).
- **gashadokuro**: MODEL DEFECT (for the rig lane): his kuma-a1.glb renders as a tiny flat skeleton lying on the ground in every phase — the wiring probe is fully functional, but the MODEL is broken (scale/rig). The shipped video is the honest proof of the defect. probe: correct ×8, fires-no-damage ×2. fires but 0 damage: 4, 1+3. video: roster-videos/gashadokuro-fight-20261103.mp4 (101 frames captured).
- **aotsuki**: probe: correct ×9, throw connects (damage) ×1. video: roster-videos/aotsuki-fight-20261103.mp4 (147 frames captured).
- **silvertongue**: probe: correct ×8, fires-no-damage ×1, throw connects (damage) ×1. fires but 0 damage: 2. video: roster-videos/silvertongue-fight-20261103.mp4 (89 frames captured).

Notes on cannot-instance verdicts: rin/byou (and the other select-hidden originals tou, sha, kai, retsu, gyou, plus ryuji) cannot be instanced as P1 via quick-start — probe them as P2 with `roster_p2.py`. phantom (`model-rerig.glb`) and diablo (`model-rigged.glb`) 404 in the local serve snapshot — their models are bucket-only, so this is a snapshot gap, not a game defect; instance them from the deployed build or a bucket-synced tree. zen has no bank by owner decision (2026-10-24) — pose-only. pond/ryusan banks are produced by the T7 lane; chatur/menajerii real banks by the TTT2 lane; megami is governed by the outfit-not-the-gate rule (skin/eyes/hair are the criteria) — include her when her no-outfit variant lands.

## Resume commands

```
cd ~/workspace/_pantera-wiring-20261103
python3 -m http.server 8791 --bind 127.0.0.1 --directory serve-fix   # if not running
xvfb-run -a python3 -u roster_full.py <remaining ids>   # P1 mode, skips banked fighters
xvfb-run -a python3 -u roster_p2.py rin byou tou sha kai retsu zen gyou ryuji   # hidden set as P2
python3 gen_handoff.py   # regenerate this verdict table from the JSONL
```


## Roster pass continuation (2026-11-04)

The roster pass was finished by a continuation lane on a main-current,
bucket-completed tree (serve-roster: main-HEAD game JS incl. PR #1548/#1550
wiring + every roster model vendored — bucket copy used only where its size
equaled the repo size, otherwise the repo blob from main; vendor-manifest in
the lane scratch). phantom and diablo instance from that tree — the earlier
404s were the local snapshot gap, exactly as noted above. Probes used the
same identity-gated BASICS set (1, 2, 3, 4, 1+2, d/f+1, d+1, d/f+2, u/f+4,
1+3); videos use the Pantera framing method (pair re-centered on the setup
midpoint at every phase + drift correction). Per-input facts for every
fighter: docs/proof/2026-11-03/roster/roster-verdicts-20261103.json.
Delivered videos: ~/workspace/your_files/roster-proof/<fighter>-fight-20261103.mp4.
zen stays pose-only (no bank, owner decision 2026-10-24) and chatur
pose-only with the no-bank note; menajerii's verdict names the kuma
stand-in bank; megami was probed on the merged no-outfit variant (PR #1549)
and is unbanked pending the TTT2 Jun bank; pond/ryusan received
confirmation probes against their merged T7 banks (PR #1550), their proof
videos having been delivered by the T7 lane.
