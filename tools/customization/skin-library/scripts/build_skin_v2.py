#!/usr/bin/env python3
"""Stage 1b: regional skin-tone fill for large patches.
For each patch component, sample good-skin color from a ring around it,
fill with that tone + matched grain, feather edges.
"""
import numpy as np, cv2

W = '/home/hatch/workspace/skin-research/work/'

def regional_fill(name, seed):
    print(f'== {name} v2 ==')
    img = cv2.cvtColor(cv2.imread(f'{W}{name}-skin-improved.png'), cv2.COLOR_BGR2RGB)
    mask = cv2.imread(f'{W}{name}-patchmask.png', cv2.IMREAD_GRAYSCALE)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((mask>0).astype(np.uint8), 8)
    out = img.copy().astype(np.float32)
    rng = np.random.default_rng(seed)
    for i in range(1, n):
        comp = (lab==i)
        area = stats[i, cv2.CC_STAT_AREA]
        # ring: dilate 60 minus dilate 8, excluding patch areas
        d60 = cv2.dilate(comp.astype(np.uint8), np.ones((61,61),np.uint8)).astype(bool)
        d8 = cv2.dilate(comp.astype(np.uint8), np.ones((9,9),np.uint8)).astype(bool)
        ring = d60 & ~d8 & (mask==0)
        if ring.sum() < 50:
            continue
        ring_px = img[ring].astype(np.float32)
        med = np.median(ring_px, axis=0)
        std = ring_px.std(axis=0).mean()
        # fill with tone + grain matched to ring variance
        fill = np.ones((comp.sum(),3), np.float32)*med
        fill += rng.normal(0, max(std,6), fill.shape)
        out[comp] = fill
        # feather edge: blur a band around component boundary
    # feather: blend filled regions at edges via blurred mask
    msoft = cv2.GaussianBlur(mask.astype(np.float32)/255.0, (0,0), 6)
    # recombine: filled where mask=1 feathered
    base = cv2.cvtColor(cv2.imread(f'{W}{name}-skin-improved.png'), cv2.COLOR_BGR2RGB).astype(np.float32)
    # out already has fills; feather between out and base using soft mask
    final = out*msoft[...,None] + base*(1-msoft[...,None])
    # second mottling pass to unify
    h,w,_ = final.shape
    rng2 = np.random.default_rng(seed+1)
    noise = np.zeros((h,w), np.float32); amp, freq = 1.0, 5
    for _ in range(4):
        g = rng2.random((freq+2,freq+2), dtype=np.float32)
        noise += amp*cv2.resize(g,(w,h),interpolation=cv2.INTER_CUBIC); amp*=0.5; freq*=2
    noise = (noise-noise.mean())/noise.std()
    final *= (1.0+0.030*noise)[...,None]
    final = np.clip(final,0,255).astype(np.uint8)
    p = f'{W}{name}-skin-v2.png'
    cv2.imwrite(p, cv2.cvtColor(final, cv2.COLOR_RGB2BGR))
    print('  wrote', p, f'({n-1} components)')

regional_fill('star', 7)
regional_fill('silv', 21)
