# Phase 4B — created fighter on a suite template body, fighting: BROWSER PROOF

**Verdict: WORKS.** A fighter built through the Creation Suite's own save
flow on the `powerhouse` template body — with morphs applied — enters a
real fight through the game's own pipeline and ANIMATES: idle stance,
single attacks, and a two-hit string all play real retargeted clips on
the template body, driven by real keyboard input. This closes the one
item PR #1498 ("Phase 4b: created fighters fight on their template body
+ morphs", merged 2026-11-02, merge commit
`d789819cabef9e11b69ee395ae26f851c11eb58d`) explicitly left unproven:
its tests were Node-only and its PR body states the browser/material
path was not proven. The wiring itself was already complete on main —
this PR adds no game code, only this proof and the harness that made it.

## Run facts

- Code under test: repo main pinned at
  `aa96f52c92d4fead7fc06f6c5b1993d3b407479f` (current main at run time;
  `game/js` is byte-identical between `90a0e692` and `aa96f52c` per
  compare — the intervening commits touch docs/tools only).
- Served locally (headless Chromium cannot reach the live site from
  the test VM): a static proxy of the pinned tree; all non-local DNS
  refused fast so the game's own asset-candidate fallback (B2 worker
  → local) is exercised exactly as in the repo's other proof runs.
- The created fighter is a Creation Suite save in localStorage
  (`wh_creation_suite_v1`), the exact object the suite writes:
  mode `blank`, template `powerhouse`,
  baseGlb `customization/templates/meshes/powerhouse.glb`,
  morph_targets `{ b_weight: 0.8, b_tone: 0.4 }`, name "PHASE4B PROOF".
  It reaches the fight through `custom-fighter.js` →
  `customFighterToRoster` → `__modes.startFight('custom', 'pantera',
  { mode: 'arcade' })` — the game's own entry points, no test-only
  shortcuts. Opponent: pantera (stock fighter, king bank).
- Fight discipline follows `tools/proof-harness/`: after the round
  went live, the CPU controller was frozen (`ai.update` no-op,
  timer pinned) and each frame was captured in the same task as a
  real arena render, with bone world positions read from
  `matrixWorld`. Inputs are real CDP keyboard events (Digit1/2/4 =
  buttons 1/2/4 per `game/js/input.js`; arrows = stick).

## What the run proved (wiring.json + console.log)

- p1 model resolved to **`custom-template-powerhouse`**; template
  `powerhouse`; the save's morph targets reached the fighter and
  **20 morph influences were applied** to the model
  (`model.userData.morphInfluencesApplied = 20`) — the PR #1495/#1496
  morph path, exercised end-to-end in the browser.
- Console: `[WH] custom-template-powerhouse: MB-Lab rig remapped to
  T3 bone names (23 joints renamed)` — the `assets.js` MB-Lab remap
  fired in the browser (the piece Node could not prove).
- Console: `[WH] Fighter custom: 22 real T3 actions from bank 'jin'
  (retargeted onto custom-template-powerhouse)`, with the jin-bank
  fallback logged by `fighter.js` (no custom moveset registered yet —
  a stated TODO of #1498, unchanged by this proof). All 19 required
  T3 bones present on the bound rig (`bonesMissing: []`).
- Opponent sanity: pantera bound 22 actions from bank 'king' onto
  `pantera-leoman`.

## Frames (shots.json carries state + pose vectors per frame)

All PNGs are hash-verified writes (sha256 prefixes in shots.json).

- `01-idle-stance.png` — idle, clip `t3_jin_stance@custom-template-powerhouse`.
- `02-attack-1.png` — after Digit1: state `attack`, clip `atk:1:1`.
  Head moved ~0.51 m from idle (lunge), hips dropped 0.12 m,
  left hand extended ~0.28 m. Visibly lunged jab in the frame.
- `03-attack-2.png` — after Digit2: state `attack`, clip `atk:2:2`,
  hands up at head height — a different strike.
- `04-attack-4.png` — after Digit4 (+170 ms): deep crouch mid-move
  (hips Y 0.709 vs 0.836 idle), caught in recovery.
- `05-string-1-2.png` — Digit1 then Digit2: the string advanced to
  clip `atk:4:3`, deepest lunge of the set (head Y 1.099), bodies in
  contact with the opponent.
- `06-walk-forward.png` — forward held 650 ms: both feet lifted
  (Y 0.248 / 0.280 vs 0.139 / 0.133 at idle) — mid-stride.
- A seventh frame (df+2) was attempted; the final grab starved in
  this VM's renderer before it could be captured. Six frames cover
  the brief (idle + several attacks + a string + locomotion), so the
  run was closed without it.

The template body renders untextured (pale) in the fight scene — the
known, owner-decided state from #1498: the nine `custom-template-*`
models pass the material gate when their only failing verdict is
'untextured'. Textures/materials for template bodies are a separate
remainder, not part of the Phase 4B animation gate.

## Harness

- `tools/proof-harness/phase4b_template_fight.mjs` — the full run
  (launch, seed, boot, fight, wiring dump, frames). Expects the local
  server below on 127.0.0.1:8765.
- `tools/proof-harness/phase4b_local_server.mjs` — static proxy of a
  pinned main SHA (jsDelivr upstream, disk fallback), request log
  with byte sizes. `PIN_SHA=<sha> node phase4b_local_server.mjs`.

## Remainders (unchanged by this proof, already recorded in #1498)

- Roster-mode edits still fight on the legacy `custom` (Soldier)
  slot; template resolution currently covers blank-mode saves.
- Custom moveset slots are still TODO; created fighters animate on
  the jin bank fallback (logged in-game per the T3-use rule).
