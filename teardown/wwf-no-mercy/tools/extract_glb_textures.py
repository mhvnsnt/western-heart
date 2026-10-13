#!/usr/bin/env python3
"""Extract embedded PNG textures from the community No Mercy GLBs into files.

Reads each .glb under re-docs/assets/3d Assets/, pulls the image bufferViews
(all are image/png), and writes them as
  <outdir>/characters/<wrestler>/part_<meshname>.png
  <outdir>/environments/<scene>/<imgname>.png
Also writes <outdir>/inventory.json (mesh/material/texture counts per GLB).
"""
import struct, json, os, glob, sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 're-docs', 'assets', '3d Assets')

def read_glb(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'glTF'
    ln = struct.unpack('<I', d[12:16])[0]
    js = json.loads(d[20:20 + ln])
    off = 20 + ln
    off += (-off) % 4  # chunks are 4-byte aligned
    bin_data = b''
    if off + 8 <= len(d) and d[off + 4:off + 8] == b'BIN\x00':
        blen = struct.unpack('<I', d[off:off + 4])[0]
        bin_data = d[off + 8:off + 8 + blen]
    return js, bin_data

def main():
    outdir = sys.argv[1]
    inv = {}
    for g in sorted(glob.glob(os.path.join(SRC, '*', '*.glb')) +
                     glob.glob(os.path.join(SRC, '*', '*', '*.glb'))):
        rel = os.path.relpath(g, SRC)
        parts = rel.split(os.sep)
        if len(parts) == 3:
            kind, name = parts[0], parts[1]      # characters/<wrestler>/x.glb
        else:
            kind, name = parts[0], os.path.splitext(parts[1])[0]  # environments/x.glb
        js, bind = read_glb(g)
        bvs = js.get('bufferViews', [])
        imgs = js.get('images', [])
        sub = os.path.join(outdir, kind, name)
        os.makedirs(sub, exist_ok=True)
        n = 0
        for i, im in enumerate(imgs):
            bv = bvs[im['bufferView']]
            blob = bind[bv['byteOffset']:bv['byteOffset'] + bv['byteLength']]
            fn = (im.get('name') or f"img_{i}") + '.png'
            open(os.path.join(sub, fn), 'wb').write(blob)
            n += 1
        inv[rel] = {"meshes": len(js.get('meshes', [])),
                    "materials": len(js.get('materials', [])),
                    "textures_extracted": n,
                    "nodes": [x.get('name') for x in js.get('nodes', [])]}
        print(f"{rel}: {n} textures")
    json.dump(inv, open(os.path.join(outdir, 'inventory.json'), 'w'), indent=1)
    print(f"inventory.json written -> {outdir}")

if __name__ == '__main__':
    main()
