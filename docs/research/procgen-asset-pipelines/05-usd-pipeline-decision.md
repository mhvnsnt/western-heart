# 05 — USD Pipelines: should teardown→game standardize on USD? (2026 research)

**Date:** 2026-10-16 · **Scope:** OpenUSD in 2026, Blender USD workflows, pipeline decision.

## What we found

### OpenUSD in 2026
- **Core Specification 1.0 ratified** (Alliance for OpenUSD); eyes on ISO ratification.
  **v26.03** (Mar 2026): native **3D Gaussian Splatting** schema
  (`UsdVolParticleField3DGaussianSplat`) + **experimental character rigging extensions**
  (groundwork for animation in Core Spec 1.1).
- Industry: Pixar/DreamWorks/Weta/ILM/DNEG (film); Remedy, Activision/COD, Epic/Fortnite
  (games); Blender, Maya, Houdini, Omniverse, Unreal, Unity (DCC/engines).
- WWDC26: **USDKit**, Safari `<model>` tag (USD native on the web for Apple platforms),
  AOM-backed mesh compression (up to 90% reduction) + AVIF textures → **7× smaller assets**.

### OpenUSD and glTF: complementary, not competing (AOUSD–Khronos liaison)
- **OpenUSD = authoring & interchange** (layers, variants, references, overrides —
  the full composed scene). **glTF = delivery** (compact runtime format for web/mobile).
- This is the industry-settled division. Adopting it avoids the "one format for everything"
  trap.

### Blender USD in 2026
- Blender imports/exports USD, and support grows every release — **but Blender still has no
  native USD stage**: import converts everything to Blender objects (no live layering /
  references / Hydra). "After import, USD is not a thing anymore."
- Our Blender is 4.0.2 (TOOLS.md); Blender 5.x manuals exist in 2026. USD round-trip works
  for meshes/materials/transforms; rig/animation round-trip is the weak point (hence the
  v26.03 rigging extensions — still experimental).

## Decision for WH teardown→game pipeline

**YES to USD for authoring/archival, NO to USD as the runtime format:**

1. **Teardown archival → USD.** Each teardown's assembled assets get a USD stage:
   variants (P1/P2 attires), layer overrides (damage states), references (shared rigs).
   USD's composition is exactly what "teardown is not done until extracted, decrypted,
   decoded, AND assembled" needs as a container. Blender USD export is sufficient for this.
2. **Web delivery → glTF** (see doc 06). The playable build is Three.js; glTF is its
   native tongue. USD→glTF export at build time.
3. **Do not wait for native USD in Blender** and do not route the runtime through USD —
   the ecosystem (compression, web loaders) is glTF-first for delivery.

## Wire-up
- `tools/procgen/usd/` — `wh_blender_to_usd.py` (headless Blender → USD export wrapper
  with WH conventions: variant sets for attires, stage layering) + README.
  (Blender built-in USD IO — no new dependency to pull.)
- This doc is the decision record. Revisit when Blender ships a native USD stage or
  Core Spec 1.1 rigging finalizes.
