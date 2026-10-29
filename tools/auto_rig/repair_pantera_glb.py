#!/usr/bin/env python3
"""Repair pantera.glb: broken Idle clip + L/R-swapped skin joints + torn seams.

Three defects were measured in the shipped game/assets/models/pantera.glb
(see tools/auto_rig/anim_check.py gate, PR #367):

1. SCENE PLACEMENT BAKED INTO IDLE — the Idle clip's Hips translation keys
   orbit a mean ~8.2 m from bind (an exporter's scene origin), so the root
   joint "wanders 8.21 m" and the gate fails. The bob itself is smooth,
   periodic and authored; only its center is wrong. Fix: re-center the
   keys on the bind position, preserving the authored offset curve
   (v' = bind + (v - mean)).

2. L/R-SWAPPED JOINTS_0 — 8 primitives (arms, boots 1-3, fingers, glove
   parts, pants, thighs) referenced mirrored joints, so under any
   non-bind pose the left-side geometry followed the right-side bones
   (the in-game "gyro arms" knot; PR #369 fixed the IK bug, this is the
   data bug underneath it). The repo already carries the audited fix in
   game/assets/models/pantera_fixed.glb (docs/qa/anim/
   pantera_skin_lr_fix_before_after.jpg) — it just was never the wired
   model. assets.js loads pantera.glb. Fix: transplant the 8 JOINTS_0
   accessors from pantera_fixed.glb (the files are otherwise identical:
   same positions, weights, IBMs, nodes, animations).

3. HARD SKIN SEAMS TEARING — with joints corrected, 83 triangle edges
   still stretched > 2.5x in the Idle stance: pants/thigh verts bound
   100% to LeftUpLeg sit directly against verts bound 100% to
   RightUpLeg (crotch seam), the chest logo is split 100% Spine vs
   100% Spine2, a few arm verts likewise. Fix: iteratively average the
   weight vectors across every edge whose posed/rest ratio exceeds 2.0
   (identical weights move together, so the seam behaves like fabric),
   capped at 4 influences, renormalized, until the gate passes.

Result on the shipped file (2026-10-20): Idle root dev 8.21 m -> 0.63 m;
edge p99.9 11.27 -> 1.88 (gate 2.5); all four clips pass anim_check.
Only 14 accessors change; JSON structure is untouched.

Run/Walk in this file are 2-keyframe rest-pose stubs (values == bind).
They are intentionally NOT replaced here: real locomotion comes from
the decoded Tekken 3 banks at runtime (game/js/t3anims.js, wh-anim/1
via lab/tools/t3_motion_bake.py). Baking those into the GLB is a
separate, larger change.

Usage (run from tools/auto_rig, where anim_check.py/validate.py live):
    python3 repair_pantera_glb.py --in ../../game/assets/models/pantera.glb \
        --fixed ../../game/assets/models/pantera_fixed.glb
Then verify:
    python3 anim_check.py --in ../../game/assets/models/pantera.glb
"""
import argparse
import struct
import sys

import numpy as np

sys.path.insert(0, '.')
import anim_check as ac  # noqa: E402
from validate import read_glb  # noqa: E402

COMP = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}


def bin_offset(raw):
    return 20 + struct.unpack_from('<I', raw, 12)[0] + 8


# ---- step 1: re-center Idle Hips translations on bind -----------------
def recenter_root(path):
    js, _ = read_glb(path)
    raw = bytearray(open(path, 'rb').read())
    boff = bin_offset(raw)
    anim = next(a for a in js['animations'] if a.get('name') == 'Idle')
    chan = next(c for c in anim['channels']
                if c['target']['path'] == 'translation'
                and js['nodes'][c['target']['node']].get('name') == 'Hips')
    s = anim['samplers'][chan['sampler']]
    out_i = s['output']
    acc = js['accessors'][out_i]
    assert acc['componentType'] == 5126 and acc['type'] == 'VEC3'
    bv = js['bufferViews'][acc['bufferView']]
    off = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    vals = np.frombuffer(bytes(raw[off:off + acc['count'] * 12]),
                         dtype='<f4').reshape(-1, 3).astype(np.float64)
    hips = next(n for n in js['nodes'] if n.get('name') == 'Hips')
    bind = np.array(hips['translation'], float)
    mean = vals.mean(axis=0)
    new = bind + (vals - mean)
    packed = new.astype('<f4').tobytes()
    assert len(packed) == acc['count'] * 12
    raw[off:off + len(packed)] = packed
    open(path, 'wb').write(raw)
    dev = np.abs(vals - bind).max()
    print(f"[1] Idle Hips re-centered: mean {np.round(mean, 3)} -> bind "
          f"{np.round(bind, 3)}; max dev {dev:.2f} m -> "
          f"{np.abs(new - bind).max():.2f} m")


# ---- step 2: transplant corrected JOINTS_0 from pantera_fixed.glb -----
def transplant_joints(path, fixed_path):
    raw = bytearray(open(path, 'rb').read())
    src_raw = open(fixed_path, 'rb').read()
    jd, _ = read_glb(path)
    jf, _ = read_glb(fixed_path)
    assert jd['bufferViews'] == jf['bufferViews'], 'bufferView layout differs'
    boff, soff = bin_offset(raw), bin_offset(src_raw)
    changed = 0
    for mi, m in enumerate(jd['meshes']):
        for p in m['primitives']:
            ai = p.get('attributes', {}).get('JOINTS_0')
            if ai is None:
                continue
            ad, af = jd['accessors'][ai], jf['accessors'][ai]
            assert (ad['count'], ad['type'], ad['componentType']) == \
                   (af['count'], af['type'], af['componentType'])
            size = COMP[ad['componentType']][1]
            nbytes = ad['count'] * 4 * size
            o = boff + jd['bufferViews'][ad['bufferView']].get('byteOffset', 0) \
                + ad.get('byteOffset', 0)
            so = soff + jf['bufferViews'][af['bufferView']].get('byteOffset', 0) \
                + af.get('byteOffset', 0)
            if bytes(raw[o:o + nbytes]) != src_raw[so:so + nbytes]:
                raw[o:o + nbytes] = src_raw[so:so + nbytes]
                changed += 1
    open(path, 'wb').write(raw)
    print(f"[2] JOINTS_0 transplanted from pantera_fixed.glb: "
          f"{changed} accessors")


