# Stage 01r — fit the Rigify human meta-rig to the REAL DXMMII model landmarks.
# Landmarks measured from ~/workspace/tripo-recovery/dxmmii.glb (decoded plain),
# rotated into Rigify convention via Rz(-90): faces -Y, L=+X, up=+Z.
# (See /tmp/landmarks.json; facing verified by render.)
# Extra arms = the UPPER pair. TRANSFER FIX 2026-10-16: the Tripo source
# geometry has the upper arms floating disconnected by the head (generation
# artifact); sockets are therefore placed at the upper torso sides
# (torso |x|~0.063 at z=0.28) so the transferred arms visibly meet the torso.
# Main arms = the MIDDLE pair.
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="rigify")

bpy.ops.object.armature_human_metarig_add()
meta = bpy.context.object
meta.name = "DXMMII_metarig_real"
arm = meta.data

S = 1.0  # model is ~0.98m tall; work in meters

def V(x, y, z):
    return Vector((x * S, y * S, z * S))

# ---------------- fitted joint positions (meters, Rigify space) ----------------
# spine chain: spine..spine.003 torso, spine.004 neck, spine.005 upper neck, spine.006 head
SPINE = [V(0, 0, -0.10), V(0, 0, 0.02), V(0, 0, 0.12), V(0, 0, 0.21), V(0, 0, 0.30),
         V(0, 0, 0.345), V(0, 0, 0.375), V(0, -0.01, 0.46)]
SPINE_BONES = ("spine", "spine.001", "spine.002", "spine.003",
               "spine.004", "spine.005", "spine.006")
# arms: socket -> elbow(42%) -> wrist(70%) -> tip ; L=+X
ARMS = {
    # main pair (middle, z~0.182)
    "L": dict(sock=V(0.100, 0.003, 0.182), tip=V(0.483, 0.005, 0.182)),
    "R": dict(sock=V(-0.100, 0.003, 0.182), tip=V(-0.483, 0.005, 0.182)),
}
XARMS = {
    # extra pair (upper-torso sides, z~0.28 — TRANSFER FIX 2026-10-16, see above)
    # tip x kept at the measured fingertip (0.483) so axial assignment covers it
    "L": dict(sock=V(0.068, 0.010, 0.280), tip=V(0.483, 0.012, 0.284)),
    "R": dict(sock=V(-0.068, 0.010, 0.280), tip=V(-0.483, 0.012, 0.284)),
}
# legs: hip -> knee -> ankle -> toe-tip ; L=+X
LEGS = {
    "L": dict(hip=V(0.050, 0, -0.03), knee=V(0.050, -0.008, -0.20),
               ankle=V(0.050, -0.008, -0.36), toe=V(0.050, -0.10, -0.475)),
    "R": dict(hip=V(-0.050, 0, -0.03), knee=V(-0.050, -0.008, -0.20),
               ankle=V(-0.050, -0.008, -0.36), toe=V(-0.050, -0.10, -0.475)),
}

def joints(sock, tip, e_frac=0.42, w_frac=0.70):
    elb = sock + (tip - sock) * e_frac
    wri = sock + (tip - sock) * w_frac
    return sock, elb, wri, tip

bpy.context.view_layer.objects.active = meta
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.edit_bones

# spine / neck / head
for i, bn in enumerate(SPINE_BONES):
    eb[bn].head, eb[bn].tail = SPINE[i], SPINE[i + 1]

for side in ("L", "R"):
    sgn = 1 if side == "L" else -1
    # clavicle: spine top outer -> main socket
    eb[f"shoulder.{side}"].head = V(sgn * 0.02, 0, 0.27)
    eb[f"shoulder.{side}"].tail = ARMS[side]["sock"]
    # main arm chain (record hand delta first to carry fingers along)
    hand_old_head = eb[f"hand.{side}"].head.copy()
    sock, elb, wri, tip = joints(ARMS[side]["sock"], ARMS[side]["tip"])
    eb[f"upper_arm.{side}"].head, eb[f"upper_arm.{side}"].tail = sock, elb
    eb[f"forearm.{side}"].head, eb[f"forearm.{side}"].tail = elb, wri
    eb[f"hand.{side}"].head, eb[f"hand.{side}"].tail = wri, tip
    # carry finger chains with the hand (they are unused; just don't dangle at 1.8m)
    delta = eb[f"hand.{side}"].head - hand_old_head
    stack = [b for b in eb if b.parent == eb[f"hand.{side}"]]
    while stack:
        b = stack.pop()
        b.head += delta; b.tail += delta
        stack.extend([c for c in eb if c.parent == b])
    # legs
    L = LEGS[side]
    eb[f"thigh.{side}"].head, eb[f"thigh.{side}"].tail = L["hip"], L["knee"]
    eb[f"shin.{side}"].head, eb[f"shin.{side}"].tail = L["knee"], L["ankle"]
    eb[f"foot.{side}"].head, eb[f"foot.{side}"].tail = L["ankle"], L["toe"]
    eb[f"toe.{side}"].head = L["toe"]
    eb[f"toe.{side}"].tail = L["toe"] + V(0, -0.04, 0)
    eb[f"heel.02.{side}"].head = V(sgn * 0.050, 0.04, -0.48)
    eb[f"heel.02.{side}"].tail = L["ankle"]

# ---------------- extra arms: duplicate main samples, reposition ----------------
bpy.ops.armature.select_all(action="DESELECT")
for side in ("L", "R"):
    for bn in (f"upper_arm.{side}", f"forearm.{side}", f"hand.{side}"):
        b = eb[bn]
        b.select, b.select_head, b.select_tail = True, True, True
    bpy.ops.armature.duplicate()
    dup = {bn: eb[bn + ".001"] for bn in (f"upper_arm.{side}", f"forearm.{side}", f"hand.{side}")}
    new_names = {f"upper_arm.{side}": f"upper_arm.x.{side}",
                 f"forearm.{side}": f"forearm.x.{side}",
                 f"hand.{side}": f"hand.x.{side}"}
    for old, b in dup.items():
        b.name = new_names[old]
    sock, elb, wri, tip = joints(XARMS[side]["sock"], XARMS[side]["tip"])
    eb[new_names[f"upper_arm.{side}"]].head, eb[new_names[f"upper_arm.{side}"]].tail = sock, elb
    eb[new_names[f"forearm.{side}"]].head, eb[new_names[f"forearm.{side}"]].tail = elb, wri
    eb[new_names[f"hand.{side}"]].head, eb[new_names[f"hand.{side}"]].tail = wri, tip
    root = eb[new_names[f"upper_arm.{side}"]]
    root.parent = eb["spine.003"]
    root.use_connect = False
    bpy.ops.armature.select_all(action="DESELECT")

bpy.ops.object.mode_set(mode="OBJECT")

# rigify types on the extra roots (main arms already have limbs.arm)
for side in ("L", "R"):
    bn = f"upper_arm.x.{side}"
    pb = meta.pose.bones[bn]
    print("extra arm base:", bn, "rigify_type before:", pb.rigify_type)
    pb.rigify_type = "limbs.arm"
    print("extra arm base:", bn, "rigify_type after:", pb.rigify_type)

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/01_metarig_real.blend")
print("STAGE01R DONE")
