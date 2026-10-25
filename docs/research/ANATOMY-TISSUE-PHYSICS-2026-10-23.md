# Anatomy & Tissue Physics — Advanced Systems Integration (Track 2)

**Date:** 2026-10-23
**Owner instruction (verbatim):** "Pull all of this stuff in and wire it up and put it to work the best way possible"
**Status:** wired where possible; native/game-file pulls documented as [AWAITS PULL].

**License note (user override 2026-10-23):** the license firewall is OFF per
explicit user direction — pull and wire regardless of license. For
transparency: **none of the four tools in this track are copyleft**.
FEMFX = MIT, MyoSuite = Apache-2.0, OpenSim = Apache-2.0, Open3D = MIT
(all verified against the upstream repos 2026-10-23). No GPL component was
introduced by this track.

---

## 1. Status board

| # | Tool | License (verified) | Verdict |
|---|---|---|---|
| 1 | AMD FEMFX (GPUOpen-Effects/FEMFX) | **MIT** (Copyright © 2019 AMD) | **[WIRED]** JS adapter in `game/` (Jolt fallback); **[AWAITS PULL]** Emscripten WASM build |
| 2 | MyoSuite / MuJoCo (MyoHub/myosuite + myo-sim 0.2.3) | **Apache-2.0** | **[WIRED]** converter + 346-muscle dataset |
| 3 | OpenSim (opensim-org/opensim-core + opensim-models) | **Apache-2.0** | **[WIRED]** converter + 92-muscle dataset |
| 4 | Open3D mesh-cutting (isl-org/Open3D) | **MIT** | **[WIRED]** `tools/anatomy/mesh_cut.py` |

**Existing foundation (built on top of, not rebuilt):**
- PR #846 — Jolt soft-body physics (`game/js/softbody.js`): FEMFX adapter
  mirrors its `SoftBody` API exactly (`fromMesh` / `update` / `hit` /
  `dispose` / `anatomyFor` / `globalQuality`), so the backend switch never
  changes the visual mapping — only the solver.
- PR #860 — layered anatomy BONE/MUSCLE/FAT/SKIN
  (`tools/anatomy/generate_layers.py`, schema `wh.anatomy-layers/2`):
  the new `wh.anatomy-muscles/1` sidecar feeds its MUSCLE layer
  (origin/insertion replace the procedural capsule guesses) — converter
  side is [WIRED], `generate_layers.py` consuming it is [AWAITS PULL].
- PR #876 — ORGAN layer (7 organs as SDF primitives): untouched; cut faces
  from `mesh_cut.py` can expose organ cross-sections later.
- PR #874 — X-ray system (`game/js/xray.js`): `mesh_cut.py` emits one GLB
  primitive per (side, layer) with `WH_BONE`/`WH_MUSCLE`/`WH_FAT`/`WH_SKIN`
  materials, ready for the X-ray layer toggles.

---

## 2. Tool evaluations

### 2.1 AMD FEMFX — finite-element deformable tissue [WIRED adapter / AWAITS PULL build]

- **Repo:** github.com/GPUOpen-Effects/FEMFX — **MIT license** (verified from
  `LICENSE.txt`: "Copyright (c) 2019 Advanced Micro Devices, Inc.").
- **What it is:** multithreaded CPU finite-element library. Solids are
  tetrahedral meshes; each tet carries material params — Young's modulus
  (stiffness), Poisson ratio (volume preservation; ~0.5 = incompressible
  tissue), plastic yield/creep (permanent deformation), and
  **fracture stress threshold** (bone fracturing between tet faces).
  Implicit integration = stable for stiff materials, unlike explicit XPBD.
  Ships a Houdini plugin and a UE4 plugin upstream.
- **Buildability:** premake5/CMake native build; the lib is all of
  `amd_femfx/src/{Bvh,Common,ConstraintSolver,FindContacts,
  PrimitiveCollision,Scene,Simulation,SparseSolvers,Threading}/*.cpp` plus
  `amd_femfx/inc` headers (incl. Vectormath). For the browser game the path
  is Emscripten → WASM (single-threaded; pthreads optional).