# ---- step 3: blend weights across torn seams ---------------------------
def evaluate_idle(path):
    model = ac.AnimModel(path)
    js = model.js
    anim = next(a for a in js['animations'] if a.get('name') == 'Idle')
    times, chans = model.animation_frames(anim, 120)
    bind = model.bind_world()
    jidx = np.array(model.joint_nodes)
    bind_skin = np.stack([bind[int(j)] @ model.ibm[k]
                          for k, j in enumerate(jidx)])
    frame_skin = []
    for t in times:
        w = model.eval_world(chans, t)
        frame_skin.append(np.stack([w[int(j)] @ model.ibm[k]
                                    for k, j in enumerate(jidx)]))
    bad, allr = {}, []
    for mi, prim in enumerate(model.prims):
        pos_h = np.concatenate(
            [prim['pos'], np.ones((len(prim['pos']), 1))], 1)
        tris = prim['idx'].reshape(-1, 3)
        e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]],
                            tris[:, [2, 0]]])
        e = np.sort(e, 1)
        edges = np.unique(e, axis=0)
        srest = ac._skin(model, bind_skin, prim, pos_h)
        rest_e = np.linalg.norm(srest[edges[:, 0]] - srest[edges[:, 1]],
                                axis=1)
        keep = rest_e >= 0.0098
        edges, rest_e = edges[keep], rest_e[keep]
        maxr = np.zeros(len(edges))
        for fi in range(len(times)):
            cur = ac._skin(model, frame_skin[fi], prim, pos_h)
            el = np.linalg.norm(cur[edges[:, 0]] - cur[edges[:, 1]], axis=1)
            maxr = np.maximum(maxr, el / rest_e)
        allr.append(maxr)
        for ei in np.nonzero(maxr > 2.0)[0]:
            bad.setdefault(mi, []).append(
                (float(maxr[ei]), int(edges[ei][0]), int(edges[ei][1])))
    return model, bad, float(np.percentile(np.concatenate(allr), 99.9))


def write_vert_weights(path, model, prim_i, updates):
    js = model.js
    meta = []
    for mesh in js['meshes']:
        for p in mesh['primitives']:
            at = p.get('attributes', {})
            if 'JOINTS_0' in at and 'POSITION' in at:
                meta.append((at['JOINTS_0'], at['WEIGHTS_0']))
    raw = bytearray(open(path, 'rb').read())
    boff = bin_offset(raw)
    for acc_i, is_j in ((meta[prim_i][0], True), (meta[prim_i][1], False)):
        acc = js['accessors'][acc_i]
        bv = js['bufferViews'][acc['bufferView']]
        base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
        fmt, size = COMP[acc['componentType']]
        stride = bv.get('byteStride', 0) or 4 * size
        for v, (jj, ww) in updates.items():
            vals = jj if is_j else ww
            for k in range(4):
                struct.pack_into('<' + fmt, raw,
                                 base + v * stride + k * size,
                                 vals[k] if is_j else float(vals[k]))
    open(path, 'wb').write(raw)


def blend_seams(path, rounds=10):
    for rnd in range(rounds):
        model, bad, p999 = evaluate_idle(path)
        print(f"[3] round {rnd}: edge p99.9 = {p999:.2f} "
              f"(bad prims: {{ {', '.join(f'{k}: {len(v)}' for k, v in bad.items())} }})")
        if not bad:
            return
        for mi, ebs in bad.items():
            prim = model.prims[mi]
            J = prim['joints'].copy()
            W = prim['weights'].copy()
            updates = {}

            def vec(v):
                d = {}
                for k in range(4):
                    if W[v][k] > 0:
                        j = int(J[v][k])
                        d[j] = d.get(j, 0.0) + float(W[v][k])
                return d

            for _ratio, a, b in sorted(ebs, reverse=True):
                da, db = vec(a), vec(b)
                avg = {k: (da.get(k, 0.0) + db.get(k, 0.0)) / 2.0
                       for k in set(da) | set(db)}
                top = sorted(avg.items(), key=lambda kv: -kv[1])[:4]
                tot = sum(v for _, v in top)
                jj = [k for k, _ in top] + [0] * (4 - len(top))
                ww = [v / tot for _, v in top] + [0.0] * (4 - len(top))
                for v in (a, b):
                    J[v] = jj
                    W[v] = ww
                    updates[v] = (jj, ww)
            if updates:
                write_vert_weights(path, model, mi, updates)
    model, bad, p999 = evaluate_idle(path)
    print(f"[3] final: edge p99.9 = {p999:.2f}")
    if bad:
        raise SystemExit('seam blend did not converge')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--fixed', dest='fixed', required=True,
                    help='pantera_fixed.glb (source of corrected JOINTS_0)')
    args = ap.parse_args()
    recenter_root(args.inp)
    transplant_joints(args.inp, args.fixed)
    blend_seams(args.inp)
    print('repair complete')


if __name__ == '__main__':
    main()
