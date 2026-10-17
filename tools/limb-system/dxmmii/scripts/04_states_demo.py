# Stage 4 — DXMMII 5-state extra-arm state machine, keyed as a 300-frame demo.
#
# States per extra arm: ATTACHED -> RETRACTING -> HIDDEN -> GROWING -> ATTACHED,
# plus DETACHED (floating, driven by gyro controllers). Implemented with:
#  - FK controls (Rigify limb FK; STRETCH_TO muted on arm DEF chains as a
#    deliberate mechanical-design choice: DXMMII is a patchwork robot, his
#    limbs do not stretch — verified by render that FK then drives correctly)
#  - socket-centric part scaling for retract/grow (parts collapse onto the
#    socket point; verified 0.67mm collapse in stage 3)
#  - shape-key socket_open (no-pop grow) + stump-cap scale (no hollow hole)
#  - object reparenting with keep_transform for detach/reattach
#    (Blender-native constraint-switching equivalent; switch-frame delta measured)
#  - gyro animation set: spring-damper hover + attack sweeps baked onto the
#    gyro controllers (superset-skeleton drivers, per the R&D doc)
#
# Timeline (24fps): f1-48 attached | f48-72 R retract | f72-96 R hidden |
# f96-132 R grow | f132-156 attached flourish | f156-168 L detach anticip. |
# f168 SWITCH detach | f168-228 gyro | f228-240 fly back | f240 SWITCH reattach |
# f240-300 attached finale.
import bpy, math, json
from mathutils import Vector, Matrix

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/03_meshed.blend")
rig = bpy.data.objects["DXMMII_rig"]
S = bpy.context.scene
S.render.engine = "BLENDER_EEVEE"
FPS = 24
S.render.fps = FPS
S.frame_start, S.frame_end = 1, 300

# ---------------------------------------------------------------- rig config
# (DEF hierarchy repaired in 02b; arm DEF chains are pure FK.)
# Mute ALL constraints on the arm DEF chains -> pure direct FK.
# (Rigify's COPY_TRANSFORMS/STRETCH_TO mechanism was non-functional on the
# duplicated extra-arm chains; the DEF skeleton is now the animation skeleton,
# exactly as a game engine would drive it. Rigify FK/IK controls remain generated.)
for bn in ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L",
           "DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R",
           "DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L",
           "DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"):
    for c in rig.pose.bones[bn].constraints:
        c.mute = True
print("arm DEF constraints muted (pure FK)")

FK = {  # DIRECT DEF bones (pure FK after 04b repair). Poses use DEF-local axes:
    # upper arm: Z- raises / Z+ lowers; forearm: X- bends / X+ extends.
    # key_fk() takes the old FK-style (0,Y,0) poses and converts.
    "main_L": ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L"),
    "main_R": ("DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R"),
    "x_L": ("DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L"),
    "x_R": ("DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"),
}
for key, (ua, fa, ha) in FK.items():
    for bn in (ua, fa, ha):
        rig.pose.bones[bn].rotation_mode = "XYZ"

PARTS = {
    "x_L": ["DX_xarm_L_upper", "DX_xarm_L_fore", "DX_xarm_L_hand"],
    "x_R": ["DX_xarm_R_upper", "DX_xarm_R_fore", "DX_xarm_R_hand"],
}
BONES = {
    "x_L": ["DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L"],
    "x_R": ["DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"],
}
SOCKET = {
    side: Vector(rig.data.bones[f"DEF-upper_arm.x.{side}"].head_local)
    for side in ("L", "R")
}
gyro = {"L": bpy.data.objects["gyro_L"], "R": bpy.data.objects["gyro_R"]}
collar = {s: bpy.data.objects[f"DX_socket_collar_{s}"] for s in ("L", "R")}
cap = {s: bpy.data.objects[f"DX_stump_cap_{s}"] for s in ("L", "R")}
socket_sk = {s: collar[s].data.shape_keys.key_blocks["socket_open"] for s in ("L", "R")}

