"""cloth_render.py — Blender 4.3 headless proof renders for the CLOTHING + ACCESSORIES phase (Cycles CPU).

Run:  blender -b -P cloth_render.py -- jobs.json
jobs.json: [{template, items:[item-id], tints:{item-id:[r,g,b]}, morphs:{shape-key: value}, aim:[[bone, spec]],
             views:[{name, kind:'body'|'upper'|'lower'|'feet'|'hands'|'head', yaw}], out_prefix, res, skin:[r,g,b]}]
Items come from fit/<item>/<template>.json (shell_fit.py / mh_blender.py output): skinned to the template armature
with their weights (Armature modifier) and carrying their shape keys, so a slider value set on the body is set on
every garment with the same key name and a pose moves them by their weights. The body triangles each garment hides
(its hide lists, same data the runtime uses) are deleted from the body before rendering.
"""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Euler, Matrix
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from items import BY_ID  # noqa: E402
jobs = json.load(open(sys.argv[sys.argv.index('--') + 1]))
MH = '/workspace/work/hairpipe/mhzip'


def gl2bl(P):
    return np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)


def item_material(it, tint=None):
    m = bpy.data.materials.new(it['id'])
    m.use_nodes = True
    nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    c = tint or it['color']
    bs.inputs['Base Color'].default_value = (*c, 1)
    bs.inputs['Roughness'].default_value = it.get('rough', 0.6)
    tex = None
    if it['kind'] == 'mh':
        d = os.path.join(MH, it['src']); nm = os.path.basename(it['src'])
        for line in open(os.path.join(d, nm + '.mhmat')):
            if line.startswith('diffuseTexture'):
                tex = os.path.join(d, line.split()[1])
    if tex and os.path.exists(tex):  # same as the runtime: greyscale texture x tint
        im = nt.nodes.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(tex)
        bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(im.outputs['Color'], bw.inputs['Color'])
        gain = nt.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = it.get('_gain', 1.6)
        nt.links.new(bw.outputs[0], gain.inputs[0])
        mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
        mix.inputs[1].default_value = (*c, 1)
        cr = nt.nodes.new('ShaderNodeCombineColor')
        for k in range(3):
            nt.links.new(gain.outputs[0], cr.inputs[k])
        nt.links.new(cr.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], bs.inputs['Base Color'])
    return m


