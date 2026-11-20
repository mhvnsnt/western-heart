# Parametric Body Models — Deep Research (Rig Perfection Wave)

**Date:** 2026-10-17 · **Lane:** parametric-body research
**Status:** MPFB2 pulled COMPLETELY and WIRED (see `production/tools/mpfb2/WIRING.md`).
ANNY proven working locally (CC0). MHR/ATLAS/SOMA verified via published sources.

## 1. THE IDENTIFICATION — "the body equivalent of Google GNM"

**Answer: MPFB — MakeHuman for Blender (MPFB2, v2.0.18).**

Correction history, stated plainly (per VERIFY-BEFORE-CLAIMING):
- 2026-10-17 ~20:40: I first identified Meta's **MHR** (with ATLAS integrated) as
  "the body equivalent of GNM" — a different org (Meta vs Google), parametric body
  family, model + perception stack. Technically defensible, but **not what he meant**.
- 2026-10-17 ~20:46: owner corrected: *"y'all actually told me about it — the Google
  GNM body equivalent, customized bodies or something."* He was right — on 2026-10-13
  the team told him: *"GNM is Google's open-source face morphing, Apache 2.0. MPFB
  (MakeHuman for Blender, the body morphing equivalent)."*
- 2026-10-17 ~20:49: owner directive: *"pull it [MPFB] in completely, wire it up
  completely into the repo."* Done — see WIRING.md.

**Forge3D claim — CONTRADICTED by source of truth.** The 2026-10-13 history claimed
the Forge3D track (2026-10-06/07) "PROVED GNM semantic body morphs + 58-bone retarget
(commit 43ca3db, mhvnsnt/Forge3D)." I checked: commit `43ca3db` exists **neither** in
the local `~/workspace/Forge3D` clone **nor** on GitHub (`gh api repos/mhvnsnt/Forge3D/commits`
— latest are 245f890, f675702, 4503478, 23eff54). The Forge3D GNM-pipeline proof is
**unverified** — do not cite it as prior work. The MPFB wiring in THIS repo
(`cape_jones_mpfb_wired.blend`) is the first verified implementation.

## 2. MPFB2 — what it is (verified from the pulled source)

- **Repo:** `makehumancommunity/mpfb2` (pulled: `production/tools/mpfb2/`, commit 3af0cd5,
  v2.0.18). **Code: GPL-3.0-or-later. Assets/data: CC0-1.0.** (GPL already precedented
  in this repo — AnimeEffects, BlenRig 6.)
- **Base mesh:** 19,158 verts (`data/3dobjs/base.obj`), CC0.
- **Morph targets:** hundreds of `.target.gz` across `data/targets/`
  (arms, legs, torso, stomach, breast, buttocks, hip, pelvis, neck, head, face parts,
  hands, feet, asym, macrodetails). Both measurement-based (`measure-shoulder-dist`,
  `measure-waist-circ`, …) and sculpt-based (`torso-muscle-pectoral`,
  `stomach-tone`, `l-upperarm-muscle`, …), plus macro props (gender/age/weight/
  height/muscle via `reapply_macro_details`).
- **Rigs** (`data/rigs/standard/`, each with precomputed `weights.*.json` —
  auto-skinning with zero hand-painting):
  | rig | bones | notes |
  |-----|-------|-------|
  | `default` | **163** | canonical MakeHuman rig — **the full skeleton** |
  | `default_no_toes` | ~143 | no toe bones |
  | `mixamo` | **52** | Mixamo bone naming/topology |
  | `mixamo_unity` | 52 | Unity variant |
  | `game_engine` / `game_engine_with_breast` | ~60 | simplified |
  | `cmu_mb` | — | CMU mocap compatible |
  | `openpose` | — | OpenPose keypoint topology |
  | `rigify.*` | — | Rigify generation from MPFB |
