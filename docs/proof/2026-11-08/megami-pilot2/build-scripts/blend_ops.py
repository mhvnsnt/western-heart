"""Blender-side operations for Pilot 2 v2. Run:
blender -b work/pilot2_v2.blend --python scripts/blend_ops.py -- <stage> [args]
Stages: stage0 | anchors | warp | tattoo | body | skindump | export
All coordinates in Blender world space (Z-up, model faces -Y, her right = -X).
"""
import bpy, json, math, os, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BASE = '/home/hatch/workspace/_pilot2-v2-20261108'
argv = sys.argv[sys.argv.index('--') + 1:]
STAGE = argv[0]

BODY = 'Parvati Mesh'
KEY_MESHES = ['Parvati Mesh', 'Eyebrow', 'Eyelashes']
FACE_MATS = {'Face-2', 'Lips-2', 'EyeSocket-2', 'Pupils-2', 'EyeMoisture-3', 'Cornea-2', 'Irises-2', 'Sclera-2'}

def set_key(mesh_name, key_name, value):
    ob = bpy.data.objects[mesh_name]
    kb = ob.data.shape_keys.key_blocks.get(key_name)
    if kb:
        kb.value = value

def evaluated_mesh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return ob.evaluated_get(dg)

def get_basis(ob):
    kb = ob.data.shape_keys.key_blocks['Basis']
    arr = np.empty(len(ob.data.vertices) * 3)
    kb.data.foreach_get('co', arr)
    return arr.reshape(-1, 3)

def get_key_co(ob, name):
    kb = ob.data.shape_keys.key_blocks[name]
    arr = np.empty(len(ob.data.vertices) * 3)
    kb.data.foreach_get('co', arr)
    return arr.reshape(-1, 3)

def set_key_co(ob, name, co):
    kb = ob.data.shape_keys.key_blocks[name]
    kb.data.foreach_set('co', co.astype(np.float64).ravel())
    kb.data.update()

def cam_basis(pos, tgt):
    fwd = (tgt - pos); fwd.normalize()
    up_world = Vector((0, 0, 1))
    right = fwd.cross(up_world)
    if right.length < 1e-6:
        right = Vector((1, 0, 0))
    right.normalize()
    upv = right.cross(fwd); upv.normalize()
    return fwd, right, upv

def ray_dir(pos, tgt, fov_deg, aspect, nx, ny):
    """nx, ny: image-normalized coords (x right, y DOWN) -> world ray direction."""
    fwd, right, upv = cam_basis(pos, tgt)
    tv = math.tan(math.radians(fov_deg) / 2)
    th = tv * aspect
    d = fwd + right * ((2 * nx - 1) * th) + upv * ((1 - 2 * ny) * tv)
    d.normalize()
    return d

def load_cams():
    return json.load(open(f'{BASE}/cam_specs.json'))

def raycast_all(cam, landmarks, value_face):
    """Raycast warp landmarks against evaluated body/brow/lash meshes.
    landmarks: {idx: [nx, ny]}. Returns {idx: {point, mesh}}."""
    for m in KEY_MESHES:
        set_key(m, 'AngelFace', value_face)
    bpy.context.view_layer.update()
    pos = Vector(cam['pos']); tgt = Vector(cam['tgt'])
    trees = {}
    for m in KEY_MESHES:
        ob = bpy.data.objects[m]
        ev = evaluated_mesh(ob)
        trees[m] = BVHTree.FromObject(ev, bpy.context.evaluated_depsgraph_get())
    out = {}
    for idx, (nx, ny) in landmarks.items():
        d = ray_dir(pos, tgt, cam['fov'], cam['aspect'], nx, ny)
        best = None
        for m, tree in trees.items():
            loc, nrm, fi, dist = tree.ray_cast(pos, d)
            if loc is not None and (best is None or dist < best[3]):
                best = (loc, nrm, fi, dist, m)
        if best:
            out[str(idx)] = {'point': [float(v) for v in best[0]], 'mesh': best[4],
                             'normal': [float(v) for v in best[1]]}
    return out

