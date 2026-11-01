# Test: verify mask placement + eye swap with one front render.
import bpy, os, math
from mathutils import Vector

WORK = "/home/hatch/workspace/creation-suite-flagship/work"
FILES = os.path.join(WORK, "files")

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for img in list(bpy.data.images):
    if img.users == 0:
        bpy.data.images.remove(img)

bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "pantera-attire1.glb"))

# (eye swap + decal replace happen here; head detection BEFORE mask import)
def find_image(sub):
    for img in bpy.data.images:
        if sub.lower() in img.name.lower():
            return img
    return None

eye_img = find_image("Eye_D")
new_eye = bpy.data.images.load(os.path.join(FILES, "eye-yellow-tiger.png"))
w, h = eye_img.size
new_eye.scale(w, h)
eye_img.pixels = new_eye.pixels[:]
eye_img.update()
bpy.data.images.remove(new_eye)

pants = find_image("PantsLower_D")
newp = bpy.data.images.load(os.path.join(FILES, "_pants_decal.png"))
pw, ph = pants.size
newp.scale(pw, ph)
pants.pixels = newp.pixels[:]
pants.update()
bpy.data.images.remove(newp)

# head detection FIRST (before mask import)
# domino mask goes over the EYES -> eye mesh center = placement anchor
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
def center(o):
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    return sum(ws, Vector()) / len(ws)
eye_mesh = None
for o in meshes:
    if 'eye' in o.name.lower():
        c = center(o)
        if c.z > 0.5:
            eye_mesh = o
            break
top = [o for o in meshes if center(o).z > 0.8]
top.sort(key=lambda o: len(o.data.vertices), reverse=True)
head_wmesh = top[0] if top else None
hc = center(eye_mesh) if eye_mesh else Vector((0,0,1.0))
if head_wmesh:
    hxs = [(head_wmesh.matrix_world @ v.co).x for v in head_wmesh.data.vertices]
    head_w = max(hxs) - min(hxs)
else:
    head_w = 0.2
print("EYES:", eye_mesh.name if eye_mesh else None, "at", [round(c,3) for c in hc])
print("HEADW:", head_wmesh.name if head_wmesh else None, "w", round(head_w,3))

bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "batgirl-domino-mask.glb"))
mask_objs = list(bpy.context.selected_objects)

# scale: mask wide axis should span ~55% of head width
mw = []
for o in mask_objs:
    if o.type == 'MESH':
        mw += [(o.matrix_world @ v.co).x for v in o.data.vertices]
mask_w = (max(mw)-min(mw)) if mw else 0.1
s = (head_w*0.55)/mask_w if mask_w else 1.0

# rotate 90deg about Z: mask modeled wide-in-X for +/-Y-facing wearer, Pantera faces -X
# (GLB imports with rotation_mode=QUATERNION, so set XYZ first)
# object origin is NOT at the geometry -> place by geometry center after transform
for o in mask_objs:
    if o.type in ('MESH', 'CURVE', 'EMPTY'):
        o.rotation_mode = 'XYZ'
        o.rotation_euler = (0, 0, math.radians(90))
        o.scale = (s, s, s)
bpy.context.view_layer.update()
target = Vector((hc.x - head_w*0.35, hc.y, hc.z))
for o in mask_objs:
    if o.type == 'MESH':
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        c = sum(ws, Vector()) / len(ws)
        o.location += (target - c)
bpy.context.view_layer.update()
print("MASK at", [round(c,3) for c in target], "scale", round(s,3))

# quick front render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.cycles.samples = 24
scene.cycles.use_denoising = True
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (1,1,1,1)
    bg.inputs[1].default_value = 1.0
bpy.ops.object.light_add(type='SUN', location=(3,-4,6))
bpy.context.active_object.data.energy = 3.0

cam_data = bpy.data.cameras.new("TestCam")
cam = bpy.data.objects.new("TestCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
# front = -X per convention
cam.location = (hc.x - head_w*3.0, hc.y, hc.z)
# explicit look-at (TRACK_TO was misbehaving)
from mathutils import Matrix
loc = Vector(cam.location); tgt = Vector((hc.x, hc.y, hc.z))
fw = (tgt-loc).normalized(); up = Vector((0,0,1))
rt = fw.cross(up).normalized(); up2 = rt.cross(fw).normalized()
m = Matrix((rt, up2, -fw)).transposed().to_4x4(); m.translation = loc
cam.matrix_world = m
scene.render.filepath = os.path.join(WORK, "mask-test.png")
bpy.ops.render.render(write_still=True)
print("TEST DONE")
