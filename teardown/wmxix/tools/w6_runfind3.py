#!/usr/bin/env python3
"""W6: test the v3 formula — vertex run = [skin_off+24, skel_off-4)."""
import sys, struct, math, random
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_extract as w

def s16(b, i): return struct.unpack('>h', b[i:i + 2])[0]
def u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]

def main():
    iso = w.ISOFile()
    ymgs = sorted(p for p in iso.files
                  if p.startswith('edit_data/MODEL/') and p.endswith('.ymg'))
    v3 = []
    for p in ymgs:
        d = iso.read(p)
        if d[:4] == b'YOBJ' and struct.unpack('>I', d[8:12])[0] == 0x30001:
            v3.append(p)
    print(f'v3.0001 files: {len(v3)}')
    random.seed(3)
    sample = ['edit_data/MODEL/Man/Elbow/me0_000/l0.ymg'] + \
             random.sample(v3, 19)
    ok = 0
    for p in sample:
        d = iso.read(p)
        skin = u32(d, 0x60); skel = u32(d, 0x14)
        start = skin + 24
        span = skel - 4 - start
        n = span // 6
        rem = span % 6
        tris = [(s16(d, start + i * 6), s16(d, start + i * 6 + 2),
                 s16(d, start + i * 6 + 4)) for i in range(n)]
        steps = [dist(tris[i], tris[i + 1]) for i in range(len(tris) - 1)]
        med = median(steps) if steps else 9999
        maxc = max(max(abs(x) for x in t) for t in tris) if tris else 0
        xs = [t[0] for t in tris]; ys = [t[1] for t in tris]; zs = [t[2] for t in tris]
        bb = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) if tris else (0, 0, 0)
        good = med < 400 and maxc < 8192 and rem == 0
        ok += 1 if good else 0
        short = '/'.join(p.split('/')[-2:])
        print(f'{short}: n={n} rem={rem} med_step={med:.0f} maxcoord={maxc} '
              f'bbox={tuple(round(x) for x in bb)} {"OK" if good else "??"}')
    print(f'{ok}/{len(sample)} fit the formula cleanly')
    iso.close()

if __name__ == '__main__':
    main()
