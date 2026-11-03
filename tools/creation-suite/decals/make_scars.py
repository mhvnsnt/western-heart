#!/usr/bin/env python3
"""make_scars.py — generate Western Heart's own CC0 scar decal set (procedural, deterministic).

Why procedural: the repo holds NO scar texture (PR #1518 audit: 0 scar-labeled legacy assets;
PR #1523: Tekken 7 has exactly one scar-named face-paint item, kaz_fam_scar / item 90016, and its
texture file is not in western-heart). Owner order (CREATION-SUITE-ORDER, scars "create or cut"):
create. So these are original textures drawn by this script — no source-game pixels — released
CC0 by Western Heart.

Usage: python3 tools/creation-suite/decals/make_scars.py [out_dir]
  default out_dir: customization/decal-library/scars
Writes <id>.png (RGBA, straight alpha) + scars.json (id, name, default region, u/v hint, size).
Same seed -> same bytes (numpy default_rng seeded per scar).

Look: a scar is a raised, slightly glossy, pinker-or-paler line with a darker healed rim; old
stitch marks are short cross ticks; burns are irregular patches with a mottled centre. The
colour is near-neutral so the layer's colour control (WWE Parts Color) can tint it to the skin.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else 'customization/decal-library/scars'

# id, generic name, region, (u, v) hint on the region canvas, canvas (w, h), recipe
SCARS = [
    ('cheek-slash',    'Cheek Slash',      'face',        (0.10, 0.12), (256, 256), 'slash'),
    ('brow-cut',       'Brow Cut',         'face',        (0.06, 0.40), (256, 128), 'short'),
    ('lip-split',      'Lip Split',        'face',        (0.02, -0.02), (128, 128), 'tiny'),
    ('nose-bridge',    'Nose Bridge',      'face',        (0.00, 0.30), (192, 128), 'short'),
    ('eye-cross',      'Eye Cross',        'face',        (0.07, 0.32), (128, 256), 'vertical'),
    ('chin-nick',      'Chin Nick',        'face',        (0.02, -0.08), (128, 128), 'tiny'),
    ('chest-slash',    'Chest Slash',      'chest',       (0.00, 0.55), (512, 512), 'long'),
    ('back-lashes',    'Back Lashes',      'back',        (0.50, 0.55), (512, 512), 'lashes'),
    ('forearm-stitch', 'Stitched Forearm', 'forearm_R',   (0.00, 0.50), (512, 160), 'stitched'),
    ('shoulder-claw',  'Claw Marks',       'upper_arm_L', (0.00, 0.30), (256, 256), 'claws'),
    ('burn-patch',     'Burn Patch',       'upper_arm_R', (0.00, 0.50), (256, 256), 'burn'),
]


def stroke(mask, rim, pts, w0, w1, rng):
    """Paint a tapered stroke along a polyline into mask (core) and rim (wider halo)."""
    H, W = mask.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = len(pts)
    for i in range(n - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        t0, t1 = i / (n - 1), (i + 1) / (n - 1)
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1.0
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        tt = t0 + (t1 - t0) * t
        width = (w0 + (w1 - w0) * tt) * np.sin(np.pi * np.clip(tt, 0.02, 0.98)) ** 0.6
        core = np.clip(1 - d / np.maximum(width, 0.5), 0, 1)
        halo = np.clip(1 - d / np.maximum(width * 2.6, 1.0), 0, 1)
        np.maximum(mask, core, out=mask)
        np.maximum(rim, halo, out=rim)


def jitter_line(rng, a, b, n=24, amp=2.0):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        nx, ny = -(b[1] - a[1]), (b[0] - a[0])
        L = math.hypot(nx, ny) or 1
        off = rng.normal(0, amp) * math.sin(math.pi * t)
        pts.append((x + nx / L * off, y + ny / L * off))
    return pts


def render(recipe, W, H, rng):
    mask = np.zeros((H, W), np.float32)
    rim = np.zeros((H, W), np.float32)
    stitch = np.zeros((H, W), np.float32)
    m = 0.12
    if recipe == 'slash':
        stroke(mask, rim, jitter_line(rng, (W * m, H * 0.75), (W * (1 - m), H * 0.28), amp=2.5), 5, 4, rng)
    elif recipe == 'short':
        stroke(mask, rim, jitter_line(rng, (W * 0.18, H * 0.62), (W * 0.82, H * 0.40), amp=1.5), 4, 3, rng)
    elif recipe == 'tiny':
        stroke(mask, rim, jitter_line(rng, (W * 0.5, H * 0.22), (W * 0.47, H * 0.78), n=12, amp=1.0), 4, 3, rng)
    elif recipe == 'vertical':
        stroke(mask, rim, jitter_line(rng, (W * 0.52, H * 0.08), (W * 0.46, H * 0.92), amp=1.8), 4, 4, rng)
    elif recipe == 'long':
        stroke(mask, rim, jitter_line(rng, (W * 0.12, H * 0.18), (W * 0.86, H * 0.82), n=40, amp=4), 9, 7, rng)
    elif recipe == 'lashes':
        for k in range(3):
            y0 = H * (0.2 + 0.25 * k) + rng.normal(0, 8)
            stroke(mask, rim, jitter_line(rng, (W * 0.1, y0 + 60), (W * 0.9, y0 - 50), n=36, amp=5), 7, 6, rng)
    elif recipe == 'stitched':
        pts = jitter_line(rng, (W * 0.06, H * 0.52), (W * 0.94, H * 0.48), n=40, amp=2)
        stroke(mask, rim, pts, 5, 5, rng)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        for i in range(2, 38, 3):
            x, y = pts[i]
            d = np.hypot((xx - x) * 3.0, (yy - y) * 0.45)
            np.maximum(stitch, np.clip(1 - d / 9.0, 0, 1), out=stitch)
    elif recipe == 'claws':
        for k in range(3):
            x0 = W * (0.25 + 0.22 * k)
            stroke(mask, rim, jitter_line(rng, (x0, H * 0.1), (x0 + W * 0.08, H * 0.9), amp=2), 5, 3, rng)
    elif recipe == 'burn':
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy = W / 2, H / 2
        ang = np.arctan2(yy - cy, xx - cx)
        r = np.hypot(xx - cx, yy - cy)
        edge = 0.36 * W * (1 + 0.12 * np.sin(3 * ang + rng.uniform(0, 6)) + 0.07 * np.sin(7 * ang + rng.uniform(0, 6)))
        mask = np.clip((edge - r) / 10.0, 0, 1)
        rim = np.clip((edge * 1.15 - r) / 14.0, 0, 1)
    # mottled tissue
    noise = rng.normal(0, 1, (H // 4 + 1, W // 4 + 1)).astype(np.float32)
    noise = np.array(Image.fromarray(noise).resize((W, H), Image.BICUBIC))
    noise = (noise - noise.min()) / (np.ptp(noise) or 1)
    # colour: raised pale-pink core, darker healed rim, near-neutral so the layer tint can match skin
    core_c = np.array([0.93, 0.78, 0.76], np.float32)
    rim_c = np.array([0.55, 0.36, 0.34], np.float32)
    st_c = np.array([0.45, 0.30, 0.30], np.float32)
    rimonly = np.clip(rim - mask, 0, 1)
    rgb = (core_c[None, None, :] * (0.85 + 0.15 * noise[..., None]) * mask[..., None]
           + rim_c[None, None, :] * rimonly[..., None]
           + st_c[None, None, :] * stitch[..., None])
    a = np.clip(mask * 0.95 + rimonly * 0.45 + stitch * 0.9, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, rgb / np.maximum(a[..., None], 1e-4), 0)
    img = np.dstack([np.clip(rgb, 0, 1), a])
    out = Image.fromarray((img * 255 + 0.5).astype(np.uint8), 'RGBA')
    return out.filter(ImageFilter.GaussianBlur(0.6))


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {'_doc': 'Western Heart procedural scar decals (CC0). Generated by tools/creation-suite/decals/make_scars.py; '
                        'no source-game pixels. region/u/v = default placement on the body-region canvas '
                        '(game/js/decal-layers.js BODY_REGIONS); v hints < 0 are clamped by the layer model.',
                'license': 'CC0-1.0', 'scars': []}
    for i, (sid, name, region, (u, v), (W, H), recipe) in enumerate(SCARS):
        rng = np.random.default_rng(1000 + i)
        img = render(recipe, W, H, rng)
        path = os.path.join(OUT, sid + '.png')
        img.save(path, optimize=True)
        manifest['scars'].append({'id': sid, 'name': name, 'region': region, 'u': u, 'v': max(0.0, v),
                                  'size': [W, H], 'file': sid + '.png'})
        print('wrote', path)
    with open(os.path.join(OUT, 'scars.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    with open(os.path.join(OUT, 'LICENSE.txt'), 'w') as f:
        f.write('Western Heart scar decals — CC0 1.0 Universal (public domain dedication).\n'
                'Generated procedurally by tools/creation-suite/decals/make_scars.py. No third-party pixels.\n')


if __name__ == '__main__':
    main()
