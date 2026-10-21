#!/usr/bin/env python3
"""tools/auto_rig/backends/apply_skin.py — finish a k-NN weight transfer.

Consumes the .npz produced by knn_transfer.py and writes a complete,
skinned, animated GLB. Pure numpy GLB surgery (no Blender in this path):
Blender import/export can reorder a ~1M-vert mesh and silently scramble
the per-vertex weight correspondence; writing the GLB directly keeps
vertex order — and therefore the transfer — exact.

Pipeline (the PR #264 Tripo path, completed):
  1. Read the target static GLB (tightly packed accessors; if your
     source is interleaved, repack first) and the donor GLB.
  2. Rotate the target into the donor's facing (--rotate-y degrees,
     applied to POSITION/NORMAL). knn_transfer must have been run on
     the SAME rotation — this tool recomputes knn's normalize
     (uniform scale by Y-height ratio, min-corner translate) from the
     rotated target and the donor's full-mesh bbox and applies it, so
     the mesh lands in the donor's bind space where the donor's skin
     and inverse bind matrices are valid.
  3. Write JOINTS_0/WEIGHTS_0 from the .npz (ordinals into the donor
     skin's joint list).
  4. Tail: targets with a tail the donor lacks get a 4-bone chain
     (Tail1..Tail4) parented to Hips. The chain is fitted to the actual
     tail geometry by a medial walk over the tail verts (bind space),
     and tail verts are reweighted with smooth triangular kernels along
     the chain (Hips blend at the base). No authored tail animation
     exists anywhere in this repo, so the tail follows the body through
     skinning only — it is never hand-keyed (RULES_NO_GUESSING).
  5. Skeleton: the donor's node subtree (nodes 0..49 in pantera.glb:
     49 joints + the Character wrapper) is copied verbatim; the target
     mesh node and the tail nodes are appended. The donor skin is
     copied and extended with the tail joints + their IBMs.
  6. Animations: the donor's Idle clip is copied (real authored data),
     and wh-anim/1 JSON clips (--bake name=path, repeatable) are baked
     as direct rotation channels — quaternions verbatim from the JSON,
     in-place (no root translation), exactly as game/js/t3anims.js
     applies them at runtime. Bones missing from the donor skeleton
     (Root, Chest on the WH 49-bone rig) are skipped and reported.

Usage:
    python3 apply_skin.py --in TARGET.glb --donor DONOR.glb \
        --knn TARGET_knn.npz --out OUT.glb [--rotate-y -90] \
        [--bake T3Stance=game/assets/anim/t3/.../t3_stance.json] ...
"""
import argparse
import hashlib
import json
import struct
import sys

import numpy as np

COMP_SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
DTYPE = {5120: '<i1', 5121: '<u1', 5122: '<i2', 5123: '<u2',
         5125: '<u4', 5126: '<f4'}


def read_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'glTF', 'not a GLB'
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    boff = 20 + jlen
    bdat = b''
    if len(data) > boff + 8 and data[boff + 4:boff + 8] == b'BIN\x00':
        blen = struct.unpack('<I', data[boff:boff + 4])[0]
        bdat = data[boff + 8:boff + 8 + blen]
    return js, bdat


def acc_array(js, bdat, ai):
    """Stride-aware accessor read -> (count, ncomp) numpy array."""
    a = js['accessors'][ai]
    bv = js['bufferViews'][a['bufferView']]
    nc = NCOMP[a['type']]
    esz = COMP_SIZE[a['componentType']] * nc
    stride = bv.get('byteStride') or esz
    base = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    dt = DTYPE[a['componentType']]
    if stride == esz:
        return np.frombuffer(bdat, dtype=dt, count=a['count'] * nc,
                             offset=base).reshape(a['count'], nc).copy()
    out = np.empty((a['count'], nc), dtype=dt)
    raw = memoryview(bdat)
    for i in range(a['count']):
        s = base + i * stride
        out[i] = np.frombuffer(bytes(raw[s:s + esz]), dtype=dt)
    return out


def quat_matrix(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1]], dtype=np.float64)


