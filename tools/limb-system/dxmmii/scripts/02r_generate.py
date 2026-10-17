# Stage 02r — generate the Rigify control rig from the fitted real-model meta-rig.
import bpy

bpy.ops.preferences.addon_enable(module="rigify")
bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/01_metarig_real.blend")

meta = bpy.data.objects.get("DXMMII_metarig_real")
assert meta, "metarig missing"
bpy.context.view_layer.objects.active = meta
meta.select_set(True)

print("generating rigify rig (real model) ...")
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.rigify_generate()
print("generate operator returned")
bpy.ops.object.mode_set(mode="OBJECT")

rigs = [o for o in bpy.data.objects if o.type == "ARMATURE" and o is not meta]
print("armatures:", [(o.name, len(o.data.bones)) for o in rigs])
assert len(rigs) == 1, "expected exactly one generated rig"
rig = rigs[0]
rig.name = "DXMMII_rig"
print("rig renamed to DXMMII_rig")

xdefs = sorted(b.name for b in rig.data.bones if "x." in b.name and b.name.startswith("DEF-"))
print("extra-arm DEF bones:", xdefs[:12], "... total", len(xdefs))

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
print("STAGE02R DONE")
