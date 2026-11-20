#!/usr/bin/env python3
"""Stage 2: improved normal + roughness maps.
- Normal: blend TextureCan OpenGL pore normals at 35% over model's normal map.
- Roughness: base 0.62 skin with pore-driven variation + slightly lower on smooth zones.
"""
import numpy as np, cv2, io, re
from PIL import Image
from pygltflib import GLTF2

W = '/home/hatch/workspace/skin-research/work/'

def get_png(glb, idx):
    g = GLTF2().load(glb); blob = g.binary_blob()
    pngs = [m.start() for m in re.finditer(b'\x89PNG\r\n\x1a\n', blob)]
    off = pngs[idx]; p = off + 8
    while True:
        ln = int.from_bytes(blob[p:p+4],'big'); typ = blob[p+4:p+8]
        p += 12 + ln
        if typ == b'IEND': break
    return np.array(Image.open(io.BytesIO(blob[off:p])).convert('RGB'))

# pore normal, resized to 4K, as float vectors
pore = np.array(Image.open(f'{W}skin0001/skin_0001_normal_opengl_4k.png').convert('RGB')).astype(np.float32)
pore_v = (pore/255.0)*2.0-1.0
pore_v /= np.linalg.norm(pore_v, axis=-1, keepdims=True)

for name, glb in [('star','star-a5.glb'), ('silv','silv-a2.glb')]:
    print(f'== {name} ==')
    nrm = get_png(glb, 1).astype(np.float32)  # 2nd PNG = normal map
    if nrm.shape[:2] != (4096,4096):
        nrm = cv2.resize(nrm, (4096,4096), interpolation=cv2.INTER_LINEAR)
    nv = (nrm/255.0)*2.0-1.0
    nv /= np.linalg.norm(nv, axis=-1, keepdims=True)
    # blend 35% pore detail
    b = nv*0.65 + pore_v*0.35
    b /= np.linalg.norm(b, axis=-1, keepdims=True)
    out_n = ((b+1.0)/2.0*255.0).astype(np.uint8)
    p = f'{W}{name}-normal-improved.png'
    cv2.imwrite(p, cv2.cvtColor(out_n, cv2.COLOR_RGB2BGR))
    print('  wrote', p)
    # roughness: skin base 158 (~0.62) with pore-driven variation
    pore_h = cv2.cvtColor((pore).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    pore_h = (pore_h-128)/128.0  # -1..1
    rough = np.full((4096,4096), 158, np.float32) + pore_h*14.0
    rng = np.random.default_rng(3)
    rough += rng.normal(0, 5, (4096,4096)).astype(np.float32)
    rough = np.clip(rough, 120, 200).astype(np.uint8)
    pr = f'{W}{name}-roughness.png'
    cv2.imwrite(pr, rough)
    print('  wrote', pr)
