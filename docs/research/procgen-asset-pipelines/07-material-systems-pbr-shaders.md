# 07 — Material Systems: open PBR libraries & procedural shaders (2026 research)

**Date:** 2026-10-16 · **Scope:** open PBR material libraries, procedural shader collections
for Godot/Three.js.

## What we found

### OpenPBR v1.1 — the material standard to watch (not adopt yet)
- Academy Software Foundation subproject (Autodesk + Adobe): successor to Autodesk
  Standard Surface and Adobe Standard Material. Reference implementation lives in
  **MaterialX** (v1.39.3+); supported in **OpenUSD** (v0.25.05+); Substance 3D Painter
  12.1+ and Designer 16 ship OpenPBR across the ecosystem.
- glTF roadmap explicitly lists **MaterialX node-graph representation** and **OpenPBR
  alignment** — the whole industry is converging here.
- **WH position:** document and track. Our runtime is glTF PBR (Three.js) today; when
  three.js/glTF ratify the OpenPBR alignment, we follow. No code change now — but all
  new WH materials should be authored as **metal/rough PBR** (no spec/gloss legacy) so the
  migration is mechanical. Material Maker (doc 03) already exports this way.

### Open PBR libraries (CC0 — fetch, don't vendor)
- **AmbientCG** — ~2,000 CC0 PBR materials + HDRIs, API-friendly downloads.
- **PolyHaven** — CC0 textures/models/HDRIs, high quality bar.
- **Kimbatt/cc0-textures** — torrent bundle of CC0 PBR collections for bulk seeding.
- Wire-up: `tools/procgen/textures/wh_fetch_cc0.sh` fetches named materials on demand
  (NO-DISK-STAGING: nothing bulk-vendored).

### Procedural shader collections
- **GodotShaderCollection** (alfredbaudisch, Godot 4): dissolve/object-space effects etc.
  **No license file, last push 2022** — reference patterns only, not pulled.
- **Three.js**: MIT; its examples/jsm shaders (post-processing, instancing) are already
  our runtime library — no pull needed, usage documented in the playable-build docs.
- **penumbra23/PBR-Shaders** (MIT): educational Cg/HLSL PBR (Lambert + Cook-Torrance) —
  reference for anyone writing custom WH shaders; not needed as a dependency.

### WH material conventions (adopted 2026-10-16)
1. Author metal/rough PBR only. No spec/gloss, no legacy pipelines.
2. Procedural base via **Material Maker** graphs (versioned `.pmm` in repo) →
   exported sets per engine target.
3. AI gap-filling via **TEXTtoPBR port** (prompt → tileable set) for stages/backgrounds.
4. CC0 libraries for commodity surfaces (concrete, metal, fabric) — fetched, attributed
   per CC0 (no attribution required, logged anyway).
5. Delivery: KTX2/BasisU + meshopt via `tools/procgen/gltf-delivery/`; attire variants
   via `KHR_materials_variants`.
6. Track OpenPBR/MaterialX-in-glTF; migrate when three.js supports it.

## Wire-up
- Conventions documented here; tooling lives in `tools/procgen/textures/` and
  `tools/procgen/gltf-delivery/`. No new code in this doc.
