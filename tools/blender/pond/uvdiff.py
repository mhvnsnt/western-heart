"""Compare shipped GLB meshes to the clean source objects: transform fit, nearest-vertex distance, UV agreement.
Run in the source .blend: blender -b src.blend --python uvdiff.py -- GLB"""
import bpy, sys, mathutils, json, numpy as np
from mathutils.kdtree import KDTree
argv = sys.argv[sys.argv.index('--') + 1:]
glb = argv[0]
FIXED = '--fixed' in argv  # graft output is already in the game frame: use the known source->game transform
EXACT = ['tsuyu', 'suit', 'gloves', 'boots', 'Body_belt.dmx', 'Body_google.dmx', 'Body_mask.dmx', 'Hair']
src_names = {'Holo_001': 'suit', 'Mesh0000_003': 'Bulge', 'Mesh0000_004': 'Penis', 'Plane_003': 'gloves', 'Tsuyu': 'tsuyu',
             'Belt': 'Body_belt.dmx', 'Googles': 'Body_google.dmx', 'Mask_Body': 'Body_mask.dmx', 'hair_Body': 'Hair'}
# source rest data (undeformed mesh coords in world, shape keys at basis, no modifiers)
def src_data(o):
    me = o.data; mw = o.matrix_world
    co = np.array([mw @ v.co for v in me.vertices])
    uvl = me.uv_layers.active
    vuv = {}
    if uvl:
        for l in me.loops:
            vuv.setdefault(l.vertex_index, []).append(tuple(uvl.data[l.index].uv))
    return co, vuv
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=glb)
new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
# fit similarity using body mesh bbox: shipped 'Tsuyu' vs source tsuyu (all verts)
def bb(a): return a.min(0), a.max(0)
src_body, _ = src_data(bpy.data.objects['tsuyu'])
def world_co(o):
    me = o.data; mw = o.matrix_world
    return np.array([mw @ v.co for v in me.vertices])
ship_body = world_co([o for o in new if o.data.name.startswith('Tsuyu') or o.name.lower().startswith('tsuyu')][0])
smn, smx = bb(src_body); hmn, hmx = bb(ship_body)
s = (smx[2] - smn[2]) / (hmx[2] - hmn[2])
t = (smn + smx) / 2 - s * (hmn + hmx) / 2
if FIXED: s = 2.4521072; t = np.array([0, 0.08413951, -0.02454758])
print('FIT scale', s, 'offset', t, 'src body bbox', smn, smx, 'ship', hmn, hmx)
report = {}
for o in new:
    base = o.name[:-4] if o.name[-4:-3] == '.' and o.name[-3:].isdigit() else o.name
    if FIXED and base in EXACT: so = bpy.data.objects[base]
    else:
        key = next((k for k in src_names if o.name.startswith(k) or k in o.name), None)
        if not key: print('UNMAPPED', o.name); continue
        so = bpy.data.objects[src_names[key]]
    sco, svuv = src_data(so)
    kd = KDTree(len(sco))
    for i, c in enumerate(sco): kd.insert(c, i)
    kd.balance()
    co = world_co(o) * s + t
    me = o.data; uvl = me.uv_layers.active
    d = np.array([kd.find(c)[2] for c in co])
    res = {'src': so.name, 'ship_verts': len(co), 'src_verts': len(sco), 'dist_med': float(np.median(d)), 'dist_p99': float(np.percentile(d, 99)),
           'dist_max': float(d.max()), 'far_frac(>0.01)': float((d > 0.01).mean()), 'ship_uv': bool(uvl), 'materials': [m.name for m in me.materials]}
    if uvl and svuv:
        ok = okflip = okswap = n = 0
        loops = me.loops
        idx = np.arange(0, len(loops), max(1, len(loops) // 20000))
        for li in idx:
            l = loops[int(li)]
            c = co[l.vertex_index]
            near = kd.find(c)
            if near[2] > 0.005: continue
            u, v = uvl.data[int(li)].uv
            cands = svuv.get(near[1], [])
            if not cands: continue
            n += 1
            ok += min(abs(u - a) + abs(v - b) for a, b in cands) < 0.01
            okflip += min(abs(u - a) + abs((1 - v) - b) for a, b in cands) < 0.01
        res.update({'uv_samples': n, 'uv_match': ok / max(n, 1), 'uv_match_vflip': okflip / max(n, 1)})
    report[o.name] = res
    print('CMP', o.name, json.dumps(res))
json.dump(report, open('/pond/uvdiff_' + glb.split('/')[-1] + '.json', 'w'), indent=1)
