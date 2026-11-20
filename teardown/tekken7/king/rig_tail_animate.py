"""Rig Pantera's tail with a bone chain and procedural cat-tail sway animation.
Renders 3 frames at different sway positions with UNIQUE filenames.
Run: blender -b --python rig_tail_animate.py
"""
import bpy, math, sys, os
from mathutils import Vector

KDIR = os.path.join(os.path.expanduser("~"), "workspace/game-reverse-engineering/tekken7/king")
PDIR = os.path.join(KDIR, "pantera")
VDIR = os.path.join(PDIR, "views")
os.makedirs(VDIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.join(KDIR, '5PMH7G85GYN7P71W3BD1V0249.fbx'))
for o in bpy.context.scene.objects:
    o.scale = tuple(s*100 for s in o.scale)
bpy.context.view_layer.update()

# Apply pantera textures
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for l in m.node_tree.links:
        if l.to_node.type=='BSDF_PRINCIPLED' and l.to_socket.name=='Base Color':
            node=l.from_node
            if node.type=='TEX_IMAGE' and node.image:
                want=os.path.basename(node.image.filepath)
                plocal=os.path.join(PDIR,want)
                if os.path.exists(plocal):
                    node.image.filepath=plocal; node.image.reload()
            break

# Compute bounds
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
minx=miny=minz=1e9; maxx=maxy=maxz=-1e9
for o in meshes:
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        minx,maxx=min(minx,w.x),max(maxx,w.x)
        miny,maxy=min(miny,w.y),max(maxy,w.y)
        minz,maxz=min(minz,w.z),max(maxz,w.z)
cx,cy,cz=(minx+maxx)/2,(miny+maxy)/2,(minz+maxz)/2
height=maxz-minz; widthx=maxx-minx; widthy=maxy-miny

# ---- Build tail curve (same shape as render_pantera.py) ----
tail_base = Vector((maxx - widthx*0.06, cy + 0.0, 0.09))
L = height*0.28

bpy.ops.curve.primitive_bezier_curve_add(location=tail_base)
curve_obj = bpy.context.active_object
curve_obj.name = "PanteraTailCurve"
spline = curve_obj.data.splines[0]
pts = [(0,0,0), (L*0.25,L*0.05,-L*0.30), (L*0.35,L*0.35,-L*0.55), (L*0.25,L*0.70,-L*0.60)]
while len(spline.bezier_points) < 4:
    spline.bezier_points.add(1)
for i, (px,py,pz) in enumerate(pts):
    bp = spline.bezier_points[i]
    bp.co = (px,py,pz)
    bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
curve_obj.data.bevel_depth = height*0.018
curve_obj.data.bevel_resolution = 6
curve_obj.data.fill_mode = 'FULL'

bpy.ops.curve.primitive_bezier_curve_add(location=(0,0,0))
taper_obj = bpy.context.active_object
taper_obj.name = "TailTaper"
tspline = taper_obj.data.splines[0]
while len(tspline.bezier_points) < 2:
    tspline.bezier_points.add(1)
tspline.bezier_points[0].co = (0,1.0,0)
tspline.bezier_points[0].handle_left_type='AUTO'; tspline.bezier_points[0].handle_right_type='AUTO'
tspline.bezier_points[1].co = (1.0,0.12,0)
tspline.bezier_points[1].handle_left_type='AUTO'; tspline.bezier_points[1].handle_right_type='AUTO'
curve_obj.data.taper_object = taper_obj
taper_obj.hide_render=True; taper_obj.hide_viewport=True

mat = bpy.data.materials.new("TailBlack")
mat.use_nodes=True
bsdf=mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value=(0.02,0.02,0.02,1.0)
bsdf.inputs['Roughness'].default_value=0.6
curve_obj.data.materials.append(mat)

# ---- Convert to mesh ----
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)
bpy.ops.object.convert(target='MESH')
tail_mesh = bpy.context.active_object
tail_mesh.name = "PanteraTail"
bpy.context.view_layer.update()