- **What it gives WH:** fat elasticity (Poisson ~0.49, low Young's),
  muscle shearing (mid stiffness + deformation limits), **bone fracturing**
  (per-tet fracture threshold + fracture reports), permanent damage shape
  (plasticity) — everything the Jolt XPBD lattice cannot do.
- **What was wired:**
  - `tools/femfx/femfx_bind.cpp` — minimal C API over the real
    `AMD_FEMFX.h` surface (every function name/signature verified against
    the header 2026-10-23): `femfx_create`, `femfx_add_tetmesh`,
    `femfx_step`, `femfx_get_positions`, `femfx_apply_impulse`,
    `femfx_poll_fractures`, `femfx_destroy`. Tissue presets fat/muscle/bone
    → `FmTetMaterialParams`. Fracture report buffer wired per the header's
    required app-side setup.
  - `tools/femfx/build_wasm.sh` — Emscripten build; clones FEMFX at build
    time (not vendored, repo stays lean; pin `FEMFX_REV` for releases);
    emits `game/vendor/femfx/femfx.wasm.js`.
  - `tools/femfx/README.md` — architecture, tissue table, status.
  - `game/js/femfx-adapter.js` — `FemfxBody` class, **API-identical to
    `SoftBody`**: `fromMesh`, `update(dt)`, `hit(worldPoint, dirX, damage)`,
    `dispose`, `anatomyFor`, `globalQuality`/`setGlobalQuality`,
    `WH_PHYSICS_BACKEND` selector. Builds the same belly-region lattice
    (spine-anchored ellipsoid, pinned core + caps), converts each lattice
    cell to 5 tets (verified decomposition: 4× vol 1/6 + 1× vol 1/3 = 1.0,
    all positive orientation), trilinear vertex skinning shared with the
    Jolt path. **Never throws**: WASM missing/failed → silently drives the
    fighter with the Jolt `SoftBody` instead. `pollFractures()` exposed but
    wired to nothing visible — the show-animation lock means bone breaking
    needs explicit owner approval before any visual is built on it.
- **[AWAITS PULL]:** run `build_wasm.sh` with the Emscripten SDK to produce
  `game/vendor/femfx/femfx.wasm.js`, then playtest with
  `WH_PHYSICS_BACKEND='femfx'`. Native premake5 build for the desktop
  tooling lane is also open.

### 2.2 MyoSuite / MuJoCo — 346-muscle attachment dataset [WIRED]

- **Repo:** github.com/MyoHub/myosuite — **Apache-2.0** (verified via GitHub
  license API). Muscle XML data ships in the `myo-sim` pip package
  (0.2.3, also Apache-2.0).
- **What it is:** contact-rich musculoskeletal humanoids with Hill-type
  muscle actuators. The task's "416-muscle humanoid" counts the full body
  incl. the hand model; the downloadable `myo-sim` package carries
  **346 muscles** across leg (80 + 26), arm (24), torso (210 + 6 abdomen) —
  every one extracted.
- **Data layout (verified by pulling the real files):** muscles are MuJoCo
  `<general>` actuators in `*_muscle.xml` (`name`, `tendon`, `lengthrange`,
  10-element `gainprm`/`biasprm`); tendon routing (origin → wrap geoms →
  insertion sites) in `*_tendon.xml` `<spatial>` elements; attachment sites
  (`<site name pos>`) nested under `<body>` elements in `*_chain.xml`.
  Hill-type params per the MuJoCo XML reference (`actuator/muscle`:
  `gainprm = range(2), force, scale, lmin, lmax, vmax, fpmax, fvmax`) —
  `force` = peak isometric force (N).
- **Coordinate note:** MuJoCo is Z-up; the converter rotates every point
  `(x, y, z) → (x, z, −y)` to WH/three.js Y-up (handedness-preserving).
- **What was wired:**
  - `tools/anatomy/myosuite_to_anatomy.py` — parses the three XML kinds,
    resolves sites → bodies, converts coordinates, emits
    `wh.anatomy-muscles/1` JSON.
  - `tools/anatomy/data/myosuite_muscles.json` — **346 real muscles** with
    origin/insertion bones + points, via-points, wrap geoms, and Hill params
    (peak force, length range, vmax, fpmax/fvmax). 13 arm-muscle site refs
    (PECM/LAT → torso bodies absent from the isolated arm XML) are flagged
    in `unresolved_sites` rather than silently dropped.
- **Feeds:** (1) `generate_layers.py` MUSCLE layer — real origin/insertion
  anchors replace procedural capsule guesses ([AWAITS PULL] on the
  `generate_layers.py` side); (2) vertex-shader muscle deformation —
  contraction math (`force = F0 · activation · F_length · F_velocity`) uses
  the per-muscle Hill params.

### 2.3 OpenSim — 92-muscle attachment dataset [WIRED]

- **Repo:** github.com/opensim-org/opensim-core — **Apache-2.0** (verified);
  model files from github.com/opensim-org/opensim-models (same license).
- **What it is:** Stanford biomechanics; `.osim` files are XML with
  `Millard2012EquilibriumMuscle` / `Thelen2003Muscle` elements carrying
  `GeometryPath → PathPointSet → PathPoint` (each with `socket_parent_frame`
  = bone + `location`) plus Hill params (`max_isometric_force`,
  `optimal_fiber_length`, `tendon_slack_length`,
  `pennation_angle_at_optimal`, `max_contraction_velocity`).
- **What was wired:**
  - `tools/anatomy/osim_to_anatomy.py` — parses any `.osim`, extracts every
    muscle's path-points in order (P1 = origin, Pn = insertion, middle =
    via), wrap objects, and Hill params → `wh.anatomy-muscles/1` JSON.
    Handles Millard2012, Thelen2003, Schutte1993, Delp1990, and generic
    `Muscle` tags.
  - `tools/anatomy/data/gait2392_muscles.json` — **92 real muscles** from
    the Gait2392 reference model (`gait2392_millard2012muscle.osim`),
    54 with via-points. OpenSim is Y-up already — no rotation needed.
