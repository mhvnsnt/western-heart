# Stage 3 — build DXMMII's modular mechanical body (v2).
# FIX: geometry stays in WORLD coordinates; bone-parent inverse = rest bone
# matrix inverted. child_world = bone_new @ inv(bone_rest) -> rigid follow.
import bpy, math, bmesh
from mathutils import Vector, Matrix

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig.blend")
rig = bpy.data.objects["DXMMII_rig"]
# Clear any residual pose so rest matrices are authoritative
for pb in rig.pose.bones:
    pb.location = (0, 0, 0)
    pb.rotation_euler = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
    pb.scale = (1, 1, 1)
bpy.context.view_layer.update()
S = bpy.context.scene
S.render.engine = "BLENDER_EEVEE"
S.render.resolution_x, S.render.resolution_y = 960, 540

# ---------------------------------------------------------------- materials
def mat(name, rgb, rough=0.6, metallic=0.1):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m

M_YEL = mat("DX_yellow", (0.82, 0.62, 0.10))
M_ORG = mat("DX_orange", (0.78, 0.34, 0.10))
M_TEAL = mat("DX_teal", (0.13, 0.48, 0.48))
M_WHT = mat("DX_white", (0.78, 0.76, 0.70))
M_DARK = mat("DX_dark", (0.12, 0.12, 0.13), 0.5, 0.3)
M_STEEL = mat("DX_steel", (0.42, 0.43, 0.45), 0.35, 0.8)
M_PINK = mat("DX_pink", (0.85, 0.42, 0.48))
M_HAZ = mat("DX_hazard", (0.85, 0.68, 0.08))

# ---------------------------------------------------------------- helpers
def bone_ht(name):
    b = rig.data.bones[name]
    return Vector(b.head_local), Vector(b.tail_local)

def make_obj(name, mesh, material=None, shade_smooth=False):
    ob = bpy.data.objects.new(name, mesh)
    S.collection.objects.link(ob)
    if material:
        mesh.materials.append(material)
    if shade_smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return ob

def parent_to_bone(ob, bone_name):
    """Rigid mechanical parenting. Geometry must be in WORLD coords.
    parent_inverse is built from the armature-DATA rest matrix,
    never the pose matrix — the pose matrix needs a depsgraph eval and goes
    stale on file load, which silently offsets every part.

    BLENDER 4.0.2 QUIRK (root cause of the disassembled-parts defect, found
    2026-10-16): setting parent_type='BONE' via RNA makes the depsgraph AND
    the renderer parent the object to the bone's TAIL, not its head
    (effective parent matrix = T(posed_tail) @ Rot(pose_bone); the
    bpy.ops.object.parent_set(type='BONE') operator parents to the head).
    Verified with minimal repros: RNA => tail-based, operator => head-based,
    regardless of RNA assignment order. So Pinv MUST be the inverse of the
    TAIL-based rest matrix: (T(tail_local) @ Rot(matrix_local))^-1.
    The old head-based Pinv = (R @ matrix_local)^-1 shifted every part by
    exactly one bone-vector toward the tail in every render. Bone roll was
    investigated and ruled out — this quirk is the whole defect."""
    rb = rig.data.bones[bone_name]
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = bone_name
    M_rest = Matrix(rb.matrix_local)
    tail = Vector(rb.tail_local)
    X_rest = Matrix.Translation(tail) @ M_rest.to_3x3().to_4x4()
    ob.matrix_parent_inverse = (rig.matrix_world @ X_rest).inverted()

def box_part(name, bone, center, size, material):
    mesh = bpy.data.meshes.new(name + "_mesh")
    verts = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    sx, sy, sz = size[0]/2, size[1]/2, size[2]/2
    verts = [tuple(center + Vector((v[0]*sx, v[1]*sy, v[2]*sz))) for v in verts]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = make_obj(name, mesh, material)
    parent_to_bone(ob, bone)
    return ob

def limb_seg(name, bone, r_head, r_tail, material, ball_r=0.0):
    head, tail = bone_ht(bone)
    axis = tail - head
    length = axis.length
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10,
                          radius1=r_head, radius2=r_tail, depth=length)
    # cone local +Z = axis; rotate +Z onto bone dir, move to midpoint
    q = Vector((0, 0, 1)).rotation_difference(axis.normalized())
    M = Matrix.Translation(head + axis/2) @ q.to_matrix().to_4x4()
    for v in bm.verts:
        v.co = M @ v.co
    if ball_r > 0:
        b2 = bmesh.new()
        bmesh.ops.create_icosphere(b2, subdivisions=2, radius=ball_r)
        for v in b2.verts:
            v.co = v.co + head
        # merge
        for v in b2.verts:
            bm.verts.new(v.co)
        bm.verts.ensure_lookup_table()
        b2.free()
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(mesh)
    bm.free()
    ob = make_obj(name, mesh, material, shade_smooth=True)
    parent_to_bone(ob, bone)
    return ob

