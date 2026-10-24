# Anatomy-Combat Integration: Open-Source Pull Research (2026-10-23)

Owner directive: "any other open source stuff we can find do more research on stuff like that that you can find and pull in and wire up"

**Goal:** Wire Purdue's Dissectible Anatomy tech into combat — X-ray attacks (Tekken-styled),
fatality-style finishers (Tekken-styled), organ layers, soft-body physics, layered anatomy.

**Foundation already merged:** Jolt soft-body physics (PR #846), layered anatomy BONE/MUSCLE/FAT/SKIN
(PR #860), research docs (PR #839 — DISSECTIBLE-ANATOMY, ANATOMY-LAYERS-SPEC, PBD-SOFTBODY-OPTIONS).

**This sweep:** NEW projects not yet in the repo research, prioritized MIT/Apache 2.0 (pullable).
GPL/LGPL and CC Share-Alike flagged **study-only — do not pull code**.

---

## TIER 0 — TOP PULLS (permissive license, directly usable)

### 1. iMSTK — Interactive Medical Simulation Toolkit
- **What:** C++ real-time surgical simulation toolkit: **extended position-based dynamics (XPBD)**
  soft-tissue deformation, continuous collision detection, SPH fluids, tetrahedral FEM,
  cutting/tearing, level-set collision — exactly the stack a fatality/X-ray combat system needs.
- **License:** **Apache 2.0** — fully pullable. (Note: docs site carried a "sunset notice" as of
  early 2026; code remains open and licensed; verify activity before depending on upstream.)
- **Game use:** soft-tissue impact deformation, cut/tear logic for finishers, XPBD tissue sim
  reusable alongside our Jolt XPBD (PR #846).
- **Pull:** `git clone https://gitlab.kitware.com/iMSTK/iMSTK.git`
- **Take:** `Source/DynamicalModels/` (XPBD deformable bodies), `Source/Collision/` (CCD),
  `Source/Geometry/Mesh/` (cut/tear), the Unity/Unreal bridge examples if we want an editor preview.
- **Ref:** https://gitlab.kitware.com/iMSTK/iMSTK — paper: doi 10.3389/frvir.2023.1130156.

### 2. OpenSim — Musculoskeletal Simulation
- **What:** Stanford's musculoskeletal modeling/simulation engine: rigid-body segments + joints,
  Hill-type muscle actuators, tendon routing, forward/inverse dynamics, muscle force estimation
  (via Simbody underneath).
- **License:** **Apache 2.0** — fully pullable.
- **Game use:** muscle-activation/force numbers for damage modeling (which muscle is hit, how much
  force it takes), ragdoll-adjacent musculoskeletal layer under the skeleton, injury-state sims.
- **Pull:** `git clone https://github.com/opensim-org/opensim-core.git`
- **Take:** `OpenSim/Simulation/Model/Muscle/` (muscle force curves), the `.osim` gait2354/FullBody
  reference models as calibration data for our hit-reaction tuning.
- **Ref:** https://github.com/opensim-org/opensim-core (paper: PLoS Comput Biol, PMID 30048444).

### 3. MuJoCo — Multi-Joint dynamics with Contact
- **What:** Google DeepMind's fast rigid-body + soft-contact engine; closed-form tendon routing
  (~600x faster than OpenSim on forward sims), muscle actuators, soft contacts, deformables.
- **License:** **Apache 2.0** — fully pullable.
- **Game use:** real-time muscle-tendon driven hit reactions, soft-contact punch landing,
  a second soft-body reference beside Jolt.
- **Pull:** `git clone https://github.com/google-deepmind/mujoco.git`
- **Take:** `src/engine/` muscle/tendon code, `python/mujoco` for offline calibration of our
  impact-deformation parameters.
- **Ref:** https://github.com/google-deepmind/mujoco

### 4. FEBio — Finite Elements for Biomechanics
- **What:** Nonlinear finite element solver designed for biomechanics: large-deformation solid
  mechanics, **hyperelastic tissue materials**, active muscle contraction, contact, poroelasticity,
  nearly-incompressible element formulations.
- **License:** **MIT** (v2.9+; older versions were custom non-open — take 2.9 or newer) — pullable.
- **Game use:** OFFLINE bake: compute real tissue-deformation response curves (skin/fat/muscle
  under punch-like loads) → bake into our runtime Jolt soft-body parameters. Plugin framework
  lets us add custom "combat tissue" material models.
- **Pull:** `git clone https://github.com/febiosoftware/FEBio.git` (check out v2.9+ tag)
- **Take:** `FEBio/FEBioMech/` material library (hyperelastic models), `FEBio/FEBioLib/`
  plugin scaffolding.
- **Ref:** https://febio.org/ — Wikipedia: https://en.wikipedia.org/wiki/Febio

### 5. SPlisHSPlasH — SPH Fluid Library
- **What:** TU Munich SPH fluid simulation library (DFSPH/PBF solvers): fast, stable fluids.
- **License:** **MIT** — pullable.
- **Game use:** blood/viscera fluids for finishers, sweat/impact fluid effects. Particle-based,
  pairs with Jolt particles.
- **Pull:** `git clone https://github.com/InteractiveComputerGraphics/SPlisHSPlasH.git`
- **Take:** `Simulator/` (solvers), `SPlisHSPlasH/` (DFSPH core).

### 6. IPC — Incremental Potential Contact (ipc-sim)
- **What:** MIT lab contact solver: intersection-free, inversion-free frictional contact for
  deformables — the modern reference for "soft bodies never interpenetrate" (cited in Blender's
  2020 soft-body GSoC).
- **License:** **MIT** — pullable.
- **Game use:** guaranteeing fist never clips through skull/torso in X-ray shots; clean
  self-collision for layered anatomy.
- **Pull:** `git clone https://github.com/ipc-sim/IPC.git`
- **Take:** `src/ipc/` barrier/contact code (study first; integrate narrow-phase against Jolt).

### 7. HXPBD / Feather engine (Barthélemy Paléologue)
- **What:** Small self-contained XPBD + hierarchical-PBD soft-body demo engine with a working
  **tearing** prototype (discards violated distance constraints), spatial hash grid collision.
- **License:** **Public domain** — pullable, no restrictions.
- **Game use:** reference implementation for our own skin/muscle tearing (finisher wounds),
  and its documented HXPBD report is a clean spec to port against Jolt.
- **Pull:** `git clone https://github.com/BarthPaleologue/feather.git`
- **Take:** the soft-body solver + tearing code; report PDF at `HXPBD_report.pdf` in repo root.
- **Ref:** https://barthpaleologue.github.io/Blog/posts/hxpbd/

---

## TIER 1 — ANATOMY DATA & VISUALIZATION (layer peeling, X-ray)

### 8. 3D Slicer
- **What:** The reference open medical imaging platform: volume rendering, slice views, 4D
  rendering, segmentation, DICOM/CT/MRI pipeline, plugin architecture.
- **License:** **BSD-style** — pullable.
- **Game use:** study its volume-rendering + transfer-function pipeline for our X-ray shader
  design; slice/section plane tools inform the finisher "peel" camera. Don't ship Slicer;
  port the rendering concepts to WebGL/three.js.
- **Pull:** `git clone https://github.com/Slicer/Slicer.git`
- **Take:** `Modules/Loadable/VolumeRendering/` (transfer function design), `Libs/vtkSegmentationCore`.

### 9. VTK — Visualization Toolkit
- **What:** Industry-standard 3D visualization lib: volume rendering, GPU ray casting, clipping,
  isosurfaces.
- **License:** **BSD 3-Clause** — pullable.
- **Game use:** reference for our three.js X-ray layer renderer (ray-march transfer functions
  → port math to GLSL). Also powers 3D Slicer and MITK.
- **Pull:** `git clone https://gitlab.kitware.com/vtk/vtk.git`
- **Take:** `Rendering/Volume/` (GPU ray-cast mapper) as a GLSL porting spec.

### 10. MITK — Medical Imaging Interaction Toolkit
- **What:** ITK + VTK + app framework: interactive segmentation, multimodal (CT/MRI/PET) viewing,
  Workbench app with 2D/3D/4D views.
- **License:** **BSD 3-Clause** — pullable.
- **Game use:** segmentation tooling to auto-generate our BONE/MUSCLE/FAT/SKIN layers from
  scan-like data; plugin pattern for anatomy-layer modules.
- **Pull:** `git clone https://github.com/MITK/MITK.git`
- **Take:** segmentation plugin code, layer/opacity management in `Modules/`.

### 11. human-atlas / ha (BodyParts3D web viewers)
- **What:** Open-source browser anatomy explorers using BodyParts3D meshes: per-structure GPU
  textures for visibility/selection, exploded views, system layers, search — i.e. a working
  **layer-peeling + exploded anatomy UI** in the browser, exactly our character-select anatomy
  viewer shape.
- **License:** code — **verify in repo** (reported MIT); anatomy data is BodyParts3D CC BY-SA —
  study the CODE, treat the DATA as study-only (see §13).
- **Game use:** steal the rendering architecture (merged batches + per-structure GPU textures
  for visibility/translate/select), exploded-view packing algorithm.
- **Pull:** `git clone https://github.com/ashemag/human-atlas.git`
- **Take:** `scripts/convert-anatomy.py`, `scripts/optimize-anatomy.mjs`, `scripts/compress-models.mjs`,
  the per-structure texture visibility shader.

---

## TIER 2 — MORE ENGINES (verify then pull)

### 12. Simbody
- **What:** SimTK's high-accuracy multibody dynamics (what OpenSim is built on).
- **License:** **Apache 2.0** — pullable.
- **Game use:** reference-grade joint/contact dynamics for validating our hit reactions.
- **Pull:** `git clone https://github.com/simbody/simbody.git`

### 13. Project Chrono
- **What:** BSD multibody + FEA + SPH + granular dynamics; deformable terrain, co-simulation.
- **License:** **BSD** — pullable.
- **Game use:** arena-floor deformation (mud/sand ring dents), granular debris on impacts.
- **Pull:** `git clone https://github.com/projectchrono/chrono.git`

### 14. SurRoL soft-body branch (MPM + Taichi)
- **What:** Taichi-language Material Point Method soft-tissue sim (Neo-Hookean) added to the
  SurRoL surgical-robot platform — GPU-parallel, plausible visuals.
- **License:** **verify** (SurRoL base reported open; confirm before pulling).
- **Game use:** MPM reference for organ-squish on heavy impacts; Taichi kernels as a GPU
  soft-body sketch for future work.

### 15. ArtiSynth
- **What:** Interactive biomechanical toolkit combining multibody + FEM (tet/hex elements,
  co-rotated linear, hyperelastic, viscoelastic materials), point-to-point Hill muscles,
  contact/friction, inverse muscle-activation solving. Demo models include FEM face/tongue/jaw,
  head-neck impact models.
- **License:** **verify in repo** (open-source release; confirm license file before pulling code).
- **Game use:** FEM face model = reference for facial impact deformation; muscle-activation
  inverse sims for hit-reaction authoring.

---

## STUDY-ONLY — DO NOT PULL CODE (copyleft / share-alike)

### 16. SOFA — Simulation Open Framework Architecture
- **License: LGPL** → **study-only, do not pull code into the repo.**
- Study: its soft-tissue scene-graph architecture and mapping concepts inform our Jolt/iMSTK
  integration design. Read docs, don't copy.

### 17. BodyParts3D / Anatomography
- **License: CC BY-SA 2.1 Japan** → **study-only.** Share-Alike would infect our game assets.
- Study: 2,200+ named anatomical meshes = the reference for our organ-layer naming and
  hierarchy (FMA terms). Never commit the meshes.

### 18. Z-Anatomy
- **License: CC lineage (BodyParts3D-derived)** → **study-only.**
- Study: its Blender layer-toggle / cross-section-plane / hierarchical labeling UI design
  for our anatomy viewer menus; Unity hierarchy import notes for mobile viewer architecture.
  Do not copy the mesh data.

---

## WIRE-UP PLAN (suggested order for the crew)

1. **iMSTK XPBD tissue module → Jolt soft-body layer (PR #846):** port cutting/tearing +
   level-set collision into our soft-body bodies; finishers use tear constraints.
2. **FEBio (offline) → bake tissue response curves → Jolt parameters:** punch-load sims on
   skin/fat/muscle produce stiffness/damping tables; runtime stays real-time.
3. **OpenSim/MuJoCo muscle models → damage system:** muscle force/length curves drive the
   anatomy-layer damage states (bruised/torn/severed per muscle).
4. **VTK/3D Slicer volume-render math → three.js X-ray GLSL:** ray-march transfer functions
   for BONE/MUSCLE/FAT/SKIN layers (PR #860) during X-ray attacks.
5. **human-atlas rendering architecture → anatomy viewer:** merged batches + per-structure
   GPU textures for layer visibility/exploded views in character select.
6. **SPlisHSPlasH → finisher fluids:** blood/viscera SPH on fatality finishers.
7. **IPC → contact guarantee:** narrow-phase against Jolt so X-ray shots never interpenetrate.
8. **Chrono → arena deformation:** ring-floor dents/debris.

## GAPS / RISKS
- iMSTK docs site shows a sunset notice — verify the GitLab repo is still maintained before
  deep integration; Apache 2.0 code is safe regardless.
- FEBio: only v2.9+ is MIT; pin the tag in the pull, don't take older checkouts.
- SurRoL/ArtiSynth/human-atlas licenses must be verified in-repo before any code lands in ours.
- BodyParts3D/Z-Anatomy/SOFA: ideas only, never code or meshes.
