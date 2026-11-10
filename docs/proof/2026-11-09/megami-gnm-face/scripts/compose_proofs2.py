"""Finisher-2 proof composition: side-by-side sheets + tone strip for the
WINNER build. Usage: compose_proofs2.py <winner_tag> <final_glb_path>
Sheets (all matched-camera, gate framing):
  sbs_front_v2 / sbs_front_orig / sbs_front_angel
  sbs_q34_v2   / sbs_q34_orig   / sbs_q34_angel
Tone strip: face zones from texture_report.json (atlas is byte-identical in
every candidate incl. the final build) + torso/arm sampled from the FINAL
GLB's own images 19/26 (same method as compose_proofs.py).
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/hatch/workspace/_gnmface-20261109/scripts')
from glb_lib import load_glb

TAG = sys.argv[1]
FINAL = sys.argv[2]
W = '/home/hatch/workspace/_gnmface-20261109/work'
P = '/home/hatch/workspace/_gnmface-20261109/proof'
V2 = '/home/hatch/workspace/_pilot2-v2-20261108'

def sheet(model_path, ref_path, out, left_label, right_label, H=900):
    m = Image.open(model_path).convert('RGB')
    r = Image.open(ref_path).convert('RGB')
    def rs(im):
        return im.resize((int(im.width * H / im.height), H))
    m, r = rs(m), rs(r)
    s = Image.new('RGB', (m.width + r.width + 12, H + 28), (20, 18, 28))
    s.paste(m, (0, 28))
    s.paste(r, (m.width + 12, 28))
    dr = ImageDraw.Draw(s)
    dr.text((8, 8), left_label, fill=(255, 255, 255))
    dr.text((m.width + 20, 8), right_label, fill=(255, 255, 255))
    s.save(out)
    print('wrote', out, s.size)

WF = f'{P}/final_front_{TAG}.png'
WQ = f'{P}/final_q34_{TAG}.png'
sheet(WF, f'{P}/gate_on_front_v2base.png', f'{P}/sbs_front_v2.png', f'WINNER {TAG} (GNM, AngelFace=1)', 'REJECTED V2 WARP (AngelFace=1)')
sheet(WF, f'{P}/gate_off_front.png', f'{P}/sbs_front_orig.png', f'WINNER {TAG} (GNM, AngelFace=1)', 'ORIGINAL MEGAMI FACE (AngelFace=0)')
sheet(WF, f'{V2}/angel/f0004.png', f'{P}/sbs_front_angel.png', f'WINNER {TAG} (GNM, AngelFace=1)', 'ANGEL REFERENCE f0004')
sheet(WQ, f'{P}/gate_on_q34_v2base.png', f'{P}/sbs_q34_v2.png', f'WINNER {TAG} 3/4 (GNM, AngelFace=1)', 'REJECTED V2 WARP 3/4 (AngelFace=1)')
sheet(WQ, f'{P}/gate_on_q34_corr2_a.png', f'{P}/sbs_q34_corr2a.png', f'WINNER {TAG} 3/4 (GNM, AngelFace=1)', 'CORR2_A 3/4 (stage-2 GNM)')
sheet(WQ, f'{V2}/angel/482_f003.png', f'{P}/sbs_q34_angel.png', f'WINNER {TAG} 3/4 (GNM, AngelFace=1)', 'ANGEL REFERENCE 482_f003')

# ---- tone strip from the FINAL glb ----
g, buf = load_glb(FINAL)

def img_arr(ii):
    bv = g['bufferViews'][g['images'][ii]['bufferView']]
    data = bytes(buf[bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']])
    from io import BytesIO
    return np.asarray(Image.open(BytesIO(data)).convert('RGB'), dtype=np.float64)

def trim_mean(vals):
    lum = vals @ np.array([0.299, 0.587, 0.114])
    lo, hi = np.quantile(lum, 0.1), np.quantile(lum, 0.9)
    k = vals[(lum >= lo) & (lum <= hi)]
    return k.mean(0)

rep = json.load(open(f'{W}/texture_report.json'))
samples = {
    'face cheek (new atlas)': np.array(rep['megami_after']['cheek']),
    'face forehead (new atlas)': np.array(rep['megami_after']['forehead']),
    'lips (new atlas)': np.array(rep['megami_lip_after']),
}
for name, ii in [('torso (image 19)', 19), ('arm (image 26)', 26)]:
    a = img_arr(ii)
    flat = a.reshape(-1, 3)
    lum = flat @ np.array([0.299, 0.587, 0.114])
    skin = flat[(lum > 40) & (lum < 170) & (flat[:, 0] > flat[:, 2] * 1.1)]
    samples[name] = trim_mean(skin)
    print(name, 'skin texels:', len(skin), 'mean', np.round(samples[name], 1))

strip = Image.new('RGB', (len(samples) * 220, 150), (24, 22, 32))
dr = ImageDraw.Draw(strip)
for i, (name, v) in enumerate(samples.items()):
    x = i * 220 + 10
    dr.rectangle([x, 10, x + 200, 90], fill=tuple(int(c) for c in v))
    dr.text((x, 100), name, fill=(255, 255, 255))
    dr.text((x, 118), 'RGB ' + ' '.join(str(int(c)) for c in v), fill=(200, 200, 210))
strip.save(f'{P}/skin_tone_strip.png')
json.dump({k: [round(float(c), 2) for c in v] for k, v in samples.items()},
          open(f'{P}/skin_tone_samples.json', 'w'), indent=1)
print('wrote skin_tone_strip.png + skin_tone_samples.json')