def node_local(node):
    m = np.eye(4)
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=np.float64).reshape(4, 4).T
    if 'rotation' in node:
        m = quat_matrix(node['rotation'])
    if 'scale' in node:
        s = node['scale']
        m = m @ np.diag([s[0], s[1], s[2], 1.0])
    if 'translation' in node:
        m[:3, 3] = node['translation']
    return m


def node_worlds(js):
    """World matrix per node index, from the scene roots down."""
    parent = {}
    for i, n in enumerate(js['nodes']):
        for c in n.get('children', []):
            parent[c] = i
    worlds = {}

    def world(i):
        if i in worlds:
            return worlds[i]
        m = node_local(js['nodes'][i])
        if i in parent:
            m = world(parent[i]) @ m
        worlds[i] = m
        return m

    for i in range(len(js['nodes'])):
        world(i)
    return worlds


class GlbBuilder:
    """Accumulates a fresh BIN chunk + accessor/bufferView tables."""

    def __init__(self):
        self.bin = bytearray()
        self.bvs = []
        self.accs = []

    def add_bv(self, data):
        off = len(self.bin)
        self.bin.extend(data)
        while len(self.bin) % 4:
            self.bin.append(0)
        self.bvs.append({'buffer': 0, 'byteOffset': off,
                         'byteLength': len(data)})
        return len(self.bvs) - 1

    def add_acc(self, arr, ct, typ):
        arr = np.ascontiguousarray(arr, dtype=DTYPE[ct])
        bvi = self.add_bv(arr.tobytes())
        a = {'bufferView': bvi, 'componentType': ct, 'type': typ,
             'count': int(arr.shape[0])}
        if typ in ('VEC3', 'VEC2', 'SCALAR') and ct == 5126:
            flat = arr.reshape(arr.shape[0], -1)
            a['min'] = flat.min(0).tolist()
            a['max'] = flat.max(0).tolist()
        self.accs.append(a)
        return len(self.accs) - 1

    def write(self, path, js):
        js['accessors'] = self.accs
        js['bufferViews'] = self.bvs
        js['buffers'] = [{'byteLength': len(self.bin)}]
        jb = json.dumps(js, separators=(',', ':')).encode()
        jb += b' ' * ((-len(jb)) % 4)
        total = 12 + 8 + len(jb) + 8 + len(self.bin)
        with open(path, 'wb') as f:
            f.write(struct.pack('<III', 0x46546C67, 2, total))
            f.write(struct.pack('<I', len(jb)) + b'JSON' + jb)
            f.write(struct.pack('<I', len(self.bin)) + b'BIN\x00' + self.bin)


def rot_y(deg):
    t = np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


# ---------------- tail fitting ----------------

