#!/usr/bin/env python3
"""Round 11 Job 2: build CORRECTED skeleton GLBs for all 12 packages.
Convention proven from BONE bytes + mesh ground truth: bind joint world
positions compose T*R down the parent chain; the per-bone scale array
does NOT propagate into descendant translations (r10_batch's TRS walk put
idx00 ASHI_R at y=-9.7, below the mesh floor -0.7; TR puts it at 135.2).
A plain glTF node tree compounds scales, so to make a standard glTF walk
reproduce the proven bind pose exactly while keeping each node's own
scale value, each node's translation is divided by the accumulated
ancestor scale product (all BONE scales are uniform per bone, so this
is exact). Local rotations are unchanged from the BONE bytes.
Also emits a JSON diff: per package, max |glTF-walk(corrected) - TR| and
max |glTF-walk(r10 shipped) - TR|."""
import struct, sys, os, json, math, glob

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/r11_models'
os.makedirs(OUT, exist_ok=True)

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

def get_slot(data, k):
    off, sz = slots_of(data)[k]; return data[off:off + sz]

def parse_bone(sec):
    n = struct.unpack_from('<I', sec, 16)[0]
    table = struct.unpack_from('<8I', sec, 24)
    parents = [p if p != 0xFFFFFFFF else -1 for p in struct.unpack_from(f'<{n}I', sec, table[0])]
    trans = [struct.unpack_from('<3f', sec, table[1] + 12 * i) for i in range(n)]
    eulers = [struct.unpack_from('<3f', sec, table[2] + 12 * i) for i in range(n)]
    names = []
    for i in range(n):
        raw = sec[table[5] + 32 * i: table[5] + 32 * i + 32]
        names.append(raw.split(b'\x00')[0].decode('ascii', 'replace'))
    scales = [struct.unpack_from('<3f', sec, table[6] + 12 * i) for i in range(n)]
    return dict(n=n, parents=parents, trans=trans, eulers=eulers, names=names, scales=scales)

def euler_to_quat(ex, ey, ez):
    def q(axis, a):
        s = math.sin(a / 2); return (axis[0]*s, axis[1]*s, axis[2]*s, math.cos(a/2))
    def mul(a, b):
        ax, ay, az, aw = a; bx, by, bz, bw = b
        return (aw*bx + ax*bw + ay*bz - az*by, aw*by - ax*bz + ay*bw + az*bx,
                aw*bz + ax*by - ay*bx + az*bw, aw*bw - ax*bx - ay*by - az*bz)
    return mul(q((0,0,1), ez), mul(q((0,1,0), ey), q((1,0,0), ex)))

def R_from_euler(e):
    ex, ey, ez = e
    cx, cy, cz = math.cos(ex), math.cos(ey), math.cos(ez)
    sx, sy, sz = math.sin(ex), math.sin(ey), math.sin(ez)
    return [[cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx],
            [sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx],
            [-sy, cy*sx, cy*cx]]

def compose_TR(bone):
    worlds = []
    for i in range(bone['n']):
        R = R_from_euler(bone['eulers'][i]); t = bone['trans'][i]
        p = bone['parents'][i]
        if p < 0: worlds.append((R, tuple(t)))
        else:
            Mp, tp = worlds[p]
            Mw = [[sum(Mp[r][k]*R[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            tw = tuple(tp[r] + sum(Mp[r][k]*t[k] for k in range(3)) for r in range(3))
            worlds.append((Mw, tw))
    return [w[1] for w in worlds]

def write_glb(path, bone, name):
    n = bone['n']
    # accumulated ancestor scale product (excluding own scale)
    acc = [1.0] * n
    for i in range(n):
        p = bone['parents'][i]
        acc[i] = 1.0 if p < 0 else acc[p] * bone['scales'][p][0]
    children = {}; roots = []
    for i, p in enumerate(bone['parents']):
        if p < 0: roots.append(i)
        else: children.setdefault(p, []).append(i)
    nodes = []
    for i in range(n):
        t = bone['trans'][i]
        node = {'name': bone['names'][i] or f'bone_{i}',
                'translation': [round(t[a] / acc[i], 4) for a in range(3)],
                'rotation': [round(v, 6) for v in euler_to_quat(*bone['eulers'][i])],
                'scale': [round(v, 4) for v in bone['scales'][i]]}
        if i in children: node['children'] = children[i]
        nodes.append(node)
    gltf = {'asset': {'version': '2.0', 'generator': 't6r11 bone parse (TR bind convention, scale-compensated translations)'},
            'scene': 0, 'scenes': [{'nodes': roots}], 'nodes': nodes}
    js = json.dumps(gltf).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    open(path, 'wb').write(out)

def glb_world(path):
    d = open(path, 'rb').read()
    ln, typ = struct.unpack_from('<II', d, 12)
    g = json.loads(d[20:20 + ln]); nodes = g['nodes']
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []): parent[c] = i
    def q2R(q):
        x, y, z, w = q
        return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    W = [None] * len(nodes)
    def solve(i):
        if W[i] is not None: return W[i]
        nd = nodes[i]
        t = nd.get('translation', [0,0,0]); q = nd.get('rotation', [0,0,0,1]); s = nd.get('scale', [1,1,1])
        R = q2R(q); M = [[R[r][c]*s[c] for c in range(3)] for r in range(3)]
        if i not in parent: W[i] = (M, tuple(t))
        else:
            Mp, tp = solve(parent[i])
            Mw = [[sum(Mp[r][k]*M[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            tw = tuple(tp[r] + sum(Mp[r][k]*t[k] for k in range(3)) for r in range(3))
            W[i] = (Mw, tw)
        return W[i]
    for i in range(len(nodes)): solve(i)
    return [w[1] for w in W]

CHAR = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21]
files = {int(os.path.basename(f)[3:5]): f for f in glob.glob(os.path.join(DEC, 'idx*_entry*.bin'))}
MODELS = '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/models'
report = {}
for idx in CHAR:
    data = open(files[idx], 'rb').read()
    for slot, tag in ((1, 'skeleton'), (12, 'bone_slot12')):
        try: sec = get_slot(data, slot)
        except Exception: continue
        if sec[:4] != b'BONE': continue
        bone = parse_bone(sec)
        out = os.path.join(OUT, f'idx{idx:02d}_{tag}_r11.glb')
        write_glb(out, bone, f'idx{idx:02d}_{tag}')
        tr = compose_TR(bone)
        new = glb_world(out)
        oldp = os.path.join(MODELS, f'idx{idx:02d}_{tag}_r10.glb')
        old = glb_world(oldp) if os.path.exists(oldp) else None
        dnew = max(max(abs(a-b) for a, b in zip(tr[i], new[i])) for i in range(bone['n']))
        dold = max(max(abs(a-b) for a, b in zip(tr[i], old[i])) for i in range(bone['n'])) if old else None
        uniq = sorted({round(s[0], 4) for s in bone['scales']})
        report[f'idx{idx:02d}_slot{slot}'] = {'bones': bone['n'], 'scale_values': uniq,
            'max_err_corrected_vs_TR': round(dnew, 4),
            'max_err_r10shipped_vs_TR': round(dold, 2) if dold is not None else None}
        print(f"idx{idx:02d} slot{slot}: N={bone['n']} scales={uniq} corrected_err={dnew:.4f} r10_err={dold}")
json.dump(report, open(os.path.join(OUT, 'r11_skeleton_correction.json'), 'w'), indent=1)
print('written to', OUT)
