"""tpose_render_xps.py - T-pose front+side renderer for XPS (XNALara) models.
Variant of tpose_render_cycles.py for Y-up XPS imports (e.g. Dr. Bosconovitch):
- model faces -Y, arms along X, already in T-pose rest
- front camera at -Y, side camera at +X (character's left)
- Cycles CPU only, emission-override flat look, pure white background
Usage: blender -b --python tpose_render_xps.py -- <xpsfile> <outprefix>
"""
import bpy, os, sys, re, glob, math
import addon_utils
from mathutils import Matrix, Vector

addon_utils.enable('XNALara-io-Tools', default_set=True)

argv = sys.argv[sys.argv.index("--") + 1:]
SRC = argv[0]
OUT = argv[1]
texdir = os.path.dirname(os.path.abspath(SRC))
os.chdir(texdir)

report = {"src": SRC, "armatures": 0, "posed": []}

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('XNALara-io-Tools', default_set=True)
bpy.ops.xnal.operator_modal_import_xps(filepath=os.path.abspath(SRC))
print("IMPORT OK:", SRC)

tex_report = {"recovered": 0, "missing": []}

def diffuse_node(nt):
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        for link in nt.links:
            if (link.to_node == bsdf and link.to_socket.name == 'Base Color'
                    and link.from_node.type == 'TEX_IMAGE'):
                return link.from_node
    timgs = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image]
    return timgs[0] if timgs else None

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is None:
        continue
    img_node = diffuse_node(nt)
    if img_node is None or img_node.image is None:
        tex_report["missing"].append(mat.name)
        continue
    em = nt.nodes.new('ShaderNodeEmission')
    try:
        nt.links.new(img_node.outputs['Color'], em.inputs['Color'])
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    except Exception as e:
        print("link fail", mat.name, e)
        continue

print("TEXTURES recovered=%d missing=%d" % (tex_report["recovered"], len(tex_report["missing"])))
if tex_report["missing"]:
    print("  missing:", tex_report["missing"])
report["textures"] = tex_report

# bbox over mesh world verts
mn = [1e9, 1e9, 1e9]; mx = [-1e9, -1e9, -1e9]
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
print("BBOX dx=%.4f dy=%.4f dz=%.4f" % (mx[0]-mn[0], mx[1]-mn[1], mx[2]-mn[2]))
report["bbox"] = [list(mn), list(mx)]

cx = (mn[0]+mx[0])/2; cy = (mn[1]+mx[1])/2; cz = (mn[2]+mx[2])/2
span = max(mx[0]-mn[0], mx[1]-mn[1], mx[2]-mn[2])

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 2
sc.cycles.use_denoising = False
sc.view_settings.look = "None"
sc.render.resolution_x = 2048
sc.render.resolution_y = 2048
sc.render.film_transparent = False
w = bpy.data.worlds.new('WhiteWorld')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (1, 1, 1, 1)
sc.world = w
sc.view_settings.view_transform = 'Standard'

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

def render_view(name, eye):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = span * 1.12
    cam.matrix_world = look_at(eye, Vector((cx, cy, cz)), Vector((0, 0, 1)))
    sc.camera = cam
    sc.render.filepath = OUT + '_' + name + '.png'
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name, "ortho_scale=%.4f" % cam.data.ortho_scale)
    bpy.data.objects.remove(cam, do_unlink=True)

D = span * 3
render_view('front', Vector((cx, cy - D, cz)))   # face is at -Y
render_view('side', Vector((cx + D, cy, cz)))    # character's left side (+X)
print("DONE")