def fit_tail(pos, hips_pos):
    """Detect tail verts + fit a 4-joint chain by medial walk.

    Returns (tail_mask, chain_points[5,3], u_per_tail_vert, report str).
    Bind space, character facing +Z, tail behind Hips (-Z)."""
    hx, hy, hz = hips_pos
    seed = (pos[:, 2] < hz - 0.16) & (pos[:, 1] > hy - 0.30) & \
           (pos[:, 1] < hy + 0.16) & (np.abs(pos[:, 0] - hx) < 0.30)
    if seed.sum() < 200:
        raise SystemExit(f'tail seed too small: {seed.sum()} verts')
    pts = [np.array([hx, hy - 0.02, hz - 0.10])]  # p0: pelvis back surface
    claimed = np.zeros(len(pos), dtype=bool)
    cur = pts[0]
    for step in range(4):
        d = np.linalg.norm(pos - cur, axis=1)
        near = (d < 0.36) & seed if step == 0 else (d < 0.36)
        # walk only through tail-ish space: behind pelvis plane, below neck
        near &= (pos[:, 2] < hz + 0.02) & (pos[:, 1] < hy + 0.16) & \
                (pos[:, 1] > 0.15)
        fresh = near & ~claimed
        if fresh.sum() < 30:
            # widen once before giving up
            fresh = (d < 0.5) & ~claimed & (pos[:, 2] < hz + 0.02) & \
                    (pos[:, 1] < hy + 0.16) & (pos[:, 1] > 0.15)
        if fresh.sum() < 10:
            raise SystemExit(f'tail walk stalled at step {step}: '
                             f'{fresh.sum()} fresh verts')
        nxt = pos[fresh].mean(0)
        pts.append(nxt)
        claimed |= np.linalg.norm(pos - nxt, axis=1) < 0.20
        cur = nxt
    chain = np.array(pts)  # p0..p4 (p4 = tip end, beyond last joint)

    # assignment: verts within a tube around the polyline
    seg_a, seg_b = chain[:-1], chain[1:]
    seg_v = seg_b - seg_a
    seg_l = np.linalg.norm(seg_v, axis=1)
    rel = pos[:, None, :] - seg_a[None, :, :]
    t = np.einsum('nij,nij->ni', rel, seg_v[None]) / (seg_l ** 2)[None]
    t = np.clip(t, 0, 1)
    closest = seg_a[None] + t[:, :, None] * seg_v[None]
    dist = np.linalg.norm(pos[:, None, :] - closest, axis=1)
    segi = np.argmin(dist, axis=1)
    dmin = dist[np.arange(len(pos)), segi]
    u = segi + t[np.arange(len(pos)), segi]
    mask = (dmin < 0.13) & (pos[:, 2] < hz + 0.02) & \
           (pos[:, 1] < hy + 0.16) & (pos[:, 1] > 0.18)
    rep = (f'tail verts={int(mask.sum())} chain=' +
           ' -> '.join(f'({p[0]:+.2f},{p[1]:.2f},{p[2]:+.2f})' for p in chain))
    return mask, chain, u, rep


def tail_weights(u):
    """Triangular kernels along the chain. Centers: Hips -0.6,
    Tail1 0, Tail2 1, Tail3 2, Tail4 3. Returns (n,5) weights."""
    centers = np.array([-0.6, 0.0, 1.0, 2.0, 3.0])
    w = np.maximum(0.0, 1.0 - np.abs(u[:, None] - centers[None]))
    w /= w.sum(1, keepdims=True).clip(min=1e-12)
    return w


