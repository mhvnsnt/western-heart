"""shell_fit.py — CLOTHING + ACCESSORIES phase, Blender stage for the GENERATED (original CC0) garments.

Run:  blender -b -P shell_fit.py -- <template-id> [item-id ...]

Input : tpl/<template>.glb (meshopt-decoded template body), dumps/<template>.json (dump_prims.mjs: the GLB's own skin /
        generic (underwear) / nails vertex order, world bind space), items.py.
Output: fit/<item>/<template>.json {pos (glTF world bind, metres), idx, joints[4], weights[4] (template skin joint
        order), joint_names, targets{slider name: deltas}, hide{skin, generic, nails: GLB vertex indices the garment
        covers}, src (nearest template skin vertex per garment vertex, for the proof test), offset, stats}

Per garment, in Blender, on the template's own body surface (skin + the MB-Lab 'generic' underwear patch, welded):
 1. region = a scalar field in metres, >= 0 inside: AND / OR (min / max) of the template's own bone-weight labels
    (Blender vertex groups summed into torso / upper arm / forearm / hand / thigh / calf / foot / neck+head; a label
    term is 0 on the 50 % weight seam) and cut lines measured along the template's own bones (armature bind heads:
    hip / knee / ankle / shoulder / elbow / wrist, waist + chest heights), so one rule lands at the same anatomical
    place on all 9 bodies (male and female topologies differ).
 2. the surface is CLIPPED along the field's zero line (edge points interpolated), so hems, straps and cuffs are clean
    lines instead of the body's triangle staircase.
 3. shell: every vertex pushed out along the surface normal by the item offset (+ a puff profile tapered to the edge
    for pads, a thicker sole for boots, knuckle padding for open-finger gloves).
    Skin weights: the source surface's own vertex-group weights, interpolated at clipped edge points (= a Data
    Transfer at distance 0), top 4.
 4. shape keys: for every body shape key (the 168 slider targets) the shell is rebuilt from that key's coordinates AND
    that key's normals, so a slider moves the garment with the body and the offset follows the new surface; deltas
    under 0.5 mm are dropped.
 5. body hide: body vertices >= 4 mm inside the region (+ the nails under full gloves / boots), as GLB vertex indices,
    so the runtime drops the body triangles under the garment (no poke-through at bends under the cloth).
"""
import bpy, bmesh, sys, os, json, re
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from items import ITEMS  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:]
TPL = argv[0]
ONLY = set(argv[1:])
HAIRDUMP = json.load(open('/workspace/work/hairpipe/pipe/dumps/' + TPL + '.json'))
JOINTS = HAIRDUMP['joints']
DUMP = json.load(open(os.path.join(HERE, 'dumps', TPL + '.json')))['prims']


def bl2gl(P):
    return np.stack([P[:, 0], P[:, 2], -P[:, 1]], 1)


def gl2bl(P):
    return np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, '..', 'hairpipe', 'tpl', TPL + '.glb'))
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
body = next(o for o in bpy.data.objects if o.type == 'MESH' and o.data.shape_keys)
MW = np.array(body.matrix_world)
H = {b.name: np.array(arm.matrix_world @ b.head_local) for b in arm.data.bones}

# body surface = skin + generic (underwear patch) faces, welded at their shared border (keeps groups + shape keys)
skin = body.copy(); skin.data = body.data.copy(); skin.name = 'surf_src'
bpy.context.scene.collection.objects.link(skin)
for m in list(skin.modifiers):
    skin.modifiers.remove(m)
keep_mats = [i for i, m in enumerate(skin.data.materials) if re.search('skin|generic', m.name, re.I)]
bm = bmesh.new(); bm.from_mesh(skin.data)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep_mats], context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bm.to_mesh(skin.data); bm.free()
me = skin.data
n = len(me.vertices)
me.calc_loop_triangles()
TRI = np.array([t.vertices[:] for t in me.loop_triangles])


def world(c):
    return c @ MW[:3, :3].T + MW[:3, 3]


keys = me.shape_keys.key_blocks
KEYS = [k.name for k in keys][1:]
a = np.empty(n * 3); keys[0].data.foreach_get('co', a); P = world(a.reshape(-1, 3))
KCO = {}
for k in KEYS:
    a = np.empty(n * 3); keys[k].data.foreach_get('co', a); KCO[k] = world(a.reshape(-1, 3))

