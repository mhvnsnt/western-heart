# Dissectible Anatomy & Gram-Schmidt Voxel Constraints — Technique Summary

**Date:** 2026-10-23
**Status:** research → implementation-ready brief. MIT-licensed reference code pulled and verified.

---

## 1. Lineage (Purdue IGT Lab, Tim McGraw)

| Step | What | Award / note |
|---|---|---|
| Mesh Mortal Kombat | SIGGRAPH 2024 Real-Time Live! voxelized soft-body destruction demo | Best in Show + Audience Choice |
| "Gram-Schmidt Voxel Constraints for Real-Time Destructible Soft Bodies" | MIG 2024, 10 pp., sole author Tim McGraw. DOI `10.1145/3677388.3696322` | **Best Long Paper + Best Presentation** |
| "Real-time voxelized mesh fracture with Gram–Schmidt constraints" | Computers & Graphics vol. 132 (2025), 104382 (McGraw + Xinyi Zhou) — journal extension w/ LOD constraints | Names the public MIT reference repo |
| Dissectible Anatomy: Embodied Exploration for Education | SIGGRAPH 2026 Real-Time Live! (McGraw + student Jack Myers) — same constraints applied to color cryosection data (Visible Human Project etc.), rendered as volumetric splats with per-splat SDF | Audience Choice |
| "Interaction Techniques for Virtual Dissectible Models" | IEEE VIS 2026 short paper — rest-pose clipping, incision retraction/reflection | — |

Author background (verified): B.S. MechE → MS/PhD CS (Univ. of Florida, medical image processing) → **Rainbow Studios, EA Tiburon, Schell Games** → Purdue ~12 years. Game-dev native; explicitly invites games/VFX uptake of the method (80.lv interview, Sept 17 2026): *"VFX pre-vis and in-game destruction effects at a small to medium scale seem doable… It would be an interesting art task to design the 3D texture representing alien or monster anatomy."*

## 2. What code exists (public)

**https://github.com/brohaooo/DestructibleVoxelSystem** — the ONLY public code. Pulled and verified 2026-10-23 (file-level, raw.githubusercontent.com).

- C++, OpenGL 4.6, GLSL compute shaders, CMake; vendors assimp (3rd_party). Camera-only tech demo.
- Project files: `source/main.cpp`, `include/DestructiveCSSceneObject.h` (the sim scene object), `include/VoxelGenerator.h` (mesh→voxel pipeline), `include/GeometryPreprocess.h`, `include/GraphicObject.h`, `include/Scene.h`, `include/Renderer.h`.
- **Shaders (the crown jewels):** `shaders/particle_vgs_voxel.comp` (VGS shape constraint), `shaders/particle_vgs_face.comp` (breakable face constraints + strain-limit fracture), `shaders/particle_collision.comp`, `shaders/particle_uniform_grid.comp`, `shaders/particle_prefix_sum.comp`.
- `resource/`: pre-voxelized OBJs (Stanford bunny, teapot, gummy bear, head, pig, spot, skyscraper…), skybox, fonts, `example.gif`.
- **Whole-repo pull was intentionally NOT committed here** — it is a C++/OpenGL demo, not game code. Only the method (this doc) was pulled.

**No public code for the Dissectible Anatomy splat/SDF layer** — McGraw (80.lv): "All we have right now is a demo of a technique." No repo, no binary, no release plan stated. McGraw's project page covers only Mesh Mortal Kombat; no IGT Lab GitHub org found on github.com.

## 3. License provenance

