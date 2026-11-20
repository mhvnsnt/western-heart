#!/usr/bin/env python3
"""Compact GLB rebuild: keeps only referenced bufferViews, appends new images,
remaps indices. Drops orphaned garbage (the wrong-offset image regions).
baseColor -> JPEG q92, ORM -> PNG, normal -> PNG.
"""
import struct, json, io
import numpy as np, cv2
from PIL import Image
from pygltflib import GLTF2

W = '/home/hatch/workspace/skin-research/work/'

def jpeg_bytes(path, q=92):
    im = Image.open(path).convert('RGB')
    buf = io.BytesIO(); im.save(buf, format='JPEG', quality=q)
    return buf.getvalue(), 'image/jpeg'

def png_bytes(path):
    im = Image.open(path)
    buf = io.BytesIO(); im.save(buf, format='PNG')
    return buf.getvalue(), 'image/png'

def build_orm(rough_path):
    r = cv2.imread(rough_path, cv2.IMREAD_GRAYSCALE)
    orm = np.zeros((r.shape[0], r.shape[1], 3), np.uint8)
    orm[...,1] = r; orm[...,0] = 255
    ok, buf = cv2.imencode('.png', orm)
    return buf.tobytes(), 'image/png'

def rebuild(name, src_glb, skin_png, normal_png, rough_png, out_glb):
    print(f'== {name} ==')
    g = GLTF2(); gltf = g.load(src_glb)
    blob = gltf.binary_blob()
    j = json.loads(gltf.to_json())
    # bufferViews referenced by accessors (vertex data etc.)
    used = set()
    for acc in j.get('accessors', []):
        if acc.get('bufferView') is not None:
            used.add(acc['bufferView'])
    # also sparse etc. (none here)
    print(f'  accessor-used bufferViews: {sorted(used)}')
    new_blob = bytearray()
    remap = {}
    for old_idx in sorted(used):
        bv = j['bufferViews'][old_idx]
        off = bv['byteOffset']; ln = bv['byteLength']
        new_off = len(new_blob)
        new_blob.extend(blob[off:off+ln])
        while len(new_blob) % 4: new_blob.append(0)
        remap[old_idx] = len(j['bufferViews'])  # placeholder, fixed below
    # rebuild bufferView list: referenced ones first (compacted)
    new_bvs = []
    idx_map = {}
    for old_idx in sorted(used):
        bv = j['bufferViews'][old_idx]
        # compute new offset: cumulative
        idx_map[old_idx] = len(new_bvs)
        new_bvs.append({'buffer': 0, 'byteOffset': None, 'byteLength': bv['byteLength'],
                        **({'byteStride': bv['byteStride']} if 'byteStride' in bv else {}),
                        **({'target': bv['target']} if 'target' in bv else {})})
    # assign offsets
    off = 0
    # we already appended data in sorted order above; recompute cleanly
    new_blob = bytearray()
    for old_idx in sorted(used):
        bv = j['bufferViews'][old_idx]
        data = blob[bv['byteOffset']:bv['byteOffset']+bv['byteLength']]
        new_bvs[idx_map[old_idx]]['byteOffset'] = len(new_blob)
        new_blob.extend(data)
        while len(new_blob) % 4: new_blob.append(0)
    for acc in j.get('accessors', []):
        if acc.get('bufferView') is not None:
            acc['bufferView'] = idx_map[acc['bufferView']]
    # new images
    img_datas = [jpeg_bytes(skin_png), build_orm(rough_png), png_bytes(normal_png)]
    for i, (data, mime) in enumerate(img_datas):
        new_bvs.append({'buffer': 0, 'byteOffset': len(new_blob), 'byteLength': len(data)})
        new_blob.extend(data)
        while len(new_blob) % 4: new_blob.append(0)
        j['images'][i]['bufferView'] = len(new_bvs)-1
        j['images'][i]['mimeType'] = mime
        print(f'  image{i}: {len(data)/1e6:.1f} MB {mime}')
    j['bufferViews'] = new_bvs
    j['buffers'][0]['byteLength'] = len(new_blob)
    json_bytes = json.dumps(j, separators=(',', ':')).encode('utf-8')
    while len(json_bytes) % 4: json_bytes += b' '
    total = 12 + 8 + len(json_bytes) + 8 + len(new_blob)
    out = struct.pack('<III', 0x46546C67, 2, total)
    out += struct.pack('<II', len(json_bytes), 0x4E4F534A) + json_bytes
    out += struct.pack('<II', len(new_blob), 0x004E4942) + bytes(new_blob)
    open(out_glb,'wb').write(out)
    print(f'  wrote {out_glb}: {len(out)/1e6:.1f} MB')
    # validate
    g2 = GLTF2().load(out_glb); b2 = g2.binary_blob()
    for i, im in enumerate(g2.images):
        bv = g2.bufferViews[im.bufferView]
        magic = b2[bv.byteOffset:bv.byteOffset+4]
        good = magic[:2]==b'\xff\xd8' or magic[:4]==b'\x89PNG'
        print(f'  image{i} valid: {good}')
    # validate mesh still intact
    print(f'  meshes: {len(g2.meshes)}, skins: {len(g2.skins or [])}, acc: {len(g2.accessors)}')

rebuild('star', f'{W}star-a5.glb', f'{W}star-skin-v2.png', f'{W}star-normal-improved.png',
        f'{W}star-roughness.png', f'{W}star-a5-improved.glb')
rebuild('silv', f'{W}silv-a2.glb', f'{W}silv-skin-v2.png', f'{W}silv-normal-improved.png',
        f'{W}silv-roughness.png', f'{W}silv-a2-improved.glb')