# ---------------- main assembly ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--donor', required=True)
    ap.add_argument('--knn', required=True, help='npz from knn_transfer.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--rotate-y', type=float, default=0.0,
                    help='degrees; must match the rotation knn_transfer saw')
    ap.add_argument('--bake', action='append', default=[],
                    help='Name=clip.json (wh-anim/1), repeatable')
    ap.add_argument('--rest-ref', default=None,
                    help='GLB of the rig the --bake clips were authored for; '
                         'per-bone rest-rotation correction q * conj(r_ref) * '
                         'r_donor is applied (wh-anim clips are rig-specific: '
                         'verbatim transplant is only valid when rest local '
                         'rotations match per bone)')
    ap.add_argument('--no-tail', action='store_true')
    args = ap.parse_args()

    tjs, tbdat = read_glb(args.inp)
    djs, dbdat = read_glb(args.donor)
    npz = np.load(args.knn, allow_pickle=False)
    kj, kw = npz['joints'], npz['weights']
    log = []

    prim0 = tjs['meshes'][0]['primitives'][0]
    pos = acc_array(tjs, tbdat, prim0['attributes']['POSITION']).astype(np.float64)
    n = len(pos)
    assert kj.shape[0] == n, f'knn verts {kj.shape[0]} != target verts {n}'

    # donor full-mesh positions (bbox + bind reference)
    dpos = np.concatenate([
        acc_array(djs, dbdat, p['attributes']['POSITION']).astype(np.float64)
        for m in djs['meshes'] for p in m['primitives']])

    # --- rotate target into donor facing, then knn's normalize ---
    R = rot_y(args.rotate_y)
    pos_r = pos @ R.T
    if 'NORMAL' in prim0['attributes']:
        nai = prim0['attributes']['NORMAL']
        nrm_raw = acc_array(tjs, tbdat, nai)
        nrm = nrm_raw.astype(np.float64)
        if tjs['accessors'][nai]['componentType'] == 5120:
            nrm = nrm / 127.0
        nrm_r = nrm @ R.T
        nrm_r /= np.linalg.norm(nrm_r, axis=1, keepdims=True).clip(min=1e-12)
    else:
        nrm_r = None

    tmin, tmax = pos_r.min(0), pos_r.max(0)
    dmin, dmax = dpos.min(0), dpos.max(0)
    s = (dmax[1] - dmin[1]) / (tmax[1] - tmin[1])
    pos_n = (pos_r - tmin) * s + dmin
    log.append(f'normalize scale={s:.4f} (recomputed, matches knn)')

    # --- donor skeleton facts ---
    dskin = djs['skins'][0]
    djoints = dskin['joints']                       # node indices, in order
    dnames = [djs['nodes'][j].get('name') for j in djoints]
    dworlds = node_worlds(djs)
    hips_node = djoints[dnames.index('Hips')]
    hips_world = dworlds[hips_node]
    hips_pos = hips_world[:3, 3]
    log.append(f'donor joints={len(djoints)} hips_world={np.round(hips_pos, 3)}')

    # --- tail fit + weight override ---
    out_j = kj.astype(np.int64).copy()
    out_w = kw.astype(np.float64).copy()
    tail_nodes_local = []
    tail_ibms = []
    n_tail_joints = 0
    if not args.no_tail:
        mask, chain, u, rep = fit_tail(pos_n, hips_pos)
        log.append(rep)
        tw = tail_weights(u[mask])
        # columns: Hips=ordinal 0, Tail1..4 = ordinals len(djoints)+0..3
        combos = np.zeros((int(mask.sum()), 5), dtype=np.int64)
        combos[:, 0] = 0
        for k in range(4):
            combos[:, k + 1] = len(djoints) + k
        top = np.argsort(-tw, axis=1)[:, :4]
        rows = np.arange(len(tw))
        newj = np.zeros((len(tw), 4), dtype=np.int64)
        neww = np.zeros((len(tw), 4), dtype=np.float64)
        for c in range(4):
            sel = top[:, c]
            newj[:, c] = combos[rows, sel]
            neww[:, c] = tw[rows, sel]
        neww /= neww.sum(1, keepdims=True).clip(min=1e-12)
        out_j[mask] = newj
        out_w[mask] = neww
        n_tail_joints = 4
        # tail joint world positions: Tail1..4 at chain p0..p3,
        # identity local rotations (world rotation = Hips world rotation)
        hips_rot = hips_world[:3, :3]
        hips_rot_inv = np.linalg.inv(hips_rot)
        q = chain[:4]
        prev_world = hips_world
        prev_q = hips_pos
        for k in range(4):
            local_t = hips_rot_inv @ (q[k] - prev_q) if k == 0 else \
                hips_rot_inv @ (q[k] - q[k - 1])
            tail_nodes_local.append(local_t)
            wmat = np.eye(4)
            wmat[:3, :3] = hips_rot
            wmat[:3, 3] = q[k]
            tail_ibms.append(np.linalg.inv(wmat))
            prev_world, prev_q = wmat, q[k]

    # --- build output GLB ---
    b = GlbBuilder()
    # target accessors, in original order (POSITION/NORMAL replaced)
    acc_map = {}
    img_bv_map = {}
    for ai, a in enumerate(tjs['accessors']):
        if ai == prim0['attributes']['POSITION']:
            acc_map[ai] = b.add_acc(pos_n.astype('<f4'), 5126, 'VEC3')
        elif nrm_r is not None and ai == prim0['attributes'].get('NORMAL'):
            ct = a['componentType']
            if ct == 5120:
                arr = np.round(np.clip(nrm_r, -1, 1) * 127).astype('<i1')
            else:
                arr = nrm_r.astype('<f4')
            acc_map[ai] = b.add_acc(arr, ct, 'VEC3')
            if ct in (5120, 5121, 5122, 5123):
                # integer normals are only valid glTF with normalized=true
                # (Blender's importer asserts on it); the repack preserved
                # the flag, so the rewrite must too.
                b.accs[acc_map[ai]]['normalized'] = True
        else:
            acc_map[ai] = b.add_acc(acc_array(tjs, tbdat, ai),
                                    a['componentType'], a['type'])
    # image bufferViews copied byte-identical
    images = []
    for im in tjs.get('images', []):
        nim = dict(im)
        if 'bufferView' in im:
            bv = tjs['bufferViews'][im['bufferView']]
            base = bv.get('byteOffset', 0)
            nim['bufferView'] = b.add_bv(bytes(tbdat[base:base + bv['byteLength']]))
        images.append(nim)
    # skin attribute accessors
    j_acc = b.add_acc(out_j.astype('<u2'), 5123, 'VEC4')
    w_acc = b.add_acc(out_w.astype('<f4'), 5126, 'VEC4')
    # IBMs: donor's + tail
    dibm = acc_array(djs, dbdat, dskin['inverseBindMatrices']).astype(np.float64)
    ibms = [dibm[i].reshape(4, 4).T for i in range(len(djoints))]
    ibms.extend(tail_ibms)
    ibm_arr = np.stack([m.T.reshape(-1) for m in ibms]).astype('<f4')
    ibm_acc = b.add_acc(ibm_arr, 5126, 'MAT4')

    # nodes: donor 0..49 verbatim (joints + Character), then mesh node,
    # then tail nodes appended (indices continue)
    nodes = [json.loads(json.dumps(nd)) for nd in djs['nodes'][:50]]
    mesh_node_i = len(nodes)
    nodes.append({'name': tjs['nodes'][0].get('name', 'mesh'),
                  'mesh': 0, 'skin': 0})
    tail_first = len(nodes)
    for k in range(n_tail_joints):
        nd = {'name': f'Tail{k + 1}',
              'translation': [float(v) for v in tail_nodes_local[k]]}
        if k < n_tail_joints - 1:
            nd['children'] = [tail_first + k + 1]
        nodes.append(nd)
    if n_tail_joints:
        nodes[hips_node].setdefault('children', []).append(tail_first)

    skin = {'name': dskin.get('name', 'skin'),
            'joints': list(djoints) + [tail_first + k for k in range(n_tail_joints)],
            'inverseBindMatrices': ibm_acc}
    if 'skeleton' in dskin:
        skin['skeleton'] = dskin['skeleton']

    # animations
    anims = []

    def add_clip(name, chan_specs):
        """chan_specs: (node, path, times, values) — builds samplers/channels."""
        samplers, channels = [], []
        for node_i, path, times, values in chan_specs:
            t_acc = b.add_acc(np.asarray(times, dtype='<f4'), 5126, 'SCALAR')
            if path == 'rotation':
                v_acc = b.add_acc(np.asarray(values, dtype='<f4'), 5126, 'VEC4')
            else:
                v_acc = b.add_acc(np.asarray(values, dtype='<f4'), 5126, 'VEC3')
            samplers.append({'input': t_acc, 'output': v_acc,
                             'interpolation': 'LINEAR'})
            channels.append({'sampler': len(samplers) - 1,
                             'target': {'node': node_i, 'path': path}})
        anims.append({'name': name, 'samplers': samplers, 'channels': channels})

    # donor Idle copied verbatim (sampler data re-homed into new accessors)
    for a in djs.get('animations', []):
        if a.get('name') != 'Idle':
            continue
        specs = []
        for ch in a['channels']:
            smp = a['samplers'][ch['sampler']]
            times = acc_array(djs, dbdat, smp['input']).reshape(-1)
            values = acc_array(djs, dbdat, smp['output'])
            specs.append((ch['target']['node'], ch['target']['path'],
                          times, values))
        add_clip('Idle', specs)
        log.append(f'copied donor Idle: {len(specs)} channels')

    # baked wh-anim/1 clips
    name2node = {dnames[i]: djoints[i] for i in range(len(dnames))}
    # Optional rest-pose retarget: wh-anim clips carry ABSOLUTE local
    # rotations authored against a specific rig's rest pose. If that rig's
    # rest local rotations differ from the donor's (measured 2026-10-21:
    # leoman T3 rig vs pantera.glb donor — Hips/UpLegs/LeftShoulder 180deg,
    # RightShoulder/Feet 90deg), verbatim baking folds the body. Correct
    # per bone: q_out(t) = q(t) * conj(r_ref) * r_donor (Hamilton, xyzw);
    # identity wherever the rests already match.
    rest_corr = {}
    if args.rest_ref:
        rjs, _rb = read_glb(args.rest_ref)
        ref_rest = {n['name']: np.array(n.get('rotation', [0, 0, 0, 1]),
                                        dtype=np.float64)
                    for n in rjs['nodes'] if 'name' in n}
        don_rest = {}
        for ni, dn in enumerate(djs['nodes']):
            if 'name' in dn:
                don_rest[dn['name']] = np.array(
                    dn.get('rotation', [0, 0, 0, 1]), dtype=np.float64)

        def qmul(a, b):
            ax, ay, az, aw = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
            bx, by, bz, bw = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
            return np.stack([aw * bx + ax * bw + ay * bz - az * by,
                             aw * by - ax * bz + ay * bw + az * bx,
                             aw * bz + ax * by - ay * bx + az * bw,
                             aw * bw - ax * bx - ay * by - az * bz], -1)
        for bone, rr in ref_rest.items():
            if bone in don_rest:
                c = qmul(np.array([rr[0], rr[1], rr[2], -rr[3]]), don_rest[bone])
                c = c / np.linalg.norm(c)
                rest_corr[bone] = (qmul, c)
        log.append(f'rest-ref correction armed for {len(rest_corr)} bones '
                   f'from {args.rest_ref}')
    for spec in args.bake:
        cname, cpath = spec.split('=', 1)
        data = json.load(open(cpath))
        fps = float(data.get('fps', 30.0))
        nfr = max(len(v) for v in data['rot_xyzw'].values())
        times = np.arange(nfr, dtype=np.float64) / fps
        specs, skipped = [], []
        for bone, quats in data['rot_xyzw'].items():
            if bone not in name2node:
                skipped.append(bone)
                continue
            q = np.asarray(quats, dtype=np.float64)
            if len(q) < nfr:
                q = np.concatenate([q, np.repeat(q[-1:], nfr - len(q), 0)])
            if bone in rest_corr:
                qmul, c = rest_corr[bone]
                q = qmul(q, np.broadcast_to(c, q.shape))
                q = q / np.linalg.norm(q, axis=1, keepdims=True)
            specs.append((name2node[bone], 'rotation', times, q))
        add_clip(cname, specs)
        log.append(f'baked {cname}: {len(specs)} rotation channels from '
                   f'{cpath} (skipped bones: {skipped})')

    # extensionsUsed/Required dropped: the output is plain glTF (full-
    # precision accessors, no meshopt/quantization) even if the source
    # still declared them.
    out_js = {k: v for k, v in tjs.items()
              if k not in ('accessors', 'bufferViews', 'buffers', 'images',
                           'nodes', 'scenes', 'skins', 'animations',
                           'extensionsUsed', 'extensionsRequired')}
    out_js['meshes'] = json.loads(json.dumps(tjs['meshes']))
    p0 = out_js['meshes'][0]['primitives'][0]
    p0['attributes'] = {k: acc_map[v] for k, v in p0['attributes'].items()}
    p0['attributes']['JOINTS_0'] = j_acc
    p0['attributes']['WEIGHTS_0'] = w_acc
    if 'indices' in p0:
        p0['indices'] = acc_map[p0['indices']]
    if images:
        out_js['images'] = images
    out_js['nodes'] = nodes
    out_js['scenes'] = [{'name': 'Scene', 'nodes': [49, mesh_node_i]}]
    out_js['skins'] = [skin]
    if anims:
        out_js['animations'] = anims
    out_js['asset'] = {'version': '2.0',
                       'generator': 'apply_skin.py (tools/auto_rig) — knn transfer + donor skin'}
    b.write(args.out, out_js)

    sha = hashlib.sha256(open(args.out, 'rb').read()).hexdigest()
    print('APPLY_SKIN_OK')
    for line in log:
        print(' ', line)
    print(f'  out={args.out} sha256={sha}')


if __name__ == '__main__':
    main()
