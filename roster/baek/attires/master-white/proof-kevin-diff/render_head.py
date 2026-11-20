"""Head close-up renderer — derived from docs/RENDER-ORIENTATION.md locked method
(tpose_render_cycles.py): same Cycles emission-override flat look, white bg,
ortho camera on -X after facing correction, T-pose reset. Difference: framing
targets the head (ortho_scale = 1.12 x head span) instead of the full body.

Usage: blender -b --python render_head.py -- <model.glb> <out.png> [faceY]
  faceY: apply Rz(-90) post-import (models authored facing -Y, per the locked
  doc's variant detection: base script's side view showed the front).
"""
import bpy, sys, os, re, glob, math
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = a[0], a[1]
FACEY = len(a) > 2 and a[2] == "faceY"
ROT180 = len(a) > 2 and a[2] == "rot180"
FRONTY = len(a) > 2 and a[2] == "frontY"  # no rotation; front camera sits on -Y (rigged models the faceY rotation mangles)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=SRC)
for o in sc.objects:
    if o.animation_data:
        o.animation_data_clear()
if FACEY or ROT180:
    ang = math.radians(-90) if FACEY else math.radians(180)
    R = Matrix.Rotation(ang, 4, 'Z')
    for o in list(sc.objects):
        if o.parent is None:
            o.matrix_world = R @ o.matrix_world
    bpy.context.view_layer.update()

# T-pose reset (same as locked script)
for arm in [o for o in sc.objects if o.type == "ARMATURE"]:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

# emission override fed by albedo (same as locked script)
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        continue
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    img_node = None
    if bsdf is not None:
        for link in nt.links:
            if link.to_node == bsdf and link.to_socket.name == "Base Color" and link.from_node.type == "TEX_IMAGE":
                img_node = link.from_node
    if img_node is None:
        img_node = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None)
    if img_node is None or img_node.image is None:
        continue
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(img_node.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])

# evaluated bbox; head = top 18% slab
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type != "MESH":
        continue
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    pts += [e.matrix_world @ v.co for v in m.vertices]
    e.to_mesh_clear()
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
height = mx.z - mn.z
axis_x = (mn.x + mx.x) / 2
axis_y = (mn.y + mx.y) / 2
# top slab AND near the body axis — in T-pose the arms sit at head height and
# would otherwise blow the framing out to the full arm span
head_pts = [p for p in pts if p.z > mx.z - 0.14 * height
            and abs(p.x - axis_x) < 0.12 * height and abs(p.y - axis_y) < 0.12 * height]
hmn = Vector((min(p.x for p in head_pts), min(p.y for p in head_pts), min(p.z for p in head_pts)))
hmx = Vector((max(p.x for p in head_pts), max(p.y for p in head_pts), max(p.z for p in head_pts)))
c = (hmn + hmx) / 2
d = hmx - hmn
span = max(d.x, d.z) if FRONTY else max(d.y, d.z)

w = bpy.data.worlds.new("WhiteVoid")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
sc.world = w
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 2
sc.cycles.use_denoising = False
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.render.film_transparent = False

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_end = 1000

def look_at(eye, target, up):
    z = (eye - target).normalized()
    x = up.cross(z).normalized()
    y = z.cross(x)
    M = Matrix.Identity(4)
    M[0][0], M[1][0], M[2][0] = x[0], x[1], x[2]
    M[0][1], M[1][1], M[2][1] = y[0], y[1], y[2]
    M[0][2], M[1][2], M[2][2] = z[0], z[1], z[2]
    M[0][3], M[1][3], M[2][3] = eye[0], eye[1], eye[2]
    return M

if FRONTY:
    eye = Vector((c.x, mn.y - 10 * max(height, span), c.z))
else:
    eye = Vector((mn.x - 10 * max(height, span), c.y, c.z))
cam.matrix_world = look_at(eye, c, Vector((0, 0, 1)))
cam.data.ortho_scale = span * 1.35
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("HEAD RENDERED", OUT, "center=", list(c), "span=%.3f" % span)