# ---------------------------------------------------------------- stage0
if STAGE == 'stage0':
    for m in KEY_MESHES:
        set_key(m, 'AngelFace', 0.0)
    bpy.context.view_layer.update()
    ob = bpy.data.objects[BODY]
    ev = evaluated_mesh(ob)
    me = ev.data
    verts = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get('co', verts)
    verts = verts.reshape(-1, 3)
    head = verts[verts[:, 2] > 1.10]
    print('EVAL verts', len(verts), 'z max', verts[:, 2].max(), 'head(>1.10) count', len(head))
    print('head x', head[:, 0].min(), head[:, 0].max(), 'y', head[:, 1].min(), head[:, 1].max(), 'z', head[:, 2].min(), head[:, 2].max())
    # key values census
    keys = ob.data.shape_keys.key_blocks
    nz = [(k.name, round(k.value, 3)) for k in keys if abs(k.value) > 1e-4]
    print('non-zero keys on body:', len(nz), nz[:20])
    # forehead + chin anchors (evaluated, AngelFace=0) — from probe data:
    # hairline centre (0,-0.040,1.2407); chin (0.004,-0.046,1.130). All LOCAL
    # space (world = local + (0,0,0.0816), pure translation, no scale/rot).
    forehead = np.array([0.0, -0.040, 1.2407])
    chin = np.array([0.004, -0.046, 1.130])
    HC = np.array([0.0, -0.014, 1.196])
    print('forehead anchor', forehead, 'chin anchor', chin, 'head centre', HC)
    # chest profile: front-most y on centreline at several z
    for z in [1.10, 1.07, 1.04, 1.01, 0.98, 0.95, 0.90]:
        col = verts[(np.abs(verts[:, 0]) < 0.006) & (np.abs(verts[:, 2] - z) < 0.008)]
        if len(col):
            print(f'chest centreline z={z}: front y={col[:,1].min():.4f} (n={len(col)})')
    for x in [0.03, 0.05, 0.07]:
        col = verts[(np.abs(verts[:, 0] - x) < 0.006) & (np.abs(verts[:, 2] - 1.06) < 0.01)]
        if len(col):
            print(f'chest x=+{x} z=1.06: front y={col[:,1].min():.4f} (n={len(col)})')
    # bones of interest (MHX naming)
    arm = bpy.data.objects['Parvati']
    bones = {}
    for bname in ['Hips', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot',
                  'Spine', 'Spine1', 'Spine2', 'Chest', 'Neck', 'Head',
                  'LeftShoulder', 'LeftArm', 'LeftForeArm', 'RightShoulder', 'RightArm', 'RightForeArm',
                  'spine', 'spine-1', 'chest', 'chest-1', 'back', 'neck-1']:
        b = arm.data.bones.get(bname)
        if b:
            bones[bname] = {'head': [round(v, 4) for v in b.head_local], 'tail': [round(v, 4) for v in b.tail_local]}
    json.dump(bones, open(f'{BASE}/bones.json', 'w'), indent=1)
    print('BONES saved', len(bones))
    # camera specs (LOCAL space; gltf = world = local + (0,0,0.0816), axes
    # (x, z, -y)). Distance solved so forehead->chin spans 0.191 of frame height.
    WOFF = np.array([0.0, 0.0, 0.0816])
    def proj_ny(P, pos, tgt, fov_deg=55.0):
        fwd = tgt - pos; fwd = fwd / np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
        upv = np.cross(right, fwd)
        rel = P - pos
        cz = rel @ fwd
        return (rel @ upv) / (cz * math.tan(math.radians(fov_deg) / 2))
    def spec(az_deg, el_deg, dist):
        az, el = math.radians(az_deg), math.radians(el_deg)
        off = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)]) * dist
        pos = HC + off
        pw, tw = pos + WOFF, HC + WOFF
        return {'az': az_deg, 'el': el_deg, 'dist': dist, 'fov': 55.0, 'aspect': 720 / 1280,
                'pos': [float(v) for v in pos], 'tgt': [float(v) for v in HC],
                'pos_gltf': [float(pw[0]), float(pw[2]), float(-pw[1])],
                'tgt_gltf': [float(tw[0]), float(tw[2]), float(-tw[1])]}
    def solve_dist(az_deg, el_deg, target=0.191):
        lo, hi = 0.25, 2.5
        for _ in range(40):
            mid = (lo + hi) / 2
            s = spec(az_deg, el_deg, mid)
            frac = abs(proj_ny(forehead, np.array(s['pos']), HC) - proj_ny(chin, np.array(s['pos']), HC)) / 2
            if frac > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    d_front = solve_dist(0, 4.8)
    d_q34 = solve_dist(-52, 0.0)
    print('solved dist front', round(d_front, 3), 'q34', round(d_q34, 3))
    cams = {'front_p': spec(0, 4.8, d_front), 'front_m': spec(0, -4.8, d_front),
            'q34': spec(-52, 0.0, d_q34), 'front': spec(0, 4.8, d_front)}
    json.dump(cams, open(f'{BASE}/cam_specs.json', 'w'), indent=1)
    json.dump({'forehead': [float(v) for v in forehead], 'chin': [float(v) for v in chin],
               'head_centre': [float(v) for v in HC]}, open(f'{BASE}/head_anchors.json', 'w'), indent=1)
    print('CAMS saved')

