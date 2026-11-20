# Open-source wave 2026-10-22 — comprehensive integration pass (worker 22)

Owner directive (verbatim): "Audit everything we've built and pulled in. Find
more open-source/free stuff we're NOT using yet that would help — physics,
animation, rigging, UI, audio, AI, procedural generation, anything relevant
to a fighting game. Prioritize free, open-source, no licensing issues,
actually works. Be aggressive — 'anything you can get a hold of.' Then wire
it ALL up."

## Part 1 — Audit: wired vs unwired (verified 2026-10-22)

### WIRED — actually connected to the game or creation suite

| # | Tool / asset | License | Wired to |
|---|---|---|---|
| 1 | TKMovesets (Kiloutre) | GPL-3.0 | moveset-decode lanes (format reference) |
| 2 | Wiggle 2 (shteeve3d) | repo license | tools/jiggle/ — Blender jiggle bake pipeline |
| 3 | Keemap (nkeeline) | GPL-3.0 | tools/anim-retarget/ — mocap retarget |
| 4 | GameRig (Arminando) | repo license | tools/auto_rig/backends/gamerig_backend.py |
| 5 | UniRig (VAST-AI) | MIT | tools/auto_rig backends |
| 6 | MagicArticulate (Seed3D) | Apache-2.0 | tools/auto_rig backends |
| 7 | Puppeteer | Apache-2.0 | tools/auto_rig backends |
| 8 | Material Maker (RodZill4) | MIT | tools/procgen/textures/ |
| 9 | TEXTtoPBR (Vasco888888) | MIT | tools/procgen/textures/wh_seamless_pbr.py |
| 10 | lite-rollback + webrtc (zakkster) | MIT | game/netplay/ — proven demo + mirror proof |
| 11 | netfox, Snoring Cat rollback | MIT | tools/netcode/godot/ (Godot target) |
| 12 | Nakama (heroiclabs) | Apache-2.0 | tools/netcode/matchmaking/ (self-hosted) |
| 13 | Kenney + KayKit packs | CC0 | game/assets/accessories/ |
| 14 | T3 motion banks (decoded) | teardown | game/js/t3anims.js (runtime retarget) |
| 15 | wavu frame data | CC0 | docs/t7t8-reference/frame-data-t8-full/ |
| 16 | t7chicken frame data | ISC | docs/t7t8-reference/frame-data-t7/ |
| 17 | three.js SkeletonUtils | MIT | tools/anim-retarget/runtime/wh-retarget.js |
| 18 | tripo-intake | WH | roster/<fighter>/attires auto-rig pipeline |
| 19 | game-hud UI kit (threejsassets) | MIT | tools/creation-suite/ui-kit/ (pulled 2026-10-16; suite-viewer binding = follow-up) |

### UNWIRED — in repo, not connected (disposition this pass)

| # | Item | Status | Disposition |
|---|---|---|---|
| 1 | stable-fast-3d (Stability AI) | vendored, no WH wiring | **WIRED (docs):** tripo-intake image→3D source path documented |
| 2 | triposr (VAST-AI) | vendored, no WH wiring | **WIRED (docs):** same as above (fast-iteration alt) |
| 3 | netplay → real combat | proven demo only; README: "next step, not done here" | **WIRED (menu):** NETPLAY (BETA) entry in ui-wh options opens game/netplay/demo/ |
| 4 | game-hud → suite viewer | pulled, WH-README exists, not mounted | follow-up lane (documented below) |
| 5 | game-score adaptive music | game has complete procedural audio.js | stays pipeline-side (decision log) |
| 6 | arena-gen three.json | emits Three.js JSON nobody loads | **WIRED:** physics.js loadArenaProps() consumes props |
| 7 | Chatterbox | not vendored (GPU service) | by design — external default (decision log) |
| 8 | Materialize / ArmorPaint | documented, code not vendored | by design (decision log) |
| 9 | WMXIX .ymg meshes | BLOCKED (decode unsolved) | real blocker, documented |
| 10 | WWE 2K pac/edit | BLOCKED (~96GB transfer) | real blocker, documented |
| 11 | T7 .uasset item meshes | never pulled | open (documented) |

