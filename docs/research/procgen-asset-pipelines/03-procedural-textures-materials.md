# 03 — Procedural Textures / Materials (2026 research)

**Date:** 2026-10-16 · **Scope:** Material Maker state, open Substance alternatives, seamless AI
texture generators.

## What we found

### Material Maker (RodZill4/material-maker) — PULLED (wired)
- The open Substance Designer alternative. Node-based procedural PBR authoring **built on the
  Godot engine**; nodes are GLSL shaders; one-click export to Godot/Unity/Unreal/HDRP.
- License: **MIT** (verified via GitHub API + repo README). 5,995 stars, pushed 2026-10-16 —
  actively maintained. v1.7 (2026) added SDF nodes, DDS support, 3D painting; also on Steam
  (paid build funds development; the GitHub build is free).
- **Why it beats what we have:** today WH textures are hand-painted per character/stage.
  Material Maker gives a **node-graph, version-controllable, batch-exportable** PBR texture
  pipeline — one graph → albedo/normal/roughness/metallic/AO sets for every stage surface.
- Wire-up: `tools/procgen/textures/` — install notes + `wh_material_maker_export.sh`
  (headless batch export wrapper) + README with the Godot→WH texture workflow.

### TEXTtoPBR (Vasco888888/text-to-pbr) — PULLED (algorithm ported)
- MIT-licensed (verified) web app: text prompt → **Pollinations.AI (Flux)** albedo →
  client-side mirror-blend seamless tiling → Sobel-filter normal maps, blur/contrast
  roughness & displacement → ZIP of PBR maps + Three.js preview.
- **Why it fits WH:** Pollinations is already our tested zero-signup image backend
  (MEMORY: "Pollinations.ai tested working"). This closes the loop: prompt → tileable PBR
  set → stage/character materials, no Substance license.
- Wire-up: `tools/procgen/textures/wh_seamless_pbr.py` — Python port of the core
  algorithms (seamless mirror-blend tiling, Sobel normal-map generation, roughness from
  luminance) so the pipeline runs headless without the React app; plus
  `wh_prompt_pbr.sh` (Pollinations → process → PBR set). Tested (see tools README).

### AI texture landscape 2026 (documented, not pulled)
- **ComfyUI + SDXL + PBR-decomposition models** is the dominant self-hosted text-to-PBR
  stack (Ubisoft CHORD, StableMaterials, ComfyUI-TextureAlchemy; late-2025: native 4K
  SVBRDF HiMat, millisecond SuperMat decomposition). Powerful but heavy — revisit when a
  stage needs 4K AI materials; the TEXTtoPBR port covers the 1–2K need today.
- **fal.ai PATINA** generators (el-ouardy/ahmed0x77 forks): good, but require a fal.ai API
  key (paid credit model) — excluded from pull, documented.
- **PlaneToPBR** (Blender extension, AI single-image → PBR plane, updated Apr 2026): single
  image → diffuse/normal/roughness/depth/segmentation. Interesting for photo-sourced stage
  graffiti/decals; no repo URL captured — watch item, not pulled.

### CC0 PBR libraries (documented — fetch scripts, not bulk)
- **AmbientCG** (ambientcg.com) and **PolyHaven** (polyhaven.com): thousands of CC0 PBR
  materials + HDRIs, free, no account. The standard open material library answer.
- **Kimbatt/cc0-textures**: torrent bundle of CC0 PBR collections (any-purpose use).
- Wire-up: `tools/procgen/textures/wh_fetch_cc0.sh` — scripted fetch of specific AmbientCG
  materials by ID into `assets/` (no bulk vendoring — NO-DISK-STAGING law).

## Wire-up summary
- `tools/procgen/textures/`: Material Maker export wrapper, seamless-PBR Python port,
  Pollinations prompt→PBR script, CC0 fetch script. All tested 2026-10-16.
