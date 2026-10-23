"""Assign pkg00 diffuse textures to decls by UV-footprint evidence.
For each decl with UV0 and each diffuse texture (fmt 18 DXT1 / fmt 20 DXT5):
  score = mean sampled local-gradient (structure under the UV footprint)
          x painted fraction (samples not on the texture's modal color).
Prints top-3 textures per decl. Assignment is statistical (no file-internal
material->texture index exists in the item records - censused in phase 5/6);
the textured render is viewed before any claim.
"""
import numpy as np, sys, os, json, struct
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
import build6 as B
from tx2d_decode import parse_tx2d, decode_tex
from PIL import Image

d = open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone_pkg00_window.bin', 'rb').read()
g = json.load(open('/home/hatch/workspace/_doa4p2-scratch/work/chrone_pkg00_graph.json'))
xp = g['xpr2_offset']
texs = parse_tx2d(d, xp)
imgs = {}
for i, t in enumerate(texs):
    if t['fmt'] in (18, 20):
        imgs[i] = decode_tex(d, t).astype(np.float32)
grads = {}
for i, img in imgs.items():
    gr = np.abs(np.diff(img[:, :, :3], axis=0)).mean(axis=2)
    grads[i] = np.pad(gr, ((0, 1), (0, 0)))
    if img.shape[2] == 4: grads[i] = grads[i]  # alpha handled separately
decls = B.parse_decls(d, g)
pals = {oi: B.palette(d, g, oi) for oi in range(g['object_count'])}
seg = {int(k): tuple(v) for k, v in json.load(open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone-pkg00_segmap.json')).items()}
results = {}
for dd in sorted(decls, key=lambda x: x['decl_id']):
    did = dd['decl_id']
    if did not in seg: continue
    off, st = seg[did]
    s = B.parse_seg(d, dd, off, st)
    if 'uv0' not in s: continue
    uv = s['uv0']
    if len(uv) > 4000: uv = uv[::len(uv) // 4000 + 1]
    scores = []
    for i, img in imgs.items():
        h, w = img.shape[:2]
        xs = (np.clip(uv[:, 0], 0, 1) * (w - 1)).astype(int)
        ys = (np.clip(uv[:, 1], 0, 1) * (h - 1)).astype(int)
        samp = img[ys, xs]
        if texs[i]['fmt'] == 20:
            hit = (samp[:, 3] > 128).mean()
            scores.append((float(hit), i, 'alpha-hit'))
        else:
            modal = np.median(img[:, :, :3].reshape(-1, 3), axis=0)
            painted = (np.abs(samp[:, :3] - modal).max(axis=1) > 24).mean()
            st_ = grads[i][ys, xs].mean() / 255.0
            scores.append((float(painted * (0.2 + st_)), i, f'painted={painted:.2f} struct={st_:.3f}'))
    scores.sort(reverse=True)
    results[did] = scores[:3]
    print(f"decl{did} obj{dd['obj']} vtx{dd['vtx']}: " + ' | '.join(f"tex{i} {sc:.3f} ({note})" for sc, i, note in scores[:3]))
json.dump({str(k): [(sc, i) for sc, i, _ in v] for k, v in results.items()}, open('/home/hatch/workspace/_doa4p2-scratch/p6/tex_assign.json', 'w'), indent=1)