# surface vertex -> GLB vertex indices per primitive (a welded border vertex maps into both skin and generic)
GLBMAP = {}
for prim in ('skin', 'generic'):
    D = gl2bl(np.array(DUMP[prim]['pos']).reshape(-1, 3))
    tree = cKDTree(D)
    GLBMAP[prim] = tree.query_ball_point(P, 2e-5)
nomatch = sum(1 for i in range(n) if not GLBMAP['skin'][i] and not GLBMAP['generic'][i])
assert nomatch == 0, ('unmapped surface vertices', nomatch)
SKIN1 = np.array([(GLBMAP['skin'][i] or [-1])[0] for i in range(n)])  # -1 = generic-only vertex
Dnails = gl2bl(np.array(DUMP['nails']['pos']).reshape(-1, 3))

# vertex-group weights -> body-part labels
GN = [g.name for g in skin.vertex_groups]
gi = {nm: i for i, nm in enumerate(GN)}
W = np.zeros((n, len(GN)))
for v in me.vertices:
    for g in v.groups:
        W[v.index, g.group] = g.weight
W /= np.maximum(W.sum(1, keepdims=True), 1e-9)


def gsum(names):
    return sum((W[:, gi[nm]] for nm in names if nm in gi), np.zeros(n))


FING = ['thumb01', 'thumb02', 'thumb03'] + [f'{f}{k:02d}' for f in ('index', 'middle', 'ring', 'pinky') for k in range(4)]
LAB = {'torso': gsum(['root', 'pelvis', 'spine01', 'spine02', 'spine03', 'clavicle_L', 'clavicle_R', 'breast_L', 'breast_R']),
       'neckhead': gsum(['neck', 'head']), 'uarm': 0, 'farm': 0, 'hand': 0, 'thigh': 0, 'calf': 0, 'foot': 0}
for s in 'LR':
    LAB['uarm'] = LAB['uarm'] + gsum([f'upperarm_{s}', f'upperarm_twist_{s}'])
    LAB['farm'] = LAB['farm'] + gsum([f'lowerarm_{s}', f'lowerarm_twist_{s}'])
    LAB['hand'] = LAB['hand'] + gsum([f'hand_{s}'] + [f'{f}_{s}' for f in FING])
    LAB['thigh'] = LAB['thigh'] + gsum([f'thigh_{s}', f'thigh_twist_{s}'])
    LAB['calf'] = LAB['calf'] + gsum([f'calf_{s}', f'calf_twist_{s}'])
    LAB['foot'] = LAB['foot'] + gsum([f'foot_{s}', f'toes_{s}'])

x, y, z = P[:, 0], P[:, 1], P[:, 2]


def side_t(a, b):
    """param along the side's own bone a->b: 0 at a's head, 1 at b's head; and the bone length"""
    out = np.zeros(n)
    for s, m in (('L', x >= 0), ('R', x < 0)):
        A, B = H[f'{a}_{s}'], H[f'{b}_{s}']
        out[m] = ((P[m] - A) @ (B - A)) / np.dot(B - A, B - A)
    return out, float(np.linalg.norm(H[f'{b}_L'] - H[f'{a}_L']))


S = (H['neck'][2] - H['pelvis'][2]) / (1.563 - 0.889)  # body scale vs the technician
z_hip = H['thigh_L'][2]
z_waist = z_hip + 0.6 * (H['spine01'][2] - z_hip)
z_chest = H['breast_L'][2]
z_clav = H['clavicle_L'][2]
t_thigh, LEN_T = side_t('thigh', 'calf')
t_calf, LEN_C = side_t('calf', 'foot')
t_uarm, LEN_U = side_t('upperarm', 'lowerarm')
t_farm, LEN_F = side_t('lowerarm', 'hand')
_ND = np.array(HAIRDUMP['node_matrix']).reshape(4, 4).T  # the dump's eye positions are raw (quantised) accessor values
_E = np.array(HAIRDUMP['prims']['eyes']['pos']).reshape(-1, 3)
eyes = gl2bl(_E @ _ND[:3, :3].T + _ND[:3, 3])
z_eye = eyes[:, 2].mean()
x_strap = 0.55 * abs(H['upperarm_L'][0])


