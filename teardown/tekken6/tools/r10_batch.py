#!/usr/bin/env python3
"""Tekken 6 PSP round-10 batch: full slot census of the top-76 containers,
full-section NDPP decode for the 12 character packages, and skeleton GLBs
for every character package's BONE chunks (body slot 1 + head slot 12).

Skeleton convention (round 9 JOB2, proven): BONE chunk = parents u32*N /
local translations f3*N / local Eulers f3*N (R = Rz*Ry*Rx) / name table
32B*N at offset table[5] / scales f3*N at offset table[6].

Usage: r10_batch.py <decoded76_dir> <models_out_dir> <inventory_json_out>
Mesh decode reuses tools/r9_ndpp_decode.py (same directory as this file).
"""
import struct, sys, os, json, glob, math, array
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'r9', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r9_ndpp_decode.py'))
r9 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r9)

CHAR_IDX = [0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21]

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    if n > 64 or hs > len(data) or 8 + n * 8 > len(data):
        return []  # not a directory container (e.g. COM moveset file)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append({'slot': i, 'off': start, 'size': sz,
                    'magic': data[start:start + 4].decode('latin1') if sz else ''})
        start = end if end else start
    return out

def get_slot(data, k):
    n, hs = struct.unpack_from('<II', data, 0); start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        if i == k: return data[start:start + sz]
        start = end if end else start
    return b''

# ---------- skeleton ----------
def euler_to_quat(ex, ey, ez):
    # R = Rz*Ry*Rx  ->  q = qz * qy * qx (Hamilton, applied right-first)
    def q(axis, a):
        s = math.sin(a / 2)
        return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(a / 2))
    def mul(a, b):
        ax, ay, az, aw = a; bx, by, bz, bw = b
        return (aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw,
                aw * bw - ax * bx - ay * by - az * bz)
    return mul(q((0, 0, 1), ez), mul(q((0, 1, 0), ey), q((1, 0, 0), ex)))

def parse_bone(sec):
    assert sec[:4] == b'BONE'
    ver, unk, one, flags, n = struct.unpack_from('<IIHHI', sec, 4)
    table = struct.unpack_from('<8I', sec, 24)
    parents = struct.unpack_from(f'<{n}I', sec, table[0])
    parents = [p if p != 0xFFFFFFFF else -1 for p in parents]
    trans = [struct.unpack_from('<3f', sec, table[1] + 12 * i) for i in range(n)]
    eulers = [struct.unpack_from('<3f', sec, table[2] + 12 * i) for i in range(n)]
    names = []
    for i in range(n):
        raw = sec[table[5] + 32 * i: table[5] + 32 * i + 32]
        names.append(raw.split(b'\x00')[0].decode('ascii', 'replace'))
    scales = [struct.unpack_from('<3f', sec, table[6] + 12 * i) for i in range(n)]
    return {'n': n, 'parents': parents, 'trans': trans, 'eulers': eulers,
            'names': names, 'scales': scales}

