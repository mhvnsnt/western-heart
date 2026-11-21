#!/usr/bin/env python3
"""W6: v2 CAW mesh decode probe — batch path (v4) + table-end run path (v3)."""
import sys, struct, math, random
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_extract as w
import extract_wrestlers as ew

def s16(b, i): return struct.unpack('>h', b[i:i + 2])[0]
def u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2]

def extend_run(d, start, end_limit, maxcoord=8192, win=9, med_max=500):
    """Extend an s16x3 run from start while the rolling median step stays
    small. Returns list of triples."""
    triples = []
    steps = []
    o = start
    prev = None
    while o + 6 <= end_limit:
        t = (s16(d, o), s16(d, o + 2), s16(d, o + 4))
        if max(abs(x) for x in t) > maxcoord:
            break
        if prev is not None:
            steps.append(dist(prev, t))
            if len(steps) >= win and median(steps[-win:]) > med_max:
                break
        triples.append(t)
        prev = t
        o += 6
    return triples

def table_end_run(d, skin_off, skel_off):
    """Find the vertex run starting just after the skin table: try starts
    skin_off..skin_off+64 (step 2), keep the longest run."""
    best = None
    for start in range(skin_off, min(skin_off + 64, skel_off - 6), 2):
        tris = extend_run(d, start, skel_off)
        if best is None or len(tris) > len(best[1]):
            best = (start, tris)
    return best

def bbox(tris):
    xs = [t[0] for t in tris]; ys = [t[1] for t in tris]; zs = [t[2] for t in tris]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))

def main():
    iso = w.ISOFile()
    # --- v4 batch path test ---
    print('=== v4 batch path ===')
    for p in ('edit_data/MODEL/Woman/Hair/mk0_024/c0.ymg',
              'edit_data/MODEL/Woman/Face/mq0_014/c4.ymg',
              'edit_data/MODEL/Man/Hair/mk0_043/c0.ymg'):
        d = iso.read(p)
        bs = ew.extract_batches(d)
        if bs is None:
            print(p, 'NO BATCH TABLE')
            continue
        batches, stats = bs
        tot = sum(len(b) for b in batches)
        allv = [v for b in batches for v in b]
        print(f'{p}: {len(batches)} batches, {tot} verts, '
              f'bbox(raw)={tuple(round(x) for x in bbox(allv))}, '
              f'med-dists={[round(s) for s in stats]}')
    # --- v3 table-end run path test ---
    print('=== v3 table-end run path ===')
    ymgs = sorted(p for p in iso.files
                  if p.startswith('edit_data/MODEL/') and p.endswith('.ymg'))
    v3 = [p for p in ymgs
          if iso.read(p)[:4] == b'YOBJ'
          and struct.unpack('>I', iso.read(p)[8:12])[0] == 0x30001]
    test = ['edit_data/MODEL/Man/Elbow/me0_000/l0.ymg'] + \
           random.Random(11).sample(v3, 7)
    for p in test:
        d = iso.read(p)
        skin = u32(d, 0x60); skel = u32(d, 0x14)
        start, tris = table_end_run(d, skin, skel)
        short = '/'.join(p.split('/')[-2:])
        print(f'{short}: skin={skin:#x} skel={skel:#x} run_start={start:#x} '
              f'(+{start - skin}) n={len(tris)} '
              f'bbox(raw)={tuple(round(x) for x in bbox(tris)) if tris else None}')
    iso.close()

if __name__ == '__main__':
    main()
