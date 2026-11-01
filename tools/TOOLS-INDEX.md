# Tools index: every tool the 2026-10-20/21 Claude session used, and what it is for

Owner, 2026-10-21: "Put all tools clearly labeled in the repo that u have used, all ur methods
and work and everything shown in the repo and documents and handoffs."

Every tool below is in this repo. Nothing in this session ran from a script that lives only on
a private machine. External programs are free/open source and pinned. `tools/setup/setup_toolchain.sh`
installs them. The method write-ups are in `docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md`
(why each fix and where the old pipeline went wrong) and `WORKLOG.md` (what ran, in order).

## 1. Data pulls (game data in, nothing hand-typed)

| tool | pulls | writes |
|---|---|---|
| `tools/fetch_wavu_framedata.py` | Tekken 8 frame data + move lists, wavu.wiki Cargo API (CC0). `--full` adds notes/alias/alt/reach/tracking. Restored from e03195de; the cd3bf38 wipe deleted the original | `docs/t7t8-reference/frame-data/` (Oct 14 baseline, 20 chars, untouched), `docs/t7t8-reference/frame-data-t8-full/` (all 41 T8 chars, 6,284 moves) |
| `tools/fetch_t7chicken_framedata.py` | Tekken 7 frame data, dayhaysoos/t7chickenplus-graphql @ 91a054e8 (ISC, TekkenBot-extracted). The same dataset Muse used in 74efb3fb, whose import script never landed | `docs/t7t8-reference/frame-data-t7/` (47 chars, 11,137 rows) + `SOURCE.json` with SHA-256 per file; `--check` re-verifies |
| `tools/anim/t3_extract_bodies.py` | each T3 character's own body (KMD) out of `TEKKEN3.BNS`, using the original BNS index (SHA-256 per record) to pair every body with its own motion bank | `teardown/tekken3/BODY-EXTRACTION.json` (provenance). The KMD/OBJ/GLB outputs are regenerated locally and not committed (public repo, owner rule 8) |
| `tools/gen-movesets-t3.py` | T3 move lists from the decoded motion banks (`teardown/tekken3/movesets/moveset_*.json`) + the EXE common branch table | per-fighter move dicts (called by the moveset tools) |

## 2. Animation (decoded T3 motion onto WH rigs)

| tool | does |
|---|---|
| `tools/anim/t3_bank_skeleton.py` | writes each bank's source skeleton (`game/assets/anim/t3/<bank>/skeleton.json`) for the runtime retarget; `--check` proves bank clips == source GLB channels |
| `tools/anim/t3_row_bake.py` | bakes every move row a moveset references (`rows.pack.json`) and named clips (neutral stance, crouch hold, ...) from the decoded banks |
| `game/js/t3anims.js` `retargetT3Clips` | runtime swing retarget onto Mixamo / Biped / L_R_ / GameRig rigs (same math as `lab/tools/t3_motion_bake.py`) |
| `game/poselab.html` | close-up pose lab: any model × bank × clip × frame, rest view, per-fighter view (`window.__poselab`) |
| `tools/anim/repair_sleeve_weights.py` | k-NN weight transfer inside one GLB (fixed the steve-fox / demonio shirt weighted to the spine) |
| `tools/anim/gltf_codec.mjs` | meshopt/quantization decode for Blender, re-encode after rigging (@gltf-transform 4.1.1, meshoptimizer 0.22.0) |
| `tools/anim/t7_move_resolve.py` | maps a fighter's moveset rows to its T7 base's motbin moves exactly (input path from the base stance + exact T7 damage / first active frame) |
| `tools/anim/t7_move_bake.py` | bakes the resolved rows' real T7 clips (`game/assets/anim/t7/<base>/moves.pack.json`) through the proven 0xC8 path; 0x64 clips when `T7_EXE` is set |
| `tools/anim/t7_anim64_to_c8.py` + `tools/anim/exe_re/` | 0x64 (compressed) clips -> 0xC8 values through Tekken 7's own sampler (Unicorn emulation; `exe_re/README.md`); the exe stays private |
| `tools/anim/t7_attack_probe.mjs` | plays moves by notation in the real game and photographs each one frozen at its active frames, logging the plan (`t7:` = real T7 clip) |

## 3. Rigging (Tripo statics → skinned)

| tool | does |
|---|---|
| `tools/auto_rig/backends/gamerig_backend.py` | GameRig (vendored Rigify feature set) in Blender 4.0.2. This session added exact `--facing`, the bone-heat proxy (world-unit voxel remesh + decimate + Data Transfer weights) and A-pose droop fitting |
| `tools/auto_rig/rig_tripo_static.py` | 2026-10-21. One command for an unrigged Tripo static: codec decode, then gamerig_backend, then smooth_weights, then validate + anim_check, then render_poses, then codec encode. Writes `<name>-rigged.glb` beside the original and never modifies it. Report, renders and logs go to `--report-dir`. Wiring into assets.js stays a reviewed step. Used for Zui A1, which passed. Diablo A1 failed: A-pose winged demon, see `docs/proof/claude-2026-10-21/auto-rig-diablo/README.md` |
| `tools/tripo-intake/` | 2026-10-21. Tripo auto-intake (owner: "rig new Tripo models ASAP to their character rig"). `inbox/<fighter>/attire<N>.glb` → env check → claim (fighter id = roster dir, never guessed; never clobbers; unrigged statics only) → sha256 + `ledger.json` → codec decode → `facing_check.py` (two-geometry-cue facing determination with confidence gate; REFUSEs instead of guessing) → `rig_tripo_static.py --facing` (Blender 4.0.2 + GameRig) → validate (hard gate) + anim_check (flags recorded) → stages `roster/<fighter>/attires/attire<N>/model-rigged.glb` + `WIRING-CHECKLIST.md`. Wiring stays a reviewed step. Runbook: `tools/tripo-intake/README.md`; suite dropzone: `game/tripo-intake.html` |
| `tools/auto_rig/render_poses.py` | 2026-10-21. Blender workbench front/back/side renders of a rigged GLB at given clip times (the anim_check spike frames) |
| `tools/model-audit/gamerig_debug.py`, `gamerig_debug_heat.py` | Blender debug runs that found the facing-estimate failure that left bone heat empty |

