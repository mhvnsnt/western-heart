#!/usr/bin/env python3
"""Chirality audit instrument v2 — full-model-audit lane 2026-11-07.

ALL geometry is computed in IBM (bind/mesh) space: joint bind position
B[k] = translation of inv(IBM[k]). That is the space POSITION vertices
live in, so joints and mesh compare directly (the repo's own
tools/model-audit/facing_cues.py works in this frame; the 2026-10-22
nightwolf correction in model-facing.json documents the trap of
measuring mesh facing through a -Z template skeleton's bone matrices).

Layers:
  mesh_facing   : from VERTICES only (head / toe / torso / foot centroids)
  skel_facing   : from joint layout (toe dir + knee bulge) — a mismatch
                  vs mesh_facing is the documented template pattern
  L1            : bone names vs MESH anatomical frame (left = up x fwd)
  L2            : model-facing.json record vs mesh_facing
  L3            : engine-effective: assets.js Y-rotation from the RECORD
                  (unlisted -> meshForward feet cue, else +Z) then
                  t3anims analyzeRig swapLR on Arm X order; the bone the
                  game drives as canonical LeftArm must sit on instance
                  +X (game left). Tekken 1 = LEFT punch decides.
Hand chirality: thumb must be anterior OR lateral-out vs pinky (flat
bind poses make the wrist tetra determinant ~0 — recorded, not judged).
Mirror scan: negative node scale / negative-determinant node matrices.

Usage: glb_audit.py MODEL.glb [--record +Z]
"""
import json, struct, sys, re
import numpy as np

CT = {5120: ('b',1), 5121: ('B',1), 5122: ('h',2), 5123: ('H',2),
      5125: ('I',4), 5126: ('f',4)}
TC = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16}

def read_glb(path):
    d = open(path,'rb').read()
    assert d[:4] == b'glTF', 'not a GLB'
    ln = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20+ln])
    off = 20+ln; blob = b''
    if off < len(d):
        bln = struct.unpack('<I', d[off:off+4])[0]
        blob = d[off+8:off+8+bln]
    return j, blob

def accessor(j, blob, ai):
    a = j['accessors'][ai]; bv = j['bufferViews'][a['bufferView']]
    if 'EXT_meshopt_compression' in bv.get('extensions', {}):
        return None
    fmt, sz = CT[a['componentType']]; n = TC[a['type']]
    data = np.frombuffer(blob, dtype=np.dtype(fmt).newbyteorder('<'),
                         count=a['count']*n,
                         offset=bv.get('byteOffset',0)+a.get('byteOffset',0))
    return data.reshape(a['count'], n) if n > 1 else data

def qmat(q):
    x,y,z,w = q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def node_local(nd):
    if 'matrix' in nd: return np.array(nd['matrix'],float).reshape(4,4).T
    M = np.eye(4)
    M[:3,:3] = qmat(nd.get('rotation',[0,0,0,1])) @ np.diag(nd.get('scale',[1,1,1]))
    M[:3,3] = nd.get('translation',[0,0,0]); return M

def norm_name(n):
    return re.sub(r'^mixamorig[:_]?', '', str(n or ''), flags=re.I)

def side_of(n):
    base = norm_name(n)
    m = re.search(r'(?i)(left|right)', base)
    if m: return 'L' if m.group(1).lower()=='left' else 'R'
    m = re.search(r'[._\-\s]([LR])(?=[._\-\s\d]|$)', base)
    if m: return m.group(1)
    m = re.search(r'^([LR])[_\-\s]', base)
    if m: return m.group(1)
    return None

ROLE_KEYWORDS = [
    ('thumb', r'(?i)thumb'), ('index', r'(?i)index'),
    ('middle', r'(?i)middle'), ('ring', r'(?i)ring'),
    ('pinky', r'(?i)pinky|little'),
    ('shoulder', r'(?i)shoulder|clavicle|collar'),
    ('forearm', r'(?i)forearm|fore_arm|lowerarm|elbow'),
    ('hand', r'(?i)hand|wrist'),
    ('arm', r'(?i)arm|upperarm'),
    ('toe', r'(?i)toe'), ('foot', r'(?i)foot|ankle'),
    ('upleg', r'(?i)upleg|upperleg|thigh'),
    ('leg', r'(?i)shin|calf|knee|(?<![a-z])leg'),
    ('head', r'(?i)(?<![a-z])head'), ('neck', r'(?i)neck'),
    ('chest', r'(?i)chest|spine2|upperchest'), ('spine', r'(?i)spine'),
    ('hips', r'(?i)hips|pelvis|(?<![a-z])hip(?![a-z])'),
]
def role_of(n):
    base = norm_name(n)
    for role, pat in ROLE_KEYWORDS:
        if re.search(pat, base): return role
    return None

