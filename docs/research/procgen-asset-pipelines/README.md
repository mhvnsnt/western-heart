# Procedural Generation + Asset Pipelines — research index

**Lane:** procgen + asset pipelines · **Date:** 2026-10-16 · **Repo:** mhvnsnt/western-heart
**Branch:** `procgen-research-pullin` → PR (this lane)

## Topic docs
1. [Procedural levels/stages](01-procedural-levels-stages.md) — GDQuest PCG (MIT, pulled as
   concepts), polyblast-arena pattern (repo gone — documented), fighting-stage fairness gap.
2. [Procedural characters](02-procedural-characters.md) — MakeHuman 1.2.0a1/2 (AGPL, documented),
   MB-Lab (GPL, archived 2024), no maintained open MetaHuman equivalent (honest).
3. [Procedural textures/materials](03-procedural-textures-materials.md) — Material Maker 1.7
   (MIT, pulled), TEXTtoPBR (MIT, algorithm ported), ComfyUI PBR stack (documented),
   CC0 libraries (fetch-on-demand).
4. [Procedural music for game scores](04-procedural-music-game-score.md) — Tone.js (MIT, pulled;
   adaptive engine written), MIDI-GPT (excluded: non-commercial), Melodrive cracks
   (excluded: commercial crack). Sibling audio branch owns YuE/Stable Audio/MusicGen.
5. [USD pipeline decision](05-usd-pipeline-decision.md) — **USD for authoring/archival,
   glTF for delivery** (AOUSD–Khronos settled split). Blender USD export wired.
6. [glTF web delivery 2026](06-gltf-web-delivery-2026.md) — KHR_materials_variants (P1/P2!),
   EXT_meshopt_compression, EXT_mesh_gpu_instancing, KTX2/BasisU; gltfpack + glTF-Transform
   (both MIT, pulled and tested).
7. [Material systems](07-material-systems-pbr-shaders.md) — OpenPBR v1.1/MaterialX (track,
   don't adopt yet), CC0 libraries, WH material conventions adopted.

## What was pulled (all wired + tested 2026-10-16)
→ [`tools/procgen/`](../../tools/procgen/README.md): gltf-delivery, game-score,
arena-gen, textures, usd. Full log: [PULL-LOG.md](PULL-LOG.md).