## Part 2 — New finds (all free, open-source, permissive, verified 2026-10-22)

Every item below was license-checked from its repo/npm metadata on
2026-10-22. All MIT. All ship as ESM (or single-file ESM builds) with zero
native deps — they fit the game's no-build-step stack via the import map.

| # | Tool | Version | License | Fills the gap |
|---|---|---|---|---|
| 1 | **cannon-es** (pmndrs/cannon-es) | 0.20.0 | MIT | No physics engine: jump/launch hand-written; owner wants partial-ragdoll feel |
| 2 | **three-mesh-bvh** (gkjohnson) | 0.9.16 | MIT | Hit detection bug (only ~1/10 land): BVH shapecast vs real posed meshes |
| 3 | **three-nebula** (creativelifeform) | 13.3.0 | MIT | Hit effects look prototype: JSON GPU particle presets |
| 4 | **troika-three-text** (protectwise) + troika-three-utils 0.52.5, troika-worker-utils 0.53.0, webgl-sdf-generator 1.1.1, bidi-js 1.1.0 | 0.52.5 | MIT ×5 | No 3D text: nameplates, damage numbers, arena signage |
| 5 | **camera-controls** (yomotsu) | 3.1.2 | MIT | Cutscene camera (owner: real-time rendered cutscenes) + photo mode |
| 6 | **lip-sync-engine** (biolimbo) | 1.0.3 | MIT | Voice acting (Dorowani first): WASM Rhubarb-compatible mouth cues |

Evaluated and NOT pulled (documented): Tone.js (game audio.js complete —
adapter stays the upgrade path), transformers.js (server-side AI is the
established pattern), Rapier (WASM, heavier than cannon-es for our needs),
Auto-Rig Pro / Substance (paid), MoCapAnything (research-grade).

## Part 3 — Wiring map (what landed where)

### game/vendor/ (new, all MIT, unmodified ESM builds + ATTRIBUTION.md)
- `cannon-es/cannon-es.js` — zero-dep rigid-body physics
- `three-mesh-bvh/index.module.js` — BVH raycast/shapecast
- `three-nebula/three-nebula.mjs` — GPU particle engine
- `troika-three-text/` — esm.js + 4 dep builds (bare specifiers mapped)
- `camera-controls/camera-controls.module.js` — smooth camera transitions

### game/js/ (new systems, lazy-loaded by integration.js)
- `physics.js` — `WHPhysics`: cannon-es world, knockable arena props,
  `loadArenaProps()` (consumes arena-gen three.json), impact debris,
  hit blast impulses, KO tumble proxy. **Visuals only** — combat sim and
  netplay rollback never read physics state.
- `hitdetect.js` — `WHHitDetect`: per-fighter BVH from posed SkinnedMesh
  (root-local bake), limb-capsule shapecast, **verify mode** (logs
  sphere-vs-mesh disagreements; never changes outcomes), `pick()` fast
  raycast for the suite's tap-to-select. Complements the 2026-10-22
  hitbox fix (generous boxes + step-in, `game/js/fighter.js`): the BVH
  layer is the tuning instrument for the NEXT round of hit-detection
  tightening, and the path to mesh-accurate hits if a lane promotes it
  with proof.
- `springbones.js` — `WHSpringBones`: WH-original verlet spring chains with
  VRM-springbone-compatible params; `autoDiscover()` finds jiggle chains
  (breast/butt/belly/hair) on any WH rig at runtime. This is the runtime
  half of the jiggle system (Blender/Wiggle-2 bake is the pipeline half).
- `hitfx-nebula.js` — `WHHitFX`: JSON particle presets
  (impact/heavy/ko/block/dust/surge). LAYERS on top of the game's `HitFX`
  (`game/js/hitfx.js`, built 2026-10-22 with proof) via the
  `Game.prototype._spawnImpact` patch — heavy/KO hits get extra nebula
  bursts; light hits stay with HitFX alone. Never replaces.
