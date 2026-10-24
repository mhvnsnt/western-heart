# Stage 02cr — calibrate the DEF-local FK axis mapping on the fitted real-model rig.
# For each arm bone, try +/-0.5 rad about each local axis, measure the world-space
# displacement of the chain tip. Prints a table; the mapping is derived from it.
import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
rig = bpy.data.objects["DXMMII_rig"]
S = bpy.context.scene

def deps_update():
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    return dg

def tail_world(bone_name):
    dg = deps_update()
    re_ = rig.evaluated_get(dg)
    pb = re_.pose.bones[bone_name]
    # tail in armature space -> world
    P = pb.matrix
    db = rig.data.bones[bone_name]
    L = (Vector(db.tail_local) - Vector(db.head_local)).length
    return rig.matrix_world @ (P @ Vector((0, L, 0)))

# clear pose
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0)
deps_update()

TESTS = [
    ("DEF-upper_arm.x.L", "DEF-hand.x.L"),   # measure hand tip (whole chain moves)
    ("DEF-forearm.x.L", "DEF-hand.x.L"),     # measure hand tip (fore rotation moves hand)
    ("DEF-upper_arm.L", "DEF-hand.L"),
    ("DEF-forearm.L", "DEF-hand.L"),
]
for bone, tip in TESTS:
    pb = rig.pose.bones[bone]
    pb.rotation_mode = "XYZ"
    base = tail_world(tip)
    print(f"== {bone} (rest tip {tuple(round(v,3) for v in base)}) ==", flush=True)
    for ax in (0, 1, 2):
        for sgn, ang in (("+", 0.5), ("-", -0.5)):
            e = [0, 0, 0]; e[ax] = ang
            pb.rotation_euler = e
            p = tail_world(tip)
            d = p - base
            print(f"  axis {'XYZ'[ax]}{sgn}: d=({d.x:+.3f},{d.y:+.3f},{d.z:+.3f})", flush=True)
    pb.rotation_euler = (0, 0, 0)
print("STAGE02CR DONE")