def chain_key(n):
    base = norm_name(n); extra = ''
    m = re.search(r'[._](\d{3})$', base)
    if m: extra = m.group(1)
    m2 = re.search(r'(?i)(arm|hand|shoulder|forearm)(\d+)(?![0-9])', base)
    if m2: extra += 'n'+m2.group(2)
    m3 = re.search(r'(?i)\bT(\d+)[_\-]', base)
    if m3: extra += 'T'+m3.group(1)
    return extra

def canon_bone(n):
    base = norm_name(n)
    cs = {'Hips','Spine','Spine1','Spine2','Chest','Neck','Head',
      'LeftShoulder','LeftArm','LeftForeArm','LeftHand','RightShoulder','RightArm','RightForeArm','RightHand',
      'LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase','RightUpLeg','RightLeg','RightFoot','RightToeBase'}
    if base in cs: return base
    b2 = re.sub(r'_\d+$','',base)
    if b2 in cs: return b2
    m = re.match(r'^Bip0*1_(?:(L|R)_)?([A-Za-z]+\d?)$', base)
    biped = {'Pelvis':'Hips','Spine':'Spine','Spine1':'Spine1','Spine2':'Spine2','Neck':'Neck','Head':'Head',
             'Clavicle':'Shoulder','UpperArm':'Arm','Forearm':'ForeArm','Hand':'Hand',
             'Thigh':'UpLeg','Calf':'Leg','Foot':'Foot','Toe0':'ToeBase'}
    if m and m.group(2) in biped:
        part = biped[m.group(2)]
        if not m.group(1): return part if part in ('Hips','Spine','Spine1','Spine2','Neck','Head') else None
        return ('Left' if m.group(1)=='L' else 'Right')+part
    m = re.match(r'^([LR])_([A-Za-z]+)$', base)
    lrs = {'Shoulder':'Shoulder','Arm':'Arm','ForeArm':'ForeArm','Hand':'Hand',
           'UpLeg':'UpLeg','Leg':'Leg','Foot':'Foot','Toe':'ToeBase'}
    if m and m.group(2) in lrs: return ('Left' if m.group(1)=='L' else 'Right')+lrs[m.group(2)]
    if base in ('Hip','Pelvis'): return 'Hips'
    return None

FV = {'+Z': np.array([0,0,1.]), '-Z': np.array([0,0,-1.]),
      '+X': np.array([1.,0,0]), '-X': np.array([-1.,0,0])}
def axis_of(vec):
    axes = ['+X','-X','+Z','-Z']; vecs = [FV['+X'],FV['-X'],FV['+Z'],FV['-Z']]
    dots = [float(vec@v) for v in vecs]; bi = int(np.argmax(dots))
    return axes[bi], round(dots[bi],3)
def rot_y_to_plusz(f):
    if f == '-Z': return np.diag([-1.,1,-1])
    if f == '+X': return np.array([[0.,0,-1],[0,1,0],[1,0,0]])
    if f == '-X': return np.array([[0.,0,1],[0,1,0],[-1,0,0]])
    return np.eye(3)

