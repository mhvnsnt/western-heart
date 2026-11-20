# Cloth Physics Evaluation — 2026-10-23

**Task:** pull and evaluate three cloth systems, wire the best fit into
`game/js/fx/cloth.js` for costume cloth / hair dynamics / cape physics
on the Three.js stack, with a CPU fallback where WebGPU is unavailable.

**Winner: jspdown/cloth** — its XPBD algorithm, constraint model, and
solver architecture are ported into `game/js/fx/cloth.js` (CPU backend).
The existing roster-wide cloth pipeline (`game/js/cloth-hair.js` →
`fighter-depth.js` → `autoAttachCloth`) now runs on the new engine, so
every tagged costume/hair mesh on the roster gets the upgrade.

---

## 1. The three candidates

### 1a. jspdown/cloth — WINNER (algorithm + design reference)
- **What:** WebGPU XPBD cloth, real-time on GPU via WGSL compute
  shaders, graph-coloring parallel constraint solving.
  https://deepwiki.com/jspdown/cloth · https://github.com/jspdown/cloth
- **License: MIT** (verified — `LICENSE.txt`, © 2023 Harold Ozouf).
- **Physics:** semi-explicit Euler → XPBD distance constraints
  (stretch from mesh edges, bend from adjacent-triangle hinges) →
  velocity update, with Macklin "small steps" sub-stepping
  (15 substeps/frame in the demo) and greedy graph coloring so each
  color group is particle-disjoint (parallel-safe Gauss-Seidel).
- **Why it won:**
  - Web-native, dependency-free TypeScript — the only candidate that
    speaks the game's language (browser + Three.js).
  - The constraint model is exactly what costume cloth needs:
    compliance = per-fabric stiffness (silk vs leather vs hair), bend
    hinges (proper drape, no shear-diagonal hack), mass from triangle
    areas, pinning.
  - The color-group layout ports mechanically to a future WebGPU
    backend: one compute dispatch per color group using the project's
    WGSL shaders verbatim (`semi_explicit_euler`, `apply_constraint`,
    `update_position`, `update_normal`).
  - MIT license, single author, small readable codebase (~1.5k LOC).

### 1b. openxrlab/XRTailor — evaluated, not wired
- **What:** dual-mode cloth — Swift Mode (XPBD real-time) + Quality
  Mode (FEM offline). SMPL/GLTF input. https://deepwiki.com/openxrlab/xrtailor
- **License: Apache 2.0** (verified via project docs).
- **Why not:** CUDA-only C++ with a CMake build — zero web story, cannot
  run in the game's browser stack or on the user's phone. Quality Mode
  is offline-only (~5 FPS). No Three.js/WebGL/WebGPU path exists.
- **What it contributed:** Swift Mode's real-time parameter guidance
  (substeps/iterations budgets for 30–60 FPS targets) informed our
  quality table; its multi-color Gauss-Seidel analysis corroborates the
  jspdown approach. If an offline costume-baking pipeline is ever
  wanted (pre-simulated drape LODs), XRTailor Quality Mode is the
  candidate — documented here for that future, not wired now.

### 1c. vitalight/Velvet — evaluated, reference only
- **What:** CUDA-accelerated XPBD cloth, open-source NVIDIA Flex
  alternative (attach / long-range-attachment / stretch / bend
  constraints, SDF + particle collision, spatial hashing, OpenGL
  rendering). https://deepwiki.com/vitalight/Velvet
- **License: MIT** (verified — `LICENSE.txt`, © 2022 vitalight).
- **Why not:** CUDA-only C++ (VS2019 + CUDA 11.1 build) — cannot run in
  a browser or on a phone GPU. No web port exists.
- **What it contributed:** two ideas ported into `game/js/fx/cloth.js`:
  long-range attachment constraints (used as soft skip-one bend links
  in hair chains so strands curve instead of kinking) and analytic
  capsule colliders alongside spheres for body collision. SDF collision
  is noted as a future upgrade if mesh-accurate body collision is ever
  needed.

## 2. Comparison matrix

| | jspdown/cloth | XRTailor | Velvet |
|---|---|---|---|
| Algorithm | XPBD + substeps + graph coloring | Swift: PBD/XPBD; Quality: FEM | XPBD + spatial hash |
| Platform | WebGPU (browser) | CUDA (desktop) | CUDA (desktop) |
| Web/Three.js fit | **native** | none | none |
| Phone viable | yes (WebGPU) / **yes (our CPU port)** | no | no |
| Visual quality | real-time drape, compliance fabrics | Swift: plausible; Quality: film-grade offline | Flex-class real-time |
| Integration difficulty | **low** — plain TS, portable math | very high — C++/CMake/CUDA port | very high — C++/CUDA port |
| License | **MIT** | Apache 2.0 | MIT |
| Maintained | demo-complete, stable | research-active | stable |