- The **default 163-bone rig** is the deliverable skeleton: `spine01`–`spine05`
  (5-segment spine), `neck01`–`neck03`, `pelvis.L/R`, full clavicle/shoulder/
  `upperarm01/02`/`lowerarm01/02` chains (segmented twist limbs), full finger
  segments (`finger1-1…`), toe segments, `breast.L/R`, eyes.
- **Animation:** `AnimationService` — BVH import (`import_bvh_file_as_pose`),
  `make_cyclic`, Mixamo workflows; `animops/operators/mapmixamo.py` (Mixamo bone
  map); pose libraries (`data/poses/`: `default_fk/t-pose.json`, …).
- **Expressions:** 2.0.16 added the full expression toolset (ARKit-compatible
  `faceunits01` asset pack, shape-key driven) — relevant to the GNM-face lane.
- Headless: proven working in Blender 4.5 LTS via direct import + two mocks
  (`extension_path_user`, `get_preference`) — see `mpfb_proof.py`. No upstream
  modifications.

## 3. THE FULL LANDSCAPE — ranked by production readiness + license usability

| # | Model | Org | License | Usability verdict |
|---|-------|-----|---------|-------------------|
| 1 | **MPFB2** | MakeHuman community | Code GPL-3.0, assets **CC0** | ✅ **PULLED + WIRED.** Body-morph equivalent of GNM per owner. |
| 2 | **ANNY** | Naver Labs Europe (HUMANS) | **CC0** | ✅ **PROVEN locally** (numpy backend, auto-download). 13,718 verts, 163 bones, 11 semantic shape params + 256 local blendshapes. Best free drop-in body model. Paper: arXiv 2511.03589. |
| 3 | **MHR** (Momentum Human Rig, ATLAS integrated) | Meta | **Apache-2.0** | ✅ **PULLED 2026-10-18** (`production/tools/mhr/`, upstream @ d96fafa, 9MB code+scripts+docs only; model assets runtime-downloaded via `mhr-download-assets`, Kaggle-side). 18,439 verts, 127 joints, 7 LODs, FBX rigs + `corrective_blendshapes_lodN.npz` per LOD, 45 identity / 204 pose / 72 FACS expression params, SAM 3D Body perception. The "different org's GNM" — Meta's answer. Wiring: `production/tools/mhr/CAPE-JONES-WIRING.md`. |
| 4 | **SOMA-X** | NVIDIA | **Apache-2.0** (own-eyes verified 2026-10-18: repo LICENSE + SPDX badge + README "licensed under Apache-2.0"; gh api `license: Apache-2.0`) | ✅ **PULLED 2026-10-18** (`production/tools/soma-x/`, upstream @ 56a3d957 v0.3.4, 2.3MB code+scripts+docs, 124/124 py pass py_compile; `assets/` holds only Git-LFS pointer text — real identity assets runtime-download from HF `nvidia/SOMA-X` at first use, Kaggle/GPU-side only; SMPL-X + MANO backends need user-supplied licensed model files, NOT redistributed). Unifies 5 backends (SOMA-Shape, MHR, SMPL-X, Anny, GarmentMeasurements) under one 77-joint skeleton + **single MLP pose-correctives** model. Best corrective tech to study. Wiring: `production/tools/soma-x/CAPE-JONES-WIRING.md`. |
| 5 | **ATLAS** | Meta + CMU (ICCV 2025) | via MHR (Apache-2.0) | Research integrated into MHR: decoupled skeleton/shape, sparse **non-linear** pose correctives (MLP per joint + geodesic sparsity), 76 skeletal params. |
| 6 | **SMPL-X** | MPI | registration, **non-commercial** | Industry baseline. 10,475 verts, 54 joints, 207 pose corrective blendshapes B_P(θ). Code usable (Blender addon, `smplx` pip) but **model files need registration + are non-commercial** — document, don't ship. |
| 7 | **SKEL** | MPI | registration | Biomechanical: anatomically-true joints, bone-interpenetration constraints. Study its joint definitions for our joint placement. |
| 8 | **STAR** | MPI | registration | Sparse pose correctives (ECCV 2020) — direct ancestor of ATLAS's correctives. |
| 9 | **SUPR** / **imGHUM** / **GHUM(L)** | MPI / Google | registration / research terms | Expressive (SUPR), implicit (imGHUM), Google's older body (GHUM). Documented; not pulled (license friction). |
| 10 | **GNM Head** | Google | permissive (commercial OK) | The FACE side. 17,821 verts, 170 head + 80 teeth components, 383 expression controls. Blender addon exists (Nathan Dickson). Face lane's job. |

