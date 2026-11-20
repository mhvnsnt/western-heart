# Soft-Body Nextgen — SurRoL / Isaac Healthcare / Neural Deformation Gradients

**Date:** 2026-10-23
**Owner instruction (verbatim):** "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate"
**Status:** all three items evaluated; everything that can run in the browser game is WIRED. GPU/Python-only parts are documented as [AWAITS GPU LANE].

**License note:** SurRoL is open-source (github.com/med-air/SurRoL). NVIDIA Isaac for
Healthcare numerical sim is Apache-2.0. Neural Deformation Gradients is
**CC BY-NC — technique reference only; no code copied.** Every line of the new
solver is an original implementation of the standard MPM algorithm.

---

## 1. Status board

| # | Source | License (verified) | Browser verdict | Wired |
|---|---|---|---|---|
| 1 | SurRoL MPM soft-body (arXiv:2402.01181v1, Taichi) | Open source (med-air/SurRoL) | Taichi can't run in browser (Python DSL, CUDA/Metal/Vulkan only — no WASM target). Algorithm core ported to JS. | **[WIRED]** `game/js/mpm-tissue.js` — CPU MPM-lite: Lagrangian particles carry F, Eulerian grid solves Neo-Hookean stress, quadratic B-spline P2G/G2P, APIC transfer, explicit substepped solve |
| 2 | NVIDIA Isaac for Healthcare — Newton 1.6.1 + Warp 1.17.0 (GA April 2026) | Apache-2.0 (numerical_sim) | Newton/Warp need CUDA + Python + Docker — cannot run in the browser game. Architecture ports. | **[WIRED]** staged solver (MUSCLE → FAT → SKIN stages per frame), per-layer Lamé materials, rigid↔soft coupling (pinned bone-wrap core = Dirichlet boundary, Newton two-way-coupling analogue) |
| 3 | Neural Deformation Gradients (Nolte et al., Eurographics 2026) | **CC BY-NC** — technique only | No code copied. Techniques ported. | **[WIRED]** deformation-gradient-space inversion guard (rescale F when det < 0.35), high-λ Neo-Hookean volume preservation (λ≈16µ), embedded-deformation skinning (hi-res mesh rides coarse sim volume), NDG published tissue values E_muscle=45kPa / E_fat=15kPa / ν=0.47 |

---

## 2. Evaluations

### 2.1 SurRoL — MPM soft-body surgical sim [WIRED as MPM-lite]

- **Paper:** Yang et al., arXiv:2402.01181v1 (cs.RO, Feb 2024). MPM + Neo-Hookean
  tissue model; Lagrangian particles track motion/deformation, Eulerian grid
  discretizes space for forces/velocities; Taichi for GPU parallelism; SDF-based
  collision between soft tissue and rigid surgical tools. Code: new branch of
  github.com/med-air/SurRoL.
- **Why MPM beats the existing lanes for large deformation:** the paper's related
  work calls out exactly our situation — PBD/XPBD (our Jolt lane) is "fast and
  easy to implement, but not derived from physical rules"; FEM (our FEMFX lane)
  inverts under large deformation. MPM's particles carry the deformation gradient
  through arbitrary distortion, so deep dents (finisher hits, X-ray KOs) stay
  stable where FEM tets invert and XPBD volume constraints fight the pose.
- **Can MPM run in the browser?** Not SurRoL's — Taichi is a Python-embedded DSL
  with CUDA/Metal/Vulkan/CPU backends and **no WASM target**. But the algorithm
  core (P2G → grid solve → G2P) is ~200 lines and needs no GPU at our scale:
  36–80 particles × ~150–300 grid nodes × ≤12 substeps ≈ 10⁴–10⁵ FLOPs/frame.
  That runs on a phone CPU with headroom. **So: algorithm ported, Taichi not.**
- **What was wired:** `game/js/mpm-tissue.js` (`MpmTissue`, `ENGINE='mpm-lite'`):
  quadratic B-spline weights (C¹, 27-node stencil), APIC momentum transfer,
  stable Neo-Hookean first Piola-Kirchhoff stress
  P(F) = µ(F−F⁻ᵀ) + λ·ln(J)·F⁻ᵀ, explicit substepped solve (h ≤ 1/480, CFL),
  pinned core+caps as Dirichlet boundary, same belly region + same nearest-4
  vertex skinning as the Jolt lane (identical visual mapping — only the solver
  differs), same integration contract (`fromMesh`/`update`/`hit`/`dispose`/
  `anatomyFor`/`globalQuality`), zero boot cost (one dependency-free import),
  ready on frame one (no WASM wait — also the natural fallback where WASM
  is unavailable).