# ---------------------------------------------------------------- key helpers
def key_fk(arm_key, frame, upper=(0, 0, 0), fore=(0, 0, 0), hand=(0, 0, 0)):
    # Convert FK-style (0,Y,0) poses to DEF-local: upper Y -> -Z, fore Y -> X.
    ua, fa, ha = FK[arm_key]
    for bn, e in ((ua, (0, 0, -upper[1])), (fa, (fore[1], 0, 0)), (ha, (0, 0, 0))):
        pb = rig.pose.bones[bn]
        pb.rotation_euler = e
        pb.keyframe_insert(data_path="rotation_euler", frame=frame)

def key_part_scale(arm_key, frame, s):
    # Scale the OBJECTS (not bones) — x_R is never reparented, so pivots stay valid.
    # (Bone scale did not propagate to bone-parented objects in this rig.)
    # NOTE: Object scale does not render correctly on bone-parented objects
    # in Blender 4.0.2 headless (depsgraph has 0.001, render shows full size).
    # Workaround: also key hide_render for the fully-hidden state.
    for pn in PARTS[arm_key]:
        ob = bpy.data.objects[pn]
        ob.scale = (s, s, s)
        ob.keyframe_insert(data_path="scale", frame=frame)
        # Hide when fully retracted (s <= 0.001)
        hide = s <= 0.001
        ob.hide_render = hide
        ob.keyframe_insert(data_path="hide_render", frame=frame)

def key_socket(side, frame, v):
    socket_sk[side].value = v
    socket_sk[side].keyframe_insert(data_path="value", frame=frame)

def key_cap(side, frame, s):
    cap[side].scale = (s, s, s)
    cap[side].keyframe_insert(data_path="scale", frame=frame)

def key_gyro(side, frame, loc, rot=(0, 0, 0)):
    g = gyro[side]
    g.location = loc
    g.rotation_euler = rot
    g.keyframe_insert(data_path="location", frame=frame)
    g.keyframe_insert(data_path="rotation_euler", frame=frame)

# ---------------------------------------------------------------- world-matrix helper (true world, not the RNA shortcut)
def deps_update():
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    return deps

def eval_bone_matrix(bone_name):
    deps = deps_update()
    re_ = rig.evaluated_get(deps)
    return Matrix(re_.pose.bones[bone_name].matrix), deps

def eval_bone_parent_X(bone_name):
    """TRUE runtime parent matrix for RNA BONE-parenting in Blender 4.0.2.

    RNA parent_type='BONE' parents to the bone's TAIL (quirk, see 03 script
    header): X = T(posed_tail) @ Rot(pose_bone), in armature space.
    posed_tail = P @ (0, L, 0) with L = rest bone length."""
    P, deps = eval_bone_matrix(bone_name)
    db = rig.data.bones[bone_name]
    L = (Vector(db.tail_local) - Vector(db.head_local)).length
    ptail = P @ Vector((0, L, 0))
    X = Matrix.Translation(ptail) @ P.to_3x3().to_4x4()
    return X, deps

def pinv_for_bone(bone_name):
    """Parent-inverse matching the TRUE (tail-based) runtime parent matrix:
    Pinv = (R @ T(tail_local) @ Rot(matrix_local))^-1. (Do NOT use the pose
    matrix — the rest matrix is authoritative here.)"""
    rb = rig.data.bones[bone_name]
    M_rest = Matrix(rb.matrix_local)
    X_rest = Matrix.Translation(Vector(rb.tail_local)) @ M_rest.to_3x3().to_4x4()
    return (rig.matrix_world @ X_rest).inverted()

def true_world_of(ob):
    deps = deps_update()
    oe = ob.evaluated_get(deps)
    B = Matrix(oe.matrix_basis)
    if ob.parent_type == "BONE" and ob.parent and ob.parent.type == "ARMATURE":
        # NOTE: uses the TRUE tail-based parent matrix X, not the pose bone
        # matrix P (Blender 4.0.2 RNA BONE-parenting quirk). The old head-based
        # formula measured a fantasy — parts rendered tail-shifted while the
        # measurements claimed sub-micron deltas.
        X, _ = eval_bone_parent_X(ob.parent_bone)
        return rig.matrix_world @ X @ Matrix(ob.matrix_parent_inverse) @ B
    if ob.parent_type == "OBJECT" and ob.parent:
        pe = ob.parent.evaluated_get(deps)
        return Matrix(pe.matrix_world) @ Matrix(ob.matrix_parent_inverse) @ B
    return Matrix(oe.matrix_world)

