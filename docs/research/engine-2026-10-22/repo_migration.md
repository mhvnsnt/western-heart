# Western Heart repo: migration constraints from the three.js web game to a native mobile engine (Godot 4 target)

Scope and method: a read-only inventory of the local checkout `/home/user/western-heart`. After `git fetch origin main`, the checkout was at branch `claude/amazing-keller-p8644u` @ `e3ae81b76` (2026-10-22). That commit contains current `origin/main` (`b7aaa251f`, the merge of PR #474); `git log HEAD..FETCH_HEAD` is empty. The clone is shallow (`git rev-parse --is-shallow-repository` = true, 806 commits visible). Every "source" below is a repo file. Links point to GitHub blobs at commit `e3ae81b76` (the repo is private). Counts and sizes come from my own scans: `du`, `wc`, `find`, and a Python GLB-header parser that reads only each GLB's JSON chunk. Each scan is labeled "local scan" next to the path it measured.

Base URL used below: `https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/`

---

## Q1. The existing Godot project (lab/game): config, milestones, systems, tests, history

### Takeaway
`lab/game` is a small, working Godot **4.3** project. It runs on the **GL Compatibility** renderer, including on mobile, and has **only a Web export preset** (no Android or iOS). It has 7 GDScript files (745 lines), a data-driven 4-slot T3 MoveTable, a playable 1v1 slice (Pantera vs King, best of 3) with keyboard, gamepad and on-screen touch buttons, and real decoded T3 clips. Headless tests exist, but it was built in one burst on 2026-10-14. Since then it has only received asset drops, and it has no netcode wired in.

### Cited Findings
**Project config**
- `project.godot`: `config_version=5`, `config/features=PackedStringArray("4.3", "GL Compatibility")`, `renderer/rendering_method="gl_compatibility"` **and** `renderer/rendering_method.mobile="gl_compatibility"`, viewport 1280×720, `stretch/mode="canvas_items"`, `window/handheld/orientation=4`, `pointing/emulate_touch_from_mouse=true`, `physics_ticks_per_second=60`, `textures/vram_compression/import_etc2_astc=true` — [lab/game/project.godot](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/project.godot)
- `export_presets.cfg` holds a single preset, `[preset.0] name="Web" platform="Web"`. It sets `variant/thread_support=false`, `export_path="build/web/index.html"`, `include_filter="data/moves/*.json, attire/*/*.json"` and `vram_texture_compression/for_mobile=true`. **There is no Android or iOS preset** — [lab/game/export_presets.cfg](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/export_presets.cfg)
- `lab/game/.gitignore` ignores `.godot/` and `build/`, so a fresh clone needs `godot --headless --import` before tests (the M2 run did exactly this) — [lab/game/.gitignore](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/.gitignore); [docs/workflows/WORKLOG.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/workflows/WORKLOG.md)
- `lab/game/` has no `addons/` directory. Its top level is `assets attire data export_presets.cfg project.godot scenes scripts tests tools` (local scan `ls lab/game`). So none of the vendored Godot netcode addons are installed in the project.

**Size**
- `lab/` holds 155 files and is 78 MB. Of that, `lab/game/assets` is 25 MB, `lab/game/data` 616 KB and `lab/source_assets` 45 MB (the owner's original GLBs) — local scan `du -sh lab/*`.
- `lab/game/assets` holds 53 GLBs (22,752,016 bytes):
  - 15 `t3_<name>.glb`: 18 joints, 11 authored clips each.
  - 16 `t3_<name>_t3real.glb`: 18 joints, 40 real decoded clips each (King has 42).
  - 19 `t3body_<name>.glb`: 18 joints, 11 clips.
  - `pantera_leoman.glb` (22 joints, 11 clips) and `pantera_leoman_t3real.glb` (42 clips).
  - `t3_stage_l.glb` (stage, no skin).
  - Source: local GLB-header scan of [lab/game/assets](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/lab/game/assets).

**Milestones (lab/README.md)**
- **M1:** `skeleton/canonical_skeleton.json` defines "WH-Canonical-22" (Mixamo-compatible names, Y-up meters, faces +Z). `retarget_maps.json` maps three source rigs (`tekken3_rigid27`, `mixamo49`, `rigify13`). `t3_to_gltf.py` converts KMD + stance OBJ into a rigid-skinned GLB with 11 combat clips. `rig_check.py` provides the automated rig check.
  - Honest gaps listed for M1: only King had a decoded stance at the time; about 43% of KMD faces reference undecoded "imported" seam vertices (joint gaps/holes); TIM textures are not applied (vertex colours only) — [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md)
- **M2:** `MoveTable` (GDScript) computes frame data at 60 fps:
  - startup = `active_first`;
  - active = `active_last − active_first + 1`;
  - recovery = `stream_frames − active_last`;
  - damage on the T3 170 life bar;
  - hit freeze falls back to 6/9/12;
  - Lab advantage rule: HIT_ADV light +8 … heavy +10, BLOCK_ADV light +1 … heavy −8.
  - Gap: "input → T3 command-branch mapping (the `branches` field) isn't interpreted yet. Slots are light/medium/heavy/grab" — [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md); [lab/game/scripts/move_table.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/scripts/move_table.gd)
- **M3 ("playable 1v1 slice (Godot 4.3, GL Compatibility, HTML5)"):**
  - P1 is Pantera (Leo-Man attire, auto-rigged Tripo GLB) and P2 is a CPU King (T3 KMD import wearing the Bannon mask), on King's T3 stage `l`.
  - Best of 3, 60 s rounds, hit freeze, block, an unblockable grab, knockback, K.O.
  - Controls: keyboard, gamepad and touch (on-screen buttons shown automatically on touch devices or with `--touch`).
  - Web export command: `godot --headless --path lab/game --export-release Web build/web/index.html` — [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md)

**Scripts** (local scan `wc -l`)
- `fighter.gd` 223 lines: a state machine. States are idle, walk, attack, jump, crouch, crouch_hold, sidestep, hitstun, blockstun and ko.
  - A `REAL` map plays decoded `t3_*` clips. `JUMP_PRE=8`, `JUMP_FRAMES=48`, `CROUCH_ENTRY=8` and `SIDESTEP_FRAMES=14` all come from the decoded T3 branch lists (EXE table 0x80017C78, BranchFind 0x8002E078).
  - Animation is driven by `AnimationPlayer.seek()` with `speed_scale=0`, so it is frame-driven, not time-driven — [lab/game/scripts/fighter.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/scripts/fighter.gd)
- `main.gd` 235 lines: match arbiter in `_physics_process`.
  - InputMap actions `p1_left/right/up/down/light/medium/heavy/grab/block/mask` are bound to keys and pad buttons.
  - `--autoplay` drives P1 through the same InputMap path.
  - CLI flags: `--p1-attire=`, `--p1-char=`, `--p2-char=`, `--shots=`, `--quit-after-match`, `--no-mask` — [lab/game/scripts/main.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/scripts/main.gd)
- `hud.gd` 68 lines: life bars, timer, pips, popups.
  - The touch UI is 7 fixed-position `Button`s (`<`, `>`, BLK, LP, MP, K, GRB, each 100×90 px) that call `Input.action_press/release`.
  - There is no virtual joystick and no up/down touch control — [lab/game/scripts/hud.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/scripts/hud.gd)
- `ai.gd` is 43 lines. `attire.gd` is 62 lines (a `BoneAttachment3D` loading `<id>.manifest.json` with per-rig presets and material params). `height_scale.gd` is 46 lines (reads `data/characters/heights.json`). `move_table.gd` is 68 lines. Together these 7 scripts total 745 lines — local scan of [lab/game/scripts](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/lab/game/scripts)
- Tool scripts in `lab/game/tools/*.gd` (5 files, 228 lines) render portraits, cards, title hero and pose exports. Outside `tools/netcode`, the only other GDScript in the repo is `game/ui-wh/tools/render_card.gd`. Total non-vendored GDScript is 1,228 lines (local scan `find -name '*.gd'`).

**Data**
- `lab/game/data/moves/*.json` holds 7 fighters (king, jin, bryan, heihachi, xiaoyu, yoshimitsu, gunjack). Format keys: `fighter, summary{light,medium,heavy,grab}, rows{<t3_row>: {active_first, active_last, stream_frames, damage, hit_freeze, reaction, attack_class}}, attack_rows[], source`. King has 298 attack rows.
  - This is a **different, much smaller format** than the web game's `game/assets/movesets/*.json` (see Q4) — local scan; [lab/tools/export_moves.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/tools/export_moves.py)

**Tests** (in `lab/game/tests`)
- `test_move_table.gd` (SceneTree script): checks 7 fighters × 4 slots.
- `test_height_scale.gd`.
- `qa_playtest.gd` (127 lines). It replaces P2 with a scripted dummy, drives P1 through InputMap, logs per-frame state and writes `QA|` lines plus `build/qa/qa_log.csv`. It has an optional `--capture` mode under xvfb.
- `run_match_headless.sh`: `godot --headless --path . --quit-after 20000 -- --autoplay --quit-after-match` must print `MATCH RESULT wins=[2, x]` or `[x, 2]`.
- Python test: `lab/tests/test_rig_check.py` — [lab/game/tests](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/lab/game/tests); [lab/game/tests/qa_playtest.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/tests/qa_playtest.gd)

**Recorded headless runs**
- On Godot 4.3, `test_move_table.gd` PASSed, and the headless CPU-vs-CPU match printed `MATCH RESULT wins=[1, 2] rounds=3 hits=35 blocks=32`. After the movement-states update it printed `wins=[2, 1] rounds=3 hits=43 blocks=37 frames=7420 moves={jump_up:18, crouch:11, crouch_hold:5, sidestep_a:6, sidestep_b:6}` — [docs/anim/PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md)
- How it was run: "Godot 4.3-stable was installed headless at /workspace/tools/godot. Web export templates were streamed out of the .tpz with python `stream-unzip`". Capture used "Godot Movie Maker under xvfb with Mesa llvmpipe → ffmpeg H.264". The "HTML5 export uses the `web_nothreads` template" — [docs/workflows/WORKLOG.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/workflows/WORKLOG.md)
- The M3 capture `lab/docs/m3_ffprobe.txt` records h264, 1280×720, 60 fps, 4,026 frames, 67.1 s — [lab/docs/m3_ffprobe.txt](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/docs/m3_ffprobe.txt)
- The playtest method says "`godot --version` needs 4.3.x (box has /usr/local/bin/godot 4.3.stable)". The standing rule for agents is to rerun `qa_playtest.gd` and `run_match_headless.sh` after every change — [docs/PLAYTEST-METHOD.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/PLAYTEST-METHOD.md); [docs/HOW-TO-CONTINUE.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/HOW-TO-CONTINUE.md)

**Known Godot-import defect**
- `game/assets/models/demonio.glb` has correct weights, "but the Godot 4.3 render still shows the arms in T-pose while the legs move". The next step named there is to check how Godot names and imports the 49 Mixamo bones.
- `game/assets/models/pantera.glb` has a mirrored skin: "5,805 of 5,805 side-weighted vertices are skinned to the opposite-side bone" — [docs/anim/PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md)

**Git activity on lab/**
- The original development branches are all dated 2026-10-14:
  - `origin/grok/lab-skeleton-importer` @ 3321c0826 (M1);
  - `origin/grok/lab-move-interpreter` @ 504bf5ded (M2);
  - `origin/grok/lab-playable-slice` @ 4a58f1a6c (M3);
  - `origin/feat/lab-movement-states` @ f4b28b292 (crouch/jump/sidestep).
  - Source: `git log -1` on each remote branch.
- Visible history on lab/ in this shallow clone:
  - ad97528f0 (10-16 merge);
  - cd3bf387c (10-17, the DXMMII wipe);
  - 00e352263 (10-17, restore of 54,432 files);
  - ea42298c8 (10-21, `*_t3real.glb` for 10 remainder banks);
  - 9b669ca62 (10-21, nine `t3_<name>.glb` plus 10 lines in `lab/tools/t3_motion_bake.py`).
- `lab/game/scripts` and `lab/game/tests` were last touched by the 10-17 restore commit, and before that only by the 10-14 branches — `git log -- lab/game/scripts lab/game/tests`.

### Inferences
- **The project is not configured for native mobile yet.** It needs an Android (and/or iOS) export preset, a keystore and export templates. The renderer also needs a decision. The owner's directive asks for "Godot 4's native mobile rendering pipeline (Vulkan / GLES3)". The Lab currently forces `gl_compatibility` even on mobile. In Godot terms, Compatibility is the GLES3 path and "Mobile" is the Vulkan path, so the directive can be met either way, but someone has to choose. (That Godot renderer mapping is general Godot knowledge, not from the repo.)
- `window/handheld/orientation=4` most likely means sensor-landscape in Godot 4's enum (general Godot knowledge). The owner's 2026-10-22 directive requires **portrait** support in the creation suite (see Q6), so orientation handling has to change.
- The Lab's combat core is a thin 4-slot subset:
  - It does not interpret Tekken notation, strings, specials, hit levels or juggles.
  - It doesn't use the 99-file web moveset schema.
  - The web game's TekkenBuffer and T3 guard/hit-word rules are **not yet ported** (Q3).
  - It is a working skeleton (input → state machine → frame-seeked clips → HUD → headless test) to grow from, not a feature-complete port.
- The Lab is pinned at 4.3. The engine survey recommends 4.7, and the snoringcat rollback addon targets 4.7+ (Q2). An engine-version bump is therefore a likely early migration task, with 4.7 breaking changes to check.

### Gaps
- I could not run any Godot test (no Godot binary here; see Q7), so I can't confirm the Lab still passes on the current tree. The only evidence is the 2026-10-14 records.
- `git log` on lab/ is truncated by the shallow clone. I could not determine the full commit count or authorship before 2026-10-16 beyond the remote branch tips.
- I did not open `scenes/main.tscn` or `ai.gd` in full. Their roles above come from file headers and `main.gd`.

---

## Q2. Vendored Godot netcode (tools/netcode/godot): projects, versions, licenses, fit

### Takeaway
Three Godot 4 network addons are vendored as **reference copies, not installed in lab/game**:
- netfox (MIT; plugin.cfg says 1.49.4);
- Snoring Cat godot-rollback-netcode (MIT; plugin 1.0.2; targets Godot 4.7+);
- nakama-godot (Apache-2.0; changelog top 3.4.0).

The repo's own netcode doc sets a determinism law: a fixed-point combat sim, with Godot physics used only for visuals. The web build already has a deterministic integer reference sim to port.

### Cited Findings
- Tree: `tools/netcode/godot/{netfox (1.1 MB), snoringcat-rollback-netcode (996 KB), nakama-client (712 KB)}` plus README, `tools/netcode/matchmaking/docker-compose.yml` (Nakama self-host) and `tools/netcode/streaming/SUNSHINE-PLAYTEST-GUIDE.md` — local scan; [tools/netcode/godot/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/README.md)
- **netfox**
  - Source foxssake/netfox, "main @ 2026-10-16", MIT (Copyright 2023 Gálffy Tamás).
  - Four addons: netfox, netfox.extras, netfox.internals, netfox.noray. Each `plugin.cfg` has `version="1.49.4"`, while ATTRIBUTION.md says "(v1.35.x line…)", a **discrepancy inside the repo**.
  - 10,668 GDScript lines — [tools/netcode/godot/netfox/ATTRIBUTION.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/netfox/ATTRIBUTION.md); [netfox/netfox/plugin.cfg](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/netfox/netfox/plugin.cfg)
- **Snoring Cat godot-rollback-netcode**
  - Source snoringcatgames/godot-rollback-netcode, "main @ 2026-10-16", MIT (Copyright 2025-2026 Snoring Cat LLC). `plugin.cfg` `version="1.0.2"`; CHANGELOG top entry `[0.1.0] — 2026-04-25`.
  - Pure GDScript, no GDExtension; transports are ENet, WebSocket and WebRTC.
  - ATTRIBUTION says "copy … to `res://addons/rollback_netcode/` in a Godot **4.7+** project". Its `.github/parse-check/project.godot` declares features "4.7"; its `examples/simple_game/project.godot` declares "4.3", "Forward Plus".
  - 16,622 GDScript lines, including tests and examples — [tools/netcode/godot/snoringcat-rollback-netcode/ATTRIBUTION.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/snoringcat-rollback-netcode/ATTRIBUTION.md); [plugin.cfg](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/snoringcat-rollback-netcode/plugin.cfg)
- **nakama-godot**: Heroic Labs, "main @ 2026-10-16", Apache-2.0; CHANGELOG top `[3.4.0] - 2024-03-19`; Godot 4.0+ client for accounts, matchmaker and leaderboards — [tools/netcode/godot/nakama-client/ATTRIBUTION.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/nakama-client/ATTRIBUTION.md)
- **Repo recommendation table**:
  - "Godot 4 desktop (target)" → netfox RollbackSynchronizer (server-authoritative).
  - "Godot 4 web export (if ever)" → snoringcat (P2P GGPO-shaped, WebRTC).
  - "Determinism law (both lanes): the fighter sim must be integer/fixed-point, seeded RNG in lockstep, no wall-clock … Godot's built-in physics is NOT guaranteed deterministic across machines — run combat on a custom fixed-point sim (port `game/netplay/sim/fighter-sim.js` semantics), use physics only for visuals." — [tools/netcode/godot/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/README.md)
- Pull-in log, step 3: "Godot 4 project: drop in `netfox` (desktop) or `snoringcat` (web export); re-run a `mirror.mjs`-style checksum proof against the GDScript sim before enabling versus." Excluded options: GGRS/bevy_ggrs ("Relevant only if we go Rust/Bevy — we didn't (Godot 4 is the target)"), orbitnet (Rust GDExtension, no web), and dsnopek's addon (repo 404 on 2026-10-16) — [tools/netcode/PULLIN.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/PULLIN.md)
- **Web reference sim**: `game/netplay/sim/fighter-sim.js` (223 lines) is "ALL arithmetic … integer (positions in 1/16 px) — no floats, no Math.random, no Date". It covers walk, jump, LP/HP/LK/HK, block, hitstun/blockstun, KO and a 3600-frame round. `mirror.mjs` reports lockstep and real-rollback runs with 0 desyncs. lite-rollback is 1.2.1 (MIT); `inputDelay = 2 frames` — [game/netplay/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/netplay/README.md); [game/netplay/sim/fighter-sim.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/netplay/sim/fighter-sim.js); [tools/netcode/PULLIN.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/PULLIN.md)

### Inferences
- The Lab's `fighter.gd` and `main.gd` use floats (positions in metres, `kb_vel *= 0.85`) and Godot `Input`. That violates the repo's own determinism law, so rollback needs a fixed-point combat-state refactor (port fighter-sim.js semantics), not a drop-in addon.
- On mobile, netfox's server-authoritative lane and noray punch-through, or the P2P snoringcat lane, are both GDScript and would work on Android/iOS exports. Snoringcat's 4.7+ requirement pushes the Lab off 4.3.

### Gaps
- I could not verify the exact netfox upstream version (the plugin.cfg 1.49.4 vs the ATTRIBUTION 1.35.x claim).
- No vendored addon has been tested inside `lab/game`, and the repo records no Godot rollback proof run.

---

## Q3. The current web game (game/js): modules, sizes, engine-agnostic logic vs three.js-specific code

### Takeaway
The web game is **25 ES modules, 12,049 lines / 579,575 bytes** of hand-written JS with vendored three.js and no build step. About a third is pure data and logic that ports almost mechanically: movesets, TekkenBuffer, roster, attires, modes, AI. Rendering, staging, retargeting and the CCD-IK combat layer are heavily three.js-bound. Menus and UI are DOM/HTML-bound. The combat loop runs at **120 Hz with floats, `Math.random` and `performance.now`**, so it is neither deterministic nor matched to the Lab's 60 Hz.

### Cited Findings
**Module sizes** (lines / bytes, local scan `wc -lc game/js/*.js` at e3ae81b76)
- Largest modules:
  - stages.js 1,609 / 82,284
  - fighter.js 1,419 / 69,832
  - modes.js 1,115 / 54,364
  - assets.js 1,061 / 55,933
  - t3anims.js 917 / 47,302
  - main.js 688 / 28,121
  - select-screen.js 656 / 27,979
  - movesets.js 558 / 25,276
  - menus.js 545 / 21,536
  - game.js 508 / 20,482
  - heartmind.js 497 / 24,318
  - episodes.js 369 / 19,229
  - roster-full.js 302 / 25,590
- Smaller modules:
  - customization-consumer.js 281
  - input.js 253
  - attires.js 233
  - audio.js 202 (procedural Web Audio)
  - dome-params.js 184
  - transform-cinematic.js 181
  - scene.js 149
  - ai.js 111
  - custom-fighter.js 100
  - ui-wh-bridge.js 92
  - characters.js 12
  - attire-customizations.js 7
- Source: [game/js](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/game/js)
- "No build step. No CDN — Three.js and its addons are vendored in `game/vendor/`." The two original fighters use "Mocap Idle/Walk/Run base layer + CCD inverse-kinematics combat layer" — [game/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/README.md)

**Coupling** (local grep: lines containing `THREE.` / lines with `document.|window.|localStorage`)
- three.js-heavy modules:
  - stages.js 198 / 2
  - t3anims.js 36 / 0
  - fighter.js 21 / 8
  - select-screen.js 17 / 7
  - assets.js 14 / 0
  - game.js 7 / 0
- Zero `THREE.` references:
  - movesets.js (7 DOM)
  - input.js (7 DOM)
  - ai.js (0 DOM)
  - roster-full.js (0 DOM)
  - attires.js (3 DOM, localStorage `wh_attires_v1`)
  - modes.js (13 DOM)
  - episodes.js (10 DOM)
  - heartmind.js (9 DOM)
  - menus.js (71 DOM)
  - main.js (82 DOM)

**Loop and determinism**
- `game.js` uses `const FIXED_DT = 1 / 120;` with a `requestAnimationFrame` accumulator loop that "Resolves hitbox/hurtbox collisions every fixed step" — [game/js/game.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/game.js)
- Non-determinism sources (local grep):
  - `Math.random`: fighter.js 5, ai.js 12, stages.js 51, game.js 1;
  - `performance.now`: fighter.js 2, movesets.js 4, input.js 4.

**TekkenBuffer (engine-agnostic, movesets.js)**
- A 60-entry circular per-frame direction history (`HIST_LEN`).
- `_doubleTap` ports T3 FUN_8002CB08/FUN_8002CBF0 with `DOUBLE_TAP_BUDGET`.
- `_seqMatch` ports T3 InputSequenceMatch 0x8002CCD8.
- Dash latch `DASH_FRAMES`.
- It still keeps a `performance.now()`-timed `dirEvents` list for legacy motion matching.
- Timing constants come from `game/assets/movesets/t3_input_tables.json` (format `wh-t3-input/1`, `history_frames: 60`, `double_tap_budget: 19`, source EXE `SLUS_004.02` sha256-pinned) — [game/js/movesets.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/movesets.js); [tools/moveset-merge/t3_input_tables.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/moveset-merge/t3_input_tables.py)

**T3 guard/hit rules (fighter.js, logic-only but embedded in the three.js Fighter class)**
- `_guardBits()` and `canBeHitBy(move)` implement "T3 HitClassify: guarded when (guard & attack word) != 0 and the defender faces the attacker". Standing guard is state 0x1052 and crouching guard 0x2829; the HitClassify address is 0x80044D24.
- Attack words: high 0x412, mid 0x217, low 0x10F, s.mid 0x31F, unblockable 0x607. The fallback is mid 0x217 when no decoded level exists. Lows whiff vs airborne — [game/js/fighter.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/fighter.js)

**t3anims.js (three-specific)**
- Loads wh-anim/1 clips and converts them to `THREE.AnimationClip` (`jsonToClip`).
- Decodes `rows.pack.json` (`b64i16`, `decodePackRow`).
- Runtime retarget: `retargetClipToRig`, `analyzeRig`, `canonBoneName` (Mixamo/Biped/LR-style name canonicalisation), `bankFacing`/`turnSkeleton` facing fixes, and per-instance `retargetT3Clips`.
- `T3_CLIP_DEFS` maps 24 game actions to clip files (stance, intro, light/medium/heavy/grab, block, hit, launch, ko, win, walk, dash, crouch, backdash, jumps, sidesteps) — [game/js/t3anims.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/t3anims.js)

**UI layers**
- `game/ui-wh/` (8.1 MB): an HTML/CSS/JS menu UI in a full-screen iframe over the canvas (`ui-wh-bridge.js`). It contains 2 HTML, 2 CSS, 5 JS and 3 MJS files plus 16 PNGs.
- `packages/creation-suite/src`: 13 modules, 59,023 bytes; 7 of 13 import three. `dna.js`, `catalogs.js`, `slotmap.js`, `menu.js`, `layering.js` and `index.js` don't.
- The design doc marks `regions.js` as "no three; Godot port reads the same table" and plans "a GDScript port of `regions.js` + `secondary.js`" for the Lab.
- Sources: local scan; [game/js/ui-wh-bridge.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/ui-wh-bridge.js); [docs/creation-suite/DESIGN.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/creation-suite/DESIGN.md)
- Web tests: `game/tests/` has only 2 Node tests (`fighter-completeness.test.mjs`, `model-key-guard.test.mjs`). The CI workflows are only `deletion-guard.yml`, `instruction-gate.yml` and `no-deletion-guard.yml`, and **no CI job runs Godot or the game** — local scan [.github/workflows](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/.github/workflows)

### Inferences
**Ports near-mechanically to GDScript or C#** (data and logic, about 3,000 lines):
- `movesets.js` (TekkenBuffer, notation parsing, `resolveMove`);
- `roster-full.js` and `attires.js` (pure data; could become JSON/`.tres`);
- `ai.js`;
- the guard/hit-word functions in `fighter.js`;
- `modes.js` and `episodes.js` logic (their DOM parts become UI).

**Must be rewritten against Godot APIs:**
- `stages.js` (procedural three.js scene building);
- `scene.js` (renderer and camera);
- `t3anims.js` retarget (in Godot this becomes import-time retarget or Skeleton3D pose math);
- the CCD-IK layer in `fighter.js`;
- `select-screen.js`;
- `assets.js` (GLTFLoader, tinting);
- all DOM menus (`main.js`, `menus.js`, `ui-wh`) → Control nodes;
- `audio.js` (synthesised Web Audio) → AudioStreamGenerator or pre-rendered audio.

**Two combat cores now diverge:**
- The web Fighter: 120 Hz, seconds-based move data, a large notation moveset.
- The Lab Fighter: 60 Hz, frames, 4 slots.

A migration must pick one canonical sim (ideally integer, 60 Hz, per the netcode law) and port the web's richer rules into it.

### Gaps
- I did not audit `fighter.js` line by line to estimate exactly how much of its 1,419 lines is pure combat logic versus three.js; the grep counts are a proxy.
- `stages.js` content (8 canon lands + 15 T3 panoramas per its header) was not measured per stage.

---

## Q4. Data assets: movesets, animation banks, GLB models, roster, customization, teardown outputs

### Takeaway
Most of the value is engine-agnostic JSON and glTF:
- 99 moveset files (about 40.7k moves);
- 17 decoded T3 animation banks in documented JSON formats (37 MB, 3,176 packed rows);
- 62 game GLBs (about 1.04 GB);
- 53 Lab GLBs;
- a 1,150-entry parts registry, plus thousands of converted GLB/PNG parts.

Main risks: GLB **size** (six models are 86–92 MB each), mixed skeleton conventions (49/50-bone Mixamo-style vs 18-joint T3 vs 109–328-joint T7/T8 native rigs), and a 6 GB non-LFS git repo.

### Cited Findings
**Movesets** (`game/assets/movesets/`)
- 101 JSON files, 32 MB. That's 99 fighter files plus `index.json` (format `wh-moveset-index/1`) and `t3_input_tables.json`.
- `index.json` lists 98 fighters with **40,673 moves** in total. Files range from 4,349 to 1,273,708 bytes — local scan.
- Schema (pantera.json, `schema_version: 2`):
  - top-level `fighter, display, tekken_base, t3_source, proxy, variant, strings[], specials[], frame_convention, t3_bank, t3_bank_rows, moves{873}, slots{394}, hit_words{667}, stance_after, merge_sources, …`;
  - move entry e.g. `{"input":"1","t3_row":44,"t3_command":"LP","startup":0.117,"active":0.017,"recovery":0.467,"damage":11,"t3_damage":18,"limb":"armL","knock":2.2,"soulGain":8,"anim_ref":"t3:king:row:44","move_class":"strike"}`.
  - **Timings are in seconds**: "T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP" — [game/assets/movesets/pantera.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/movesets/pantera.json)
- `frame_convention` comes in 17 variants (T3 69 files, SFEX 6, SF 6, SamSho 3, DOA 3+, VF5FS 3, KOF 1, T7 1, T8 1, …); 98 of 98 fighter files (at the earlier scan) are `schema_version 2` — local scan.
- Notation and merge tooling: `tools/moveset-merge/notation.py` defines "One Tekken notation for every move source"; the schema doc is `docs/movesets/MOVESET-SCHEMA.md` — [tools/moveset-merge/notation.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/moveset-merge/notation.py)
- The Lab uses a separate 7-file, frame-based slot format (Q1).
- The 8 legacy `game/assets/<name>_moves.json` files are 4–56 KB each — local scan.

**T3 animation banks** (`game/assets/anim/t3/`)
- 17 bank dirs, 37 MB: anna, armorking, bosconovitch, bryan, eddy, gunjack, heihachi, heihachi_on_jin, hwoarang, jin, julia, king_on_pantera_leoman, lei, nina, paul, xiaoyu, yoshimitsu. Each bank has 28–34 files and is 0.8–4.3 MB — local scan.
- **wh-anim/1 per-clip JSON** (e.g. `jin/t3_light.json`):
  - `format, source, bank (teardown/tekken3/animations/divmot09_jin.bin), slot, move_row, stream_frames, fps: 30.0, decoder, tool, source_glb, source_glb_sha256, hand_keyed:false, bones[22], rot_xyzw{bone:[[x,y,z,w]…]}, root_t[[x,y,z]…]`.
  - Bones use WH-Canonical-22 names (Root, Hips, Spine, Chest, Neck, Head, L/R Shoulder/Arm/ForeArm/Hand, L/R UpLeg/Leg/Foot/ToeBase).
  - Note: "t3anims.js ignores root_t (game drives root.position)" — [game/assets/anim/t3/jin/t3_light.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/anim/t3/jin/t3_light.json)
- **rows.pack.json (`wh-anim-pack/1`)**:
  - `bank, body_kmd, target_rig, bones[18], fps 30, decoder, tool, sha256{SLUS_004.02, divmot, kmd, glb}, rows{<move_row>: {move_row, n, slot, stream_frames, used_by[], q, rx, ry, rz}}, missing`.
  - `q` is base64 little-endian int16 quaternions (÷32767), laid out frame-major × bone × 4. `rx/ry/rz` are base64 int16 root translation in mm (÷1000).
  - The decoder is `decodePackRow` in t3anims.js. 16 packs hold **3,176 rows**; jin's pack is 1,007,770 bytes with 153 rows — local scan; [game/js/t3anims.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/t3anims.js)
- **skeleton.json (`wh-anim-skel/1`)**: 18 joints with parent and rest, `root_rest_y`, `foot_tip`. Tool: `tools/anim/t3_bank_skeleton.py` — [game/assets/anim/t3/jin/skeleton.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/anim/t3/jin/skeleton.json)
- The same clips also exist **inside** the Lab's `*_t3real.glb` files as glTF animations (40–42 each), so Godot can consume them natively via glTF import — local GLB scan of lab/game/assets.
- Missing real motion sources are listed in the audit: no decoders for T6 PSP (encrypted), T7, TTT2, DOA4, VF5 or SF, and Mokujin is absent. Undertaker/Kane clips are decoded but not retargeted — [docs/anim/PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md)

**GLB models** (`game/assets/models/`, local GLB-header scan at e3ae81b76)
- **62 GLBs, 1,041 MB**: 59 skinned, **3 unrigged** (scimitar.glb 13.26 MB, sun-ra-base.glb 0.88 MB, thor_alt1.glb 0.22 MB); 7 carry animations.
- Skeleton naming: 57 use a `Hips`-rooted stripped-Mixamo/canonical scheme; dio.glb is `MODEL_00`-rooted (174 joints); 1 is `global_pos`-rooted.
- Joint-count histogram: 49 ×22, 50 ×20, 53 ×4, 33 ×3, 32 ×1, plus single native rigs at 109, 142, 160, 174, 178, 244, 246, 311 and 328 joints.
- **Largest**: kiko-tanaka 92.2 MB, kiko-tanaka_alt1 91.0, mariposa 90.4, purple-rain-main 89.5, saku-ra-main 88.7, cape-jones 86.2. All are 49-joint, single-mesh, and require `KHR_mesh_quantization`.
  - In `game/assets/models`, 6 GLBs require `KHR_mesh_quantization` and 1 requires `KHR_texture_transform`.
  - Across models, Lab, stages and accessories (earlier scan), `extensionsUsed` was KHR_materials_ior 40, KHR_materials_specular 39, KHR_texture_transform 35 and KHR_mesh_quantization 7. Embedded images: 1,162 PNG, 419 JPEG.
  - No current game GLB requires `EXT_meshopt_compression`, but Tripo pulls arrive gltfpack-compressed (`tools/anim/gltf_codec.mjs`).
- `model-facing.json` (`wh-model-facing/1`): per-model rest facing "+Z"/"-Z" ("a -Z model is turned 180 deg at instance creation"), with flagged problems: "deathfang: renders EMPTY at rest", "vega: no Mixamo/Biped core bones" — [game/assets/models/model-facing.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/models/model-facing.json)
- Playable gate: "valid glTF, ≥1 skinned mesh, Mixamo-style bones (Hips/Spine1/Spine2/Head/hands/feet), sane world scale (~1.5–2.2 m)". The 41 re-rigged models were bone-heat auto-rigged "onto the WH 49-bone skeleton" or renamed from foreign skeletons (ValveBiped, T7, T8) — [game/assets/models/MODEL-STATUS.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/models/MODEL-STATUS.md)
- Other asset dirs: `game/assets/stages` 24 MB (18 GLB, 32 OBJ, 63 PNG, 10 JPG); `portraits` 7.1 MB; `accessories` 2.1 MB — local scan.
- **Repo weight**: `.git` is 6.0 GB (`size-pack: 5.78 GiB`). There is no `.gitattributes`/LFS, so binaries are committed directly. `roster/` is 2.4 GB, `teardown/` 2.7 GB and `customization/` 407 MB — local scan `du`, `git count-objects -vH`.

**Roster**
- `game/js/roster-full.js` exports `FULL_ROSTER`. My parse finds **58 `id:` entries, all distinct**. By display name there are **49 distinct fighters**: DEMONIO ×4 (base + bloodline-ember/winged/human forms), DOC FRANK ×5, CHARGER ×2, KRONOS ×2. The entries reference **50 distinct `model:` keys**.
  - The coordinator's figure is 59 entries / 50 distinct fighters. I could not reproduce 59 on `e3ae81b76` or on `FETCH_HEAD`/origin/main `b7aaa251f` (both give 58). The difference may come from counting method (e.g. 50 distinct model keys).
  - Tiers: `getRosterByTier()` slices souls 0–9, main 9–16, bonus 16+.
  - Entry fields: `id, name, title, base, moveset, model, tintStrength, colors{suit,trim}, style, archetype, surge{}, stats{speed,jump,power,defense}, ai{aggression,grabBias,reaction}, forms{}` — [game/js/roster-full.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/roster-full.js)
- `game/ui-wh/roster_canon.json` is 16 KB, keyed by display name, with fields `name, soul, tier, subtitle, quote, element, body, signature, owner_locked, origin` — [game/ui-wh/roster_canon.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/ui-wh/roster_canon.json)
- `attires.js` `ATTIRE_VARIANTS` maps a model key to `[{model, label}]` (e.g. demonio has 5 variants; kiko-tanaka has 3) — [game/js/attires.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/attires.js)
- Heights: `lab/game/data/characters/heights.json` holds per-character `height_cm` (Tekken profile heights, T8 baseline), applied by `height_scale.gd` — [lab/game/data/characters/heights.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/data/characters/heights.json)

**Customization**
- `customization/PARTS-REGISTRY.json` (v3): **1,150 parts**, 13 libraries, 7 character mappings. Entry shape: `{id, kind, library, name, asset, part_class texture_part|mesh_part, suite_slot, editable[], placement{}}`.
  - At the earlier snapshot of 1,148 parts, 1,102 were `geometryPending: true`.
  - The registry "carries only a slice … (1,148 of 25,784 indexed parts)". Per-source catalogs such as `customization/parts/no-mercy/CATALOG.json` hold the rest — [customization/PARTS-REGISTRY.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/customization/PARTS-REGISTRY.json); [packages/creation-suite/src/catalogs.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/packages/creation-suite/src/catalogs.js)
- `customization/parts/` (221 MB, 4,207 files): raw teardown formats — `.tex` 1,470, `.ymg` 1,200, `.png` 443, `.glb` 334, `.vc` 303, `.obj` 303.
- `customization/parts-converted/` (144 MB, 5,189 files): **engine-ready `.glb` 1,521 + `.png` 3,661**, tracked in `CATALOG.json`. WMXIX textures decoded: 1,477 — local scan; [customization/parts-converted/WMXIX-TEX-REMAINDER-REPORT-2026-10-20.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/customization/parts-converted/WMXIX-TEX-REMAINDER-REPORT-2026-10-20.md)
- Smaller libraries: decal-library 72 PNG; reskin-library 20 PNG; eye-library 3 PNG; face-morphs and body-morphs JSON — local scan.
- Lab attire format: `lab/game/attire/bannon_mask/bannon_mask.manifest.json` plus GLB plus PBR textures (Color/NormalGL/ORM), consumed by `attire.gd` with per-rig presets (`wh_canonical_t3`, `wh_canonical_autorig`) — [lab/game/scripts/attire.gd](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/game/scripts/attire.gd)

**Teardown outputs**
- `teardown/` is 2.7 GB. Biggest dirs: urban-reign 1.5 GB, eastern-mind 416 MB, tekken3 231 MB, tekken8 108 MB, wwf-no-mercy 105 MB, models 105 MB, dead-or-alive-4 100 MB, tekken7 83 MB, wmxix 64 MB.
- File-type counts: 20,904 PNG, 4,033 OBJ, 382 GLB, 350 JSON, 331 BIN, 233 WAV, 40 KMD, 2 FBX — local scan.

### Inferences
**Ports with zero or near-zero conversion:**
- moveset JSON;
- wh-anim/1 and wh-anim-pack/1 banks (a ~20-line GDScript decoder mirrors `decodePackRow`; alternatively use the GLB-embedded clips);
- skeleton.json;
- roster_canon.json, heights.json, PARTS-REGISTRY and catalogs;
- the attire manifest;
- all GLBs (glTF 2.0).

**Engine-specific work centres on:**
- runtime retarget and skeleton-name canonicalisation (three.js does it at runtime; Godot would use import-time `BoneMap`/`SkeletonProfile` or bake);
- per-model facing fixes;
- mobile memory/size budgets for 86–92 MB GLBs (needs decimation/texture compression; the Lab's import setting `import_etc2_astc=true` already targets mobile VRAM compression);
- converting roster/attires JS objects to JSON/Resources.

The non-LFS 6 GB repo will slow CI and Godot import of a full roster. A migration milestone may need an asset-selection or LFS plan; that is a constraint, not something I measured in Godot.

### Gaps
- I did not measure triangle counts or texture resolutions per GLB, which matter most for mobile budgets.
- I didn't check whether Godot 4.3/4.7 imports the KHR_materials_* extensions used here. That needs Godot docs or a test import, and no binary is available.
- I didn't verify which of the 62 models are actually referenced by `MODEL_URLS` in `assets.js` versus orphaned.

---

## Q5. Engine-agnostic pipelines already in Python/Blender

### Takeaway
The asset pipeline is already engine-neutral. Everything ends in glTF/GLB or JSON:
- auto-rig: 4,784 own Python lines plus vendored AI riggers;
- T3 row bake, skeleton and facing tools (742 lines);
- moveset merge and notation (1,921 lines);
- Lab T3→glTF importer and motion baker (1,241 Python lines).

These carry over unchanged to any engine that imports glTF. Two caveats: several steps need **Blender 4.0.2**, and some depend on the T3 decoder modules noted as living outside the repo.

### Cited Findings
**tools/auto_rig** ("one CLI, six backends, one gate")
- Backends:
  - `blender-heat` (Blender 4.0.2, fixed WH skeleton plus heat weights);
  - `gamerig` (Blender 4.0.2, vendored Rigify feature set, fresh per-mesh deform skeleton plus optional CMU BVH/GLB clip bake);
  - `knn` (numpy/scipy weight transfer from a donor rig);
  - GPU AI backends via Kaggle/Colab (`magicarticulate`, plus vendored `unirig` and `puppeteer`).
- Every run ends at `validate.py` (valid glTF, skinned mesh, Mixamo-style bones, 1.5–2.2 m, stretch < 2.5).
- Own Python (excluding vendor and checkpoints) is 4,784 lines; 39,662 lines including vendored code — [tools/auto_rig/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/auto_rig/README.md); local scan.

**tools/anim** (742 lines)
- `t3_row_bake.py` (181): "Bake EVERY Tekken 3 move row the WH movesets reference into one compact pack per bank".
- `t3_bake_packs.py`.
- `t3_bank_skeleton.py` (178): exports the source skeleton for runtime retargeting.
- `t3_bank_facing.py`: the "Offline twin of game/js/t3anims.js bankFacing()".
- `t3_extract_bodies.py`: each T3 character's own KMD body.
- `repair_sleeve_weights.py`.
- `gltf_codec.mjs`: "Tripo pulls ship as gltfpack output (EXT_meshopt_compression + KHR_mesh_quantization), which Blender 4.0.2's glTF importer cannot read. This decodes them…" — [tools/anim/gltf_codec.mjs](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/anim/gltf_codec.mjs); [tools/anim/t3_row_bake.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/anim/t3_row_bake.py)

**tools/moveset-merge** (1,921 lines)
- `merge_sources.py` (847): additive merge of T8/T7/T3 sources.
- `notation.py` (182): unifies wavu T8 / t7chicken / T3 notations.
- `t3_input_tables.py` → `wh-t3-input/1`.
- `guard.py` and `guard_zui.py`: no-loss guards.
- `build_merge.py`, `build_zui_stances.py`, `report_md.py`, `engine_check.mjs` — [tools/moveset-merge](https://github.com/mhvnsnt/western-heart/tree/e3ae81b76/tools/moveset-merge)

**lab/tools** (13 Python files, 1,241 lines, numpy-based)
- `t3_to_gltf.py` (149): KMD + stance OBJ → rigid-skinned GLB, Kabsch fit, max RMS 0.94 T3 units ≈ 1 mm.
- `t3_motion_bake.py` (286): decoded T3 motion → glTF clips.
  - It has a generalized `TargetRig` with "full node-tree world rest, non-identity rest, a Mixamo-49 canonical map, and -Z facing".
- `autorig.py`, `rig_check.py`, `gltf_eval.py` (numpy glTF evaluator with CPU skinning), `clips.py` (2-bone IK authored clips), `gltf_write.py`, `mask_fit.py`, `t3_branch_dump.py`, `export_moves.py`.
- Sources: [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md); [docs/anim/PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md); local scan.
- Dependency caveat: M1 says `pose_assemble.py`'s "`kmd`/`motion` modules lived at `/home/hatch/...` and are not in the repo". Banks were later decoded with `teardown/tekken3/tools/local/pose_assemble.py + usa_motion.py` (decoder field in every bank file). Reproducing them also needs the external `n0madic/Tekken3Remake` research checkout (`T3REMAKE_RESEARCH`) — [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md); [docs/anim/PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md)
- **I ran the Python rig check here**:
  - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B lab/tests/test_rig_check.py`, numpy 2.5.3, scipy 1.18.1.
  - Result: 3 tests ran in 43 s with **1 FAIL**. `pantera_leoman_t3real.glb` fails with "t3_stance@0.00: 0.68% of triangles stretched >x2.0 (tearing)", "mesh sinks below floor (-0.174)", and similar errors at t3_stance@0.22 and t3_stance_c@0.90/1.12.
  - Source: local test run, [lab/tests/test_rig_check.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/tests/test_rig_check.py).

### Inferences
- These pipelines make the engine choice mostly a **runtime** decision. Asset prep (rig, bake, merge, validate) is reusable as-is for Godot, Unity, Unreal or Bevy alike, since all consume glTF.
- The real porting cost sits in game code (Q3), not data.
- The currently failing Lab rig check (Pantera Leo-Man real-clip tearing and floor sink) is a quality defect any engine port inherits. It should be a gate in migration milestone 1.

### Gaps
- Blender is not installed here (`which blender` returns nothing), so I couldn't exercise the Blender backends.
- I didn't verify whether every bank can be rebuilt from in-repo sources alone.

---

## Q6. Docs recording engine decisions and Godot plans

### Takeaway
Every design doc since 2026-10-12 names **Godot 4** as the target. Earlier docs emphasise web export / phone browser or PC. The **2026-10-22 owner directive** (now committed on main via PR #474) hardens this to "exclusively … Godot 4's native mobile rendering pipeline", while explicitly inviting research into "whatever's better". The 2026-10-16 engine survey recommends staying on Godot and upgrading to 4.7, and it rejects Bevy, Unreal, Stride, O3DE, Flax and Cocos for team, stack or license reasons.

### Cited Findings
- **Owner directive (2026-10-22)**: "WebGL and Three.js are permanently stripped from the architecture; Western Heart operates exclusively on Godot 4's native mobile rendering pipeline (Vulkan / GLES3, standalone mobile executable)". Also: "Or even whatever's better than that for what we're building here based on research, deep research, even if Godot is the best one but there might be better."
  - The same doc names `lab/game` (Godot 4.3, M1–M3) and `tools/netcode/godot` as the existing Godot work.
  - It requires portrait mode ("the viewport stays fully visible"), Tekken 8-style creation-suite layout, camera gestures (orbit, pinch, 2-finger pan, double-tap focus), and JSON serialization of equipped mesh IDs, material overrides, decal UV transforms and socket offsets.
  - Source: [docs/creation-suite/OWNER-DIRECTIVE-2026-10-22.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/creation-suite/OWNER-DIRECTIVE-2026-10-22.md)
- **GAME-DEV-BRIEFING.md**: "**Engine:** Godot 4, web export first (phone browser). DriftEngine (WebGPU) evaluated for 3D viewer." "**Rendering target:** PS1-authentic — vertex snapping, affine texture mapping" — [GAME-DEV-BRIEFING.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/GAME-DEV-BRIEFING.md)
- **DESIGN.md**: "**Engine:** Godot 4 (free, open-source — fits the owner's free-tool directive). **Fighting core:** Reimplemented from the Tekken 3 Ghidra teardown" — [DESIGN.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/DESIGN.md)
- **technical-plan.md (2026-10-12)**:
  - "Choice: Godot 4.x"; "Exports to PC (primary target)".
  - "Why not Unity: Licensing cost… Why not Unreal: overkill for PS1 aesthetics, revenue share".
  - PS1 shader plan: render at 320×240 and vertex snap.
  - Source: [teardown/western-heart-design/technical-plan.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/teardown/western-heart-design/technical-plan.md)
- **prototype/README.md**: "The prototype targets Godot 4 with web export (phone browser)… **Not yet implemented:** Godot project files, scene trees, GDScript port of combat core. See `docs/TK-COMBAT-ANALYSIS.md` for the port checklist." (This predates and is superseded in part by lab/game.) — [prototype/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/prototype/README.md)
- **ENGINE-SURVEY-2026.md** (branch `research/engine-survey-20261016`; the identical file is on main):
  - Godot is current at "4.7 'Director's Cut' (June 18, 2026)", and "Local tools already carry 4.7.2".
  - Recommends Jolt for hitboxes and the 4.7 **VirtualJoystick** node for mobile.
  - Warns of "Breaking changes in 4.7 (device IDs, RichTextLabel renames, removed tap_back_pos/Android OBB) — read the migration guide before upgrading any lane past 4.5".
  - Verdicts: Bevy excluded ("no editor + churn"), Unreal "proprietary", Cocos Creator 4 "Mobile/web strength, but … not our stack", Stride and O3DE excluded, Flax excluded on license.
  - Source: [docs/ENGINE-SURVEY-2026.md](https://github.com/mhvnsnt/western-heart/blob/research/engine-survey-20261016/docs/ENGINE-SURVEY-2026.md)
- **docs/ANIMATION-PIPELINE.md** plans "Path C: … Reimplement the CCD IK solver from `fighter.js` in Godot. Godot has built-in `SkeletonIK3D`", and lists "Godot 4 … — to set up" as an unchecked prerequisite — [docs/ANIMATION-PIPELINE.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/ANIMATION-PIPELINE.md)
- **docs/creation-suite/DESIGN.md**: "Western-heart's Godot Lab gets a GDScript port of `regions.js` + `secondary.js` (same data)… 3. Godot port for western-heart Lab" — [docs/creation-suite/DESIGN.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/creation-suite/DESIGN.md)
- **game/netplay/README.md**: "Server-authoritative (netfox-style) is the Godot-target option" — [game/netplay/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/netplay/README.md)
- **Godot-only lab README**: "The Lab track turns the owner's own Tekken 3 teardown into playable Godot 4 content" — [lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md)
- 48 Markdown files outside `tools/netcode/godot` mention Godot (local `grep -rIl -i godot --include=*.md`).

### Inferences
- The docs disagree on the **primary platform**: PC (technical-plan), phone browser via web export (briefing, prototype, Lab M3), and native mobile (owner 10-22). The 10-22 directive is the newest and binding.
- The docs also disagree on the **Godot version**: the Lab uses 4.3, the survey recommends 4.7, and snoringcat needs 4.7+.
- The survey's note that 4.7 removed Android OBB matters for a large-asset Android build. Combined with the roughly 1 GB of fighter GLBs, it points to asset-pack/download planning. (Mechanism not researched here.)
- The PS1-authentic rendering target (low internal resolution, vertex snap) would reduce mobile GPU cost. It conflicts with the 86–92 MB high-detail Tripo models, so it's an open art-direction question for the report.

### Gaps
- `docs/TK-COMBAT-ANALYSIS.md` (the referenced "port checklist") was not read in detail.
- I didn't verify the survey's external claims (Godot 4.7 date and features); they are repo assertions, not checked against Godot release notes.

---

## Q7. Godot binary / export templates in this environment; can the Lab tests run headless here?

### Takeaway
**No.** This container has no Godot binary, no export templates, no Android SDK and no Blender, so the Lab's GDScript tests and any export can't run here without installing Godot 4.3.x (per the playtest doc). Java, xvfb-run, Node 22 and Python 3.13 with numpy/scipy are present. The Python rig check does run, and it currently fails 1 of 3 tests.

### Cited Findings
- `which godot godot4 Godot` returns nothing.
- `~/workspace/tools` and `/home/user/workspace/tools` don't exist.
- `/opt` holds no Godot. It contains apache-maven, claude-code, google-cloud-sdk, gradle(-8.14.3), maven, node-tools, node20/21/22, nvm, pw-browsers, rbenv, rclone, ruby-3.x.
- `find / -maxdepth 4 -iname '*godot*'` (excluding the repo) finds nothing.
- `~/.local/share/godot` (the export-templates location) doesn't exist.
- Source for all of the above: local shell checks on 2026-10-22.
- Other tools: `ANDROID_HOME` is empty and `sdkmanager`/`adb` are not on PATH. `/usr/bin/java` is present, `/usr/bin/xvfb-run` is present, `node` is v22.22.0, `python3` is 3.13.16 (numpy 2.5.3, scipy 1.18.1), and `blender` is not on PATH — local shell checks.
- Historical environments: Godot 4.3-stable was installed at `/workspace/tools/godot` with web templates streamed from the `.tpz` (2026-10-14). The playtest doc says "box has /usr/local/bin/godot 4.3.stable" and gives the install fallback "download `Godot_v4.3-stable_linux.x86_64.zip`". The engine survey claims "Local tools already carry 4.7.2" — [docs/workflows/WORKLOG.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/workflows/WORKLOG.md); [docs/PLAYTEST-METHOD.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/PLAYTEST-METHOD.md); [docs/ENGINE-SURVEY-2026.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/ENGINE-SURVEY-2026.md)
- Python rig check result here: 3 tests, 1 FAIL (see Q5) — local test run.

### Inferences
- **Milestone 0/1 of any migration needs a reproducible Godot toolchain**: a pinned Godot binary, export templates, an Android SDK/NDK plus keystore for native mobile, and a CI job. Today no CI runs Godot, and the agent sandbox doesn't have it. The Lab's tests (`test_move_table.gd`, `run_match_headless.sh`, `qa_playtest.gd`) are ready-made CI gates once a binary exists.

**Candidate first three migration milestones**, grounded in the facts above (offered for the report-writer to adapt):
1. **Toolchain + mobile shell.**
   - Pin the Godot version (4.3 → 4.7 upgrade per the survey) and decide the mobile renderer (Mobile/Vulkan vs Compatibility/GLES3) and orientation (portrait support).
   - Add an Android export preset and build an APK of the existing Lab slice.
   - Put `test_move_table.gd`, `run_match_headless.sh`, `qa_playtest.gd` and `test_rig_check.py` into CI.
   - Fix or gate the failing `pantera_leoman_t3real` rig check.
2. **One canonical combat sim.**
   - Port the web TekkenBuffer, notation `resolveMove`, T3 guard/hit-word rules and the schema-v2 moveset loader (seconds → frames) into a fixed-point 60 Hz GDScript sim, following the `fighter-sim.js` determinism law.
   - Replace the Lab's 4-slot MoveTable usage. Load wh-anim-pack rows (or GLB-embedded clips) per `anim_ref`.
   - Prove determinism with a mirror-style checksum test.
3. **Roster + assets + UI parity.**
   - Convert `roster-full.js`, attires and canon to JSON/Resources.
   - Run a Godot import pass over the 62 game GLBs: BoneMap for the 49/50-bone scheme, facing from `model-facing.json`, and a size/LOD budget for the 86–92 MB models.
   - Build touch-first character select and menus (VirtualJoystick, Control UI).
   - Netcode (netfox or snoringcat) and the creation suite follow as later milestones.

### Gaps
- I didn't install Godot (forbidden by scope), so I can't confirm the Lab still opens, imports or passes on 4.3 or 4.7. I also can't confirm the KHR_* material extensions import cleanly, or measure the APK size and mobile frame rate.