def L(*labs):
    """label membership: 0 on the 50 % weight seam, + inside (metres-ish scale)"""
    return (sum(LAB[l] for l in labs) - 0.5) * 0.06


AND = lambda *f: np.minimum.reduce(f)
OR = lambda *f: np.maximum.reduce(f)
neck_r = np.hypot(x - H['neck'][0], y - H['neck'][1])
front = np.clip(-(y - H['neck'][1]) / 0.05, 0, 1)
z_collar = z_clav - 0.02 * S - 0.035 * S * front
NECK_OK = AND((0.5 - LAB['neckhead']) * 0.06, OR(neck_r - 0.085 * S, z_collar - z))
ARMHOLE = (0.15 - LAB['uarm']) * 0.1
STRAPBAND = 0.03 * S - np.abs(np.abs(x) - x_strap)
fing_far = gsum([g for g in GN if re.match(r'^(thumb0[23]|(index|middle|ring|pinky)0[23])_', g)])


def straps(lo):
    return AND(L('torso'), NECK_OK, ARMHOLE, OR(lo - z, STRAPBAND))


GEN = np.array([1.0 if GLBMAP['generic'][i] else 0.0 for i in range(n)])
UNDER = AND((GEN - 0.5) * 0.06, z_chest - 0.10 * S - z)  # the body's own briefs patch


def lower(f):
    return OR(f, UNDER)


REG = {
    'trunks': lambda: lower(AND(L('torso', 'thigh'), z_waist - z, (0.30 - t_thigh) * LEN_T)),
    'tights': lambda: lower(AND(L('torso', 'thigh', 'calf'), z_waist - z, (0.93 - t_calf) * LEN_C)),
    'shorts': lambda: lower(AND(L('torso', 'thigh'), z_waist + 0.01 * S - z, (0.62 - t_thigh) * LEN_T)),
    'compression': lambda: AND(L('torso', 'uarm', 'farm'), z - (z_waist - 0.05 * S), NECK_OK, (0.85 - t_farm) * LEN_F),
    'tee': lambda: AND(L('torso', 'uarm'), z - (z_waist - 0.07 * S), NECK_OK, (0.45 - t_uarm) * LEN_U),
    'tank': lambda: AND(straps(z_chest + 0.03 * S), z - (z_waist - 0.05 * S)),
    'crop': lambda: AND(straps(z_chest + 0.03 * S), z - (z_chest - 0.085 * S)),
    'singlet': lambda: lower(AND(L('torso', 'thigh'), NECK_OK, ARMHOLE, OR(z_chest + 0.03 * S - z, STRAPBAND), (0.30 - t_thigh) * LEN_T)),
    'gloves_full': lambda: AND(L('hand', 'farm'), (t_farm - 0.86) * LEN_F),
    'gloves_open': lambda: AND(L('hand', 'farm'), (t_farm - 0.86) * LEN_F, (0.35 - fing_far) * 0.06),
    'boots_knee': lambda: AND(L('foot', 'calf'), (t_calf - 0.14) * LEN_C),
    'boots_ankle': lambda: AND(L('foot', 'calf'), (t_calf - 0.80) * LEN_C),
    'kneepads': lambda: AND(L('thigh', 'calf'), (0.15 - np.abs(t_thigh - 1.0)) * LEN_T),
    'elbowpads': lambda: AND(L('uarm', 'farm'), (0.17 - np.abs(t_uarm - 1.0)) * LEN_U),
    'wrist': lambda: AND(L('farm', 'hand'), (t_farm - 0.80) * LEN_F, (1.03 - t_farm) * LEN_F),
    'armbands': lambda: AND(L('uarm'), (t_uarm - 0.36) * LEN_U, (0.58 - t_uarm) * LEN_U),
    'headband': lambda: AND(L('neckhead'), z - (z_eye + 0.032 * S), (z_eye + 0.062 * S) - z, z - H['head'][2]),
    'belt': lambda: AND(L('torso', 'thigh'), z - (z_waist - 0.012 * S), (z_waist + 0.045 * S) - z),
}


