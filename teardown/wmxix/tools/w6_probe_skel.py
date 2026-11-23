#!/usr/bin/env python3
"""W6 probe: which bone-world-position computation matches the solution doc?
Solution doc Y values: head~1.0 torso~0.7 pelvis~0.38 thigh~0.27
calf~-0.13 foot~-0.63. Candidates: (a) translation-only chain (current,
WRONG: calf/foot upside down), (b) full euler-matrix chain, with and
without the (1,0,2) perm applied to the final world position."""
import json
import numpy as np

SKEL = '/data/wmxix/tools-src/docs/wrestler-skeleton-000.json'
EXPECT = {5: 1.0, 3: 0.7, 1: 0.38, 65: 0.27, 67: -0.13, 68: -0.63}


def Rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def main():
    sk = json.load(open(SKEL))
    by = {b['index']: b for b in sk}
    # full-matrix chain (a3 load_skeleton)
    world = {}
    for b in sk:
        i, p = b['index'], b['parent']
        R = Rx(b['euler_xyz'][0]) @ Ry(b['euler_xyz'][1]) @ Rz(b['euler_xyz'][2])
        M = np.eye(4)
        M[:3, :3] = R
        M[:3, 3] = b['pos']
        world[i] = M if p == -1 else world[p] @ M
    print('full-matrix chain, world pos /100, NO perm:')
    for i in (5, 3, 1, 65, 67, 68):
        w = world[i][:3, 3] / 100
        print(f'  {by[i]["name"]:16s} {np.round(w, 2)}  expect Y~{EXPECT[i]}')
    print('full-matrix chain, world pos /100, perm (1,0,2):')
    for i in (5, 3, 1, 65, 67, 68):
        w = world[i][:3, 3] / 100
        w = np.array([w[1], w[0], w[2]])
        print(f'  {by[i]["name"]:16s} {np.round(w, 2)}  expect Y~{EXPECT[i]}')
    print('full-matrix chain, world pos /100, perm (1,0,2) + sign flips:')
    for i in (5, 3, 1, 65, 67, 68):
        w = world[i][:3, 3] / 100
        w = np.array([w[1], w[0], w[2]])
        print(f'  {by[i]["name"]:16s} {np.round(w, 2)}')
    # also: what does the raw chain look like for the leg?
    print('leg chain local pos (file order):')
    for i in (1, 65, 67, 68):
        print(f'  {by[i]["name"]:16s} pos={np.round(by[i]["pos"], 1)} '
              f'euler={np.round(by[i]["euler_xyz"], 2)} parent={by[i]["parent"]}')


if __name__ == '__main__':
    main()
