#!/usr/bin/env python3
"""MINI re-template: replace a drifted MINI-32/33 skeleton with the HOUSE-49
T7 King-family skeleton (donor: pantera.glb on main), fitted to the mesh.

Method (STACK-2026-10-21): inspect -> normalize to template -> re-skin -> validate.
- Frame: geometry/joints get ONE axis conversion at the root: RotY(180)
  (MINI faces +Z, HOUSE faces -Z) + translate so geometry min-y = 0.
- Skeleton: donor hierarchy + donor WORLD rest rotations verbatim (HOUSE
  conventions preserved by construction); joint positions fitted to the
  target mesh from its own bind world joint positions.
- Fingers: donor hand-frame offsets, proportionally scaled to target hand.
- Extras (breasts/belly/jaw) kept as extra joints past the 49, parented to
  their original (mapped) parent, local rotation identity.
- Weights: per-vertex remap of the model's OWN weights (no hand painting):
  core by name; eyebrows -> Head; root -> Hips; single finger chain split
  across the five HOUSE chains by bind-space nearest joint (KNN k=1).
- IBMs recomputed as exact inverses of the new bind world matrices.
Originals are never modified; output is a new file.
"""
import argparse, struct, json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/_mini-rt-scratch/tools')
from inspect2 import load, node_m, worlds, acc_data

def quat_to_R(q):
    x,y,z,w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=float)

def R_to_quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t+1.0)*2; w = 0.25*s
        x = (R[2,1]-R[1,2])/s; y = (R[0,2]-R[2,0])/s; z = (R[1,0]-R[0,1])/s
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        s = np.sqrt(1.0+R[0,0]-R[1,1]-R[2,2])*2
        w = (R[2,1]-R[1,2])/s; x = 0.25*s; y = (R[0,1]+R[1,0])/s; z = (R[0,2]+R[2,0])/s
    elif R[1,1] > R[2,2]:
        s = np.sqrt(1.0+R[1,1]-R[0,0]-R[2,2])*2
        w = (R[0,2]-R[2,0])/s; x = (R[0,1]+R[1,0])/s; y = 0.25*s; z = (R[1,2]+R[2,1])/s
    else:
        s = np.sqrt(1.0+R[2,2]-R[0,0]-R[1,1])*2
        w = (R[1,0]-R[0,1])/s; x = (R[0,2]+R[2,0])/s; y = (R[1,2]+R[2,1])/s; z = 0.25*s
    q = np.array([x,y,z,w]); return q/np.linalg.norm(q)

