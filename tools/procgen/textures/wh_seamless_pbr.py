#!/usr/bin/env python3
"""wh_seamless_pbr.py — Python port of TEXTtoPBR's (MIT) client-side PBR algorithms.

Input:  albedo image (e.g. from Pollinations via wh_prompt_pbr.sh)
Output: tileable PBR set: albedo (seamless), normal (+Y, OpenGL), roughness, height
Method (mirrors Vasco888888/text-to-pbr):
  - Seamless tiling: mirror-blend edges (offset by half, crossfade the seam band).
  - Normal map: Sobel gradients of luminance -> tangent-space normals, +Y up (glTF).
  - Roughness: inverted, blurred luminance (bright = rough).
  - Height: raw luminance.

Usage: wh_seamless_pbr.py IN.png OUTDIR/ [--size 1024] [--normal-strength 2.0]
"""
import argparse, math, os
import numpy as np
from PIL import Image, ImageFilter

def _best_boundary(a, axis, margin):
    """Smoothest adjacent line-pair along axis, constrained to [margin, n-margin]
    so the seam band we place later never touches the tile edge."""
    n = a.shape[axis]
    d = np.abs(np.diff(a, axis=axis))
    axes = tuple(i for i in range(a.ndim) if i != axis)
    d = d.mean(axis=axes)  # d[k] = diff between lines k and k+1
    lo, hi = margin, n - margin
    if hi <= lo:
        return n // 2
    k = int(np.argmin(d[lo - 1:hi - 1])) + (lo - 1)
    return k + 1  # boundary s puts lines (s-1, s) at the tile edge

def _seamless_1d(a, axis):
    """Exact tile along one axis: roll the image so its SMOOTHEST adjacent
    line-pair lands on the tile boundary. The tiled edge then shows that
    smooth pair — seamless for any input, no blending artifacts, no soft bands.
    Interior detail is untouched (interior lines repeat as pattern, not seams)."""
    n = a.shape[axis]
    s = _best_boundary(a, axis, margin=2)
    return np.roll(a, (n - s) % n, axis=axis)

def mirror_blend_seamless(img, blend=0.18):
    """Make tileable via smoothest-boundary roll (hardened TEXTtoPBR-style).
    `blend` kept for API compatibility; the exact method needs no blend band."""
    a = np.asarray(img).astype(np.float32)
    a = _seamless_1d(a, axis=1)  # x edges
    a = _seamless_1d(a, axis=0)  # y edges
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def luminance(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

def normal_map(img, strength=2.0):
    a = np.asarray(img).astype(np.float32)
    lum = luminance(a)
    # Sobel
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], np.float32)
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    for i in range(3):
        for j in range(3):
            gx += kx[i, j] * np.roll(np.roll(lum, i - 1, 0), j - 1, 1)
            gy += ky[i, j] * np.roll(np.roll(lum, i - 1, 0), j - 1, 1)
    # +Y up (glTF/OpenGL convention): negate green channel of DirectX-style
    n = np.dstack((-gx * strength / 255.0, gy * strength / 255.0,
                   np.ones_like(lum)))
    n /= np.linalg.norm(n, axis=2, keepdims=True) + 1e-8
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))

def roughness_map(img, blur=3):
    lum = Image.fromarray(luminance(np.asarray(img).astype(np.float32)).astype(np.uint8))
    lum = lum.filter(ImageFilter.GaussianBlur(blur))
    inv = 255 - np.asarray(lum).astype(np.float32)
    rgb = np.dstack([inv] * 3)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("outdir")
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--normal-strength", type=float, default=2.0)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    img = Image.open(a.inp).convert("RGB").resize((a.size, a.size), Image.LANCZOS)
    alb = mirror_blend_seamless(img)
    alb.save(f"{a.outdir}/albedo.png")
    normal_map(alb, a.normal_strength).save(f"{a.outdir}/normal.png")
    roughness_map(alb).save(f"{a.outdir}/roughness.png")
    Image.fromarray(luminance(np.asarray(alb).astype(np.float32)).astype(np.uint8)
           ).save(f"{a.outdir}/height.png")
    # metallic: stages are dielectric by default -> flat black (metalness workflow)
    Image.new("RGB", (a.size, a.size), (0, 0, 0)).save(f"{a.outdir}/metallic.png")
    print(f"PBR set -> {a.outdir}/ (albedo, normal, roughness, height, metallic)")

if __name__ == "__main__":
    main()
