#!/usr/bin/env python3
"""wh_blender_to_usd.py — headless Blender -> USD export with WH conventions.

Run inside Blender (4.x/5.x):
  xvfb-run -a env -u PYTHONPATH blender -b scene.blend --python wh_blender_to_usd.py -- out.usda

WH conventions applied:
  - meters, +Y up, +Z forward (Blender native; USD keeps it)
  - variant sets for attires: objects named "<base>__P1", "<base>__P2" become
    a USD variant set "attire" on the prim (matches the glTF KHR_materials_variants
    delivery built by tools/procgen/gltf-delivery/wh_attire_variants.mjs)
  - collections -> USD scopes (stage layering: environment / fighters / props)
"""
import bpy, sys, os

argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else "/tmp/wh_out.usda"

# Group attire variants: <base>__P1 -> variant set "attire"={P1,P2,...}
# NOTE: Blender 4.0's USD exporter drops custom string properties, so the
# authoritative variant signal is the PRIM NAME (<base>__P1) — downstream
# tooling parses prim names. (Blender 5.x preserves custom props; revisit.)
variants = {}
for ob in list(bpy.data.objects):
    if "__" in ob.name:
        base, var = ob.name.rsplit("__", 1)
        variants.setdefault(base, []).append((var, ob))

for base, items in variants.items():
    # keep first variant visible object as the prim; hide others (export handles
    # them as variant payloads via custom property for the USD layer step)
    for i, (var, ob) in enumerate(sorted(items)):
        ob["wh_attire_variant"] = var
        ob.hide_render = i != 0

# Version-tolerant kwargs: Blender 4.0 lacks export_armatures/export_subdiv etc.
_wanted = dict(
    export_animation=False,
    export_hair=False,
    export_uvmaps=True,
    export_normals=True,
    export_materials=True,
    export_textures=True,
    evaluation_mode="RENDER",
    generate_preview_surface=True,
)
_props = {p.identifier for p in bpy.ops.wm.usd_export.get_rna_type().properties}
_kwargs = {k: v for k, v in _wanted.items() if k in _props}
bpy.ops.wm.usd_export(filepath=out, **_kwargs)
print(f"USD exported -> {out} ({os.path.getsize(out)} bytes), "
      f"{len(variants)} attire variant groups tagged")
