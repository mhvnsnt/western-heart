# WH procedural textures (`tools/procgen/textures/`)

## Scripts
- **`wh_seamless_pbr.py`** — albedo → tileable PBR set (albedo seamless, normal +Y glTF,
  roughness, height, metallic). Python port of TEXTtoPBR's (MIT) client-side algorithms,
  hardened: smoothest-boundary roll gives *exact* tile-edge continuity for any input
  (no blend-band ghosting). Tested 2026-10-16: hostile split image boundary
  (113.3, 0.0) → (0.0, 0.0); gradient boundary 1.00 (< 8 threshold).
- **`wh_prompt_pbr.sh "prompt" OUTDIR/ [--size N]`** — Pollinations.AI (Flux, zero-signup,
  our tested backend) → albedo → `wh_seamless_pbr.py` → PBR set. Mirrors TEXTtoPBR's
  pipeline without the React app.
  - Tested 2026-10-16: "weathered dojo wood planks" → full 512px PBR set, own-eyes
    verified (wood planks, correct maps).
  - Caveats (honest): a `pollinations.ai` watermark appeared despite `nologo=true` —
    **inspect every output**, crop/inpaint if present; Flux may add decorative elements
    despite "no objects" — iterate prompts or crop to clean regions.
- **`wh_material_maker_export.sh graphs/ exported/ [target]`** — batch export of
  Material Maker `.ptex` graphs: `material_maker --export-material --target <engine>`
  (Blender/Godot/Unity/Unreal). Needs Material Maker installed
  (`MATERIAL_MAKER_BIN`, https://github.com/RodZill4/material-maker/releases).
- **`wh_fetch_cc0.sh OUTDIR/ <AmbientCG-ID>...`** — on-demand CC0 PBR materials
  (verified 2026-10-16: `ambientcg.com/get?file=<ID>_2K-JPG.zip`).

## Pulled (open source, verified 2026-10-16)
- **Material Maker** (RodZill4/material-maker, **MIT**) — node-based procedural PBR
  authoring; the open Substance Designer. Wired via export script above.
- **TEXTtoPBR algorithms** (Vasco888888/text-to-pbr, **MIT**) — ported to
  `wh_seamless_pbr.py` (seamless tiling, Sobel normals, roughness-from-luminance).

## Documented, not pulled
- ComfyUI+SDXL+PBR-decomposition stack (heavy; revisit for 4K needs), fal.ai PATINA
  (needs API key), PlaneToPBR (watch), AmbientCG/PolyHaven/Kimbatt cc0-textures (CC0 —
  fetched on demand, never bulk-vendored per NO-DISK-STAGING).
