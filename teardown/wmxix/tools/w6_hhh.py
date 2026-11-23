#!/usr/bin/env python3
"""W6: Triple H (slot 000) attire RE-TRIANGULATION.

The old faced assembly (TRIPLE_XXX_wmxix.obj, 606v/580f) is broken: 227
faces have max edge >= 0.2 m and only 192/580 face triples match the raw
strip mesh's 383 faces — it triangulated the assembled vertex list as one
continuous strip, creating faces that cross batch boundaries.

Fix (per the conversion note): re-triangulate PER BATCH in assembled
space; faces never cross a batch boundary.

Findings (measured 2026-11-19 against the verified solution points OBJ):
- Vertex positions: translation-only assembly (verts /2500, bone world
  positions from the FULL euler-matrix chain + perm (1,0,2) + /100,
  root-relative) reproduces the solution's 606 verts to 0.0001 m for
  11/13 batches. (The solution doc's "translation-only" refers to the
  VERTS; bone positions need the full chain — a translation-only chain
  puts the calf/foot upside down.)
- CORRECTION to the solution doc §5 map: batches 1 (arm) and 2 (hand)
  do NOT go to the LEFT arm bones (40/43). The solution placed them on
  the RIGHT side (implied Z +0.239 / +0.801; nearest bones R UpperArm 19
  / R Hand 22, +0.06 m in Z from the JSON chain — the v2 assembler's
  skeleton computation is not in the repo). This driver uses the
  positions recovered from the verified solution points OBJ.
- Faces: the raw strip mesh's 383 faces (000_0_raw_strip.obj) are the
  verified coherent per-batch triangulation (0 cross-batch faces). Its
  split rule is NOT distance-based (it splits at steps as small as 6 raw
  units — likely degenerate-triangle removal). A 1300-raw-unit distance
  rule gives 536 faces in the stable 1200-1500 plateau but ADDS 285
  unverified faces vs the raw mesh, so the raw faces are used directly.
- Verts are NOT permuted (perm=False reproduces the solution exactly;
  perm=True gives 0.31 m median error).

Writes triple-h-000_0.obj / triple-h-000_1.obj (606v/383f each), 2D
projection renders, and hhh-manifest.json to /data/wmxix/out/triple-h/.
"""
import sys, os, json, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
import extract_wrestlers as ew

SKEL = '/data/wmxix/tools-src/docs/wrestler-skeleton-000.json'
WRESTLER = '/data/wmxix/extracted/model/wrestler'
OUT = '/data/wmxix/out/triple-h'
RAW_STRIP = '/data/wmxix/tools-src/000_0_raw_strip.obj'
SOL_POINTS = '/data/wmxix/tools-src/TRIPLE_XXX_wmxix_points.obj'
BATCH_BONE = {0: 3, 1: 40, 2: 43, 3: 1, 4: 65, 5: 67, 6: 68,
              7: 5, 8: 5, 9: 5, 10: 5, 11: 5, 12: 5}
# Recovered from the verified solution points OBJ (see docstring):
# batch -> bone position in ROOT-RELATIVE coords (solution coords minus
# the Bip root offset [-1.027, 0, 0]).
BATCH_POS_OVERRIDE = {1: [0.0, 0.558, 0.239],
                      2: [0.0, 0.558, 0.801]}
VSCALE = 2500.0
BSCALE = 100.0


def load_bone_world():
    import numpy as np
    sk = json.load(open(SKEL))
    by = {b['index']: b for b in sk}

    def Rx(a):
        c, s = np.cos(a), np.sin(a)
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

    def Ry(a):
        c, s = np.cos(a), np.sin(a)
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

    def Rz(a):
        c, s = np.cos(a), np.sin(a)
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    world = {}
    for b in sk:
        i, p = b['index'], b['parent']
        R = Rx(b['euler_xyz'][0]) @ Ry(b['euler_xyz'][1]) @ Rz(b['euler_xyz'][2])
        M = np.eye(4)
        M[:3, :3] = R
        M[:3, 3] = b['pos']
        world[i] = M if p == -1 else world[p] @ M
    root = world[0][:3, 3] / BSCALE
    out = {}
    for i, M in world.items():
        w = M[:3, 3] / BSCALE - root
        out[i] = [float(w[1]), float(w[0]), float(w[2])]  # perm (1,0,2)
    return sk, by, out


def load_raw_faces():
    T = []
    for line in open(RAW_STRIP):
        if line.startswith('f '):
            T.append(tuple(int(x.split('/')[0]) - 1
                           for x in line.split()[1:4]))
    return T


def assemble(fname):
    data = open(os.path.join(WRESTLER, fname), 'rb').read()
    bs = ew.extract_batches(data)
    assert bs is not None, f'no batches in {fname}'
    batches, stats = bs
    sk, by, world = load_bone_world()
    V, parts = [], []
    voff = 0
    for bi, verts in enumerate(batches):
        if bi in BATCH_POS_OVERRIDE:
            bp = BATCH_POS_OVERRIDE[bi]
            bone = BATCH_BONE[bi]
            note = 'recovered-right-side'
        else:
            bone = BATCH_BONE[bi]
            bp = world[bone]
            note = ''
        for (x, y, z) in verts:
            V.append((x / VSCALE + bp[0], y / VSCALE + bp[1],
                      z / VSCALE + bp[2]))
        parts.append({'batch': bi, 'bone': bone,
                      'bone_name': by[bone]['name'],
                      'bone_pos': [round(v, 3) for v in bp],
                      'note': note, 'nverts': len(verts)})
        voff += len(verts)
    return V, parts, batches


