# Stage 1 — Rigify multi-arm meta-rig for DXMMII.
# 2 standard arm samples (human metarig) + 2 EXTRA arm samples socketed at the
# upper back/shoulder region (Goro-anatomy layout: extra pair roots behind the
# main pair, parented to the chest bone, unconnected so they can be repositioned
# / unparented later). Runs headless.
import bpy
from mathutils import Vector

bpy.ops.preferences.addon_enable(module="rigify")

# clean scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

bpy.ops.object.armature_human_metarig_add()
meta = bpy.context.object
meta.name = "DXMMII_metarig"
arm = meta.data

GRID = 0.05
def snap(v):
    return Vector((round(v.x / GRID) * GRID, round(v.y / GRID) * GRID, round(v.z / GRID) * GRID))

bpy.context.view_layer.objects.active = meta
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.edit_bones

# socket targets: upper back/shoulder region, behind the main shoulder line
spine3 = eb["spine.003"]
targets = {
    "L": snap(spine3.head + Vector((0.34, -0.26, 0.10))),
    "R": snap(spine3.head + Vector((-0.34, -0.26, 0.10))),
}

for side in ("L", "R"):
    # select the standard arm limb bones and duplicate them
    bpy.ops.armature.select_all(action="DESELECT")
    for bn in (f"upper_arm.{side}", f"forearm.{side}", f"hand.{side}"):
        b = eb[bn]
        b.select = True
        b.select_head = True
        b.select_tail = True
    bpy.ops.armature.duplicate()

    # the duplicates carry .001 suffixes
    dup = {bn: eb[bn + ".001"] for bn in (f"upper_arm.{side}", f"forearm.{side}", f"hand.{side}")}
    new_names = {f"upper_arm.{side}": f"upper_arm.x.{side}",
                 f"forearm.{side}": f"forearm.x.{side}",
                 f"hand.{side}": f"hand.x.{side}"}
    for old, b in dup.items():
        b.name = new_names[old]

    # translate the whole duplicate chain so its root lands on the socket point.
    # snap the DELTA once (grid pivots per KatsBits) then apply it EXACTLY to
    # every bone so the chain stays connected — never snap heads/tails alone.
    raw_delta = targets[side] - eb[new_names[f"upper_arm.{side}"]].head
    delta = snap(raw_delta)
    for b in (eb[new_names[f"upper_arm.{side}"]],
              eb[new_names[f"forearm.{side}"]],
              eb[new_names[f"hand.{side}"]]):
        b.head = b.head + delta
        b.tail = b.tail + delta

    # parent root to chest, UNCONNECTED (free parent, movable later)
    root = eb[new_names[f"upper_arm.{side}"]]
    root.parent = spine3
    root.use_connect = False

bpy.ops.object.mode_set(mode="OBJECT")

# confirm / set the rig type on the extra arm roots (lives on pose bones)
for side in ("L", "R"):
    bn = f"upper_arm.x.{side}"
    pb = meta.pose.bones[bn]
    print("extra arm base:", bn, "rigify_type before:", pb.rigify_type)
    pb.rigify_type = "limbs.arm"
    print("extra arm base:", bn, "rigify_type after:", pb.rigify_type)
print("main arm rigify_type:", meta.pose.bones["upper_arm.L"].rigify_type)

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/01_metarig.blend")
print("STAGE1 DONE")
