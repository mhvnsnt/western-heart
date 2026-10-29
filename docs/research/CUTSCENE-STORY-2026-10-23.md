# Cutscenes & Story Mode — Track 7 research & integration report

**Date:** 2026-10-23
**Owner directive (verbatim):** "Pull all of this stuff in and wire it up and put it to work the best way possible"
**Repo:** mhvnsnt/western-heart · branch `feat/track7-cutscenes-story`
**License firewall:** OFF per user override 2026-10-23 — everything pulled regardless of license; copyleft components documented below for transparency.

---

## 1. Cinematic director tools — [WIRED]

**Best option: ink/inkjs (narrative) + Theatre.js core concepts (timeline), adapted natively.**

| Candidate | License | Web/three.js fit | Verdict |
|---|---|---|---|
| ink (inkle) + inkjs (JS runtime) | MIT (both) | Native JS, 128 KB, zero deps, runs in any browser | **VENDORED — the branching-narrative layer** |
| Theatre.js `@theatre/core` | Apache-2.0 | Great runtime (Project→Sheet→Object→Sequence, scrub/play) but built for bundler workflows; our game ships no build step | **ADAPTED — sequence engine re-implemented natively** following its core concepts |
| Theatre.js `@theatre/studio` (visual editor) | **AGPL-3.0 (copyleft)** | Editor only, dev-time | NOT shipped; game consumes authored sequence data (runtime-only pattern) |
| Godot Orchestrator (visual scripting) | MIT | Godot-only (GDScript); no web runtime | **ADAPTED — trigger-graph patterns** (flag/proximity/timer/dialogue/combat event nodes → action nodes) re-implemented natively |
| Twine | GPL-family (copyleft) | Web-based, heavier than ink | Rejected — ink covers the need |

**Why this combination.** Cutscenes need two different machines: a *timeline* (keyframes over camera/props/actors, scrub/play) and a *narrative brain* (branches, flags, dialogue prompts). Theatre.js is the best timeline mind-model on the web, but its runtime expects npm/bundler integration and its studio editor is AGPL — so the game's `WHCinematicDirector` implements the Theatre core concepts (Project → Sheet → SheetObject → Sequence, typed props, `onValuesChange`, play/scrub/seek, iteration counts) in dependency-free JS, while the narrative brain is the real thing: the actual inkjs runtime, vendored unmodified. Writers author in Inky, export compiled `.ink.json`, the game runs it.

**Wired:**
- `game/vendor/inkjs/ink.mjs` — inkjs 2.4.0 ESM runtime, unmodified (MIT)
- `game/js/story/cinematic-director.js` — `WHSequence`/`WHSheet`/`WHProject` (Theatre-pattern), `WHTriggerGraph` (Orchestrator-pattern: flag / zone / timer / dialogue-choice / combat triggers → play / dialogue / flag / fn actions), `WHCinematicDirector` (owns both + ink story: `loadStory`, `storyContinue`, `storyChoose`, `storyVar`, `syncFlagsToStory`, shot-list playback)
- `game/story/demo/demo-banter.ink` + `demo-banter.ink.json` — demo story, compiled with inkjs's own compiler; canon-safe (uses only established canon terms: the Trial, the Nine Souls, Tong-Nou)
- `game/js/integration.js` — boots `cinematic` into `window.WHIntegration`, per-frame `update(dt, {playerPos})`, dialogue prompts dispatch `wh-dialogue` CustomEvent for the UI to bind (no UI files touched — ui_sources gate respected)

**Proof:** `game/tests/story-track7.test.mjs` — sequence interpolation/easing, scrub, `onDone`, trigger flag/zone/one-shot behavior, shot playback, and the full ink round-trip (load → 2 lines → 3 choices → branch text → variable increment). 15/15 green.

**Sources:**
- https://github.com/inkle/ink (MIT)
- https://www.gitplanet.com/project/inky
- https://deepwiki.com/theatre-js/theatre (dual license: core Apache-2.0, studio AGPL-3.0)
- https://www.jsdelivr.com/package/npm/@tomorrowevening/theatre-core

---

