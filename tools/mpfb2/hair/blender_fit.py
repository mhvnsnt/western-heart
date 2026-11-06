"""blender_fit.py — HAIR phase, Blender stage (Blender 4.3 headless, Cycles-free: no render here).

Run:  blender -b -P blender_fit.py -- <template-id> [asset-id ...]

Input : tpl/<template>.glb  (template body, meshopt-decoded by decode.mjs so Blender's glTF importer reads it)
        fit/<asset>/<template>.json  (fit_proxies.py: MakeHuman .mhclo fit + head transfer, field pos_w = glTF
        world bind positions in metres, uv, idx)
Output: fitbl/<asset>/<template>.json  {pos (glTF model space, metres), uv, idx, joints[4], weights[4]
        (joint indices = the template glTF skin joint order), targets{name: deltas}, stats}

Per part, in Blender:
 1. part mesh built from the numpy fit (bind pose, world).
 2. hair only — shoulder/neck clipping fix: Shrinkwrap (OUTSIDE, nearest surface point, 5 mm offset) against the
    template skin, so no hair vertex sits inside the neck/shoulders/back at bind; the head region keeps its fit.
 3. skin weights: Data Transfer (vertex groups, nearest face interpolated) from the template skin, then limited to
    head / neck / upper spine / clavicles (hair, beards); brows + lashes stay 100 % head. Weights smoothed along the
    part's own edges for hair so long strands bend gradually from head -> neck -> upper back.
 4. shape keys: Surface Deform bound to the template skin at basis; every body shape key is set to 1 in turn and
    the deformed part read back -> part morph target under the same name (face sliders drive brows / lashes /
    beards / hairline; head-shape sliders drive the hair).
"""
import bpy, bmesh, sys, os, json, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index('--') + 1:]
TPL = argv[0]
ONLY = set(argv[1:])
assets = json.load(open(os.path.join(HERE, 'assets.json')))
dump = json.load(open(os.path.join(HERE, 'dumps', TPL + '.json')))
JOINTS = dump['joints']

HAIR_TARGETS = re.compile(r'^(f_head_[wh]|f_fh_|f_temples|f_round|f_square|f_tri|f_ear_size|f_ear_w|f_ear_angle|b_head_size)[+-]$')
ALLOWED = {'hair': ['head', 'neck', 'spine03', 'spine02', 'clavicle_L', 'clavicle_R'],
           'beard': ['head', 'neck'], 'eyebrows': ['head'], 'eyelashes': ['head']}


def gl2bl(P):
    return np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)


def bl2gl(P):
    return np.stack([P[:, 0], P[:, 2], -P[:, 1]], 1)


def override(obj):
    return bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj], selected_editable_objects=[obj])


def apply_mod(obj, name):
    with override(obj):
        bpy.ops.object.modifier_apply(modifier=name)


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, '..', 'tpl', TPL + '.glb'))
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.data.shape_keys)
# skin-only copy of the body (keeps vertex groups + shape keys) = transfer source
skin = body.copy(); skin.data = body.data.copy(); skin.name = 'skin_src'
bpy.context.scene.collection.objects.link(skin)
for m in list(skin.modifiers):
    skin.modifiers.remove(m)
skin.parent = None; skin.matrix_world = body.matrix_world.copy()
skin_mat = [i for i, m in enumerate(skin.data.materials) if re.search('skin', m.name, re.I)][0]
bm = bmesh.new(); bm.from_mesh(skin.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != skin_mat], context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(skin.data); bm.free()
keys = skin.data.shape_keys.key_blocks
key_names = [k.name for k in keys][1:]
print('[bl]', TPL, 'skin verts', len(skin.data.vertices), 'shape keys', len(key_names), flush=True)

parts = []
for a in assets:
    if ONLY and a['id'] not in ONLY:
        continue
    J = json.load(open(os.path.join(HERE, 'fit', a['id'], TPL + '.json')))
    P = gl2bl(np.array(J['pos_w']).reshape(-1, 3))
    F = np.array(J['idx']).reshape(-1, 3)
    me = bpy.data.meshes.new(a['id'])
    me.from_pydata(P.tolist(), [], F.tolist())
    me.update()
    ob = bpy.data.objects.new(a['id'], me)
    bpy.context.scene.collection.objects.link(ob)
    parts.append(dict(a=a, ob=ob, J=J, F=F))

dg = bpy.context.evaluated_depsgraph_get()


def eval_co(ob):
    oe = ob.evaluated_get(dg)
    m = oe.to_mesh()
    co = np.empty(len(m.vertices) * 3); m.vertices.foreach_get('co', co)
    oe.to_mesh_clear()
    return co.reshape(-1, 3)


def edges_of(F):
    E = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    return np.unique(np.sort(E, 1), axis=0)


