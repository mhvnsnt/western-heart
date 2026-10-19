#!/usr/bin/env python3
"""Improved nude-reskin texture pipeline.
Stage 1: detect pale unpainted patches -> OpenCV Telea inpaint from surrounding skin.
Stage 2: procedural skin detail (mottling + grain), tattoo/clothing preserved.
Uses only license-clean inputs: the model's own textures + procedural noise.
"""
import numpy as np, cv2, sys

def load_base(name):
    return np.load(f'/home/hatch/workspace/skin-research/work/{name}-base.npy')

def detect_patches(img, v_hi, s_lo, min_area):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    s = hsv[...,1]/255.0; v = hsv[...,2]/255.0
    pale = ((v > v_hi) & (s < s_lo)).astype(np.uint8)*255
    # keep only flat fills: low local stddev
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mean = cv2.blur(gray, (15,15))
    sq = cv2.blur(gray*gray, (15,15))
    std = np.sqrt(np.maximum(sq-mean*mean,0))
    flat = (std < 9.0).astype(np.uint8)*255
    cand = cv2.bitwise_and(pale, flat)
    # connected components, drop small
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cand, 8)
    mask = np.zeros_like(cand)
    kept=0
    for i in range(1,n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            mask[lab==i]=255; kept+=1
    print(f'  patch components kept: {kept}/{n-1}, mask frac: {(mask>0).mean():.4f}')
    # dilate a bit so inpaint covers edges
    mask = cv2.dilate(mask, np.ones((7,7),np.uint8))
    return mask

def add_mottling(img, seed):
    rng = np.random.default_rng(seed)
    h,w,_ = img.shape
    # multi-octave value noise via resized random grids
    noise = np.zeros((h,w), np.float32)
    amp, freq = 1.0, 4
    for _ in range(4):
        g = rng.random((freq+2, freq+2), dtype=np.float32)
        up = cv2.resize(g, (w,h), interpolation=cv2.INTER_CUBIC)
        noise += amp*up; amp*=0.5; freq*=2
    noise = (noise-noise.mean())/noise.std()
    # luminance mottling +/-3.5%, plus warm shift
    lum = 1.0 + 0.035*noise
    out = img.astype(np.float32)*lum[...,None]
    warm = 0.5+0.5*noise
    out[...,0] *= (1.0+0.020*warm)   # R
    out[...,2] *= (1.0-0.015*warm)   # B
    # fine grain +/-1.5%
    grain = rng.normal(0,1,(h,w)).astype(np.float32)
    grain = cv2.GaussianBlur(grain,(0,0),0.8)
    out *= (1.0+0.015*grain)[...,None]
    return np.clip(out,0,255).astype(np.uint8)

def process(name, v_hi, s_lo, min_area, seed):
    print(f'== {name} ==')
    img = load_base(name)
    mask = detect_patches(img, v_hi, s_lo, min_area)
    cv2.imwrite(f'/home/hatch/workspace/skin-research/work/{name}-patchmask.png', mask)
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    inp = cv2.inpaint(bgr, mask, 9, cv2.INPAINT_TELEA)
    img2 = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
    print('  inpainted')
    img3 = add_mottling(img2, seed)
    print('  detail added')
    out = f'/home/hatch/workspace/skin-research/work/{name}-skin-improved.png'
    cv2.imwrite(out, cv2.cvtColor(img3, cv2.COLOR_RGB2BGR))
    print('  wrote', out)
    return out

if __name__=='__main__':
    # star: deeper tone, patches are pale flat fills
    process('star', v_hi=0.70, s_lo=0.28, min_area=400, seed=7)
    # silv: lighter tone, patches near-white
    process('silv', v_hi=0.74, s_lo=0.26, min_area=400, seed=21)
