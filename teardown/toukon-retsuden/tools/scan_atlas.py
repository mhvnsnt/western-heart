#!/usr/bin/env python3
"""Scan the JP EXE for the T1 menu atlas as raw 256x256 4bpp data (numpy, fast).

Two passes:
1. Cumsum filter: a text atlas is mostly background (sparse ink). Keep 32KB
   windows with 2%-40% nonzero nibbles.
2. T1 rect test on survivors only.
"""
import struct
import numpy as np

EXE = "/home/hatch/workspace/toukon-english/work/tr1-files/SLPS_000.84"
data = open(EXE, "rb").read()

T1_OFF = 0x5B0F8
rects = []
for i in range(66):
    x, y, w, h = struct.unpack_from("<HHHH", data, T1_OFF + i*8)
    if x == 0xFFFF:
        break
    rects.append((x - 512, y, w, h))
print("T1 rects:", len(rects))

b = np.frombuffer(data, dtype=np.uint8)
pix = np.empty(len(b) * 2, dtype=np.uint8)
pix[0::2] = b & 0x0F
pix[1::2] = b >> 4
nz = (pix != 0).astype(np.int32)
cum = np.concatenate([[0], np.cumsum(nz)])

lo, hi = 0x40000, len(data) - 32768
offs = np.arange(lo, hi, 16)
starts = offs * 2
totals = cum[starts + 65536] - cum[starts]
fracs = totals / 65536.0
mask = (fracs >= 0.02) & (fracs <= 0.40)
survivors = offs[mask]
print(f"pass1 survivors: {len(survivors)} of {len(offs)}")

best = []
for off in survivors:
    img = pix[int(off)*2 : int(off)*2 + 65536].reshape(256, 256)
    nzr = 0
    total = 0
    for (rx, ry, rw, rh) in rects:
        sub = img[ry:ry+rh, rx:rx+rw]
        nzr += int((sub != 0).sum())
        total += sub.size
    frac = nzr / total
    nd = len(np.unique(img))
    if frac < 0.02 or frac > 0.8 or nd < 2:
        continue
    best.append((frac * nd, int(off), frac, nd))
best.sort(reverse=True)
print("candidates:", len(best))
for s, off, frac, nd in best[:20]:
    print(f"  file 0x{off:06x} RAM 0x{off - 0x800 + 0x80010000:08x} score={s:.2f} ink={frac:.2f} distinct={nd}")
