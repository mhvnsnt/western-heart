# WH glTF Web Delivery (`tools/procgen/gltf-delivery/`)

Ships WH fighters/stages to the Three.js playable build as optimized, variant-carrying GLBs.

## Tools (pulled, both MIT — verified via GitHub API 2026-10-16)
- **gltfpack** (zeux/meshoptimizer, MIT) — mesh optimizer: `EXT_meshopt_compression`,
  quantization, LOD. Faster web decode than Draco, better on animated meshes.
- **@gltf-transform/cli** (donmccurdy/glTF-Transform, MIT) — pipeline glue: inspect,
  texture transcode, variant authoring.

## Install
```bash
./install.sh   # repo-local bin/ (gltfpack) + node_modules (gltf-transform), no sudo
```

## Pipeline
```bash
# 1. Build attire variants (KHR_materials_variants): one GLB, P1/P2/alt switch at runtime
node wh_attire_variants.mjs fighter.glb variants.json fighter.glb
# 2. Optimize for web (meshopt + quantize; optional WebP texture transcode)
./wh_optimize_glb.sh fighter.glb fighter.web.glb [--texture-webp]
```
`variants.json` maps glTF material names → per-variant overrides (`baseColorFactor`,
`metallicFactor`, `roughnessFactor`, `emissiveFactor`, `baseColorTexture` path).
Variant[0] keeps originals; later variants clone + override. See doc 06 for the
three.js runtime side (`selectVariant`).

## Test evidence (2026-10-16, zui_rework_v2.glb 22M scratch copy)
- `wh_optimize_glb.sh`: 22M → 20M, `EXT_meshopt_compression` + `KHR_mesh_quantization`
  (texture-heavy asset — mesh compression can't shrink PNGs; honest result).
- `wh_attire_variants.mjs`: 2 variants (P1/P2), 3 cloned materials, 46/46 primitives
  mapped, `KHR_materials_variants` in extensionsUsed.
- End-to-end (variants → optimize): variants survive gltfpack; final GLB carries
  quantization + meshopt + variants together.
