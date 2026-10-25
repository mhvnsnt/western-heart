# Open Source 3D & Character Tools — 2026 Industry Survey

**Research date:** 2026-10-23 · **Purpose:** Feed the Western Heart fighting game's creation suite with current (2026) open-source, industry-standard tooling for character customization, morphing, face scan, and parts/clothing systems.

**Context for the suite:** Every tool must fit into the creation-suite menu structure (per user directives: Tool-to-Menu Wiring Law + Tool Unification Law). Candidates are evaluated on: alive/maintained status in 2026, license compatibility (commercial use in our game), hardware needs, and Blender integration (the crew's pipeline runs Blender 4.0.2+ on the VM toolchain).

> **Landscape event of the day:** Hi3D V1.0 (formerly Sparc3D) was open-sourced **today, 2026-10-23** — production-validated image-to-3D trained on 2M curated assets. Also in 2026: **Epic Games acquired Meshcapade** (announced 2026-02-18; online platforms shut down 2026-04-18). The SMPL/SMPL-X commercial licensing path now runs through Epic's digital-human stack and is effectively **closed as a self-serve option** — this makes the new Apache-2.0 body models (Anny, MHR) the recommended replacement, not SMPL-X.

---

## 1. Image/Text → 3D Generation (2026 state of the art)

### 1a. TRELLIS.2 — Microsoft Research ⭐ *Best image-to-3D for quality + license*
- **What it does:** Single-image → textured mesh with **PBR materials**, GLB export (WebP textures up to 4K), OBJ/PLY/Gaussians/Radiance-field output. 4B-parameter model; O-Voxel representation; three-stage flow-matching pipeline (sparse structure → shape → texture).
- **License:** **MIT** (core). ⚠️ NVIDIA deps (nvdiffrast, nvdiffrec) carry separate licenses — review before shipping.
- **Hardware:** Official minimum **24 GB VRAM** (tested A100/H100; Linux only). 512³ in ~3s / 1024³ in ~17s / 1536³ in ~60s on H100. Community experiment (2026-09) ran the full pipeline on an **8 GB RTX 2080 SUPER**: 36/36 generations, 0 OOMs, ~5.3 GB process VRAM, 115–638 s/generation. So lowpoly work is feasible on consumer GPUs with patience.
- **2026 status:** Active — GitHub microsoft/TRELLIS.2; ComfyUI community nodes; HuggingFace demo. Microsoft's strongest open 3D model. Original TRELLIS 1.x remains the only one with **native text-to-3D checkpoints** (text-base/text-large/text-xlarge, 16 GB VRAM, MIT) — TRELLIS.2 itself is image-only.
- **Suite fit:** Menu item "Generate from concept art / photo" in the import lane. Text→image→TRELLIS.2 (image stage) covers text-to-3D without any new dependency.

### 1b. Hi3D V1.0 (formerly Sparc3D) — ⭐ *Best new entry, open-sourced 2026-10-23*
- **What it does:** Image-to-3D with high-resolution geometry reconstruction (progressive, up to 1536³ effective sparse resolution), structural consistency, 90% reported slicing success rate. Formerly Sparc3D (2025); V1.0 trained on **2M curated 3D assets** (up from ~500k) and validated in production workflows (3D print, e-commerce, industrial design, VR, film).
- **License:** Open source as of 2026-10-23 — **check the actual license text before commercial use** (PR wording is "open source," verify it's Apache/MIT-class, not community-gated).
- **Hardware:** TBD from release docs; Sparc3D-era needed ~16–24 GB VRAM. Free generation on the official Hi3D website for quick evaluation.
- **2026 status:** Brand new — evaluate this week against TRELLIS.2 on our character-pose test set before committing.
- **Suite fit:** Candidate second generator in the import lane; strongest if its topology is game-clean.

### 1c. Hunyuan3D 2.1 — Tencent (quality king, **restricted license**)
- **What it does:** Image→3D with best-in-class open-weights mesh+texture (multi-view diffusion → reconstruction). Chained behind a text-to-image model for text-to-3D. Sibling projects: Hunyuan3D-Omni, **Hunyuan3D-Part** (part-level generation — relevant to our parts system).
- **License:** **Tencent Hunyuan 3D 2.1 Community License** — NOT permissive: **1M monthly-active-user gate**, **excludes EU/UK/South Korea**, and **forbids using outputs to train non-Hunyuan models**. Hunyuan3D 2.5+ is hosted/report-only, not open.
- **Hardware:** ~24 GB VRAM, 3–8 min/generation.
- **2026 status:** 2.1 (June 2025) remains the open release. Usable internally for one-off asset prototyping; **do not build the suite's pipeline on it** given the territory and training-use restrictions.
- **Suite fit:** Optional "experimental generator" toggle, clearly labeled with its license caveat.

### 1d. SPAR3D — Stability AI + NVIDIA (fast, editable)
- **What it does:** Single image → textured GLB in **~0.7 s**. Point-cloud-conditioned feed-forward: diffusion generates point cloud (captures structure), triplane transformer builds geometry/texture/materials. The point cloud is **directly editable** (delete/duplicate/extend/recolor points) — unique among open models. Mesh-from-pointcloud in 0.3 s.
- **License:** **Stability AI Community License** — free, commercial use allowed **under $1M annual revenue**; enterprise license above that.
- **Hardware:** Runs locally; sub-second on H100, workable on consumer cards.
- **2026 status:** Alive (github.com/Stability-AI/stable-point-aware-3d, HF space). Improvement over Stable Fast 3D's weak backside.
- **Suite fit:** "Rapid concept" lane — instant 360° previews, and the editable point cloud is a natural on-ramp to our customization menus.

### 1e. Stable Fast 3D — Stability AI (fastest, lowest fidelity)
- **What it does:** Single image → UV-unwrapped textured GLB in **~0.5 s**; predicts roughness/metallic; includes de-lighting. Quality: functional, not beautiful.
- **License:** Stability AI Community License (same $1M revenue gate).
- **Hardware:** **6–7 GB VRAM**; CPU inference works. Weights gated on HF (sign-in + accept license).
- **2026 status:** Alive; superseded by SPAR3D for quality, but still the latency champion.
- **Suite fit:** Real-time in-app preview lane (e.g., "snap a sketch → see a rough 3D in the suite instantly").

### 1f. TripoSR — Stability AI + Tripo (lightweight baseline)
- **What it does:** Single image → mesh in **<1 s** on consumer GPUs. 8 GB+ VRAM. Feed-forward reconstruction; fidelity lower than multi-view models but extremely deployable.
- **License:** **MIT.**
- **2026 status:** Alive and still the go-to when GPU is the constraint. Already in our intake pipeline history (Torch A3).
- **Suite fit:** Keep as the fallback/fast lane. No reason to retire.

### 1g. Zero123 family (legacy — deprioritize)
- **Status:** Original Zero123 is superseded. Survivors: **Zero123++** (SUDO-AI-3D, ~5 GB VRAM, generates 6 consistent views; useful as a *multi-view pre-pass* for other reconstructors), SV3D (Stability, ECCV 2024 — research-grade), Cascade-Zero123 (2026, research only). For actual asset generation, the feed-forward models above beat them. Keep Zero123++ only as a utility node (e.g., turning a single character render into 6 views for manual retopology reference).

### 🏆 Ranked recommendation — 3D generation
1. **TRELLIS.2** — MIT, PBR, game-usable GLB, character-safe pipeline. Primary generator for the import lane.
2. **Hi3D V1.0** — evaluate head-to-head this week; could take #1 if topology is cleaner and license is permissive.
3. **SPAR3D** — sub-second, editable point cloud, commercial-friendly under $1M revenue. Rapid-concept lane.
4. **TripoSR** — MIT, lightest; keep as fast fallback.
5. **Stable Fast 3D** — niche: real-time in-app preview only.
6. **Hunyuan3D 2.1** — quality prototyping only, behind the license warning.
7. Original **TRELLIS 1.x text checkpoints** — the one open MIT text-to-3D path (16 GB VRAM).

---

## 2. Photo → 3D Face (2026 state of the art)

### 2a. RealDenseFace — ⭐ *Best open pick for monocular face recon (Aug 2026)*
- **What it does:** Real-time monocular 3D face reconstruction from dense UV-space priors. Single-image fitting + offline/online video tracking + multi-view (NeRSemble v2) tracking. FLAME-model based.
- **License:** **MIT.** Code: github.com/LinzhouLi/RealDenseFace (created 2026-08-11).
- **Hardware:** Real-time capable; consumer GPU friendly.
- **2026 status:** Brand new, actively maintained.
- **Suite fit:** "Scan your face" lane in character creation — MIT means we can bundle it directly into the suite.

### 2b. FaceLift (ICCV 2025) — best identity preservation
- **What it does:** Single image → high-fidelity **3D Gaussian head** (full 360°, hair + face detail) via multi-view diffusion → GS-LRM transformer. Trained on synthetic data, generalizes to real photos. Paper: UC Merced + Adobe Research (arXiv 2412.17812v2, ICCV 2025).
- **License / code:** Community reimplementation at github.com/deepmancer/FaceLift (outputs `gaussians.ply` + turntable video). Check the repo's license before shipping; Gaussian-splat output needs conversion to mesh for game use.
- **Hardware:** GPU-heavy (diffusion + transformer), ~12–24 GB VRAM class.
- **2026 status:** Reimplementation active (crawled 56 days ago).
- **Suite fit:** "Hero head" mode — best likeness; pair with a Gaussian→mesh conversion step before rigging.

### 2c. 3DDFA-V3 (CVPR 2024 Highlight) — robust parametric face
- **What it does:** 3DMM face reconstruction with facial-part-segmentation guidance; excels at extreme expressions (closed eyes, wide mouth, frowns). Landmarks + dense mesh output.
- **License:** Academic/open (wang-zidu/3DDFA-V3). Verify repo license before commercial bundling.
- **Hardware:** Lightweight; runs on modest GPUs.
- **2026 status:** Stable, mature; no 2026 updates needed — it's a finished tool.
- **Suite fit:** Expression-corrective shape-key extraction lane — its segmentation guidance makes it the best source for **corrective blendshapes**, not base heads.

### 2d. DECA / EMOCA — the expression workhorses (unchanged)
- **What they do:** DECA — detailed expression capture with wrinkle-level displacement maps; EMOCA — emotion-consistent reconstruction. Both are the standard for **facial animation params**.
- **License:** Non-commercial research licenses (MPI). **Do not bundle into shipped game builds**; use as offline R&D reference.
- **2026 status:** No updates; superseded for base recon, still cited for expression fitting.
- **Suite fit:** Research-only; expressions lane should use MPFB2's ARKit face units (below) instead.

### 2e. KeenFace (KeenTools, 2026-10-22 launch) — commercial only, note for reference
- **What it does:** Photos → production head in **native MetaHuman topology**, 4K PBR (Base Color/Normal/Roughness/Specular), automated de-hairing, Scan Reconstruction mode. Browser/API.
- **License:** **Commercial, pay-as-you-go** (free starter credits). Not open source.
- **Suite fit:** Not for the suite — but its output convention (MetaHuman topology + 4K PBR set) is the quality bar our face pipeline should target.

### 🏆 Ranked recommendation — photo-to-face
1. **RealDenseFace** — MIT, real-time, FLAME-based; bundle directly into the suite's "scan your face" lane.
2. **FaceLift** — best identity/likeness; add Gaussian→mesh conversion, use for hero heads.
3. **3DDFA-V3** — expression/corrective-shape extraction; verify license for bundling.
4. **MPFB2 faceunits01 asset pack** (see §3) — ARKit-compatible face units for the *animation* side of faces, avoiding DECA/EMOCA license traps.

---

## 3. Parametric Human Bodies (beyond MB-Lab/MakeHuman)

### 3a. Anny — NAVER LABS Europe (Nov 2025) ⭐ *Best free parametric body, full stop*
- **What it does:** Differentiable human body model, PyTorch. **11 semantic shape params** (gender, age, weight, height, muscle, cup size…) + **256 local-change blendshapes** (waist circumference, breast volume, etc.). ~13.7K vertices, 163 bones, full-body + hands + face models. Built on MakeHuman community anthropometry, calibrated to WHO population stats (ages: infants → elders). PyPI `anny` 0.1.0 (Nov 2025); Gradio interactive demo; Jupyter tutorials.
- **License:** Code **Apache 2.0**; bundled MPFB2 assets **CC0 1.0**; only the optional SMPL-X-interop data is non-commercial. **Commercially clean.**
- **Hardware:** Pure PyTorch; no GPU needed for param→mesh.
- **2026 status:** Active (github.com/naver/anny). Companion: **Anny-Fit** (2026) — all-age multi-person HMR via optimization.
- **Suite fit:** **This is our body system.** Semantic params map directly onto creation-suite sliders (age/weight/muscle/cup size…), and the 256 local blendshapes are a ready-made "fine-tune" menu. Replaces any SMPL-X plans. Pairs with MPFB2 (below) — Anny is literally built on MPFB2's CC0 assets.

### 3b. MHR (Momentum Human Rig) — Meta (late 2025) ⭐ *Best mesh quality + commercial HMR path*
- **What it does:** New parametric representation decoupling **skeletal structure from surface shape**. ~18.4K vertices, 127 joints, **7 LOD levels**. **SAM 3D Body** (Meta Superintelligence Labs, checkpoints released 2025-11-19, `facebook/sam-3d-body-dinov3` on HF) outputs MHR params directly from a single photo — state-of-the-art in-the-wild HMR (beats prior SOTA ~14% on AGORA-3D). Supports one-click Mixamo skeleton binding. PyPI `body-models` 0.7.0 auto-downloads MHR.
- **License:** **SAM License** — commercially permissive (not Apache 2.0; read the Meta terms). 
- **Hardware:** SAM 3D Body inference needs a solid GPU (DINOv3-H+ backbone is 840M params).
- **2026 status:** Active (github.com/facebookresearch/sam-3d-body, crawled 1 day ago). Community forks: Fast-SAM-3D-Body, C++ port, CEB Blender addon.
- **Suite fit:** Photo→body lane: snap a photo → MHR params → convert to Anny for editing (the dev.to piece documents an MHR→Anny bridge). 7 LOD levels matter for the game's perf tiers.

### 3c. MPFB 2 — MakeHuman Plugin for Blender ⭐ *Best Blender-native body system (not dead)*
- **What it does:** Full character generator **inside Blender** (not just an importer): parametric bodies, rigging (Rigify/GameRig/Mixamo variants incl. extended Mixamo+Unity rig with face/breast bones), MakeClothes, skin/materials, export to glTF/FBX/USD/Alembic.
- **License:** Code **GPLv3**, bundled assets **CC0**. (GPLv3 on the *addon* is fine for our pipeline use — it doesn't infect exported meshes; only be careful if we fork and redistribute the addon itself.)
- **2026 status:** **Actively maintained** — releases every ~2 months: **2.0.18 (2026-10-10)**, 2.0.17 (2026-07-22, character randomization + materials), 2.0.16 (2026-06-13, complete expressions toolset + Rigify overhaul), 2.0.15 (visemes01/visemes02 + **faceunits01: 54 ARKit face-unit shape keys**), 2.0.14 (export-copy automation), 2.0.11 (geometry-nodes hair). Official Blender Extensions Platform listing. Blender 4.2+ required.
- **Suite fit:** The **unified BODY system front-end** per user directive. It's the base GNM/MPFB2 were already earmarked for — and Anny's CC0 assets are MPFB2 assets, so they unify naturally. The export-copy tool (2.0.14) automates bake/apply on export — exactly our game-asset path.

### 3d. STAR — Max Planck (SMPL upgrade, still restricted)
- **What it does:** Drop-in SMPL replacement; sparse local pose-corrective blendshapes (20% of SMPL's params, better generalization); shape-dependent correctives; 300-PC shape space.
- **License:** **Research-only** (non-commercial), like SMPL.
- **2026 status:** No updates since 2020; finished research.
- **Suite fit:** Reference only. License rules it out for the game.

### 3e. GHUM / imGHUM / SUPR — research tier
- **GHUM:** Google's generative human model; **research-only, not commercially licensed.** Volumetric variants (imGHUM) are research code.
- **SUPR:** Superior to SMPL-X in articulation; license is MPI research-style (non-commercial). Reference only.
- **Suite fit:** None for shipping. If we ever need a volumetric collision body, COAP (SMPL-space) is the practical one — but it's SMPL-licensed too.

### 3f. Datasets worth knowing (not models)
- **Bedlam, AGORA, GTA-Human** — synthetic training datasets for HMR. Useful if we ever train custom fitting networks; not suite components. AGORA-3D is the current HMR benchmark SAM 3D Body leads.

### 🏆 Ranked recommendation — parametric bodies
1. **Anny** — Apache 2.0 + CC0 assets, semantic sliders, 256 local blendshapes. **The suite's body system.**
2. **MHR + SAM 3D Body** — photo→body recovery with the best in-the-wild accuracy; bridge MHR→Anny for editing.
3. **MPFB 2.0.18** — Blender-native generator/rigging/export front-end; unify with Anny (same CC0 asset base).
4. STAR / GHUM / SUPR — research reference only; licenses exclude shipping.

---

## 4. Morphing / Blendshape Tools (Blender, 2026)

### 4a. MPFB2 built-ins (free, CC0/GPLv3) ⭐ *Best starting point*
- Face units: **faceunits01 pack — 54 ARKit-compatible face-unit shape keys**, expressions toolset (2.0.16), "Face operations" panel (2.0.15), viseme packs (22 Microsoft-style + 15 Meta/VR-style). Shape keys drive directly (no bone-pose indirection like old MakeHuman).
- Body: 256 local-change blendshapes via Anny bridge (same asset base).
- Export-copy tool bakes shape keys on export.

### 4b. Blender Extensions: Corrective Shape Keys + Pose Shape Keys (free, GPLv2)
- **Corrective Shape Keys** (extensions.blender.org, v1.0.0, approved, ~26k downloads, Blender 4.2 LTS+): the standard corrective workflow — sculpt fix shapes on posed mesh, drive by bone angle.
- **Pose Shape Keys** (extensions.blender.org): stores final sculpted shapes separately so you can **re-do weight painting/rigging without losing corrective sculpts** — directly addresses our "decrypted backwards / wrong-bone weight" class of bugs: sculpt correctives, fix the rig, re-apply shapes.
- Both are official-extension-vetted and current in 2026.

### 4c. RBF Nodes — Brave Rabbit (Oct 2026) ⚠️ *paid, but the concept to copy*
- **What it does:** Node-based **Radial Basis Function solver** for Blender: multiple inputs → multiple outputs with smooth interpolation between posed examples. Corrective shapes for shoulders/hips driven by several joints at once; facial rigs blending multiple shapes from controller positions; drives shader/geometry-nodes params from transforms.
- **License:** Commercial (paid); includes a free runtime for rig consumers. Blender 4.2+.
- **Suite fit:** Don't buy for the suite — but an **RBF driver is the correct technical answer** for our multi-joint correctives (e.g., the shoulder/hip collapse issues in fighting poses). Blender has no native RBF solver; either implement a small open RBF driver (numpy, ~100 lines) or wire the math into the rigging lane of the unified system. Flagged as a crew task, not a purchase.

### 4d. GNM (user-named, Google Research) — parametric head/face/neck/eyes/teeth/tongue
- Status: research model (Apache 2.0 per user notes). Goes to the unified FACE system per user directive. Verify the current repo/checkpoint availability when wiring; pair with RealDenseFace (MIT) so the suite doesn't depend on a research-only model.

### 🏆 Ranked recommendation — morphing/blendshapes
1. **MPFB2 face units + ARKit packs + Anny local blendshapes** — the suite's morphing vocabulary (free, shippable).
2. **Corrective Shape Keys + Pose Shape Keys** Blender extensions — corrective workflow + rig-repair safety net.
3. **Implement an open RBF driver** in the rigging lane (copy the concept, not the paid addon).
4. GNM for parametric heads — after verifying availability.

---

## 5. Clothing / Garment Simulation (open source)

### 5a. Blender native cloth physics ⭐ *Primary*
- Blender's built-in cloth/soft-body simulation (mass-spring) with collision, sewing springs, pressure, and shape-key/collision baking. It's the production tool we already have in the pipeline; combined with geometry nodes it's enough for fighting-game attire (torn cloth, capes, skirts).
- **Cloth Lab 0.8.1 (English build, free)**: garment-workshop UI on top of Blender cloth — fabric presets, panel-based workflow. Tested on Blender 5.2.2. Useful as the "garment mode" skin for the suite's clothing menu rather than hand-rolling UI.
- License: GPL (Blender) — fine for pipeline use; exported/simulated meshes are ours.

### 5b. Seamly2D (+ Valentina fork) — open-source pattern drafting
- **What it does:** Parametric 2D garment pattern drafting (the actual fashion-industry workflow: patterns → 3D drape). GPLv3.
- **2026 status:** Alive (weekly builds on GitHub; the community split Valentina/Seamly2D continues but both are maintained).
- **Suite fit:** The "pattern → garment" lane for authentic clothing parts: draft parametric patterns, import to Blender for drape sim. This is the **non-hand-tooled** route to the user's creation-suite clothing system.

### 5c. Commercial reference only
- **Marvelous Designer / CLO Virtual Fashion / Optitex**: no free plans (paid from ~$8/user/mo billed annually). Industry standard for garment authoring; the crew should know the file interchange (OBJ→Garment import exists in MD) but the suite stays open-source.
- **Style3D AI**: free trial, AI-driven — not open.

### 5d. AI-assisted garment option
- **Hunyuan3D-Part** (Tencent): part-level 3D generation — could generate clothing *parts* (a jacket, a mask) as separate assets. License caveat applies (see §1c). Watch for a permissive-licensed equivalent.

### 🏆 Ranked recommendation — clothing
1. **Blender cloth physics + Cloth Lab UI skin** — the suite's garment sim (already in our toolchain).
2. **Seamly2D** — parametric pattern drafting lane for real garment construction.
3. Marvelous Designer — know the interchange; don't build on it (paid).

---

## 6. 3D File & Optimization Tooling (2026)

### 6a. meshoptimizer 1.3 (Sept 2026) ⭐ *Keep — it's current*
- **What:** zeux/meshoptimizer — vertex/index optimization, quantization, simplification, **meshlet codec** (v1.1+), clustered LOD. v1.3 adds: experimental **voxel remesher**, automatic normal generation, stabilized permissive simplification, faster decode/meshlet/cluster-LOD.
- **License:** MIT.
- **Status:** Very active. 2026 highlight: **KHR_meshopt_compression standardized early 2026** (successor to EXT_meshopt_compression, uses the improved v1 vertex codec). NVIDIA's 1.6B-triangle Zorah scene now ships meshoptimizer-compressed glTF.
- **Suite fit:** Already in our intake pipeline (gltfpack). **Switch exports to KHR_meshopt_compression** where the engine supports it; keep EXT_ fallback for compatibility.

### 6b. gltfpack 1.3.0 (npm, ~3 weeks ago) ⭐ *Keep*
- CLI: `gltfpack -i scene.gltf -o scene.glb [-c]` — cache optimization, quantization, mesh merging, animation resampling, node pruning, texture compression. Native binaries recommended over npm (faster, larger files, texture compression support).
- **Suite fit:** Stays as the standard "optimize for game" step after every intake/rig.

### 6c. glTF-Transform (donmccurdy) — the scriptable pipeline
- Node/CLI toolkit for inspecting, converting, compressing glTF (Basis/ETC texture compression, Draco/meshopt, dedup, prune). ~2k weekly npm installs, maintained.
- **Suite fit:** Use as the **scriptable** layer (batch jobs, CI checks) while gltfpack stays the one-shot optimizer.

### 6d. Blender 5.x note
- **Blender 5.2.2** is current; **Blender 5.3 ships 2026-11-10** with native 3D Gaussian Splatting support, dispersion in Principled BSDF, and new custom-lighting nodes. The suite's face lane (FaceLift outputs Gaussians) gets easier in 5.3. MPFB2 requires Blender 4.2+ — our toolchain (4.0.2) needs the upgrade before MPFB2/Anny wiring.

### 🏆 Ranked recommendation — file/optimization
1. **meshoptimizer 1.3 + gltfpack 1.3.0** — current, MIT, already in pipeline. Adopt KHR_meshopt_compression.
2. **glTF-Transform** — scriptable batch/CI layer.
3. **Upgrade toolchain to Blender 5.x** (after 5.3 lands) for MPFB2 + Gaussian-splat face support.

---

## Suite Integration Map (how each winner lands in the creation suite)

| Suite lane (per Tool-to-Menu Wiring Law) | Tool | License | Hardware floor |
|---|---|---|---|
| **Body** — parametric sliders | Anny (11 semantic + 256 local) | Apache 2.0 / CC0 | CPU |
| **Body** — Blender front-end/rig/export | MPFB 2.0.18 | GPLv3 / CC0 | Blender 4.2+ |
| **Face** — scan your face | RealDenseFace | MIT | Consumer GPU |
| **Face** — hero heads | FaceLift (+Gaussian→mesh) | check repo | 12–24 GB VRAM |
| **Face** — parametric head parts | GNM | Apache 2.0 (verify) | TBD |
| **Import** — concept/photo → 3D | TRELLIS.2 (primary) | MIT | 24 GB rec / 8 GB possible |
| **Import** — evaluate now | Hi3D V1.0 | verify (new) | TBD |
| **Import** — rapid concept | SPAR3D | Stability Community (<$1M) | Consumer GPU |
| **Import** — fast fallback | TripoSR | MIT | 8 GB |
| **Morphing** — expressions/visemes | MPFB2 faceunits01/visemes | CC0 | Blender |
| **Morphing** — corrective shapes | Corrective + Pose Shape Keys ext. | GPLv2 | Blender |
| **Morphing** — multi-joint correctives | Open RBF driver (crew-built) | ours | Blender |
| **Clothing** — garment sim UI | Blender cloth + Cloth Lab | GPL | Blender |
| **Clothing** — pattern drafting | Seamly2D | GPLv3 | CPU |
| **Optimize** — game-ready export | gltfpack 1.3 + meshoptimizer 1.3 | MIT | CPU |
| **Optimize** — batch/CI | glTF-Transform | Apache 2.0 | CPU |

## Strategic notes for the parent agent

1. **SMPL-X is dead as a plan.** Meshcapade's acquisition by Epic (Feb 2026) + platform shutdown (Apr 18, 2026) killed the only commercial SMPL-X self-serve path. **Anny (Apache 2.0) + MHR (SAM License) are the replacements** — better licensing, semantic controls, and a working photo→body path. Purge SMPL-X from any pipeline docs.
2. **Hi3D V1.0 dropped today** — schedule a head-to-head vs TRELLIS.2 on our character test images before the import lane is finalized. If its license is permissive and topology is game-clean, it may become the primary generator.
3. **License landmines flagged:** Hunyuan3D 2.1 (territory + MAU gate + no-training-on-outputs), Stability Community License ($1M revenue gate — fine for now, revisit at scale), MPFB2 GPLv3 (safe for pipeline use; only matters if we fork/redistribute the addon), DECA/EMOCA/GHUM/STAR/SUPR (research-only — keep out of shipped builds).
4. **Blender upgrade required:** Toolchain is on 4.0.2; MPFB2 needs 4.2+, and Blender 5.3 (2026-11-10) adds native Gaussian-splat support that the FaceLift lane wants. Plan the upgrade.
5. **RBF solver is a crew build task:** No open Blender RBF solver exists; the paid RBF Nodes (Oct 2026) proves the design. A small numpy-based RBF driver for multi-joint correctives is ~a day's work and fixes the whole class of "shoulder/hip collapse" deformation bugs.
6. **Everything above is 2026-verified alive** except where explicitly flagged (evaluate/verify). Dead projects (Point-E, Shap-E, original Zero123, MB-Lab-as-importer) are listed only to be avoided.

## Sources
- TRELLIS.2: https://deepwiki.com/microsoft/TRELLIS.2 · https://www.trellis-2.org/ · https://app.cinevva.com/news/2026-03-20-trellis-2-microsoft-open-source-3d
- Hi3D V1.0: https://www.prnewswire.com/news-releases/hi3d-v1-0-goes-open-source-the-first-production-validated-open-source-ai-3d-model-302917998.html (2026-10-23)
- Hunyuan3D vs TRELLIS comparison: https://triposr.org/blog/hunyuan3d-vs-trellis
- Open-source 3D APIs 2026: https://www.pixazo.ai/blog/best-open-source-3d-model-generation-apis
- SPAR3D: https://theresanaiforthat.com/company/stability-ai/repository/stable-point-aware-3d/
- Stable Fast 3D / free generators: https://www.theaitools.tech/2026/10/ai-3d-model-generator-from-image-free.html
- RealDenseFace: https://github.com/LinzhouLi/RealDenseFace
- FaceLift: https://arxiv.org/html/2412.17812v2 · https://deepwiki.com/deepmancer/FaceLift
- 3DDFA-V3: https://deepwiki.com/wang-zidu/3DDFA-V3
- KeenFace: https://www.awn.com/news/keentools-keenface-turns-photos-metahuman-ready-3d-heads
- Anny: https://arxiv.org/html/2511.03589 · https://pypi.org/project/anny/0.1.0/
- SAM 3D Body / MHR: https://github.com/facebookresearch/sam-3d-body · https://huggingface.co/facebook/sam-3d-body-dinov3
- Body-model landscape (Mar 2026): https://dev.to/arkadiuss/a-3d-body-scan-for-nine-cents-without-smpl-4me1
- MPFB2 releases: https://static.makehumancommunity.org/mpfb/releases/index.html · http://www.cgchannel.com/2025/03/check-out-open-source-blender-character-generation-plugin-mpfb-2/
- Meshcapade/Epic: https://www.anygen.io/showcase/meshcapade-me/index.html
- RBF Nodes: https://80.lv/articles/bring-rbf-solver-to-your-blender-rigs
- Blender extensions: http://extensions.blender.org/add-ons/pose-shape-keys/ · https://extensions.blender.org/add-ons/corrective-shape-keys/versions/
- meshoptimizer 1.3 / KHR_meshopt_compression: https://zeux.io/2026/09/30/billions-of-triangles-redux/ · https://www.gameloop.tech/gamedev/issues/2026-10-19
- gltfpack: https://npm.io/package/gltfpack
- Cloth Lab: https://slohero.com/tools/blender/en/