# ---------------------------------------------------------------- anchors
elif STAGE == 'anchors':
    # args: anchors <deltas_json> <cam_name> <angel_value> <out_json>
    dfile, cam_name, aval, outp = argv[1], argv[2], float(argv[3]), argv[4]
    dj = json.load(open(dfile))
    lm = {i: dj['landmarks'][int(i)] for i in dj['deltas'].keys()}
    cams = load_cams()
    hits = raycast_all(cams[cam_name], lm, aval)
    fw = None
    if '234' in hits and '454' in hits:
        fw = float(np.linalg.norm(np.array(hits['234']['point']) - np.array(hits['454']['point'])))
    elif '234' in hits and '1' in hits:
        fw = float(np.linalg.norm(np.array(hits['234']['point']) - np.array(hits['1']['point'])))
    json.dump({'hits': hits, 'face_width_m': fw, 'cam': cam_name}, open(outp, 'w'), indent=1)
    print(f'anchors: {len(hits)}/{len(lm)} hit, face_width_m={fw}')

# ---------------------------------------------------------------- warp
elif STAGE == 'warp':
    # args: warp <anchors_json> <deltas_json> <cam_name> <gains_json> [brow_json]
    afile, dfile, cam_name, gfile = argv[1], argv[2], argv[3], argv[4]
    brow_file = argv[5] if len(argv) > 5 else None
    anch = json.load(open(afile))
    dj = json.load(open(dfile))
    gains = json.load(open(gfile)) if os.path.exists(gfile) else {}
    cams = load_cams()
    cam = cams[cam_name]
    pos = Vector(cam['pos']); tgt = Vector(cam['tgt'])
    fwd, right, upv = cam_basis(pos, tgt)
    right = np.array(right); upv = np.array(upv); fwd = np.array(fwd)
    FW = anch['face_width_m']
    A_pts, D3 = [], []
    region_of = {}
    OVAL = {10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109}
    LIPS = {61,146,91,181,84,17,314,405,321,375,291,409,270,269,267,0,37,39,40,185,57,165,167,164,393,391,308,415,310,311,312,95,88,178,87,14,317,402,318,324}
    EYES = {33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246,263,249,390,373,374,380,381,382,362,398,384,385,386,387,388,466}
    BROWS = {70,63,105,66,107,55,65,52,53,46,300,293,334,296,336,285,295,282,283,276}
    NOSE = {1,2,4,5,6,94,98,168,195,197,240,274,278,344,440}
    for i in OVAL: region_of[i] = 'oval'
    for i in LIPS: region_of[i] = 'lips'
    for i in EYES: region_of[i] = 'eyes'
    for i in BROWS: region_of[i] = 'brows'
    for i in NOSE: region_of[i] = 'nose'
    lm_allow = gains.get('lm_allow')
    for idx, h in anch['hits'].items():
        i = int(idx)
        if idx not in dj['deltas']:
            continue
        if lm_allow is not None and i not in lm_allow:
            continue
        dx, dy = dj['deltas'][idx]
        g = gains.get(region_of.get(i, 'other'), 1.0)
        d3 = (right * dx + upv * (-dy)) * FW * g
        A_pts.append(h['point']); D3.append(d3)
    A_pts = np.array(A_pts); D3 = np.array(D3)
    print(f'warp anchors used: {len(A_pts)}, mean |delta| {np.linalg.norm(D3,axis=1).mean()*1000:.2f} mm, max {np.linalg.norm(D3,axis=1).max()*1000:.2f} mm')
    fz = f'{BASE}/field_total.npz'
    F = {}
    if os.path.exists(fz):
        z = np.load(fz)
        F = {k: z[k] for k in z.files}
    def field_for(verts, r0):
        d2 = ((verts[:, None, :] - A_pts[None, :, :]) ** 2).sum(-1)
        w = np.exp(-d2 / (r0 ** 2))
        wsum = w.sum(1, keepdims=True)
        mean_d = D3.mean(0)
        Fv = (w @ D3) / np.maximum(wsum, 1e-9)
        far = (wsum[:, 0] < 0.05)
        Fv[far] = mean_d * 0.0  # no data far away -> no move
        # blend 12% of local mean for smoothness in mid zone
        return Fv
    for m in KEY_MESHES:
        ob = bpy.data.objects[m]
        basis = get_basis(ob)
        # evaluated positions (all other keys as saved; AngelFace at current state)
        set_key(m, 'AngelFace', 1.0 if (m in F and F[m].shape == basis.shape) else 0.0)
        bpy.context.view_layer.update()
        ev = evaluated_mesh(ob)
        verts_eval = np.empty(len(ev.data.vertices) * 3)
        ev.data.vertices.foreach_get('co', verts_eval)
        verts_eval = verts_eval.reshape(-1, 3)
        if m == BODY:
            mats = [mm.name if mm else '' for mm in ob.data.materials]
            pmat = np.array([mats[p.material_index] for p in ob.data.polygons])
            vmat = np.empty(len(basis), dtype=object)
            # vertex material = material of first polygon using it (approx via loop)
            vmat[:] = ''
            for p in ob.data.polygons:
                mn = mats[p.material_index]
                for v in p.vertices:
                    if vmat[v] == '':
                        vmat[v] = mn
            Fv = field_for(verts_eval, 0.022)
            # region window
            z = verts_eval[:, 2]; x = verts_eval[:, 0]; y = verts_eval[:, 1]
            wz = np.clip((z - 1.095) / 0.035, 0, 1)
            wx = np.clip((0.088 - np.abs(x)) / 0.018, 0, 1)
            wy = np.clip((0.028 - y) / 0.02, 0, 1)
            win = wz * wx * wy
            in_face = np.array([vm in FACE_MATS for vm in vmat])
            neck = (vmat == 'Torso-3') & (z > 1.08)
            mask = (in_face | neck) & (z > 1.08) & (np.abs(x) < 0.095) & (y < 0.035)
            Fv = Fv * win[:, None] * mask[:, None]
            # clamp per-iteration step
            n = np.linalg.norm(Fv, axis=1)
            over = n > 0.012
            Fv[over] *= (0.012 / n[over])[:, None]
        elif m == 'Eyebrow':
            Fv = field_for(verts_eval, 0.012)
            if brow_file and os.path.exists(brow_file):
                bj = json.load(open(brow_file))
                # brow thickening: scale offsets along camera-up around each brow centroid
                cents = bj['centroids']  # {'L':[x,y,z],'R':[...]} in world
                scales = bj['scales']
                xs = verts_eval[:, 0]
                for side in ['L', 'R']:
                    sel = (xs > 0) if side == 'L' else (xs <= 0)  # her left = +X
                    c = np.array(cents[side]); sc = scales[side]
                    rel = verts_eval[sel] - c
                    along = rel @ upv
                    Fv[sel] += (along * (sc - 1.0))[:, None] * upv[None, :]
            n = np.linalg.norm(Fv, axis=1)
            over = n > 0.012
            Fv[over] *= (0.012 / n[over])[:, None]
        else:  # Eyelashes
            Fv = field_for(verts_eval, 0.012)
            n = np.linalg.norm(Fv, axis=1)
            over = n > 0.012
            Fv[over] *= (0.012 / n[over])[:, None]
        prev = F.get(m)
        F[m] = Fv if prev is None or prev.shape != basis.shape else prev + Fv
        set_key_co(ob, 'AngelFace', basis + F[m])
        tot = np.linalg.norm(F[m], axis=1)
        print(f'{m}: iter field max {np.linalg.norm(Fv,axis=1).max()*1000:.2f} mm | total max {tot.max()*1000:.2f} mm, verts>0.5mm {(tot>0.0005).sum()}')
    np.savez(fz, **F)
    bpy.ops.wm.save_as_mainfile(filepath=f'{BASE}/work/pilot2_v2.blend')
    print('WARP saved blend')

