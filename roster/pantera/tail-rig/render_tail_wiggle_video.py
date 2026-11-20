"""Render Pantera tail-wiggle as a real motion clip (not stills).
Rebuilds the committed rig (5-bone chain) from the King FBX and animates it
with an FK traveling wave down the bones - the actual rig bones moving.
Pose bones are explicitly set to XYZ euler (Blender defaults pose bones to
quaternion, which silently ignores euler keyframes - the bug that froze the
first attempt).
Run: env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender -b --python render_tail_wiggle_video.py
"""
import bpy, math, os
from mathutils import Vector

HOME = os.path.expanduser("~")
KDIR = os.path.join(HOME, "workspace/game-reverse-engineering/tekken7/king")
PDIR = os.path.join(KDIR, "pantera")
OUTDIR = "/tmp/pantera_tail_frames"
os.makedirs(OUTDIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.fbx(filepath=os.path.join(KDIR, '5PMH7G85GYN7P71W3BD1V0249.fbx'))
for o in bpy.context.scene.objects:
    o.scale = tuple(s * 100 for s in o.scale)
bpy.context.view_layer.update()

# Pantera textures
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    for l in m.node_tree.links:
        if l.to_node.type == 'BSDF_PRINCIPLED' and l.to_socket.name == 'Base Color':
            node = l.from_node
            if node.type == 'TEX_IMAGE' and node.image:
                want = os.path.basename(node.image.filepath)
                plocal = os.path.join(PDIR, want)
                if os.path.exists(plocal):
                    node.image.filepath = plocal
                    node.image.reload()
            break

# Bounds
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
for o in meshes:
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        minx, maxx = min(minx, w.x), max(maxx, w.x)
        miny, maxy = min(miny, w.y), max(maxy, w.y)
        minz, maxz = min(minz, w.z), max(maxz, w.z)
cx, cy, cz = (minx + maxx) / 2, (miny + maxy) / 2, (minz + maxz) / 2
height = maxz - minz
widthx = maxx - minx
widthy = maxy - miny

# ---- Tail curve -> mesh (same geometry as committed rig) ----
# Owner-placed 2026-10-12 via Model 3D Placement Tool (X=-0.04 Y=0.045 Z=0 Scale=1):
# nudge -0.04 in X, +0.045 up from the auto surface point so the tail
# sits exactly on the body surface.
tail_base = Vector((maxx - widthx*0.06 - 0.04, cy + 0.0, 0.09 + 0.045))
L = height * 0.28

bpy.ops.curve.primitive_bezier_curve_add(location=tail_base)
curve_obj = bpy.context.active_object
curve_obj.name = "PanteraTailCurve"
spline = curve_obj.data.splines[0]
pts = [(0, 0, 0), (L * 0.25, L * 0.05, -L * 0.30), (L * 0.35, L * 0.35, -L * 0.55), (L * 0.25, L * 0.70, -L * 0.60)]
while len(spline.bezier_points) < 4:
    spline.bezier_points.add(1)
for i, (px, py, pz) in enumerate(pts):
    bp = spline.bezier_points[i]
    bp.co = (px, py, pz)
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
curve_obj.data.bevel_depth = height * 0.018
curve_obj.data.bevel_resolution = 6
curve_obj.data.fill_mode = 'FULL'

bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
taper_obj = bpy.context.active_object
taper_obj.name = "TailTaper"
tspline = taper_obj.data.splines[0]
while len(tspline.bezier_points) < 2:
    tspline.bezier_points.add(1)
tspline.bezier_points[0].co = (0, 1.0, 0)
tspline.bezier_points[0].handle_left_type = 'AUTO'
tspline.bezier_points[0].handle_right_type = 'AUTO'
tspline.bezier_points[1].co = (1.0, 0.12, 0)
tspline.bezier_points[1].handle_left_type = 'AUTO'
tspline.bezier_points[1].handle_right_type = 'AUTO'
curve_obj.data.taper_object = taper_obj
taper_obj.hide_render = True
taper_obj.hide_viewport = True

mat = bpy.data.materials.new("TailBlack")
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Roughness'].default_value = 0.6
curve_obj.data.materials.append(mat)

bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)
bpy.ops.object.convert(target='MESH')
tail_mesh = bpy.context.active_object
tail_mesh.name = "PanteraTail"
bpy.context.view_layer.update()

# ---- Armature: 5-bone chain (the committed rig) ----
tail_pts_world = [tail_base + Vector(p) for p in pts]

def sample_tail(t):
    seg = t * 3.0
    i = min(int(seg), 2)
    f = seg - i
    return tail_pts_world[i].lerp(tail_pts_world[i + 1], f)

N_BONES = 5
joint_pos = [sample_tail(i / N_BONES) for i in range(N_BONES + 1)]

bpy.ops.object.armature_add(enter_editmode=True, location=joint_pos[0])
arm_obj = bpy.context.active_object
arm_obj.name = "TailRig"
arm = arm_obj.data
arm.name = "TailRigData"
arm.edit_bones.remove(arm.edit_bones[0])
bones = []
for i in range(N_BONES):
    b = arm.edit_bones.new(f"tail_{i + 1:02d}")
    b.head = joint_pos[i]
    b.tail = joint_pos[i + 1]
    if i > 0:
        b.parent = bones[i - 1]
        b.use_connect = True
    bones.append(b)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.context.view_layer.objects.active = arm_obj
tail_mesh.select_set(True)
arm_obj.select_set(True)
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
bpy.context.view_layer.update()

# ---- FK traveling wave on the REAL rig bones ----
# CRITICAL: pose bones default to QUATERNION - must force XYZ euler,
# otherwise euler keyframes are silently ignored.
scene = bpy.context.scene
for b in arm_obj.pose.bones:
    b.rotation_mode = 'XYZ'

N_FRAMES = 72  # 3 seconds @ 24fps
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = N_FRAMES
for f in range(1, N_FRAMES + 1):
    scene.frame_set(f)
    for i in range(N_BONES):
        pb = arm_obj.pose.bones[f"tail_{i + 1:02d}"]
        # BASE ANCHORED (owner 2026-10-12): tail_01 (the attachment bone) does
        # not rotate - the tail extends from the body, so the attach point
        # stays fixed. Amplitude ramps up smoothly from bone 2 to the tip.
        # Phase lags down the chain: a traveling wave, like real
        # spring-physics follow-through.
        amp = 0.35 * (i / (N_BONES - 1)) ** 1.3 if i > 0 else 0.0
        pb.rotation_euler = (amp * math.sin(2 * math.pi * (f - 1) / N_FRAMES - i * 0.55), 0, 0)
        pb.keyframe_insert(data_path="rotation_euler", frame=f)
print("FK WAG KEYFRAMED ON RIG BONES")

# ---- Camera / light / render: back view ----
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = max(widthx, widthy, height) * 1.15
cam.location = (cx + height * 2, cy, cz)
cam.rotation_euler = (math.radians(90), 0, math.radians(90))
scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(cx - height, cy - height, cz + height * 2))
sun = bpy.context.active_object
sun.data.energy = 3.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

if not scene.world:
    scene.world = bpy.data.worlds.new("World")
world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)

for f in range(1, N_FRAMES + 1):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(OUTDIR, f"frame_{f:03d}.png")
    bpy.ops.render.render(write_still=True)
    if f % 24 == 0:
        print(f"RENDERED {f}/{N_FRAMES}")

print("ALL FRAMES DONE:", OUTDIR)