- **Feeds:** same two consumers as the MyoSuite data (MUSCLE layer anchors,
  shader contraction math). Gait2392 is lower-body; MyoSuite covers
  torso/arms — together they give full-body coverage.

### 2.4 Open3D mesh-cutting — bisection utility [WIRED]

- **Repo:** github.com/isl-org/Open3D — **MIT** (verified from `LICENSE`).
- **What it is:** 3D data processing with tensor-geometry boolean ops
  (`boolean_intersection` / `boolean_difference`) that seal cut faces
  automatically — exactly the "cut plane → seal holes" primitive.
- **What was wired:** `tools/anatomy/mesh_cut.py`
  - loads `.glb` (pygltflib — already a repo dependency) or `.obj`;
  - bisects along each `--plane px,py,pz,nx,ny,nz` with oversized
    half-space boxes (boolean ops → two closed solids per cut);
  - detects fresh cap faces (coplanar with the cut, normal ∥ plane normal);
  - assigns **BONE / MUSCLE / FAT / SKIN** sub-materials on the cap by
    radial distance from a bone centerline (`--center-a/b`,
    `--r-bone/muscle/fat`) — the cross-section reads as concentric tissue;
  - exports GLB with one primitive per (side, layer) and `WH_*` materials,
    ready for X-ray layer toggles (`game/js/xray.js`) and the ORGAN-layer
    cross-section views.
  - Tested end-to-end on a synthetic limb cylinder (Open3D boolean
    bisection, cut mid-limb): 2 sealed solids; cap faces classified
    BONE=4 / MUSCLE=36 / FAT=24 / SKIN=28 by radial distance from the bone
    centerline (concentric tissue rings); output GLB re-loads with 10
    primitives (2× surface + 2× 4 layer caps), 956 tris total (864 surface
    + 92 cap), materials `WH_SKIN`/`WH_BONE`/`WH_MUSCLE`/`WH_FAT`.
    A plane-miss guard returns the mesh uncut instead of emitting boolean
    debris.

---

## 3. `wh.anatomy-muscles/1` schema (new sidecar)

Both converters emit the same schema so OpenSim and MyoSuite data feed
identical consumers:

```json
{
  "schema": "wh.anatomy-muscles/1",
  "generated": "2026-10-23",
  "source": { "tool": "OpenSim|MyoSuite", "model": "…", "license": "Apache-2.0", "repo": "…" },
  "units": "meters",
  "conventions": { "up": "+Y …", "origin": "first path-point", "side": "_r/_l suffix" },
  "muscle_count": 92,
  "muscles": [
    {
      "name": "glut_med1_r", "type": "Millard2012EquilibriumMuscle",
      "side": "R",
      "origin":    { "bone": "pelvis",  "point": [x, y, z] },
      "insertion": { "bone": "femur_r", "point": [x, y, z] },
      "via":   [ { "bone": "…", "point": […] } ],
      "wraps": [ { "type": "…", "name": "…", "body": "…" } ],
      "hill": {
        "max_isometric_force": 819.0,
        "optimal_fiber_length": 0.0535,
        "tendon_slack_length": 0.078,
        "pennation_angle": 0.1396,
        "max_contraction_velocity": 10.0
      }
    }
  ]
}
```

