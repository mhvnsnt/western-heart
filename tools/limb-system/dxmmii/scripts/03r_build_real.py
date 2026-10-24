# Stage 03r — build the REAL DXMMII mechanical body on the fitted rig.
# - Import dxmmii_plain.glb, rotate to Rigify convention (Rz-90)
# - Separate loose fragments; bisect main-arm/torso straddlers at x=+-0.10
# - Assign fragments to DEF bones (explicit axial rules for arms/legs/head,
#   nearest-bone for torso). Extra-arm fragments are topologically separate
#   (verified: 0 straddlers) -> clean detach.
# - Join per bone -> DXR_* parts; parent with FIXED tail-based Pinv.
# - Extra-arm parts: origin at socket, "retract" shape key (collapse to interior).
# - Socket tube-collars + stump caps (shape-key hidden) on the chest.
# - Gyro empties. Pinv regression check (<1e-4 mm).
import bpy, math, json
from collections import defaultdict
from mathutils import Vector, Matrix

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
rig = bpy.data.objects["DXMMII_rig"]
S = bpy.context.scene
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
bpy.context.view_layer.update()

# ---------------------------------------------------------------- import+rotate
before = set(S.objects)
bpy.ops.import_scene.gltf(filepath='/home/hatch/workspace/dxmmii-limbs/viz/dxmmii_plain.glb')
R = Matrix.Rotation(math.radians(-90), 4, 'Z')
imported = [o for o in S.objects if o not in before and o.type == 'MESH']
assert imported, "GLB import produced no meshes"
print("imported meshes:", len(imported), flush=True)
for o in imported:
    o.data.transform(R)
for o in imported:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')

def all_parts():
    # only the imported Tripo fragments (never Rigify WGT widgets)
    return [o for o in S.objects if o.type == 'MESH' and o.name.startswith('tripo')]

def cent(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(bb, Vector((0, 0, 0))) / 8

def bbox(o):
    xs, ys, zs = [], [], []
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        xs.append(w.x); ys.append(w.y); zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

# ------------------------------------------------- bisect main-arm straddlers
# Main arms are topologically connected to the torso (verified). Split at x=+-0.10
# in the mid-arm z-band so arm-side verts can follow arm FK without tearing.
n_bisect = 0
for o in all_parts():
    bb = bbox(o)
    if bb[4] < 0.32 and bb[5] > 0.08:  # overlaps mid-arm z-band
        px = None
        if bb[0] < 0.10 < bb[1] and bb[0] > -0.05:
            px = 0.10
        elif bb[0] < -0.10 < bb[1] and bb[1] < 0.05:
            px = -0.10
        if px is not None:
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=(px, 0, 0), plane_no=(1, 0, 0))
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
            n_bisect += 1
print("bisected straddlers:", n_bisect, flush=True)
parts = all_parts()
print("fragments now:", len(parts), flush=True)

# ---------------------------------------------------------------- assignment
def bone_ax_range(bn, ax):
    b = rig.data.bones[bn]
    h, t = b.head_local[ax], b.tail_local[ax]
    return (min(h, t), max(h, t))

XARM = {'L': ['DEF-upper_arm.x.L', 'DEF-forearm.x.L', 'DEF-hand.x.L'],
        'R': ['DEF-upper_arm.x.R', 'DEF-forearm.x.R', 'DEF-hand.x.R']}
ARM = {'L': ['DEF-upper_arm.L', 'DEF-forearm.L', 'DEF-hand.L'],
       'R': ['DEF-upper_arm.R', 'DEF-forearm.R', 'DEF-hand.R']}
LEGB = {'L': ['DEF-thigh.L', 'DEF-thigh.L.001', 'DEF-shin.L', 'DEF-shin.L.001', 'DEF-foot.L'],
        'R': ['DEF-thigh.R', 'DEF-thigh.R.001', 'DEF-shin.R', 'DEF-shin.R.001', 'DEF-foot.R']}
def bone_ax_range_abs(bn, ax):
    b = rig.data.bones[bn]
    h, t = abs(b.head_local[ax]), abs(b.tail_local[ax])
    return (min(h, t), max(h, t))

