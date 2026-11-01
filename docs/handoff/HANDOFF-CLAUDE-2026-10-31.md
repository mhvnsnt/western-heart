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

## 4. The 0x64 problem — SOLVED 2026-11-01 from the exe; Pantera plays King's real T7 attacks

Every T7 attack is a 0x64 (compressed) clip and the community had no 0x64 -> pose path. Solved by reading Tekken 7's
own sampler (`TekkenGame-Win64-Shipping.exe`, private GRE release `t7-shipping-exe-20261031`, sha256 7f2b6872...):
- **0x64 rotation bones are axis-angle**, not Euler: axis = R_y(Y) R_x(X) (0,0,1), q = (axis sin(Z/2), cos(Z/2)).
  **0xC8** rotation bones are Euler: q = q_X(-X) q_Y(-Y) q_Z(-Z). Both land in the same bone space.
- `tools/anim/exe_re/emulate_sampler.py` runs the game's sampler (RVA 0x73ea30) in a Unicorn CPU emulator (CRT
  math stubbed; nothing of the game runs as a program). `tools/anim/t7_anim64_to_c8.py` samples each 0x64 clip with
  it and writes the 0xC8 triple that rebuilds every rotation: re-sampled through the game's 0xC8 path it reproduces
  the game's 0x64 rotations to 3.6e-7. The community decoder differs from the game on frame 1 only.
- `tools/anim/t7_move_bake.py` / `t7_c8_stance_bake.py` take 0x64 clips when `T7_EXE=<exe>` is set; provenance
  records `t7_source.format: 0x64` + the conversion tool + the exe sha256.
- **Pantera <- King:** 29 of 35 rows map exactly (input path from Kg_sKAM00_ + exact T7 damage / first active frame),
  all 0x64, baked into `game/assets/anim/t7/king/moves.pack.json` (FK <= 0.000001 m); `T7_MOVES.pantera` in
  `game/js/t3anims.js`; `test/t7-moves-king.test.mjs`. The game plays its preferred row per input ('1~t8.king',
  'df+1', 'uf+3'), so `t7MoveClip` falls back to the pack clip for the same single input (`t7NormInput`).
- King's moves are acrobatic (flip kick, drop kick to the floor) and Tekken impacts snap in 1-2 frames (kick 3:
  knee chambered 108 deg on frames 13-15, fully extended on frame 16; the game's sampler and the community decoder
  agree), so the King test checks upright starts, floor contact and limb flips instead of Negan's "never inverted".
- Re-run for any character: resolve (`t7_move_resolve.py <GRE>/.../mothead <code> <moveset> out.json`), then
  `T7_EXE=... t7_move_bake.py ...` (see its docstring). Download the exe with the API asset endpoint (section 10).
- **Purple Rain** [T7 code lee] (24 moves, `game/assets/anim/t7/lee/moves.pack.json`) and **Chordz** [lar] (23 moves,
  `game/assets/anim/t7/lars/moves.pack.json`), 2026-11-01, same pipeline (codes `lee` / `lar`, stances
  Le_sKAM00_ / La_sKAM00_; both bound to the jin bank). `test/t7-moves-0x64.test.mjs` covers them (add the next
  fighter as one FIGHTERS row). In game (`tools/anim/t7_attack_probe.mjs`), 1 2 3 4 d/f+1 u/f+4 (Purple Rain) and
  1 2 3 4 d/f+2 b+1 (Chordz) all play `t7:` clips: `docs/proof/2026-11-01/purplerain-chordz-t7/`.
- **11 more fighters, 2026-11-01 (262 moves; T7 source codes in brackets):** Diablo [hei] 20, Skull / Retsu [bry] 28
  each, Saku Ra / Sha [xia] 17 each, Phantom [yos] 21, Gyou / Tobi [hwo] 26 each, Gashadokuro [kum] 27, Aotsuki [pan] 27,
  Nightwolf [jul] 25. Fighters on one base share its dir with their own pack (`T7_MOVES.<id>.pack`,
  bake `--out-name`). Every pack passes the bake's in-game plausibility gate (`t7_move_bake.py` gate / `--regate`: it
  kept Skull / Retsu's d/f+3 out [bry Bx_back_LK]: a knee 15 cm into the floor on the mannequin). **Hosting:** the Pages site is at its 1 GB
  cap, so new packs ship on main only and load from jsDelivr (`fetchT7Json` in `game/js/t3anims.js`: page, then
  cdn.jsdelivr.net @main); `tools/deploy/deploy_delta.py` no longer adds move packs (king / negan / lee / lars stay).