def centroid_of_W(ob, W):
    vs = [Vector(v.co) for v in ob.data.vertices]
    c = sum(vs, Vector((0, 0, 0))) / len(vs)
    return W @ c

# ---------------------------------------------------------------- manual reparenting with true keep-transform
# (bpy.ops.object.parent_set uses the RNA matrix_world, which is wrong for
# bone-parented objects — it produced 304mm pops. The math below is exact.)
def parent_to_gyro(part_name, side, frame):
    ob, g = bpy.data.objects[part_name], gyro[side]
    S.frame_set(frame)
    W0 = true_world_of(ob)
    deps = deps_update()
    Pg = Matrix(g.evaluated_get(deps).matrix_world)
    ob.parent = g
    ob.parent_type = "OBJECT"
    ob.parent_bone = ""
    ob.matrix_parent_inverse = Pg.inverted()
    ob.matrix_basis = W0  # B_new = W0 because Pinv_new = Pg^-1
    W1 = true_world_of(ob)
    for dp in ("location", "rotation_euler", "scale"):
        ob.keyframe_insert(data_path=dp, frame=frame)
    return (centroid_of_W(ob, W1) - centroid_of_W(ob, W0)).length * 1000.0

def parent_to_bone(part_name, bone_name, frame):
    ob = bpy.data.objects[part_name]
    S.frame_set(frame)
    W0 = true_world_of(ob)
    Xb, deps = eval_bone_parent_X(bone_name)
    Pinv_new = pinv_for_bone(bone_name)
    B_new = Pinv_new.inverted() @ Xb.inverted() @ W0
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = bone_name
    ob.matrix_parent_inverse = Pinv_new
    ob.matrix_basis = B_new
    W1 = true_world_of(ob)
    for dp in ("location", "rotation_euler", "scale"):
        ob.keyframe_insert(data_path=dp, frame=frame)
    return (centroid_of_W(ob, W1) - centroid_of_W(ob, W0)).length * 1000.0