xarm_xr = {s: [bone_ax_range_abs(b, 0) for b in XARM[s]] for s in 'LR'}
arm_xr = {s: [bone_ax_range_abs(b, 0) for b in ARM[s]] for s in 'LR'}
leg_zr = {s: [bone_ax_range(b, 2) for b in LEGB[s]] for s in 'LR'}
TORSO_BONES = ['DEF-spine', 'DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003',
               'DEF-spine.004', 'DEF-spine.005', 'DEF-spine.006',
               'DEF-shoulder.L', 'DEF-shoulder.R']
TORSO_SEG = {}
for bn in TORSO_BONES:
    b = rig.data.bones[bn]
    TORSO_SEG[bn] = (Vector(b.head_local), Vector(b.tail_local))

def nearest_torso(c):
    best, bd = None, 1e9
    for bn, (h, t) in TORSO_SEG.items():
        d = (c - h)
        seg = t - h
        tt = max(0.0, min(1.0, d.dot(seg) / seg.dot(seg)))
        dist = (h + seg * tt - c).length
        if dist < bd:
            bd, best = dist, bn
    return best

def axial_pick(cval, bones, ranges, tol=0.006):
    for bn, (lo, hi) in zip(bones, ranges):
        if lo - tol <= cval <= hi + tol:
            return bn
    return None

def is_xarm_zone(c, ax):
    # PROVEN two-zone spatial filter (viz/prep.py — TRANSFER FIX 2026-10-16,
    # defect 3). prep.py ran on the UNROTATED glb where lateral=|y|; 03r
    # rotates Rz(-90) so the lateral axis here is |x|.
    if c.z > 0.38:
        return ax >= 0.09
    if c.z > 0.33:
        return ax > 0.15
    return False

def dist_to_box(c, b, pad=0.04):
    # distance from centroid c to padded bbox b (prep.py)
    dx = max(b[0] - pad - c.x, 0.0, c.x - (b[1] + pad))
    dy = max(b[2] - pad - c.y, 0.0, c.y - (b[3] + pad))
    dz = max(b[4] - pad - c.z, 0.0, c.z - (b[5] + pad))
    return (dx * dx + dy * dy + dz * dz) ** 0.5

assign = {}
counts = defaultdict(int)
xarm_frag_box = {}  # per-side bbox of two-zone arm fragments (for proximity pass)
for o in parts:
    c = cent(o)
    side = 'L' if c.x >= 0 else 'R'
    bn = None
    ax = abs(c.x)
    if is_xarm_zone(c, ax):
        # extra arms: assign to the chain segment by |x|
        bn = axial_pick(ax, XARM[side], xarm_xr[side])
        if bn is None:
            bn = XARM[side][2] if ax > xarm_xr[side][2][1] else XARM[side][0]
    elif abs(c.x) < 0.075 and abs(c.y) < 0.07 and 0.24 <= c.z <= 0.44:
        bn = 'DEF-spine.006'  # head
    elif 0.08 < c.z < 0.32 and ax >= 0.095:
        # main arms (bisected clean)
        bn = axial_pick(ax, ARM[side], arm_xr[side]) or ARM[side][0]
    elif c.z < -0.02 and 0.02 < ax < 0.16:
        # legs: match the DEF z-segmentation exactly (kills the .001 gaps)
        bn = None
        zr = leg_zr[side]
        for b, (lo, hi) in zip(LEGB[side], zr):
            if lo - 0.006 <= c.z <= hi + 0.006:
                bn = b
                break
        if bn is None:
            bn = LEGB[side][-1] if c.z < zr[-1][0] else LEGB[side][0]
    if bn is None:
        bn = nearest_torso(c)
    assign[o] = bn
    counts[bn] += 1

# defect 3 proximity pass (prep.py): small fragments near the arm boxes that
# the zone filter missed get pulled into the extra-arm chains. Only fragments
# in the extra-arm z-band are eligible (never legs/main-arm/body bits).
for s in 'LR':
    xs, ys, zs = [], [], []
    for o, bn in assign.items():
        if bn in XARM[s]:
            bb = bbox(o)
            xs += [bb[0], bb[1]]; ys += [bb[2], bb[3]]; zs += [bb[4], bb[5]]
    if xs:
        xarm_frag_box[s] = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
