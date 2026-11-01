# Pass B: import pantera, eye swap, decal texture replace, mask attach, save GLB, render frames.
import bpy, os, math
from mathutils import Vector

WORK = "/home/hatch/workspace/creation-suite-flagship/work"
FILES = os.path.join(WORK, "files")
FRAMES = os.path.join(WORK, "frames")
os.makedirs(FRAMES, exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for img in list(bpy.data.images):
    if img.users == 0:
        bpy.data.images.remove(img)

bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "pantera-attire1.glb"))

def find_image(sub):
    for img in bpy.data.images:
        if sub.lower() in img.name.lower():
            return img
    return None

# eye swap
eye_img = find_image("Eye_D")
new_eye = bpy.data.images.load(os.path.join(FILES, "eye-yellow-tiger.png"))
if eye_img and new_eye:
    w, h = eye_img.size
    new_eye.scale(w, h)
    eye_img.pixels = new_eye.pixels[:]
    eye_img.update()
    print("EYE SWAP OK")
    bpy.data.images.remove(new_eye)

# decal texture replace
pants = find_image("PantsLower_D")
newp = bpy.data.images.load(os.path.join(FILES, "_pants_decal.png"))
if pants and newp:
    w, h = pants.size
    newp.scale(w, h)
    pants.pixels = newp.pixels[:]
    pants.update()
    print("DECAL OK")
    bpy.data.images.remove(newp)

# find head FIRST (before mask import pollutes the mesh list)
# domino mask goes over the EYES -> eye mesh center = placement anchor
# head WIDTH (for scale) = widest mesh in the head region (z > 0.8)
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

# mask attach (import AFTER head detection)
bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "batgirl-domino-mask.glb"))
mask_objs = list(bpy.context.selected_objects)

# scale: mask wide axis should span ~55% of head width
mw = []
for o in mask_objs:
    if o.type == 'MESH':
        mw += [(o.matrix_world @ v.co).x for v in o.data.vertices]
mask_w = (max(mw)-min(mw)) if mw else 0.1
s = (head_w*0.55)/mask_w if mask_w else 1.0
print("MASK scale:", round(s,3))

# the mask was modeled wide-in-X for a +/-Y-facing wearer (Alisa);
# Pantera faces -X, so rotate 90 deg about Z to bring the wide axis onto Y.
# NOTE: the GLB imports with rotation_mode=QUATERNION, so set XYZ first.
# NOTE 2: object origin is NOT at the geometry -> place by geometry center.
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
print("MASK OK: geometry center ->", [round(c,3) for c in target], "scale", round(s,3))

bpy.ops.export_scene.gltf(filepath=os.path.join(WORK, "pantera-customized-demo.glb"), export_format='GLB')
print("SAVED customized GLB")

# ---- render (explicit look-at matrices; no constraints) ----
from mathutils import Matrix
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
bpy.ops.object.light_add(type='SUN', location=(-3,4,3))
bpy.context.active_object.data.energy = 1.2

allv = []
for o in meshes:
    allv += [o.matrix_world @ v.co for v in o.data.vertices]
zs = [v.z for v in allv]
cz = (max(zs)+min(zs))/2; height = max(zs)-min(zs)
print("height", round(height,2))

cam_data = bpy.data.cameras.new("DemoCam")
cam = bpy.data.objects.new("DemoCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
dist = height*1.9

def look_at(loc, tgt):
    fw = (tgt-loc).normalized()
    up = Vector((0,0,1))
    rt = fw.cross(up).normalized()
    up2 = rt.cross(fw).normalized()
    m = Matrix((rt, up2, -fw)).transposed().to_4x4()
    m.translation = loc
    return m

def render_seg(name, frames, tgt, cam_dist):
    for i in range(frames):
        a = math.radians(360.0 * i / frames)
        loc = Vector((tgt.x + cam_dist*math.cos(a), tgt.y + cam_dist*math.sin(a), tgt.z))
        cam.matrix_world = look_at(loc, tgt)
        scene.render.filepath = os.path.join(FRAMES, f"{name}_{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    print("rendered", name, frames)

body_tgt = Vector((0, 0, cz))
head_tgt = Vector((hc.x, hc.y, hc.z))
render_seg("base", 36, body_tgt, dist)
render_seg("eyes", 12, head_tgt, head_w*2.4)
render_seg("mask", 12, head_tgt, head_w*2.8)
tz = cz - height*0.18
render_seg("decal", 12, Vector((0, 0, tz)), height*0.9)
render_seg("result", 36, body_tgt, dist)
print("PASS B DONE")
