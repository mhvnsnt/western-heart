"""PANTERA entrance kit v1 — Blender scene build + render (v4: clean rebuild).
Blender 4.0.2 headless. Starts from pantera_rigged_working.blend
(rig rebuilt from glTF inverse bind matrices; deform verified identity at rest).
For the repaired v3 model (armpit de-bleed), point PANTERA_BLEND at
pantera_rigged_working_v3.blend (18/18 mesh weight hashes == v3 GLB).
Character faces -Y (verified). Cameras on -Y side. Armature animated directly.
Usage:
  blender -b -P build_v1.py -- --mode probe   # 4 frames/shot @50% -> /tmp/pantera-probe/
  blender -b -P build_v1.py -- --mode full    # 1500 frames 1920x1080 -> build/frames_v1/
All motion authored procedurally (GLB Walk/Run actions are empty; Idle unused).
Env overrides (Kaggle GPU lane):
  PANTERA_WH       kit root (default /home/hatch/workspace/wh-kit)
  PANTERA_KIT      kit dir (default $PANTERA_WH/wh/promo/pantera-entrance-v1)
  PANTERA_BLEND    .blend to open (default $PANTERA_WH/pantera_rigged_working.blend)
  PANTERA_TRON     titantron PNG (default $PANTERA_KIT/assets/titantron_plate_1920.png)
  PANTERA_FRAMES   frame output dir (default $PANTERA_KIT/build/frames_v1)
  PANTERA_DEVICE   CPU (default) | CUDA
  PANTERA_SAMPLES  samples override (default 8 probe / 16 full)
  PANTERA_F0/PANTERA_F1  render only this inclusive frame range (chunk renders)
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = "probe"
for i, a in enumerate(argv):
    if a == "--mode" and i + 1 < len(argv):
        MODE = argv[i + 1]

WH = os.environ.get("PANTERA_WH", "/home/hatch/workspace/wh-kit")
KIT = os.environ.get("PANTERA_KIT", WH + "/wh/promo/pantera-entrance-v1")
BLEND = os.environ.get("PANTERA_BLEND", WH + "/pantera_rigged_working.blend")
TRON_TEX = os.environ.get("PANTERA_TRON", KIT + "/assets/titantron_plate_1920.png")
FRAMES = os.environ.get("PANTERA_FRAMES", KIT + "/build/frames_v1")
PROBE_DIR = os.environ.get("PANTERA_PROBE_DIR", "/tmp/pantera-probe")
# Kaggle chunk overrides: render only [PANTERA_F0, PANTERA_F1] (inclusive).
# Scene is still built+baked in full (procedural, deterministic).
CHUNK_F0 = int(os.environ["PANTERA_F0"]) if "PANTERA_F0" in os.environ else None
CHUNK_F1 = int(os.environ["PANTERA_F1"]) if "PANTERA_F1" in os.environ else None
# Compute device: "CPU" (default) or "CUDA" (Kaggle T4)
DEVICE = os.environ.get("PANTERA_DEVICE", "CPU").upper()
SAMPLES = int(os.environ.get("PANTERA_SAMPLES", "0")) or (8 if MODE == "probe" else 16)
FPS, F_END = 30, 1499

SHOTS = [
    ("P1_SIL", 0, 179), ("P2_CARD", 180, 419), ("P3_WALK", 420, 659),
    ("P4_TAIL", 660, 899), ("P5_GRAPPLE", 900, 1139), ("P6_WIDE", 1140, 1319),
    ("P7_HOLD", 1320, 1379), ("END_CARD", 1380, 1499),
]

bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
if DEVICE == "CUDA":
    try:
        cprefs = bpy.context.preferences.addons['cycles'].preferences
        cprefs.compute_device_type = 'CUDA'
        cprefs.get_devices()
        gpus = [d for d in cprefs.devices if d.type == 'CUDA']
        for d in cprefs.devices:
            d.use = (d.type == 'CUDA')
        if gpus:
            sc.cycles.device = 'GPU'
            print("CUDA devices:", [d.name for d in gpus], flush=True)
        else:
            sc.cycles.device = 'CPU'
            print("PANTERA_DEVICE=CUDA but no CUDA device found; using CPU", flush=True)
    except Exception as e:
        sc.cycles.device = 'CPU'
        print("CUDA setup failed:", e, "; using CPU", flush=True)
else:
    sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3
sc.cycles.min_bounces = 1
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_depth = '8'
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 0, F_END
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = 25 if MODE == "probe" else 50
os.makedirs(PROBE_DIR if MODE == "probe" else FRAMES, exist_ok=True)

arm = next(o for o in sc.objects if o.type == 'ARMATURE')
print("using armature:", arm.name, len(arm.data.bones), "bones", flush=True)

def bw(name):
    return (arm.matrix_world @ arm.pose.bones[name].head).copy()

# Keep armature at origin, no scaling for probe (1.75m is fine)
# Character faces -Y (verified)
CHAR_POS = (0, 0, 0)
arm.location = CHAR_POS
bpy.context.view_layer.update()

thigh = (bw('LeftLeg') - bw('LeftUpLeg')).length
shin = (bw('LeftFoot') - bw('LeftLeg')).length
LEGL = thigh + shin
print("leg length:", round(LEGL, 3), flush=True)
print("arm at:", [round(v,2) for v in arm.matrix_world.translation], flush=True)

# ---------------- procedural actions ----------------
STRIDE = 0.62
AMP = math.asin(min(0.9, STRIDE / (2 * LEGL)))

def walk_pose(f01):
    th = 2 * math.pi * f01
    p = {}
    for side, ph in (('Left', 0.0), ('Right', math.pi)):
        sw = AMP * math.sin(th + ph)
        knee = -0.85 * max(0.0, math.sin(th + ph + 2.1))
        p[f'{side}UpLeg'] = (None, (sw, 0, 0))
        p[f'{side}Leg'] = (None, (knee, 0, 0))
        p[f'{side}Foot'] = (None, (-(sw + knee) * 0.75, 0, 0))
        p[f'{side}ToeBase'] = (None, (0.25 * max(0.0, math.sin(th + ph + 2.6)), 0, 0))
    for side, ph in (('Left', math.pi), ('Right', 0.0)):
        p[f'{side}Shoulder'] = (None, (0.32 * math.sin(th + ph), 0, 0.06))
        p[f'{side}Arm'] = (None, (0.1 * math.sin(th + ph), 0, 0))
        p[f'{side}ForeArm'] = (None, (-0.35 - 0.1 * math.sin(th + ph), 0, 0))
    p['Hips'] = ((0, 0, -0.035 * (0.5 - 0.5 * math.cos(2 * th))), (0, 0.04 * math.sin(th), 0))
    p['Spine'] = (None, (0.06, 0.05 * math.sin(th), 0))
    p['Spine1'] = (None, (0.04, -0.06 * math.sin(th), 0))
    p['Head'] = (None, (-0.05, 0, 0))
    return p

def sway_fn(base, amp=1.0, period=180.0):
    def fn(f):
        th = 2 * math.pi * f / period
        p = {}
        for bn, eul in base.items():
            p[bn] = (None, eul)
        sx, sy, sz = base.get('Spine', (0, 0, 0))
        p['Spine'] = (None, (sx + 0.03 * amp * math.sin(th), sy, sz))
        p['Hips'] = ((0, 0, 0.012 * amp * math.sin(th)), (0, 0, 0))
        return p
    return fn

CROUCH = {'Hips': (0, 0, 0), 'Spine': (0.42, 0, 0), 'Spine1': (0.22, 0, 0),
          'LeftUpLeg': (-0.55, 0, 0.08), 'RightUpLeg': (-0.55, 0, -0.08),
          'LeftLeg': (0.85, 0, 0), 'RightLeg': (0.85, 0, 0),
          'LeftFoot': (-0.3, 0, 0), 'RightFoot': (-0.3, 0, 0),
          'Head': (-0.35, 0, 0)}
GRAPPLE = dict(CROUCH)
GRAPPLE.update({'LeftShoulder': (-1.2, 0, -0.3), 'RightShoulder': (-1.2, 0, 0.3),
                'LeftArm': (-0.3, 0, 0), 'RightArm': (-0.3, 0, 0),
                'LeftForeArm': (-0.55, 0, 0), 'RightForeArm': (-0.55, 0, 0),
                'Head': (-0.2, 0, 0)})
CRUCIFIX = {'LeftShoulder': (0, 0, 1.5), 'RightShoulder': (0, 0, -1.5),
            'LeftArm': (0, 0, 0.12), 'RightArm': (0, 0, -0.12),
            'LeftForeArm': (0, 0, 0), 'RightForeArm': (0, 0, 0),
            'Spine': (-0.14, 0, 0), 'Spine1': (-0.06, 0, 0),
            'Head': (-0.18, 0, 0), 'Hips': (0, 0, 0)}
RISE = {'Hips': (0, 0, -0.12), 'Spine': (0.3, 0, 0), 'Spine1': (0.15, 0, 0),
        'LeftUpLeg': (-0.25, 0, 0), 'RightUpLeg': (-0.25, 0, 0),
        'LeftLeg': (0.4, 0, 0), 'RightLeg': (0.4, 0, 0),
        'LeftShoulder': (-0.5, 0, -0.4), 'RightShoulder': (-0.5, 0, 0.4)}

def bake_exact(name, f0, f1, fn, step=2):
    act = bpy.data.actions.new(name)
    ad = arm.animation_data_create()
    ad.action = act
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    for b in arm.pose.bones:
        b.rotation_mode = 'XYZ'
    for f in range(f0, f1 + 1, step):
        pose = fn(f)
        sc.frame_set(f)
        for bn, (loc, rot) in pose.items():
            pb = arm.pose.bones.get(bn)
            if not pb:
                continue
            if rot is not None:
                pb.rotation_euler = rot
                pb.keyframe_insert(data_path="rotation_euler", frame=f)
            if loc is not None:
                pb.location = loc
                pb.keyframe_insert(data_path="location", frame=f)
    bpy.ops.object.mode_set(mode='OBJECT')
    ad.action = None
    return act

WALK_CYC = 24
def walk_fn(f):
    cyc = ((f - 420) % WALK_CYC) / WALK_CYC
    return walk_pose(cyc)

def rise_fn_abs(f):
    f01 = (f - 180) / 60.0
    p = {}
    for bn in set(RISE) | set(CROUCH):
        r = RISE.get(bn, (0, 0, 0)); c = CROUCH.get(bn, (0, 0, 0))
        e = tuple(c[i] + (r[i] - c[i]) * (1 - f01) for i in range(3))
        p[bn] = (None, e)
    return p

BAKED = [
    ("KIT_Silence", 0, 179, sway_fn(CROUCH, 0.5)),
    ("KIT_Rise", 180, 239, rise_fn_abs),
    ("KIT_StanceA", 240, 419, sway_fn({}, 0.8)),
    ("KIT_Walk", 420, 659, walk_fn),
    ("KIT_Crouch", 660, 899, sway_fn(CROUCH, 1.0)),
    ("KIT_Grapple", 900, 1009, sway_fn(GRAPPLE, 1.0)),
    ("KIT_DashIdle", 1010, 1139, sway_fn(CROUCH, 1.2)),
    ("KIT_Crucifix", 1140, 1499, sway_fn(CRUCIFIX, 0.7)),
]
# Bake everything into ONE action (no NLA - more reliable)
master = bpy.data.actions.new("KIT_Master")
ad = arm.animation_data_create()
ad.action = master
ad.use_nla = False
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for b in arm.pose.bones:
    b.rotation_mode = 'XYZ'
for name, f0, f1, fn in BAKED:
    print("baking", name, f0, f1, flush=True)
    for f in range(f0, f1 + 1, 2):
        pose = fn(f)
        sc.frame_set(f)
        for bn, (loc, rot) in pose.items():
            pb = arm.pose.bones.get(bn)
            if not pb:
                continue
            if rot is not None:
                pb.rotation_euler = rot
                pb.keyframe_insert(data_path="rotation_euler", frame=f)
            if loc is not None:
                pb.location = loc
                pb.keyframe_insert(data_path="location", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("master action baked: 0-1499", flush=True)

# Root motion: DISABLED for probe (character stays at origin)
# (Walk pose still plays, but no translation)
print("root motion disabled (probe)", flush=True)

# ---------------- tail (bones added to main armature) ----------------
bpy.context.view_layer.update()
# Tail in arm-local: character faces -Y, back = +Y
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
hips_local = arm.data.edit_bones['Hips'].head.copy()
back = Vector((0, 1, 0))
tail_base = hips_local + back * 0.16
tail_base.z -= 0.02
seg = 0.17
prev = None
dirs = []
tail_bones = []
for i in range(5):
    b = arm.data.edit_bones.new(f"tail_{i+1:02d}")
    d = (back * (0.75 - 0.12 * i) + Vector((0, 0, -0.45 - 0.06 * i))).normalized()
    dirs.append(d)
    b.head = tail_base + d * seg * i
    b.tail = tail_base + d * seg * (i + 1)
    if prev:
        b.parent = prev
    else:
        b.parent = arm.data.edit_bones['Hips']
    prev = b
    tail_bones.append(b.name)
bpy.ops.object.mode_set(mode='OBJECT')
# Tail mesh via curve (in arm-local, parented to arm)
curve = bpy.data.curves.new("TailCurve", type='CURVE')
spline = curve.splines.new('BEZIER')
spline.bezier_points.add(5)
for i in range(6):
    bp = spline.bezier_points[i]
    bp.co = tail_base + dirs[min(i, 4)] * seg * i
    bp.handle_left_type = bp.handle_right_type = 'AUTO'
curve.bevel_depth = 0.045
cobj = bpy.data.objects.new("TailMesh", curve)
sc.collection.objects.link(cobj)
cobj.parent = arm
cobj.matrix_parent_inverse = Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
cobj.select_set(True)
bpy.context.view_layer.objects.active = cobj
bpy.context.view_layer.update()
bpy.ops.object.convert(target='MESH')
tail_mesh = bpy.context.view_layer.objects.active
# Weight tail mesh to tail bones (simple: all verts to tail_01, gradient)
tail_mesh.modifiers.new("Arm", 'ARMATURE').object = arm
tm = bpy.data.materials.new("TailFur")
tm.use_nodes = True
tm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1)
tail_mesh.data.materials.append(tm)
# Create vertex groups for tail bones
for i, bn in enumerate(tail_bones):
    vg = tail_mesh.vertex_groups.new(name=bn)
    # Simple weighting: all verts get weight based on position along tail
    for v in tail_mesh.data.vertices:
        # Weight falls off along tail length
        w = max(0, 1.0 - abs(v.co.z - (tail_base.z - i * seg * 0.5)) / (seg * 2))
        if w > 0.01:
            vg.add([v.index], w, 'REPLACE')
# Tail animation: slow circles (signature), bigger during P4
# (baked into master action)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for bn in tail_bones:
    arm.pose.bones[bn].rotation_mode = 'XYZ'
for f in range(0, 1500, 4):
    amp, lift = (1.9, 0.55) if 660 <= f <= 899 else (1.0, 0.0)
    for i, bn in enumerate(tail_bones):
        pb = arm.pose.bones[bn]
        ph = 2 * math.pi * f / 180.0 + i * 0.65
        a = (0.10 + 0.11 * i) * amp
        pb.rotation_euler = (a * math.sin(ph) - lift * (0.25 + 0.15 * i), 0, a * math.cos(ph) * 0.8)
        pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("tail built + animated", flush=True)

# ---------------- arena ----------------
def mat_emit(name, color, strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = strength
    return m

# Ground: dark with ember cracks
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
gnd = bpy.context.active_object
gm = bpy.data.materials.new("Ground"); gm.use_nodes = True
nt = gm.node_tree; bsdf = nt.nodes["Principled BSDF"]
noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 6.0
cram = nt.nodes.new("ShaderNodeValToRGB")
cram.color_ramp.elements[0].color = (0.02, 0.015, 0.015, 1)
cram.color_ramp.elements[1].color = (0.55, 0.12, 0.02, 1)
cram.color_ramp.elements[0].position = 0.55
nt.links.new(noise.outputs["Fac"], cram.inputs["Fac"])
nt.links.new(cram.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(cram.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 0.7
gnd.data.materials.append(gm)

# Titantron at (0, 8, 5), facing -Y (toward character/camera at origin)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 8, 5))
tron = bpy.context.active_object
tron.scale = (11, 6.2, 1)
tron.rotation_euler = (math.pi / 2, 0, 0)  # face -Y
tm = bpy.data.materials.new("TronMat"); tm.use_nodes = True
nt = tm.node_tree; bsdf = nt.nodes["Principled BSDF"]
if os.path.exists(TRON_TEX):
    img = bpy.data.images.load(TRON_TEX)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.8
    print("tron texture loaded", flush=True)
else:
    bsdf.inputs["Emission Color"].default_value = (0.12, 0.02, 0.01, 1)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    print("tron texture MISSING - placeholder", flush=True)
tron.data.materials.append(tm)

# Tron frame bar
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 7.8, 11.4))
bar = bpy.context.active_object
bar.scale = (11.5, 0.3, 1)
bar.rotation_euler = (math.pi / 2, 0, 0)
bar.data.materials.append(mat_emit("TronBar", (0.8, 0.1, 0.05, 1), 2.0))

# Ember particles (small icosphere at character)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.03, location=(0, 0, 1))
ember = bpy.context.active_object
em = bpy.data.materials.new("Ember"); em.use_nodes = True
em.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.3, 0.05, 1)
em.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.0
ember.data.materials.append(em)
ember.modifiers.new("Part", 'PARTICLE_SYSTEM')
ps = ember.particle_systems[0]
ps.settings.count = 200
ps.settings.lifetime = 120
ps.settings.frame_start, ps.settings.frame_end = 0, 1499
ps.settings.emit_from = 'VOLUME'
ps.settings.physics_type = 'NEWTON'
ps.settings.normal_factor = 0.3
ps.settings.factor_random = 0.5
# Emitter is a small volume; particles spread via velocity, not object scale
ps.settings.render_type = 'HALO'

# ---------------- lights ----------------
bpy.ops.object.light_add(type='SPOT', location=(5, -7, 9))
key = bpy.context.active_object
key.data.energy = 3000
key.data.color = (1.0, 0.85, 0.7)
key.data.spot_size = 0.9
trk = key.constraints.new('TRACK_TO'); trk.target = arm
trk.track_axis = 'TRACK_NEGATIVE_Z'; trk.up_axis = 'UP_Y'

bpy.ops.object.light_add(type='AREA', location=(0, -6, 3))
fill = bpy.context.active_object
fill.data.energy = 800; fill.data.color = (1.0, 0.75, 0.55)
fill.data.size = 4
trk = fill.constraints.new('TRACK_TO'); trk.target = arm
trk.track_axis = 'TRACK_NEGATIVE_Z'; trk.up_axis = 'UP_Y'

bpy.ops.object.light_add(type='POINT', location=(-7, 5, 3.5))
rim1 = bpy.context.active_object
rim1.data.energy = 1200; rim1.data.color = (1.0, 0.25, 0.1)

bpy.ops.object.light_add(type='POINT', location=(7, 5, 3.5))
rim2 = bpy.context.active_object
rim2.data.energy = 1200; rim2.data.color = (1.0, 0.25, 0.1)

sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.005, 0.005, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3

# ---------------- camera (character at origin, faces -Y, front = -Y) ----------------
bpy.ops.object.camera_add(location=(0, -10, 6.5))
cam = bpy.context.active_object
sc.camera = cam
bpy.ops.object.empty_add(location=(0, 8, 5))
focus = bpy.context.active_object
trk = cam.constraints.new('TRACK_TO'); trk.target = focus
trk.track_axis = 'TRACK_NEGATIVE_Z'; trk.up_axis = 'UP_Y'

def cam_key(f, loc, foc):
    cam.location = loc; focus.location = foc
    cam.keyframe_insert(data_path="location", frame=f)
    focus.keyframe_insert(data_path="location", frame=f)

# P1: tron establishing
cam_key(0, (0, -12, 7.5), (0, 8, 5))
cam_key(179, (0, -9, 6.5), (0, 8, 4.5))
# P2: reveal (character at origin)
cam_key(180, (3.6, -7.8, 2.9), (0, 0, 1.4))
cam_key(419, (1.9, -5.5, 2.3), (0, 0, 1.3))
# P3: walk pose (no translation)
cam_key(420, (3.8, -4.8, 2.4), (0, 0, 1.3))
cam_key(659, (3.8, -4.8, 2.4), (0, 0, 1.3))
# P4: tail feature (orbit)
cam_key(660, (3.1, -3.4, 1.8), (0, -0.3, 1.0))
cam_key(899, (-3.1, -3.4, 1.8), (0, -0.3, 1.0))
# P5: grapple
cam_key(900, (6.6, -5.4, 1.3), (0, 0, 1.1))
cam_key(1139, (-6.6, -5.4, 1.3), (0, 0, 1.1))
# P6: crane up wide
cam_key(1140, (10.8, -12, 8.4), (0, 0, 1.5))
cam_key(1319, (6.6, -7.8, 3.8), (0, 0, 1.3))
# P7: quote close
cam_key(1320, (3.8, -5.6, 2.5), (0, 0, 1.3))
cam_key(1379, (3.1, -4.7, 2.3), (0, 0, 1.3))
# END: end card
cam_key(1380, (0, -15, 5.4), (0, 0, 2.0))
cam_key(1499, (0, -15, 5.4), (0, 0, 2.0))
for fc in list(cam.animation_data.action.fcurves) + list(focus.animation_data.action.fcurves):
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
print("cameras keyed", flush=True)

# ---------------- render ----------------
if MODE == "probe":
    for name, f0, f1 in SHOTS:
        for f in (f0, f0 + (f1 - f0) // 3, f0 + 2 * (f1 - f0) // 3, f1):
            sc.frame_set(f)
            sc.render.filepath = f"{PROBE_DIR}/{name}_f{f:05d}.png"
            bpy.ops.render.render(write_still=True)
            print("probe", name, f, flush=True)
else:
    rf0 = CHUNK_F0 if CHUNK_F0 is not None else 0
    rf1 = CHUNK_F1 if CHUNK_F1 is not None else F_END
    print(f"rendering frames {rf0}-{rf1} -> {FRAMES}", flush=True)
    for f in range(rf0, rf1 + 1):
        sc.frame_set(f)
        sc.render.filepath = f"{FRAMES}/f{f:05d}.png"
        bpy.ops.render.render(write_still=True)
        if f % 25 == 0:
            print("frame", f, flush=True)
print("DONE", MODE, flush=True)