# ---------------------------------------------------------------- measure
elif STAGE == 'measure':
    for m in KEY_MESHES:
        set_key(m, 'AngelFace', 0.0)
    bpy.context.view_layer.update()
    ob = bpy.data.objects[BODY]
    ev = evaluated_mesh(ob)
    me = ev.data
    verts = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get('co', verts)
    verts = verts.reshape(-1, 3)
    # arm-dominant verts (excluded from torso sections)
    arm_groups = {g.index for g in ob.vertex_groups if any(t in g.name for t in ['Arm', 'Hand', 'Shoulder', 'ForeArm'])}
    is_arm = np.zeros(len(verts), dtype=bool)
    for v in me.vertices:
        for ge in v.groups:
            if ge.group in arm_groups and ge.weight > 0.5:
                is_arm[v.index] = True
                break
    out = {'stature': float(verts[:, 2].max() - verts[:, 2].min()),
           'z_min': float(verts[:, 2].min()), 'z_max': float(verts[:, 2].max()),
           'sections': {}}
    verts_t = verts[~is_arm]
    # cross-sections: torso island (|x|<0.24) for z>=0.66; per-leg clusters below.
    def section_stats(band):
        cx, cy = band[:, 0].mean(), band[:, 1].mean()
        ang = np.arctan2(band[:, 1] - cy, band[:, 0] - cx)
        pts = band[np.argsort(ang)]
        per = float(np.linalg.norm(np.diff(np.vstack([pts, pts[:1]]), axis=0), axis=1).sum())
        return {'width': round(float(band[:, 0].max() - band[:, 0].min()), 4),
                'depth': round(float(band[:, 1].max() - band[:, 1].min()), 4),
                'perim': round(per, 4), 'n': int(len(band))}
    for zi in range(28, 122, 2):
        z = zi / 100
        band_all = verts_t[np.abs(verts_t[:, 2] - z) < 0.003]
        if len(band_all) < 20:
            continue
        if z >= 0.66:
            band = band_all[np.abs(band_all[:, 0]) < 0.24]
            if len(band) >= 20:
                out['sections'][f'{z:.2f}'] = section_stats(band)
        else:
            for side, sgn in [('legL', 1), ('legR', -1)]:
                band = band_all[(band_all[:, 0] * sgn > 0.02) & (np.abs(band_all[:, 0]) < 0.24)]
                if len(band) >= 15:
                    out['sections'][f'{z:.2f}:{side}'] = section_stats(band)
    json.dump(out, open(f'{BASE}/work/measure_megami.json', 'w'), indent=1)
    s = out['sections']
    def show(z):
        k = f'{z:.2f}'
        if k in s:
            print(f'z={k} width {s[k]["width"]} depth {s[k]["depth"]} perim {s[k]["perim"]}')
    print('stature', out['stature'])
    for z in [0.50, 0.60, 0.70, 0.76, 0.80, 0.84, 0.88, 0.92, 0.96, 1.00, 1.06, 1.12, 1.16]:
        show(z)
    print('MEASURE saved')

