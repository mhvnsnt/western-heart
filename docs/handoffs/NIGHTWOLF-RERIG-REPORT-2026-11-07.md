# Nightwolf attire1 re-rig + batch joint-offset audit — REPORT

She/her for Nightwolf throughout. Subject: `roster/nightwolf/attires/attire1/model-rigged.glb` (mhvnsnt/western-heart main).
Source file used: main's GLB, git blob `1cfe2f3deddb0a6576dea5c57b006f6cafbdd82a`, 27,414,444 B — **blob-verified** after sparse-clone pull (local copy `nightwolf-main.glb`).

## Method traps found (recorded so the next lane doesn't re-step on them)
- The shipped GLBs are EXT_meshopt_compression + KHR_mesh_quantization. The PyPI `meshoptimizer` binding corrupts the heap / segfaults on these files — decode with the official JS `MeshoptDecoder` (node) instead (`nodetools/decode_glb.mjs`).
- Skinned-vertex world positions must be computed through the skin bind matrix (`jointWorld @ inverseBindMatrix`), NOT the mesh node's world transform: mesh subtrees can carry a frame rotation the IBMs already account for (first batch run produced absurd 2 m "offsets" on such files before this was fixed). The bind matrix also carries the quantization dequantization (her file: uniform scale 0.835 + y-offset 0.835, consistent across all joints to 1e-6).
- `/tmp` is a 512 MB tmpfs shared with other lanes; write intermediates to home scratch.

## Task 1 — Batch joint-offset audit (all 100 PR #1641 payloads + 10 sibling files in out/)
Method: dominant-vertex test per arm bone (Arm/ForeArm ×2 sides): verts whose top weight (>0.5) is that bone; flag if a bone owns 0 dominant verts or the median distance from its dominant verts to its bone segment exceeds 8 cm (scale-checked as seg/height ratio > 0.047). Probe validated against the diagnosis lane's Blender numbers on her file (forearm centroids (±0.51, y 1.197) vs joints y 1.412 → 21.5/21.6 cm — exact match) and against the healthy Yukihyō control (clean).

RESULTS (final, 2026-11-08; full machine-readable list in `audit_summary_final.txt`, raw records in `audit_results.jsonl`, summarizer `finalize_audit.py`):

