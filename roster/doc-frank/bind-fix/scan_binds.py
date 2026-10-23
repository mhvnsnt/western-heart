#!/usr/bin/env python3
"""Scan GLBs: skin/joint/bind-local census. Flags non-identity bind locals."""
import json, struct, sys, math
import numpy as np

def load_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'glTF', path
    ln = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20+ln])
    # binary chunk offset
    off = 20 + ln
    bin_data = b''
    if off < len(data):
        bln, btyp = struct.unpack('<I4s', data[off:off+8])
        bin_data = data[off+8:off+8+bln]
    return js, bin_data

def quat_angle(q):
    x, y, z, w = q
    w = max(-1.0, min(1.0, w))
    return math.degrees(2 * math.acos(abs(w)))

def quat_axis(q):
    x, y, z, w = q
    s = math.sqrt(max(0.0, 1 - w*w))
    if s < 1e-6:
        return (0, 0, 0)
    return (x/s, y/s, z/s)

def scan(path):
    js, _ = load_glb(path)
    nodes = js.get('nodes', [])
    skins = js.get('skins', [])
    out = {'path': path, 'gen': js.get('asset', {}).get('generator'),
           'meshes': len(js.get('meshes', [])), 'images': len(js.get('images', [])),
           'anims': len(js.get('animations', [])), 'skins': len(skins), 'bad': []}
    for si, skin in enumerate(skins):
        joints = skin.get('joints', [])
        out.setdefault('joints', len(joints))
        for j in joints:
            n = nodes[j]
            rot = n.get('rotation')
            if rot:
                ang = quat_angle(rot)
                if ang > 0.5:
                    ax = quat_axis(rot)
                    out['bad'].append((n.get('name', f'node{j}'), round(ang, 1),
                                       tuple(round(a, 2) for a in ax)))
    return out

for p in sys.argv[1:]:
    r = scan(p)
    print(f"== {r['path']}")
    print(f"   gen={r['gen']} meshes={r['meshes']} images={r['images']} anims={r['anims']} skins={r['skins']} joints={r.get('joints')}")
    if r['bad']:
        print(f"   NON-IDENTITY BIND LOCALS ({len(r['bad'])}):")
        for name, ang, ax in r['bad']:
            print(f"     {name}: {ang} deg about {ax}")
    else:
        print("   all bind locals identity")
