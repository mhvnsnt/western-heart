#!/usr/bin/env python3
"""reskin_heat.py - FALLBACK re-skin via Blender built-in bone heat (automatic weights).

Headless: import GLB, re-parent meshes to armature with ARMATURE_AUTO
(Blender's heat-diffusion auto-weights), normalize, export.
Used to A/B against the shd re-skin; the pipeline doc records which skinner
the gate numbers validate.
"""
import bpy
import sys, os, json

argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d
IN = opt("--in", None); OUT = opt("--out", None); REP = opt("--report", None)
assert IN and OUT and REP
assert not os.path.exists(OUT), f"refusing to overwrite {OUT}"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"
          and any(m.type == "ARMATURE" for m in o.modifiers)]
assert arm and meshes

bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")

for o in meshes:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB",
                          export_animations=False, export_skins=True,
                          export_image_format="AUTO")
rep = {"in": IN, "out": OUT, "skinner": "blender-bone-heat (ARMATURE_AUTO)"}
json.dump(rep, open(REP, "w"), indent=1)
print(json.dumps(rep))
