# FULL CHARACTER-MODEL CHIRALITY + VISUAL AUDIT — 2026-11-07

Owner orders (verbatim):
1. "Bro u fuckin dumbass I think u have the left and right arms swapped around fix all character models man all character models need to be audited and fixed today bro no more bullshittin use industry standard and research ur wasting my time and token working lazy and cheap"
2. "Samurai is the only one who is close to perfect audit all fully and fix all visually broken parts stop making me explain glitches and bugs u can obviously see and fix"
3. (on the Demonio stance pair) "He's still broken"

Governing verdicts: SAM-UR-A1 is the control (pipeline must leave him untouched — verified: his stance numbers and renders are bit-identical with the fix in place). DEMONIO was still broken after #1633. Pond's arms were suspected swapped — settled with data below (NOT swapped in game).

---

## PHASE A — RESEARCH / METHOD (industry standard, sources first)

Method assembled from primary sources before any census run:

- **glTF 2.0 skinning (Khronos spec)**: a skin binds joints via `inverseBindMatrices` (IBM = inverse of the joint's bind-pose global transform); per-vertex `JOINTS_0`/`WEIGHTS_0` (weights normalize to 1). Consequence used throughout: bind joint positions are recovered as `inv(IBM)` translations, and any facing/side math must happen in ONE consistent frame — the scene frame the renderer sees — because files arrive in mixed authoring frames (this repo holds Y-up Blender exports, Z-up FBX-style files whose scene root carries a −90° X rotation, and meshopt-compressed Tripo pulls).
- **Blender armature conventions (Blender manual)**: `.L`/`.R` suffixes drive X-Axis Mirror and Flip Names; AutoName Left/Right assigns `.L` to bones with **positive X** root in armature space. Bone names are a claim, not a fact — sides must be verified against the mesh.
- **Mixamo convention**: `mixamorig:` joints, ~65-bone humanoid; the documented trap (found verbatim in a public retarget codebase): "Mixamo's Left is the character's ANATOMICAL left, which is +x for a character facing +z — screen-RIGHT" — i.e. anatomical-left and screen-left are opposite when a character faces the camera, and screen-space `L_*` naming sits at −x. Side tests must be anatomical (from the model's own facing), never screen-based.
- **Autodesk HumanIK**: retargeting trusts a bone→character mapping validated against a T-stance definition; Mirror Matching maps the opposite side from `l_`/`r_` naming. An unvalidated mapping is exactly how swapped limbs ship.
- **UE5 IK Retargeter**: chains must be named identically across IK rigs and mirrored from the left side (5.2 shipped mirrored finger chains that needed manual correction); Epic's published pitfall table lists "arms or legs swapped → check FK chain mappings, Left/Right, chain start/end" as a standard failure mode.
- **Mirrored geometry**: a negative-determinant transform is a reflection — it flips winding order and normals; the professional fix is to bake the mirror into the asset and keep instance scale positive, never to ship negative-scale nodes.
- **Studio QA for left/right**: asymmetric test poses and single-side animation tests (fire ONE side's move and watch which limb answers) beat static inspection — implemented here as the functional bank test (below).
- **This repo's own prior art** (binding lessons, `game/assets/models/model-facing.json` + `tools/model-audit/facing_cues.py`): facing is read from VIEWED rest renders, never from bone names; the 2026-10-22 nightwolf correction documents the trap of measuring mesh facing through a −Z template skeleton's bone matrices — the auto-rig template skeleton faces −Z inside +Z meshes (`analyzeRig`'s `swapLR` exists because of it). Any instrument that flags Sam-ur-a1 — the owner's approved control, on that same template — is measuring the template, not a defect.

### The instrument (three layers + ground truth)

Tool: `tools/model-audit/chirality_audit.py` (this PR). Pure-Python GLB parse; all geometry in scene space.

1. **Static anatomy** — for every named L/R joint chain (arms incl. every extra chain, legs, fingers): signed side of shoulder/elbow/wrist (+hip/knee/ankle) against the anatomical frame (left = up × forward), where **forward comes from the model's own mesh vertices** (head / toe / torso / foot vertex centroids in bind space), reported separately from skeleton facing (toe-joint/knee votes). A mesh-vs-skeleton facing mismatch is the documented template pattern, recorded as data, not convicted on its own.
2. **Hand chirality** — thumb-base vs pinky-base position (anterior + lateral) per hand, from joints AND from thumb/pinky-dominated vertex centroids; mirrored-geometry scan (negative-scale nodes, negative-determinant matrices). A hand is flagged only when the thumb is BOTH posterior AND medial to the pinky (the mirrored-hand signature); flat bind poses make wrist tetrahedra coplanar, so determinants are recorded, never judged.
3. **Engine-effective (L3)** — simulate the game's actual load: `assets.js` Y-rotation from the `model-facing.json` record (unlisted → feet cue → +Z), then `t3anims analyzeRig swapLR` on Arm X order. The bone the game will drive as canonical LeftArm must land on instance +X (game left). Classifications: OK / SWAPPED-RIG / SWAPPED-RETARGET / SWAPPED-GEOMETRY / UNTESTABLE (named blocker).
4. **Functional bank test (ground truth)** — Tekken notation: 1 = LEFT punch, 2 = RIGHT punch, 3 = LEFT kick, 4 = RIGHT kick. Fire the fighter's real 1 and 2 clips through the game's own retarget onto the fighter's own rig (poselab `showFighter` for T3-bank fighters; the T7 move-pack path `ensureT7Moves`/`t7MoveRetarget` for T7 fighters) and measure per-hand forward-extension peaks. If "1" lands with the anatomical right arm, the fighter is SWAPPED, full stop.

Calibration (before any verdict was trusted):
- Sam-ur-a1 (control): rig names read flipped vs his template skeleton frame; engine-effective **OK** via swapLR — consistent with the owner's "close to perfect". The instrument must (and does) pass him.
- Demonio game GLB and Sam game GLB share the auto-rig template skeleton to full float precision (identical joint positions) — template-family readings are family traits, not per-model defects (their toe joints point −Z in bind on BOTH; Pond has the same trait; feet are not convicted on it).
- First-pass instrument flaws found and fixed before census: IBM-space vs scene-space mixing (Z-up files), hand-determinant overreach, skeleton-facing used as mesh-facing.

---

## PHASE D-1 — DEMONIO (fixed first)

**Reproduction (current main, poselab, game's own engine):** stance Hips→Head direction error 17.1°, arm chain errors 17–19°; posed Hips→Head **line pitch +9.5° forward** (head world offset +0.105 m forward of hips vs the source's −0.043); side view = hunched torso, claws bunched at the mane/face — matching the owner's "still broken".

**Root cause (measured, three layers):**
1. **Bind spine pitch (the fixable defect).** His shipped rig (`roster/demonio/attires/attire1/model.glb`, instance `demonio-a1`) carries an S-curved bind: Hips local pitch +14.5°, Spine −7.4°, Spine1 −8.9°, Neck +23.3° (GLB locals). The retarget composes source motion onto the rig's rest frame, so the pitch survives into every pose: posed line pitch lands ≈ bank pitch + the rig's rest pitch. Sam-ur-a1's bind is dead straight (0.0°) on the shared template and lands at −0.8°. In retarget (G) space the transport itself is near-exact (bank +9.27° vs target +9.50° on the 18-joint composition) — the defect is the target rig's bind, expressed through the pose.
2. **Proportions (documented, not a transport bug).** World-frame FK at stance: his segment directions match the source's wide guard within ~15°; his hands land ~0.1 m lower than the source's (longer arm segments + shoulder bind position) and his head sits ~0.07 m forward (his modeled head/mane anatomy). No measured constant at the retarget layer owns this; it is what retargeting onto a differently-proportioned rig means.
3. **Shoulder/mane gap (weight class → weight-bleed lane queue).** His mesh has NO Shoulder-dominated verts (Sam has them); the shoulder mass rides Head/Spine2 (mane) weights, so when the arm raises, the arm mesh pivots away from mane-weighted flesh — the visible gap behind the mane in the front view. This is a skin-weight defect, queued for the weight-bleed lane's region pipeline (see Remaining queue), NOT patched by hand here.

**Fix (engine layer, the #1620/#1633 measured-constant pattern):** SPINE-PITCH NORMALIZATION in `game/js/t3anims.js` — at the first retarget carrying a bank's stance, probe the stance through the real frame loop: measure the target's posed Hips→Head line pitch by FK from the probe's own tracks. **Gate: engage only when the result is forward-hunched (> +5°)** — matching the bank exactly is NOT the goal (Sam's −0.8° against his bank's −13.5° is owner-approved and stays untouched; he never engages, and with no spine constant his arm path is the unmodified #1633 path). When engaged, bisect one scalar counter-pitch through the real loop to bring the result to +5°, spread evenly over the source spine joints (Spine, Spine1, Spine2, Chest, Neck) as world-frame rotations about the bank's left axis while G composes (children inherit). Cached per (bank, rig) like the arm constants. `t7:` skeletons exempt (head-fix precedent: authored stance acting). Nothing authored, no per-model hacks, no weight painting.

**Composition with the arm layer (caught by the repo's own CI, fixed before merge):** the first version of this fix estimated arm constants first and spine second; the repo's pinned arm-frame test (`test/arm-frame-normalization.test.mjs`, the #1633 test) caught the interaction — on the jun bank the spine rotation moved Megami's LeftShoulder twist residual from +28.4° (over the 25° shoulder gate, corrected) to −12.1° (inside the gate's dead zone, uncorrected). Final composition: (1) spine constant estimated FIRST (the Hips→Head line it measures does not involve the arm joints); (2) arm constants estimated from a probe built WITH the spine correction applied, so they are tuned in the frame the clips will play in; (3) while a spine correction is active, the Shoulder arm gate uses the standard 12° instead of the raised 25° — the 25° gate guards the torso-match split on the bank's own frame, and once this layer deliberately re-pitches the torso, the shoulder residual is dominated by the reframing, not the split. Result: the arm-frame test passes 7/7, and Demonio's posed result is identical to the first version's (below).

**Measured result (poselab, same harness, before → after):**
- Spine-pitch constant for (jin bank × demonio-a1 rig): **−4.8°**.
- Posed line pitch **+9.5° → +4.8°**; head forward offset **+0.105 m → +0.054 m**.
- Direction errors at stance: Hips→Head 17.1° → **12.6°**; LeftArm→ForeArm 18.9° → **14.6°**; LeftForeArm→Hand 18.2° → **14.1°**; RightArm→ForeArm 17.1° → **12.5°**; legs 0.0° → 0.0°; footYaw unchanged (L +2.9°, R +8.4° — feet were never the problem).
- **Sam-ur-a1 control: bit-identical** (every posed value and dirErr unchanged; his pitch −0.8° is under the gate, no constant is ever estimated for him).
- Diablo (heihachi bank): pitch −5.8°, under gate, unchanged by this fix (his separate stance observation is logged in the defect log).
- Test suite: `node --test game/tests/*.test.mjs` — 767 pass / 26 fail, fail set NAME-IDENTICAL with the pristine engine on the same checkout (all 26 are pre-existing stale-checkout artifacts; zero regressions).
- Fight harness (`tools/proof-harness/fight.mjs`, demonio vs pantera): attempted in this VM — the full game boot exceeds the harness's own 60 s `window.__modes` wait under headless swiftshader (the same environment wall that blocked the Megami lane's captures on 2026-11-07). Poselab above loads the same engine + models through the same page stack; the in-fight proof remains owed with the live-build Playwright pass.

**Proof:** `demonio-stance-before.png` / `demonio-stance-after.png` (poselab 4-view: source front/side + target front/side, full body in frame), `demonio-medium-strike-after.png` (grounded medium strike: full side kick, planted stance leg — reads anatomical), pair in the lane's owner folder. The earlier "heavy" frame is an airborne spin that poselab's fixed camera fragments — not used as proof (framing failure class, noted for the Phase C harness).

**Honest residuals for Demonio:** guard hands sit lower than the source's (proportions, item 2 above); claw spread is his bind design (the jin bank has no finger tracks); shoulder/mane gap is the weight-class item queued below. The stance no longer hunches: torso upright in side view, head up, claws clear of the face.

---

## PHASE D-2 — POND (chirality verdict)

**Verdict: NOT SWAPPED — in rig, in retarget, and in function.** The owner's suspicion came from the pose lane's Blender renders, not from the game.

**Evidence** (all on the file the game actually loads — `assets.js`: `pond: '../roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb'`, her full 224-joint source rig):
1. **Static anatomy**: skeleton facing +Z = facing record +Z; named-Left/Right arm chains match the mesh's anatomical sides (L1 flipped = 0); engine-effective **OK** (`swapLR` = false); **hands clean in bind** (thumbs anterior, no chirality flag); no negative transforms.
2. **Functional bank test (ground truth)** — her real T7 move pack (`game/assets/anim/t7/raven/moves.pack.json`, baked 2026-11-03 from Master Raven data): input **1** = move `1~t7.masterraven`, clip `frsd_lp_DVD`, motbin `Nj_lp002` (lp = left punch), active frame 10; input **2** = `oznj_rp_DVD`, `Nj_rp00` (rp = right punch), active frame 10. Fired through the game's own retarget (`ensureT7Moves` + `t7MoveRetarget`, current main engine incl. #1620/#1633) onto her loaded rig, hand forward-extension measured per frame (`pond-functional.json`):
   - **1**: LeftHand peak **0.597 m** forward @0.150 s; RightHand 0.223 m → **LEFT arm delivers input 1. Correct.**
   - **2**: RightHand peak **0.764 m** forward @0.150 s; LeftHand 0.439 m (chamber motion) → **RIGHT arm delivers input 2. Correct.**
   - Stance idle peaks: 0.072 / 0.110 m (guard hands home) — the strikes are real extensions, not noise.
3. **Why the renders misled:** (a) the pose lane rendered her SOURCE BLEND in Blender with a hand-built FK path — not the game's retarget, and not the game's loaded file; (b) Master Raven's stance is bladed: the shot labeled "front" is her side profile and "q34" is her back (the parent agent verified this from the shipped files); in a bladed stance the rear arm crosses the body's silhouette and reads as the wrong arm in a still.

**Method note / near-miss caught by this lane:** her attire folder also holds a 52-joint template export (`model-rigged.glb`) which the game does NOT load for her. Its hands bind supinated (thumbs posterior on both hands — the same signature measured on Chatur's non-loaded 52-joint twin). On the loaded rigs, both fighters' hands are clean. The supinated twins are logged in the census table as HAND-BIND-NOTE (not game-facing); nothing about them changes the verdicts.

---

## SMUTBASE SIX — STATIC CHIRALITY TABLE

From the instrument on each fighter's shipped game GLB (functional tests: Pond above; the other five ride T3/T7 banks through the same retarget — per-fighter functional runs are in the remaining queue):

Game-loaded file per fighter (from `assets.js` MODEL_URLS), instrument verdicts:

| Fighter | Game-loaded file | Joints | Skeleton facing (record +Z all six) | Rig names vs mesh | Engine-effective | Hands | Notes |
|---|---|---|---|---|---|---|---|
| Pond | roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb | 224 | +Z | OK | OK (swapLR false) | clean | functional test PASSED (above) |
| Ryusan | roster/mina-ashido/attires/attire1/model-rerig.glb | 521 | +Z | OK | OK (swapLR false) | clean | |
| Tobi | roster/miruko/attires/attire1/model-rerig-textured.glb | 255 | +Z | OK | OK (swapLR false) | clean | |
| Chatur | roster/rahkasa/attires/attire1/model-rigged-textured.glb | 264 | +Z | OK | OK (swapLR false) | clean | ALL FOUR chains audited (L, R + .002 pair): names on correct sides, no flips |
| Megami | roster/parvati/attires/attire1/model-rigged.glb | 469 | +Z | OK | OK (swapLR false) | clean | vertex-colour defect is a separate staged fix (not this lane) |
| Menajerii | roster/vixen/attires/attire1/model-rigged-noplane.glb | 450 | +Z | OK | OK (swapLR false) | clean | |
| Demonio* | roster/demonio/attires/attire1/model.glb | 62 | template family | OK | OK (swapLR false) | clean | spine-pitch fix above (*not SmutBase; lane priority 1) |
| Sam-ur-a1 (CONTROL) | game/assets/models/sam-ur-a1.glb | 62 | template family | flipped vs skeleton frame (template trait) | OK (swapLR true) | clean | untouched by all fixes |

Non-loaded twins flagged: Pond's and Chatur's 52-joint `model-rigged.glb` template exports bind both hands supinated (thumbs posterior) — recorded as HAND-BIND-NOTE in the census; the game does not load either file for the fighter's default.

---

## CENSUS — PER-MODEL TABLE (instrument run over WH main tree)

Scope enumerated from main: **306 GLB paths** (`roster/*` 170 + `game/assets/models/*` 136 in `data/census-paths.json` of the lane scratch — includes unrigged intake twins and statue files, classified UNTESTABLE with the blocker named).

Completed at first writing: Completed records at this writing: **22 of 306** — verdict counts: OK ×12, UNTESTABLE ×8, NEEDS-FACING-REVIEW(arms along facing axis) ×1, HAND-CHIRALITY-FLAG ×1. Plus 12 transient download-failures (non-sticky, retried by the runner).

| Path | Verdict | Rig names | Engine-effective | Hands |
|---|---|---|---|---|
| roster/armor-king/attires/attire1/model-rigged.glb | OK | OK | OK | clean |
| roster/armor-king/attires/attire1/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/baek/attires/attire1/model.glb | NEEDS-FACING-REVIEW(arms along facing axis) | FLIPPED | DEGENERATE(arms along facing axis; X-order test n/a) | clean |
| roster/baek/attires/master-white/model-custom.glb | OK | OK | OK | clean |
| roster/baek/attires/master-white/model-kevin-diff.glb | OK | OK | OK | clean |
| roster/blanka/attires/attire1/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/buffalo-bill/attires/attire3/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/burger/attires/attire1/model-rigged.glb | OK | OK | OK | clean |
| roster/burger/attires/attire1/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/burger/attires/attire2/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/burger/attires/attire4/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/cain-elias/attires/attire1/model-rigged.glb | OK | OK | OK | clean |
| roster/cain-elias/attires/attire1/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/charger/attires/attire1/model-rigged.glb | OK | OK | OK | clean |
| roster/charger/attires/attire1/model.glb | UNTESTABLE | — | — | no skins (unrigged) |
| roster/mina-ashido/attires/attire1/model-rerig.glb | OK | OK | OK | clean |
| roster/miruko/attires/attire1/model-rerig-textured.glb | OK | OK | OK | clean |
| roster/parvati/attires/attire1/model-rigged.glb | OK | OK | OK | clean |
| roster/rahkasa/attires/attire1/model-rigged-textured.glb | OK | OK | OK | clean |
| roster/rahkasa/attires/attire1/model-rigged.glb | HAND-CHIRALITY-FLAG | OK | OK | thumb-flag: L,R |
| roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb | OK | OK | OK | clean |
| roster/vixen/attires/attire1/model-rigged-noplane.glb | OK | OK | OK | clean |

Emerging pattern from completed records: every `model-rigged.glb` / `model-rerig*.glb` audited so far is **OK** (template-family rigs read names-flipped vs their skeleton frame and are corrected by the game's own swapLR — effective OK); every unrigged `model.glb` intake twin is **UNTESTABLE (no skins)** — those files are not the game's loaded rigs. One record needed instrument fixes before it could be read at all (arms along the facing axis on a meshopt Tripo pull → X-order test degenerates; classified NEEDS-FACING-REVIEW, facing settled by render, in the queue).

### Visual defect log (Phase C, from poselab stance renders viewed by this lane)

- **Demonio** — hunched stance (FIXED, spine-pitch, above); shoulder/mane gap (weight class → queue); guard low (proportions, documented).
- **Diablo** — stance hands measure BEHIND the hips plane in the lab frame (tgt L −0.22 / R −0.37 fwd vs source +0.17/+0.18) while segment dirErrs stay small (10–18°); his model faces −Z (record). SUSPECT — needs his functional strike test before any classification; queued. His earlier proof pair was also CROPPED/mis-framed (parent finding) — the Phase C harness must frame full-body (poselab fixed camera fragments airborne/large models; noted).
- **Sam-ur-a1** — control: no defects; approved by owner.
- Full Phase C (every model, front/q34/side + zoomed crops) is NOT complete — it is item 1 of the remaining queue, run per-model with the functional test so renders and strike data land together.

---

## REMAINING QUEUE (exact — no fake done)

1. **Phase C visual census**: stance renders (front/q34/side, full body, textured) + head/shoulder/arm/hand crops + checklist log for every playable model not yet rendered by this lane (all except Demonio, Sam-ur-a1, Diablo-partial). Harness fix first: poselab's fixed camera crops airborne/large models — frame from the model's bounding box (rest() already does; show() does not).
2. **Census completion**: the streamed instrument run continues over the paths without a completed record at this writing (list generated from the lane's census directory; runner is resumable and survives this document). Any SWAPPED-* or HAND-CHIRALITY-FLAG record it lands gets a functional test + a fix at the wrong layer, in severity order.
3. **Diablo functional test** (heihachi bank 1 vs 2 through poselab) + facing-frame review — classify the hands-behind observation.
4. **Baek attire1** (`roster/baek/attires/attire1/model.glb`): meshopt Tripo pull, arms along the facing axis — settle facing by rest render (poselab `restUrl`), then classify. (His `master-white` attires audit OK, mesh facing −Z, effective OK.)
5. **Supinated-bind twins** (model layer, low priority): the non-loaded 52-joint template exports `roster/tsuyu-asui/attires/attire1/model-rigged.glb` and `roster/rahkasa/attires/attire1/model-rigged.glb` bind both hands supinated. If any future path loads them, re-export with pronated bind hands first. The loaded rigs need nothing.
6. **Demonio shoulder/mane weights** → weight-bleed lane queue (their region pipeline): shoulder-mass verts on Head/Spine2 should carry Shoulder/Arm share so the arm pivots with the torso flesh. This lane does not edit weights.
7. **Multi-arm chains**: Chatur's secondary chains, DXMMII attire1 extra pair, Zen tentacle chains — instrument covers every chain in the static pass (census), functional layer-2 strike test still owed for Chatur (Second Mudra is a two-hit move; verify both pairs' sides).
8. **Megami**: her pale-render defect is root-caused and staged by the Megami lane (vertex-colour strip) — not duplicated here; her chirality rows land with the census.

## FILES IN THIS PR

- `game/js/t3anims.js` — spine-pitch normalization (only code change).
- `docs/proof/2026-11-07/full-model-audit/AUDIT.md` — this document.
- `docs/proof/2026-11-07/full-model-audit/demonio-stance-before.png`, `demonio-stance-after.png`, `demonio-medium-strike-after.png` — poselab proof (game's own engine).
- `docs/proof/2026-11-07/full-model-audit/pond-functional.json` — Pond functional test data (per-frame hand positions for stance + inputs 1/2).
- `tools/model-audit/chirality_audit.py` — the census instrument (owner law: tools land in the repo).
- `tools/anim/pond_functional_test.mjs` — the functional bank test for T7 fighters (Pond's route), repo-relative.