def normals(Pk):
    nn = np.zeros_like(Pk)
    fn = np.cross(Pk[TRI[:, 1]] - Pk[TRI[:, 0]], Pk[TRI[:, 2]] - Pk[TRI[:, 0]])
    for k in range(3):
        np.add.at(nn, TRI[:, k], fn)
    return nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-12)


NB = normals(P)
NK = {k: normals(KCO[k]) for k in KEYS}
smooth01 = lambda u: np.clip(u, 0, 1) ** 2 * (3 - 2 * np.clip(u, 0, 1))


def offset_field(item, f):
    off = np.full(n, item['offset'])
    r = item['region']
    edge = smooth01(f / 0.02)  # 0 at the hem -> 1 two cm inside
    if r == 'kneepads':
        u = np.clip(1 - np.abs(t_thigh - 1.0) / 0.15, 0, 1)
        off += item['puff'] * np.sin(u * np.pi / 2) ** 0.7 * np.clip(-NB[:, 1] * 1.2 + 0.2, 0, 1) * edge
    elif r == 'elbowpads':
        u = np.clip(1 - np.abs(t_uarm - 1.0) / 0.17, 0, 1)
        off += item['puff'] * np.sin(u * np.pi / 2) ** 0.7 * np.clip(NB[:, 1] * 1.2 + 0.2, 0, 1) * edge
    elif r.startswith('boots'):
        off += 0.008 * smooth01((-NB[:, 2] - 0.4) / 0.3) * LAB['foot']  # sole
    elif r == 'gloves_open':
        kn = gsum([g for g in GN if re.match(r'^(index|middle|ring|pinky)0[01]_', g)])
        off += 0.007 * np.clip(kn * 1.5, 0, 1) * np.clip(NB[:, 2] * 1.3, 0, 1) * edge
    return off


def clip_mesh(f):
    """clip the surface triangles to f >= 0. Returns verts as (a, b, s) rows (s=0 -> vertex a) and triangles."""
    vid = {}
    rows = []

    def vert(a, b=None):
        if b is None:
            key = (a, a)
        else:
            key = (min(a, b), max(a, b))
        if key not in vid:
            if b is None:
                rows.append((a, a, 0.0))
            else:
                a0, b0 = key
                s = f[a0] / (f[a0] - f[b0])
                rows.append((a0, b0, float(s)))
            vid[key] = len(rows) - 1
        return vid[key]

    tris = []
    inside = f >= 0
    for t in TRI:
        ins = inside[t]
        if not ins.any():
            continue
        if ins.all():
            tris.append([vert(t[0]), vert(t[1]), vert(t[2])])
            continue
        poly = []
        for k in range(3):
            a_, b_ = t[k], t[(k + 1) % 3]
            if inside[a_]:
                poly.append(vert(a_))
            if inside[a_] != inside[b_]:
                poly.append(vert(a_, b_))
        for k in range(1, len(poly) - 1):
            tris.append([poly[0], poly[k], poly[k + 1]])
    return np.array(rows), np.array(tris, int).reshape(-1, 3)


def drop_islands(V, T, min_area):
    m = len(V)
    par = np.arange(m)

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for t in T:
        r0 = find(t[0])
        for q in t[1:]:
            rq = find(q)
            if rq != r0:
                par[rq] = r0
    root = np.array([find(t[0]) for t in T])
    area = 0.5 * np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1)
    tot = {}
    for r, ar in zip(root, area):
        tot[r] = tot.get(r, 0) + ar
    keep = np.array([tot[r] >= min_area for r in root])
    T = T[keep]
    used = np.unique(T)
    re_ = -np.ones(m, int); re_[used] = np.arange(len(used))
    return used, re_[T]


