"""render_decal_proof_blender.py — render what the fight draws: the game's own decal patches
(export_decal_proof.mjs -> OBJ per layer) on each template body, in Blender (Cycles, CPU).

Run (repo root):
  node tools/creation-suite/decals/decode_glb.mjs /tmp/wh-decoded customization/templates/meshes/*.glb
  node tools/creation-suite/decals/export_decal_proof.mjs /tmp/wh-decal-proof
  blender -b --python tools/creation-suite/decals/render_decal_proof_blender.py -- \
      /tmp/wh-decoded /tmp/wh-decal-proof OUT_DIR template[,template...]
Writes OUT_DIR/<template>_{front,back,face}.png. Bodies render as clay (MB-Lab's skin shader
speckles under CPU Cycles here); each decal patch gets its PNG with alpha, so tattoos and scars
appear exactly where game/js/decal-layers.js projects them, in layer order.
"""
import sys, os, json, math, glob
sys.path.insert(0, '/tmp/bpylib')  # numpy for Blender's python when the distro lacks it (glTF importer needs it)
import bpy

argv = sys.argv[sys.argv.index('--') + 1:]
DEC, PROOF_IN, OUT, ONLY = argv[0], argv[1], argv[2], argv[3].split(',')
REPO = os.getcwd()


def mat_for(img_path, name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(img_path)
    tex.interpolation = 'Closest' if tex.image.size[0] <= 64 else 'Linear'
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.6
    return m


def render(tid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(DEC, tid + '.glb'))
    clay = bpy.data.materials.new('clay'); clay.use_nodes = True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.66, 0.5, 0.4, 1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.65
    for o in list(bpy.data.objects):
        if o.type == 'MESH':
            if o.name == 'Icosphere':
                o.hide_render = True; continue
            for s in o.material_slots:
                s.material = clay
    layers = json.load(open(os.path.join(PROOF_IN, tid, 'layers.json')))
    for f in sorted(glob.glob(os.path.join(PROOF_IN, tid, '*.obj'))):
        lid = os.path.basename(f)[3:-4]
        meta = next((x for x in layers if x['id'] == lid), None)
        if not meta:
            continue
        bpy.ops.wm.obj_import(filepath=f, forward_axis='NEGATIVE_Z', up_axis='Y')
        ob = bpy.context.selected_objects[0]
        ob.data.materials.clear(); ob.data.materials.append(mat_for(os.path.join(REPO, meta['asset']), 'decal_' + lid))
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'; scn.cycles.samples = 32; scn.cycles.device = 'CPU'; scn.cycles.use_denoising = False
    scn.render.resolution_x, scn.render.resolution_y = 420, 720
    w = bpy.data.worlds.new('w'); scn.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 1.5
    # suns aimed at the body: key from the front (travels +Y), fill from the back (travels -Y)
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(60), 0, math.radians(20))); bpy.context.active_object.data.energy = 3.5
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(-60), 0, math.radians(-20))); bpy.context.active_object.data.energy = 2.5
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); scn.collection.objects.link(cam); scn.camera = cam
    cd.type = 'ORTHO'
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    hz = (arm.matrix_world @ arm.data.bones['head'].head_local).z
    views = {'front': ((0, -4, 0.95), (math.pi / 2, 0, 0), 2.05), 'back': ((0, 4, 0.95), (math.pi / 2, 0, math.pi), 2.05),
             'face': ((0, -2, hz + 0.07), (math.pi / 2, 0, 0), 0.36)}
    for v, (loc, rot, sc) in views.items():
        cam.location = loc; cam.rotation_euler = rot; cd.ortho_scale = sc
        if v == 'face':
            scn.render.resolution_x, scn.render.resolution_y = 420, 420
        scn.render.filepath = os.path.join(OUT, f'{tid}_{v}.png')
        bpy.ops.render.render(write_still=True)


os.makedirs(OUT, exist_ok=True)
for t in ONLY:
    render(t)
    print('[proof] rendered', t, flush=True)
