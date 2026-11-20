# Stage 02b — repair Rigify DEF hierarchy BEFORE meshing.
# The generation cross-parented arm DEF chains through .001 duplicates
# (DEF-forearm.x.L -> DEF-upper_arm.x.L.001). This repair reparents them into
# clean chains so that parts authored in stage 03 land correctly.
# THEN stage 03 authors parts, stage 04 animates.
import bpy

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig.blend")
rig = bpy.data.objects["DXMMII_rig"]

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
eb = rig.data.edit_bones
for root, mid, tip in (("DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L"),
                       ("DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"),
                       ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L"),
                       ("DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R")):
    eb[mid].parent = eb[root]; eb[mid].use_connect = False
    eb[tip].parent = eb[mid]; eb[tip].use_connect = False
    print(f"repaired: {root} -> {mid} -> {tip}")
bpy.ops.object.mode_set(mode="OBJECT")

# Mute all constraints on arm DEF chains -> pure FK (documented design choice).
for bn in ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L",
           "DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R",
           "DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L",
           "DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"):
    for c in rig.pose.bones[bn].constraints:
        c.mute = True
    rig.pose.bones[bn].rotation_mode = "XYZ"
print("arm DEF chains: pure FK")

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig.blend")
print("STAGE02B DONE")