Corpus = 110 files (the 100 PR #1641 payloads + 10 sibling outputs in the same out/ folder).

| Class | Count | Meaning |
|---|---|---|
| Severe | 54 | an arm bone owns 0 dominant verts, or median dominant-vert distance to its segment ≥ 0.15 m |
| Moderate | 34 | worst arm-bone segment distance 0.08–0.15 m |
| Clean | 12 | all four arm bones ≤ 0.08 m with dominant geometry |
| **L/R-swapped weights** | **7** | separate defect class, see below |
| Unmeasurable | 3 | probe does not apply / corrupt data, see below |

**Every model whose arm-chain joints sit >8 cm from their dominant geometry = the 54 severe + 34 moderate lists in `audit_summary_final.txt`.** Nightwolf's own PR file sits in the severe list as expected (worst_seg 0.256, height_off 0.216, LeftArm 0-dominant). Other severe standouts: Demonio winged-devil (worst_seg 0.672, LeftArm+LeftForeArm 0-dominant), Zangief attire1 (0.432, RightForeArm 0-dominant), Charger attire1/attire2 (0.278/0.346, height_off 0.263/0.271), Zen tentacle (0.309) and oversoul (0.284, RightForeArm 0-dominant), Thor attire1 (0.268, height_off 0.271), Waterfall attire1 (0.222, both forearms 0-dominant), Diablo attire1 (LeftArm+LeftForeArm+RightForeArm 0-dominant), Burger attire1 (both forearms 0-dominant). The 12 clean files: Kronos attire2, Negativo attire1+attire2 (the pipeline's own refits — the method's proof), Sakura attire1, Cyborg-X attire1 refit, Kinpo attire1, King-Tyrant attire1, Silvertongue attire1, Deathfang attire1, and the three T3-real lab models (Anna, Nina, Bosconovitch).

### The 1.75 m cluster anomaly — RESOLVED: L/R-swapped skin weights (real defect, not a probe artifact, not a joint offset)
Seven files shared an impossible signature (worst_seg ≈ 1.04–1.09 at height exactly 1.75): `kiko-tanaka`, `kiko-tanaka_alt1`, `purple-rain-main`, `mariposa`, `mariposa-monarch-rigged`, `saku-ra-main`, `cape-jones` (all under game/assets/models/ except the monarch). Diagnosis:
- Their skeleton is the standard game body skeleton — joint positions are byte-identical to the healthy `pantera-body.glb` (LeftArm at (−0.209, 1.479, 0.057), etc.), and two independent decoders (this lane's MeshoptDecoder tooling and the repo's own gltf_codec) produce identical measurements, so it is not a decoder or probe-frame bug. (The files' IBMs look near-zero only because their positions are KHR-quantized integers 0–16383 with the dequantization scale 0.00010763 carried on the mesh node — the skin bind matrix reconstructs the frame exactly, verified to 3.5e-7 against exact per-vertex skinning.)
- A mirror test (`probe_mirror.py`: distance of each bone's dominant verts to its OWN segment vs the OPPOSITE side's segment) discriminates perfectly. Healthy controls — pantera-body, saku-ra_alt1, Negativo a1, Yukihyō a1 — read own 0.055–0.147 vs mirror 0.39–1.22. The seven cluster files read **own 0.45–1.09 vs mirror 0.12–0.17**: each arm bone's geometry sits on the opposite side's segment.
- A full-limb dominant census on kiko-tanaka confirms the swap is not arms-only: LeftHand/LeftUpLeg/LeftLeg dominant centroids all sit at +X while their joints sit at −X, and vice versa for the right side. **Classification: WEIGHT-stage L/R mirror swap (weights assigned to the mirror-named bones), joints correctly placed.** In bind pose these files render fine; under named-bone animation the left-side animation drives the right-side geometry. Fix class = swap the L/R joint indices in the weights (or re-derive weights); a joint refit is NOT needed.

### Unmeasurable (3, excluded from tiers with reason)
- `roster__parvati__attires__attire1__model-rigged.glb` (Parvati attire1, Megami's base): Rigify lattice rig — 469 joints × 7 skins, arm weights split across bend/twist/twk helper bones (`upper_arm.twist.twk`, `forearm.bend.twk`, …). The canonical LeftArm/RightArm/LeftForeArm/RightForeArm control bones own 0 dominant verts **by that rig's design** — the dominant-bone test does not apply. Not a joint-offset flag. (Her decode via the generic node decoder ran pathologically on the >200 KB JSON chunk; the repo codec decoded her fine: `parvati_dec.glb` in this scratch.)
- `roster__star__attires__attire5__model-improved.glb`: corrupt position data — 681 NaN verts (pre-existing, already documented in PR #1641; identical before/after that PR) plus garbage-magnitude floats, on a 29-joint Z-up Tripo rig family. The astronomic values in the raw batch summary were artifacts of those verts and are withdrawn.
- `roster__silvertongue__attires__attire2__model.glb`: same family — 588 NaN/garbage position verts; unmeasurable for the same reason.

## Armor King attire1 — named check (DONE)
- **Joint placement: CLEAN.** Head/Neck joints centered on his head geometry; Head bone axis [0,1,0] (vertical) in bind; arm height offsets 0.005 m (Nightwolf's: 0.215 m). Not her defect pattern.
- **Face weights: weight-stage bleed (milder cousin of hers).** He faces −Z in his own file (toe joints and face geometry agree). Face slab on his front: Head 52% + Neck 8% = 60% head chain; **40% rides Spine2** — chest rotation drags his face, the plausible mechanism behind the tilted-back head in his after-still.
- Arm dominant geometry sits 0.18 m toward his front from the segment line with height exact — chest/pelt mass weighted onto the Arm bones; same weight-stage family, not misplaced joints.
- **Classification: WEIGHT stage (inherited bleed), not auto-rig joint placement.** A de-bleed-class fix applies to him; a re-rig does not.
- Observation for the lead: his in-file facing is −Z.

## Task 2 — Her re-rig
Route: the pipeline's own `tools/auto_rig/refit_rig.py` (the Negativo-proven chain: landmark skeleton refit → bone-heat rebind → head_territory → secondary chains → seam-safe smoothing → validate/anim_check/rig_inspect gates → meshopt encode). No hand edits anywhere.
- Template: pipeline default `pantera.glb` (49 joints). Her shipped skeleton is the same set + `LeftHandThumb3`; the refit output carries the template's 49 — her thumb-tip verts are heat-skinned onto Thumb2/Hand. Game banks carry no finger tracks (fingers sit at rest curl in-game), so no driven motion is lost; flagged here for the lead's call.
- Facing +Z (her toe joints point +Z). --height 1.67 = her shipped file's dequantized geometry height (the replaced model is her own current file; in-game size unchanged).
- Junk stripped by construction: the rebuild exports a fresh GLB — the embedded `CMU135_04_boxing` animation and the material-less `Icosphere` node do not carry over (verified on the output, below).
- Baseline (main's file, this lane's probe): face slab Head 33% + Neck 20% = **53% head chain** (the diagnosis's 67% figure was measured on the de-bleeded PR file); LeftArm dominant verts **0**; forearm height offset **21.5/21.6 cm**.

RESULTS (2026-11-08):

**Deliverable: `nightwolf-rerigged-final.glb` in this scratch — 28,428,932 B, 58 joints, 1 mesh, 0 animations.** Not pushed anywhere; the lead lands it after own-eyes verification.

What the chain did, in order: repo codec decode → refit_skeleton (Pantera template fit) → refit_landmarks → **one measured correction** (below) → Blender bone-heat rebind at height 1.67 → head_territory → secondary_chains (8 `hair_jiggle` bones for her braids) → gates → repo codec encode → CMU test clip stripped at export (gltf-transform prune on the uncompressed rig, then encode). The embedded `CMU135_04_boxing` junk and the material-less `Icosphere` node from her shipped file do **not** carry over (0 animations, no Icosphere node in the output).

**The one correction (round 1 → round 2):** the automatic landmark fit collapsed her RightArm joint to the body centerline (fit x −0.0013; its cross-section window merged with her torso/feather mass) and sat RightForeArm 0.11 inward; her left chain fitted perfectly. Per the diagnosis REPORT §6's own prescription (joint positions from measured geometry), `fit_landmarks.json` was patched before the heat rebind: RightArm 'to' := exact mirror of the fitted LeftArm (−0.2403, 1.4291, 0.049); RightForeArm 'to' := (−0.503, 1.4049, −0.0226), on the fitted RightArm→RightHand line at the LeftForeArm mirror x. Original preserved as `refit-report/fit_landmarks.orig.json`; each patch carries a `corrected` note in the JSON. **No weights were hand-edited anywhere** — the heat rebind re-derived every weight from the corrected skeleton.

**Acceptance measurements (probe on the final encoded file, decoded back — identical to the pre-encode rig):**

| Metric | Before (main's file) | After | Bar |
|---|---|---|---|
| Face slab, Head+Neck share | 53% (Head 33% + Neck 20%) | **anatomical face slab 100.0% Head** (23,833 verts, y 1.44–1.64) | ≥95% |
| Face region (rig_inspect shares) | — | Head 96.8% | — |
| LeftArm dominant verts | **0** | 30,447 | owns geometry |
| Forearm height offset L / R | 21.5 / 21.6 cm | **0.6 / 0.4 cm** | ~4 cm |
| Arm height offset L / R | ~21 cm | 5.7 / 4.5 cm | ~4 cm |
| Arm segment median dist (LA/RA/LF/RF) | 0.26 / 0.26 / 0.22 / 0.22 m | **0.050 / 0.083 / 0.043 / 0.070 m** | ~4 cm class |

Residual medians on the two Arm bones (5.0 / 8.3 cm) are inflated by shoulder + chest-edge mass inside their dominant sets (RightArm owns 97,934 verts including shoulder armor); the forearm tubes — the geometry that was 21 cm adrift — sit at 4.3 / 7.0 cm median with p90 5.3 / 12.8 cm, and both forearm height offsets are under 1 cm. Height offsets, the diagnosis's own headline metric, are inside the bar on all four bones except LeftArm at 5.7 cm (its dominant set includes low torso-edge verts; its segment median is 5.0 cm).

**Gates (pipeline's own, on the final rig):** validate.py **PASS** (valid glTF, skinned, height 1.67 m, feet at y=0, fingers symmetric); rig_inspect seams **PASS** (349,695 seam-copy verts, max L1 disagreement 0.0004); anim_check on the baked CMU boxing clip: official edge_stretch_p999 **3.254** (gate 2.5), 70 tearing spikes all on the RightHandThumb3|Thumb2 pair (thumb-tip verts riding the thumb chain under the pinned-root boxing window — the spike class refit_rig's own report note treats as motion, listed here for the lead's judgment); rig_inspect strict stretch p999 13.003 with over-2× edges concentrated in her skirt/feather inter-leg mass and hair (median elongation of over-2× edges is 3.87 mm on a 2.21 mm median rest edge — dense small-edge geometry, not limb tears).

**Known gap — seam_safe_smooth:** the chain's smoothing step died with SIGKILL (memory) three times on this box, including one solo run that survived 4 rounds (p99.9 13.003 → 26.6 → 23.7 → 22.1, not converged) before dying in round ~4. The deliverable is therefore the post-territory/chains rig (`rig_h` stage) without the smoothing pass. The acceptance metrics above do not depend on it; if the lead wants the strict-stretch gate chased, the smooth step needs a bigger-memory box, not a different method.

**Skeleton deltas for the lead's call:** (1) 58 joints = the 49-joint template set + her mirrored LeftHandThumb3 + 8 hair_jiggle chain bones (validate flags the jiggle bones as "unmapped" — they are the pipeline's standard secondary chains, driven by the game's springbones). (2) The refit redistributed her spine proportions (Neck/Head joints sit lower than in her shipped file at the same total height 1.67 m — template proportions); the anatomical face is 100% Head-weighted and the harness frames below show her head carried naturally. (3) Her mesh was never moved; the statue geometry is byte-identical in bind (bind render matches her shipped bind).

**Proof renders (game harness rebuilt in `harness/` — the game's own current t3anims.js retarget, Three.js, Playwright; the diagnosis lane's /tmp harness was lost in a VM reboot):**
- `proof-bind-front.png` — clean T-pose bind, head up, war paint visible.
- `proof-julia-stance-t035.png` — **PASS**: a crouched fighting guard, head up, war paint visible, one forearm crossed in front as a guard, other hand raised; her braids sweep behind her (thick modeled strands frozen mid-motion) and her back bow/arrows are visible at her side. Contrast `proof-julia-BEFORE-original-file.png` (main's current file, same harness, same frame): one arm sticks straight out sideways — the clavicle-glued arm of the diagnosis.
- `proof-king-stance-t035.png` — **PASS**: upright clean guard, both hands in front (bone dump: hands at z +0.35/+0.46 in front of the body), head up, war paint visible.
- Bone-dump JSONs for all frames sit beside the PNGs in `harness/out/`.
