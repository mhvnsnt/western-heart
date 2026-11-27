#!/usr/bin/env python3
"""W6: strict s16x3 vertex-run finder for CAW .ymg files (VM probe)."""
import sys, struct, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_extract as w

def s16(b, i): return struct.unpack('>h', b[i:i + 2])[0]
def u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def find_runs(d, step_max=400, min_len=20, maxcoord=8192):
    """Find maximal spans of s16x3 triples (6-byte aligned from each start
    candidate) where consecutive steps are <= step_max. A run is a list of
    (start_offset, n_triples). Scans every 2-byte alignment start."""
    n = len(d)
    runs = []
    # candidate starts: every 2-byte offset from 0x80; extend while steps small
    for start in range(0x80, n - 6, 2):
        # quick reject: first triple must be bounded
        t0 = (s16(d, start), s16(d, start + 2), s16(d, start + 4))
        if max(abs(x) for x in t0) > maxcoord:
            continue
        # extend
        prev = t0
        k = 1
        o = start + 6
        while o + 6 <= n:
            t = (s16(d, o), s16(d, o + 2), s16(d, o + 4))
            if max(abs(x) for x in t) > maxcoord:
                break
            if dist(prev, t) > step_max:
                break
            prev = t
            k += 1
            o += 6
        if k >= min_len:
            runs.append((start, k))
    # merge overlapping runs: keep the longest run covering each region
    runs.sort(key=lambda r: -r[1])
    kept = []
    for s, k in runs:
        e = s + k * 6
        if any(s < ke and e > ks for ks, ke in [(a, a + b * 6) for a, b in kept]):
            continue
        kept.append((s, k))
    return sorted(kept)

def main():
    iso = w.ISOFile()
    d = iso.read('edit_data/MODEL/Man/Elbow/me0_000/l0.ymg')
    # step profile of the known run 0x4D8, 148 triples
    run = [(s16(d, 0x4D8 + i * 6), s16(d, 0x4D8 + i * 6 + 2),
            s16(d, 0x4D8 + i * 6 + 4)) for i in range(148)]
    steps = sorted(dist(run[i], run[i + 1]) for i in range(147))
    print('elbow run steps: min=%.0f med=%.0f p90=%.0f max=%.0f' %
          (steps[0], steps[73], steps[132], steps[-1]))
    print('steps > 400:', sum(1 for s in steps if s > 400),
          'steps > 1500:', sum(1 for s in steps if s > 1500))
    runs = find_runs(d)
    print('finder runs (start, n):', [(hex(s), k) for s, k in runs])
    iso.close()

if __name__ == '__main__':
    main()
