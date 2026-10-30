#!/usr/bin/env python3
"""Round 11 Job 5c: byte-structure discriminators for idx24 slot-9 pages.
Byte histogram, GE-opcode histogram (LE u32 top byte), and page images
at the exact factorizations of 2208 (48x46, 69x32, 92x24, 184x12)."""
import struct, os, glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

f = glob.glob(os.path.join(DEC, 'idx24_*.bin'))[0]
data = open(f, 'rb').read()
off, sz = slots_of(data)[9]
slot9 = data[off:off + sz]
pairs = [struct.unpack_from('>II', slot9, 0x78 + 8 * i) for i in range(40)]
pages = [slot9[o:o + s] for s, o in pairs]
allb = np.concatenate([np.frombuffer(p, dtype=np.uint8) for p in pages]).astype(np.int64)
hist = np.bincount(allb, minlength=256)
print('byte histogram top20:', sorted(enumerate(hist), key=lambda t: -t[1])[:20])
print('bytes >0x40 fraction:', float(np.mean(allb > 0x40)), '| ==0:', float(np.mean(allb == 0)))
# GE opcode check: LE u32 stream over the whole page region (from first page start)
region = slot9[pairs[0][1]:]
w = np.frombuffer(region[:len(region) // 4 * 4], dtype='<u4')
op = (w >> 24).astype(np.int64)
oph = np.bincount(op, minlength=256)
print('LE u32 top-byte (GE opcode) top15:', sorted(enumerate(oph), key=lambda t: -t[1])[:15])
print('words with top byte 0x04 (PRIM):', int(oph[4]), '0x0B (END):', int(oph[11]),
      '0x2B (BONE):', int(oph[43]), '0x12 (VTYPE):', int(oph[18]))
# u16 views
for dt, name in (('>u2', 'BE u16'), ('<u2', 'LE u16')):
    v = np.frombuffer(pages[5], dtype=dt).astype(np.int64)
    print(f'page5 {name}: max={v.max()} mean={v.mean():.1f} zeros={np.mean(v == 0):.2f}')

fig, axes = plt.subplots(2, 4, figsize=(14, 7))
for ax, (wdt, hgt) in zip(axes.flat, [(48, 46), (69, 32), (92, 24), (184, 12)] * 2):
    pass
for row, pno in enumerate((5, 0)):
    pg = np.frombuffer(pages[pno], dtype=np.uint8).astype(np.float64)
    for col, (wdt, hgt) in enumerate([(48, 46), (69, 32), (92, 24), (184, 12)]):
        ax = axes[row][col]
        ax.imshow(pg.reshape(hgt, wdt), cmap='gray', interpolation='nearest', aspect='auto')
        ax.set_title(f'page{pno} as {wdt}x{hgt}', fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
out = '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round11-evidence/r11_b5_page_images.png'
plt.tight_layout(); plt.savefig(out, dpi=100)
print('saved', out)