- **Slot hijack fixed on the way (19 slots, 14 movesets):** Purple Rain's 1 fired the 3-hit string 1,2,:4, its 3
  fired 3~3, its 4 fired 4,4,:4; Phantom 3/4 fired 3~4 / 4~3; Negativo, Bruno, Dio and Michiko's 4 fired WR 4. Cause:
  `tools/moveset-merge/merge_sources.py` notation_of read '3~4' as '3', 'WR 4' as '4', and slotted unparsed strings
  on their first hit. Fixed in the tool (and its `notation.py` twin now matches the game's canonNotation); the data
  was re-pointed by `tools/moveset-merge/repair_slots.py`; guard: `test/moveset-slot-hijack.test.mjs`. See
  `docs/movesets/SLOT-HIJACK-FIX-2026-11-01.md`.

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
  - Connectivity as-is does NOT work. The mesh has 67,349 connected pieces, almost all UV-seam fragments under 50 verts, and the big pieces straddle the neck line.
  - Weld vertices by position first, then grow the head region geodesically from the skull and stop at the neck ring.
  - Or mask the hair in Blender (vertex-group select above the shoulders), weight it 100% to Head, and smooth only the neck ring.
  - One material and one primitive, so the hair cannot be isolated by material.
- **ROOT CAUSE (2026-10-31, later): skeleton misfit, same class as Burger.**
  - The wired model's skeleton has horizontal T-pose arms (LeftHand joint y 0.559, mesh space).
  - The mesh's hands hang at y 0.325, about 26° lower, and further forward.
  - Bones sitting above the real arms crush the arms and drag the head.
  - Weight rules on this rig can only patch symptoms.
- **Recipe for the next pass:**
  1. Use the GameRig fitted re-rig from the T-pose static `negativo-a1.glb` (`tools/auto_rig/rig_tripo_static.py --facing +X`). Its anim_check p99.9 before smoothing was 4.96.
  2. Make the hair rigid to Head with a geodesic head territory. Weld the UV seams first: the welded mesh is one piece of 997,691 verts. Seed above the Head joint and grow along edges. Block: the neck cylinder (radius ~0.35 x half shoulder span) below the neck joint, the arm and clavicle flesh (~0.35 x upper-arm length), and anything below Spine2.
  3. Run `smooth_weights.py`.
  4. Pass the gate: `validate.py`, stretch < 2.5.
  5. Do a `NO_REMOTE=1` close-up and attack check.
  6. Commit, then have Muse re-upload the model to B2.

**Negativo — FIXED 2026-11-01 (PR #1463; live once B2 serves the new file):**
- **Real root cause (measured, beyond the arm misfit above):** `refit_skeleton.py` / GameRig scale the template by
  the FULL mesh height, and his hair adds ~0.12 m. Every joint landed high: arm line 0.828 vs the mesh arm 0.653
  (fit space, H 0.98); Spine1 at mouth height, Spine2 at the eyes, Neck/Head in the hair; hip joints at 0.565
  (belly-button height) while his legs split at 0.367; knees 0.08 above the knee. So bone heat put his face on
  chest bones (cone face), his arms on bones above them (crushed) and his abdomen on the thighs.
- **Fix:** `tools/auto_rig/refit_rig.py` (one command, any T-pose fighter) = refit_skeleton -> **refit_landmarks**
  (arms from clean arm slices, armpit, thinnest wrist; hips/knees from the crotch; neck base + chin from the
  mid-line front profile; spine centred between front and back surfaces) -> heat_rebind (bone heat, `--height 2.0`
  to match the wired model: the game renders a GLB at its own size) -> **head_territory** (hair rigid on Head by
  mesh connectivity, geodesic fade where it touches the shoulders) -> **seam_safe_smooth** (welded + continuous
  4-bone limit) -> validate / anim_check / `rig_inspect.py` seams + stretch -> encode.
- **Result:** face 99.4% Head, head + hair 97.3%, arms 74-86% on their own bones, abdomen on Hips/Spine. validate
  PASS; strict every-edge stretch p99.9 2.496 (gate 2.5); official anim_check 1.306; seam copies identical.
  In game (NO_REMOTE): `docs/proof/2026-11-01/refit-negativo/before_after_{1,2,3}.jpg` (b+2, 1, 3, d/f+1 frozen
  at their T7 active frames + Negan's idle). Face, hair, chest emblem and arms are intact in every pose.
- **Not live yet:** the live game loads non-bundled models from B2 FIRST (`asset-config.js`), and Pages is at
  993.9 MB of the 1 GB cap, so this file cannot be bundled. Muse's upload lane must re-upload
  `roster/negativo/attires/attire1/source/negativo-a1-rigged.glb` (sha256 in `model_sha256.txt` of the proof dir).
- **Bugs found on the way, fixed for every rig:** (1) the hard top-4 bone cut flips the 4th bone between
  neighbours (7-9 mm tears on every kick) -> continuous limit; (2) `smooth_weights.py` let UV-seam copies drift
  apart (6,688 on Negativo -> cracks no metric sees) -> seam copies now updated together (test added);
  (3) `anim_check.py` named skin joints 0-3 ("Hips, Spine") for every tearing spike -> now the vertex's own joints;
  (4) a hard head territory tears hair resting on the shoulders (2,157 edges > 20 mm) -> geodesic fade.
  Full list: `tools/auto_rig/README.md` "Landmark re-fit pipeline".

**Cone face universal:** the owner wants it fixed for every fighter that has it. Audit every wired model with
`python3 tools/auto_rig/rig_inspect.py shares --glb <decoded rig>` (face / chin / neck shares on Head) and
`rig_inspect.py seams`; re-rig the T-pose offenders with `tools/auto_rig/refit_rig.py` (A-pose models such as
Burger need the arm fit bent down first: refit_landmarks assumes T-pose arms).

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

1. Negativo: DONE in PR #1463 (re-rig) — needs the B2 re-upload to show live. Then the universal cone-face audit
   (rig_inspect shares/seams on every wired fighter; refit_rig.py for T-pose offenders). Burger (A-pose) after.
2. Negativo T7 attacks (section 5): already wired; they now play on a correct rig.
3. Bob's 0xC8 crouch for Burger; other 0xC8 crouch stances.
4. 0x64: SOLVED (section 4); Pantera, Purple Rain, Chordz and 11 more play their T7 source sets' real attacks
   (names: owner law `docs/rules/NO-SOURCE-CHARACTER-NAMES.md`, fighters by their WH names only). Next: the same
   resolve + `T7_EXE` bake for the other single-source T7 fighters (Diablo, Skull, Retsu, Saku Ra, Sha, Phantom, Gyou,
   Tobi, Gashadokuro, Aotsuki, Nightwolf; each base code in GRE `tkdata/mothead`), then strings / stance moves
   (resolver scope v2). The exe is downloadable from the private
   GRE release through the API (the session proxy authenticates it; the browser_download_url 404s):
   `curl -sSL -H "Accept: application/octet-stream" -o FILE https://api.github.com/repos/mhvnsnt/game-reverse-engineering/releases/assets/<asset id>`
   (asset ids: `mcp__github__get_release_by_tag`). Keep it out of every public repo/bucket; never run it.
5. Model hosting for >20 MB fighters (Muse's lane) so the new stances show live for Diablo, Skull, Sakura, Phantom,
   Nightwolf, Aotsuki, Purple Rain, Chordz, Negativo.

---

**Status note — Claude report, 2026-10-31 (recorded by Muse lane at the owner's order):**

> All 13 checks are green. It merges cleanly into the current main, deletes nothing, and changes only the handoff doc. Merging:
>
> PR #1461 is merged (e090c0f) and its check-in is cancelled. It only updated the handoff doc, so the live game is unchanged. That doc now records what's wrong with Negativo's rig and the step-by-step fix, so the next agent can pick it up.
>
> Nothing new is live since my last update. Three things are still open:
>
> 1. Negativo's rig: the fix (re-fit his skeleton, then make his hair follow his head) still has to pass the repo's stretch check before it ships.
> 2. Model re-uploads: Purple Rain's chest fix only shows in the live game after Muse re-uploads his model to the B2 bucket. I've asked her on #866.
> 3. Pantera's real King moves: I still need the TekkenGame-Win64-Shipping.exe file from your Steam folder, put somewhere private.
>
> That notification just confirms #1461's merge, which I already handled. There are no open PRs left to watch.
>
> Background command stopped — "Serve the repo locally for the Purple Rain A/B": The local test server I'd started for the Purple Rain comparisons hit its 2-hour limit and was stopped. Those comparisons finished long ago, so I haven't restarted it.
