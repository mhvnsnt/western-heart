#!/usr/bin/env python3
"""tools/deploy/fit_cdn_budget.py — pack a fighter GLB under the jsDelivr per-file limit so the LIVE build can load
it straight from main, without the B2 bucket or room on Pages.

Why (Negativo re-rig, 2026-11-01; owner: "you can handle all of that from this end"): the live loader tries the B2
Worker, then Pages, then jsDelivr (game/js/asset-config.js resolveAssetCandidates). Pages sits at its 1 GB cap and
B2 needs the upload lane's credentials; jsDelivr serves any file on main up to 20 MB (it 403s bigger files). A model
published under a NEW path (so B2 misses it and the loader falls through) and packed under the limit is live as soon
as it is on main (purge https://purge.jsdelivr.net/gh/mhvnsnt/western-heart@main/<path> to skip the alias cache).

Steps (input must be plain glTF: decode meshopt first, tools/anim/gltf_codec.mjs decode):
  1. PNG textures over --png-min MB are re-encoded as JPEG with FULL chroma (4:4:4) at --jpeg-q: normal maps keep
     their x/y channels sharp (4:2:0 blurs them). The mean / p99 normal-angle error is reported per texture
     (Negativo's 4096^2 normal map at q93: 5.95 MB -> 1.57 MB, 0.48 deg mean, 1.94 deg p99);
  2. gltfpack -cc -kn -km -ke (meshopt high compression, default quantization; skin, clip, names kept);
  3. refuse (exit 1) if the result is over --budget bytes.

usage: python3 tools/deploy/fit_cdn_budget.py --in PLAIN.glb --out OUT.glb [--budget 19500000] [--jpeg-q 93]
       env GLTFPACK=path/to/gltfpack (tools/gltfpack/fetch-gltfpack.sh builds one), default: gltfpack on PATH
"""
import argparse
import io
import json
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np


def read_glb(path):
    b = open(path, 'rb').read()
    n = struct.unpack_from('<I', b, 12)[0]
    js = json.loads(b[20:20 + n])
    off = 20 + n
    blen = struct.unpack_from('<I', b, off)[0]
    return js, b[off + 8: off + 8 + blen]


def write_glb(path, js, views):
    """Rebuild buffer 0 from per-bufferView byte strings (4-byte aligned)."""
    blob = bytearray()
    for bv, data in zip(js['bufferViews'], views):
        blob += b'\0' * (-len(blob) % 4)
        bv['byteOffset'] = len(blob)
        bv['byteLength'] = len(data)
        bv['buffer'] = 0
        blob += data
    blob += b'\0' * (-len(blob) % 4)
    js['buffers'] = [{'byteLength': len(blob)}]
    jb = json.dumps(js, separators=(',', ':')).encode()
    jb += b' ' * (-len(jb) % 4)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(jb) + 8 + len(blob)))
        f.write(struct.pack('<II', len(jb), 0x4E4F534A) + jb)
        f.write(struct.pack('<II', len(blob), 0x004E4942) + bytes(blob))


def normal_slots(js):
    out = set()
    for m in js.get('materials', []):
        t = (m.get('normalTexture') or {}).get('index')
        if t is not None:
            out.add(js['textures'][t].get('source'))
    return out


def main():
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--budget', type=int, default=19_500_000, help='bytes (jsDelivr refuses files over 20 MB)')
    ap.add_argument('--jpeg-q', type=int, default=93)
    ap.add_argument('--png-min', type=float, default=1.0, help='re-encode PNGs larger than this many MB')
    a = ap.parse_args()
    js, blob = read_glb(a.inp)
    if 'EXT_meshopt_compression' in (js.get('extensionsUsed') or []):
        sys.exit('input is meshopt-compressed: decode first (tools/anim/gltf_codec.mjs decode)')
    views = [blob[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']] for bv in js['bufferViews']]
    normals = normal_slots(js)
    rep = {'input': a.inp, 'tool': 'tools/deploy/fit_cdn_budget.py', 'textures': []}
    for ii, im in enumerate(js.get('images', [])):
        if im.get('mimeType') != 'image/png' or 'bufferView' not in im:
            continue
        data = views[im['bufferView']]
        if len(data) < a.png_min * 1e6:
            continue
        img = Image.open(io.BytesIO(data))
        if img.mode not in ('RGB', 'L'):
            if 'A' in img.mode and np.asarray(img.getchannel('A')).min() < 255:
                rep['textures'].append({'image': ii, 'kept_png': 'has transparency'})
                continue
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=a.jpeg_q, subsampling=0, optimize=True)
        jpg = buf.getvalue()
        t = {'image': ii, 'size': list(img.size), 'png_bytes': len(data), 'jpeg_bytes': len(jpg), 'normal_map': ii in normals}
        A = np.asarray(img.convert('RGB')).astype(np.float64)
        B = np.asarray(Image.open(io.BytesIO(jpg)).convert('RGB')).astype(np.float64)
        t['channel_err_mean'] = round(float(np.abs(A - B).mean()), 3)
        if ii in normals:
            na, nb = A / 127.5 - 1, B / 127.5 - 1
            na /= np.linalg.norm(na, axis=2, keepdims=True) + 1e-9
            nb /= np.linalg.norm(nb, axis=2, keepdims=True) + 1e-9
            ang = np.degrees(np.arccos(np.clip((na * nb).sum(2), -1, 1)))
            t['normal_angle_err_deg'] = {'mean': round(float(ang.mean()), 3), 'p99': round(float(np.percentile(ang, 99)), 3)}
        views[im['bufferView']] = jpg
        im['mimeType'] = 'image/jpeg'
        rep['textures'].append(t)
    gltfpack = os.environ.get('GLTFPACK', 'gltfpack')
    with tempfile.TemporaryDirectory() as td:
        mid = os.path.join(td, 'tex.glb')
        write_glb(mid, js, views)
        r = subprocess.run([gltfpack, '-i', mid, '-o', a.out, '-cc', '-kn', '-km', '-ke'], capture_output=True, text=True)
        if r.returncode:
            sys.exit('gltfpack failed: ' + r.stderr[-2000:])
    size = os.path.getsize(a.out)
    rep.update({'output': a.out, 'bytes': size, 'budget': a.budget, 'pass': size <= a.budget})
    print(json.dumps(rep, indent=1))
    sys.exit(0 if rep['pass'] else 1)


if __name__ == '__main__':
    main()
