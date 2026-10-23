import bpy, sys, os, math
from mathutils import Vector
# Usage: -- out.png body.glb head.glb tx ty tz [red]
# Imports body, then head; translates head root objects by (tx,ty,tz)
# (the body skeleton's head-joint world position, from the Hie — see
# anchor_match.py). Optional 'red' tints head meshes for placement proof.
argv = sys.argv[sys.argv.index('--')+1:]
out, body_p, head_p = argv[0], argv[1], argv[2]
# argv translation is in glTF coords (x, y-up, z); Blender maps glTF (x,y,z) -> (x,-z,y)
t = Vector((float(argv[3]), -float(argv[5]), float(argv[4])))
red = len(argv) > 6 and argv[6] == 'red'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=body_p)
before = set(o.name for o in bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=head_p)
mat = None
if red:
    mat = bpy.data.materials.new('RED'); mat.diffuse_color = (1, 0.1, 0.1, 1)
for o in bpy.data.objects:
    if o.name not in before:
        if o.parent is None:
            o.location += t
        if red and o.type == 'MESH':
            o.data.materials.clear(); o.data.materials.append(mat)
w = bpy.data.worlds.new('W') if not bpy.data.worlds else bpy.data.worlds[0]
bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.32,0.32,0.32,1); bg.inputs[1].default_value = 0.8
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in bpy.data.objects:
    if o.type == 'MESH':
        eo = o.evaluated_get(dg)
        m = eo.to_mesh()
        pts += [eo.matrix_world @ v.co for v in m.vertices]
def pct(vals, q):
    s = sorted(vals); return s[min(len(s)-1, max(0, int(q*len(s))))]
mn = Vector((pct([q[i] for q in pts], 0.002) for i in range(3))); mx = Vector((pct([q[i] for q in pts], 0.998) for i in range(3)))
c = (mn+mx)/2; size = max((mx-mn)[i] for i in range(3)) or 1.0
cam = bpy.data.cameras.new('c'); cam.clip_end = 1000
co = bpy.data.objects.new('cam', cam); bpy.context.scene.collection.objects.link(co)
co.location = (c.x, c.y-size*1.45, c.z); co.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = co
lt = bpy.data.lights.new('s', 'SUN'); lt.energy = 4
lo = bpy.data.objects.new('sun', lt); bpy.context.scene.collection.objects.link(lo); lo.rotation_euler = (math.radians(50), 0, math.radians(30))
lt2 = bpy.data.lights.new('f', 'SUN'); lt2.energy = 1.2
lo2 = bpy.data.objects.new('fill', lt2); bpy.context.scene.collection.objects.link(lo2); lo2.rotation_euler = (math.radians(70), 0, math.radians(-120))
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 8; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.render.resolution_x = 512; sc.render.resolution_y = 640
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('RENDERED', out)