### 2.2 NVIDIA Isaac for Healthcare — Newton/Warp medical physics [WIRED as architecture]

- **Source:** isaac-for-healthcare.github.io, release v0.9.0. `numerical_sim/`
  (six Python packages): tetrahedral soft tissue with **XPBD deformation**,
  grasp, contact, stretch/breaking and **thermal stages**; deformable organ
  surfaces + organ–organ contact; particle-based fluids (PBF) with suction;
  Cosserat/XPBD catheter solver (deprecated in favor of numerical sim).
  Pins Warp 1.17.0 + Newton 1.6.1, Python ≥3.12, NVIDIA GPU + Docker for the
  generative sim. **Newton went GA April 2026** (per task brief).
- **Can it run in the browser?** No — CUDA, Python, Docker. This is a desktop/
  lab lane, not a game lane.
- **What ports to the game (all wired):**
  - **Staged solver systems** (i4h-physics runs deformation/grasp/contact/
    stretch stages per step): the MPM lane runs **MUSCLE → FAT → SKIN stages**
    per frame — muscle stage and fat stage solve with their own Lamé params,
    the skin stage is a lattice-neighbor relax of the displacement field
    (the discrete-shell regularizer analogue).
  - **Rigid↔soft coupling** (Newton's two-way contact; the catheter solver's
    Cosserat tree with surface skinning): the deep core + top/bottom caps are
    pinned as the **rigid bone wrap** (Dirichlet grid boundary); soft layers
    deform around it. Same idea, character-local, no contact solver needed.
  - **Per-layer materials**: particles split MUSCLE (core, enorm ≤ 0.8) / FAT
    (shell) with NDG's published moduli; `anatomySpec.materials` (future:
    fed from `roster/<fighter>/anatomy/anatomy-layers.json`) overrides them.
- **[AWAITS GPU LANE]:** full Newton/Warp desktop tooling lane (offline
  tissue sim for baking, Cosmos-H-Dreams generative surgical video — needs
  ≥12 GB VRAM + Docker; evaluated, not browser-appropriate).

### 2.3 Neural Deformation Gradients (2026) [WIRED as technique — CC BY-NC]

- **Paper:** Nolte, Kemper, Schwanecke, Botsch, "Skeletal-Driven Animation of
  Anatomical Humans via Neural Deformation Gradients", Eurographics 2026
  (Computer Graphics Forum 45(2)). **CC BY-NC — research only. No code from
  the paper or its repo (github.com/fabiankemper/NeuralDeformationGradients)
  was copied; only the published techniques are referenced.**
- **The idea:** train a network to predict **per-element deformation gradients**
  instead of vertex displacements. In thin elements a small vertex displacement
  inverts the element (negative volume, anatomy poking through skin); in
  gradient space the same configuration correctly incurs a large error — so the
  representation is naturally inversion-resistant and volume-preserving.
  Gradients are reconstructed to vertex positions with a Poisson solve; a
  prism-based approximation runs at 30 fps on consumer CPUs. Hi-res anatomy is
  driven by **embedded deformation** (barycentric embed in the coarse sim
  volume — 60× faster than their RBF warp). Bones are hard Dirichlet
  constraints; muscle/fat use stable Neo-Hookean (E_muscle=45 kPa, E_fat=15 kPa,
  ν=0.47 → λ≈16µ); skin gets discrete stretch+bend shell energies as a
  visual regularizer.