def mat_from_trs(t, e, s):
    ex, ey, ez = e
    cx, cy, cz = math.cos(ex), math.cos(ey), math.cos(ez)
    sx, sy, sz = math.sin(ex), math.sin(ey), math.sin(ez)
    # R = Rz*Ry*Rx
    m = [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
         [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
         [-sy, cy * sx, cy * cx]]
    for r in range(3):
        for c in range(3): m[r][c] *= s[c]
    return m, t

def compose(a, b):
    ma, ta = a; mb, tb = b
    m = [[sum(ma[r][k] * mb[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
    t = tuple(ta[r] + sum(ma[r][k] * tb[k] for k in range(3)) for r in range(3))
    return (m, t)

def bone_world(bone):
    worlds = []
    for i in range(bone['n']):
        local = mat_from_trs(bone['trans'][i], bone['eulers'][i], bone['scales'][i])
        p = bone['parents'][i]
        worlds.append(local if p < 0 else compose(worlds[p], local))
    return worlds

def write_skeleton_glb(path, bone, name):
    children = {}
    roots = []
    for i, p in enumerate(bone['parents']):
        if p < 0: roots.append(i)
        else: children.setdefault(p, []).append(i)
    nodes = []
    for i in range(bone['n']):
        node = {'name': bone['names'][i] or f'bone_{i}',
                'translation': [round(v, 4) for v in bone['trans'][i]],
                'rotation': [round(v, 6) for v in euler_to_quat(*bone['eulers'][i])],
                'scale': [round(v, 4) for v in bone['scales'][i]]}
        if i in children: node['children'] = children[i]
        nodes.append(node)
    gltf = {'asset': {'version': '2.0', 'generator': 't6r10 bone parse'},
            'scene': 0, 'scenes': [{'nodes': roots}], 'nodes': nodes}
    js = json.dumps(gltf).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    open(path, 'wb').write(out)

def main():
    src_dir, models_dir, inv_path = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(models_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src_dir, 'idx*_entry*.bin')))
    inventory = {'packages': []}
    for f in files:
        base = os.path.basename(f)
        idx = int(base[3:5])
        data = open(f, 'rb').read()
        sl = slots_of(data)
        pkg = {'idx': idx, 'file': base, 'size': len(data), 'slots': sl,
               'class': 'unknown'}
        s0 = sl[0]['magic'] if sl else ''
        if idx in CHAR_IDX: pkg['class'] = 'character'
        elif s0 == 'NDPP' and len(sl) == 13: pkg['class'] = 'stage/object?'
        elif s0 == 'NTPP': pkg['class'] = 'texture-NTPP'
        inventory['packages'].append(pkg)
        if idx not in CHAR_IDX: continue
        # full-section NDPP decode: every nonzero NDPP slot
        pkg['decoded'] = []
        for s in sl:
            if s['size'] == 0 or s['magic'] != 'NDPP': continue
            sec = get_slot(data, s['slot'])
            try:
                verts, tris, nrms, uvs, wgts, desc = r9.decode_mesh(sec)
            except Exception as e:
                pkg['decoded'].append({'slot': s['slot'], 'error': str(e)[:120]})
                continue
            entry = {'slot': s['slot'], 'verts': len(verts), 'tris': len(tris),
                     'units': len(r9.parse_units(sec))}
            if s['slot'] in (0, 10):
                entry['glb'] = f"idx{idx:02d}_slot{s['slot']}_r9.glb (round 9, already landed)"
            else:
                out = os.path.join(models_dir, f"idx{idx:02d}_slot{s['slot']}_r10.glb")
                mins, maxs = r9.write_glb(out, verts, tris, nrms, f'idx{idx:02d}_slot{s["slot"]}')
                entry['glb'] = os.path.basename(out)
                entry['bbox'] = [[round(x, 2) for x in mins], [round(x, 2) for x in maxs]]
            pkg['decoded'].append(entry)
        # skeletons: body slot 1 + head slot 12
        pkg['skeletons'] = []
        for s in sl:
            if s['size'] == 0 or s['magic'] != 'BONE': continue
            bone = parse_bone(get_slot(data, s['slot']))
            tag = 'skeleton' if s['slot'] == 1 else f"bone_slot{s['slot']}"
            out = os.path.join(models_dir, f"idx{idx:02d}_{tag}_r10.glb")
            write_skeleton_glb(out, bone, f'idx{idx:02d}_{tag}')
            worlds = bone_world(bone)
            wp = {bone['names'][i]: [round(v, 1) for v in worlds[i][1]]
                  for i in range(bone['n']) if bone['names'][i] in
                  ('ATAMA_jnt', 'ASHI_R_jnt', 'TE_R_jnt', 'HARA_ROT1')}
            pkg['skeletons'].append({'slot': s['slot'], 'bones': bone['n'],
                                     'glb': os.path.basename(out), 'world_key_joints': wp})
    json.dump(inventory, open(inv_path, 'w'), indent=1)
    nc = sum(1 for p in inventory['packages'] if p['class'] == 'character')
    print(f'packages={len(inventory["packages"])} characters={nc}')
    for p in inventory['packages']:
        if p['class'] == 'character':
            print(f"idx{p['idx']:02d}: decoded={p.get('decoded')} skeletons={[(s['slot'], s['bones']) for s in p.get('skeletons', [])]}")

if __name__ == '__main__':
    main()