# ---------------------------------------------------------------- body
elif STAGE == 'body':
    import mathutils
    # z-remap control points (z -> shift), legs carry most of the +0.275 gain
    ZC = [(0.0, 0.0), (0.0424, 0.0), (0.3519, 0.1065), (0.682, 0.2200), (0.7575, 0.2200),
          (0.8531, 0.2475), (1.0272, 0.2650), (1.1027, 0.2750), (1.1305, 0.2750), (1.40, 0.2750)]
    # radial factor control points (z -> r) applied to (x, y) around axis x=0,y=0
    RC = [(0.0, 1.0), (0.10, 1.02), (0.30, 1.02), (0.34, 1.03), (0.64, 1.03), (0.68, 1.0),
          (0.79, 1.0), (0.83, 1.20), (0.87, 1.08), (0.88, 1.0), (0.99, 1.0), (1.06, 1.01),
          (1.09, 1.0), (1.40, 1.0)]
    # neck extra radial (z -> r) only for |x|<0.035 & z in neck band
    NC = [(1.05, 1.0), (1.09, 1.06), (1.12, 1.06), (1.15, 1.0)]
    zs = np.linspace(0, 1.4, 1401)
    def build(ctrl):
        xs = np.array([c[0] for c in ctrl]); ys = np.array([c[1] for c in ctrl])
        v = np.interp(zs, xs, ys)
        # gaussian smooth sigma ~8mm (8 samples)
        k = np.exp(-0.5 * (np.arange(-24, 25) / 8.0) ** 2); k /= k.sum()
        return np.convolve(np.pad(v, 24, mode='edge'), k, mode='same')[24:-24]
    shift_g = build(ZC); r_g = build(RC); n_g = build(NC)
    def shift(z):
        return np.interp(z, zs, shift_g)
    def rfac(z):
        return np.interp(z, zs, r_g)
    def nfac(z):
        return np.interp(z, zs, n_g)
    def field(P):
        P = np.asarray(P, dtype=np.float64)
        z = P[:, 2]
        r = rfac(z)
        out = P.copy()
        out[:, 0] = P[:, 0] * r
        out[:, 1] = P[:, 1] * r
        # shoulder widening: x-only extra for |x|>0.10 in z 1.00-1.10
        sw = np.clip((np.abs(P[:, 0]) - 0.10) / 0.05, 0, 1) * np.clip((z - 0.99) / 0.03, 0, 1) * np.clip((1.11 - z) / 0.03, 0, 1)
        out[:, 0] += np.sign(P[:, 0]) * sw * 0.03 * np.abs(P[:, 0])
        # neck thickening
        nk = np.clip((0.040 - np.abs(P[:, 0])) / 0.01, 0, 1) * (nfac(z) - 1.0)
        out[:, 0] = out[:, 0] + P[:, 0] * nk
        out[:, 1] = out[:, 1] + P[:, 1] * nk
        out[:, 2] = P[:, 2] + shift(z)
        return out
    # apply as AngelBody key on every mesh
    report = {}
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        me = ob.data
        if me.shape_keys is None:
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.shape_key_add(from_mix=False)  # creates Basis
            ob.select_set(False)
        keys = me.shape_keys.key_blocks
        if 'AngelBody' not in keys:
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.shape_key_add(from_mix=False)
            ob.select_set(False)
            keys[-1].name = 'AngelBody'
        basis = get_basis(ob)
        newp = field(basis)
        set_key_co(ob, 'AngelBody', newp)
        keys['AngelBody'].value = 1.0
        d = np.linalg.norm(newp - basis, axis=1)
        report[ob.name] = {'max_disp_mm': round(float(d.max()) * 1000, 1)}
    print('BODY field applied:', json.dumps(report))
    # bones: move axial deform bones by the same field
    arm = bpy.data.objects['Parvati']
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    moved = []
    AXIAL = ['LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot',
             'Spine', 'Spine1', 'Spine2', 'Chest', 'Neck', 'Head', 'Hips',
             'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm',
             'spine', 'spine-1', 'chest', 'chest-1', 'back', 'neck-1', 'pelvis']
    for bn in AXIAL:
        eb = arm.data.edit_bones.get(bn)
        if eb is None:
            continue
        h = field(np.array([[eb.head.x, eb.head.y, eb.head.z]]))[0]
        t = field(np.array([[eb.tail.x, eb.tail.y, eb.tail.z]]))[0]
        eb.head = mathutils.Vector(h); eb.tail = mathutils.Vector(t)
        moved.append(bn)
    bpy.ops.object.mode_set(mode='OBJECT')
    print('bones moved:', moved)
    bpy.ops.wm.save_as_mainfile(filepath=f'{BASE}/work/pilot2_v2.blend')
    print('BODY saved')

