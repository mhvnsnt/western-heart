#!/usr/bin/env python3
"""Stage A analysis: per-model rest-pose head twist + scale audit from GLB JSON metadata.
Key idea (from t3anims.js): the retarget sets W(Head) = D.Head * Wrest(Head) with A(Head)=identity
(no direction correction for the head, unlike limbs). At a neutral stance frame D~identity, so the
head's world orientation IS the model's rest head orientation, and its twist relative to the chest
is the model's own rest head-vs-chest rotation. Same for scales: retarget emits quaternion tracks
only, so any non-uniform bone scale in the file persists and shears under rotation."""
import os, json, math, re
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
META = os.path.join(ROOT, 'glbmeta')

CANON = {'Hips','Spine','Spine1','Spine2','Chest','Neck','Head','LeftShoulder','LeftArm','LeftForeArm','LeftHand',
 'RightShoulder','RightArm','RightForeArm','RightHand','LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase',
 'RightUpLeg','RightLeg','RightFoot','RightToeBase'}
BIPED = {'Pelvis':'Hips','Spine':'Spine','Spine1':'Spine1','Spine2':'Spine2','Neck':'Neck','Head':'Head',
 'Clavicle':'Shoulder','UpperArm':'Arm','Forearm':'ForeArm','Hand':'Hand','Thigh':'UpLeg','Calf':'Leg','Foot':'Foot','Toe0':'ToeBase'}
LR = {'Shoulder':'Shoulder','Arm':'Arm','ForeArm':'ForeArm','Hand':'Hand','UpLeg':'UpLeg','Leg':'Leg','Foot':'Foot','Toe':'ToeBase'}
def canon(name):
    n = re.sub(r'^mixamorig[:_]?', '', str(name), flags=re.I)
    if n in CANON: return n
    n2 = re.sub(r'_\d+$', '', n)
    if n2 in CANON: return n2
    m = re.match(r'^Bip0*1_(?:(L|R)_)?([A-Za-z]+\d?)$', n)
    if m and m.group(2) in BIPED:
        part = BIPED[m.group(2)]
        if not m.group(1): return part if part in ('Hips','Spine','Spine1','Spine2','Neck','Head') else None
        return ('Left' if m.group(1)=='L' else 'Right') + part
    m = re.match(r'^(L|R)_([A-Za-z]+)$', n)
    if m and m.group(2) in LR: return ('Left' if m.group(1)=='L' else 'Right') + LR[m.group(2)]
    if n in ('Hip','Pelvis'): return 'Hips'
    return None