| Item | License | Verdict |
|---|---|---|
| `DestructibleVoxelSystem` code | **MIT, Copyright (c) 2025 Lin Xinhao** (verified from repo LICENSE file) | ✅ Commercial use OK — keep the copyright notice in any pulled code |
| MIG 2024 paper (version of record) | **CC-BY 4.0** (Crossref metadata, 0-day delay) | ✅ Ideas implementable; paper openly available |
| C&G 2025 journal paper | © 2025 Elsevier, paywalled text | Ideas same as MIG + MIT code; text itself not pulled |
| Dissectible Anatomy demo/video | No license stated | Technique lineage covered above; generate own anatomy textures (Visible Human data has its own NLM licensing — irrelevant for generated monster anatomy) |
| matthias-research/pages (Müller demos) | **NO LICENSE FOUND** | ⚠️ UNRESOLVED — study/reference only, **do NOT pull code** |
| jspdown/cloth | LICENSE.txt present, type **unverified** | ⚠️ UNRESOLVED — reference only, **do NOT pull code** |

Note: the MIT repo is published under collaborator account `brohaooo` (copyright Lin Xinhao 2025), not McGraw's own account; the C&G 2025 paper officially states "Source code for the project is available at https://github.com/brohaooo/DestructibleVoxelSystem", making it authoritative.

## 4. Game-actionable technical brief (from the actual shader code)

Everything below is verified against `shaders/particle_vgs_voxel.comp` and `shaders/particle_vgs_face.comp` as pulled 2026-10-23. **This is the implementation spec the game port is built from.**

### 4.1 The setup: voxelized PBD, no connectivity

1. Voxelize a watertight input mesh into a regular cubic grid (see §4.4).
2. Create **8 PBD particles per voxel** (one per corner). Each voxel owns its 8 particles (base index + 0..7); adjacent voxels share NO particle data — connectivity is replaced by face constraints.
3. Particle = XPBD-style struct: `xpos` (w = radius), `xprev` (w = inverse mass; negative = deleted), `vel` (w = friction μ), `flags` (LOD, type, packed RGBA8 color).
4. Destruction = **disabling constraints**, never remeshing. Broken voxels/particles separate cleanly because nothing ever shared geometry.

### 4.2 VGS voxel shape constraint (`particle_vgs_voxel.comp`)

One dispatch, one thread per voxel (256-wide workgroups). 3 constraint iterations per step. Parameters: `uAlpha = 0.75` (shape stiffness), `uAlphaLen = 0.0` (volume-preservation blend; 0 = pure shape).

Per voxel, per iteration:
1. **Sum parallel edges:** for each axis, sum the 4 parallel edge vectors from the 8 corners → `dp[0..2]`. Sum the corners → center `cen`.
2. **Simultaneous (Jacobi-style) relaxed Gram-Schmidt:**
   `u[i] = dp[i] − α·(proj(dp[j],dp[i]) + proj(dp[k],dp[i]))`
   The simultaneous formulation avoids the ordering bias of classical Gram-Schmidt — this is the paper's claimed novelty.
3. **Inversion guard:** if `dot(cross(u0,u1), u2) < 0`, negate the shortest axis (by length).
4. **Volume preservation:** rescale axes by `r_v = (r³/(len0·len1·len2))^(1/3)` (r = particle radius), blended: `dp[i] = u[i]/|u[i]| · mix(r, len_i · r_v, uAlphaLen)`.
5. **Write back:** 8 corners as `cen ± dp[0] ± dp[1] ± dp[2]`, skipping zero-mass (static) particles. Skip whole voxel if all particles deleted or all static.
6. Corner index convention: `0=(−,−,−) 1=(+,−,−) 2=(−,+,−) 3=(+,+,−) 4=(−,−,+) 5=(+,−,+) 6=(−,+,+) 7=(+,+,+)`.

### 4.3 Breakable face constraints (`particle_vgs_face.comp`)