n_prox = 0
for o in parts:
    c = cent(o)
    if assign[o] in (XARM['L'] + XARM['R']):
        continue
    if c.z < 0.30 or len(o.data.vertices) >= 5000:
        continue
    side = 'L' if c.x >= 0 else 'R'
    d = dist_to_box(c, xarm_frag_box[side])
    if d < 0.001:
        obn = assign[o]
        counts[obn] -= 1
        ax = abs(c.x)
        bn = axial_pick(ax, XARM[side], xarm_xr[side])
        if bn is None:
            bn = XARM[side][2] if ax > xarm_xr[side][2][1] else XARM[side][0]
        assign[o] = bn
        counts[bn] += 1
        n_prox += 1
print("proximity pass moved:", n_prox, flush=True)

print("assignment counts:", dict(counts), flush=True)
# sanity: every extra-arm bone got fragments
for s in 'LR':
    for bn in XARM[s] + ARM[s]:
        assert counts[bn] > 0, f"NO FRAGMENTS for {bn}"
    for bn in LEGB[s]:
        assert counts[bn] > 0, f"NO FRAGMENTS for {bn}"
print("all arm/leg bones have fragments", flush=True)

# ---------------------------------------------------------------- join per bone
PN = {
    'DEF-upper_arm.x.L': 'DXR_xarm_L_upper', 'DEF-forearm.x.L': 'DXR_xarm_L_fore',
    'DEF-hand.x.L': 'DXR_xarm_L_hand',
    'DEF-upper_arm.x.R': 'DXR_xarm_R_upper', 'DEF-forearm.x.R': 'DXR_xarm_R_fore',
    'DEF-hand.x.R': 'DXR_xarm_R_hand',
    'DEF-upper_arm.L': 'DXR_arm_L_upper', 'DEF-forearm.L': 'DXR_arm_L_fore',
    'DEF-hand.L': 'DXR_arm_L_hand',
    'DEF-upper_arm.R': 'DXR_arm_R_upper', 'DEF-forearm.R': 'DXR_arm_R_fore',
    'DEF-hand.R': 'DXR_arm_R_hand',
    'DEF-thigh.L': 'DXR_leg_L_thigh', 'DEF-thigh.L.001': 'DXR_leg_L_thigh2',
    'DEF-shin.L': 'DXR_leg_L_shin', 'DEF-shin.L.001': 'DXR_leg_L_shin2',
    'DEF-foot.L': 'DXR_leg_L_foot',
    'DEF-thigh.R': 'DXR_leg_R_thigh', 'DEF-thigh.R.001': 'DXR_leg_R_thigh2',
    'DEF-shin.R': 'DXR_leg_R_shin', 'DEF-shin.R.001': 'DXR_leg_R_shin2',
    'DEF-foot.R': 'DXR_leg_R_foot',
    'DEF-spine': 'DXR_pelvis', 'DEF-spine.001': 'DXR_belly',
    'DEF-spine.002': 'DXR_chest', 'DEF-spine.003': 'DXR_uchest',
    'DEF-spine.004': 'DXR_neck', 'DEF-spine.005': 'DXR_neck2',
    'DEF-spine.006': 'DXR_head',
    'DEF-shoulder.L': 'DXR_clav_L', 'DEF-shoulder.R': 'DXR_clav_R',
}
by_bone = defaultdict(list)
for o, bn in assign.items():
    by_bone[bn].append(o)

manifest = {}
for bn, objs in by_bone.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    p = bpy.context.view_layer.objects.active
    p.name = PN[bn]
    manifest[p.name] = bn
    print(f"joined {p.name}: {len(objs)} frags, {len(p.data.vertices)} verts", flush=True)