# ---------------------------------------------------------------- torso / pelvis / head
def mid(bn):
    h, t = bone_ht(bn)
    return (h + t) / 2

box_part("DX_pelvis", "DEF-spine", mid("DEF-spine"), (0.42, 0.26, 0.30), M_TEAL)
box_part("DX_belly", "DEF-spine.001", mid("DEF-spine.001"), (0.46, 0.28, 0.34), M_WHT)
box_part("DX_chest", "DEF-spine.002", mid("DEF-spine.002"), (0.52, 0.30, 0.36), M_YEL)
box_part("DX_uchest", "DEF-spine.003", mid("DEF-spine.003"), (0.56, 0.30, 0.38), M_ORG)
box_part("DX_hazard_band", "DEF-spine.002", mid("DEF-spine.002") + Vector((0, 0.155, 0.02)),
         (0.53, 0.02, 0.10), M_HAZ)

HEAD = "DEF-spine.006"  # head DEF bone
head_c = mid(HEAD)
box_part("DX_head", HEAD, head_c, (0.34, 0.30, 0.36), M_YEL)
box_part("DX_eye_L", HEAD, head_c + Vector((0.09, 0.155, 0.05)), (0.09, 0.02, 0.11), M_DARK)
box_part("DX_eye_R", HEAD, head_c + Vector((-0.09, 0.155, 0.05)), (0.09, 0.02, 0.11), M_DARK)
box_part("DX_tongue", HEAD, head_c + Vector((0.0, 0.17, -0.12)), (0.07, 0.10, 0.05), M_PINK)
box_part("DX_boombox", HEAD, head_c + Vector((0, 0.02, 0.28)), (0.30, 0.18, 0.16), M_DARK)
box_part("DX_speaker_L", HEAD, head_c + Vector((0.08, 0.115, 0.28)), (0.09, 0.02, 0.09), M_STEEL)
box_part("DX_speaker_R", HEAD, head_c + Vector((-0.08, 0.115, 0.28)), (0.09, 0.02, 0.09), M_STEEL)
box_part("DX_antenna", HEAD, head_c + Vector((0.12, 0.0, 0.42)), (0.015, 0.015, 0.22), M_STEEL)

# ---------------------------------------------------------------- arms
ARM_STYLE = {"L": (M_TEAL, M_WHT, M_YEL), "R": (M_YEL, M_ORG, M_YEL)}
def build_arm(tag, side):
    up, fo, ha = ARM_STYLE[side]
    if tag == "":
        ub, fb, hb = f"DEF-upper_arm.{side}", f"DEF-forearm.{side}", f"DEF-hand.{side}"
        prefix = f"DX_arm_{side}"
    else:
        ub, fb, hb = f"DEF-upper_arm.x.{side}", f"DEF-forearm.x.{side}", f"DEF-hand.x.{side}"
        prefix = f"DX_xarm_{side}"
    limb_seg(f"{prefix}_upper", ub, 0.085, 0.070, up, ball_r=0.105)
    limb_seg(f"{prefix}_fore", fb, 0.070, 0.058, fo, ball_r=0.075)
    box_part(f"{prefix}_hand", hb, mid(hb), (0.11, 0.16, 0.07), ha)
    return Vector(bone_ht(ub)[0])

sockets = {}
for side in ("L", "R"):
    build_arm("", side)
    sockets[side] = build_arm("x", side)

# ---------------------------------------------------------------- legs
for side in ("L", "R"):
    limb_seg(f"DX_leg_{side}_thigh", f"DEF-thigh.{side}", 0.105, 0.085,
             M_TEAL if side == "L" else M_ORG, ball_r=0.12)
    limb_seg(f"DX_leg_{side}_shin", f"DEF-shin.{side}", 0.085, 0.070,
             M_YEL if side == "L" else M_WHT, ball_r=0.09)
    fh, ft = bone_ht(f"DEF-foot.{side}")
    box_part(f"DX_foot_{side}", f"DEF-foot.{side}",
             (fh + ft) / 2 + Vector((0, 0.05, -0.02)), (0.16, 0.30, 0.12), M_DARK)

