#!/usr/bin/env python3
"""tools/souls/textures.py — tileable surface textures for the soul bodies, made from Osamu Sato's own pixels.

Sato's Eastern Mind renders have a dithered, speckled surface (a few hundred palette colours scattered pixel by pixel)
rather than flat colour. For each surface this collects the pixels of that surface from the soul's own art (a region
of the bitmap and a colour rule that excludes the black background and the other surfaces), keeps the lit ones (the
render's shadows are not the surface's colour), sorts them by luminance,
and synthesises a tileable texture that picks from that palette with a periodic low-frequency field plus per-texel
noise: the art's own colours in the art's own speckle, wrapping seamlessly on any part.

    python3 tools/souls/textures.py --teardown teardown/eastern-mind --out tools/souls/tex
Reads the bitmaps from git (git show HEAD:<path>) when the checkout is sparse.
"""
import argparse
import io
import os
import subprocess

import numpy as np
from PIL import Image

CHARA = 'prologue-ending/bitmaps/CHARA/'
# name: (bitmap, region box (x0, y0, x1, y1) in px, colour rule)
SURFACES = {
    'kai_red': (CHARA + 'CHARA_b006_286x463.png', (60, 15, 230, 380), 'red'),
    'kai_blue': (CHARA + 'CHARA_b006_286x463.png', (20, 60, 270, 460), 'blue'),
    'kai_gold': (CHARA + 'CHARA_b006_286x463.png', (80, 245, 200, 320), 'gold'),
    'tou_teal': (CHARA + 'CHARA_b012_478x428.png', (200, 200, 420, 428), 'teal'),
    'tou_head': (CHARA + 'CHARA_b012_478x428.png', (340, 60, 478, 200), 'teal'),
}


def rule(name, a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    lum = r + g + b
    if name == 'red':
        return (r > 70) & (r > 1.7 * g) & (r > 1.7 * b)
    if name == 'blue':
        return (b > 60) & (b > 1.25 * r) & (b > 1.05 * g)
    if name == 'gold':
        return (r > 110) & (g > 80) & (b < 0.75 * g) & (r > 1.05 * b)
    if name == 'teal':
        return (g > 70) & (g > 1.15 * r) & (b > 0.6 * g) & (lum > 150)
    raise SystemExit('unknown rule ' + name)


def periodic_noise(n, rng, octaves=((4, 1.0), (8, 0.5), (16, 0.25))):
    y, x = np.mgrid[0:n, 0:n] / n
    f = np.zeros((n, n))
    for freq, amp in octaves:
        for _ in range(3):
            kx, ky = rng.integers(-freq, freq + 1, 2)
            ph = rng.uniform(0, 2 * np.pi)
            f += amp * np.cos(2 * np.pi * (kx * x + ky * y) + ph)
    f -= f.min()
    return f / max(f.max(), 1e-9)


def load(teardown, rel):
    p = os.path.join(teardown, rel)
    if os.path.exists(p):
        return Image.open(p).convert('RGB')
    raw = subprocess.run(['git', 'show', 'HEAD:' + p], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--teardown', default='teardown/eastern-mind')
    ap.add_argument('--out', default='tools/souls/tex')
    ap.add_argument('--size', type=int, default=256)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for i, (name, (rel, box, col)) in enumerate(SURFACES.items()):
        im = np.asarray(load(a.teardown, rel).crop(box))
        px = im[rule(col, im)]
        if len(px) < 50:
            raise SystemExit('%s: only %d pixels matched' % (name, len(px)))
        # a lit render's pixels include its shading: keep the lit part (luminance >= the 45th percentile) as the
        # surface's own colour, so the texture is the albedo's speckle, not the render's shadows
        lum = px.astype(int).sum(1)
        px = px[lum >= np.percentile(lum, 45)]
        order = np.argsort(px.astype(int).sum(1))
        pal = px[order]
        rng = np.random.default_rng(1000 + i)
        f = 0.65 * periodic_noise(a.size, rng) + 0.35 * rng.random((a.size, a.size))
        idx = np.clip((f * (len(pal) - 1)).astype(int), 0, len(pal) - 1)
        tex = pal[idx].astype(np.uint8)
        out = os.path.join(a.out, name + '.png')
        Image.fromarray(tex).save(out, optimize=True)
        print('%-10s %6d source pixels -> %s (mean rgb %s)' % (name, len(px), out, np.round(px.mean(0)).astype(int).tolist()))


if __name__ == '__main__':
    main()