# TRANSFER FIX 2026-10-16 defect 1: relocate the extra-arm parts from the
# Tripo floating positions (by the head) to the upper-torso sockets.
# D = new socket - old socket; applied as a rigid world translation BEFORE
# parenting, so the tail-based Pinv is computed for the relocated rest state.
S_OLD = {'L': Vector((0.105, 0.037, 0.435)), 'R': Vector((-0.105, 0.037, 0.435))}
for s in 'LR':
    s_new = Vector(rig.data.bones[f'DEF-upper_arm.x.{s}'].head_local)
    d = s_new - S_OLD[s]
    for bn in XARM[s]:
        bpy.data.objects[PN[bn]].location += d
    print(f"relocated extra-arm parts ({s}) by {[round(v, 4) for v in d]}", flush=True)

# ------------------------------------------------- extra-arm prep (BEFORE parenting)
# Extra-arm parts get their origin at the socket (correct scale pivot for the
# game) and a "retract" shape key (mesh-level collapse, since object scale
# does not render on bone-parented objects in Blender 4.0.2 headless).
S_surf = {s: Vector(rig.data.bones[f'DEF-upper_arm.x.{s}'].head_local) for s in 'LR'}
# retract target: interior point inside the torso near the (relocated) socket
S_in = {'L': Vector((0.020, 0.010, 0.280)), 'R': Vector((-0.020, 0.010, 0.280))}

def set_origin_to(ob, p):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    S.cursor.location = p
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

XPARTS = {'L': ['DXR_xarm_L_upper', 'DXR_xarm_L_fore', 'DXR_xarm_L_hand'],
          'R': ['DXR_xarm_R_upper', 'DXR_xarm_R_fore', 'DXR_xarm_R_hand']}
for s in 'LR':
    for pname in XPARTS[s]:
        ob = bpy.data.objects[pname]
        set_origin_to(ob, S_surf[s])
        ob.rotation_mode = 'QUATERNION'
        ob.shape_key_add(name='Basis', from_mix=False)
        sk = ob.shape_key_add(name='retract', from_mix=False)
        tgt = S_in[s] - S_surf[s]
        sk.data.foreach_set('co', [tgt.x, tgt.y, tgt.z] * len(ob.data.vertices))
    print(f"extra-arm parts ready ({s}): origin@socket, retract shape key", flush=True)

# ---------------------------------------------------------------- parenting (FIXED tail-based Pinv)
def parent_to_bone(ob, bone_name):
    rb = rig.data.bones[bone_name]
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = bone_name
    M_rest = Matrix(rb.matrix_local)
    tail = Vector(rb.tail_local)
    X_rest = Matrix.Translation(tail) @ M_rest.to_3x3().to_4x4()
    ob.matrix_parent_inverse = (rig.matrix_world @ X_rest).inverted()

def deps_update():
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    return dg

def true_world_of(ob):
    dg = deps_update()
    oe = ob.evaluated_get(dg)
    B = Matrix(oe.matrix_basis)
    if ob.parent_type == "BONE" and ob.parent and ob.parent.type == "ARMATURE":
        P = Matrix(rig.evaluated_get(dg).pose.bones[ob.parent_bone].matrix)
        db = rig.data.bones[ob.parent_bone]
        L = (Vector(db.tail_local) - Vector(db.head_local)).length
        ptail = P @ Vector((0, L, 0))
        X = Matrix.Translation(ptail) @ P.to_3x3().to_4x4()
        return rig.matrix_world @ X @ Matrix(ob.matrix_parent_inverse) @ B
    return Matrix(oe.matrix_world)

def centroid_W(ob, W):
    vs = [Vector(v.co) for v in ob.data.vertices]
    return W @ (sum(vs, Vector((0, 0, 0))) / len(vs))

# Pinv regression check: world must not move when parenting is applied
max_dev = 0.0
for pname, bn in manifest.items():
    ob = bpy.data.objects[pname]
    pre = centroid_W(ob, Matrix(ob.matrix_world))
    parent_to_bone(ob, bn)
    post = centroid_W(ob, true_world_of(ob))
    dev = (post - pre).length * 1000.0
    max_dev = max(max_dev, dev)
print(f"Pinv regression check: max parenting deviation = {max_dev:.6f} mm", flush=True)
assert max_dev < 1e-3, "PINV REGRESSION"


def mat(name, rgb, rough=0.6, metallic=0.1):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m