for p in parts:
    ob, kind = p['ob'], p['a']['kind']
    n = len(ob.data.vertices)
    # ---- 2. shoulder / neck clipping fix (hair) ----
    moved = 0.0
    if kind == 'hair':
        before = np.array([v.co[:] for v in ob.data.vertices])
        sw = ob.modifiers.new('clear', 'SHRINKWRAP')
        sw.target = skin; sw.wrap_method = 'NEAREST_SURFACEPOINT'; sw.wrap_mode = 'OUTSIDE'; sw.offset = 0.005
        apply_mod(ob, 'clear')
        after = np.array([v.co[:] for v in ob.data.vertices])
        # spread the push over the strand (Laplacian smoothing of the displacement field, pushed vertices keep at
        # least their own push) so strands lift off the shoulders as a sheet instead of single vertices snapping
        # onto the skin; a second Shrinkwrap pass then catches anything the smoothing left inside.
        D = after - before; D0 = D.copy(); m0 = np.linalg.norm(D0, axis=1)
        E = edges_of(p['F'])
        for _ in range(25):
            acc = np.zeros_like(D); cnt = np.zeros(n)
            np.add.at(acc, E[:, 0], D[E[:, 1]]); np.add.at(acc, E[:, 1], D[E[:, 0]])
            np.add.at(cnt, E[:, 0], 1); np.add.at(cnt, E[:, 1], 1)
            D = np.where(cnt[:, None] > 0, acc / np.maximum(cnt, 1)[:, None], D)
            keep = m0 > np.linalg.norm(D, axis=1)
            D[keep] = D0[keep]
        for v, c in zip(ob.data.vertices, before + D):
            v.co = c
        sw = ob.modifiers.new('clear2', 'SHRINKWRAP')
        sw.target = skin; sw.wrap_method = 'NEAREST_SURFACEPOINT'; sw.wrap_mode = 'OUTSIDE'; sw.offset = 0.005
        apply_mod(ob, 'clear2')
        after = np.array([v.co[:] for v in ob.data.vertices])
        moved = float(np.linalg.norm(after - before, axis=1).max())
        p['n_pushed'] = int((np.linalg.norm(after - before, axis=1) > 1e-4).sum())
    # ---- 3. skin weights ----
    dt = ob.modifiers.new('dt', 'DATA_TRANSFER')
    dt.object = skin; dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'
    dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
    with override(ob):
        bpy.ops.object.datalayout_transfer(modifier='dt')
    apply_mod(ob, 'dt')
    allowed = ALLOWED[kind]
    W = np.zeros((n, len(allowed)))
    gidx = {g.index: g.name for g in ob.vertex_groups}
    other = np.zeros(n)
    for v in ob.data.vertices:
        for g in v.groups:
            nm = gidx[g.group]
            if nm in allowed:
                W[v.index, allowed.index(nm)] += g.weight
            else:
                other[v.index] += g.weight
    # weight that sat on disallowed bones (upper arms, breasts, lower spine) goes to the nearest allowed parent
    fallback = {'hair': 'spine03', 'beard': 'neck'}.get(kind, 'head')
    W[:, allowed.index(fallback)] += other
    if kind == 'hair':
        E = edges_of(p['F'])
        for _ in range(6):
            acc = np.zeros_like(W); cnt = np.zeros(n)
            np.add.at(acc, E[:, 0], W[E[:, 1]]); np.add.at(acc, E[:, 1], W[E[:, 0]])
            np.add.at(cnt, E[:, 0], 1); np.add.at(cnt, E[:, 1], 1)
            W = np.where(cnt[:, None] > 0, 0.5 * W + 0.5 * acc / np.maximum(cnt, 1)[:, None], W)
    s = W.sum(1); W[s == 0, 0] = 1.0; W /= W.sum(1, keepdims=True)
    names_ext = list(allowed) + [allowed[0]] * max(0, 4 - len(allowed))
    W = np.hstack([W, np.zeros((n, len(names_ext) - len(allowed)))])
    order = np.argsort(-W, 1, kind='stable')[:, :4]
    Wt = np.take_along_axis(W, order, 1)
    Wt[Wt < 0.01] = 0; Wt /= Wt.sum(1, keepdims=True)
    Jt = np.array([JOINTS.index(nm) for nm in names_ext])[order]
    Jt[Wt == 0] = 0
    p['joints'] = Jt; p['weights'] = Wt
    p['wstats'] = {nm: round(float((W[:, i] > 0.01).mean()), 3) for i, nm in enumerate(allowed)}
    # ---- 4. surface deform for shape keys ----
    for g in list(ob.vertex_groups):
        ob.vertex_groups.remove(g)
    sd = ob.modifiers.new('sd', 'SURFACE_DEFORM')
    sd.target = skin; sd.falloff = 4.0
    with override(ob):
        bpy.ops.object.surfacedeform_bind(modifier='sd')
    p['moved'] = moved

dg.update()
for p in parts:
    if not p['ob'].modifiers['sd'].is_bound:
        print('[bl] WARN surface deform not bound', p['a']['id'], flush=True)
    p['base'] = eval_co(p['ob'])
    p['targets'] = {}

for kn in key_names:
    keys[kn].value = 1.0
    dg.update()
    for p in parts:
        kind = p['a']['kind']
        if kind == 'hair' and not HAIR_TARGETS.match(kn):
            continue
        d = eval_co(p['ob']) - p['base']
        thr = 0.0015 if kind == 'hair' else 0.0006
        if np.abs(d).max() >= thr:
            p['targets'][kn] = bl2gl(d)
    keys[kn].value = 0.0

out_root = os.path.join(HERE, 'fitbl')
summary = {}
for p in parts:
    a, J = p['a'], p['J']
    pos = bl2gl(p['base'])
    od = os.path.join(out_root, a['id']); os.makedirs(od, exist_ok=True)
    stats = dict(verts=len(pos), targets=len(p['targets']), shoulder_push_max_m=round(p['moved'], 4),
                 verts_pushed=p.get('n_pushed', 0), weight_share=p['wstats'])
    json.dump(dict(id=a['id'], template=TPL, kind=a['kind'], space='model-bind', pos=pos.round(6).ravel().tolist(),
                   uv=J['uv'], idx=J['idx'], joints=p['joints'].ravel().tolist(),
                   weights=p['weights'].round(4).ravel().tolist(), joint_names=JOINTS,
                   targets={k: v.round(6).ravel().tolist() for k, v in p['targets'].items()}, stats=stats),
              open(os.path.join(od, TPL + '.json'), 'w'))
    summary[a['id']] = stats
    print('[bl]', TPL, a['id'], json.dumps(stats), flush=True)
json.dump(summary, open(os.path.join(out_root, '_report_' + TPL + '.json'), 'w'), indent=1)