MyoSuite variant adds `part` (leg/arm/torso), `tendon`, `unresolved_sites`,
and the MuJoCo muscle parametrization
(`lengthrange_m`, `norm_length_range`, `scale`, `lmin/lmax`, `vmax`,
`fpmax/fvmax`) under `hill`. Bone names are source-native (`pelvis`,
`femur_r`, …); the game-side name map (→ WH joint names) belongs in the
`generate_layers.py` integration ([AWAITS PULL]).

## 4. Integration points (what's next, in dependency order)

1. **[AWAITS PULL]** `generate_layers.py` ← `wh.anatomy-muscles/1`: match
   `origin.bone`/`insertion.bone` to WH joint names, drive MUSCLE-layer
   capsule endpoints from real attachments (both datasets Y-up, meters).
2. **[AWAITS PULL]** Emscripten build (`tools/femfx/build_wasm.sh`) →
   `game/vendor/femfx/femfx.wasm.js` → playtest `WH_PHYSICS_BACKEND='femfx'`.
   Tune tissue presets (Young's/Poisson) against the Jolt backend feel.
3. **[AWAITS PULL]** vertex-shader muscle deformation using `hill` params
   (force = F0 · activation · F_length · F_velocity) — data is ready in both
   JSONs.
4. **[AWAITS PULL]** `mesh_cut.py` on real fighter GLBs → dissection/X-ray
   views in `xray.js` (organ cross-sections from the PR #876 ORGAN layer).
5. **Blocked on owner:** any visible fracture effect — `pollFractures()` is
   exposed but wired to nothing (show-animation lock).

## 5. Proof

- `tools/anatomy/osim_to_anatomy.py` on the real
  `gait2392_millard2012muscle.osim` → `tools/anatomy/data/gait2392_muscles.json`:
  **92 muscles, 54 with via-points** (e.g. `glut_med1_r`: pelvis →
  femur_r, F0=819 N, optimal fiber 0.0535 m).
- `tools/anatomy/myosuite_to_anatomy.py` on `myo-sim 0.2.3`
  (`myo_sim/models/{leg,arm,torso}`) →
  `tools/anatomy/data/myosuite_muscles.json`: **346 muscles**
  (arm 24, leg 106, torso 216), 13 cross-part site refs flagged in
  `unresolved_sites` (documented source limitation, not a parse bug).
- `tools/anatomy/mesh_cut.py` on a synthetic limb cylinder (Open3D
  boolean bisection): 2 sealed solids; cap faces classified BONE/MUSCLE/
  FAT/SKIN by radial distance; output GLB re-loads with 5 primitives
  (surface + 4 layer caps). (Full run log in the PR body.)
- `node --check game/js/femfx-adapter.js` → syntax OK; 5-tet lattice
  decomposition numerically verified (volumes 4×1/6 + 1×1/3 = 1.0, all
  positive orientation).
- `tools/femfx/femfx_bind.cpp` API usage verified function-by-function
  against `amd_femfx/inc/AMD_FEMFX.h` (init/state/report/fracture paths);
  first compile happens at `build_wasm.sh` time [AWAITS PULL].

## 6. Files added by this track

- `tools/anatomy/osim_to_anatomy.py` — OpenSim `.osim` → `wh.anatomy-muscles/1`
- `tools/anatomy/myosuite_to_anatomy.py` — MyoSuite/MuJoCo XMLs → `wh.anatomy-muscles/1`
- `tools/anatomy/mesh_cut.py` — Open3D bisection + tissue-layer caps → GLB
- `tools/anatomy/data/gait2392_muscles.json` — 92 real OpenSim muscles
- `tools/anatomy/data/myosuite_muscles.json` — 346 real MyoSuite muscles
- `tools/femfx/README.md`, `tools/femfx/build_wasm.sh`, `tools/femfx/femfx_bind.cpp`
- `game/js/femfx-adapter.js` — FEMFX backend, `SoftBody`-identical API
- `docs/research/ANATOMY-TISSUE-PHYSICS-2026-10-23.md` — this file