def build_item(iid, tpl, arm, tint=None):
    it = BY_ID[iid]
    J = json.load(open(os.path.join(HERE, 'fit', iid, tpl + '.json')))
    P = gl2bl(np.array(J['pos']).reshape(-1, 3)); F = np.array(J['idx']).reshape(-1, 3)
    me = bpy.data.meshes.new(iid); me.from_pydata(P.tolist(), [], F.tolist()); me.update()
    if J.get('uv'):
        uv = np.array(J['uv']).reshape(-1, 2)
        ul = me.uv_layers.new(name='UV')
        loops = np.empty(len(me.loops), int); me.loops.foreach_get('vertex_index', loops)
        ul.data.foreach_set('uv', uv[loops].ravel())
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(iid, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(item_material(it, tint))
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
            sk.data.foreach_set('co', (P + gl2bl(np.array(d).reshape(-1, 3))).ravel())
    ob.parent = arm
    mod = ob.modifiers.new('arm', 'ARMATURE'); mod.object = arm
    return ob, J


def hide_body(body, tpl, hides):
    dump = json.load(open(os.path.join(HERE, 'dumps', tpl + '.json')))['prims']
    co = np.empty(len(body.data.vertices) * 3); body.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(body.matrix_world); co = co @ M[:3, :3].T + M[:3, 3]
    tree = cKDTree(co)
    kill = set()
    for prim in ('skin', 'generic', 'nails'):
        idx = sorted(set(i for h in hides for i in h.get(prim, [])))
        if not idx:
            continue
        D = gl2bl(np.array(dump[prim]['pos']).reshape(-1, 3))[idx]
        dd, j = tree.query(D, k=4)  # seam duplicates share a position
        for row_d, row_j in zip(dd, j):
            kill.update(int(jj) for d_, jj in zip(row_d, row_j) if d_ < 1e-5)
    if not kill:
        return 0
    bm = bmesh.new(); bm.from_mesh(body.data)
    dead = [f for f in bm.faces if all(v.index in kill for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context='FACES_ONLY')
    bm.to_mesh(body.data); bm.free()
    return len(dead)


def setup_scene(res):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('WH_SAMPLES', 20))
    sc.cycles.use_denoising = False; sc.cycles.max_bounces = 4
    sc.render.resolution_x = res; sc.render.resolution_y = res
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.42, 0.44, 0.48, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    for nm, rot, en in [('key', (50, 0, 30), 3.2), ('rim', (60, 0, 200), 1.5)]:
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = en
        lo = bpy.data.objects.new(nm, ld); lo.rotation_euler = Euler([math.radians(x) for x in rot]); sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    return cam


def frame_cam(cam, center, height, yaw_deg, lens=60, pitch=0.0):
    cam.data.lens = lens
    dist = height / (2 * math.tan(cam.data.angle / 2)) * 1.12
    yaw = math.radians(yaw_deg); pt = math.radians(pitch)
    cam.location = Vector(center) + Vector((math.sin(yaw) * dist * math.cos(pt), -math.cos(yaw) * dist * math.cos(pt), dist * math.sin(pt)))
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
    cam = setup_scene(job.get('res', 768))
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, '..', 'hairpipe', 'tpl', job['template'] + '.glb'))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.data.shape_keys)
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o is not body and not o.parent:
            bpy.data.objects.remove(o)
    for m in body.data.materials:
        if 'skin' in m.name.lower() and m.use_nodes and 'Principled BSDF' in m.node_tree.nodes:
            m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = tuple(job.get('skin', (0.55, 0.33, 0.21))) + (1,)
    tints = job.get('tints', {})
    built = [build_item(i, job['template'], arm, tints.get(i)) for i in job.get('items', [])]
    if not job.get('no_hide'):
        hide_body(body, job['template'], [J.get('hide', {}) for _, J in built])
    parts = [ob for ob, _ in built]
    for k, v in (job.get('morphs') or {}).items():
        for ob in [body] + parts:
            if ob.data.shape_keys and k in ob.data.shape_keys.key_blocks:
                kb = ob.data.shape_keys.key_blocks[k]; kb.slider_min = -1; kb.value = v
    for bn, spec in job.get('aim') or []:
        pb = arm.pose.bones.get(bn)
        if not pb:
            continue
        bpy.context.view_layer.update()
        M = pb.matrix.copy()
        if 'dir' in spec:
            cur = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
            q = cur.rotation_difference(Vector(spec['dir']).normalized())
        else:
            q = Matrix.Rotation(math.radians(spec['deg']), 4, spec['axis']).to_quaternion()
        R = q.to_matrix().to_4x4(); loc = M.to_translation()
        NM = R @ M; NM.translation = loc
        pb.matrix = NM
    bpy.context.view_layer.update()
    P = world_pts(body)
    lo, hi = P.min(0), P.max(0); h = hi[2] - lo[2]
    for view in job['views']:
        k = view['kind']; yaw = view.get('yaw', 0)
        if k == 'body':
            frame_cam(cam, (lo + hi) / 2, h, yaw, 50)
        else:
            zc, hh, xc = {'upper': (0.72, 0.42, 0), 'lower': (0.45, 0.45, 0), 'feet': (0.10, 0.22, None),
                          'hands': (0.62, 0.20, None), 'head': (0.93, 0.18, 0), 'legs': (0.28, 0.56, 0)}[k]
            c = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2] + zc * h))
            if k == 'hands':
                c.x = hi[0] - 0.09 * h
                sel = P[P[:, 0] > hi[0] - 0.2 * h]; c.z = float(sel[:, 2].mean())
            if k == 'feet':
                sel = P[P[:, 2] < lo[2] + 0.12 * h]; c.x = 0; c.y = float(sel[:, 1].mean())
            frame_cam(cam, c, hh * h, yaw, 70, view.get('pitch', 8 if k in ('feet', 'hands') else 0))
        out = job['out_prefix'] + '_' + view['name'] + '.png'
        bpy.context.scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print('[render]', out, flush=True)