out_root = os.path.join(HERE, 'fit')
summary = {}
surf_tree = cKDTree(P)
for item in ITEMS:
    if item['kind'] != 'shell' or (ONLY and item['id'] not in ONLY):
        continue
    f = REG[item['region']]()
    off = offset_field(item, f)
    rows, T = clip_mesh(f)
    A, B, Sx = rows[:, 0].astype(int), rows[:, 1].astype(int), rows[:, 2][:, None]
    lerp = lambda X: X[A] * (1 - Sx) + X[B] * Sx
    base_all = P + NB * off[:, None]
    base = lerp(base_all)
    used, T = drop_islands(base, T, 4e-4)  # drop crumbs < 4 cm^2
    A, B, Sx = A[used], B[used], Sx[used]
    base = base[used]
    D = np.zeros_like(base)
    if item['region'].startswith('boots'):
        # boots: smooth the toes / instep into one boot surface (Laplacian over the shell's own edges, foot area only),
        # then keep every vertex at least the item offset outside its source skin point
        E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
        wf = np.clip((lerp(LAB['foot'][:, None])[:, 0] - 0.2) / 0.5, 0, 1)
        X = base.copy()
        for _ in range(int(item.get('smooth', 20))):
            acc = np.zeros_like(X); cnt = np.zeros(len(X))
            np.add.at(acc, E[:, 0], X[E[:, 1]]); np.add.at(acc, E[:, 1], X[E[:, 0]])
            np.add.at(cnt, E[:, 0], 1); np.add.at(cnt, E[:, 1], 1)
            X = X + wf[:, None] * 0.5 * (acc / np.maximum(cnt, 1)[:, None] - X)
        ps, ns = lerp(P), lerp(NB)
        ns /= np.linalg.norm(ns, axis=1, keepdims=True)
        h = np.einsum('ij,ij->i', X - ps, ns)
        X += ns * np.maximum(item['offset'] - h, 0)[:, None]
        D = X - base
        base = X
    targets = {}
    for k in KEYS:
        pk = lerp(KCO[k] + NK[k] * off[:, None]) + D
        dlt = pk - base
        if np.abs(dlt).max() >= 0.0005:
            targets[k] = bl2gl(dlt)
    Wv = lerp(W)
    order = np.argsort(-Wv, 1, kind='stable')[:, :4]
    Wt = np.take_along_axis(Wv, order, 1); Wt[Wt < 2e-3] = 0; Wt /= Wt.sum(1, keepdims=True)
    Jt = np.array([[JOINTS.index(GN[g]) for g in row] for row in order]); Jt[Wt == 0] = 0
    hidev = np.where(f >= 0.004)[0]
    hide = {'skin': sorted({j for i in hidev for j in GLBMAP['skin'][i]}),
            'generic': sorted({j for i in hidev for j in GLBMAP['generic'][i]}), 'nails': []}
    if item['region'] == 'gloves_full' or item['region'].startswith('boots'):
        dn, jn = surf_tree.query(Dnails)
        hs = np.zeros(n, bool); hs[hidev] = True
        hide['nails'] = np.where((dn < 0.02) & hs[jn])[0].tolist()
    src = np.where(Sx[:, 0] < 0.5, A, B)
    od = os.path.join(out_root, item['id']); os.makedirs(od, exist_ok=True)
    offv = (off[A] * (1 - Sx[:, 0]) + off[B] * Sx[:, 0])
    stats = dict(verts=len(base), tris=len(T), targets=len(targets),
                 offset_mm=[round(float(offv.min()) * 1000, 2), round(float(offv.max()) * 1000, 2)],
                 hide={k: len(v) for k, v in hide.items()}, bones=sorted({GN[g] for g in np.unique(order[Wt > 0])}))
    json.dump(dict(id=item['id'], template=TPL, kind='shell', space='model-bind', pos=bl2gl(base).round(6).ravel().tolist(),
                   idx=T.ravel().tolist(), joints=Jt.ravel().tolist(), weights=Wt.round(4).ravel().tolist(), joint_names=JOINTS,
                   targets={k: v.round(6).ravel().tolist() for k, v in targets.items()},
                   hide=hide, src=SKIN1[src].tolist(), offset=offv.round(5).tolist(), stats=stats),
              open(os.path.join(od, TPL + '.json'), 'w'))
    summary[item['id']] = stats
    print('[shell]', TPL, item['id'], json.dumps({k: v for k, v in stats.items() if k != 'bones'}), flush=True)
json.dump(summary, open(os.path.join(out_root, '_shell_report_' + TPL + '.json'), 'w'), indent=1)