# ---------------------------------------------------------------- tattoo_uv
elif STAGE == 'tattoo_uv':
    for m in KEY_MESHES:
        set_key(m, 'AngelFace', 0.0)
    bpy.context.view_layer.update()
    ob = bpy.data.objects[BODY]
    ev = evaluated_mesh(ob)
    me = ev.data
    tree = BVHTree.FromObject(ev, bpy.context.evaluated_depsgraph_get())
    uv_layer = me.uv_layers.active.data
    mats = [mm.name if mm else '' for mm in me.materials]
    def surf_point(x, z):
        loc, nrm, fi, dist = tree.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)))
        return loc, fi
    def uv_at(fi, loc):
        poly = me.polygons[fi]
        pts = [me.vertices[v].co for v in poly.vertices]
        uvs = [uv_layer[l].uv for l in poly.loop_indices]
        # barycentric in 3D (triangle fan: use first 3 verts; polys are tris/quads -> triangulate via fan weights fallback: nearest vert blend)
        import mathutils
        if len(pts) >= 3:
            a, b, c = pts[0], pts[1], pts[2]
            v0, v1, v2 = b - a, c - a, loc - a
            d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
            d20, d21 = v2.dot(v0), v2.dot(v1)
            den = d00 * d11 - d01 * d01
            if abs(den) > 1e-12:
                w1 = (d11 * d20 - d01 * d21) / den
                w2 = (d00 * d21 - d01 * d20) / den
                w0 = 1 - w1 - w2
                uv = uvs[0] * w0 + uvs[1] * w1 + uvs[2] * w2
                return [float(uv.x), float(uv.y)]
        return [float(uvs[0].x), float(uvs[0].y)]
    targets = {'T13': (0.045, 1.048), 'T14': (0.0, 1.005)}
    out = {}
    cents = np.array([me.vertices[v].co for p in me.polygons for v in [p.vertices[0]]])  # placeholder
    for name, (tx, tz) in targets.items():
        loc, fi = surf_point(tx, tz)
        uv0 = uv_at(fi, loc)
        locx, fix = surf_point(tx + 0.005, tz)
        uvx = uv_at(fix, locx)
        locz, fiz = surf_point(tx, tz + 0.005)
        uvz = uv_at(fiz, locz)
        duv_dx = [(uvx[i] - uv0[i]) / 0.005 for i in range(2)]
        duv_dz = [(uvz[i] - uv0[i]) / 0.005 for i in range(2)]
        # mask: UV polys of Torso-3 faces whose centroid is within 4cm of hit point
        polys_uv = []
        for p in me.polygons:
            if mats[p.material_index] != 'Torso-3':
                continue
            c = p.center
            if (Vector(c) - loc).length < 0.04:
                polys_uv.append([[float(uv_layer[l].uv.x), float(uv_layer[l].uv.y)] for l in p.loop_indices])
        out[name] = {'point3d': [float(v) for v in loc], 'uv': uv0, 'duv_dx': duv_dx, 'duv_dz': duv_dz,
                     'mask_polys': polys_uv}
        print(name, 'point', [round(v, 4) for v in loc], 'uv', [round(v, 4) for v in uv0], 'mask polys', len(polys_uv))
    json.dump(out, open(f'{BASE}/work/tattoo_uv.json', 'w'))
    print('TATTOO UV saved')