def edge_stats(V, T):
    worst = 0.0
    bad = 0
    for a, b, c in T:
        for p, q in ((a, b), (b, c), (c, a)):
            d = math.sqrt(sum((x - y) ** 2 for x, y in zip(V[p], V[q])))
            worst = max(worst, d)
            if d >= 0.2:
                bad += 1
                break
    return worst, bad


def write_obj(path, V, T, parts):
    with open(path, 'w') as f:
        f.write('# Triple H slot 000 re-triangulated (W6)\n')
        f.write('# per-batch faces from the verified raw strip mesh; '
                'no face crosses a batch boundary\n')
        for x, y, z in V:
            f.write(f'v {x:.4f} {y:.4f} {z:.4f}\n')
        voff = 0
        for p in parts:
            f.write(f'# batch {p["batch"]} -> {p["bone_name"]} '
                    f'({p["nverts"]} verts)\n')
            voff += p['nverts']
        for a, b, c in T:
            f.write(f'f {a + 1} {b + 1} {c + 1}\n')


def render(path, V, T, parts, title):
    """2D projection renders (front X-Y, side Z-Y, top X-Z), like the
    solution's proof render — Y is the up axis."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    import numpy as np
    Va = np.array(V)
    Ta = np.array(T)
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    colors = plt.cm.tab20(np.linspace(0, 1, max(13, len(parts))))
    # per-batch face ranges (faces are ordered by batch in the raw mesh)
    voff = 0
    ranges = []
    for p in parts:
        lo, hi = voff, voff + p['nverts']
        idx = [k for k, t in enumerate(T)
               if lo <= t[0] < hi]
        ranges.append((idx, p))
        voff += p['nverts']
    for ax, (a1, a2, t, lims) in zip(axes, [
            (0, 1, 'front (X-Y)', (-0.2, 1.0, -1.1, 1.5)),
            (2, 1, 'side (Z-Y)', (-0.2, 1.5, -1.1, 1.5)),
            (0, 2, 'top (X-Z)', (-0.2, 1.0, -0.2, 1.5))]):
        for k, (idx, p) in enumerate(ranges):
            if idx:
                polys = Va[Ta[idx]][:, :, [a1, a2]]
                pc = PolyCollection(polys, alpha=0.85,
                                    facecolor=colors[k % 20],
                                    edgecolor='none')
                ax.add_collection(pc)
        ax.set_xlim(lims[0], lims[1])
        ax.set_ylim(lims[2], lims[3])
        ax.set_aspect('equal')
        ax.set_title(t)
        ax.grid(True, alpha=0.3)
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(path, dpi=90)
    print('render ->', path)


def main():
    os.makedirs(OUT, exist_ok=True)
    T = load_raw_faces()
    print(f'raw strip faces: {len(T)}')
    # verify 0 cross-batch faces using the 000_0 batch layout
    V0, parts0, batches0 = assemble('000_0.ymg')
    offs = [0]
    for b in batches0:
        offs.append(offs[-1] + len(b))
    cross = 0
    for t in T:
        owners = set()
        for v in t:
            for bi in range(13):
                if offs[bi] <= v < offs[bi + 1]:
                    owners.add(bi)
        if len(owners) > 1:
            cross += 1
    print(f'cross-batch faces in raw set: {cross}')
    # verify positions vs the solution points OBJ
    sol = []
    for line in open(SOL_POINTS):
        if line.startswith('v '):
            sol.append(tuple(map(float, line.split()[1:4])))
    errs = [math.sqrt((sol[i][0] - (V0[i][0] - 1.027)) ** 2 +
                      (sol[i][1] - V0[i][1]) ** 2 +
                      (sol[i][2] - V0[i][2]) ** 2) for i in range(606)]
    errs.sort()
    print(f'position error vs solution points: median={errs[303]:.4f} '
          f'max={errs[-1]:.4f} m')
    manifest = {'raw_faces': len(T), 'cross_batch_faces': cross,
                'pos_err_median_m': round(errs[303], 4),
                'pos_err_max_m': round(errs[-1], 4)}
    V1, parts1, batches1 = assemble('000_1.ymg')
    same_verts = all(a == b for a, b in zip(V0, V1))
    print(f'000_1 verts identical to 000_0: {same_verts}')
    manifest['alt_attire_identical_geometry'] = same_verts
    for fname, V, parts in (('000_0.ymg', V0, parts0),
                            ('000_1.ymg', V1, parts1)):
        xs = [v[0] for v in V]
        ys = [v[1] for v in V]
        zs = [v[2] for v in V]
        bbox = [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2),
                round(max(zs) - min(zs), 2)]
        worst, bad = edge_stats(V, T)
        out = os.path.join(OUT, f'triple-h-{fname[:-4]}.obj')
        write_obj(out, V, T, parts)
        rp = os.path.join(OUT, f'triple-h-{fname[:-4]}.png')
        render(rp, V, T, parts, f'Triple H {fname} re-triangulated (W6)')
        print(f'{fname}: {len(V)} verts {len(T)} tris bbox={bbox} '
              f'(solution [0.77, 2.22, 1.27]) max_edge={worst:.3f}m '
              f'bad_faces(>=0.2m)={bad} -> {out}')
        manifest[fname] = {'verts': len(V), 'tris': len(T),
                           'bbox_m': bbox, 'max_edge_m': round(worst, 3),
                           'bad_faces_ge_0.2m': bad, 'parts': parts}
    with open(os.path.join(OUT, 'hhh-manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