## 4. Model audit (read-only checks behind every model claim)

All in `tools/model-audit/`. Each file's header says what it measures and how to run it.
`rigaudit.py` (skinned/unskinned per roster model → `data/skinned.json`, `data/statics.json`),
`bindcheck.py` (node rest vs inverse bind), `armaudit.py` (arm-region verts on non-arm bones),
`facing_cues.py`, `facing_joints.py`, `feet_cue.py`, `feet_cue_all.py`, `meshface.py` (facing cues),
`glbinfo.py`, `check_bank_vs_glb.py`, `check_bank_vs_glb_jin.py`.
`data/kmd_pairs.json` = BNS record → KMD → divmot bank pairing; `data/own.json` = models
with their own files; `data/roster_ids.json` = roster ids at audit time.

## 5. Proof harness (the frames and logs in docs/proof)

`tools/proof-harness/*.mjs`. Playwright + Chromium (SwiftShader). Serve the repo with
`python3 -m http.server 8765` from the root.
`fight.mjs` (fight frames + per-fighter state), `select.mjs` (select screen), `poselab.mjs`,
`rest.mjs`, `resturl.mjs` (rest renders = facing evidence), `dbg.mjs`, `dbg2.mjs`.
Every image cited in a PR was opened and looked at before it was cited.

## 6. Data repair

| tool | does |
|---|---|
| `tools/moveset-restore/restore_sweep_338.py` | restored 49 movesets wiped by merge commit 8ebdc527 from its parent 4cc6b41b |
| `tools/moveset-merge/repair_slots.py` | re-points slots the old notation reading hijacked (Purple Rain 1 -> string 1,2,:4, Phantom 3 -> 3~4, Negativo 4 -> WR 4); report mode exits 1 while any remain (`docs/movesets/SLOT-HIJACK-FIX-2026-11-01.md`) |

## 7. Safety
- `tools/git-merge/git_merge.py` merges a PR as a real merge commit via the Git
  Database API (for machines where SSH is blocked and the merge endpoint is
  unusable): `git_merge.py <PR> [--yes]`. Refuses unless the PR is open,
  not a draft, mergeable_state is clean, and CI is green; 3-way merges every
  touched file and aborts on any conflict instead of clobbering.

- `gitleaks` 8.21.2 runs before every push: `gitleaks detect --no-git --source <changed files>`
  and `gitleaks git --log-opts=origin/main..HEAD`.
- Deletion check before every commit: `git diff --cached --diff-filter=D --name-only` must be
  empty unless the commit message names the deletion.
- Files are staged by explicit path, never with `git add -A`. Tracked `__pycache__/*.pyc` files
  that Python rewrites get restored with `git checkout`, never committed.

## 8. External programs (pinned, installed by tools/setup/setup_toolchain.sh)

Blender 4.0.2 · GameRig (vendored, tools/auto_rig/vendor) · @gltf-transform 4.1.1 · meshoptimizer 0.22.0 ·
n0madic/Tekken3Remake @ e59c4da1 (T3 RE: fight_sim, pose, motion) · Playwright Chromium ·
gitleaks 8.21.2 · numpy / scipy / pygltflib.

## 9. Procedural world generation (TRACK 5, 2026-10-23)

| tool | does | writes |
|---|---|---|
| `tools/worldgen/build-wfc-bundle.mjs` | bundles vendored wavefunctioncollapse CJS → `game/js/worldgen/vendor/wfc.bundle.mjs` (ESM). Mechanical wrap; sources untouched. | `game/js/worldgen/vendor/wfc.bundle.mjs` |
| `tools/worldgen/generate.mjs` | demo CLI: `generateZone()` → proof artifacts (layout json/txt/ppm, heightmap ppm, standalone demo.html, timings json) | `tools/worldgen/demo/` |
| `game/js/worldgen/` | runtime: WFC layouts (`wfc.js`), FastNoiseLite terrain (`terrain.js`), prop scatter (`props.js`), `generateZone()` entry (`worldgen.js`); rule sets in `game/js/worldgen/rulesets/` | — |

Vendored (MIT, provenance in `game/js/worldgen/vendor/VENDOR.md`): wavefunctioncollapse 2.1.0 (kchapelier port of mxgmn/WaveFunctionCollapse), fastnoise-lite 1.1.1 (JS port of Auburn's FastNoiseLite). FastNoise2 proper is C++/SIMD with no JS/WASM build — [RESEARCHED], emscripten path documented. Research: `docs/research/WORLD-GENERATION-2026-10-23.md`. Tests: `test/worldgen.test.mjs` (29).