# ---------------------------------------------------------------- tattoo_load
elif STAGE == 'tattoo_load':
    png = argv[1]
    img = bpy.data.images['Parvati_Torso']
    new = bpy.data.images.load(png)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    new.pixels.foreach_get(arr)
    img.pixels.foreach_set(arr)
    img.update()
    bpy.data.images.remove(new)
    bpy.ops.wm.save_as_mainfile(filepath=f'{BASE}/work/pilot2_v2.blend')
    print('TATTOO loaded + blend saved')

# ---------------------------------------------------------------- tex_load
elif STAGE == 'tex_load':
    # args: tex_load Name1=png1 Name2=png2 ...
    for pair in argv[1:]:
        name, png = pair.split('=', 1)
        img = bpy.data.images[name]
        new = bpy.data.images.load(png)
        w, h = img.size
        arr = np.empty(w * h * 4, dtype=np.float32)
        new.pixels.foreach_get(arr)
        img.pixels.foreach_set(arr)
        img.update()
        bpy.data.images.remove(new)
        print('loaded', name, 'from', png)
    bpy.ops.wm.save_as_mainfile(filepath=f'{BASE}/work/pilot2_v2.blend')
    print('TEX saved')

# ---------------------------------------------------------------- export
elif STAGE == 'export':
    out = argv[1] if len(argv) > 1 else f'{BASE}/glb/megami-v2.glb'
    for m in KEY_MESHES:
        set_key(m, 'AngelFace', 1.0)
    if 'AngelBody' in bpy.data.objects[BODY].data.shape_keys.key_blocks:
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ob.data.shape_keys and 'AngelBody' in ob.data.shape_keys.key_blocks:
                ob.data.shape_keys.key_blocks['AngelBody'].value = 1.0
    bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_morph_normal=False)
    print('EXPORTED', out, os.path.getsize(out))
