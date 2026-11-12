"""Skin pass: light-touch tone nudge toward Angel + variation preservation proof.
- Samples Angel's skin tone from held photos (doorway thigh, 457 cheek).
- Samples Megami's skin from her textures.
- Derives per-channel gains moving ~25% of the measured delta, hard-capped
  (R<=1.04, G<=1.015, B>=0.95). Applies to skin-classified pixels only
  (ink/dark pixels excluded). Per-channel gains preserve inter-zone ratios.
- Samples general skin + variation zones before/after and writes skin_report.json.
"""
import json
import numpy as np
from PIL import Image

BASE = '/home/hatch/workspace/_pilot2-v2-20261108'

def box_mean(img_arr, cx, cy, r=14):
    b = img_arr[cy - r:cy + r, cx - r:cx + r].reshape(-1, 3)
    return b.mean(0)

# --- Angel samples ---
p5 = np.asarray(Image.open('/home/hatch/workspace/user/files/1000182498_22_nnd9.png').convert('RGB')).astype(np.float64)
# doorway main image: her right thigh front ~(472, 760); left thigh ~(565, 720); forearm raised ~(390,330) is arm
angel_thigh = box_mean(p5, 472, 760)
angel_thigh2 = box_mean(p5, 565, 720)
f2 = np.asarray(Image.open(f'{BASE}/angel/detail_457_f002.png').convert('RGB')).astype(np.float64)
# cheek approx from that frame's landmarks
track = json.load(open(f'{BASE}/angel_track.json'))
lm = np.array(track['detail_457_f002.png']['landmarks'])
H, W = f2.shape[:2]
ck = (((lm[234] + lm[1]) / 2)[:2] * [W, H]).astype(int)
angel_cheek = box_mean(f2, int(ck[0]), int(ck[1]), 10)
angel_mean = np.mean([angel_thigh, angel_thigh2, angel_cheek], axis=0)
print('angel samples: thigh', angel_thigh.round(1), 'thigh2', angel_thigh2.round(1), 'cheek', angel_cheek.round(1), 'mean', angel_mean.round(1))

# --- Megami texture samples ---
TEXTURES = {'Parvati': 'tex/Parvati.png', 'Parvati_Torso': 'tex/Parvati_Torso_v2.png',
            'Parvati_Arm': 'tex/Parvati_Arm.png', 'Parvati_Leg': 'tex/Parvati_Leg.png'}
samples = {}
arrs = {}
for name, path in TEXTURES.items():
    arrs[name] = np.asarray(Image.open(f'{BASE}/{path}').convert('RGB')).astype(np.float64)

# general skin: broad skin-classified mean per texture (mid luminance, R>B warm)
def skin_mask(a):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return (lum > 45) & (lum < 225) & (r > b + 8) & (r > g - 6)

gen_means = {}
for name, a in arrs.items():
    m = skin_mask(a)
    gen_means[name] = a[m].mean(0)
    print(name, 'general skin mean', gen_means[name].round(1), 'skin px', int(m.sum()))
meg_mean = np.mean(list(gen_means.values()), axis=0)
print('megami mean', meg_mean.round(1), 'angel mean', angel_mean.round(1))

# gains: move 25% of the ratio delta, capped
ratio = angel_mean / meg_mean
gains = 1.0 + 0.25 * (ratio - 1.0)
gains = np.clip(gains, [0.95, 0.99, 0.95], [1.04, 1.015, 1.0])
print('raw ratio', ratio.round(3), '-> applied gains', gains.round(4))

# variation-zone samples on torso texture (before)
tor = arrs['Parvati_Torso']
zones = {'areola_L': (438, 452), 'areola_R': (586, 452), 'chest_skin': (512, 300),
         'belly_skin': (512, 560), 'gp_area': (512, 735), 'back_skin': (150, 640)}
before = {k: box_mean(tor, x, y, 10) for k, (x, y) in zones.items()}

out_paths = {}
for name, a in arrs.items():
    m = skin_mask(a)
    out = a.copy()
    out[m] = np.clip(a[m] * gains, 0, 255)
    p = f'{BASE}/tex/{name}_skin.png'
    Image.fromarray(out.astype(np.uint8)).save(p)
    out_paths[name] = p
    print('wrote', p)

tor2 = np.asarray(Image.open(out_paths['Parvati_Torso']).convert('RGB')).astype(np.float64)
after = {k: box_mean(tor2, x, y, 10) for k, (x, y) in zones.items()}
rep = {'angel_samples': {'thigh': angel_thigh.tolist(), 'thigh2': angel_thigh2.tolist(),
                         'cheek': angel_cheek.tolist(), 'mean': angel_mean.tolist()},
       'megami_general_means': {k: v.tolist() for k, v in gen_means.items()},
       'gains_applied': gains.tolist(),
       'zones_before': {k: v.tolist() for k, v in before.items()},
       'zones_after': {k: v.tolist() for k, v in after.items()}}
for k in zones:
    b, a = before[k], after[k]
    print(f'zone {k}: before {b.round(1)} after {a.round(1)} delta% {((a-b)/b*100).round(2)}')
json.dump(rep, open(f'{BASE}/work/skin_report.json', 'w'), indent=1)
print('SKIN PASS done')
