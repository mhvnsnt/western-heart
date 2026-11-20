# FEMFX — finite-element tissue physics (tools/femfx/)

AMD FEMFX (github.com/GPUOpen-Effects/FEMFX, **MIT license**, © 2019 AMD) is a
multithreaded CPU finite-element library for deformable materials: solids are
tetrahedral meshes, each tet carries material params (Young's modulus,
Poisson ratio, plasticity, fracture stress), and the solver does implicit
integration with fracture between tet faces. It complements rather than
replaces rigid-body physics — exactly our use case (tissue UNDER the skin,
alongside the fight physics).

## What it gives WH

| WH need | FEMFX feature |
|---|---|
| fat jiggle / belly deformation | per-tet Young's modulus + Poisson ~0.5 (near-incompressible tissue) |
| muscle shearing under skin | anisotropic-ish stiffness via deformation limits |
| bone fracturing (KO moments) | `fractureStressThreshold` per tet + fracture reports |
| permanent damage shape | plastic yield / creep params |
| stable stiff tissue | implicit integration (unlike explicit XPBD) |

## Integration architecture

```
game/js/femfx-adapter.js   <- drop-in SoftBody replacement (same API)
        |  dynamic import (falls back to Jolt SoftBody when absent)
game/vendor/femfx/femfx.wasm.js   <- built by build_wasm.sh (NOT in repo)
tools/femfx/femfx_bind.cpp        <- C API over FEMFX (this dir)
```

The adapter builds the SAME region lattice the Jolt backend uses (belly
ellipsoid, pinned core + caps), converts each lattice cell into 5 tets, and
hands the tet mesh to FEMFX with tissue material params. Vertex skinning
(region verts -> lattice verts) is shared logic, so switching backends never
changes the visual mapping — only the solver.

Backend selection: `WH_PHYSICS_BACKEND = 'jolt' | 'femfx'` (default 'jolt').
The adapter never throws: if the WASM module is missing or fails to init, it
constructs the Jolt `SoftBody` for that fighter instead. Physics must NEVER
crash the fight.

## Files

- `femfx_bind.cpp` — C API: `femfx_create`, `femfx_add_tetmesh`,
  `femfx_step`, `femfx_get_positions`, `femfx_apply_impulse`,
  `femfx_poll_fractures`, `femfx_destroy`. Tissue presets (fat/muscle/bone)
  map to FEMFX `FmTetMaterialParams` (Young's modulus, Poisson, fracture
  threshold). API usage verified against `amd_femfx/inc/AMD_FEMFX.h`.
- `build_wasm.sh` — Emscripten build; clones FEMFX at build time (not
  vendored; pin `FEMFX_REV` for releases), emits to `game/vendor/femfx/`.
- This README.

## Status

- [x] Evaluation (license MIT, builds via premake5/CMake natively, UE4 +
      Houdini plugins exist upstream)
- [x] C binding written against the real `AMD_FEMFX.h` API surface
- [x] JS adapter (`game/js/femfx-adapter.js`) mirrors `SoftBody` API
- [ ] **AWAITS PULL**: run `build_wasm.sh` with the Emscripten SDK to
      produce `game/vendor/femfx/femfx.wasm.js`, then flip
      `WH_PHYSICS_BACKEND='femfx'` and playtest. Native (non-WASM) build is
      also possible via premake5 for the desktop tooling lane.
- [ ] Fracture gameplay is **not** wired to anything visible yet — the
      adapter polls fracture counts, but the show-animation lock means bone
      breaking needs explicit owner approval before any visual is built on it.

## License note

FEMFX is MIT — fine for `game/` runtime use. `NOTICES.txt` upstream lists
third-party bits (Vectormath); keep the MIT header intact in any vendored
copy.