FINGERS = ['Thumb','Index','Middle','Ring','Pinky']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--donor', required=True)
    ap.add_argument('--target', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report', required=True)
    args = ap.parse_args()

    # ---------- donor (HOUSE-49) ----------
    dg, dblob = load(args.donor)
    dw = worlds(dg)
    dskin = dg['skins'][0]
    donor_names = [dg['nodes'][j].get('name') for j in dskin['joints']]
    donor_pos = {n: dw[j][:3,3].copy() for n,j in zip(donor_names, dskin['joints'])}
    donor_rot = {n: dw[j][:3,:3].copy() for n,j in zip(donor_names, dskin['joints'])}
    dparent_idx = {}
    for i,n in enumerate(dg['nodes']):
        for c in n.get('children',[]): dparent_idx[c] = i
    donor_parent = {n: (dg['nodes'][dparent_idx[j]].get('name') if j in dparent_idx else None)
                    for n,j in zip(donor_names, dskin['joints'])}
    donor_parent = {n: (p if p in donor_names else None) for n,p in donor_parent.items()}
    assert len(donor_names) == 49, len(donor_names)

    # ---------- target ----------
    tg, tblob = load(args.target)
    tblob = bytearray(tblob)
    tw = worlds(tg)
    tskin = tg['skins'][0]
    old_names = [tg['nodes'][j].get('name') for j in tskin['joints']]
    old_pos = {n: tw[j][:3,3].copy() for n,j in zip(old_names, tskin['joints'])}
    tparent_idx = {}
    for i,n in enumerate(tg['nodes']):
        for c in n.get('children',[]): tparent_idx[c] = i
    old_parent = {n: (tg['nodes'][tparent_idx[j]].get('name') if j in tparent_idx else None)
                  for n,j in zip(old_names, tskin['joints'])}

    # geometry bbox over all prims of all meshes
    min_y = np.inf
    prims = []
    for mi, mesh in enumerate(tg['meshes']):
        for prim in mesh['primitives']:
            pos = acc_data(tg, bytes(tblob), prim['attributes']['POSITION'])
            prims.append((mi, prim, pos))
            min_y = min(min_y, float(pos[:,1].min()))
    # frame transform F = Trans(0,-min_y,0) @ RotY(pi): (x,y,z)->(-x, y-min_y, -z)
    def F(p): 
        p = np.asarray(p, dtype=float).copy()
        return np.array([-p[0], p[1]-min_y, -p[2]])
    def Fv(arr):
        out = arr.copy(); out[:,0] = -arr[:,0]; out[:,1] = arr[:,1]-min_y; out[:,2] = -arr[:,2]; return out

    tp = {n: F(p) for n,p in old_pos.items()}  # transformed old joint positions

    # ---------- fitted HOUSE positions ----------
    fit = {}
    NAME_MAP = {  # old -> HOUSE for shared names (identity for most)
        'Spine':'Spine','Spine1':'Spine1','Spine2':'Spine2','Hips':'Hips',
        'Neck':'Neck','Head':'Head','LeftShoulder':'LeftShoulder','RightShoulder':'RightShoulder',
        'LeftArm':'LeftArm','RightArm':'RightArm','LeftForeArm':'LeftForeArm','RightForeArm':'RightForeArm',
        'LeftHand':'LeftHand','RightHand':'RightHand','LeftUpLeg':'LeftUpLeg','RightUpLeg':'RightUpLeg',
        'LeftLeg':'LeftLeg','RightLeg':'RightLeg','LeftFoot':'LeftFoot','RightFoot':'RightFoot',
        'LeftToeBase':'LeftToeBase','RightToeBase':'RightToeBase'}
    for oldn, hn in NAME_MAP.items():
        if oldn in tp: fit[hn] = tp[oldn]
    # Spine for Diablo (no 'Spine'): interpolate Hips->Spine2
    if 'Spine' not in fit:
        fit['Spine'] = fit['Hips'] + (fit['Spine2']-fit['Hips'])*(1/3)
        fit['Spine1'] = fit['Hips'] + (fit['Spine2']-fit['Hips'])*(2/3)
    # fingers via donor hand frame
    finger_report = {}
    for side in ['Left','Right']:
        hand, fore = f'{side}Hand', f'{side}ForeArm'
        # donor frame
        u_d = donor_pos[hand]-donor_pos[fore]; u_d /= np.linalg.norm(u_d)
        e3_d = np.cross(u_d, [0,1,0]); e3_d /= (np.linalg.norm(e3_d)+1e-12)
        e2_d = np.cross(e3_d, u_d)
        u_t = fit[hand]-fit[fore]; u_t /= np.linalg.norm(u_t)
        e3_t = np.cross(u_t, [0,1,0]); e3_t /= (np.linalg.norm(e3_t)+1e-12)
        e2_t = np.cross(e3_t, u_t)
        # scale from an old finger reference if present
        ref_old = tp.get(f'{side}HandFinger1')
        if ref_old is None: ref_old = tp.get(f'{side}HandIndex1')
        for f in FINGERS:
            for seg in [1,2,3]:
                jn = f'{side}Hand{f}{seg}'
                if jn not in donor_pos: continue
                off_d = donor_pos[jn]-donor_pos[hand]
                c = np.array([off_d@u_d, off_d@e2_d, off_d@e3_d])
                if ref_old is not None and f in ('Middle','Index') and seg == 1:
                    ref_d = donor_pos[f'{side}Hand{f}1']-donor_pos[hand]
                    s = np.linalg.norm(ref_old-fit[hand])/(np.linalg.norm(ref_d)+1e-12)
                elif ref_old is not None:
                    ref_d = donor_pos[f'{side}HandMiddle1']-donor_pos[hand]
                    s = np.linalg.norm(ref_old-fit[hand])/(np.linalg.norm(ref_d)+1e-12)
                else:
                    s = np.linalg.norm(fit[hand]-fit[fore])/(np.linalg.norm(donor_pos[hand]-donor_pos[fore])+1e-12)
                fit[jn] = fit[hand] + s*(c[0]*u_t + c[1]*e2_t + c[2]*e3_t)
        if f'{side}HandFinger1' in tp:
            finger_report[side] = {
                'old_finger1': tp[f'{side}HandFinger1'].round(4).tolist(),
                'fitted_middle1': fit[f'{side}HandMiddle1'].round(4).tolist(),
                'old_finger2': tp[f'{side}HandFinger2'].round(4).tolist(),
                'fitted_middle2': fit[f'{side}HandMiddle2'].round(4).tolist()}
    missing = [n for n in donor_names if n not in fit]
    assert not missing, f'unfitted: {missing}'

    # ---------- extras ----------
    EXTRA_MAP = {  # old name -> (new name, HOUSE parent)
        'LeftBreast': ('LeftBreast','Spine1'), 'RightBreast': ('RightBreast','Spine1'),
        'L breast': ('LeftBreast','Spine2'), 'R breast': ('RightBreast','Spine2'),
        'Belly': ('Belly', None), 'Jaw': ('Jaw','Head')}
    extras = []  # (newname, parent_house_or_oldmapped, pos)
    for oldn,(newn,par) in EXTRA_MAP.items():
        if oldn in tp:
            p = par
            if oldn == 'Belly':
                op = old_parent.get('Belly')
                p = NAME_MAP.get(op, 'Spine')
            extras.append((newn, p, tp[oldn]))
    extra_names = [e[0] for e in extras]

    # ---------- build new skeleton ----------
    new_names = donor_names + extra_names
    new_index = {n:i for i,n in enumerate(new_names)}
    W = {}
    for n in donor_names:
        M = np.eye(4); M[:3,:3] = donor_rot[n]; M[:3,3] = fit[n]; W[n] = M
    for newn, par, pos in extras:
        M = np.eye(4); M[:3,:3] = W[par][:3,:3]; M[:3,3] = pos; W[newn] = M
    parent_of = dict(donor_parent)
    for newn, par, pos in extras: parent_of[newn] = par

    nodes = []
    for n in new_names:
        par = parent_of[n]
        L = np.linalg.inv(W[par]) @ W[n] if par else W[n]
        node = {'name': n,
                'translation': [round(float(x),6) for x in L[:3,3]],
                'rotation': [round(float(x),6) for x in R_to_quat(L[:3,:3])]}
        nodes.append(node)
    for n in new_names:
        par = parent_of[n]
        if par: nodes[new_index[par]].setdefault('children', []).append(new_index[n])
    # wrapper mesh node (preserve original wrapper props)
    wrapper_src = None
    for nd in tg['nodes']:
        if nd.get('mesh') is not None: wrapper_src = nd; break
    wrapper = dict(wrapper_src)
    wrapper.pop('children', None); wrapper['children'] = [new_index['Hips']]
    wrapper['skin'] = 0
    wrapper_idx = len(nodes)
    nodes.append(wrapper)
    tg['nodes'] = nodes
    tg['scenes'] = [{'name': tg['scenes'][0].get('name','Scene'), 'nodes': [wrapper_idx]}]
    # IBMs appended to blob
    ibms = np.zeros((len(new_names),4,4), dtype=np.float32)
    for i,n in enumerate(new_names):
        ibms[i] = np.linalg.inv(W[n]).astype(np.float32)
    ibm_bytes = ibms.transpose(0,2,1).tobytes()  # column-major per matrix
    pad = (-len(tblob)) % 4
    tblob.extend(b'\x00'*pad)
    ibm_off = len(tblob)
    tblob.extend(ibm_bytes)
    tg['buffers'][0]['byteLength'] = len(tblob)
    bv_idx = len(tg['bufferViews'])
    tg['bufferViews'].append({'buffer':0,'byteOffset':ibm_off,'byteLength':len(ibm_bytes)})
    acc_idx = len(tg['accessors'])
    tg['accessors'].append({'bufferView':bv_idx,'byteOffset':0,'componentType':5126,'count':len(new_names),'type':'MAT4'})
    tg['skins'] = [{'joints':[new_index[n] for n in new_names],'inverseBindMatrices':acc_idx}]

    # ---------- geometry transform (in place) ----------
    for mi, prim, pos in prims:
        newpos = Fv(pos.astype(float)).astype(np.float32)
        ai = prim['attributes']['POSITION']
        a = tg['accessors'][ai]; bv = tg['bufferViews'][a['bufferView']]
        off = (bv.get('byteOffset',0))+(a.get('byteOffset',0))
        tblob[off:off+newpos.nbytes] = newpos.tobytes()
        a['min'] = [float(x) for x in newpos.min(0)]; a['max'] = [float(x) for x in newpos.max(0)]
        ni = prim['attributes'].get('NORMAL')
        if ni is not None:
            nrm = acc_data(tg, bytes(tblob), ni).astype(float)
            nn = nrm.copy(); nn[:,0] = -nrm[:,0]; nn[:,2] = -nrm[:,2]
            na = tg['accessors'][ni]; nbv = tg['bufferViews'][na['bufferView']]
            noff = (nbv.get('byteOffset',0))+(na.get('byteOffset',0))
            tblob[noff:noff+nn.astype(np.float32).nbytes] = nn.astype(np.float32).tobytes()

    # ---------- weights remap (in place) ----------
    chain_of = {}  # (side) -> chosen chain per vertex handled inline
    for mi, prim, pos in prims:
        j_ai = prim['attributes']['JOINTS_0']; w_ai = prim['attributes']['WEIGHTS_0']
        J = acc_data(tg, bytes(tblob), j_ai)
        Wt = acc_data(tg, bytes(tblob), w_ai).astype(float)
        newpos = Fv(pos.astype(float))
        newJ = np.zeros_like(J); newW = np.zeros_like(Wt)
        # precompute finger joint positions (new space)
        seg1 = {s: {f: fit[f'{s}Hand{f}1'] for f in FINGERS} for s in ['Left','Right']}
        seg23 = {s: {f: [(seg, fit[f'{s}Hand{f}{seg}']) for seg in (2,3) if f'{s}Hand{f}{seg}' in fit] for f in FINGERS} for s in ['Left','Right']}
        for v in range(len(J)):
            acc = {}
            chain_choice = {}
            for k in range(4):
                oj = int(J[v,k]); wgt = float(Wt[v,k])
                if wgt <= 0 or oj >= len(old_names): continue
                on = old_names[oj]
                if on in ('Root','MrAndres5555'):
                    tgt = 'Hips'; acc[tgt] = acc.get(tgt,0)+wgt
                elif 'Eyebrow' in on or 'Brow' in on:
                    acc['Head'] = acc.get('Head',0)+wgt
                elif on in NAME_MAP:
                    tgt = NAME_MAP[on]; acc[tgt] = acc.get(tgt,0)+wgt
                elif on in EXTRA_MAP:
                    tgt = EXTRA_MAP[on][0]; acc[tgt] = acc.get(tgt,0)+wgt
                elif 'HandFinger' in on or 'HandThumb' in on or 'HandIndex' in on:
                    side = 'Left' if on.startswith('Left') else 'Right'
                    seg = 1 if on.endswith('1') else 2
                    if 'Thumb' in on: chain = 'Thumb'
                    elif 'Index' in on: chain = 'Index'
                    else:
                        if side in chain_choice: chain = chain_choice[side]
                        else:
                            d = {f: np.linalg.norm(newpos[v]-seg1[side][f]) for f in FINGERS}
                            chain = min(d, key=d.get); chain_choice[side] = chain
                    if seg == 1:
                        tgt = f'{side}Hand{chain}1'
                    else:
                        cands = seg23[side][chain]
                        tgt = f'{side}Hand{chain}' + str(min(cands, key=lambda c: np.linalg.norm(newpos[v]-c[1]))[0])
                    acc[tgt] = acc.get(tgt,0)+wgt
                else:
                    acc['Hips'] = acc.get('Hips',0)+wgt
            items = sorted(acc.items(), key=lambda kv:-kv[1])[:4]
            tot = sum(w for _,w in items)
            if tot <= 0: items = [('Hips',1.0)]; tot = 1.0
            for k,(jn,wgt) in enumerate(items):
                newJ[v,k] = new_index[jn]; newW[v,k] = wgt/tot
        ja = tg['accessors'][j_ai]; jbv = tg['bufferViews'][ja['bufferView']]
        joff = (jbv.get('byteOffset',0))+(ja.get('byteOffset',0))
        tblob[joff:joff+newJ.nbytes] = newJ.astype(J.dtype).tobytes()
        wa = tg['accessors'][w_ai]; wbv = tg['bufferViews'][wa['bufferView']]
        woff = (wbv.get('byteOffset',0))+(wa.get('byteOffset',0))
        tblob[woff:woff+newW.astype(np.float32).nbytes] = newW.astype(np.float32).tobytes()

    # ---------- write GLB ----------
    js = json.dumps(tg, separators=(',',':')).encode()
    js += b' ' * ((-len(js)) % 4)
    binchunk = bytes(tblob)
    total = 12 + 8+len(js) + 8+len(binchunk)
    with open(args.out,'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(binchunk), 0x004E4942)); f.write(binchunk)
    report = {'target': args.target, 'out': args.out, 'min_y_before': min_y,
              'joints_new': len(new_names), 'extras': extra_names,
              'finger_fit': finger_report,
              'hips_pos': fit['Hips'].round(4).tolist(),
              'head_pos': fit['Head'].round(4).tolist()}
    json.dump(report, open(args.report,'w'), indent=1)
    print(json.dumps(report, indent=1))

if __name__ == '__main__':
    main()
