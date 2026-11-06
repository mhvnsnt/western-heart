#!/usr/bin/env python3
"""proof_render.py — software z-buffer render of the EYES phase proof scenes (no WebGL: draws stall on the agent box).

  node tools/eyes/proof_dump.mjs /tmp/eyes-proof.json && python3 tools/eyes/proof_render.py /tmp/eyes-proof.json tools/eyes/proof

Orthographic front view (looking down -Z), flat Lambert shading, material base colours only (no textures).
Writes one close-up per scene plus a contact sheet (eyes-proof-sheet.png).
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255

def render(scene, size=480, half=0.075):
    eyes = np.array(scene['eyes']); c = eyes.mean(0) if len(eyes) else np.array(scene['head'])
    cx, cy = c[0], c[1] - 0.01
    img = np.full((size, size, 3), 0.12); zb = np.full((size, size), -1e9)
    light = np.array([0.3, 0.4, 1.0]); light /= np.linalg.norm(light)
    s = size / (2 * half)
    for t in scene['tris']:
        P = np.array(t[:9], float).reshape(3, 3); col = hexrgb(t[9])
        n = np.cross(P[1] - P[0], P[2] - P[0]); nl = np.linalg.norm(n)
        if nl < 1e-12: continue
        n /= nl
        shade = 0.25 + 0.75 * abs(n @ light)
        X = (P[:, 0] - cx) * s + size / 2; Y = size / 2 - (P[:, 1] - cy) * s; Z = P[:, 2]
        x0, x1 = int(max(0, np.floor(X.min()))), int(min(size - 1, np.ceil(X.max())))
        y0, y1 = int(max(0, np.floor(Y.min()))), int(min(size - 1, np.ceil(Y.max())))
        if x0 > x1 or y0 > y1: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (Y[1] - Y[2]) * (X[0] - X[2]) + (X[2] - X[1]) * (Y[0] - Y[2])
        if abs(d) < 1e-12: continue
        a = ((Y[1] - Y[2]) * (xs - X[2]) + (X[2] - X[1]) * (ys - Y[2])) / d
        b = ((Y[2] - Y[0]) * (xs - X[2]) + (X[0] - X[2]) * (ys - Y[2])) / d
        g = 1 - a - b
        m = (a >= 0) & (b >= 0) & (g >= 0)
        if not m.any(): continue
        z = a * Z[0] + b * Z[1] + g * Z[2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]; upd = m & (z > sub)
        sub[upd] = z[upd]
        img[y0:y1 + 1, x0:x1 + 1][upd] = col * shade
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    ImageDraw.Draw(im).text((8, 8), scene['name'], fill=(255, 220, 120))
    return im

def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    scenes = json.loads(src.read_text()); ims = []
    for sc in scenes:
        im = render(sc); im.save(out / f"{sc['name']}.png"); ims.append(im); print('wrote', out / f"{sc['name']}.png")
    cols = 3; rows = (len(ims) + cols - 1) // cols; w, h = ims[0].size
    sheet = Image.new('RGB', (w * cols, h * rows), (0, 0, 0))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out / 'eyes-proof-sheet.png'); print('wrote', out / 'eyes-proof-sheet.png')

if __name__ == '__main__':
    main()
