#!/usr/bin/env python3
"""Round 11 Job 5: idx24 slot-9 page record hypotheses.
Arithmetic first: 2208 = 12*184 = 24*92 = 32*69 = 48*46 = 16*138 = 8*276.
Page 0 has a 60B zero head per round 10 -> payload 2148B after head?
2148/12=179, /4=537. Test strides by rendering BE f32 streams as
point clouds (x,y,z) and scoring spatial coherence (sortedness /
neighbor smoothness), then view the leading hypothesis."""
import struct, os, math
import numpy as np

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

data = open(os.path.join(DEC, 'idx24_entry492.bin'), 'rb').read() if os.path.exists(os.path.join(DEC, 'idx24_entry492.bin')) else None
if data is None:
    import glob
    f = [x for x in glob.glob(os.path.join(DEC, 'idx24_*.bin'))][0]
    print('file:', f); data = open(f, 'rb').read()
off, sz = slots_of(data)[9]
slot9 = data[off:off + sz]
print('slot9 size', len(slot9))
# page table at +0x78: 40 x (size, offset) BE pairs
pairs = [struct.unpack_from('>II', slot9, 0x78 + 8 * i) for i in range(40)]
print('first pairs:', pairs[:3], 'sizes set:', {p[0] for p in pairs})
page0 = slot9[pairs[0][1]:pairs[0][1] + pairs[0][0]]
print('page0 len', len(page0), 'first 64B:', page0[:64].hex())
nz = next(i for i, b in enumerate(page0) if b != 0)
print('page0 first nonzero at', nz)

f_be = np.frombuffer(page0, dtype='>f4').astype(np.float64)
f_le = np.frombuffer(page0, dtype='<f4').astype(np.float64)
for name, f in (('BE', f_be), ('LE', f_le)):
    sane = np.mean((np.abs(f) < 1e6) & (f == f))
    print(f'{name}: float-sane fraction {sane:.3f}, range [{np.nanmin(f):.3g},{np.nanmax(f):.3g}]')

# integer views
u_be = np.frombuffer(page0, dtype='>u4')
print('BE u32 head:', [hex(x) for x in u_be[:16]])

# Hypothesis tests: treat stream (from first nonzero / from 0) as f3 positions
def coherence(pts):
    """mean distance to next point vs mean distance to a random point:
    ratio << 1 means a smooth stream (path/surface order)."""
    if len(pts) < 10: return float('nan')
    d_next = np.mean(np.linalg.norm(np.diff(pts, axis=0), axis=1))
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(pts), size=(200, 2))
    d_rand = np.mean(np.linalg.norm(pts[idx[:, 0]] - pts[idx[:, 1]], axis=1))
    return d_next / d_rand if d_rand else float('nan')

results = {}
for start in (0, 60, 64):
    body = f_be[start // 4:]
    for stride_f, label in ((3, 'f3 pos'), (6, 'f6 pos+nrm'), (8, 'f8 pos+nrm+uv'), (4, 'f4')):
        n = (len(body) // stride_f) * stride_f
        pts = body[:n].reshape(-1, stride_f)[:, :3]
        ok = np.all(np.abs(pts) < 1e5)
        results[(start, label)] = (len(pts), coherence(pts) if ok else None)
        print(f'start={start} {label}: verts={len(pts)} coherence={results[(start, label)][1]}')

np.save('/tmp/r11_page0_fbe.npy', f_be)
print('page0 stats: BE f32 count', len(f_be), 'zeros', int(np.sum(f_be == 0)))
# value distribution of BE floats
fin = f_be[np.isfinite(f_be)]
print('BE float percentiles:', {p: round(float(np.percentile(fin, p)), 3) for p in (1, 25, 50, 75, 99)})
