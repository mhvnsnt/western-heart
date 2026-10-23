"""Containment scoring: for each diffuse texture, background = texels within
tolerance of the modal color that are connected (4-conn) to the image border.
A decl's score for a texture = fraction of its UV samples landing on painted
(non-background) texels. The correct atlas keeps the UV islands painted."""
import numpy as np, sys, json
from collections import deque
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
import build6 as B
from tx2d_decode import parse_tx2d, decode_tex

d = open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone_pkg00_window.bin', 'rb').read()
g = json.load(open('/home/hatch/workspace/_doa4p2-scratch/work/chrone_pkg00_graph.json'))
texs = parse_tx2d(d, g['xpr2_offset'])
painted = {}
for i, t in enumerate(texs):
    if t['fmt'] not in (18, 20): continue
    img = decode_tex(d, t)
    rgb = img[:, :, :3].astype(int)
    flat = rgb.reshape(-1, 3)
    modal = np.median(flat, axis=0)
    near = (np.abs(rgb - modal).max(axis=2) < 20)
    if img.shape[2] == 4: near = near | (img[:, :, 3] < 16)
    # border-connected flood fill on `near`
    h, w = near.shape
    bg = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        if near[0, x]: dq.append((0, x))
        if near[h - 1, x]: dq.append((h - 1, x))
    for y in range(h):
        if near[y, 0]: dq.append((y, 0))
        if near[y, w - 1]: dq.append((y, w - 1))
    while dq:
        y, x = dq.popleft()
        if bg[y, x] or not near[y, x]: continue
        bg[y, x] = True
        for yy, xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= yy < h and 0 <= xx < w and near[yy, xx] and not bg[yy, xx]: dq.append((yy, xx))
    painted[i] = ~bg
    print(f'tex{i} fmt{t["fmt"]} {t["w"]}x{t["h"]} painted {painted[i].mean():.2f}')
decls = B.parse_decls(d, g)
seg = {int(k): tuple(v) for k, v in json.load(open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone-pkg00_segmap.json')).items()}
out = {}
for dd in sorted(decls, key=lambda x: x['decl_id']):
    did = dd['decl_id']
    if did not in seg: continue
    s = B.parse_seg(d, dd, *seg[did])
    if 'uv0' not in s: continue
    uv = s['uv0']
    if len(uv) > 6000: uv = uv[::len(uv) // 6000 + 1]
    sc = []
    for i, pm in painted.items():
        h, w = pm.shape
        xs = (np.clip(uv[:, 0], 0, 1) * (w - 1)).astype(int)
        ys = (np.clip(uv[:, 1], 0, 1) * (h - 1)).astype(int)
        sc.append((float(pm[ys, xs].mean()), i))
    sc.sort(reverse=True)
    out[did] = sc[:3]
    print(f"decl{did} obj{dd['obj']} vtx{dd['vtx']}: " + ' | '.join(f'tex{i} {v:.3f}' for v, i in sc[:3]))
json.dump({str(k): v for k, v in out.items()}, open('/home/hatch/workspace/_doa4p2-scratch/p6/tex_assign2.json', 'w'), indent=1)
