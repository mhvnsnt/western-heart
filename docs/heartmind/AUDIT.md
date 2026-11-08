# Western Heart — What's Already Done (audit)

**Repo:** `mhvnsnt/western-heart` (GitHub API name `Western-Heart`)
**Audit date:** 2026-11-06, ~09:40 CST
**HEAD at audit time:** `04e6d201` — merge of PR #1601, 2026-11-06 15:20 UTC ("14/14 checks pass, menu-touch-e2e flipped pass this run")
**Method:** read the repo tree with the GitHub connector (top level + 2nd/3rd level of every real directory) and read the key docs in full. No code was run, no build was played, nothing was changed or pushed. A doc describing a system is **not** counted as done — only working code/data counts.
**Warning:** this repo merges constantly (PR #1601 landed the morning of this audit; ~1,600 PRs total). This audit is a snapshot and will go stale fast.

## In one sentence

The game already exists as a playable web build — Pantera vs Demonio in one stage, with a menu, a character select, and a real fight loop in code — but only that one pair is truly wired, and nobody has watched a full phone playthrough since the last code audit found the whole loop broken.

## The three engines in the docs (reconciled, not picked)

The docs describe three different engines. All three strands are real in the repo's words; only one is real as a playable game:

| Strand | Where it lives | What it actually is |
|---|---|---|
| **Web Three.js — the real game** | `game/` | Plain web pages + JS, no build step. `game/index.html` (39,537 bytes), `game/js/` (159 files), vendored Three.js in `game/vendor/`. Run with `python3 -m http.server`. Served on GitHub Pages from `game/`. |
| **Godot 4 — a small lab** | `lab/game/` | Godot 4.3 project (`project.godot`, `main.tscn` is 159 bytes, 7 scripts). `move_table.gd` is a 4-slot interpreter (light/medium/heavy/grab) over 7 Tekken 3 move files in `lab/game/data/moves/`. T3 fighter GLBs live in `lab/game/assets/`. This is a lab, not the game. |
| **Tekken 7 / UE4 / C++ "Chimera" — design language only** | `CHIMERA-BUILD.md`, `CHIMERA-ARCHITECTURE.md`, `DESIGN.md` | Says the modern game is built on Tekken 7's foundation in UE4. **No C++ files, no CMakeLists, no Unreal project files were seen in any tree listing I took.** The Tekken 7 influence is real as *models and frame data* (see below), not as engine code in this repo. |

DESIGN.md also says "Godot 4, Tekken 3 engine" while CHIMERA-BUILD.md says "Tekken 7 base, UE4". Both are in the repo. The thing a player can actually open today is the web build.

## What the game is (from its own docs)

- **DESIGN.md:** a fighting game inside Tong-Nou (a giant green head). 9 souls roster, 7 stages (5 lands + 2), Reincarnation Rounds, Nine-Soul Meter, Force Claiming, arcade ladder Wood → Fire → Earth → Metal → Water, then Phantom Marketplace (mid-boss: the Trader), then Central Mountain (final: your own assembled soul).
- **GAME-DEV-BRIEFING.md:** the roster is actually **36 named fighters** (9 souls + 7 main vessels + 20 bonus + boss Sun Rā). Modes: Versus (incl. Tekken Tag-style tag), Story/career where death is forced reincarnation as another character. Recent work talks about "Roster-100" (Nov 6 commits).
- **ROSTER.md:** the 9 souls — RIN (Jin), BYOU (Lei), TOU (Paul), SHA (Xiaoyu), KAI (Eddy), JIN (Yoshimitsu), RETSU (Bryan), ZEN (Julia), GYOU (Hwoarang). Each soul's body is a Tekken 3 model, skin is Eastern Mind art, moveset is a Tekken 3 style. Footnote on the last line: *"All bodies… pending teardown. All skins… pending extraction. All movesets… pending teardown."*
- **CANON.md** (167,785 bytes, 3,226 lines): the character bible. North Star, the five lands, death = reincarnation (lose a round, come back in a new face picked from 3 eyes / 3 noses / 3 mouths, and the face changes your fighter). "The Seven" main vessels with full backstories (Pantera, Demonio, Phantom, Diablo, Skull, SAM-UR-A1, Saku Ra).
- **AGENTS.md** (23,207 bytes, repo's own rules): owner laws that matter here — finish one fighter to playable before starting the next; short jobs first (T-pose model + moveset straight from one source character); play it like the player before calling it done; no hand-made menus (must cite a teardown source); data priority is Tekken 5/6/7/8/TTT2 first, Tekken 3 only as a logged last resort; **no copyrighted/leaked game files in public repos or Pages** (line 78). Also: a 2026-10-17 commit once deleted 54,456 files — hence the deletion guards in CI.

## Piece-by-piece score

DONE = working code/data seen. PARTIAL = code/data exists but incomplete or unverified live. STUB = a file or doc exists, the system doesn't work yet. MISSING = no file found.

| # | Piece | Status | Evidence (file = what I actually saw) | What's owed next |
|---|---|---|---|---|
| 1 | Boot / title / menu | PARTIAL | `game/index.html`, `game/js/wh-boot.js`, `game/js/mainmenu.js` (16 KB), `game/js/menus.js` (35 KB), `game/js/main.js` (78 KB). CI `menu-touch-e2e` (Playwright, phone 390×844) passed on HEAD #1601. | A human phone playthrough. Last code-read audit (`docs/CRITICAL-PATH-STATUS.md`, 2026-10-22) had the whole loop RED: a duplicate `id="screen-stage"` made `show()` throw on every tap. The fix was in an unmerged PR then; I could not verify from the files alone whether it is fixed now. |
| 2 | Character select | PARTIAL | `game/js/select-screen.js` (52 KB), `game/js/roster-full.js` (34 KB), `game/select.css`, `select-t7.css`, `select-t8.css`, ~60 portraits in `game/assets/portraits/`. | 6 of the 9 soul portraits are the **same 6,523-byte file** (`byou.png`, `gyou.png`, `kai.png`, `retsu.png`, `rin.png`, `sha.png`) — placeholders, not real portraits. |
| 3 | Roster — fighters | PARTIAL | 36 named in `GAME-DEV-BRIEFING.md`; ~49 entries per the Oct 22 audit; **≥54 GLBs** counted in `game/assets/models/` (list cut off at "thor", so more may exist); 60+ moveset JSONs in `game/assets/movesets/`; `roster/` has ~70 per-fighter folders. `game/assets/models/MODEL-STATUS.md` (2026-10-17/18) says 47 models passed the loadable gate. | Only Pantera + Demonio are the wired playable pair. Most fighters are model + data only. The SmutBase six (Pond, Ryusan, Tobi, Menajerii, Megami, Chatur) have **no GLB in this repo** — only portraits and (Chatur only) a moveset JSON. Scarlett / Madelyn have nothing here at all; they live in Physique Lab. Demonio's body is a Tekken 7 Steve Fox model, not Jin — `game/README.md` admits this honestly. |
| 4 | Stages — 7 lands | PARTIAL | `prototype/stages/` has 8 JSON defs (Tree of Life, Plains of Chi-U, Octagonal Shrine, Helix Palace, Palace of Dreaming, Phantom Marketplace, Shrine, Tong-Nou). `game/assets/stages/t3/` has 15 Tekken 3 stage panoramas (atlas PNG + OBJ each). `game/assets/stages/eastern-mind/stages.json` + 6 land folders. `game/js/stages.js` (110 KB), `stagebreaks.js`, `stage-variants.js`. | The playable build wires **only Shrine of the Blade** (`game/README.md`: "T3 has real stage geometry — not yet wired"). Stage-select preview pane was missing in the Oct 22 audit. |
| 5 | Fight core | PARTIAL | `game/js/game.js` (49 KB), `game/js/fighter.js` (241 KB), `combat-core.js`, `hitbox.js`, `hitdetect.js`, `frame-data-schema.js`, `t3-reactions` / `t3-throw` / `t3anims.js` (86 KB), `stagebreaks.js`, wall tests. Best-of-3, 60 s timer, K.O. / DOUBLE K.O., hitstop, chip damage (12%), launchers, juggle data, sidestep (tap joystick up/down), throw breaks. | No crouch/low blocking yet (`game/README.md` known gaps). Chain-throw sequences not implemented (grabs are single-hit launchers). No rematch re-pick from the result screen. Live fight never watched by me. |
| 6 | Movesets / move table | PARTIAL | `game/assets/movesets/` 60+ JSONs (some multi-MB: demonio 3.7 MB, diablo 3.9 MB, gyou 3.6 MB). `game/data/t7-frame-data/` — 40+ Tekken 7 fighters. `game/data/t8_frame_tables.json` (326 KB). `moveset-library/` — Soulcalibur II movesets, WMXIX moves, a 2.3 MB Mat Kings move database. `lab/game/data/moves/` — 7 Tekken 3 move files. | **Correction to the Nov 2 audit:** `lab/game/scripts/move_table.gd` (3,334 bytes) is a 4-slot interpreter, not a 2,079-move table. The 2,079 number was the Physique Lab conversion, not this file. Per-fighter wiring varies; `docs/MOVESET-STUB-AUDIT-2026-10-22.md` exists because stubs exist. |
| 7 | Touch / phone controls | PARTIAL | `game/js/input.js` (24 KB), vendored `game/vendor/nipplejs` (joystick), touch buttons in `game/index.html` (LP/RP/LK/RK, S, B, D, V + joystick). CI menu-touch-e2e taps through menu → select → stage → fight at 390×844. | No live phone check by me. The e2e "flipped pass this run" per the HEAD merge message — it has been flaky. |
| 8 | Face / expressions | STUB | `game/js/faceRig.js` (5.5 KB), `lipsync-player.js`, `handPoses.js`, face manifest/spec from the earlier audit. | The WH skeleton has **no face bones at all** (`MODEL-STATUS.md`: "Pantera rule: NO facial/mouth rig on any King-based model"). Faces are not a working system. |
| 9 | Sound / music | PARTIAL | `game/assets/music/` ~45 tracks (battle themes, menu, Tong-Nou themes, Nosferatu set, victory fanfare). `game/assets/sounds/` Eastern Mind `.ogg` files. `game/js/audio.js` (13 KB), `music.js` (20 KB), `jukebox.js`, `wh-audio.js`, `game/data/music-library.json` (53 KB), voice JSONs for ~50 fighters. | `game/README.md`: the playable build's audio is procedural Web Audio; the real teardown audio is "not yet wired". |
| 10 | Arcade / story mode | PARTIAL | `game/js/modes.js` (70 KB), `heartmind.js` (27 KB), `heartmind-campaign.js`, `episodes.js`, `story-endings.js`, `story-wiring.js`, `game/story/heartmind-trial.ink` + `.yarn` + `.json`, `tournament.js`, `team-battle.js`. | Story flow exists as code + script files; no end-to-end playthrough evidence in the files. The Trader / Phantom Marketplace screens are text in `index.html`. |
| 11a | Nine-Soul Meter + Soul Surge | DONE | Implemented in the playable build per `game/README.md`: meter 0–100, 9 soul segments, +8 light / +11 heavy / +6 damage taken / +4 block; Soul Surge costs the full meter, 0.24 s startup, 24 damage. `game/js/soul-systems.js`, `soulurge.js`, `soul-kindle.js`, `soul-spirit.js`, tests `test/soul-systems.test.mjs`. | Needs a live check that it feels right in a real fight (it is code-DONE, not play-proven). |
| 11b | Reincarnation Rounds | STUB | Design is fully written (CANON.md death section, DESIGN.md, `game/js/story-wiring.js` 2.4 KB). | No working reincarnation flow found — no round-loss → new-face → changed-fighter implementation in the files I saw. |
| 11c | Force Claiming | MISSING | No file found for claiming a land's force after winning there. | Design exists (DESIGN.md §5); code does not, as far as the tree shows. |
| 12 | Save / progress | MISSING | No save file found in `game/js/` (159 files listed). Replays exist (`replay.js`, `replay-codec.js`, "REPLAY THEATER" in `index.html`) — replays are not a save system. | Save, unlocks, and records have code around them (`unlockables.js`, `ranks.js`, `game/data/ranks.json`) but no save system was found. |
| 13 | Build / packaging | DONE | Web: no build step (`game/README.md`: `python3 -m http.server`, GitHub Pages serves `game/`), `game/netlify.toml`, `_redirects`, `manifest.webmanifest`, `sw.js`. Itch zip workflow `.github/workflows/build-itch-zip.yml`. Godot `lab/game/export_presets.cfg` exists (lab only). | Nothing owed for the web build. A Godot or Unreal build does not exist as a shippable thing. |
| 14 | CI / tests | DONE | 14 workflows in `.github/workflows/` (rig-guard, deletion/clobber guards, instruction-gate, coverage-guard, material-gate, `game-checks.yml`). `test/` ~90 `.test.mjs` files + `game/tests/` ~70 files. `game-checks.yml` runs: rig-guard, all `test/*.test.mjs` under Node, the Playwright menu-touch e2e, and the material gate. HEAD #1601: 14/14 checks pass. | CI passing is not a playthrough — it proves the checks run, not that the game feels right. |
| 15 | Create Fighter / customization | PARTIAL | `customization/` is huge (PARTS-REGISTRY.json 1.2 MB, parts/clothing specs, build scripts), `packages/creation-suite/` (package.json, closet registry, src/ui), `game/js/custom-fighter.js`, `customization-consumer.js`, `customization-t56.js`, `attires.js` (27 KB). | AGENTS.md: the existing creation-suite UI is **NON-COMPLIANT** (hand-built, not teardown-sourced) and pending a rebuild. Do not delete it. |
| 16 | Online / netplay | STUB | `game/netplay/` — `rollback.js`, `mirror.mjs`, `signaling/server.js`, lobby, demo; `game/js/online.js` (43 KB). | Code present, no live verification anywhere in the files. Needs a server to run. |

**Headline counts (18 rows): DONE 3 · PARTIAL 10 · STUB 3 · MISSING 2.**
DONE: Nine-Soul Meter, build/packaging, CI/tests. MISSING: Force Claiming, save/progress.

## Docs: what exists, what's missing

- **Exist at top level:** `AGENTS.md`, `CANON.md` (167 KB, 3,226 lines), `DESIGN.md`, `GAME-DEV-BRIEFING.md`, `CHIMERA-ARCHITECTURE.md`, `CHIMERA-BUILD.md`, `MISSION.md`, `ROSTER.md`, `RENAME-MAP.md`, `WORKLOG.md` (429 KB — not read), `POSE-BLOCKERS.json`, `TERABOX-MANIFEST.md`, `WORKING-METHOD.md`, `portraits-manifest.json`, `roster-integrate-MAP.json`.
- **Cited by DESIGN.md but not found at top level:** `stages.md`, `systems.md`, `technical-plan.md`, `asset-manifest.md` (there is `teardown/western-heart-asset-catalog.md` instead; the four docs may live under `docs/` subfolders — not verified).
- **Docs worth reading next:** `docs/CRITICAL-PATH-STATUS.md` (last real playability audit, Oct 22), `docs/WH-100-GAP-INVENTORY-2026-10-30.md` (46 KB), `docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md`, `docs/MOVESET-COVERAGE.md`, `docs/ENGINE-DECISION-2026-10-22.md`.

## Tree at a glance (top level, from the connector)

Root files: AGENTS.md, CANON.md, CHIMERA-ARCHITECTURE.md, CHIMERA-BUILD.md, CLAUDE.md, DESIGN.md, GAME-DEV-BRIEFING.md, MISSION.md, POSE-BLOCKERS.json, RENAME-MAP.md, ROSTER.md, TERABOX-MANIFEST.md, WORKING-METHOD.md, WORKLOG.md, portraits-manifest.json, roster-integrate-MAP.json, .gitignore, .gitleaks.toml.
Root dirs: `.claude`, `.github`, `anims`, `arenas`, `assets`, `customization`, `docs`, `game`, `lab`, `moveset-library`, `packages`, `promo`, `proof`, `prototype`, `roster`, `shared`, `stages`, `teardown`, `test`, `tools`.
Biggest areas by file count: `game/js/` (159 files), `test/` (~90 test files), `game/tests/` (~70), `docs/` (~90 docs + ~50 subfolders), `tools/` (~90 tool folders), `teardown/` (~30 game folders), `roster/` (~70 fighter folders), `customization/` (large).
Full level-2/level-3 listings saved alongside this audit in `tree-level2.txt`, `tree-level3.txt`, `game-js.txt`.

## Commercial game files — flagged, not copied

This repo is **public** and it holds extracted commercial-game material. Jay's own rules (AGENTS.md line 78) say no copyrighted/leaked files in public repos or Pages. That is an owner decision, not mine — but the files are here, so they are flagged plainly:

- `teardown/` — Tekken 3 (movesets, 15 stages, 8,556 textures claimed), Tekken 5/6/7/8, TTT2, Eastern Mind (549 MB game on release), WWF No Mercy, WWE WrestleMania XIX, WWE 2K19/20/22, Urban Reign, Soulcalibur II/VI, Virtua Fighter 5, Dead or Alive 4/6, Def Jam: Fight for NY, Street Fighter 3D/EX games, Yakuza, Nioh, Fire Pro, Gang Beasts, Warriors, Sleeping Dogs, Fight Club.
- `game/assets/models/` — GLBs built from Tekken 7/8 models (Demonio = Steve Fox body; doc-frank / kinpo-t8 / phantom-t8 / zafina are T7/T8-native skeletons).
- `game/assets/stages/t3/` — Tekken 3 stage panoramas + atlases. `game/assets/ui/tim_*.png` — Tekken TIM textures. `game/data/t7-frame-data/`, `t8_frame_tables.json` — Tekken frame data.
- `game/assets/music/` + `sounds/` — includes Eastern Mind audio files.

**Do not copy any of the above into another project.** Jay's own material (safe to reuse): `lab/skeleton/canonical_skeleton.json` + `retarget_maps.json`, all of `game/js/` (own code), `lab/game/scripts/`, `prototype/` JSONs, `CANON.md` / `DESIGN.md` / `ROSTER.md` / `GAME-DEV-BRIEFING.md`, the Nine-Soul Meter / Soul Surge design, and the move-table interpreter.

## Buildability — plain answer

- **Web build: yes, runnable as-is.** No build step, no CDN (Three.js vendored), `python3 -m http.server` in `game/`, or GitHub Pages. I did not run it — no live browser in this audit — so "runs" is from the files + CI, not from watching it.
- **Godot lab: a project file exists** (`lab/game/project.godot`, Godot 4.3, GL Compatibility) with a 159-byte main scene. It is a lab, not a shippable game; I did not open it in Godot.
- **Unreal/C++ build: none found.** Nothing in the tree builds an Unreal or C++ game.
- **CI: green on HEAD** (14/14 checks on PR #1601, incl. the phone menu-touch e2e). CI runs unit tests + the e2e tap test on every PR. That is the strongest "it works" evidence in the repo — and it is still not a human playthrough.

## Recommended 1-piece-at-a-time order

Grounded in what is closest to working, and in the repo's own owner law (AGENTS.md, Oct 31: short jobs first, one fighter to playable before the next, play it like the player):

1. **Piece 1 — prove the loop, live.** Headed phone playthrough of the current deploy: menu → select → stage → fight → K.O. → result → rematch/menu, Pantera vs Demonio. Fix only what breaks, in the order it breaks. (This settles whether the Oct 22 RED is really fixed.)
2. **Piece 2 — second stage.** Wire one more stage into the playable build (a Tekken 3 panorama from `game/assets/stages/t3/` is the closest: files exist, geometry exists, only the wiring is missing).
3. **Piece 3 — one more short-job fighter.** Owner-named short jobs: Purple Rain (Lee moveset) or Negativo (Negan moveset) — T-pose model, single-source moveset. Finish to playable, then the next.
4. **Piece 4 — the 9 soul portraits.** Replace the six identical 6,523-byte placeholder portraits with real ones.
5. **Piece 5 — Reincarnation Rounds.** The signature system that makes this Western Heart and not Tekken. Design is done; code is a stub.
6. **Piece 6 — Force Claiming + save.** Both missing; both are small systems once the fight loop is solid.
7. **Later —** rest of the roster one fighter at a time, rest of the stages, story mode end-to-end, Create Fighter rebuild, netplay.

## Top 3 blockers

1. **No live playthrough proof.** Last human-style audit (Oct 22) found the whole menu→fight loop RED. CI's phone e2e now passes, but no one has watched a real phone play the current build. Until that happens, every "done" above is code-done, not play-proven.
2. **Breadth without depth.** 54+ models and 60+ moveset files exist, but only Pantera vs Demonio is a wired playable fight; Demonio wears a Steve Fox body; six soul portraits are the same placeholder file.
3. **Three engines, one game, plus a public-repo problem.** The docs argue Godot vs Tekken 7/UE4 while the only playable thing is web Three.js — pick the web build as the ship target and stop splitting effort. And the repo is public while holding extracted commercial files, against its own AGENTS.md rule — that needs Jay's call before anything is published or landed elsewhere.
