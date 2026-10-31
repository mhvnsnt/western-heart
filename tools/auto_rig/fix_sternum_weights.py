#!/usr/bin/env python3
"""tools/auto_rig/fix_sternum_weights.py — anatomical fix for a chest that caves in toward the spine.

Owner 2026-10-31 (Purple Rain): "his torso around his chest and spine area is getting like crushed in towards his
spine ... it's kind of like reaching up his neck towards his face and getting his ... right arm".
Measured on roster/purplerain/attires/attire1/model-rerig.glb (a GameRig rig):
  - the chest band between the shoulders carries 38% of its skin weight on the two clavicle bones
    (LeftShoulder / RightShoulder) and only 9% on the chest bone (Spine2);
  - 2,042 vertices below the neck joint carry Neck weight.
Any clavicle roll (the real T7 stances roll it up to 35 deg) or head tilt then drags the sternum inward and up.

Rules (every position comes from the model's own bind pose; nothing is hand-painted):
  1. STERNUM: on vertices between the Spine2 and Neck joint heights, clavicle weight moves to the same-side Breast
     bone (rigs that have one; else Spine2 — both ride rigidly with the chest) with a
     smoothstep falloff across the chest. All of it moves within --inner x the half shoulder span from the midline;
     none moves beyond --outer, so the shoulders still follow the clavicles.
  2. NECK BLEED: Neck weight on vertices below the neck joint moves the same way. The move fades in over the top
     --neck-band of the Spine2 -> Neck span; the neck itself keeps its weights.
  3. Each vertex keeps its 4 largest influences, renormalized. They are written back into the same accessors
     (shapes and every other byte unchanged).

usage: python3 tools/auto_rig/fix_sternum_weights.py --in PLAIN.glb --out FIXED.glb [--report R.json]
       Input must be plain glTF: decode meshopt first (gltfpack -noq -kn -km -ke).
       Re-encode afterwards with gltfpack -cc -kn -km -ke.
"""
import argparse
import json
import struct

import numpy as np

COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def read_glb(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'glTF', 'not a GLB'
    jl = struct.unpack_from('<I', b, 12)[0]
    js = json.loads(b[20:20 + jl])
    bl = struct.unpack_from('<I', b, 20 + jl)[0]
    return js, bytearray(b[20 + jl + 8:20 + jl + 8 + bl])


def write_glb(path, js, binarr):
    jb = json.dumps(js, separators=(',', ':')).encode()
    jb += b' ' * ((4 - len(jb) % 4) % 4)
    pad = (4 - len(binarr) % 4) % 4
    body = struct.pack('<I4s', len(jb), b'JSON') + jb + struct.pack('<I4s', len(binarr) + pad, b'BIN\x00') + bytes(binarr) + b'\x00' * pad
    open(path, 'wb').write(b'glTF' + struct.pack('<II', 2, 12 + len(body)) + body)


def view(js, binarr, idx):
    """Writable (count, ncomp) numpy view of an accessor inside the BIN bytearray (strided if interleaved)."""
    a = js['accessors'][idx]
    if 'sparse' in a or 'bufferView' not in a:
        raise SystemExit('accessor %d is sparse or has no bufferView: decode with gltfpack -noq first' % idx)
    bv = js['bufferViews'][a['bufferView']]
    if bv.get('extensions'):
        raise SystemExit('bufferView %d is compressed (%s): decode with gltfpack -noq first' % (a['bufferView'], list(bv['extensions'])))
    dt = np.dtype(COMP[a['componentType']]); nc = NCOMP[a['type']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride') or dt.itemsize * nc
    return np.ndarray(shape=(a['count'], nc), dtype=dt, buffer=binarr, offset=off, strides=(stride, dt.itemsize)), a


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def fix(inp, outp, inner=0.35, outer=0.75, neck_band=0.35):
    js, binarr = read_glb(inp)
    skin = js['skins'][0]
    names = [js['nodes'][j].get('name', '') for j in skin['joints']]
    need = ['Spine2', 'Neck', 'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm']
    missing = [n for n in need if n not in names]
    if missing: raise SystemExit('skeleton lacks %s' % missing)
    ibm, _ = view(js, binarr, skin['inverseBindMatrices'])
    ibm = np.array(ibm, dtype=np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
    jpos = {n: np.linalg.inv(m)[:3, 3] for n, m in zip(names, ibm)}
    S2, NK, LS, RS = (names.index(n) for n in ('Spine2', 'Neck', 'LeftShoulder', 'RightShoulder'))
    mid = (jpos['LeftArm'][0] + jpos['RightArm'][0]) / 2
    half = abs(jpos['LeftArm'][0] - jpos['RightArm'][0]) / 2
    yS2, yN = jpos['Spine2'][1], jpos['Neck'][1]
    rep = {'joints': {'Spine2_y': yS2, 'Neck_y': yN, 'mid_x': mid, 'half_span': half}, 'primitives': []}
    for mesh in js['meshes']:
        for prim in mesh['primitives']:
            at = prim['attributes']
            if 'JOINTS_0' not in at or 'WEIGHTS_0' not in at: continue
            P, _ = view(js, binarr, at['POSITION'])
            Jv, Ja = view(js, binarr, at['JOINTS_0'])
            Wv, Wa = view(js, binarr, at['WEIGHTS_0'])
            P = np.array(P, dtype=np.float64); J = np.array(Jv, dtype=np.int64)
            W = np.array(Wv, dtype=np.float64)
            if Wa.get('normalized'): W = W / np.iinfo(COMP[Wa['componentType']]).max
            y, dx = P[:, 1], np.abs(P[:, 0] - mid) / half
            t_st = (1.0 - smoothstep(inner, outer, dx)) * ((y > yS2) & (y < yN))
            t_nk = smoothstep(yN, yN - neck_band * (yN - yS2), y) * (y < yN)
            band = (y > yS2) & (y < yN) & (dx < outer)
            share = lambda Wm, Jm, js_: float(np.where(np.isin(Jm[band], js_), Wm[band], 0).sum() / max(Wm[band].sum(), 1e-9))
            before = {'clavicle_share_chest': share(W, J, [LS, RS]), 'spine2_share_chest': share(W, J, [S2]),
                      'neck_bleed_verts': int(((np.where(J == NK, W, 0).sum(1) > 0.2) & (y < yN - 0.02 * (yN - yS2))).sum())}
            moved = np.zeros(len(W))
            for k in range(J.shape[1]):
                for jidx, t in ((LS, t_st), (RS, t_st), (NK, t_nk)):
                    m = J[:, k] == jidx
                    amt = W[:, k] * t * m
                    W[:, k] -= amt
                    moved += amt
            changed = int((moved > 1e-4).sum())
            # Target bone: the same-side Breast bone where the rig has one (GameRig rigs; the territory the 2026-10-31
            # Purple Rain consolidation already uses: docs/handoffs/RIGFIX-PURPLERAIN-2026-10-31.md), else Spine2.
            # Both ride rigidly with the chest, so the deformation is the same; the Breast keeps that fix's layout.
            left_side = np.sign(jpos['LeftArm'][0] - mid)
            tgt = np.full(len(J), S2)
            if 'LeftBreast' in names and 'RightBreast' in names:
                tgt = np.where(np.sign(P[:, 0] - mid) == left_side, names.index('LeftBreast'), names.index('RightBreast'))
            rest = moved.copy()
            for k in range(J.shape[1]):              # vertices that already carry their target bone take it there
                m = (J[:, k] == tgt) & (rest > 0)
                W[m, k] += rest[m]
                rest[m] = 0.0
            # vertices without that slot: a 5th candidate, then keep the top 4
            J5 = np.concatenate([J, tgt[:, None]], 1)
            W5 = np.concatenate([W, rest[:, None]], 1)
            order = np.argsort(-W5, axis=1)[:, :J.shape[1]]
            rows = np.arange(len(J))[:, None]
            J = J5[rows, order]; W = W5[rows, order]
            s = W.sum(1, keepdims=True); W = np.where(s > 1e-9, W / np.maximum(s, 1e-9), W)
            after = {'clavicle_share_chest': share(W, J, [LS, RS]), 'spine2_share_chest': share(W, J, [S2]),
                     'neck_bleed_verts': int(((np.where(J == NK, W, 0).sum(1) > 0.2) & (y < yN - 0.02 * (yN - yS2))).sum())}
            # write back in the accessors' own formats
            if Wa.get('normalized'):
                mx = np.iinfo(COMP[Wa['componentType']]).max
                q = np.floor(W * mx + 0.5).astype(np.int64)
                q[np.arange(len(q)), np.argmax(q, 1)] += mx - q.sum(1)   # exact sums
                Wv[...] = np.clip(q, 0, mx).astype(COMP[Wa['componentType']])
            else:
                Wv[...] = W.astype(COMP[Wa['componentType']])
            Jv[...] = np.where(W > 0, J, 0).astype(COMP[Ja['componentType']])
            rep['primitives'].append({'verts': len(P), 'changed_verts': changed, 'before': before, 'after': after})
    write_glb(outp, js, binarr)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--inner', type=float, default=0.35)
    ap.add_argument('--outer', type=float, default=0.75)
    ap.add_argument('--neck-band', type=float, default=0.35)
    ap.add_argument('--report', default=None)
    a = ap.parse_args()
    rep = fix(a.inp, a.out, a.inner, a.outer, a.neck_band)
    txt = json.dumps(rep, indent=1, default=float)
    print(txt)
    if a.report: open(a.report, 'w').write(txt)


if __name__ == '__main__':
    main()
