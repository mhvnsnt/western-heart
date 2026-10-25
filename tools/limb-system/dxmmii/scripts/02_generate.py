# Stage 2 — generate the Rigify control rig from the 4-arm meta-rig.
import bpy

bpy.ops.preferences.addon_enable(module="rigify")
bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/01_metarig.blend")

meta = bpy.data.objects.get("DXMMII_metarig")
assert meta, "metarig missing"
bpy.context.view_layer.objects.active = meta
meta.select_set(True)

print("generating rigify rig ...")
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.rigify_generate()
print("generate operator returned")
bpy.ops.object.mode_set(mode="OBJECT")

rigs = [o for o in bpy.data.objects if o.type == "ARMATURE" and o is not meta]
print("armatures:", [(o.name, len(o.data.bones)) for o in rigs])

for rig in rigs:
    xdefs = sorted(b.name for b in rig.data.bones if "x." in b.name and b.name.startswith("DEF-"))
    print("extra-arm DEF bones:", xdefs[:12], "... total", len(xdefs))
    props = sorted(b.name for b in rig.pose.bones if b.name.startswith("properties_arm"))
    print("arm property bones:", props)

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig.blend")
print("STAGE2 DONE")