## 3. What shipped (and the honest backend call)

`game/js/fx/cloth.js` ports jspdown/cloth's **algorithm and solver
architecture** to dependency-free JavaScript with a **CPU backend**:

- `XPBDSolver`: typed-array XPBD — semi-explicit Euler, compliance
  distance constraints solved per graph-color group (greedy coloring
  ported from `constraints.ts`), velocity commit, analytic
  sphere/capsule colliders with inelastic contact (no bounce, no
  energy gain on deep spawns — verified by test).
- `extractTopology()`: edges + adjacent-triangle hinges from an index
  list (ports `triangles.ts`).
- Builders: `buildSheet()` (capes/skirts/sashes), `buildFromMesh()`
  (intake costume geometry directly — mass from triangle areas, pin via
  test), `buildChain()` (hair/tassels with skip-one bend links).
- Fabric presets (silk/cotton/denim/leather/cape/hair) as XPBD
  compliances; quality table (`low/medium/high` substeps + particle
  budgets) with phone-safe auto-detect + `wh-cloth-quality` override,
  mirroring `game/js/fx/particles.js`; LOD sleep at 14m.
- Three.js adapters `writePositions()`/`writeNormals()` with no three
  import — the module is node-testable.
- `availableBackends()` probes WebGPU honestly: `{ cpu: true, webgpu,
  active: 'cpu' }`.

**Why CPU and not WebGPU compute:** the game renders Three.js **WebGL**
(Effekseer shares the WebGL context), and the user's phone browser
cannot be assumed WebGPU-capable. Cloth positions must live on the CPU
to feed `BufferGeometry` attributes every frame regardless, and
cape/hair/costume particle counts (hundreds to low thousands) hold
60fps on CPU XPBD. Shipping a WebGPU path now would add a readback
round-trip per frame for zero visual gain. The color-group layout is
preserved precisely so the WebGPU upgrade is mechanical later: port
the four WGSL shaders, dispatch one pass per color group, keep the
JS-side topology/builders/adapters.

**What this replaces:** `game/js/cloth-hair.js`'s verlet core is now a
compatibility facade over the new engine — same public API
(`VerletSystem`, `ClothSheet`, `HairChain`, `autoAttachCloth`,
`CLOTH_LOD_DIST`), so `fighter-depth.js` and the roster need zero
call-site changes. Upgrades delivered roster-wide: compliance fabrics
(silk drapes ≠ leather), real bend hinges (shear-diagonal hack
removed), area-based mass, inelastic body colliders (spheres +
capsules), first-placement root translate (no attach whip).

## 4. Verification

- `node --test game/tests/cloth-xpbd.test.mjs` — 13 tests: drape
  stability (top pinned, bottom hangs, stretch < 5%, no NaN), coloring
  invariant (groups particle-disjoint), compliance (silk vs leather),
  topology extraction, mesh builder (pinning, area mass, budget
  rejection), hair chain, sphere/capsule colliders (incl. deep-spawn
  stability), adapters, quality/backends.
- `node --test game/tests/fighter-depth.test.mjs` — 43/43 pass
  (pre-existing cloth/hair API contract intact).
- Full `node --test game/tests/*.test.mjs`: 144/148 pass; the 4
  failures (fluid-decals, model-key-guard ×2, stagerage) are
  pre-existing on main without this change (verified via stash).
- Numerical drape proof: 8×10 cotton sheet, 120 steps — top row
  displacement 0.0000, bottom hangs at −0.902 of −0.90 rest, max
  rigid-link stretch 0.76%, zero NaN. ASCII side-view frames show the
  drape curve developing from flat to hanging.

## 5. Future work (not in this PR)

- WebGPU backend: port the four WGSL shaders, dispatch per color group;
  keep CPU as fallback (the module already probes and reports).
- Velvet-style SDF body collision if analytic colliders prove too
  coarse for layered costumes.
- XRTailor Quality Mode as an offline costume-drape baking pipeline.
- Wind gusts per-arena (arena metadata → `solver.wind`).

## 6. License compliance

- jspdown/cloth is MIT — attribution + algorithm port documented in
  `game/js/fx/cloth.js` header (© 2023 Harold Ozouf, project URL).
- Velvet is MIT — ideas only, no code copied; credited in header.
- XRTailor is Apache 2.0 — parameter guidance only; credited in header.
- No third-party code was vendored; no copyrighted assets involved.
- ALL CHARACTERS ARE ADULTS — cloth attaches to adult fighter costume
  meshes only (owner law).