def q2m(q):
    x,y,z,w = q
    return np.array([
      [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
      [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
      [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], float)
def local_mat(n):
    if 'matrix' in n:
        return np.array(n['matrix'], float).reshape(4,4).T  # glTF column-major
    t = n.get('translation',[0,0,0]); r = n.get('rotation',[0,0,0,1]); s = n.get('scale',[1,1,1])
    M = np.eye(4); M[:3,:3] = q2m(r) * np.array(s)[None,:]; M[:3,3] = t
    return M
def quat_of(M):
    R = M[:3,:3]
    # strip scale
    nrm = np.linalg.norm(R, axis=0); R = R / np.where(nrm==0,1,nrm)[None,:]
    tr = np.trace(R)
    if tr > 0:
        s = math.sqrt(tr+1)*2; w = 0.25*s; x=(R[2,1]-R[1,2])/s; y=(R[0,2]-R[2,0])/s; z=(R[1,0]-R[0,1])/s
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        s = math.sqrt(1+R[0,0]-R[1,1]-R[2,2])*2; w=(R[2,1]-R[1,2])/s; x=0.25*s; y=(R[0,1]+R[1,0])/s; z=(R[0,2]+R[2,0])/s
    elif R[1,1] > R[2,2]:
        s = math.sqrt(1+R[1,1]-R[0,0]-R[2,2])*2; w=(R[0,2]-R[2,0])/s; x=(R[0,1]+R[1,0])/s; y=0.25*s; z=(R[1,2]+R[2,1])/s
    else:
        s = math.sqrt(1+R[2,2]-R[0,0]-R[1,1])*2; w=(R[1,0]-R[0,1])/s; x=(R[0,2]+R[2,0])/s; y=(R[1,2]+R[2,1])/s; z=0.25*s
    q = np.array([x,y,z,w]); return q/np.linalg.norm(q)
def qmul(a,b): # xyzw
    ax,ay,az,aw=a; bx,by,bz,bw=b
    return np.array([aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz])
def qinv(q): return np.array([-q[0],-q[1],-q[2],q[3]])/np.dot(q,q)
def euler_yxz(q):
    # rotation matrix, extract YXZ euler (yaw Y, pitch X, roll Z) degrees
    R = q2m(q)
    pitch = math.asin(max(-1,min(1,-R[1,2])))
    yaw = math.atan2(R[0,2], R[2,2])
    roll = math.atan2(R[1,0], R[1,1])
    return tuple(math.degrees(a) for a in (yaw,pitch,roll))

rows = []
for fn in sorted(os.listdir(META)):
    if not fn.endswith('.json'): continue
    key = fn[:-5]
    try: g = json.load(open(os.path.join(META, fn)))
    except Exception as e: rows.append((key, f'PARSE-ERR {e}')); continue
    nodes = g.get('nodes', [])
    if not nodes: rows.append((key,'no-nodes')); continue
    parent = {}
    for i,n in enumerate(nodes):
        for c in n.get('children',[]): parent[c]=i
    world = [None]*len(nodes)
    def wm(i):
        if world[i] is not None: return world[i]
        M = local_mat(nodes[i])
        if i in parent: M = wm(parent[i]) @ M
        world[i]=M; return M
    for i in range(len(nodes)): wm(i)
    by = {}
    for i,n in enumerate(nodes):
        c = canon(n.get('name',''))
        if c and c not in by: by[c]=i
    rec = {'key':key,'url':g.get('_wh_url'),'bones':len(nodes)}
    if 'Head' not in by or 'Hips' not in by:
        rec['error']='no Head/Hips canon'; rows.append(rec); continue
    hi, he = by['Hips'], by['Head']
    chest = by.get('Chest') or by.get('Spine2') or by.get('Spine1') or by.get('Spine')
    qh, qc, qhip = quat_of(world[he]), quat_of(world[chest]), quat_of(world[hi])
    rel = qmul(qinv(qc), qh)
    yaw,pitch,roll = euler_yxz(rel)
    rec.update({'head_vs_chest_yaw':round(yaw,1),'pitch':round(pitch,1),'roll':round(roll,1),
                'rel_angle':round(math.degrees(2*math.acos(min(1,abs(rel[3])))),1)})
    # neck chain length
    chain=[]; o=he
    while o is not None and o!=chest:
        chain.append(nodes[o].get('name','')); o=parent.get(o)
    rec['neck_chain']=chain
    # scales: world column norms for head chain + ancestors; local scales too
    def wscale(i): 
        c=np.linalg.norm(world[i][:3,:3],axis=0); return c
    bad=[]
    o=he; anc=[]
    while o is not None:
        anc.append(o); o=parent.get(o)
    for i in anc:
        ws = wscale(i); ratio = ws.max()/max(ws.min(),1e-9)
        ls = nodes[i].get('scale',[1,1,1])
        if ratio>1.03 or max(abs(np.array(ls)-1))>0.01:
            bad.append(f"{nodes[i].get('name')} localS={ls} worldRatio={ratio:.2f} worldS={np.round(ws,2).tolist()}")
    rec['scale_flags']=bad
    # face/head descendant bones with non-unit local scale
    desc=[]
    stack=[he]
    while stack:
        i=stack.pop()
        for c in nodes[i].get('children',[]):
            stack.append(c)
            ls=nodes[c].get('scale',[1,1,1])
            if max(abs(np.array(ls)-1))>0.01: desc.append(f"{nodes[c].get('name')} {ls}")
    rec['head_desc_scale_flags']=desc[:6]
    rec['n_head_desc']=len(desc)
    # embedded animations: scale tracks on head/neck nodes
    st=[]
    for a in g.get('animations',[]):
        for ch in a.get('channels',[]):
            tg=ch.get('target',{})
            if tg.get('path')=='scale':
                nm=nodes[tg.get('node',-1)].get('name','?') if tg.get('node',-1)<len(nodes) else '?'
                if canon(nm) in ('Head','Neck','Chest','Spine2','Hips') or 'head' in nm.lower() or 'neck' in nm.lower():
                    st.append(f"{a.get('name','?')}:{nm}")
    rec['embedded_head_scale_tracks']=st[:5]
    rows.append(rec)

json.dump(rows, open(os.path.join(ROOT,'stageA_results.json'),'w'), indent=1)
tw = [r for r in rows if isinstance(r,dict) and abs(r.get('head_vs_chest_yaw',0))>20]
print(f"models analyzed: {len(rows)}; head-vs-chest |yaw|>20deg: {len(tw)}")
for r in sorted(tw, key=lambda r:-abs(r['head_vs_chest_yaw'])):
    print(f"TWIST {r['key']:28s} yaw={r['head_vs_chest_yaw']:7.1f} pitch={r['pitch']:7.1f} roll={r['roll']:7.1f} angle={r['rel_angle']:6.1f} chain={r['neck_chain']}")
sc = [r for r in rows if isinstance(r,dict) and (r.get('scale_flags') or r.get('head_desc_scale_flags'))]
print(f"\nmodels with scale flags: {len(sc)}")
for r in sc: print('SCALE', r['key'], r['scale_flags'], r['head_desc_scale_flags'])
et = [r for r in rows if isinstance(r,dict) and r.get('embedded_head_scale_tracks')]
print(f"\nmodels with embedded head/neck scale tracks: {len(et)}")
for r in et: print('EMBSCALE', r['key'], r['embedded_head_scale_tracks'])
err = [r for r in rows if not isinstance(r,dict) or r.get('error')]
print('\nerrors:', err)