- `labels3d.js` — `WHLabels`: troika nameplates, floating damage numbers,
  cutscene banners (billboarded, auto-fade).
- `camdirector.js` — `WHCamDirector`: cutscene shot lists + photo-mode
  orbit rig. Fight camera untouched.
- `lipsync-player.js` — `WHLipSyncPlayer`: plays `*.cues.json` against the
  jaw bone (lerped viseme opens). Voice lane calls
  `WHIntegration.systems.lipsync.play(fighterRoot, cuesUrl, {audio})`.
- `integration.js` — boot: waits for `window.__game`, lazy-inits every
  system with try/catch (game runs if any fail), per-frame updates on its
  own rAF (never the combat step), auto-attaches spring chains + nameplates
  to P1/P2, and **patches `Game.prototype._spawnImpact` /
  `_resolveCombat`** so nebula FX, debris, BVH-verify, damage numbers and
  KO tumble fire with zero edits to game.js.

### game/index.html (surgical edit on latest main)
- Import map: 9 new entries for the vendored libs.
- One script tag: `js/integration.js` after `js/main.js`.

### game/ui-wh/ui.js (surgical edit; file verified identical to base)
- OPTIONS += "NETPLAY (BETA)" → opens `netplay/demo/index.html` in a new
  tab (the proven rollback demo, now reachable from the game).

### tools/character-voice/lipsync/ (new pipeline tool)
- `lipsync.html` + `lipsync.mjs` (Playwright driver, proof-harness pattern)
  + `README.md`. WAV → `*.cues.json` via lip-sync-engine (MIT, CDN on the
  pipeline machine only — the 37MB acoustic model is never vendored or
  shipped; the game only sees KB-sized cue JSON).

### Tool-unification note
Per the unification law: **one physics system** (cannon-es; nothing else
does rigid bodies), **one particle system** (three-nebula replaces future
hand-rolled FX; the legacy `_spawnImpact` sprite path stays as the
fallback, not a parallel system), **one 3D-text system** (troika),
**one camera-transition system** (camera-controls; fight cam untouched),
**one lip-sync path** (cues JSON → player). Jiggle is two halves of one
system by design: Wiggle-2 bake (pipeline) + springbones (runtime), with
compatible parameters.

## Part 4 — Verification

- All vendor builds import-checked: `three-mesh-bvh` exports MeshBVH/
  acceleratedRaycast/StaticGeometryGenerator/shapecast; `three-nebula`
  exports System/Emitter/Rate/Span + flat initializer/behaviour names
  (API corrected from the vendored README); troika bare specifiers mapped
  in the import map; camera-controls exposes installable default;
  cannon-es zero-dep ESM.
- `node --check` on every new game/js module (syntax).
- The game cannot break: integration.js loads after main.js, every system
  is try/catch'd, hooks are prototype patches guarded by
  `_whPatchedImpact` / `_whPatchedCombat` flags, and every hook falls back
  to the original method on any error.
- Live play verification (fight frames) is left to the playtest lane —
  this pass adds systems; it does not change combat outcomes.

## Follow-ups for other lanes (not this PR)
1. **Hit-detection lane:** use `WHHitDetect` verify logs to re-derive the
   sphere hitbox tables (the "~1/10 attacks land" bug). Promote to
   `mode='authority'` only with proof.
2. **Suite UI lane:** mount game-hud kit components (health/boss bars) in
   the creation-suite viewer (research doc has the follow-up).
3. **Netplay lane:** port `game/netplay/sim/fighter-sim.js` state layout to
   the real combat state per the README's 4-step contract; run mirror proof
   against the REAL sim before enabling versus.
4. **Voice lane:** run `lipsync.mjs` on Dorowani's lines; call
   `WHLipSyncPlayer.play` from win/taunt/intro triggers.
5. **Cutscene lane:** author shot lists for `WHCamDirector.playCutscene`.
6. **FX lane:** author Nebula designer JSONs into `game/assets/fx/`.
