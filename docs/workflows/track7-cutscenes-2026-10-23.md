# Track 7 — Cutscenes & story mode (2026-10-23)

Owner directive (verbatim): "Pull all of this stuff in and wire it up and put it to work the best way possible"

## What was done

1. **Researched** all four systems (web search, docs read, API verified in node):
   - Cinematic director: ink/inkjs (MIT) for narrative + Theatre.js core concepts (Apache-2.0 runtime) + Godot Orchestrator trigger patterns (MIT). Studio editor is AGPL — not shipped (runtime-only pattern).
   - Brawler camera: no maintained three.js multi-target brawler cam exists; implemented the public-domain Smash-style algorithm natively on the PR #851 CameraRig math.
   - Yuka.js 0.7.8 (MIT) for NavMesh/pathfinding — vendored ESM build unmodified.
   - Inworld AI / WebLLM / Transformers.js evaluated — all [SPEC ONLY] for this phone-first game (latency, network, mobile WebGPU); the wired default is a combat-state FSM with an LLM provider seam.
2. **Vendored:** `game/vendor/yuka/yuka.module.js` (442 KB), `game/vendor/inkjs/ink.mjs` (128 KB), each with ATTRIBUTION.md + LICENSE.
3. **Wired** `game/js/story/`: `cinematic-director.js`, `brawler-camera.js`, `navmesh.js`, `dialogue-fsm.js`, `index.js`.
4. **Demo story:** `game/story/demo/demo-banter.ink` compiled with inkjs's own compiler to `demo-banter.ink.json` (branching + variables verified at runtime).
5. **Boot wiring:** `game/js/integration.js` systems 8–11 (surgical edit on main's file via API).
6. **Tests:** `game/tests/story-track7.test.mjs` — 15/15 green (`node --test`).
7. **Coordination:** posted Yuka lane split to issue #866 (Track 7 = navmesh/pathfinding; other track = combat state machines; shared vendored build).

## Bugs found & fixed during wiring

- Yuka 0.7.8 `SeparationBehavior` reads `vehicle.neighbors` (caller-maintained), not `behavior.neighbors` — fixed in `WHGrunt.init`.
- `WHDialogueFSM` cooldown bug: `last || 0` treated "never spoke" as "spoke at t=0", suppressing all cooldown lines for the first 8 s of process life — fixed with `last !== undefined` check.
- Yuka `clampMovement` is 4-arg `(region, start, end, out)`; when end is on-mesh `out` is untouched — handled in `clampStep`.

## Repo-law notes

- The shared checkout at ~/workspace/wh-repo was on another agent's branch (`feat/fluid-dynamics-20261023`) in a 3%-sparse checkout → per NO-SPARSE-COMMIT LAW, the commit was built via the Git Data API from main's tree SHA, never from the working tree. No working-tree state was touched.
- License firewall OFF per user override 2026-10-23 — documented (inkjs MIT, Yuka MIT, Theatre core Apache-2.0 / studio AGPL not shipped).
- No UI files touched (ui_sources gate not triggered); no Tekken names in non-technical content; all characters adults (demo content uses only established canon terms).

## Files

- game/js/story/cinematic-director.js, brawler-camera.js, navmesh.js, dialogue-fsm.js, index.js
- game/vendor/yuka/{yuka.module.js,ATTRIBUTION.md,LICENSE}
- game/vendor/inkjs/{ink.mjs,ATTRIBUTION.md,LICENSE.md}
- game/story/demo/demo-banter.ink{,.json}
- game/tests/story-track7.test.mjs
- game/js/integration.js (systems 8–11)
- docs/research/CUTSCENE-STORY-2026-10-23.md

## Post-merge note (2026-10-24 ~00:40 UTC)

- Discovered the combat-AI track had already vendored Yuka on main
  (master @ 10591304, byte-identical to npm 0.7.8 modulo the copyright
  year). Restored their build + LICENSE verbatim; ATTRIBUTION.md now
  carries both lanes. No second Yuka copy.
- integration.js rebased onto current main: Track 4's chrono-grapple
  landed as system 8; Track 7 story systems are now 9-12. Both kept.
