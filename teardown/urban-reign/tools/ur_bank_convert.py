#!/usr/bin/env python3
"""Convert a general .gyu bank to packed wh-anim-style clip JSONs.

Output layout (mirrors PR #425's wh-anim/1 + rows.pack.json conventions):
  <outdir>/skeleton.json  - nodes (GLB node names in motion-bone order),
                            fps, mapping provenance
  <outdir>/clips.json     - per-motion metadata (frames, duration)
  <outdir>/rows.pack.json - base64 i16 quaternion rows: for each motion,
                            per keyframe (union key grid), per bone xyzw
                            i16 = round(q * 32767); root translations in
                            a parallel float array (root_t per motion).
Local rotations are delta-composed absolute locals:
q_local(t) = q_bindlocal (x) q_euler(t), matching ur_embed.py.
This shared-bank conversion is data-exact; which fighter plays which
general motion is a movelist question (pmotID/.info correlation), so
these banks ship as shared pools, NOT per-fighter assignments.
"""
import base64, json, struct, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/ur-phase2-work/tools')
from ur_gyu import Bank, load_tables
from ur_skin_bake import load_glb, eul2mat, MB2NODE
from ur_embed import mat2quat, qmul

def convert(gyu_path, glb_path, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    set1, set2 = load_tables('/home/hatch/workspace/ur-decode/work/SLUS_212.09')
    bank = Bank(gyu_path)
    g, skin, W, glb_parent, pos, jts, wts, idx = load_glb(glb_path)
    joints = skin['joints']
    Lbind = {}
    for ji in joints:
        par = glb_parent.get(ji)
        Lbind[ji] = W[ji].copy() if par is None else np.linalg.inv(W[par]) @ W[ji]
    qbind = {ji: mat2quat(Lbind[ji][:3, :3]) for ji in joints}
    node2mb = {v: k for k, v in MB2NODE.items()}
    bones = [g['nodes'][ji]['name'] for ji in range(21)]
    clips_meta = []
    pack = {}
    root_t = {}
    for mi in range(bank.n_motions):
        trs = bank.tracks(mi)
        dec = [t.decode(bank.d, set1, set2) for t in trs]
        nframes = max((t.nkeys - 1) * t.fpk for t in trs) + 1
        # union grid = every frame (60 Hz); per bone sample its own keys
        def sample(vals, fpk, frame):
            p = frame / fpk
            i = min(int(p), len(vals) - 1); fr = p - i
            j = min(i + 1, len(vals) - 1)
            a = np.array(vals[i]); b = np.array(vals[j])
            return a * (1 - fr) + b * fr
        rows = []
        rt = []
        root0 = np.array(dec[0][0])
        for f in range(nframes):
            row = []
            for ji in range(21):
                mb = node2mb[ji]
                e = sample(dec[mb], trs[mb].fpk, f)
                qe = mat2quat(eul2mat(e[0], e[1], e[2], 'RzRyRx'))
                q = qmul(qbind[ji], qe)
                row.extend([q[1], q[2], q[3], q[0]])
            rows.append(row)
            rp = sample(dec[0], trs[0].fpk, f)
            delta = (rp - root0) * 0.4034
            base_t = Lbind[12][:3, 3]
            rt.append([float(base_t[0] + delta[0]), float(base_t[1] + delta[2]),
                       float(base_t[2] - delta[1])])
        arr = np.array(rows, dtype=np.float64)
        i16 = np.round(np.clip(arr, -1, 1) * 32767).astype('<i2')
        pack[f'ur_m{mi:03d}'] = base64.b64encode(i16.tobytes()).decode()
        root_t[f'ur_m{mi:03d}'] = rt
        clips_meta.append({'name': f'ur_m{mi:03d}', 'motion': mi, 'frames': nframes,
                           'duration_s': round(nframes / 60, 3)})
    json.dump({'format': 'wh-anim-skel/1', 'fps': 60, 'bones': bones,
               'root_bone': bones[12],
               'mapping': 'motion bone b -> GLB node index b (H-index); local = bind (x) euler-delta (RzRyRx)',
               'source_bank': gyu_path}, open(f'{outdir}/skeleton.json', 'w'), indent=1)
    json.dump({'format': 'wh-anim/1', 'clips': clips_meta}, open(f'{outdir}/clips.json', 'w'), indent=1)
    json.dump({'format': 'wh-anim-pack/1', 'encoding': 'base64-i16 quat xyzw, scale 32767',
               'rows': pack, 'root_t': root_t}, open(f'{outdir}/rows.pack.json', 'w'))
    print(f'{outdir}: {len(clips_meta)} motions packed')

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2], sys.argv[3])
