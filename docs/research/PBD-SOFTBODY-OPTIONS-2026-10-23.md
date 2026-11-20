# PBD Soft-Body Options for Web — Survey

**Date:** 2026-10-23
**Status:** recommendation made; license flags recorded.
**Target:** three.js/WebGL, mid-range Android; soft-body deformation / muscle jiggle / destructible behavior; commercial-friendly license.

---

## Recommendation (short)

- **Keep Rapier for rigid bodies** (standing plan). Rapier's core has an experimental `SoftBodySet`, but **it is NOT exposed in rapier.js** — community Jolt-vs-Rapier comparison states plainly: "Only Jolt: Supports soft-body physics." Rapier cannot deliver the jiggle requirement.
- **Add JoltPhysics.js as the soft-body engine** (MIT). Two options: (a) Rapier (rigid) + Jolt (soft only) side-by-side now; (b) full Jolt migration later — Jolt is a strict superset (rigid + soft + character controller), actively developed, now Godot's default 3D physics.
- **For jiggle specifically:** a full volumetric sim per character is overkill. Industry pattern (DynamicBone): verlet spring patches in bone space. Near-zero-cost commercial-safe option: **three-vrm's SpringBone** (MIT) — verlet bone-spring chains with stiffness/drag/gravity/colliders, made for exactly this on three.js. Use Müller's Tutorial 12 embedding (coarse tet sim → skin render mesh) only when springs aren't enough.
- **Tearing/destructible:** none of the surveyed web implementations ship it. DIY strain-threshold constraint removal is the standard route — easiest in owned code (Müller-style solver); the Purdue Gram-Schmidt voxel method (`DISSECTIBLE-ANATOMY-2026-10-23.md`) is the stronger, GPU-ready destruction path.

## Ranked candidates

| # | Candidate | What | License | Lang | XPBD | Tearing | Mobile-web fit |
|---|---|---|---|---|---|---|---|
| 1 | **JoltPhysics.js** (`jolt-physics` npm; https://github.com/jrouwe/JoltPhysics.js) | Full Jolt engine → WASM (Emscripten), maintained by Jolt's author | **MIT** | C++→WASM | Yes (XPBD-style compliant constraints) | No (DIY via constraint removal) | Excellent — WASM+SIMD, asm.js fallback |
| 2 | Matthias Müller "Ten Minute Physics" demos (matthias-research/pages) | XPBD inventor's pure-JS teaching demos: soft bodies, tet embedding, cloth | ⚠️ **No license found** | Plain JS | Yes | No (trivial to add in owned code) | Excellent — one demo: 6400 triangles >30fps on a phone in JS |
| 3 | three.js official physics examples | `webgl_physics_cloth` (Ammo btSoftBody) + `webgl_animation_cloth` (pure-JS Verlet) — wiring patterns | MIT (three.js) | JS + Ammo WASM | No (mass-spring/Verlet) | No | Excellent (Verlet one: zero deps) |
| 4 | Ammo.js (kripken/ammo.js) | Bullet port: btSoftBody mass-spring, pressure, anchors | zlib (Bullet's; verify in-repo before shipping) | C++→WASM | No | No | OK but heavy (~MBs WASM, clunky bindings) |
| 5 | jspdown/cloth | WebGPU compute-shader XPBD cloth, graph-colored parallel Gauss-Seidel, 15 substeps | ⚠️ LICENSE.txt exists, type **unverified** | TS + WGSL | Yes | No | Weak — WebGPU coverage thin on mid-range Android fleet; cloth-only |

## JoltPhysics.js (top pick) — details

- **Install:** `npm install jolt-physics`; ESM via `https://www.unpkg.com/jolt-physics/dist/jolt-physics.wasm-compat.js`. Flavors: `wasm`, `wasm-compat` (WASM base64-embedded, avoids separate .wasm hosting), `asm.js`, multithread/SIMD (Safari 16.4+ has WASM SIMD).
- **Soft bodies:** edge/distance, shear, bend compliant constraints, pressure, `SoftBodyCreationSettings`, body creation from vertex/triangle data. npm README lists a **"Soft Body Demo - Shows a soft body cloth"**.
- "Almost the entire Jolt interface has been exposed" via `JoltJS.idl`; missing bindings can be added by editing the IDL.
- Tearing not exposed natively; feasible DIY in JS bindings (unproven).
- Integration effort: medium. `npm install` + async init, standard Emscripten pattern; C++ soft-body docs are excellent, JS-specific soft-body docs thin — read `JoltJS.idl` + C++ samples. Bundle weight: a full engine just for jiggle is heavy — best justified if Jolt also replaces Rapier.

## Müller demos (best reference) — details

- https://matthias-research.github.io/pages/tenMinutePhysics/index.html — plain JS, single self-contained HTML files, zero deps.
- Tutorial 10: "Simple and unbreakable simulation of soft bodies" (discrete PBD — the classic starting point).
- Tutorial 12: "100x speedup for soft body simulations" — embed high-detail visual mesh in a **low-res tet sim mesh**: exactly the character-jiggle technique.
- Tutorial 14: "6400 triangles at more than 30 fps on a cell phone in javascript".
- `challenges/softBody.html`: full XPBD with Neo-Hookean material (deviatoric + volumetric tet constraints), mouse grab, Float32Array SoA layout.
- Integration: low-to-medium — no build step, wire three.js meshes to particle arrays. Cost is ownership (no broadphase/rigid coupling; tutorials 11/24 cover spatial hashing/BVH if needed).

## Rapier gap assessment

- Rapier core has `SoftBodySet` (experimental) in simulation structures — **not exposed in rapier.js**. Soft-body/muscle-jiggle cannot be delivered on the standing Rapier plan.
- Recommendation stands: Rapier (rigid) + JoltPhysics.js (soft) side-by-side now; evaluate full Jolt migration after spikes.

## License provenance & flags

| Item | License | Verdict |
|---|---|---|
| JoltPhysics.js | **MIT** (reported by socket.dev/Snyk) | ✅ Commercial-safe |
| three.js examples | **MIT** | ✅ Commercial-safe |
| three-vrm SpringBone | **MIT** | ✅ Commercial-safe |
| Ammo.js / Bullet | zlib (permissive) | Verify in-repo before shipping |
| matthias-research/pages | **NO LICENSE FOUND** | ⚠️ UNRESOLVED — reference/study only, **do NOT pull code from this repo** |
| jspdown/cloth | LICENSE.txt present, type **unverified** | ⚠️ UNRESOLVED — reference only, **do NOT pull code from this repo** |
| Purdue DestructibleVoxelSystem | MIT (Lin Xinhao 2025) | ✅ See DISSECTIBLE-ANATOMY-2026-10-23.md |
| MIG 2024 paper | CC-BY 4.0 | ✅ |

## Suggested spikes (crew)

1. Load `jolt-physics` (wasm-compat) in a test page; create a soft body from a sphere mesh; verify `SoftBody` bindings exist in shipped `JoltJS.idl`; measure frame cost on a mid-range Android device.
2. Port Müller's Tutorial 10/12 soft-body code into a three.js harness driving a low-res tet volume skinned to a character mesh — the jiggle prototype.
3. Decision point: Rapier+Jolt side-by-side vs. full Jolt migration, informed by spikes.
4. Resolve the two license flags (matthias-research/pages, jspdown/cloth) before any of their code enters the repo.