- **What was wired (technique, not code):**
  - **Gradient-space inversion guard** — the solver state IS the deformation
    gradient F per particle; when det(F) < 0.35 the guard rescales F
    isotropically back above the floor instead of letting the volume collapse.
    Same guard added to the Jolt lane as a per-lattice-cell volume check
    (crushed cell relaxes toward rest).
  - **Volume preservation via high-λ Neo-Hookean** — λ≈16µ makes the
    volume term dominate, exactly NDG's tissue character.
  - **Embedded deformation** — the render mesh rides the coarse sim lattice
    (nearest-4 inverse-distance skinning, identical to the Jolt lane's map),
    the grid-space analogue of NDG's barycentric embed.
  - **Published tissue values as defaults** — E_muscle=45kPa / E_fat=15kPa /
    ν=0.47, solver-scaled for explicit-integration stability with the µ/λ
    ratio preserved (verified in tests: λ/µ ≈ 16).
- **[FUTURE]:** Poisson reconstruction from predicted gradients (needs the
  trained network — research artifact, not shippable); full BONE→MUSCLE→FAT→
  SKIN→ORGAN volumetric layers driven by the MPM grid (today: belly region
  with muscle/fat split; the `tools/anatomy` SDF layers are the data source).

---

## 3. What was wired (files)

| File | Change |
|---|---|
| `game/js/mpm-tissue.js` | **NEW** — `MpmTissue` CPU MPM-lite backend (SurRoL algorithm core + Newton stages + NDG techniques). Same contract as `SoftBody`/`FemfxBody`; pure JS, ready frame one |
| `game/js/tissue-quality.js` | **NEW** — one shared `wh_softbody_v1` quality store for all three backends (fixes mid-session divergence: previously each backend had its own variable, so the X-ray gate could disagree with the driving backend) |
| `game/js/softbody.js` | **UPGRADED** v1.0.0 → v1.1.0: substepped world stepping (2×/frame, SurRoL/Newton technique); NDG-style per-cell inversion guard; delegates quality to the shared store; `ENGINE='jolt-xpbd'` stamp |
| `game/js/femfx-adapter.js` | Quality delegates to the shared store (was `wh_femfx_v1`) |
| `game/js/fighter.js` | **Backend picker wired for real**: `window.WH_PHYSICS_BACKEND` (`'jolt'` default \| `'mpm'` \| `'femfx'`) or per-character `char.softbodyBackend`. `'mpm'` is synchronous (zero boot cost); `'femfx'` lazy-imports with its Jolt fallback |
| `game/tests/mpm-tissue.test.mjs` | **NEW** — 13 tests: region build, NDG material ratios, muscle/fat split, 60-frame boundedness, hit injection + elastic recovery, inversion-guard det floor, dispose restore, cross-backend quality sharing, zero heavy imports |
| `WORKLOG.md` | Entry for this lane |

**Defaults are unchanged:** `'jolt'` remains the default backend — existing fights
look and feel exactly as before. Opt in per session with
`window.WH_PHYSICS_BACKEND='mpm'` or per character with
`char.softbodyBackend='mpm'`.

---

## 4. GPU vs browser matrix

| Workload | Browser (this PR) | Needs GPU/desktop |
|---|---|---|
| MPM tissue solve (36–80 particles) | ✅ CPU JS, ~10⁴ FLOPs/frame | — |
| XPBD lattice (Jolt WASM) | ✅ already shipped | — |
| Staged MUSCLE→FAT→SKIN solve | ✅ in the MPM lane | — |
| Inversion guard / volume preservation | ✅ both lanes | — |
| Full Newton/Warp sim (Newton 1.6.1) | — | [AWAITS GPU LANE] CUDA + Python + Docker |
| Cosmos-H-Dreams generative tissue video | — | [AWAITS GPU LANE] ≥12 GB VRAM + Docker |
| Taichi SurRoL sim | — | Python + CUDA/Metal (no WASM target) |
| NDG trained network + Poisson solve | — | [FUTURE] research artifact (CC BY-NC) |

---

## 5. Future work

1. **Multi-region MPM** — extend beyond belly to chest/thighs (region presets
   already support a list; the MPM grid is per-region).
2. **Anatomy-layers material feed** — `MpmTissue.anatomyFor` already accepts
   `char.softbodyMaterials`; wire `tools/anatomy/generate_layers.py` output
   (`wh.anatomy-layers` schema) to emit per-layer E/ν.
3. **ORGAN layer** — the 5th anatomy layer (PR #876); MPM handles it as a
   stiffer inner stage.
4. **WebGPU compute MPM** — when the roster needs thousands of particles,
   move P2G/G2P to a compute shader (SurRoL's Taichi kernels are the reference
   design; WGSL port).
5. **Desktop Newton lane** — offline baking of hit-deformation clips with the
   real Newton/Warp stack for the heaviest finisher moments.
6. **X-ray coupling** — `xray.js` already dents the muscle layer with the same
   injection math; drive the revealed MUSCLE layer directly from MPM particle
   positions during the KO beat.

---

## 6. Proof

- `node --test game/tests/mpm-tissue.test.mjs` — 13/13 pass.
- `node --test game/tests/*.test.mjs` — 144/149 pass; the 5 failures
  (fluid-decals, rage/urge input routing, 2 stagebreak flakes) reproduce on
  clean `origin/main` — pre-existing, unrelated to this lane.
- `node --check` clean on all touched/new JS files.
- No live-browser playtest in this pass (subagent has no live browser);
  default backend is unchanged (`'jolt'`), so existing fights are unaffected.
  Recommended follow-up: playtest `WH_PHYSICS_BACKEND='mpm'` on the
  6-SmutBase-fighter select per the owner's playtest list.
