import bpy, sys
from math import radians
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUTBASE = a[0], a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=SRC)

# part roots = armature objects with UE bone names (root/pelvis), not the base Mixamo rig
part_roots = [o for o in sc.objects if o.type == 'ARMATURE' and 'pelvis' in o.data.bones]
print("part roots:", [o.name for o in part_roots])
from mathutils import Quaternion, Euler
saved = {o.name: o.rotation_quaternion.copy() for o in part_roots}

w = bpy.data.worlds.new("W")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
sc.world = w
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 2
sc.cycles.use_denoising = False
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x = sc.render.resolution_y = 768
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_end = 1000
cam.data.ortho_scale = 0.9
c = Vector((0.02, 0.08, 1.58))
eye = Vector((c.x, c.y - 10, c.z))
z = (eye - c).normalized()
x = Vector((0, 0, 1)).cross(z).normalized()
y = z.cross(x)
M = Matrix.Identity(4)
M[0][0], M[1][0], M[2][0] = x[0], x[1], x[2]
M[0][1], M[1][1], M[2][1] = y[0], y[1], y[2]
M[0][2], M[1][2], M[2][2] = z[0], z[1], z[2]
M[0][3], M[1][3], M[2][3] = eye[0], eye[1], eye[2]
cam.matrix_world = M

def shot(tag, euler):
    for o in part_roots:
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = Euler(euler, 'XYZ').to_quaternion()
    bpy.context.view_layer.update()
    sc.render.filepath = f"{OUTBASE}_{tag}.png"
    bpy.ops.render.render(write_still=True)
    print("SHOT", tag)

shot('base', (0, 0, 0))
shot('ry90', (0, radians(90), 0))
shot('rym90', (0, radians(-90), 0))
shot('rx90', (radians(90), 0, 0))
shot('rxm90', (radians(-90), 0, 0))
shot('rz90', (0, 0, radians(90)))
for o in part_roots:
    o.rotation_quaternion = saved[o.name]
print("ROT PROBE DONE")
