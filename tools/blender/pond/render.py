"""Render source .blend (as the owner opens it: visible objects only, repo code untouched) or the shipped GLB.
usage: blender -b [file.blend] --python render.py -- MODE VIEWS OUTDIR [hide=Name,Name] [show=Name]
MODE: src | ship (ship imports /pond/shipped/model-rigged-textured.plain.glb into an empty scene)
"""
import bpy, sys, math, mathutils, os
argv = sys.argv[sys.argv.index('--') + 1:]
mode, views, outdir = argv[0], argv[1].split(','), argv[2]
opts = dict(a.split('=', 1) for a in argv[3:])
glb = opts.get('glb', '/pond/shipped/model-rigged-textured.plain.glb')
os.makedirs(outdir, exist_ok=True)
sc = bpy.context.scene
if mode == 'ship':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=glb)
for n in opts.get('hide', '').split(','):
    if n and n in bpy.data.objects:
        bpy.data.objects[n].hide_render = True; bpy.data.objects[n].hide_viewport = True
for n in opts.get('show', '').split(','):
    if n and n in bpy.data.objects:
        o = bpy.data.objects[n]; o.hide_render = False; o.hide_viewport = False; o.hide_set(False)
if opts.get('flipv') == '1':
    for o in sc.objects:
        if o.type == 'MESH':
            for uvl in o.data.uv_layers:
                for d in uvl.data: d.uv = (d.uv[0], 1 - d.uv[1])
# remove existing lights/cameras from render
for o in list(sc.objects):
    if o.type in ('LIGHT', 'CAMERA'): o.hide_render = True
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type == 'MESH' and o.visible_get() and not o.hide_render:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        mw = o.matrix_world
        vs = me.vertices
        step = max(1, len(vs) // 4000)
        pts += [mw @ vs[i].co for i in range(0, len(vs), step)]
        ev.to_mesh_clear()
mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
H = mx.z - mn.z; cx = (mn.x + mx.x) / 2
# front of figure: source faces -Y (Blender convention). glTF import also -Y after Y-up->Z-up conversion.
print('BBOX', tuple(mn), tuple(mx), 'H', H)
world = bpy.data.worlds.new('w') if not sc.world else sc.world
sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.82, 0.84, 0.88, 1); bg.inputs[1].default_value = 0.9
def light(name, rot, e):
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = e; ld.angle = 0.3
    lo = bpy.data.objects.new(name, ld); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(a) for a in rot]
light('key', (55, 0, -30), 3.0); light('fill', (70, 0, 140), 1.0)
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(opts.get('samples', 12))
sc.cycles.use_denoising = False; sc.cycles.max_bounces = 3
sc.render.film_transparent = False
sc.view_settings.view_transform = 'Standard'
def frame(view):
    # (target z fraction, half-height fraction of H, yaw degrees)
    tbl = {'front': (0.5, 0.56, 0), 'q34': (0.5, 0.56, 35), 'face': (0.905, 0.075, 0), 'face34': (0.905, 0.075, 35),
           'crotch': (0.47, 0.09, 0), 'crotch34': (0.47, 0.09, 50), 'crotchside': (0.47, 0.09, 90)}
    zf, hf, yaw = tbl[view]
    zf = float(opts.get(view + '_z', zf)); hf = float(opts.get(view + '_h', hf))
    tgt = mathutils.Vector((cx, (mn.y + mx.y) / 2 if view in ('front', 'q34') else float(opts.get('ty', (mn.y + mx.y) / 2)), mn.z + zf * H))
    cd.type = 'ORTHO'; cd.ortho_scale = 2 * hf * H * 1.0
    d = 10 * H; a = math.radians(yaw)
    cam.location = tgt + mathutils.Vector((d * math.sin(a), -d * math.cos(a), 0))
    cam.rotation_euler = (math.radians(90), 0, a)
    cd.clip_end = 30 * H
    w, h = (560, 840) if view in ('front', 'q34') else (560, 560)
    sc.render.resolution_x, sc.render.resolution_y = w, h
for v in views:
    frame(v)
    sc.render.filepath = os.path.join(outdir, f'{mode}-{v}.png')
    bpy.ops.render.render(write_still=True)
    print('WROTE', sc.render.filepath)
