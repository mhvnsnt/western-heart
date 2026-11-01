# Creation Suite flagship — pipeline demo: customize Pantera live, render frames.
# Steps: import Attire 1 -> eye swap (yellow tiger) -> decal composite (snow leopard)
#        -> domino mask attach -> render orbit/close-up frames.
import bpy, os, math, sys
from mathutils import Vector

WORK = "/home/hatch/workspace/creation-suite-flagship/work"
FILES = os.path.join(WORK, "files")
FRAMES = os.path.join(WORK, "frames")
os.makedirs(FRAMES, exist_ok=True)

# ---- clean scene ----
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for img in list(bpy.data.images):
    if img.users == 0:
        bpy.data.images.remove(img)

# ---- import pantera ----
bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "pantera-attire1.glb"))
print("imported objects:", len(bpy.context.scene.objects))

def find_image(sub):
    for img in bpy.data.images:
        if sub.lower() in img.name.lower():
            return img
    return None

# ---- STEP 1: eye swap -> yellow tiger ----
eye_img = find_image("Eye_D")
new_eye = bpy.data.images.load(os.path.join(FILES, "eye-yellow-tiger.png"))
if eye_img and new_eye:
    w, h = eye_img.size
    new_eye.scale(w, h)
    eye_img.pixels = new_eye.pixels[:]
    eye_img.update()
    print(f"EYE SWAP OK: {eye_img.name} {w}x{h}")
    bpy.data.images.remove(new_eye)
else:
    print("EYE SWAP FAILED", eye_img, new_eye)

# ---- STEP 2: decal composite onto tights (PIL, pre-blender) ----
from PIL import Image
pants_img = find_image("PantsLower_D")
if pants_img:
    pw, ph = pants_img.size
    tmp = os.path.join(FILES, "_pants.png")
    pants_img.filepath_raw = tmp
    pants_img.file_format = 'PNG'
    pants_img.save()
    base = Image.open(tmp).convert("RGBA")
    decal = Image.open(os.path.join(FILES, "pantera-logo-snow-leopard.png")).convert("RGBA")
    # owner placement: rect x=130, y=90, 279x279 in 512x512 texture space
    sx = base.width / 512.0
    rect = (int(130*sx), int(90*sx), int(279*sx))
    d = decal.resize((rect[2], rect[2]), Image.LANCZOS)
    # GL textures are Y-flipped vs PIL: flip base, paste, flip back
    base = base.transpose(Image.FLIP_TOP_BOTTOM)
    base.paste(d, (rect[0], rect[1]), d)
    base = base.transpose(Image.FLIP_TOP_BOTTOM)
    base.save(tmp)
    newp = bpy.data.images.load(tmp)
    newp.scale(pw, ph)
    pants_img.pixels = newp.pixels[:]
    pants_img.update()
    bpy.data.images.remove(newp)
    print(f"DECAL OK: {pants_img.name}")
else:
    print("DECAL FAILED: no PantsLower_D")

# ---- STEP 3: domino mask attach ----
bpy.ops.import_scene.gltf(filepath=os.path.join(FILES, "batgirl-domino-mask.glb"))
mask_objs = [o for o in bpy.context.selected_objects]
print("mask objects:", len(mask_objs))

# find head mesh: highest-center mesh
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
def center(o):
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    return sum(ws, Vector()) / len(ws)
meshes.sort(key=lambda o: center(o).z)
head = meshes[-1]
hc = center(head)
# head width
xs = [(head.matrix_world @ v.co).x for v in head.data.vertices]
head_w = max(xs) - min(xs)
print("head:", head.name, "center:", tuple(round(c,3) for c in hc), "width:", round(head_w,3))

# fit mask: scale to ~55% of head width, place at face front
mb = Vector((0,0,0)); n=0
for o in mask_objs:
    if o.type == 'MESH':
        for v in o.data.vertices:
            mb += o.matrix_world @ v.co; n+=1
mb = mb/n if n else Vector()
mxs = []
for o in mask_objs:
    if o.type == 'MESH':
        mxs += [(o.matrix_world @ v.co).x for v in o.data.vertices]
mask_w = (max(mxs)-min(mxs)) if mxs else 0.1
s = (head_w*0.55)/mask_w if mask_w else 1.0
root = mask_objs[0]
# parent all to root first
for o in mask_objs[1:]:
    o.parent = root
root.scale = (s,s,s)
# move mask center to face: in front of head center (face on -X per convention)
root.location = (hc.x - head_w*0.35, hc.y, hc.z + head_w*0.05)
print("MASK placed, scale:", round(s,3))

# save customized GLB
bpy.ops.export_scene.gltf(
    filepath=os.path.join(WORK, "pantera-customized-demo.glb"),
    export_format='GLB')
print("SAVED customized GLB")

# ---- render setup ----
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.film_transparent = False
# white world
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (1,1,1,1)
    bg.inputs[1].default_value = 1.0

# lights
bpy.ops.object.light_add(type='SUN', location=(3,-4,6))
sun = bpy.context.active_object
sun.data.energy = 3.0
bpy.ops.object.light_add(type='SUN', location=(-3,4,3))
sun2 = bpy.context.active_object
sun2.data.energy = 1.2

# model bounds for camera framing
allv = []
for o in meshes:
    allv += [o.matrix_world @ v.co for v in o.data.vertices]
zs = [v.z for v in allv]; xs2=[v.x for v in allv]; ys2=[v.y for v in allv]
cz = (max(zs)+min(zs))/2; height = max(zs)-min(zs)
print("model height:", round(height,2))

# camera rig: pivot empty + camera on arm
bpy.ops.object.empty_add(location=(0,0,cz))
pivot = bpy.context.active_object
cam_data = bpy.data.cameras.new("DemoCam")
cam = bpy.data.objects.new("DemoCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
dist = height*1.9
cam.location = (dist, 0, cz + height*0.1)
# track to pivot
con = cam.constraints.new('TRACK_TO')
con.target = pivot
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
cam.parent = pivot

def render_seg(name, frames, cam_dist=None, cam_z=None, target_z=None, close_target=None):
    if cam_dist: cam.location = (cam_dist, 0, (cam_z or cz))
    if target_z is not None: pivot.location = (0,0,target_z)
    if close_target is not None: pivot.location = close_target
    for i in range(frames):
        pivot.rotation_euler.z = math.radians(360.0 * i / frames)
        scene.render.filepath = os.path.join(FRAMES, f"{name}_{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    print("rendered", name, frames)

# base orbit
render_seg("base", 36, cam_dist=dist)
# eyes close-up (face on -X side)
render_seg("eyes", 12, cam_dist=head_w*2.2, close_target=(hc.x, hc.y, hc.z))
# mask close-up
render_seg("mask", 12, cam_dist=head_w*2.6, close_target=(hc.x - head_w*0.3, hc.y, hc.z))
# decal close-up (tights ~ mid height)
tz = cz - height*0.18
render_seg("decal", 12, cam_dist=height*0.9, close_target=(0, 0, tz))
# result turntable
render_seg("result", 36, cam_dist=dist, close_target=(0,0,cz))
print("DONE ALL FRAMES")
