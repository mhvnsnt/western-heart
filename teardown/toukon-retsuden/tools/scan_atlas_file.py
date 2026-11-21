#!/usr/bin/env python3
"""Scan any file for a 256x256 4bpp text atlas (dominant-background filter).

A text atlas has one dominant nibble value (background) covering 60-98% of
its 32KB, with ink in a few other values. Pass 1 finds such windows via 16
per-value cumsums; pass 2 scores T1 rect regions on survivors.
Usage: scan_atlas_file.py <file> [lo] [hi]
"""
import struct
import sys
import numpy as np

PATH = sys.argv[1]
LO = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0
HI = int(sys.argv[3], 0) if len(sys.argv) > 3 else None

EXE = "/home/hatch/workspace/toukon-english/work/tr1-files/SLPS_000.84"
exe = open(EXE, "rb").read()
T1_OFF = 0x5B0F8
rects = []
for i in range(66):
    x, y, w, h = struct.unpack_from("<HHHH", exe, T1_OFF + i*8)
    if x == 0xFFFF:
        break
    rects.append((x - 512, y, w, h))

data = open(PATH, "rb").read()
if HI is None:
    HI = len(data) - 32768
print(f"{PATH}: {len(data)} bytes, scanning 0x{LO:x}..0x{HI:x}")

b = np.frombuffer(data, dtype=np.uint8)
pix = np.empty(len(b) * 2, dtype=np.uint8)
pix[0::2] = b & 0x0F
pix[1::2] = b >> 4

# Per-value cumsums (16 values)
cums = []
for v in range(16):
    cums.append(np.concatenate([[0], np.cumsum((pix == v).astype(np.int32))]))

offs = np.arange(LO, HI, 16)
starts = offs * 2
# dominant fraction per window
dom = np.zeros(len(offs), dtype=np.float64)
for v in range(16):
    c = cums[v]
    cnt = c[starts + 65536] - c[starts]
    dom = np.maximum(dom, cnt / 65536.0)
mask = (dom >= 0.60) & (dom <= 0.98)
survivors = offs[mask]
print(f"pass1 survivors: {len(survivors)} of {len(offs)}")

best = []
for off in survivors:
    img = pix[int(off)*2 : int(off)*2 + 65536].reshape(256, 256)
    nzr = 0
    total = 0
    bg = np.bincount(img.ravel(), minlength=16).argmax()
    for (rx, ry, rw, rh) in rects:
        sub = img[ry:ry+rh, rx:rx+rw]
        nzr += int((sub != bg).sum())
        total += sub.size
    frac = nzr / total
    nd = len(np.unique(img))
    if frac < 0.02 or frac > 0.8 or nd < 2:
        continue
    best.append((frac * nd, int(off), frac, nd, int(bg)))
best.sort(reverse=True)
print("candidates:", len(best))
for s, off, frac, nd, bg in best[:20]:
    print(f"  file 0x{off:06x} score={s:.2f} ink={frac:.2f} distinct={nd} bg={bg}")
