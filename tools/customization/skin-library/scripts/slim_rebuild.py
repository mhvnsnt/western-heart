import struct, json, io
import numpy as np, cv2
from PIL import Image
from pygltflib import GLTF2
W = '/home/hatch/workspace/skin-research/work/'
def rebuild(name, src_glb, skin_jpg, normal_png, orm_png, out_glb):
    print(f'== {name} ==')
    g = GLTF2(); gltf = g.load(src_glb)
    blob = gltf.binary_blob()
    j = json.loads(gltf.to_json())
    used = sorted({a['bufferView'] for a in j['accessors'] if a.get('bufferView') is not None})
    new_bvs = []; idx_map = {}; new_blob = bytearray()
    for old_idx in used:
        bv = j['bufferViews'][old_idx]
        data = blob[bv['byteOffset']:bv['byteOffset']+bv['byteLength']]
        idx_map[old_idx] = len(new_bvs)
        d = {'buffer': 0, 'byteOffset': len(new_blob), 'byteLength': len(data)}
        if 'byteStride' in bv: d['byteStride'] = bv['byteStride']
        if 'target' in bv: d['target'] = bv['target']
        new_bvs.append(d); new_blob.extend(data)
        while len(new_blob) % 4: new_blob.append(0)
    for acc in j['accessors']:
        if acc.get('bufferView') is not None: acc['bufferView'] = idx_map[acc['bufferView']]
    def img_data(p, mime):
        d = open(p,'rb').read(); return d, mime
    imgs = [img_data(skin_jpg,'image/jpeg'), img_data(orm_png,'image/png'), img_data(normal_png,'image/png')]
    for i,(data,mime) in enumerate(imgs):
        new_bvs.append({'buffer':0,'byteOffset':len(new_blob),'byteLength':len(data)})
        new_blob.extend(data)
        while len(new_blob)%4: new_blob.append(0)
        j['images'][i]['bufferView'] = len(new_bvs)-1
        j['images'][i]['mimeType'] = mime
        print(f'  image{i}: {len(data)/1e6:.1f}MB {mime}')
    j['bufferViews'] = new_bvs
    j['buffers'][0]['byteLength'] = len(new_blob)
    jb = json.dumps(j, separators=(',',':')).encode()
    while len(jb)%4: jb += b' '
    out = struct.pack('<III',0x46546C67,2,12+8+len(jb)+8+len(new_blob))
    out += struct.pack('<II',len(jb),0x4E4F534A)+jb
    out += struct.pack('<II',len(new_blob),0x004E4942)+bytes(new_blob)
    open(out_glb,'wb').write(out)
    print(f'  wrote {out_glb}: {len(out)/1e6:.1f}MB')
rebuild('star', f'{W}star-a5.glb', f'{W}star-skin-q88.jpg', f'{W}star-normal-improved.png', f'{W}star-orm-2k.png', f'{W}star-a5-slim.glb')
rebuild('silv', f'{W}silv-a2.glb', f'{W}silv-skin-q88.jpg', f'{W}silv-normal-improved.png', f'{W}silv-orm-2k.png', f'{W}silv-a2-slim.glb')