- A `FaceConstraint` joins two adjacent voxels: `mEnd = (voxel0 base vertex, voxel1 base vertex, face0_id)`; `mStrainLimit = (tension limit, compression limit)` per face.
- **Fracture test (every constraint, every iteration):** for each of the 4 face-correspondence pairs, `strain = (L − 2r)/(2r)` where L = pair distance, r = particle radius. If `strain > limit[0]` (over-stretched) or `strain < limit[1]` (over-compressed) → `BreakConstraint` (sets `mEnd = -1`; permanent) and return.
- **Projection (if not broken):** a 2-voxel VGS — same summed-edges → relaxed simultaneous Gram-Schmidt → inversion guard → volume rescale, this time with `dp[0]` = across-constraint direction, `dp[1]/dp[2]` = in-face directions. One static-voxel branch (projects the free voxel's face onto the static one; note the code carries `HACK TODO` comments on the axis permutation and the face-3 flip sign — carry these over verbatim, they are load-bearing).
- **Anisotropy is free:** different strain limits per face direction → peel into sheets (loose x, tight y/z), shred into strips, or crumble into voxels. The demo ships all three.

### 4.4 Partitioning (the parallelization that makes it fast)

- Regular grid ⇒ max vertex degree 8 ⇒ constraints partition **trivially**: 1 dispatch for all voxel constraints + 3 dispatches for face constraints (one per face-normal direction: X, Y, Z), each followed by `glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)`. No graph coloring needed (unlike tet meshes).
- The struct comment in `DestructiveCSSceneObject.h` states it outright: "faces have X, Y, Z three directions, so we need 3 buffers for partition".
- Performance (papers/interview): "hundreds of frames per second", ~3-pass Gauss-Seidel scaling near-linearly on GPU.

### 4.5 Voxelizer (`include/VoxelGenerator.h`)

- Normalize mesh to unit cube (max axis scale, so voxels stay cubic — resolution must be identical on all 3 axes; default 32³).
- Per triangle: rasterize its AABB, mark voxels passing triangle-box overlap (`triBoxOverlap`), then flood-fill (`imfill`) to get a solid volume.
- Also generates embedded surface data: clips the source triangles to each boundary voxel and builds closed polygon caps per face (the "most painful part" per the code comment) — this is how exposed interiors avoid looking hollow. The C&G 2025 paper renders via task/mesh shaders from this embedded data.

### 4.6 Port notes for the game (WebGL/WebGPU compute)

- The VGS voxel kernel is ~60 lines of GLSL with no engine dependency; ports to WGSL `compute` nearly line-for-line (SSBOs → storage buffers). The 3-dispatch partition maps to 3 `dispatchWorkgroups` calls with pipeline barriers.
- Precision: mobile GPUs — keep the `1e-12` epsilons; half-precision will break the Gram-Schmidt. Use f32 storage.
- Rendering: for a fighting game, the practical path is voxel/splat rendering (like Dissectible Anatomy's shell-only splat pass) or marching a surface from the particle field — full task/mesh-shader surface+interior rendering is desktop-class. Scope small/medium destruction first (McGraw's own suggested scope: props, dismemberment with custom "monster anatomy" interior textures, over-the-top finisher effects).

## 5. What it is NOT

Not physically accurate — deliberately non-physical "visual plausibility" constraints, not FEM, no global solver, no matrix assembly. Inversion handling is a heuristic (shortest-axis flip), not a continuum guarantee.

## 6. Demos to watch

- Dissectible Anatomy RTL 2026: https://www.youtube.com/watch?v=YffYAQLh_2s
- Mesh Mortal Kombat RTL 2024: https://www.youtube.com/watch?v=BvI6k3aEiSE
- SIGGRAPH 2026 Real-Time Live! program: https://s2026.siggraph.org/program/real-time-live/
- Project page (Mesh Mortal Kombat only): https://web.ics.purdue.edu/~tmcgraw/destruct.html
- 80.lv interview (Sept 2026): Dissectible Anatomy — McGraw details the splat/SDF layer: cryosection images define particle placement on a low-res grid; splats on a 4× grid carry color; per-splat SDF updated per frame; fracture via SDF boolean ops; only the outer shell of splats is drawn.

## 7. Gaps (not public)

- Dissectible Anatomy codebase, VIS 2026 full text, per-splat SDF update specifics, LOD-constraint formulation beyond the C&G abstract.
- Optional outreach: McGraw explicitly invites industry collaborators (tmcgraw@purdue.edu) — could shortcut the SDF-splat layer R&D.
