#!/usr/bin/env python3
"""Per-part facing checker (diagnostic scratch v1).

For each body part of a skinned GLB, measures which way the part's anatomy
faces, from the mesh geometry. No guessing: every number is measured.

Method:
  - Parse GLB (nodes, skins, IBMs, mesh positions + skinning weights).
  - W_J = rest-pose world matrix of joint J; M_J = W_J @ IBM_J (rest-render xform).
  - Part verts = verts whose dominant joint is the part's joint (transformed by M_J).
  - Facing cue per part = horizontal direction of the anatomically-distinctive
    protrusion (nose, chest, toes, calf...). See CUES below.
  - Character forward F: knee-bend cue (knees bend forward; joint positions
    only, immune to mesh flips) + model-facing.json when available.
  - A part is BACKWARDS when its cue points opposite the model's facing.

Usage: python3 per_part_facing.py MODEL.glb
"""
import json, struct, sys, re
import numpy as np

def read_glb(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'glTF'
    jlen = struct.unpack('<I', data[12:16])[0]
    j = json.loads(data[20:20+jlen])
    off = 20 + jlen
    blob = b''
    if off < len(data):
        clen = struct.unpack('<I', data[off:off+4])[0]
        blob = data[off+8:off+8+clen]
    return j, blob

COMP = {5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}
NCOMP = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def accessor(j, blob, idx):
    a = j['accessors'][idx]
    bv = j['bufferViews'][a['bufferView']]
    base = bv.get('byteOffset',0) + a.get('byteOffset',0)
    n = a['count']*NCOMP[a['type']]
    fmt = '<'+str(n)+COMP[a['componentType']]
    return np.array(struct.unpack(fmt, blob[base:base+struct.calcsize(fmt)])).reshape(a['count'],-1)

def qm(q):
    x,y,z,w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

def canon(n):
    n = re.sub(r'^mixamorig:?', '', n); n = re.sub(r'_\d+$', '', n)
    m = re.match(r'^Bip0*1 ([LR]) (.*)$', n)
    if m:
        side = 'Left' if m.group(1) == 'L' else 'Right'
        rest = m.group(2).lower()
        table = {'upperarm':'Arm','forearm':'ForeArm','hand':'Hand','thigh':'UpLeg',
                 'calf':'Leg','foot':'Foot','toe0':'ToeBase','head':'Head','neck':'Neck',
                 'spine':'Spine','spine1':'Spine1','spine2':'Spine2','pelvis':'Hips'}
        return side + table.get(rest, rest)
    m = re.match(r'^([LR])_(.*)$', n)
    if m:
        side = 'Left' if m.group(1) == 'L' else 'Right'
        return side + m.group(2).capitalize()
    return n

def horiz(v):
    v = np.asarray(v, float).copy(); v[1] = 0
    return v

def norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

class Model:
    def __init__(self, path):
        j, blob = read_glb(path)
        self.j, self.blob = j, blob
        N = j['nodes']
        par = {}
        for i, nd in enumerate(N):
            for c in nd.get('children', []):
                par[c] = i
        def local(i):
            nd = N[i]; M = np.eye(4)
            M[:3,:3] = qm(nd.get('rotation',[0,0,0,1])) @ np.diag(nd.get('scale',[1,1,1]))
            M[:3,3] = nd.get('translation',[0,0,0]); return M
        sys.setrecursionlimit(10000)
        W = {}
        def world(i):
            if i not in W:
                W[i] = (world(par[i]) if i in par else np.eye(4)) @ local(i)
            return W[i]
        for i in range(len(N)): world(i)
        self.W = W
        sk = j['skins'][0]
        self.jidx = sk['joints']
        self.names = [canon(N[i].get('name','?')) for i in self.jidx]
        self.idx = {n: k for k, n in enumerate(self.names)}
        self.ibm = accessor(j, blob, sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
        self.M = [W[i] @ self.ibm[k] for k, i in enumerate(self.jidx)]
        self.bindpos = {n: np.linalg.inv(self.ibm[k])[:3,3] for k, n in enumerate(self.names)}
        # gather skinned verts
        self.pos = []; self.dom = []
        for m in j['meshes']:
            for pr in m['primitives']:
                at = pr['attributes']
                if 'JOINTS_0' not in at: continue
                pos = accessor(j, blob, at['POSITION']).astype(float)
                jt = accessor(j, blob, at['JOINTS_0']).astype(int)
                wt = accessor(j, blob, at['WEIGHTS_0']).astype(float)
                dom = jt[np.arange(len(jt)), wt.argmax(1)]
                self.pos.append(pos); self.dom.append(dom)
        self.pos = np.concatenate(self.pos); self.dom = np.concatenate(self.dom)

    def part_verts(self, joint_names, rendered=True):
        """Verts dominated by any of joint_names, optionally in rest-rendered space."""
        ids = [self.idx[n] for n in joint_names if n in self.idx]
        if not ids: return None, None
        sel = np.isin(self.dom, ids)
        if not sel.any(): return None, None
        v = self.pos[sel]
        if rendered:
            # group by dominant joint for correct per-joint M
            out = np.empty_like(v)
            for k in ids:
                s = self.dom[sel] == k
                vv = np.concatenate([v[s], np.ones((s.sum(),1))],1)
                out[s] = (self.M[k] @ vv.T).T[:,:3]
            v = out
        # dominant joint per vert (for joint pos reference)
        dj = self.dom[sel]
        return v, dj

    def knee_forward(self):
        """Character forward from knee anatomy (joint positions only)."""
        F = np.zeros(3)
        for s in ('Left','Right'):
            try:
                H = self.bindpos[s+'UpLeg']; K = self.bindpos[s+'Leg']; A = self.bindpos[s+'Foot']
            except KeyError:
                continue
            off = horiz(K - (H+A)/2)
            if np.linalg.norm(off) > 1e-6: F += norm(off)
        return norm(F) if np.linalg.norm(F) > 1e-9 else None

def foot_facing(model, side):
    """Foot facing from the toe joint (skeleton) verified by mesh presence.
    Returns ('-Z'|'+Z'|'TIE'|'UNCERTAIN', note)."""
    bp = model.bindpos
    Fk, Tk = side+'Foot', side+'ToeBase'
    if Fk not in bp or Tk not in bp:
        return 'UNCERTAIN', 'no toe joint'
    skel = np.array([bp[Tk][0]-bp[Fk][0], 0, bp[Tk][2]-bp[Fk][2]])
    if np.linalg.norm(skel) < 1e-6:
        return 'UNCERTAIN', 'toe joint coincident'
    skel = skel/np.linalg.norm(skel)
    # mesh verification: is there foot mesh beyond the ankle in skel dir?
    v, dj = model.part_verts([Fk, Tk])
    if v is None: return 'UNCERTAIN', 'no foot verts'
    v = v[v[:,1] < bp[Fk][1]+0.06]
    if len(v)==0: return 'UNCERTAIN', 'no low foot verts'
    proj = (v - bp[Fk]) @ skel
    reach = float(np.percentile(proj, 98))
    if reach < 0.05:
        return 'UNCERTAIN', 'no mesh toward toe joint (reach %.2f)' % reach
    facing = '-Z' if skel[2] < -0.5 else ('+Z' if skel[2] > 0.5 else 'TIE')
    return facing, 'toe joint + mesh reach %.2fm' % reach

# part -> (joints, kind, ref, expected, confidence, note)
# kind 'point': signed proj of (vert - refpoint) onto F; ref = joint name
# kind 'axis' : signed proj of perp-from-axis(a,b) onto F; ref = (jointA, jointB)
PARTS = [
    ('head',     ['Head'],                    'point', 'Head',              'front', 'high',     'nose/chin', None),
    ('torso',    ['Spine','Spine1','Spine2'],  'axis',  ('Spine','Spine2'),  'front', 'med-high', 'chest/breast', None),
    ('foot',     ['Foot','ToeBase'],           'point', 'Foot',              'front', 'high',     'toes', ('below', 'Foot', 0.05)),
    ('shin',     ['Leg'],                      'axis',  ('Leg','Foot'),       'back',  'high',     'calf muscle', ('band', 'Foot', 0.30, 'Leg', -0.03)),
    ('thigh',    ['UpLeg'],                    'axis',  ('UpLeg','Leg'),      'front', 'med',      'quadriceps', ('band', 'Leg', 0.03, 'UpLeg', -0.03)),
    ('upperarm', ['Arm'],                      'axis',  ('Arm','ForeArm'),    'front', 'low-med',  'biceps/deltoid', None),
    ('forearm',  ['ForeArm'],                  'axis',  ('ForeArm','Hand'),   'back',  'low',      'elbow tip (olecranon)', None),
    ('hand',     ['Hand'],                     'point', 'Hand',              'side',  'med',      'thumb (T-pose)', None),
]

def check(model):
    """Returns dict part -> {facing: '+Z'/'-Z'/'TIE', front, back, conf, note, n}.
    facing is ABSOLUTE (glTF coords). front/back = protrusion meters toward -Z/+Z.
    Here F is fixed to -Z; 'front' means toward -Z."""
    F = np.array([0., 0., -1.])
    bp = model.bindpos
    results = {}
    for side in ('Left', 'Right'):
        for (part, joints, kind, ref, expected, conf, note, yrestr) in PARTS:
            jn = [(side + j) if j not in ('Spine','Spine1','Spine2','Head') else j
                  for j in joints]
            v, dj = model.part_verts(jn)
            if v is None or len(v) == 0:
                results[f'{part}_{side[0].lower()}'] = None; continue
            if yrestr:
                try:
                    if yrestr[0] == 'below':
                        ymax = bp[side+yrestr[1]][1] + yrestr[2]
                        keep = v[:,1] < ymax
                    elif yrestr[0] == 'band':
                        ymin = bp[side+yrestr[1]][1] + yrestr[2]
                        ymax = bp[side+yrestr[3]][1] + yrestr[4]
                        keep = (v[:,1] > ymin) & (v[:,1] < ymax)
                except KeyError:
                    results[f'{part}_{side[0].lower()}'] = None; continue
                v = v[keep]
                if len(v) == 0:
                    results[f'{part}_{side[0].lower()}'] = None; continue
            Fh = np.array([F[0], 0, F[2]])
            if kind == 'point':
                rp = bp[ref] if ref in bp else bp.get(side+ref)
                if rp is None:
                    results[f'{part}_{side[0].lower()}'] = None; continue
                scores = (v - rp) @ Fh
            else:
                a, b = ref
                abp = bp[a] if a in bp else bp.get(side+a)
                bbp = bp[b] if b in bp else bp.get(side+b)
                if abp is None or bbp is None:
                    results[f'{part}_{side[0].lower()}'] = None
                    continue
                a, b = abp, bbp
                ab = b - a
                rel = v - a
                # full-3D perpendicular from the bone line, then signed onto F
                t = (rel @ ab) / (ab @ ab + 1e-12)
                perp = rel - np.outer(t, ab)
                perph = perp.copy(); perph[:,1] = 0
                scores = perph @ Fh
            front = float(np.percentile(scores, 95))   # robust max toward -Z
            back = float(-np.percentile(scores, 5))    # robust max toward +Z
            med = float(np.median(scores))             # bulk direction
            if part == 'shin':
                # calf is the BULK of the upper shin; use median (boots/spikes are outliers)
                if med > 0.015: facing = '-Z'
                elif med < -0.015: facing = '+Z'
                else: facing = 'TIE'
            elif front > back*1.25: facing = '-Z'
            elif back > front*1.25: facing = '+Z'
            else: facing = 'TIE'
            rep = {'facing': facing, 'front': front, 'back': back,
                   'expected': expected, 'conf': conf, 'note': note, 'n': len(v)}
            if part == 'hand':
                tipname = side + 'HandThumb3'
                if tipname not in bp: tipname = side + 'HandThumb2'
                if tipname in bp and (side+'Hand') in bp:
                    tv = bp[tipname] - bp[side+'Hand']
                    rep['thumb_dotF'] = float(np.array([tv[0],0,tv[2]]) @ Fh / (np.linalg.norm([tv[0],tv[2]])+1e-12))
            if part == 'foot':
                # override with toe-joint + mesh-verified facing (robust to boots)
                ff, fnote = foot_facing(model, side)
                rep['facing'] = ff
                rep['note'] = 'toes: ' + fnote
            results[f'{part}_{side[0].lower()}'] = rep
    return results

def consensus(results):
    """Majority vote of high/med-high conf parts -> model facing."""
    votes = {}
    for k, rep in results.items():
        if rep is None or rep['conf'] not in ('high','med-high'): continue
        f = rep['facing']
        if f in ('TIE','UNCERTAIN'): continue
        # shin expects 'back': its facing is the calf side; model faces opposite
        part = k.rsplit('_',1)[0]
        model_f = {'+Z':'-Z', '-Z':'+Z'}[f] if rep['expected']=='back' else f
        votes[model_f] = votes.get(model_f, 0) + 1
    if not votes: return None
    return max(votes, key=votes.get)

def main():
    import glob
    paths = sys.argv[1:]
    if len(paths)==1 and '*' in paths[0]: paths = sorted(glob.glob(paths[0]))
    print(f"{'model':28s} {'consensus':9s} backwards-parts")
    for path in paths:
        try:
            model = Model(path)
        except Exception as e:
            print(f"{path.split('/')[-1]:28s} ERROR {e}"); continue
        res = check(model)
        con = consensus(res)
        bad = []
        for k in sorted(res):
            rep = res[k]
            if rep is None: continue
            part = k.rsplit('_',1)[0]
            if part == 'hand':
                td = rep.get('thumb_dotF')
                if td is not None and con:
                    # thumb should point toward the model's facing (T-pose, palms down).
                    # td = dot(thumb_dir, [0,0,-1]); for con=-Z want td>0, for +Z want td<0.
                    bad_thumb = (con == '-Z' and td < -0.15) or (con == '+Z' and td > 0.15)
                    if bad_thumb:
                        bad.append(k + "(thumb%+.2f)" % td)
                continue
            if rep['expected'] == 'back':
                part_f = {'+Z':'-Z','-Z':'+Z'}.get(rep['facing'], 'TIE')
            else:
                part_f = rep['facing']
            if con and part_f != 'TIE' and part_f != con and rep['conf'] in ('high','med-high','med'):
                bad.append("%s(%s)" % (k, rep['facing']))
        name = path.split('/')[-1]
        print("%-28s %-9s %s" % (name, str(con), ', '.join(bad) if bad else '-'))

if __name__ == '__main__':
    main()
