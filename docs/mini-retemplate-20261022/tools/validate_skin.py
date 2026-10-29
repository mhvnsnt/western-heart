import sys, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/_mini-rt-scratch/tools')
from inspect2 import load, node_m, worlds, acc_data

def lbs_check(path, pose=None):
    g, blob = load(path)
    w = worlds(g)
    skin = g['skins'][0]
    joints = skin['joints']
    ibm = acc_data(g, blob, skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
    # IBM error: IBM @ W(bind) should be I
    err = 0.0
    for i,j in enumerate(joints):
        err = max(err, float(np.abs(ibm[i] @ w[j] - np.eye(4)).max()))
    prim = g['meshes'][0]['primitives'][0]
    pos = acc_data(g, blob, prim['attributes']['POSITION']).astype(float)
    J = acc_data(g, blob, prim['attributes']['JOINTS_0']).astype(int)
    Wt = acc_data(g, blob, prim['attributes']['WEIGHTS_0']).astype(float)
    def deform(worlds_map):
        skin_m = np.zeros((len(joints),4,4))
        for i,j in enumerate(joints): skin_m[i] = worlds_map[j] @ ibm[i]
        out = np.zeros_like(pos)
        for k in range(4):
            idx = J[:,k]
            m = skin_m[idx]
            hom = np.concatenate([pos, np.ones((len(pos),1))], axis=1)
            d = np.einsum('nij,nj->ni', m, hom)[:,:3]
            out += d * Wt[:,k:k+1]
        return out
    rest = deform(w)
    rest_err = float(np.abs(rest-pos).max())
    res = {'file': path, 'joints': len(joints), 'ibm_err': err, 'rest_lbs_err': rest_err,
           'geom_min_y': float(pos[:,1].min()), 'geom_max_y': float(pos[:,1].max())}
    if pose:
        # pose: dict joint_name -> (axis, degrees) applied as local rotation premultiply
        name2node = {g['nodes'][j].get('name'): j for j in joints}
        w2 = dict(w)
        # recompute worlds with posed locals: rebuild hierarchy
        parent = {}
        for i,n in enumerate(g['nodes']):
            for c in n.get('children',[]): parent[c]=i
        def local_m(n, extra=None):
            m = node_m(n)
            if extra is not None:
                R = np.eye(4); R[:3,:3] = extra; m = m @ R
            return m
        import math
        def axis_R(axis, deg):
            t = math.radians(deg); c,s = np.cos(t), np.sin(t)
            if axis=='x': return np.array([[1,0,0],[0,c,-s],[0,s,c]])
            if axis=='y': return np.array([[c,0,s],[0,1,0],[-s,0,c]])
            return np.array([[c,-s,0],[s,c,0],[0,0,1]])
        new_w = {}
        def visit(i, pm):
            n = g['nodes'][i]; nm = n.get('name')
            extra = axis_R(*pose[nm]) if nm in pose else None
            m = pm @ local_m(n, extra); new_w[i] = m
            for c in n.get('children',[]): visit(c, m)
        for s in g['scenes']:
            for r in s['nodes']: visit(r, np.eye(4))
        posed = deform(new_w)
        disp = np.linalg.norm(posed-pos, axis=1)
        res['pose'] = {k: list(v) for k,v in pose.items()}
        res['pose_max_disp'] = float(disp.max())
        res['pose_mean_disp_weighted_bones'] = float(disp[Wt.max(1)>0.9].mean()) if (Wt.max(1)>0.9).any() else None
        # verts bound to Head must not move when only legs bend
        head_j = joints.index(name2node['Head']) if 'Head' in name2node else None
        res['posed_bbox_min_y'] = float(posed[:,1].min())
    print(json.dumps(res, indent=1))
    return res

if __name__ == '__main__':
    pose = {'LeftLeg': ('x', 50), 'RightForeArm': ('x', -70), 'Spine1': ('x', 12)}
    lbs_check(sys.argv[1], pose)