M_STEEL = mat("DXR_steel", (0.42, 0.43, 0.45), 0.35, 0.8)
M_DARK = mat("DXR_dark", (0.12, 0.12, 0.13), 0.5, 0.3)

def make_obj(name, mesh, material=None, shade_smooth=False):
    ob = bpy.data.objects.new(name, mesh)
    S.collection.objects.link(ob)
    if material:
        mesh.materials.append(material)
    if shade_smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return ob

manifest['sockets'] = {s: [round(v, 4) for v in S_surf[s]] for s in 'LR'}
manifest['retract_interior'] = {s: [round(v, 4) for v in S_in[s]] for s in 'LR'}

# socket tube-collars (short open cylinder sleeve at the arm root, chest-parented)
import bmesh
for s in 'LR':
    sgn = 1 if s == 'L' else -1
    bm = bmesh.new()
    # open tube along X: circle in YZ plane extruded along X
    n = 20
    # TRANSFER FIX 2026-10-16: larger/longer collar so the socket visibly
    # bridges torso -> arm root (reads as the shoulder joint, no gap).
    r, x0, x1 = 0.070, S_surf[s].x - 0.035 * sgn, S_surf[s].x + 0.035 * sgn
    verts0, verts1 = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        y = S_surf[s].y + r * math.cos(a)
        z = S_surf[s].z + r * math.sin(a)
        verts0.append(bm.verts.new((x0, y, z)))
        verts1.append(bm.verts.new((x1, y, z)))
    bm.verts.ensure_lookup_table()
    for i in range(n):
        bm.faces.new((verts0[i], verts0[(i + 1) % n], verts1[(i + 1) % n], verts1[i]))
    bm.to_mesh(bm_mesh := bpy.data.meshes.new(f"DXR_socket_{s}_mesh"))
    bm.free()
    collar = make_obj(f"DXR_socket_{s}", bm_mesh, M_STEEL, shade_smooth=True)
    set_origin_to(collar, S_surf[s])
    parent_to_bone(collar, 'DEF-spine.003')
    collar.shape_key_add(name='Basis', from_mix=False)
    sk = collar.shape_key_add(name='socket_open', from_mix=False)
    for i, v in enumerate(collar.data.vertices):
        radial = Vector((0, v.co.y, v.co.z))
        sk.data[i].co = v.co + radial * 0.5
    print(f"collar {s} at {[round(v,3) for v in S_surf[s]]}", flush=True)

# stump caps (squashed dome disc, shape-key hidden, chest-parented)
for s in 'LR':
    sgn = 1 if s == 'L' else -1
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.055)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.35 + S_surf[s].x + 0.004 * sgn,
                       v.co.y + S_surf[s].y, v.co.z + S_surf[s].z))
    cap_mesh = bpy.data.meshes.new(f"DXR_stump_cap_{s}_mesh")
    bm.to_mesh(cap_mesh); bm.free()
    cap = make_obj(f"DXR_stump_cap_{s}", cap_mesh, M_DARK, shade_smooth=True)
    set_origin_to(cap, S_surf[s])
    parent_to_bone(cap, 'DEF-spine.003')
    cap.shape_key_add(name='Basis', from_mix=False)
    sk = cap.shape_key_add(name='hidden', from_mix=False)
    sk.data.foreach_set('co', [0.0, 0.0, 0.0] * len(cap.data.vertices))
    sk.value = 1.0  # start hidden
    print(f"stump cap {s} ready (hidden)", flush=True)

# gyro controllers (world-space)
manifest['gyro_home'] = {}
for s in 'LR':
    sgn = 1 if s == 'L' else -1
    e = bpy.data.objects.new(f"gyro_{s}", None)
    e.empty_display_type = "SPHERE"
    e.empty_display_size = 0.06
    S.collection.objects.link(e)
    home = S_surf[s] + Vector((sgn * 0.19, -0.08, 0.30))
    e.location = home
    manifest['gyro_home'][s] = [round(v, 4) for v in home]

with open('/home/hatch/workspace/dxmmii-limbs/dxrm_manifest.json', 'w') as fh:
    json.dump(manifest, fh, indent=1)
print("manifest saved", flush=True)

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/03_meshed_real.blend")
print("STAGE03R DONE")
