# Workflow: Materialize — photo to PBR maps (FREE, open source)

Materialize (Bounding Box Software) turns a single diffuse/albedo image
into a full PBR set: height, normal, ambient occlusion, edge, roughness
(inverted shininess), metallic. It was used on the Uncharted games for
material updates.

**Cost:** $0. **License: GPL-3.0** — the *application* is GPL; the texture
maps it outputs are yours to ship (GPL covers code, not output). We do NOT
vendor its code — we document the workflow and consume its outputs.

- Download: https://www.boundingboxsoftware.com/materialize/
- Source: GitHub `BoundingBoxSoftware/Materialize` (GPL-3.0)

## WH workflow: clay render -> full PBR

1. Render the gray-clay fighter orthographic (front/side/back) — or paint a
   flat albedo in ArmorPaint / GIMP.
2. Materialize: load the albedo → adjust Height → generate Normal / AO /
   Edge / Smoothness maps → export PNGs.
3. Convert Smoothness → Roughness: invert (Materialize exports shininess;
   `roughness = 1 - smoothness`). One-liner with PIL or GIMP.
4. Drop the set into `textures/<fighter>/` + write `manifest.json`, then:
   ```bash
   xvfb-run -a env -u PYTHONPATH <blender> -b --python tools/texture-pipe/apply_pbr_set.py -- \
     --in game/assets/models/<fighter>.glb --setdir textures/<fighter>/ \
     --manifest textures/<fighter>/manifest.json \
     --out game/assets/models/<fighter>-textured.glb
   ```

## Notes

- Materialize is Unity-engine based (Windows-first); on this Linux pipeline
  it runs under Wine, or on any team Windows box. The *outputs* flow into
  the Linux pipeline above either way.
- For a pure-Linux alternative with the same math, use
  `tools/procgen/textures/wh_seamless_pbr.py` (MIT-ported algorithms:
  Sobel normals, seamless tiling, roughness-from-luminance).