# Sample world positions along the tail for bone placement
# The tail runs from tail_base outward; get approximate joint positions
# by evaluating the original bezier points in world space
tail_pts_world = [tail_base + Vector(p) for p in pts]
# Subdivide into 5 bone segments: interpolate along the polyline
def sample_tail(t):
    """t in [0,1] along the 4-point polyline"""
    seg = t * 3.0
    i = min(int(seg), 2)
    f = seg - i
    return tail_pts_world[i].lerp(tail_pts_world[i+1], f)

N_BONES = 5
joint_pos = [sample_tail(i/N_BONES) for i in range(N_BONES+1)]

# ---- Create armature ----
bpy.ops.object.armature_add(enter_editmode=True, location=joint_pos[0])
arm_obj = bpy.context.active_object
arm_obj.name = "TailRig"
arm = arm_obj.data
arm.name = "TailRigData"
# Remove default bone, add our chain
arm.edit_bones.remove(arm.edit_bones[0])
bones = []
for i in range(N_BONES):
    b = arm.edit_bones.new(f"tail_{i+1:02d}")
    b.head = joint_pos[i]
    b.tail = joint_pos[i+1]
    if i > 0:
        b.parent = bones[i-1]
        b.use_connect = True
    bones.append(b)
bpy.ops.object.mode_set(mode='OBJECT')

# ---- Parent mesh to armature with automatic weights ----
bpy.context.view_layer.objects.active = arm_obj
tail_mesh.select_set(True)
arm_obj.select_set(True)
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
bpy.context.view_layer.update()

# ---- Procedural animation: cat tail sway ----
# 120 frames, 24fps = 5 sec loop
# Traveling sine wave: amplitude grows toward tip, phase delay per bone
# Plus an occasional tip flick around frame 70-85
scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 120

import math as m
amplitudes = [0.06, 0.10, 0.16, 0.24, 0.34]  # radians, grows toward tip
freq = 0.35  # Hz - slow languid sway
phase_step = 0.7  # radians delay per bone (wave travels outward)

for f in range(1, 121):
    t = (f - 1) / 24.0
    scene.frame_set(f)
    for i, bname in enumerate([f"tail_{j+1:02d}" for j in range(N_BONES)]):
        pb = arm_obj.pose.bones[bname]
        # Main sway: side-to-side (rotation around local X gives lateral swing
        # for a tail pointing mostly down/back; use euler)
        sway = amplitudes[i] * m.sin(2*m.pi*freq*t - i*phase_step)
        # Gentle vertical bob, half amplitude
        bob = amplitudes[i]*0.5 * m.sin(2*m.pi*freq*0.5*t - i*phase_step*0.5 + 1.0)
        # Tip flick: quick snap on last 2 bones around t=3s (frame ~73)
        flick = 0.0
        if i >= N_BONES-2:
            ft = t - 3.0
            if 0 <= ft < 0.6:
                flick = (0.5 if i == N_BONES-1 else 0.3) * m.sin(m.pi * ft/0.6) * m.sin(2*m.pi*8*ft)
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (sway + flick, bob*0.3, bob)
        pb.keyframe_insert(data_path="rotation_euler", frame=f)
    # Root stays put
    arm_obj.pose.bones["tail_01"].location = (0,0,0)

# Set interpolation to smooth
for fc in arm_obj.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'

bpy.context.view_layer.update()
print("RIG + ANIMATION DONE")

# ---- Camera / lighting / render setup (back view) ----
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = max(widthx, widthy, height) * 1.15
cam.location = (cx + height*2, cy, cz)
cam.rotation_euler = (math.radians(90), 0, math.radians(90))
scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(cx-height, cy-height, cz+height*2))
sun = bpy.context.active_object
sun.data.energy = 3.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

if not scene.world:
    scene.world = bpy.data.worlds.new("World")
world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)

# ---- Render 3 sway positions with UNIQUE filenames ----
# Frame 1: neutral-ish, Frame 31: max sway one way, Frame 61: max sway other way
for frame, tag in [(1, "a_neutral"), (31, "b_swayL"), (61, "c_swayR")]:
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(VDIR, f"tail_sway_{tag}_f{frame:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"WROTE {scene.render.filepath}")

print("ALL DONE")
