# WH USD tooling (`tools/procgen/usd/`)

No new dependency — Blender's built-in USD IO. See research doc 05 for the decision:
**USD for teardown authoring/archival, glTF for web delivery.**

## `wh_blender_to_usd.py`
Headless Blender → USD export with WH conventions:
```bash
xvfb-run -a env -u PYTHONPATH blender -b scene.blend \
  --python wh_blender_to_usd.py -- out.usda
```
- Meters, +Y up (Blender native, USD keeps it).
- Attire variants: objects named `<base>__P1` / `<base>__P2` export as prims whose
  names carry the variant — the same convention `tools/procgen/gltf-delivery/`
  uses to build `KHR_materials_variants` at delivery time.
- Collections → USD scopes (stage layering: environment / fighters / props).

Tested 2026-10-16 on Blender 4.0.2 (kwargs are version-tolerant; 4.0 lacks
`export_armatures`): cube scene → 5.2 KB `.usda`, prim `Fighter__P1` present.

## Watch items
- Blender still has no native USD stage (import converts to Blender objects).
- OpenUSD v26.03 experimental character rigging → revisit for rig round-trip.
- OpenPBR v1.1 / MaterialX alignment → migrate materials when three.js supports it.
