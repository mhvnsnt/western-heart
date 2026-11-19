#!/usr/bin/env python3
"""W6 probe: per-batch position error of my assembly vs the solution points."""
import sys, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_hhh as h


def load_obj(p):
    V = []
    for line in open(p):
        if line.startswith('v '):
            V.append(tuple(map(float, line.split()[1:4])))
    return V


def main():
    sol = load_obj('/data/wmxix/tools-src/TRIPLE_XXX_wmxix_points.obj')
    V, T, parts = h.assemble('000_0.ymg', False)
    voff = 0
    for p in parts:
        n = p['nverts']
        errs = []
        for i in range(voff, voff + n):
            errs.append(math.sqrt(
                (sol[i][0] - (V[i][0] - 1.027)) ** 2 +
                (sol[i][1] - V[i][1]) ** 2 +
                (sol[i][2] - V[i][2]) ** 2))
        errs.sort()
        print('batch %2d -> bone %2d %-16s n=%3d median=%.4f max=%.4f'
              % (p['batch'], p['bone'], p['bone_name'], n,
                 errs[n // 2], errs[-1]))
        voff += n
    # which individual verts are worst?
    worst = []
    for i in range(606):
        e = math.sqrt((sol[i][0] - (V[i][0] - 1.027)) ** 2 +
                      (sol[i][1] - V[i][1]) ** 2 +
                      (sol[i][2] - V[i][2]) ** 2)
        worst.append((e, i))
    worst.sort(reverse=True)
    print('worst 10 verts (err, idx):',
          [(round(e, 2), i) for e, i in worst[:10]])


if __name__ == '__main__':
    main()