## 2. Brawler camera controllers — [WIRED]

**Best option: the multi-target "keep everyone in frame" algorithm, built on our own PR #851 CameraRig math.**

| Candidate | License | Fit | Verdict |
|---|---|---|---|
| Smash-bros-style multi-target camera (bounding box → centroid → dolly from hFOV fit) | Public-domain algorithm (Unreal forums tutorial; same math as Cinemachine TargetGroup) | Exact fit for brawler density | **IMPLEMENTED natively** in the repo's CameraRig style |
| Godot Phantom Camera (multi-target follow) | MIT | Godot-only | Patterns noted, not portable |
| three.js addons | — | No multi-target brawler controller exists in three.js examples | — |

**Why not a library:** there is no maintained open-source multi-target brawler camera for three.js — the genre-standard algorithm is a ~40-line public-domain recipe (Unreal Engine forums "Local Multiplayer Camera" tutorial; Smash Bros blueprint tutorial): bounding box of all targets → weighted centroid → dolly distance `d = halfExtent / tan(hFov/2)` per axis, take the max. Our game *already* ports this exact formula for 2 fighters in `game/js/scene.js` (PR #851, Tekken CameraRig port). The right move is extending that rig to N targets, not importing a foreign one.

**Wired:** `game/js/story/brawler-camera.js` — `WHBrawlerCamera`:
- N-target weighted framing (player weight 2×), same fit math/constants/portrait behavior as PR #851 (FOV widens instead of pulling past the 10.5 m arena-wall cap), same exponential damping family
- **No view clipping in tight spaces:** injectable obstacle tester; in-game wired to a `THREE.Raycaster` over arena collidables, dolly clamped to `hit − 0.35 m`
- Trauma-based shake channel, cinematic framing overrides (`setFraming({zoomMul, focus})`) for the director's push-ins
- Opt-in: `enable()`/`disable()` (restores FOV); the 1v1 fight camera in `scene.js` is untouched — build on, don't replace, per the track brief
- `game/js/integration.js` — boots `brawlerCam`, default target provider reads `game.p1`/`game.p2` + the Heart-and-Mind-Within grunt squad (`window.__heartmind`), per-frame update only when enabled

**Proof:** tests — weighted centroid leans to the player, wider threat spread pulls the camera back, portrait widens FOV under the wall cap, wall clamp shortens the dolly. (Live arena raycast verification belongs to the Heart-and-Mind-Within phase-2 wiring.)

**Sources:**
- https://forums.unrealengine.com/t/local-multiplayer-camera/476089 (bounding-box + `a = o / tan(θ)` fit algorithm)
- https://forums.unrealengine.com/t/tutorial-smash-bros-style-multiplayer-camera-system-blueprints/27721

---

## 3. Yuka.js NavMesh — [WIRED] (pathfinding lane)

**Best option: Yuka.js — no contest.**

| Candidate | License | Web/three.js fit | Verdict |
|---|---|---|---|
| **Yuka (Mugen87)** | MIT | Engine-independent, three.js-first examples, NavMesh + NavMeshLoader + Corridor + steering in one package | **VENDORED 0.7.8** |
| three-pathfinding (donmccurdy/PatrolJS) | MIT | three.js-only, unmaintained since ~2017 | Rejected — stale, no steering |
| recast-navigation (WASM Recast) | MIT | Powerful but WASM build pipeline + heavy for phone | Rejected — overkill for arena zones |

**Wired:**
- `game/vendor/yuka/yuka.module.js` — Yuka 0.7.8 ESM build, unmodified (MIT)
- `game/js/story/navmesh.js`:
  - `WHNavMesh` — `buildFromRects` (arena floor quads → merged convex regions), `buildFromTriangles` (geometry → navmesh), `findPath` (corridor-smoothed waypoints), `clampStep` (border slide), `regionFor`/`contains`
  - `WHNavZoneSet` — multi-level structures: zones per level + off-mesh links (stairs/doors/ledges), cross-zone `route()` returning segments
  - `WHGrunt` — Yuka `Vehicle` + Seek/Separation on the navmesh: pursue / flank (ring slots) / swarm, repath throttle, steps clamped to the mesh
  - `WHSquad` — dozens of grunts, one `update(dt)`, ring spawn, shared focus
- `game/js/integration.js` — boots `navmesh` (`WHNavZoneSet` + `buildStageZone(zoneId, rects)` + `makeSquad`) for Heart-and-Mind-Within phase-2

**Verified API notes (Yuka 0.7.8, node-tested 2026-10-23):** contours need positive-area CCW winding in the xz-plane; `fromPolygons` merges coplanar+convex regions; `clampMovement(region, start, end, out)` is 4-arg — when the end point is already on the mesh, `out` is untouched (handled in `clampStep`); `SeparationBehavior` reads `vehicle.neighbors` (caller-maintained). Two real bugs caught during wiring (cooldown-epoch bug in the FSM, `neighbors` on the wrong object) — both fixed, both covered by tests.

**Coordination (issue #866):** lane split posted — Track 7 owns **NavMesh/pathfinding** (`NavMesh`, `Corridor`, `Vehicle` + steering); the other track owns **combat state machines** (`State`, `StateMachine`, `GoalEvaluator`). Both share this one vendored `yuka.module.js` — no duplicate pulls.

**Proof:** tests — cross-region path, clamp keeps steps on the mesh, 8-grunt squad closes distance with separation (min pairwise dist > 0.15 m after 2 s).

**Sources:**
- https://deepwiki.com/Mugen87/yuka/5.2-navigation-meshes
- https://mugen87.github.io/yuka/docs/navigation_navmesh_NavMesh.js.html
- https://www.jsdelivr.com/package/npm/three-pathfinding (rejected alternative)

---

## 4. Inworld AI / LLM state machines — [SPEC ONLY] + [WIRED] fallback

**Evaluation:**

| Option | License/cost | Runtime reality on our target (user's phone) | Verdict |
|---|---|---|---|
| **Inworld AI** (Character Engine + web/JS SDK) | Proprietary, usage-priced; needs account + API key + session-token server | Network round-trip per line (latency), needs connectivity, streaming TTS optional — workable for *menu/hub* NPC chat, wrong for *in-fight* banter | **SPEC ONLY** — integration seam designed, not wired |
| Server-side LLM (any API) via the seam | API cost per call | Same latency problem in-fight; fine for pre/post-fight | **SPEC ONLY** — same seam |
| WebLLM (in-browser, WebGPU) | Apache-2.0 | Desktop-class GPUs; mobile WebGPU is inconsistent, iOS tabs die past ~400 MB, battery/thermal cost — effectively desktop-only | **SPEC ONLY** — documented, not shipped |
| Transformers.js (in-browser) | Apache-2.0 | Same mobile story; sub-1B models too weak for characterful dialogue | **SPEC ONLY** |
| **Combat-state FSM (this track)** | WH-original, zero deps | Instant, offline, deterministic, phone-safe | **[WIRED] — the default brain** |

**Why the FSM is the right default.** The track's concrete ask — *"enemy banter changes based on damage taken"* — is a state-machine problem, not an LLM problem: event (damage ≥ X, HP ≤ Y%, KO, wave start) → priority-ordered line selection → cooldowns. An LLM adds seconds of latency and a network dependency to a 60 fps fight for lines a designer already wrote. The LLM belongs *around* the fight (hub NPCs, post-fight interviews), never *in* the hot loop.

**Wired:** `game/js/story/dialogue-fsm.js` — `WHDialogueFSM`:
- Events: `fightStart/roundStart/roundEnd/damageTaken/hpLow/hpCritical/ko/timeout/waveStart/waveClear/taunt`
- Lines: `{id, speaker, line, event, priority, cond:{minDmg,maxHpPct,minHpPct,wave,tags}, once, cooldownMs}` — the FSM *selects*, never authors; lines register from the game's canon data (`registerLines`, `registerBeats` reads the existing `versus-banter.js` beat contract)
- `watchHp()` — threshold watcher firing `hpLow`/`hpCritical` once per fighter per fight
- **Inworld-compatible seam:** `toInworldEvent()` formats combat state as a structured character-event payload; `setLLMProvider({generateReply})` + `emitAsync()` asks the provider with a 1200 ms timeout and falls back to the FSM on failure/offline — Inworld's web SDK (or any server LLM) slots in here later with zero changes to the fight code
- `game/js/integration.js` — boots `dialogue`, seeds from `versus-banter.js`, `bindFight(p1Id, p2Id)` for pair-key banter, emits `wh-dialogue-line` CustomEvent for the UI

**Proof:** tests — threshold selection (5 dmg silent / 50 dmg fires the `minDmg:40` line), hp watcher once-per-fight semantics, envelope shape.

**Sources:**
- https://gamefromscratch.com/inworld-ai-powered-npcs/ (Inworld web/JS API)
- https://blog.jeffschomay.com/adding-inworld-ai-characters-to-an-existing-game-part-3-integration-and-analysis-826172445e10/rss.xml (web SDK integration notes)
- https://www.mograblog.com/2026/09/webllm-running-smart-models-in-browser/ (WebLLM vs Transformers.js)
- https://dev.to/roman_solodkyi/zero-cost-ai-running-llms-locally-in-the-browser-o8n (mobile verdict: WebLLM desktop-only)
- https://nearform.com/digital-community/web-ai-runtimes-five-ways-to-run-a-language-model-in-the-browser/ (iOS tab-death past ~400 MB)

---

## 5. Status board

| System | Status | Paths |
|---|---|---|
| Cinematic director (sequences + triggers) | [WIRED] | `game/js/story/cinematic-director.js`, `game/js/story/index.js` |
| inkjs narrative runtime | [WIRED] (vendored) | `game/vendor/inkjs/ink.mjs`, `game/story/demo/demo-banter.ink{,.json}` |
| Theatre.js studio editor | [RESEARCHED] (AGPL, not shipped — runtime-only pattern) | — |
| Brawler camera (multi-target) | [WIRED] | `game/js/story/brawler-camera.js` |
| Yuka NavMesh / grunt pathfinding | [WIRED] (vendored 0.7.8) | `game/vendor/yuka/yuka.module.js`, `game/js/story/navmesh.js` |
| Yuka combat state machines | Other track's lane (coordination posted #866) | — |
| Combat-reactive dialogue FSM | [WIRED] | `game/js/story/dialogue-fsm.js` |
| Inworld AI / runtime LLM | [SPEC ONLY] (seam ready) | `WHDialogueFSM.setLLMProvider` / `toInworldEvent` |
| In-game boot wiring | [WIRED] | `game/js/integration.js` (systems 8–11) |
| Tests | [WIRED] 15/15 green | `game/tests/story-track7.test.mjs` |

## 6. Integration-law compliance

Per the repo INTEGRATION LAW, story systems wire *into* existing structure, not alongside it:
- The cinematic director drives the existing `WHCamDirector` shot grammar and the existing story-beat UI (via `wh-dialogue` / `wh-dialogue-line` events) — no new menus, no UI files touched (ui_sources gate not triggered).
- The brawler camera extends the PR #851 CameraRig math; `scene.js` untouched.
- The dialogue FSM consumes `versus-banter.js` / `intro-interactions.js` data; authors nothing.
- The navmesh plugs the `HM_TEARDOWN` seam in `heartmind.js` — phase-2 density (simultaneous multi-enemy) gets movement for free when the teardown tables land.

## 7. Follow-ups (not this track)

- **Menus/UI binding:** `wh-dialogue` / `wh-dialogue-line` events need a subtitle/choice UI — the menus track's lane (teardown-sourced, ui_sources-gated).
- **Inworld/LLM provider:** needs an owner decision (account, key custody, cost) — the seam is ready; the user never takes custody of logins per standing rules, so this waits on explicit owner setup.
- **Heart-and-Mind-Within phase-2:** `buildStageZone` per stage + squad spawn tables when the T5 teardown wave data lands in `HM_TEARDOWN`.
- **Theatre studio (AGPL):** if the owner ever wants visual timeline authoring, the studio editor can run as a *dev-only* tool against exported sequence JSON — never shipped in the game bundle.
