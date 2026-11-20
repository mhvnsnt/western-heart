# tools/texture-pipe — PBR texture pipeline for Western Heart

Tripo models land as **gray clay** (bottleneck #3 in the 2026-10-19 roster
audit). This pipeline takes a fighter from clay to game-ready PBR —
complements `tools/procgen/textures/` (which covers *authoring* PBR sets
from prompts / CC0 libraries).

## Pipeline

```
gray-clay GLB ──> bake_pbr_blender.py ──> PBR set (PNGs) ──> apply_pbr_set.py ──> textured GLB
   (Tripo)        (AO/normal/roughness     albedo/        (Principled BSDF
                   bakes + vertex-color    normal/         node trees wired
                   -> albedo)              roughness/      into the GLB)
                                           ao/metallic
```

## Quick start

```bash
BL=~/workspace/tools/blender/blender-4.0.2-linux-x64/blender

# 1. Bake maps from the mesh itself (AO, object-space detail -> tangent normal,
#    vertex colors -> albedo). Add --highpoly HIPOLY.glb for true normal bakes.
xvfb-run -a env -u PYTHONPATH $BL -b --python tools/texture-pipe/bake_pbr_blender.py -- \
  --in game/assets/models/demonio-body.glb --outdir textures/demonio-body/ --size 1024

# 2. Author/extend the albedo (Materialize, ArmorPaint, Material Maker, or
#    tools/procgen/textures/wh_prompt_pbr.sh), then wire the set into the GLB:
xvfb-run -a env -u PYTHONPATH $BL -b --python tools/texture-pipe/apply_pbr_set.py -- \
  --in game/assets/models/demonio-body.glb \
  --setdir textures/demonio-body/ \
  --manifest textures/demonio-body/manifest.json \
  --out game/assets/models/demonio-body-textured.glb

# 3. Validate + optimize
python3 tools/auto_rig/validate.py --in game/assets/models/demonio-body-textured.glb
```

## Manifest format (`manifest.json`)

Maps GLB material names to texture files in the set dir:

```json
{
  "Body":  { "baseColor": "body_albedo.png", "normal": "body_normal.png",
             "roughness": "body_rough.png", "metallic": 0.0 },
  "Armor": { "baseColor": "armor_albedo.png", "metallic": 0.9, "roughness": 0.35 }
}
```

Missing maps fall back to scalar values (metallic/roughness) or white.

## Tools wired (open source / free)

| Tool | Source | License | Role |
|------|--------|---------|------|
| Blender bake engine | blender.org (local 4.0.2) | **GPL** | AO/normal/roughness bakes, node wiring, GLB export |
| Materialize | BoundingBoxSoftware (GitHub) | **GPL-3.0** | photo -> PBR maps (normal/AO/height); see `materialize-workflow.md`. Output textures are yours — GPL covers the app, not its output |
| Material Maker | RodZill4/material-maker | **MIT** | procedural PBR authoring; already wired at `tools/procgen/textures/` |
| ArmorPaint 1.0 | armory3d/armorpaint | **open source** (verify LICENSE at build; binaries $19, source build free) | Substance-style 3D painting; see `armorpaint-build.md` for the free source build |
| TEXTtoPBR port | `tools/procgen/textures/wh_seamless_pbr.py` | **MIT** (ported) | albedo -> tileable PBR set |

## Documented, not pulled

- **Adobe Substance 3D Painter** (paid) — industry standard; the pipeline
  above is the free equivalent. Not cracked, not pulled.
- **Materialize** itself is GPL-3.0 and Unity-based — we document the
  workflow and wire its *outputs*; we don't vendor its code.
