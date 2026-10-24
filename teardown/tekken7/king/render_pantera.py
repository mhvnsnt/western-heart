import bpy, math, sys, os
from mathutils import Vector

VIEW = sys.argv[-1]
KDIR = os.getcwd()
PDIR = os.path.join(KDIR, "pantera")
OUT = os.path.join(PDIR, f"views/pantera_{VIEW}.png")
os.makedirs(os.path.join(PDIR, "views"), exist_ok=True)

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

# ---- RIGGED TAIL (5-bone chain, rest pose) ----
# For automatic secondary motion, install Wiggle 2 addon:
#   ~/workspace/tools/wiggle-bones/wiggle_2_ultimate.py  (GPL v3, free)
# Enable: scene.wiggle_enable=True, arm_obj.wiggle_enable=True,
# then per-bone: pb.wiggle_enable=True, pb.wiggle_tail=True
tail_base = Vector((maxx - widthx*0.06, cy + 0.0, 0.09))  # user: 50% / Y=46.5%
L = height*0.28

bpy.ops.curve.primitive_bezier_curve_add(location=tail_base)
curve_obj = bpy.context.active_object
curve_obj.name = "PanteraTailCurve"
spline = curve_obj.data.splines[0]
_tail_pts = [(0,0,0), (L*0.25,L*0.05,-L*0.30), (L*0.35,L*0.35,-L*0.55), (L*0.25,L*0.70,-L*0.60)]
while len(spline.bezier_points) < 4:
    spline.bezier_points.add(1)
for i, (px,py,pz) in enumerate(_tail_pts):
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

_tail_mat = bpy.data.materials.new("TailBlack")
_tail_mat.use_nodes=True
_bsdf=_tail_mat.node_tree.nodes['Principled BSDF']
_bsdf.inputs['Base Color'].default_value=(0.02,0.02,0.02,1.0)
_bsdf.inputs['Roughness'].default_value=0.6
curve_obj.data.materials.append(_tail_mat)

# Convert to mesh for skinning
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)
bpy.ops.object.convert(target='MESH')
tail_mesh = bpy.context.active_object
tail_mesh.name = "PanteraTail"
bpy.context.view_layer.update()

# 5-bone chain along tail
_tail_world = [tail_base + Vector(p) for p in _tail_pts]
def _sample_tail(t):
    seg = t * 3.0
    i = min(int(seg), 2)
    f = seg - i
    return _tail_world[i].lerp(_tail_world[i+1], f)
_NB = 5
_jp = [_sample_tail(i/_NB) for i in range(_NB+1)]
bpy.ops.object.armature_add(enter_editmode=True, location=_jp[0])
arm_obj = bpy.context.active_object
arm_obj.name = "TailRig"
_arm = arm_obj.data
_arm.edit_bones.remove(_arm.edit_bones[0])
_pbones = []
for _i in range(_NB):
    _b = _arm.edit_bones.new(f"tail_{_i+1:02d}")
    _b.head = _jp[_i]
    _b.tail = _jp[_i+1]
    if _i > 0:
        _b.parent = _pbones[_i-1]
        _b.use_connect = True
    _pbones.append(_b)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = arm_obj
tail_mesh.select_set(True)
arm_obj.select_set(True)
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
bpy.context.view_layer.update()

# Camera setup - orthographic, 1:1
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = max(widthx, widthy, height) * 1.15

# Position camera based on view
if VIEW == 'front':
    cam.location = (cx - height*2, cy, cz)
    cam.rotation_euler = (math.radians(90), 0, math.radians(-90))
elif VIEW == 'back':
    cam.location = (cx + height*2, cy, cz)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
elif VIEW == 'left':
    cam.location = (cx, cy - height*2, cz)
    cam.rotation_euler = (math.radians(90), 0, math.radians(180))
elif VIEW == 'right':
    cam.location = (cx, cy + height*2, cz)
    cam.rotation_euler = (math.radians(90), 0, 0)

bpy.context.scene.camera = cam

# Lighting
bpy.ops.object.light_add(type='SUN', location=(cx-height, cy-height, cz+height*2))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.render.resolution_x = 1500
scene.render.resolution_y = 1500
scene.render.resolution_percentage = 100
scene.render.filepath = OUT
scene.render.image_settings.file_format = 'PNG'

# Gray background
if not bpy.context.scene.world:
    bpy.context.scene.world = bpy.data.worlds.new("World")
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)

bpy.ops.render.render(write_still=True)
print(f"WROTE {OUT}")
