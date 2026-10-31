# Handoff — Claude session 2026-10-30/31 (T7 stances, 0x64 research, deploys, rig triage)

Read this first if you continue any of: real Tekken 7 animation in the game, the live deploy, Burger/Negativo rigs,
the FREE CAMERA placement, or the T7 0x64 joint-frame problem. Owner directives from this session are in
`docs/owner-directives.md` (2026-10-31 section) and the new UI law is in `AGENTS.md`.

## 1. Owner priorities (2026-10-30/31, in order)

1. **Pantera 100% from King**: moves, combos, inputs, animations.
2. Then fighters whose moveset comes from ONE character of the newest game (single-source), then mixed movesets.
3. Then rigs/skeletons (only Pantera is near perfect), then arenas (save defaults so they never get deleted) and modes.
4. **Everything lands on the playable deploy** (live Pages build) so he can test on his phone. No clobbering.
5. Reverse engineer from the real game files (Tekken 7 Steam teardown in the private `game-reverse-engineering`
   repo, "GRE"); community modding tools allowed (read them first; nothing unlicensed vendored).
6. **Build like the real game, play like the player** (new law, see `AGENTS.md`): use real game code/teardowns as
   the template, no free-floating UI over menus/HUD, test by actually playing.

## 1b. Work order (owner law 2026-10-31, AGENTS.md "work order")

- **Short jobs first:** a T-pose model AND a moveset taken straight from ONE source character, with no extra canon moves. Finish each fighter to playable, then deploy it:
  1. rig (no stretch or cone face, correct facing);
  2. stance;
  3. moves, animations and inputs;
  4. a live check.
- **Long jobs later:** A-pose models (fit the skeleton to the pose first), size/form transformations, and canon extra or mixed moves. Checkpoint them (push + merge + note) when they run long, then switch to a short job.
- **Current sequence:**
  1. Negativo (Negan, T-pose static) — re-rig to fix the cone face and arms, then wire his 26 real T7 attacks.
  2. Universal cone-face audit of the other short-job fighters.
  3. Pantera, Purple Rain and the rest of the single-source fighters' moves once the 0x64 joint frame lands.
  4. Long jobs: Burger, then Deathfang, etc.

## 2. What shipped (all merged to main and deployed live)

| PR | What | Live check |
|---|---|---|
| #1137 | main's failing tests fixed; Rage Drive + Urge resolver; slotless movesets | yes |
| #1281 | 0x64 joint-frame research doc + `tools/anim/t7_frame_probe.py` | n/a |
| #1296 | **King's real T7 stance on Pantera** (first real T7 clip in the game) | yes, live fight |
| #1368 | Real T7 stances for 12 more fighters (Heihachi, Bryan, Bob, Xiaoyu, Yoshimitsu, Hwoarang, Kuma, Panda, Julia bases) | Burger live; others need model hosting |
| #1371 | Stances for Purple Rain (Lee), Chordz (Lars), Negativo (Negan) + research results + King clip inventory | local fights |
| (this PR) | FREE CAMERA moved behind PAUSE; handoff/notes; deploy + probe tools; gltfpack fetch fix | — |

Live Pages branch: `gh-pages-m1-20261029` (manifest `deploy-manifest.json` records the main commit + source PR).

## 3. Real T7 animation pipeline (how it works, how to re-run)

**Formats.** T7 clips are 0xC8 (raw floats) or 0x64 (compressed). Bank rule for a motbin move's clip:
`anim_id & 0xC000` -> `0x4000` `<code>rotsm.arc` (MOTA block 0), `0x8000` `common.arc`, `0x0000` `<code>mot.bin`
(first MOTA, inline); index `anim_id & 0x3FFF`. Raw files: GRE `teardown/tekken7-steam/tkdata/mothead/{json,mask,bin}`.
Never copy raw game files into western-heart.

**0xC8 path (works, verified):** Kiloutre's `applyRotationFromAnimdata` (BlenderTekkenDirect `TekkenAnimHelper.py`,
commit `bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1`, no license -> not vendored) on Koenji's
`TekkenMannequin_no_ik.blend` (MEGA folder in the bake tool docstring), Blender 4.0.2 headless, then convert to the
game's bank format (`wh-anim-skel/1` + `wh-anim/1`, 60 fps). FK self-check must be ~0 m.
- `tools/anim/t7_c8_stance_bake.py` — one clip -> `skeleton.json` + `<name>.json` (provenance inside).
- `tools/anim/t7_bl_pose.py` — Blender side.
- Example: see the docstring of `t7_c8_stance_bake.py` (King clip 132).