# ---------------------------------------------------------------- socket collars + stump caps (WORLD-space authored, chest-parented)
chest_bone = "DEF-spine.003"
for side in ("L", "R"):
    s = sockets[side]
    uh, ut = bone_ht(f"DEF-upper_arm.x.{side}")
    adir = (ut - uh).normalized()  # world arm direction
    # collar torus, axis along arm dir, at socket (operator then transform)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.115, minor_radius=0.035,
                                     major_segments=16, minor_segments=8, location=(0, 0, 0))
    _to = bpy.context.object
    collar_mesh = _to.data
    bpy.data.objects.remove(_to, do_unlink=True)
    q = Vector((0, 0, 1)).rotation_difference(adir)
    collar_mesh.transform(Matrix.Translation(s) @ q.to_matrix().to_4x4())
    collar = make_obj(f"DX_socket_collar_{side}", collar_mesh, M_STEEL, shade_smooth=True)
    parent_to_bone(collar, chest_bone)
    # shape keys: Basis + socket_open (radial flare, no pop on grow)
    collar.shape_key_add(name="Basis", from_mix=False)
    sk = collar.shape_key_add(name="socket_open", from_mix=False)
    for i, v in enumerate(collar_mesh.vertices):
        p = v.co - s
        radial = p - adir * p.dot(adir)
        sk.data[i].co = v.co + radial * 0.45
    # stump cap dome, hidden at scale ~0 until detach.
    # Authored RELATIVE to the socket with object location AT the socket, so
    # scaling the object grows/shrinks it around the socket point.
    bm2 = bmesh.new()
    bmesh.ops.create_uvsphere(bm2, u_segments=12, v_segments=6, radius=0.13)
    M2 = Matrix.Translation(adir * 0.02) @ q.to_matrix().to_4x4()
    for v in bm2.verts:
        v.co = M2 @ v.co
    cap_mesh = bpy.data.meshes.new(f"DX_stump_cap_{side}_mesh")
    bm2.to_mesh(cap_mesh)
    bm2.free()
    cap = make_obj(f"DX_stump_cap_{side}", cap_mesh, M_DARK, shade_smooth=True)
    cap.location = s
    parent_to_bone(cap, chest_bone)
    cap.scale = (0.001, 0.001, 0.001)

# ---------------------------------------------------------------- gyro controllers (world-space)
for side in ("L", "R"):
    e = bpy.data.objects.new(f"gyro_{side}", None)
    e.empty_display_type = "SPHERE"
    e.empty_display_size = 0.12
    S.collection.objects.link(e)
    e.location = sockets[side] + Vector((0.35 if side == "L" else -0.35, -0.15, 0.55))

# ---------------------------------------------------------------- ground + lights + camera (FRONT = +Y)
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
gnd = bpy.context.object
gnd.name = "DX_ground"
gnd.data.materials.append(mat("DX_ground", (0.09, 0.09, 0.10), 0.9, 0.0))

def light(name, typ, loc, energy, size=1.0):
    bpy.ops.object.light_add(type=typ, location=loc)
    l = bpy.context.object
    l.name = name
    l.data.energy = energy
    if typ == "AREA":
        l.data.size = size
    return l

light("DX_key", "AREA", (3, 4, 5), 900, 3.0)
light("DX_fill", "AREA", (-4, 2, 3), 350, 2.0)
light("DX_rim", "SPOT", (0, -5, 4), 1200)

bpy.ops.object.empty_add(location=(0, 0, 1.1))
orb = bpy.context.object
orb.name = "cam_orbiter"
bpy.ops.object.camera_add(location=(2.4, 3.8, 1.7))
cam = bpy.context.object
cam.name = "cam_orbit"
cam.data.lens = 45
cam.parent = orb
cam.parent_type = "OBJECT"
cam.matrix_parent_inverse = orb.matrix_world.inverted()
bpy.ops.object.empty_add(location=(0, 0, 1.0))
tgt = bpy.context.object
tgt.name = "cam_target"
c = cam.constraints.new("TRACK_TO")
c.target = tgt
c.track_axis = "TRACK_NEGATIVE_Z"
c.up_axis = "UP_Y"
S.camera = cam

# ---------------------------------------------------------------- extra-arm parts: standard parenting
# (No pivots — object scale does not render on bone-parented objects in
#  Blender 4.0.2 headless, so retract uses hide_render instead of scale.)
print("extra-arm parts use standard parenting (no pivots)")

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/03_meshed.blend")
print("STAGE3 DONE v2 — objects:", len([o for o in bpy.data.objects if o.name.startswith('DX_')]))