**2026 state:** the field moved — late 2025 gave us the two commercially-permissive
bodies (ANNY/CC0, MHR/Apache-2.0); 2026 gave us GNM Head (Google, permissive) and
MPFB2 2.0.16's expression toolset. Registration-walled MPI models (SMPL-X et al.)
are now the *study* tier, not the *ship* tier.

## 4. HOW THEY SOLVE OUR EXACT PROBLEMS

**Elbow/knee candy-wrapper collapse.** SMPL-X: 207 linear pose corrective
blendshapes `B_P(θ) = P·(R(θ)−R(θ*))` — vertex offsets as a function of joint
rotation, baked from scans. ATLAS/MHR: sparse **non-linear** MLP correctives per
joint (geodesic-sparsity masked, so no long-range bleed). MPFB: ships corrective
*targets* + segmented limb bones (`upperarm01/02`, `lowerarm01/02`) so twist
distributes across segments instead of collapsing at one joint.

**Twisting without collapse.** All of them segment the forearm/shin into 2+
twist bones with smooth weight ramps (MPFB's weights JSONs are the free,
inspectable reference). Our 85-bone rig has single `forearm_*`/`shin_*` — this
is the structural gap.

**Volume preservation.** We have DQ preserve-volume + CorrectiveSmooth (good
base). Parametric models add *pose-dependent* volume: muscle-bulge correctives
(MPFB `torso-muscle-*`, `l-upperarm-muscle-*` targets are literally this shape
library; MHR's MLP correctives learn it from scans).

**Spine.** Our rig: `spine_1, spine_2, chest` (3 segments). MPFB default:
`spine01–05` (5) + 3 neck bones. ATLAS: 76 skeletal params incl. per-vertebra
lengths. The wave's "real flexible spine" = 5 segments minimum.

## 5. CONCRETE PORTING PLAN (for the deformation + spine lanes)

1. **PSD correctives as driven shape keys (SMPL-X B_P pattern).** Bake per-joint
   corrective deltas → Blender shape keys driven by bone rotation (drivers on
   `pose.bones["forearm_L"].rotation`). Source shapes: MPFB target library
   (already in repo) for hand-authored correctives; MHR
   `corrective_blendshapes_lodN.npz` as the learned reference (pull when disk
   allows). Priority joints: elbow, knee, shoulder, hip.
2. **Segment the limbs.** Split `forearm_*`→2 bones, `shin_*`→2 bones,
   `upperarm_*`→2 bones with MPFB-style weight ramps (copy the ramp *shape*
   from `weights.default.json`, refit to our proportions). This is the
   anti-candy-wrapper structural fix.
3. **5-segment spine + 3-neck.** Adopt MPFB's `spine01–05`/`neck01–03`
   segmentation and joint positions (scaled to 0.925 m) into the 85-bone rig.
   `MPFB_FullSkeleton` in `cape_jones_mpfb_wired.blend` is the measured reference.
4. **Anatomical joint placement (ATLAS/SKEL lesson).** Joints from the skeleton,
   not the skin: re-derive our joint centers from the MPFB skeleton's
   proportional landmarks instead of eyeballing.
5. **Auto-skinning.** MPFB's precomputed weights as the prior; bakeoff = MPFB weights vs our W5r surface-heat-diffuse on the 7-pose test. ❌ **Adaptive Auto Skinning (Sept 2026, Jessy Leite) REJECTED 2026-10-18** — $35.00 USD paid product on SuperHive (own-eyes verified: JSON-LD `Product.offers` price 35.00 USD, "Free updates within the version you bought", 30-day refund), NOT free, no open-source repo — fails the free+commercial-use license law. Technique notes kept for reference only: adaptive voxel grid (coarse body, refines where surfaces near-touch; finger separation), GPU solver reading skeleton *geometry* not bone names (Mixamo/ARP/custom all bind the same), 80.9% dominant-bone match vs artist weights on a 202-character benchmark.
6. **Muscle layer.** BlenRig 6's MDEF cage (already in repo) is our muscle
   system *today*; MPFB's muscle *targets* are the shape library that drives
   it. (Ziva-class FEM is $$$; Shirzad Bahrami's open FEM/XPBD tool is
   unreleased — watch, don't wait.)
7. **Auto-rigging (owner priority, NO-HAND-TOOLING law).** Ranked: **UniRig**
   (MIT, local CUDA 8GB+) → AccuRIG (free tier, joint refinement) → Mixamo
   (free/Adobe ID, royalty-free output) → Cinevva/Tripo/Meshy (credits).
   MagicArticulate stays skeleton-only (verdict in
   MAGICARTICULATE-WEIGHT-VERDICT-2026.md).

## 6. WHAT'S PULLED / PROVEN / PENDING

- ✅ **Pulled:** `production/tools/mpfb2/` (complete, 106 MB, commit 3af0cd5,
  v2.0.18; code GPL-3.0, assets CC0).
- ✅ **Wired:** `3d-assets/cape-jones-rig/cape_jones_mpfb_wired.blend` (147 MB) —
  5 semantic morphs as driven shape keys on the real 910k-vert CJ mesh
  (`MPFB_bulk/height/shoulders/belly/limbs` ← custom props `mpfb_*`), plus the
  163-bone `MPFB_FullSkeleton` scaled to 0.925 m in-scene.
- ✅ **Proven:** `mpfb_proof.py` (headless create+morph+rig+render),
  `mpfb_wire_cj.py` (transfer), `mpfb_anim_proof.py` (morph sweep, skeleton,
  scripted knee/elbow/spine poses, Mixamo-rig generation). Renders in
  `3d-assets/cape-jones-rig/mpfb_proofs/`.
- ✅ **Pulled:** `production/tools/mhr/` (MHR Momentum Human Rig, 9 MB code +
  scripts + docs, upstream `facebookresearch/MHR` @ d96fafa, main; Apache-2.0
  own-eyes verified in-tree; 25/25 py pass py_compile; model assets NOT in repo —
  download GPU-lane via `mhr-download-assets`; wiring in
  `production/tools/mhr/CAPE-JONES-WIRING.md`).
- ✅ **Proven:** ANNY (CC0) loads + forwards in the numpy backend.
- ⏳ **Pending:** real Mixamo FBX retarget (needs Adobe account —
  browser lane); Adaptive Auto Skinning license check — ❌ **REJECTED 2026-10-18**
  (paid $35 SuperHive product, not free, no OSS repo — fails the free+commercial
  license law; bakeoff = MPFB precomputed weights vs our W5r surface-heat-diffuse
  only; AAS technique notes kept in §5 for reference); SOMA-X license check — ✅
  **VERIFIED 2026-10-18** (Apache-2.0, own-eyes: repo LICENSE + SPDX + README;
  NVlabs/SOMA-X @ 56a3d957, 820★, ~21MB code-only, zero weights in repo —
  runtime identity assets download from HF `nvidia/SOMA-X` at first use,
  Kaggle/GPU-side only; SMPL-X/MANO backends need user-licensed files, NOT
  redistributed) — ✅ **PULLED 2026-10-18** (`production/tools/soma-x/`, upstream
  @ 56a3d957 v0.3.4, 2.3MB code+scripts+docs, 124/124 py pass py_compile;
  assets are LFS pointers only, weights download GPU-side; wiring in
  `production/tools/soma-x/CAPE-JONES-WIRING.md`); SOMA-X 7-pose bakeoff vs W5r
  + MPFB weights once pulled.