**Game wiring.** `game/js/t3anims.js` `T7_STANCES` (fighter -> bound bank + baked dir) and `applyT7Stance()`;
called in `fighter.js` `_bindT3` and `select-screen.js`. Only the `stance` action is replaced; every other action
stays the bound bank's. Tests: `test/t7-stance.test.mjs` (data, physical stance checks, wiring, exclusions).
Owner exclusions kept: Zen is NOT Heihachi; Cyborg X and Zui keep their stances; jin_soul on the decision list;
Menajerii/Silvertongue only borrow banks.

**What 0xC8 can still give (inventory, `tools/anim/t7_clip_formats.py`):**
- King: every attack (552) is 0x64 -> Pantera's moves wait on 0x64 (below). Only the stance is 0xC8.
- **Negan is the exception: 126 of 336 attacks are 0xC8** -> Negativo can get real T7 attacks now (section 5).
- 0xC8 crouch stances exist for Bob, Eddy, Lili, Xiaoyu, Yoshimitsu, Zafina (not wired yet).

## 4. The 0x64 joint-frame problem (blocks every T7 attack except Negan's)

`tools/anim/t7_anim64.py` decodes 0x64 faithfully (port of TKMovesets2 `ParseAnimation0x64`), but the decoded
per-bone values live in an unknown per-bone frame. Proven facts, rejected hypotheses and the routes to the exact
answer are in `docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md`. Routes:
1. The game exe (`TekkenGame-Win64-Shipping.exe`, owner's Steam install, stored PRIVATELY) -> Ghidra the routine after
   `TK__Anim_64_sub_140733340`.
2. A live capture on the owner's PC (TKMovesets2/BlenderTekkenDirect know the player-struct addresses).
3. TTT2 same-motion pairs, once the TTT2 lane extracts motion data.
Never ask the owner for passwords; he provides files himself.

## 5. Negativo plays Negan's real T7 attacks (wired 2026-10-31, PR after #1377)

**Status:** 26 moves wired and verified in a local fight; the pack ships in the PR after #1377.
- Example: b+2 plays `t7:b+2__main` = Negan's `Na_4rp` and travels 0.76 m.
- Root motion comes from the raw T7 root channel (`root_motion_fwd_m`), not the applier's hips track.
- Lateral travel stays 0 until its sign is proven on a sidestep clip.
- His model is not hosted live yet, and his rig still needs the fix in section 6.

**Background and design notes:**

- `tools/anim/t7_move_resolve.py` maps moveset rows to Negan's motbin moves by the game's own cancel graph (group
  cancels: cmd `0x800B` -> `group_cancels[move_id..]`, ends at `0x800C`; command u64 = buttons<<32 | direction)
  AND exact frame data (damage + first active frame). v1: 28 single-input rows mapped, 0 ambiguous, all 0xC8.
- `tools/anim/t7_move_bake.py` bakes them into `game/assets/anim/t7/negan/moves.pack.json` (26 clips, FK <= 1e-6;
  2 multi-hit rows skipped). The pack is NOT committed yet (regenerable).
- **Blocker found before wiring:** the 0xC8 root translation lands 90 deg off the body after the community applier
  (T7 forward = slot0 z -> glTF x in the bake). Root motion must be taken from the raw T7 root channel (slot 0,
  mm, forward = +z, both formats agree; King's 0x64 jab root z 21 -> 555 -> 458 mm) before `_rootMotionApply` uses it.
- Wiring plan: `T7_MOVES` loader per fighter; `_attackClipPlan` picks `t7:<moveKey>` before bank rows; retarget
  MUST reuse the stance's skeleton id (`t7:assets/anim/t7/negan/`) so the rest pose cached at bind time is used
  (`analyzeRig` reads the CURRENT pose; a new skeleton id mid-fight would capture a posed rig).
- Negativo's model must be fixed first (section 6) or the attacks will look broken anyway.

## 6. Rig triage (owner 2026-10-31: "fix his model weighting", "cone face ... fix universally")

**Burger** (`roster/burger/attires/attire1/model-rigged.glb`, the wired model):
- Skeleton = standard T-pose facing -Z (arms along X, toes -Z); mesh = A-pose facing **+X** (arms along Z).
  The skeleton and mesh are 90 deg apart and in different poses -> every weight is wrong ("Cronenberg blob",
  torso/legs/feet backwards). `tools/auto_rig/anim_check.py`: edge stretch p99.9 = 42.6 (gate 2.5).
- A 2026-10-23 fix pass (rotate + repose + re-skin + recomputed IBMs) existed but was never landed and its scripts
  were lost (see `tools/gltfpack/BURGER-REEXPORT.md`). Redo it: rotate the static `attire1/model.glb` (+X -> -Z),
  fit the skeleton to the A-pose (arm chains bent down to the mesh arms), heat weights on a decimated proxy in
  Blender -> data-transfer to the full 1M-vertex mesh -> `validate.py` + `anim_check.py` gates -> `gltfpack -cc -kn`.
- His portrait `game/assets/portraits/burger.png` has the broken face baked in; re-render after the fix.
- Canon (`roster/burger/CANON.md`): Bob's FULL moveset + all animations + **Kusaregedo** (Samurai Shodown V/VI)
  moves per form; Slim Bob = uncursed attire (TTT2). No Samurai Shodown data is extracted yet.

**Negativo** (`roster/negativo/attires/attire1/source/negativo-a1-rigged.glb`, 73 joints, 1.24M verts, quantized):
cone face (head/neck verts pulled toward the pelvis) and shoulders/arms crushed across the chest; his skeleton
sits in a T-pose while the mesh does not follow it -> broken bind/weights. Static source
`negativo-a1.glb` (T-pose, faces +X). Same re-rig path as Burger.

**Checkpoint 2026-10-31 (GameRig auto-rig, `tools/auto_rig/rig_tripo_static.py`; proof in `docs/proof/2026-10-31/auto-rig-{burger,negativo}/`):**
- **Burger:** A-pose detected and the arms were fitted. Edge stretch p99.9 went 42.6 (shipped rig) -> 12.4 (anim_check) -> 15.3 after 12 smoothing rounds (smooth_weights sampling). Gate 2.5: NOT shipped.
- **Negativo:** p99.9 4.96 (anim_check) and 9.45 after smoothing. Gate 2.5: NOT shipped.
- GameRig adds non-canonical joints (Breast, Pelvis, `.001` twist bones), and the stress clip flags the Hips->Pelvis bones.
- Next to try:
  - k-NN weight transfer from a clean T-pose donor (`tools/auto_rig/reskin_pantera_weights.py` method, donor `steve-fox.glb`) after rotating Negativo to the donor's facing. Fit the skeleton with `refit_skeleton.py`, because the hair spikes break bbox height matching.
  - Treat hair spikes and props as rigid children of Head/Hips before weighting.
- Burger is a long job (A-pose, forms, Bob + Kusaregedo). It is paused per the work-order law.
- **Purple Rain** (owner 2026-10-31): his chest and spine collapse inward toward the spine, the pull reaches up the neck, and his right arm is affected. Two fixes landed on `roster/purplerain/attires/attire1/model-rerig.glb`:
  - **Spine-chain fix** (another lane, 15:15 UTC, `97b4301ca`, doc `docs/handoffs/RIGFIX-PURPLERAIN-2026-10-31.md`): chest and head weight consolidated off the spine chain.
  - **Clavicle rule** (`tools/auto_rig/fix_sternum_weights.py`): cuts central-chest clavicle weight from 38% to 12%. It is NOT shipped on the model.
    - A valid local A/B (Worker blocked) showed no visible gain over the spine-chain fix (`docs/proof/2026-10-31/purplerain-clavicle/valid-ab-chainfix-vs-clavicle-front-side.png`).
    - Both versions still show a stretched skin WEDGE under the chin in the side view, the "reaching up his neck toward his face" symptom. Next: neck/jaw territory, with chin and jaw verts on Head and a smooth Neck->Head blend on the neck skin.
  - **Not live yet:** the Worker (B2) still serves the old 28,465,008 B model. Muse must re-upload that path (asked on #866).

**Negativo, territory attempt 2026-10-31 (not shipped):**
- His bind is consistent: every skin matrix is the same uniform transform at rest, so this is a weights problem.
- Measured: 42% of his head (with the hair spikes) sits on the clavicles, which causes the cone face. The chest band carries 42% clavicle weight.
- `fix_sternum_weights.py --head --arms` raised the head share to 97%. But its height cutoff splits the hair spikes that hang below the neck joint, and that tears a big flat sheet beside the head (`docs/proof/2026-10-31/negativo-territory/valid-ab-original-vs-headrule.png`).
- Next: build the head territory from mesh connectivity (each hair spike stays whole on the head), or run the seam smoothing (`tools/auto_rig/backends/smooth_weights.py`) after the rule.

**Cone face universal:** the owner wants it fixed for every fighter that has it. Audit every wired model with
`anim_check.py` (stretch per region) and re-rig the offenders the same way.

## 7. Deploy (how the live build is updated)

`tools/deploy/deploy_delta.py` (this PR): guarded delta deploy of origin/main onto `gh-pages-m1-20261029`:
- updates files whose blob differs from the live branch's ACTUAL blobs; adds the T7 stance files the shipped code
  loads (`T7_STANCES` dirs); adds any module the graph check reports missing;
- refuses removals, a tree over the 1 GB Pages cap, or a failing `tools/deploy/check_module_graph.py`;
- fast-forward push only (a concurrent deploy makes it fail, never overwrite). Dry run first, then `--push --pr N`.
Lesson (2026-10-30): deploying fighter.js without its new import broke boot; always run the module graph check on
the ASSEMBLED tree (the script does). After a push, Pages publishes in ~2 min; verify `deploy-manifest.json` live.
Model files over 20 MB are not served live (Pages cap / jsDelivr refuses >20 MB): Muse's Backblaze + Cloudflare
Worker route handles that lane.

## 8. Verification tools

- `tools/anim/t7_stance_probe.mjs` — open `?quick=P1,P2,STAGE`, log each fighter's stance clip/weight, screenshots.
- `tools/anim/t7_closeup_probe.mjs` — stop the AI (stub, never null: the loop calls `ai.update`), take over the
  camera, photograph each fighter front/side large, log arm/head bone positions. Use it to SEE rig problems.
- Both need Playwright (preinstalled) and run headless with SwiftShader; screenshots via CDP with a timeout.

## 9. Gotchas that cost time this session

- `pkill -f <pattern>` matches its own shell command line and kills it (exit 144). Use TaskStop / exact PIDs.
- `git ls-tree -l` in a blob:none partial clone (GRE) fetches every blob to get sizes. Use `--name-only`.
- instruction-gate: "Method actually used" must equal "Method the owner specified" (normalized); put details under
  an extra heading. Its workflow cancels concurrent runs; re-run one at a time.
- `tools/gltfpack/fetch-gltfpack.sh` pinned a nonexistent tag and missed `-DMESHOPT_BUILD_GLTFPACK=ON` (fixed here).
- Fighter close-ups: the fight camera is small; judge rigs only from close-ups (section 8).
- **Remote-first model loading (since the B2 Worker went live, 2026-10-31).** `resolveAssetCandidates()` fetches every non-bundled model from `https://western-heart-assets.mhvnsnt.workers.dev` BEFORE the local file.
  - A local test of a changed model silently shows the OLD B2 copy. Run the probes with `NO_REMOTE=1` (`tools/anim/t7_closeup_probe.mjs` blocks the Worker) to see the local file.
  - Live players see whatever B2 holds, so a fixed model is live only after it is re-uploaded to the bucket under the same repo path. That upload is Muse's lane and needs the bucket credentials.
  - Never claim a model fix is visible live until the Worker serves the new byte size.

## 10. Open items (next agent, in order)

1. Burger re-rig (section 6), then Negativo, then the universal cone-face audit.
2. Negativo T7 attacks (section 5) after his rig is fixed.
3. Bob's 0xC8 crouch for Burger; other 0xC8 crouch stances.
4. 0x64 joint frame (section 4) — needs the exe or a capture from the owner.
5. Model hosting for >20 MB fighters (Muse's lane) so the new stances show live for Diablo, Skull, Sakura, Phantom,
   Nightwolf, Aotsuki, Purple Rain, Chordz, Negativo.
