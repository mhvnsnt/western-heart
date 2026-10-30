#!/usr/bin/env python3
"""Round 11 Job 2: idx00 skeleton discrepancy.
Parse idx00 BONE slot1 bytes directly; compose world joints under
several conventions; compare against r9 spot values (JOB2-BONE-ROLES)
and r10 batch values (r10_inventory.json); also walk the shipped
r9/r10 skeleton GLBs' node trees with glTF semantics."""
import struct, sys, os, json, math

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

def get_slot(data, k):
    sl = slots_of(data); off, sz = sl[k]; return data[off:off + sz]

def parse_bone(sec):
    ver, unk, one, flags, n = struct.unpack_from('<IIHHI', sec, 4)
    table = struct.unpack_from('<8I', sec, 24)
    parents = [p if p != 0xFFFFFFFF else -1 for p in struct.unpack_from(f'<{n}I', sec, table[0])]
    trans = [struct.unpack_from('<3f', sec, table[1] + 12 * i) for i in range(n)]
    eulers = [struct.unpack_from('<3f', sec, table[2] + 12 * i) for i in range(n)]
    names = []
    for i in range(n):
        raw = sec[table[5] + 32 * i: table[5] + 32 * i + 32]
        names.append(raw.split(b'\x00')[0].decode('ascii', 'replace'))
    scales = [struct.unpack_from('<3f', sec, table[6] + 12 * i) for i in range(n)]
    return dict(n=n, table=table, parents=parents, trans=trans, eulers=eulers,
                names=names, scales=scales, hdr_f32=struct.unpack_from('<f', sec, 20)[0])

def R_from_euler(e):
    ex, ey, ez = e
    cx, cy, cz = math.cos(ex), math.cos(ey), math.cos(ez)
    sx, sy, sz = math.sin(ex), math.sin(ey), math.sin(ez)
    return [[cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx],
            [sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx],
            [-sy, cy*sx, cy*cx]]

def compose_world(bone, mode):
    """mode: 'TR' ignore scales; 'TRS' full glTF/r10 (local=R*S cols, chain);
    'TRSu' scales applied to rotation only for self, translations scaled by
    accumulated rotation but NOT accumulated scale."""
    worlds = []
    acc_scale = []
    for i in range(bone['n']):
        R = R_from_euler(bone['eulers'][i]); t = bone['trans'][i]; s = bone['scales'][i]
        if mode == 'TR':
            M = R
        else:
            M = [[R[r][c] * s[c] for c in range(3)] for r in range(3)]
        p = bone['parents'][i]
        if p < 0:
            worlds.append((M, tuple(t))); acc_scale.append(tuple(s))
        else:
            Mp, tp = worlds[p]
            Mw = [[sum(Mp[r][k] * M[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            if mode == 'TR':
                tw = tuple(tp[r] + sum(Mp[r][k] * t[k] for k in range(3)) for r in range(3))
            elif mode == 'TRS':
                tw = tuple(tp[r] + sum(Mp[r][k] * t[k] for k in range(3)) for r in range(3))
            worlds.append((Mw, tw))
    return [w[1] for w in worlds]

def read_glb_nodes(path):
    d = open(path, 'rb').read()
    ln, typ = struct.unpack_from('<II', d, 12)
    g = json.loads(d[20:20 + ln])
    return g['nodes']

def glb_world(nodes):
    # build parent map from children lists
    parent = {}
    roots = []
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []): parent[c] = i
    def quat_to_R(q):
        x, y, z, w = q
        return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    worlds = [None] * len(nodes)
    def solve(i):
        if worlds[i] is not None: return worlds[i]
        nd = nodes[i]
        t = nd.get('translation', [0, 0, 0]); q = nd.get('rotation', [0, 0, 0, 1]); s = nd.get('scale', [1, 1, 1])
        R = quat_to_R(q)
        M = [[R[r][c] * s[c] for c in range(3)] for r in range(3)]
        if i not in parent:
            worlds[i] = (M, tuple(t))
        else:
            Mp, tp = solve(parent[i])
            Mw = [[sum(Mp[r][k] * M[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            tw = tuple(tp[r] + sum(Mp[r][k] * t[k] for k in range(3)) for r in range(3))
            worlds[i] = (Mw, tw)
        return worlds[i]
    for i in range(len(nodes)): solve(i)
    return [w[1] for w in worlds]

KEY = ('ATAMA_jnt', 'TE_R_jnt', 'TE_L_jnt', 'ASHI_R_jnt', 'HARA_ROT1', 'KUBI_jnt')

for idx in (0, 1, 5, 8):
    data = open(os.path.join(DEC, f'idx{idx:02d}_entry{ {0:454,1:457,5:467,8:475}[idx] }.bin'), 'rb').read() if False else None

files = {0: 'idx00_entry454.bin', 1: 'idx01_entry457.bin', 5: 'idx05_entry467.bin', 8: 'idx08_entry475.bin'}
for idx, fn in files.items():
    data = open(os.path.join(DEC, fn), 'rb').read()
    bone = parse_bone(get_slot(data, 1))
    uniq = {}
    for s in bone['scales']: uniq[tuple(round(v, 4) for v in s)] = uniq.get(tuple(round(v, 4) for v in s), 0) + 1
    print(f"== idx{idx:02d}: N={bone['n']} hdr_f32={bone['hdr_f32']} table={bone['table']}")
    print(f"   scale value histogram: {uniq}")
    for mode in ('TR', 'TRS'):
        w = compose_world(bone, mode)
        row = {bone['names'][i]: tuple(round(v, 1) for v in w[i]) for i in range(bone['n']) if bone['names'][i] in KEY}
        print(f"   [{mode}] {row}")

# shipped GLBs comparison for idx00
for tag, path in (('r9', '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/models/idx00_skeleton_r9.glb'),
                  ('r10', '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/models/idx00_skeleton_r10.glb')):
    nodes = read_glb_nodes(path)
    w = glb_world(nodes)
    row = {nodes[i].get('name'): tuple(round(v, 1) for v in w[i]) for i in range(len(nodes)) if nodes[i].get('name') in KEY}
    sc = {tuple(nodes[i].get('scale', [1, 1, 1])) for i in range(len(nodes))}
    print(f"GLB {tag}: nodes={len(nodes)} scales_present={sc} world={row}")
