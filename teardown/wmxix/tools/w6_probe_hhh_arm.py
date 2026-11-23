#!/usr/bin/env python3
"""W6 probe: which bone did the solution use for batches 1 (arm) and 2 (hand)?
The per-batch error is EXACTLY uniform, so the solution placed those
batches at a different bone position. Recover the implied bone position
from the solution points and find the nearest bone in the skeleton."""
import sys, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import extract_wrestlers as ew
import w6_hhh as h


def load_obj(p):
    V = []
    for line in open(p):
        if line.startswith('v '):
            V.append(tuple(map(float, line.split()[1:4])))
    return V


def main():
    sol = load_obj('/data/wmxix/tools-src/TRIPLE_XXX_wmxix_points.obj')
    data = open('/data/wmxix/extracted/model/wrestler/000_0.ymg', 'rb').read()
    batches, _ = ew.extract_batches(data)
    sk, by, world = h.load_bone_world()
    # batch vertex offsets in the 606-vert order
    offs = [0]
    for b in batches:
        offs.append(offs[-1] + len(b))
    for bi in (1, 2):
        # implied bone pos (solution coords) from vert 0 of the batch:
        # sol = vert/2500 + bone  =>  bone = sol - vert/2500
        v0 = batches[bi][0]
        s0 = sol[offs[bi]]
        implied = [s0[j] - v0[j] / 2500.0 for j in range(3)]
        # my world coords are root-relative; solution coords include the
        # -1.027 X root offset, so compare in solution coords:
        print(f'batch {bi}: implied bone pos (solution coords) = '
              f'{[round(x, 3) for x in implied]}')
        # nearest bones (solution coords = my world + [-1.027, 0, 0])
        dists = []
        for i, w in world.items():
            sw = [w[0] - 1.027, w[1], w[2]]
            d = math.sqrt(sum((sw[j] - implied[j]) ** 2 for j in range(3)))
            dists.append((d, i, by[i]['name'], [round(x, 2) for x in sw]))
        dists.sort()
        for d, i, name, sw in dists[:4]:
            print(f'   bone {i:2d} {name:18s} at {sw} dist={d:.4f}')
        print(f'   my mapped bone {h.BATCH_BONE[bi]}: '
              f'{[round(x, 2) for x in [world[h.BATCH_BONE[bi]][0] - 1.027, world[h.BATCH_BONE[bi]][1], world[h.BATCH_BONE[bi]][2]]]}')


if __name__ == '__main__':
    main()
