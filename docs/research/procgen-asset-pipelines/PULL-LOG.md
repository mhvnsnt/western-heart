# PULL-LOG — procgen + asset pipelines (2026-10-16)

Every finding: what it is, why it beats what we have, license (verified via GitHub
API 2026-10-16), install+test evidence, where it landed. A finding without a pull-in
is incomplete — exclusions carry explicit reasons.

## Pulled + wired

| Tool | Source | License | Why it beats what we have | Landed | Test evidence |
|---|---|---|---|---|---|
| gltfpack | zeux/meshoptimizer | **MIT** (8.5k★, pushed 2026-10-14) | Web mesh compression: EXT_meshopt_compression decodes faster than Draco, better on animated meshes | `tools/procgen/gltf-delivery/` (`install.sh`, `wh_optimize_glb.sh`) | 22M→20M GLB, extensions verified in output |
| glTF-Transform | donmccurdy/glTF-Transform | **MIT** (pushed 2026-10-16) | Pipeline glue: KHR_materials_variants authoring, texture transcode, inspect | `tools/procgen/gltf-delivery/wh_attire_variants.mjs` | P1/P2 variants, 46/46 prims mapped, survives gltfpack |
| Tone.js | Tonejs/Tone.js | **MIT** (14.7k★, pushed 2026-10-12) | Browser Web Audio framework → infinite adaptive score, zero shipped audio | `tools/procgen/game-score/` (core + adapter) | 21/21 node tests green |
| Material Maker | RodZill4/material-maker | **MIT** (6k★, pushed 2026-10-16) | Open Substance Designer: node-graph PBR, batch CLI export | `tools/procgen/textures/wh_material_maker_export.sh` | CLI flags verified against official docs |
| TEXTtoPBR algorithms | Vasco888888/text-to-pbr | **MIT** | Prompt→PBR via Pollinations (our tested backend); seamless+normal+roughness algos | `tools/procgen/textures/wh_seamless_pbr.py`, `wh_prompt_pbr.sh` | Hostile boundary (113.3,0)→(0,0); gradient 1.0<8 |
| GDQuest PCG concepts | gdquest-demos/godot-procedural-generation | **MIT code** / CC-BY art | Canonical open PCG reference (walker/BSP/noise) | `tools/procgen/arena-gen/wh_arena_gen.py` (ported, fighting-stage-specific) | Mirrored+symmetric+deterministic; fairness bug caught |
| Blender USD IO | Blender built-in | GPL (app) | USD archival without new deps | `tools/procgen/usd/wh_blender_to_usd.py` | Blender 4.0.2 → .usda, prim names carry attire variants |

## Documented, not pulled (license/quality reasons)

| Item | Reason |
|---|---|
| MakeHuman (makehumancommunity) | **AGPL-3.0** code — safe to *use* for base meshes (output not AGPL-encumbered per their LICENSE.md §D); not forked into repo without legal review |
| MB-Lab (animate1978) | GPL-3.0 but **repo archived 2024-07**, all forks stale — wrong foundation |
| HumGen3D | Code GPL-3.0 but **3D assets paid (BlenderMarket)** — mixed model, excluded |
| Avatar Creator (avcsuite) | Commercial/paid — excluded |
| MIDI-GPT (Metacreation) | Code MIT but **model use restricted to non-commercial** — excluded pending terms change |
| Melodrive "unlocked" repos | **Commercial software cracks** — hard no, never crack |
| fal.ai PATINA generators | Requires paid fal.ai API key — documented |
| GodotShaderCollection | **No license file**, last push 2022 — reference only |
| polyblast-arena | **Repo 404** (gone) — pattern documented from search results |
| ComfyUI PBR stack (CHORD/StableMaterials/HiMat) | Legit but heavy — revisit for 4K needs |
| AmbientCG / PolyHaven / Kimbatt cc0-textures | CC0 — **fetched on demand** via `wh_fetch_cc0.sh`, never bulk-vendored (NO-DISK-STAGING) |

## Decisions recorded
- USD for authoring/archival, glTF for web delivery (doc 05).
- WH material conventions: metal/rough only, OpenPBR tracked not adopted (doc 07).
- Music RNG isolated from gameplay RNG; layer-crossfade architecture (doc 04).
- Arena fairness: generate one side, mirror (arena-gen README).
