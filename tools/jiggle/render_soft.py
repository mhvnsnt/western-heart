import bpy, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUTDIR, START, END = argv[0], argv[1], int(argv[2]), int(argv[3])
os.makedirs(OUTDIR, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene
for o in bpy.data.objects:
    o.hide_render = False
    o.hide_viewport = False

def body_bounds(frame):
    scene.frame_set(frame)
    dg2 = bpy.context.evaluated_depsgraph_get()
    mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name == "Icosphere":
            continue
        eo = o.evaluated_get(dg2)
        me = eo.to_mesh()
        vs = me.vertices
        step = max(1, len(vs) // 3000)
        for i in range(0, len(vs), step):
            w = eo.matrix_world @ vs[i].co
            mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
        eo.to_mesh_clear()
    return mins, maxs

sample = sorted(set([START, (START + END) // 2, END]))
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
for f in sample:
    a, b = body_bounds(f)
    mins = Vector(map(min, mins, a)); maxs = Vector(map(max, maxs, b))
center = (mins + maxs) / 2
size = maxs - mins
span = max(size) * 1.15
print("UNION BOUNDS", tuple(round(v, 2) for v in mins), tuple(round(v, 2) for v in maxs), "span", round(span, 2), flush=True)

world = bpy.data.worlds.new("SoftWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.55, 0.56, 0.58, 1.0)
bg.inputs[1].default_value = 1.0

def aim(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def add_light(name, ltype, loc, energy, size_=1.0):
    ld = bpy.data.lights.new(name, ltype)
    ld.energy = energy
    if ltype == "AREA":
        ld.shape = "DISK"; ld.size = size_
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    scene.collection.objects.link(lo)
    aim(lo, center)
    return lo

c = center
add_light("KeyArea", "AREA", c + Vector((1.6, -2.4, 1.6)), 650, size_=4.0)
add_light("FillArea", "AREA", c + Vector((-2.0, -1.6, 0.4)), 380, size_=4.0)
add_light("RimArea", "AREA", c + Vector((0.4, 2.4, 1.8)), 500, size_=3.0)
sun = bpy.data.lights.new("SoftSun", "SUN"); sun.energy = 0.7
so = bpy.data.objects.new("SoftSun", sun); so.location = c + Vector((2.0, -2.0, 3.0))
scene.collection.objects.link(so); aim(so, c)

cam_data = bpy.data.cameras.new("ProofCam"); cam_data.lens = 50
cam = bpy.data.objects.new("ProofCam", cam_data)
scene.collection.objects.link(cam)
DISTF = float(argv[4]) if len(argv) > 4 else 2.35
dist = span * DISTF
cam.location = c + Vector((0.38, -1.0, 0.10)).normalized() * dist
aim(cam, c)
scene.camera = cam

try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
try:
    bpy.context.preferences.system.gl_texture_limit = "1024"
except Exception:
    pass
scene.eevee.taa_render_samples = int(argv[7]) if len(argv) > 7 else 16
if hasattr(scene.eevee, "use_gtao"):
    scene.eevee.use_gtao = (len(argv) <= 8 or argv[8] != "nogtao")
scene.render.resolution_x = int(argv[5]) if len(argv) > 5 else 480
scene.render.resolution_y = int(argv[6]) if len(argv) > 6 else 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
for f in range(START, END + 1):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUTDIR, f"f{f:03d}.png")
    bpy.ops.render.render(write_still=True)
    print("WROTE", scene.render.filepath, flush=True)
print("SEQ DONE")
