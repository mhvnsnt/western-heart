# 06 — glTF Web Delivery Best Practice 2026 (Three.js playable build)

**Date:** 2026-10-16 · **Scope:** glTF extensions and tooling for shipping WH assets to the
Three.js playable build.

## Extension registry state (Khronos, verified Oct 2026)
Ratified and relevant to WH:
- **`KHR_materials_variants`** — material variants on one mesh. **This is the P1/P2 attire
  system done right**: one GLB per fighter, variants switch attires at runtime, no duplicate
  geometry. Directly replaces our current "recolor + separate pack" workflow for delivery
  (authoring stays in Blender/textures as today).
- **`EXT_meshopt_compression`** — meshopt vertex/index compression. Faster decode than Draco
  on web, better for animated meshes. **2026 default choice for web glTF.**
- **`EXT_mesh_gpu_instancing`** — GPU instancing (crowds, arena props, breakables). Blender
  4.1+/5.x exports it; Three.js renders it.
- **`KHR_texture_basisu`** — Basis Universal supercompression (KTX2). Textures ~5–10× smaller.
- **`EXT_texture_webp`** — WebP textures, broadly supported fallback.
- **`KHR_mesh_quantization`** — quantized attributes, pairs with meshopt.
- **`KHR_materials_emissive_strength`**, `KHR_materials_sheen/clearcoat/transmission/...` —
  richer PBR where needed (crowd glow, costume sheen).
- **`KHR_animation_pointer`**, **`KHR_interactivity`** — behavior/animation wiring (future:
  menu/attire-select interactivity in pure glTF).
- **New in 2026: `KHR_gaussian_splatting`** (ratified) — volumetric captures alongside meshes.
  Watch item for photogrammetry-sourced stage backgrounds.
- glTF 2.1 roadmap: streaming/LOD, package format, **MaterialX node-graph alignment**,
  **OpenPBR alignment** — the material future is converging (see doc 07).

## Tools pulled (both MIT, verified via GitHub API)

### gltfpack — zeux/meshoptimizer (MIT, 8.5k stars, pushed 2026-10-14)
- The mesh optimizer: `EXT_meshopt_compression`, quantization, simplification, LOD,
  normal/tangent generation (`-gn`/`-gt`, 2026 additions), animation compression.
- **Why it beats alternatives:** Draco decodes slower and compresses animated meshes worse;
  meshopt is the web sweet spot (used across three.js examples and production WebGL).
- Wire-up: `tools/procgen/gltf-delivery/wh_optimize_glb.sh` — one-command
  `fighter.glb → fighter.web.glb` (meshopt + quantize + dedup). Tested 2026-10-16.

### glTF-Transform — donmccurdy/glTF-Transform (MIT, pushed 2026-10-16)
- glTF 2.0 SDK + CLI for Node.js: inspect, dedup, prune, weld, KTX2/WebP texture
  conversion, **material variants authoring**, Draco/meshopt, LOD.
- **Why we need both:** gltfpack = best-in-class mesh compression; glTF-Transform =
  the pipeline glue (variants, texture pipeline, JSON-level surgery).
- Wire-up: `tools/procgen/gltf-delivery/wh_attire_variants.mjs` — builds
  `KHR_materials_variants` (P1/P2/…) from a base GLB + per-attire material JSON;
  `install.sh` pins versions. Tested 2026-10-16.

## WH web-delivery pipeline (adopted)
```
Blender / teardown assets
  → .glb (Blender export, EXT_mesh_gpu_instancing on)
  → wh_attire_variants.mjs   (KHR_materials_variants: P1/P2/alt attires, one file)
  → wh_optimize_glb.sh       (gltfpack: meshopt + quantize; textures → KTX2/WebP via glTF-Transform)
  → *.web.glb                (playable build / TeraBox / GitHub releases)
```
Targets: fighters < 25 MB web, stages < 60 MB web (tune per asset; numbers are budgets,
not promises — measure with `gltf-transform inspect`).

## Wire-up
- `tools/procgen/gltf-delivery/`: `install.sh`, `wh_optimize_glb.sh`,
  `wh_attire_variants.mjs`, `package.json`, `README.md`. Tested 2026-10-16.
