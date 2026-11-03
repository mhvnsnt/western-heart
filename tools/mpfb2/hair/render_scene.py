"""render_scene.py — Blender 4.3 headless proof renders (Cycles CPU; this aarch64 box has no working GL for
EEVEE/Workbench). Run:  blender -b -P render_scene.py -- jobs.json
jobs.json: [{template, parts:[asset-id], morphs:{shape-key: value}, pose:{bone:[rx,ry,rz deg]} | null,
             clip: path-to-glb-with-animation | null, frame: int, views:[{name, kind:'body'|'head'|'bust', yaw}],
             out_prefix, res, label}]
Parts come from fitbl/<asset>/<template>.json (Blender stage output): skinned to the template armature with the
transferred weights (Armature modifier) and carrying the transferred shape keys, so a morph value set on the body
is set on every part with the same key name, and a pose moves hair by its weights.
"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
jobs = json.load(open(sys.argv[sys.argv.index('--') + 1]))
assets = {a['id']: a for a in json.load(open(os.path.join(HERE, 'assets.json')))}
COL = {'hair': (0.22, 0.13, 0.07), 'eyebrows': (0.035, 0.025, 0.018), 'eyelashes': (0.02, 0.015, 0.012), 'beard': (0.10, 0.065, 0.04)}


def gl2bl(P):
    return np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)


def mh_texture(a):
    if a['kind'] == 'beard':  # the shipped procedural strand mask (build_glb.mjs), same texture the game uses
        return os.path.join(os.environ.get('WH_REPO', '/tmp/wh-bl'), 'customization/parts/hair/mpfb2', a['id'], 'texture.png')
    d = os.path.join(HERE, 'mh', a['src']); nm = os.path.basename(a['src'])
    for line in open(os.path.join(d, nm + '.mhmat')):
        if line.startswith('diffuseTexture'):
            return os.path.join(d, line.split()[1])


def part_material(a, tint=None):
    m = bpy.data.materials.new(a['id'])
    m.use_nodes = True
    nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    c = tint or COL[a['kind']]
    bs.inputs['Base Color'].default_value = (*c, 1)
    bs.inputs['Roughness'].default_value = 0.55
    tex = mh_texture(a)
    if tex and os.path.exists(tex):
        im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(tex)
        mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
        mix.inputs[1].default_value = (*c, 1)
        bw = nt.nodes.new('ShaderNodeRGBToBW')
        nt.links.new(im.outputs['Color'], bw.inputs['Color'])
        gain = nt.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = 2.2
        nt.links.new(bw.outputs[0], gain.inputs[0])
        cr = nt.nodes.new('ShaderNodeCombineColor')
        for k in range(3):
            nt.links.new(gain.outputs[0], cr.inputs[k])
        nt.links.new(cr.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], bs.inputs['Base Color'])
        ap = nt.nodes.new('ShaderNodeMath'); ap.operation = 'POWER'; ap.inputs[1].default_value = 0.35 if a['kind'] != 'hair' else 0.8
        nt.links.new(im.outputs['Alpha'], ap.inputs[0]); nt.links.new(ap.outputs[0], bs.inputs['Alpha'])
    elif a['kind'] == 'beard':
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 900.0
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.45 if a['src'] != 'beard-stubble' else 0.55
        ramp.color_ramp.elements[1].position = 0.5 if a['src'] != 'beard-stubble' else 0.6
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bs.inputs['Alpha'])
    return m


def build_part(pid, tpl, arm, tint=None):
    a = assets[pid]
    J = json.load(open(os.path.join(HERE, 'fitbl', pid, tpl + '.json')))
    P = gl2bl(np.array(J['pos']).reshape(-1, 3)); F = np.array(J['idx']).reshape(-1, 3)
    me = bpy.data.meshes.new(pid); me.from_pydata(P.tolist(), [], F.tolist()); me.update()
    uv = np.array(J['uv']).reshape(-1, 2)
    ul = me.uv_layers.new(name='UV')
    loops = np.empty(len(me.loops), int); me.loops.foreach_get('vertex_index', loops)
    ul.data.foreach_set('uv', uv[loops].ravel())
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(pid, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(part_material(a, tint))
    names = J['joint_names']; jt = np.array(J['joints']).reshape(-1, 4); wt = np.array(J['weights']).reshape(-1, 4)
    groups = {}
    for i in range(len(P)):
        for k in range(4):
            if wt[i, k] > 0:
                nm = names[jt[i, k]]
                if nm not in groups:
                    groups[nm] = ob.vertex_groups.new(name=nm)
                groups[nm].add([i], float(wt[i, k]), 'ADD')
    if J['targets']:
        ob.shape_key_add(name='Basis')
        for k, d in J['targets'].items():
            sk = ob.shape_key_add(name=k)
            co = (P + gl2bl(np.array(d).reshape(-1, 3))).ravel()
            sk.data.foreach_set('co', co)
    ob.parent = arm
    mod = ob.modifiers.new('arm', 'ARMATURE'); mod.object = arm
    return ob


def setup_scene(res):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('WH_SAMPLES', 20))
    sc.cycles.use_denoising = False; sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 16
    sc.render.resolution_x = res; sc.render.resolution_y = res; sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.42, 0.44, 0.48, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    for nm, rot, en in [('key', (50, 0, 30), 3.2), ('rim', (60, 0, 200), 1.5)]:
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = en
        lo = bpy.data.objects.new(nm, ld); lo.rotation_euler = Euler([math.radians(x) for x in rot]); sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    return cam


def frame_cam(cam, center, height, yaw_deg, lens=60):
    cam.data.lens = lens
    dist = height / (2 * math.tan(cam.data.angle / 2)) * 1.12
    yaw = math.radians(yaw_deg)
    cam.location = Vector(center) + Vector((math.sin(yaw) * dist, -math.cos(yaw) * dist, 0))
    d = Vector(center) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def world_pts(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg); m = oe.to_mesh()
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co); oe.to_mesh_clear()
    co = co.reshape(-1, 3)
    M = np.array(ob.matrix_world)
    return co @ M[:3, :3].T + M[:3, 3]


for job in jobs:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cam = setup_scene(job.get('res', 1024))
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, '..', 'tpl', job['template'] + '.glb'))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.data.shape_keys)
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o is not body and not o.parent:
            bpy.data.objects.remove(o)
    for i, m in enumerate(body.data.materials):  # the game tints the untextured MB-Lab skin with the skin tone
        if 'skin' in m.name.lower() and m.use_nodes and 'Principled BSDF' in m.node_tree.nodes:
            m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = tuple(job.get('skin', (0.55, 0.33, 0.21))) + (1,)
    tint = tuple(job['tint']) if job.get('tint') else None
    parts = [build_part(pid, job['template'], arm, tint) for pid in job.get('parts', [])]
    if job.get('parts'):  # fitted lashes replace the template's own eyelash strip (same rule as the runtime)
        if any(assets[p]['kind'] == 'eyelashes' for p in job['parts']):
            for i, m in enumerate(body.data.materials):
                if 'eyelash' in m.name.lower():
                    body.data.materials[i] = bpy.data.materials.new('hidden')
                    body.data.materials[i].use_nodes = True
                    n = body.data.materials[i].node_tree.nodes
                    n.remove(n['Principled BSDF']); tr = n.new('ShaderNodeBsdfTransparent')
                    body.data.materials[i].node_tree.links.new(tr.outputs[0], n['Material Output'].inputs[0])
    for k, v in (job.get('morphs') or {}).items():
        for ob in [body] + parts:
            if ob.data.shape_keys and k in ob.data.shape_keys.key_blocks:
                kb = ob.data.shape_keys.key_blocks[k]; kb.slider_min = -1; kb.value = v
    if job.get('clip'):
        bpy.ops.import_scene.gltf(filepath=job['clip'])
        acts = [a for a in bpy.data.actions if a.name.startswith(job.get('clip_action', ''))]
        arm.animation_data_create(); arm.animation_data.action = acts[0]
        bpy.context.scene.frame_set(job.get('frame', 1))
    if job.get('aim'):  # fight stance: point bones along armature-space directions, parents first
        from mathutils import Matrix
        for bn, spec in job['aim']:
            pb = arm.pose.bones.get(bn)
            if not pb:
                continue
            bpy.context.view_layer.update()
            M = pb.matrix.copy()
            if 'dir' in spec:
                cur = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
                q = cur.rotation_difference(Vector(spec['dir']).normalized())
            else:  # turn: rotate about an armature axis by degrees
                q = Matrix.Rotation(math.radians(spec['deg']), 4, spec['axis']).to_quaternion()
            R = q.to_matrix().to_4x4()
            loc = M.to_translation()
            NM = R @ M; NM.translation = loc
            pb.matrix = NM
        bpy.context.view_layer.update()
    if job.get('pose'):
        for bn, rot in job['pose'].items():
            pb = arm.pose.bones.get(bn)
            if pb:
                pb.rotation_mode = 'XYZ'; pb.rotation_euler = Euler([math.radians(x) for x in rot])
    bpy.context.view_layer.update()
    P = world_pts(body)
    eyes = None
    for view in job['views']:
        if view['kind'] == 'body':
            lo, hi = P.min(0), P.max(0)
            ctr = (lo + hi) / 2; h = hi[2] - lo[2]
            frame_cam(cam, ctr, h, view.get('yaw', 0), 50)
        else:
            top = P[:, 2].max()
            hh = 0.30 if view['kind'] == 'head' else 0.62
            sel = P[P[:, 2] > top - hh]
            ctr = sel.mean(0); ctr[2] = top - hh / 2 + 0.01
            frame_cam(cam, ctr, hh * 1.05, view.get('yaw', 0), 85)
        out = job['out_prefix'] + '_' + view['name'] + '.png'
        bpy.context.scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print('[render]', out, flush=True)
