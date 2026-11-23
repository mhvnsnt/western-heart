#!/usr/bin/env python3
"""W6 probe: what strip-split rule does the raw 383-face mesh use?
Reconstruct the raw mesh's strips per batch from its face list, then
measure the step size at each strip boundary. Compare with the
1300-raw-unit rule (536 faces)."""
import sys, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import extract_wrestlers as ew
import w6_hhh as h


def load_obj(p):
    V, T = [], []
    for line in open(p):
        if line.startswith('v '):
            V.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith('f '):
            T.append(tuple(int(x.split('/')[0]) - 1
                           for x in line.split()[1:4]))
    return V, T


def main():
    rawV, rawT = load_obj('/data/wmxix/tools-src/000_0_raw_strip.obj')
    data = open('/data/wmxix/extracted/model/wrestler/000_0.ymg', 'rb').read()
    batches, _ = ew.extract_batches(data)
    offs = [0]
    for b in batches:
        offs.append(offs[-1] + len(b))
    print('raw faces per batch:')
    boundary_steps = []
    cross_batch = 0
    for bi, b in enumerate(batches):
        lo, hi = offs[bi], offs[bi + 1]
        faces = [t for t in rawT if lo <= t[0] < hi]
        # verify all faces in this batch are within-batch
        xb = [t for t in faces
              if not (lo <= t[1] < hi and lo <= t[2] < hi)]
        cross_batch += len(xb)
        # reconstruct strips: a strip's faces are consecutive triples
        # (i,i+1,i+2),(i+1,i,i+2)...; find the covered vertex sequence
        used = sorted(set(v - lo for t in faces for v in t))
        # boundary steps: consecutive verts in the batch NOT connected
        # by any face edge
        edges = set()
        for t in faces:
            for a, bb in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                edges.add((min(a, bb) - lo, max(a, bb) - lo))
        n = len(b)
        for i in range(n - 1):
            if (i, i + 1) not in edges:
                d = math.sqrt(sum((x - y) ** 2
                                  for x, y in zip(b[i], b[i + 1])))
                boundary_steps.append((round(d), bi, i))
        maxfaces = max(0, n - 2)
        print('  batch %2d: n=%3d raw_faces=%3d (max %3d) cross=%d'
              % (bi, n, len(faces), maxfaces, len(xb)))
    print('cross-batch faces in raw mesh:', cross_batch)
    boundary_steps.sort()
    print('boundary steps (raw mesh splits): n=%d' % len(boundary_steps))
    print('  smallest 15:', boundary_steps[:15])
    print('  largest 10:', boundary_steps[-10:])
    import collections
    histo = collections.Counter(min(s // 200 * 200, 3000)
                                for s, _, _ in boundary_steps)
    print('  histogram (200-unit bins):', dict(sorted(histo.items())))
    # repeated-vertex restarts? (step == 0 inside a batch)
    zeros = sum(1 for b in batches for a, c in zip(b[:-1], b[1:])
                if a == c)
    print('repeated-vertex steps (step 0) in batches:', zeros)


if __name__ == '__main__':
    main()