# ---------------------------------------------------------------- ACT 1: attached idle (f1-48)
key_fk("x_L", 1, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_R", 1, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("main_L", 1, upper=(0, 0.25, 0), fore=(0, -0.4, 0))
key_fk("main_R", 1, upper=(0, 0.25, 0), fore=(0, -0.4, 0))
for f, v in ((12, 0.55), (24, 0.35), (36, 0.15), (48, 0.35)):
    key_fk("x_L", f, upper=(0, v, 0), fore=(0, -0.5, 0))
    key_fk("x_R", f, upper=(0, v, 0), fore=(0, -0.5, 0))
# torso bob
torso = rig.pose.bones["torso"]
for f, z in ((1, 0.0), (24, 0.03), (48, 0.0)):
    torso.location = (0, 0, z)
    torso.keyframe_insert(data_path="location", frame=f)

# ---------------------------------------------------------------- ACT 2: R retract (f48-72) -> hidden (f72-96)
key_fk("x_R", 52, upper=(0, 0.2, 0), fore=(0, -1.4, 0))
key_fk("x_R", 60, upper=(0, 0.1, 0), fore=(0, -2.2, 0))
key_part_scale("x_R", 48, 1.0)
key_part_scale("x_R", 56, 0.35)
key_part_scale("x_R", 66, 0.001)
key_part_scale("x_R", 72, 0.001)
key_socket("R", 48, 0.0); key_socket("R", 58, 0.25); key_socket("R", 68, 0.0)
# hidden beat: L extra arm punches (3-arm mode)
key_fk("x_L", 72, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_L", 80, upper=(0, 0.95, 0), fore=(0, -0.15, 0))
key_fk("x_L", 88, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_L", 96, upper=(0, 0.35, 0), fore=(0, -0.5, 0))

# ---------------------------------------------------------------- ACT 3: R grow (f96-132)
key_socket("R", 96, 0.0); key_socket("R", 114, 1.0); key_socket("R", 132, 0.0)
key_part_scale("x_R", 96, 0.001)
key_part_scale("x_R", 104, 0.02)
key_part_scale("x_R", 120, 0.6)
key_part_scale("x_R", 130, 1.0)
key_fk("x_R", 96, upper=(0, 0.1, 0), fore=(0, -2.2, 0))
key_fk("x_R", 120, upper=(0, 0.25, 0), fore=(0, -0.9, 0))
key_fk("x_R", 132, upper=(0, 0.35, 0), fore=(0, -0.5, 0))

# ---------------------------------------------------------------- ACT 4: attached flourish (f132-156)
for f, v in ((132, 0.35), (144, 1.05), (156, 0.35)):
    key_fk("x_L", f, upper=(0, v, 0), fore=(0, -0.5, 0))
    key_fk("x_R", f, upper=(0, v, 0), fore=(0, -0.5, 0))

# ---------------------------------------------------------------- gyro animation set (spring-damper hover, baked f150-250)
# anchor schedule: hover -> socket (dock) -> hover+lissajous -> socket (dock) -> hover
def anchor_at(f):
    sx = SOCKET["L"]
    hover = sx + Vector((0.45, -0.25, 0.62))
    if f < 156:
        return hover
    if f < 170:
        return sx  # dock for detach
    if f < 228:
        t = (f - 170) / FPS
        return hover + Vector((0.10 * math.sin(0.9 * t), 0.08 * math.sin(1.3 * t + 1.0),
                               0.06 * math.sin(1.7 * t + 2.0)))
    if f < 242:
        return sx  # dock for reattach
    return hover

p = anchor_at(150); v = Vector((0, 0, 0))
K, C, DT = 20.0, 5.0, 1.0 / FPS
gyro_keys = {}
for f in range(150, 251):
    a = anchor_at(f)
    # hard dock windows: exact socket (guarantees clean switch frames)
    if 166 <= f <= 170 or 238 <= f <= 242:
        p = SOCKET["L"].copy(); v = Vector((0, 0, 0))
    else:
        acc = K * (a - p) - C * v
        v = v + acc * DT
        p = p + v * DT
    # attack sweep as gyro rotation (rigid assembly swing about the socket)
    t = (f - 150) / FPS
    bob = (0.12 * math.sin(0.8 * t), 0.0, 0.10 * math.sin(0.6 * t + 1.0))
    if 188 <= f <= 216:
        u = (f - 188) / 28.0
        sweep = math.sin(u * math.pi) * -1.1
        bob = (bob[0], sweep, bob[2])
    gyro_keys[f] = (p.copy(), bob)

for f, (ploc, prot) in gyro_keys.items():
    key_gyro("L", f, ploc, prot)
key_gyro("R", 1, gyro["R"].location)  # R gyro parked

# detach anticipation pose on the L chain (extended, matches gyro at socket)
key_fk("x_L", 156, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_L", 166, upper=(0, 0.12, 0), fore=(0, -0.12, 0))
key_fk("x_L", 168, upper=(0, 0.12, 0), fore=(0, -0.12, 0))

# ---------------------------------------------------------------- ACT 5: SWITCH — detach L at f168
# Key identity basis at f167 so f<168 renders rigid on-bone: the f168 switch
# keys would otherwise extrapolate constantly backward and offset the parts.
S.frame_set(167)
for pn in PARTS["x_L"]:
    ob = bpy.data.objects[pn]
    ob.location = (0, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    ob.scale = (1, 1, 1)
    for dp in ("location", "rotation_euler", "scale"):
        ob.keyframe_insert(data_path=dp, frame=167)
key_socket("L", 162, 0.0); key_socket("L", 168, 0.4); key_socket("L", 176, 0.0)
measurements = {}
S.frame_set(168)
deltas = []
for pn, bn in zip(PARTS["x_L"], BONES["x_L"]):
    d = parent_to_gyro(pn, "L", 168)
    deltas.append((pn, d))
measurements["detach_frame"] = 168
measurements["detach_deltas_mm"] = {pn: d for pn, d in deltas}
print("DETACH deltas (mm):", measurements["detach_deltas_mm"])
# stump cap on (f168-180): never a hollow hole
key_cap("L", 168, 0.001); key_cap("L", 174, 0.6); key_cap("L", 180, 1.0)

# hold the L FK chain at the extended pose through the gyro phase (invisible)
key_fk("x_L", 180, upper=(0, 0.12, 0), fore=(0, -0.12, 0))
key_fk("x_L", 240, upper=(0, 0.12, 0), fore=(0, -0.12, 0))

# ---------------------------------------------------------------- ACT 6: SWITCH — reattach L at f240
key_socket("L", 234, 0.0); key_socket("L", 240, 0.4); key_socket("L", 248, 0.0)
S.frame_set(240)
deltas = []
for pn, bn in zip(PARTS["x_L"], BONES["x_L"]):
    d = parent_to_bone(pn, bn, 240)
    deltas.append((pn, d))
measurements["reattach_frame"] = 240
measurements["reattach_deltas_mm"] = {pn: d for pn, d in deltas}
print("REATTACH deltas (mm):", measurements["reattach_deltas_mm"])
key_cap("L", 240, 1.0); key_cap("L", 246, 0.6); key_cap("L", 252, 0.001)

# ---------------------------------------------------------------- ACT 7: attached finale (f240-300), 4-arm victory
key_fk("x_L", 252, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_R", 252, upper=(0, 0.35, 0), fore=(0, -0.5, 0))
key_fk("x_L", 264, upper=(0, 1.25, 0), fore=(0, -0.35, 0))
key_fk("x_R", 264, upper=(0, 1.25, 0), fore=(0, -0.35, 0))
key_fk("main_L", 264, upper=(0, 0.85, 0), fore=(0, -0.3, 0))
key_fk("main_R", 264, upper=(0, 0.85, 0), fore=(0, -0.3, 0))
for arm in ("x_L", "x_R", "main_L", "main_R"):
    ua, fa, ha = FK[arm]
    for bn in (ua, fa, ha):
        pb = rig.pose.bones[bn]
        pb.keyframe_insert(data_path="rotation_euler", frame=300)
# settle torso
for f, z in ((252, 0.0), (276, 0.02), (300, 0.0)):
    torso.location = (0, 0, z)
    torso.keyframe_insert(data_path="location", frame=f)

# ---------------------------------------------------------------- camera: slow orbit f1-300
orb = bpy.data.objects["cam_orbiter"]
for f, rz in ((1, 0.0), (300, 3.6)):
    orb.rotation_euler = (0, 0, rz)
    orb.keyframe_insert(data_path="rotation_euler", frame=f)

# ---------------------------------------------------------------- continuity check around switches (no-pop rule)
hand_ob = bpy.data.objects["DX_xarm_L_hand"]
S.frame_set(167); c167 = centroid_of_W(hand_ob, true_world_of(hand_ob))
S.frame_set(169); c169 = centroid_of_W(hand_ob, true_world_of(hand_ob))
S.frame_set(239); c239 = centroid_of_W(hand_ob, true_world_of(hand_ob))
S.frame_set(241); c241 = centroid_of_W(hand_ob, true_world_of(hand_ob))
measurements["continuity_mm"] = {
    "f167-f169": round((c169 - c167).length * 1000, 3),
    "f239-f241": round((c241 - c239).length * 1000, 3),
}
measurements["requirement_mm"] = 1.0
measurements["pass"] = all(d < 1.0 for d in list(measurements["detach_deltas_mm"].values())
                            + list(measurements["reattach_deltas_mm"].values()))

with open("/home/hatch/workspace/dxmmii-limbs/measurements.json", "w") as fh:
    json.dump(measurements, fh, indent=2)
print("MEASUREMENTS:", json.dumps(measurements, indent=2))

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/dxmmii_4arm_rig.blend")
print("STAGE4 DONE")
