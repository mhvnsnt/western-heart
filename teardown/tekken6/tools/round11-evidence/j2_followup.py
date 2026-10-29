#!/usr/bin/env python3
"""Round 11 Job 2 follow-up: (a) which bones carry non-1.0 scales per package;
(b) fingertip extents under TR vs TRS for idx00 vs slot-10 mesh span;
(c) full-bone TR-vs-TRS max delta for all 12 packages; (d) mesh bbox ground truth."""
import struct, sys, os, math, importlib.util
sys.path.insert(0, '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools')
spec = importlib.util.spec_from_file_location('j2', os.path.join(os.path.dirname(__file__), 'j2_compose.py'))

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'
import glob

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

def R_from_euler(e):
    ex, ey, ez = e
    cx, cy, cz = math.cos(ex), math.cos(ey), math.cos(ez)
    sx, sy, sz = math.sin(ex), math.sin(ey), math.sin(ez)
    return [[cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx],
            [sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx],
            [-sy, cy*sx, cy*cx]]

def compose(bone, use_scale):
    worlds = []
    for i in range(bone['n']):
        R = R_from_euler(bone['eulers'][i]); t = bone['trans'][i]; s = bone['scales'][i]
        M = [[R[r][c] * s[c] for c in range(3)] for r in range(3)] if use_scale else R
        p = bone['parents'][i]
        if p < 0: worlds.append((M, tuple(t)))
        else:
            Mp, tp = worlds[p]
            Mw = [[sum(Mp[r][k] * M[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            tw = tuple(tp[r] + sum(Mp[r][k] * t[k] for k in range(3)) for r in range(3))
            worlds.append((Mw, tw))
    return [w[1] for w in worlds]

CHAR = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21]
files = {int(os.path.basename(f)[3:5]): f for f in glob.glob(os.path.join(DEC, 'idx*_entry*.bin'))}

for idx in CHAR:
    data = open(files[idx], 'rb').read()
    bone = parse_bone(get_slot(data, 1))
    odd = [(bone['names'][i], round(bone['scales'][i][0], 3)) for i in range(bone['n'])
           if abs(bone['scales'][i][0] - 1.0) > 1e-6]
    wtr = compose(bone, False); wtrs = compose(bone, True)
    dmax = max(max(abs(a - b) for a, b in zip(wtr[i], wtrs[i])) for i in range(bone['n']))
    print(f"idx{idx:02d}: non-unit-scale bones={len(odd)} max|TR-TRS|={dmax:.1f}")
    if idx in (0, 1, 5, 8):
        print(f"   odd-scale bones: {odd[:40]}")

# idx00 finger extents + mesh ground truth
spec2 = importlib.util.spec_from_file_location('r9', '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/r9_ndpp_decode.py')
r9 = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(r9)
data = open(files[0], 'rb').read()
bone = parse_bone(get_slot(data, 1))
for mode, ws in (('TR', compose(bone, False)), ('TRS', compose(bone, True))):
    fing = [(bone['names'][i], ws[i]) for i in range(bone['n']) if any(k in bone['names'][i] for k in ('OYA', 'HITO', 'NAKA', 'KUSU', 'KO_'))]
    mx = max(abs(p[0]) for _, p in fing) if fing else 0
    allmx = max(abs(p[0]) for p in ws)
    print(f"idx00 {mode}: finger-joint max|x|={mx:.1f} all-joint max|x|={allmx:.1f} finger joints={len(fing)}")
verts, tris, nrms, uvs, wgts, desc = r9.decode_mesh(get_slot(data, 10))
xs = [v[0] for v in verts]; ys = [v[1] for v in verts]
print(f"idx00 slot10 mesh: x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] verts={len(verts)}")
verts0, *_ = r9.decode_mesh(get_slot(data, 0))
ys0 = [v[1] for v in verts0]
print(f"idx00 slot0 (head) mesh: y[{min(ys0):.1f},{max(ys0):.1f}]")