def audit(path, facing_record=None):
    j, blob = read_glb(path)
    N = j['nodes']
    par = {c:i for i,nd in enumerate(N) for c in nd.get('children',[])}
    sys.setrecursionlimit(100000)
    cache = {}
    def world(i):
        if i in cache: return cache[i]
        M = node_local(N[i]); W = (world(par[i]) @ M) if i in par else M
        cache[i] = W; return W
    skins = j.get('skins', [])
    rec = {'path': path, 'nodes': len(N), 'skins': len(skins),
           'meshopt': 'EXT_meshopt_compression' in (j.get('extensionsUsed') or [])}
    neg = []
    for nd in N:
        sc = nd.get('scale')
        if sc and any(s < 0 for s in sc): neg.append((nd.get('name'), sc))
        if 'matrix' in nd and np.linalg.det(np.array(nd['matrix'],float).reshape(4,4).T[:3,:3]) < 0:
            neg.append((nd.get('name'), 'negdet-matrix'))
    rec['negative_transform_nodes'] = neg[:20]
    if not skins:
        rec['verdict'] = 'UNTESTABLE'; rec['reason'] = 'no skins (unrigged)'; return rec
    sk = skins[0]; joints = sk['joints']
    names = [N[i].get('name','') for i in joints]
    # positions: SCENE space (node traversal). IBM-space is Z-up for
    # Z-up-authored files (root -90deg X), scene space is the frame the
    # game and renders actually see.
    B = [world(i)[:3,3] for i in joints]
    space = 'scene'
    rec['position_space'] = space
    # IBM cross-check (rotated-frame tolerant): compare pairwise distances
    if 'inverseBindMatrices' in sk:
        ibm = accessor(j, blob, sk['inverseBindMatrices'])
        if ibm is not None:
            ibm = ibm.astype(float).reshape(-1,4,4).transpose(0,2,1)
            Bi = [np.linalg.inv(m)[:3,3] for m in ibm]
            import itertools
            dd = 0.0
            for a,b in itertools.combinations(range(min(len(B),40)),2):
                dd = max(dd, abs(float(np.linalg.norm(B[a]-B[b]) - np.linalg.norm(Bi[a]-Bi[b]))))
            rec['ibm_pairwise_dist_maxdiff'] = round(dd,6)
    P = {k: B[k] for k in range(len(joints))}
    table = []
    for k, nm in enumerate(names):
        table.append({'name': nm, 'canon': canon_bone(nm), 'side': side_of(nm),
                      'role': role_of(nm), 'chain': chain_key(nm),
                      'pos': [round(float(x),4) for x in B[k]]})
    rec['joints'] = table
    ys = np.array([p[1] for p in B]); height = float(ys.max()-ys.min()) or 1.0
    rec['joint_height_span'] = round(height,3)
    hips_k = next((k for k,nm in enumerate(names) if canon_bone(nm)=='Hips'), None)
    hips = B[hips_k] if hips_k is not None else np.mean(B,axis=0)
    pos_by = {}
    for t in table: pos_by.setdefault((t['side'],t['role'],t['chain']), np.array(t['pos']))
    canon_k = {}
    for k,nm in enumerate(names):
        cb = canon_bone(nm)
        if cb and cb not in canon_k: canon_k[cb] = k
    # ---- vertex dominance centroids (IBM space) ----
    cents = {}
    readable = False
    mesh_nodes = {}
    for ni, nd in enumerate(N):
        if 'mesh' in nd: mesh_nodes.setdefault(nd['mesh'], []).append(ni)
    for mi, m in enumerate(j.get('meshes',[])):
        W = None
        for ni in mesh_nodes.get(mi, []):
            W = world(ni); break
        for pr in m['primitives']:
            at = pr['attributes']
            if 'JOINTS_0' not in at or 'POSITION' not in at: continue
            pos = accessor(j,blob,at['POSITION']); jt = accessor(j,blob,at['JOINTS_0']); wt = accessor(j,blob,at['WEIGHTS_0'])
            if pos is None or jt is None or wt is None: continue
            readable = True
            pos = pos.astype(float)
            if W is not None:
                pos = pos @ W[:3,:3].T + W[:3,3]
            dom = jt[np.arange(len(jt)), wt.argmax(1)]
            for kk in set(dom.tolist()):
                if kk < len(joints):
                    cents.setdefault(kk, []).append(pos[dom==kk])
    cents = {k: np.concatenate(v).mean(0) for k,v in cents.items() if len(np.concatenate(v))>10}
    rec['vertex_space_readable'] = readable
    # ---- mesh facing votes (vertices) ----
    mvotes = []
    if 'Head' in canon_k and canon_k['Head'] in cents:
        d = cents[canon_k['Head']] - B[canon_k['Head']]; d[1]=0
        if np.linalg.norm(d) > 0.01*height: mvotes.append(('headverts', d/np.linalg.norm(d), 2))
    toe_ds = []
    for cb_t, cb_f in (('LeftToeBase','LeftFoot'),('RightToeBase','RightFoot')):
        if cb_t in canon_k and canon_k[cb_t] in cents and cb_f in canon_k:
            d = cents[canon_k[cb_t]] - B[canon_k[cb_f]]; d[1]=0
            if np.linalg.norm(d) > 0.005*height: toe_ds.append(d/np.linalg.norm(d))
    if toe_ds:
        v = np.mean(toe_ds,axis=0); mvotes.append(('toeeverts', v/np.linalg.norm(v), 2))
    spk = [canon_k[c] for c in ('Spine','Spine1','Spine2','Chest') if c in canon_k and canon_k[c] in cents]
    if spk:
        c = np.mean([cents[k] for k in spk],axis=0); jo = np.mean([B[k] for k in spk],axis=0)
        d = c-jo; d[1]=0
        if np.linalg.norm(d) > 0.01*height: mvotes.append(('torsoverts', d/np.linalg.norm(d), 1))
    foot_ds = []
    for cb_f in ('LeftFoot','RightFoot'):
        if cb_f in canon_k and canon_k[cb_f] in cents:
            d = cents[canon_k[cb_f]] - B[canon_k[cb_f]]; d[1]=0
            if np.linalg.norm(d) > 0.01*height: foot_ds.append(d/np.linalg.norm(d))
    if foot_ds:
        v = np.mean(foot_ds,axis=0); mvotes.append(('footverts', v/np.linalg.norm(v), 1))
    rec['mesh_facing_votes'] = [(k,[round(float(x),3) for x in v],w) for k,v,w in mvotes]
    mesh_facing = None
    if mvotes:
        tot = sum(v*w for _,v,w in mvotes)
        if np.linalg.norm(tot)>1e-6:
            mesh_facing, dot = axis_of(tot/np.linalg.norm(tot))
            rec['mesh_facing_dot'] = dot
            rec['mesh_facing_agree'] = f"{sum(1 for _,v,_ in mvotes if float(v@FV[mesh_facing])>0.5)}/{len(mvotes)}"
    rec['mesh_facing'] = mesh_facing
    # ---- skeleton facing votes (joints) ----
    svotes = []
    td = []
    for s in ('L','R'):
        f = pos_by.get((s,'foot','')); t = pos_by.get((s,'toe',''))
        if f is not None and t is not None:
            d = t-f; d[1]=0
            if np.linalg.norm(d) > 0.005*height: td.append(d/np.linalg.norm(d))
    if td:
        v = np.mean(td,axis=0); svotes.append(('skeltoe', v/np.linalg.norm(v), 2))
    kd = []
    for s in ('L','R'):
        h = pos_by.get((s,'upleg','')); k = pos_by.get((s,'leg','')); a = pos_by.get((s,'foot',''))
        if h is not None and k is not None and a is not None:
            d = k-(h+a)/2; d[1]=0
            if np.linalg.norm(d) > 0.01*height: kd.append(d/np.linalg.norm(d))
    if kd:
        v = np.mean(kd,axis=0); svotes.append(('skelknee', v/np.linalg.norm(v), 1))
    rec['skel_facing_votes'] = [(k,[round(float(x),3) for x in v],w) for k,v,w in svotes]
    skel_facing = None
    if svotes:
        tot = sum(v*w for _,v,w in svotes)
        if np.linalg.norm(tot)>1e-6: skel_facing, _ = axis_of(tot/np.linalg.norm(tot))
    rec['skel_facing'] = skel_facing
    # ---- L1 ----
    f_L1 = mesh_facing or facing_record or skel_facing or '+Z'
    rec['facing_used_L1'] = f_L1
    rec['L1_confidence'] = 'mesh' if mesh_facing else ('record' if facing_record else ('skeleton' if skel_facing else 'default'))
    fwd = FV[f_L1]; left = np.cross(np.array([0,1.,0]), fwd)
    def sscore(pos): return float((np.array(pos)-hips) @ left)/height
    l1 = []; flipped = []
    for t in table:
        if t['side'] and t['role'] in ('shoulder','arm','forearm','hand','upleg','leg','foot','toe','thumb','index','middle','ring','pinky'):
            s = sscore(t['pos']); exp = 1 if t['side']=='L' else -1
            ok = s*exp > 0.01; bord = abs(s) <= 0.01
            l1.append({'name':t['name'],'side':t['side'],'role':t['role'],'chain':t['chain'],
                       'signed': round(s,4), 'ok': bool(ok), 'borderline': bool(bord)})
            if not ok and not bord: flipped.append(t['name'])
    rec['L1_rows'] = l1; rec['L1_flipped_names'] = flipped
    arm_flip = [r for r in l1 if r['role'] in ('shoulder','arm','forearm','hand') and not r['ok'] and not r['borderline']]
    leg_flip = [r for r in l1 if r['role'] in ('upleg','leg','foot','toe') and not r['ok'] and not r['borderline']]
    rec['rig_names_vs_mesh'] = 'FLIPPED' if (arm_flip or leg_flip) else 'OK'
    # ---- hands ----
    hands = {}
    for s in ('L','R'):
        for extra in sorted(set(t['chain'] for t in table if t['side']==s)):
            w = pos_by.get((s,'hand',extra)); th = pos_by.get((s,'thumb',extra))
            ix = pos_by.get((s,'index',extra)); pk = pos_by.get((s,'pinky',extra))
            if w is not None and th is not None and pk is not None:
                ant_t = float((th-w) @ fwd); ant_p = float((pk-w) @ fwd)
                lat_t = float((th-w) @ left) * (1 if s=='L' else -1)
                lat_p = float((pk-w) @ left) * (1 if s=='L' else -1)
                hands[f"{s}{extra}"] = {'thumb_ant': round(ant_t,4), 'pinky_ant': round(ant_p,4),
                    'thumb_lat_out': round(lat_t,4), 'pinky_lat_out': round(lat_p,4),
                    'thumb_bad': bool(ant_t < ant_p - 0.002*height and lat_t < lat_p - 0.002*height)}
    rec['hands'] = hands
    # ---- L2 / L3 ----
    rec['facing_record'] = facing_record
    if mesh_facing and facing_record:
        rec['L2_record'] = 'OK' if mesh_facing == facing_record else 'WRONG'
    elif facing_record: rec['L2_record'] = 'UNVERIFIED(no mesh votes)'
    else: rec['L2_record'] = 'MISSING'
    armL = next((t for t in table if t['canon']=='LeftArm'), None)
    armR = next((t for t in table if t['canon']=='RightArm'), None)
    eng = {}
    rec_used = facing_record or (mesh_facing if mesh_facing else '+Z')
    eng['record_used'] = rec_used; eng['record_source'] = 'facing.json' if facing_record else 'fallback'
    if armL and armR:
        R = rot_y_to_plusz(rec_used)
        xL = float((R @ (np.array(armL['pos'])-hips))[0]); xR = float((R @ (np.array(armR['pos'])-hips))[0])
        swap = xL < xR
        driven = armR if swap else armL
        xd = float((R @ (np.array(driven['pos'])-hips))[0])
        if abs(xL - xR) < 1e-6:
            eng.update({'xL_inst': round(xL,4), 'xR_inst': round(xR,4), 'swapLR': bool(swap),
                        'driven_left_bone': driven['name'], 'driven_left_x': round(xd,4),
                        'effective': 'DEGENERATE(arms along facing axis; X-order test n/a)'})
        else:
            eng.update({'xL_inst': round(xL,4), 'xR_inst': round(xR,4), 'swapLR': bool(swap),
                        'driven_left_bone': driven['name'], 'driven_left_x': round(xd,4),
                        'effective': 'OK' if xd > 0 else 'SWAPPED'})
    else:
        eng['effective'] = 'NO_CANON_ARMS'
    rec['L3_engine'] = eng
    # ---- verdict ----
    if eng.get('effective') == 'SWAPPED': rec['verdict'] = 'SWAPPED-RETARGET(effective in game)'
    elif str(eng.get('effective','')).startswith('DEGENERATE'): rec['verdict'] = 'NEEDS-FACING-REVIEW(arms along facing axis)'
    elif eng.get('effective') == 'NO_CANON_ARMS': rec['verdict'] = 'UNTESTABLE(no canon arms via engine map)'
    elif any(h['thumb_bad'] for h in hands.values()): rec['verdict'] = 'HAND-CHIRALITY-FLAG'
    elif rec['rig_names_vs_mesh'] == 'FLIPPED': rec['verdict'] = 'NAMES-FLIPPED-VS-MESH(engine-corrected)'
    else: rec['verdict'] = 'OK'
    return rec

if __name__ == '__main__':
    path = sys.argv[1]; fr = None
    if '--record' in sys.argv: fr = sys.argv[sys.argv.index('--record')+1]
    print(json.dumps(audit(path, fr), indent=1, default=str))
