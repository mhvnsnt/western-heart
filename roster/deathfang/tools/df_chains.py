import numpy as np, math, os
from pygltflib import GLTF2

base = os.path.expanduser("~/workspace/_wh-work/deathfang-yamazaki")
g = GLTF2().load(base + "/roster/iori/attires/attire1/model.glb")

def trs(n):
    T = np.eye(4)
    if n.translation: T[:3, 3] = n.translation
    R = np.eye(4)
    if n.rotation:
        x, y, z, w = n.rotation
        R[:3, :3] = np.array([
            [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    S = np.diag(list(n.scale)+[1.0]) if n.scale else np.eye(4)
    return T @ R @ S

world = {}
def walk(i, P):
    W = P @ trs(g.nodes[i]); world[i] = W
    for c in (g.nodes[i].children or []): walk(c, W)
for r in g.scenes[0].nodes: walk(r, np.eye(4))

name2idx = {n.name: i for i, n in enumerate(g.nodes)}
def jpos(name): return (world[name2idx[name]] @ np.array([0, 0, 0, 1.]))[:3]
def jdir(name):
    i = name2idx[name]; kids = g.nodes[i].children or []
    joint_set = set(g.skins[0].joints)
    for k in kids:
        if k in joint_set:
            d = jpos(g.nodes[k].name) - jpos(name)
            if np.linalg.norm(d) > 1e-6: return d/np.linalg.norm(d)
    return np.array([0., 1., 0.])

head = jpos('Bip001 Head_019')
eye_mid = (jpos('Eye L Bone001_024') + jpos('Eye R Bone001_025')) / 2
FACE = eye_mid - head; FACE[1] = 0; FACE = FACE/np.linalg.norm(FACE)
print("FACE dir:", FACE)
W13 = world[name2idx['Object_13']]
W13inv = np.linalg.inv(W13)
print("W13 det:", np.linalg.det(W13))

def rot_to(axis):
    z = np.array([0., 0., 1.]); a = np.array(axis, float); a = a/np.linalg.norm(a)
    v = np.cross(z, a); c = float(np.dot(z, a))
    if np.linalg.norm(v) < 1e-8:
        return np.eye(3) if c > 0 else np.diag([1., -1., -1.])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0/(1.0+c))

def torus(center, axis, R, r, ms=14, ns=8):
    Rm = rot_to(axis); verts = []; norms = []
    for i in range(ms+1):
        u = 2*math.pi*i/ms; cu, su = math.cos(u), math.sin(u)
        for j in range(ns+1):
            v = 2*math.pi*j/ns
            n = np.array([cu*math.cos(v), su*math.cos(v), math.sin(v)])
            p = np.array([R*cu, R*su, 0.]) + r*n
            verts.append(Rm @ p + np.array(center)); norms.append(Rm @ n)
    idx = []; w = ns+1
    for i in range(ms):
        for j in range(ns):
            a = i*w + j; b2 = a + w
            idx += [a, b2, a+1, b2, b2+1, a+1]
    return np.array(verts), np.array(norms), np.array(idx, 'uint32')

DOWN = np.array([0., -1., 0.]); SIDE = np.array([1., 0., 0.])
sets = {}
def newset(name, joint): sets[name] = ([], [], [], joint)
def add(name, tv, tn, ti):
    v, n, ix = sets[name][0], sets[name][1], sets[name][2]
    off = sum(len(x) for x in v)
    v.append(tv); n.append(tn); ix.append(ti + off)
def shackle(name, bone, axis_bone, R, r):
    add(name, *torus(jpos(bone), jdir(axis_bone), R, r))
def hang(name, start, count, R, r, step):
    c = np.array(start, float)
    for i in range(count):
        add(name, *torus(c, np.array([0., 0., 1.]) if i % 2 == 0 else SIDE, R, r))
        c = c + DOWN*step
def line(name, p0, p1, count, R, r):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    tang = (p1-p0)/np.linalg.norm(p1-p0)
    alt = np.cross(tang, [0., 1., 0.]) if abs(tang[1]) < 0.9 else np.cross(tang, [1., 0., 0.])
    alt = alt/np.linalg.norm(alt)
    for i in range(count):
        t = i/(count-1) if count > 1 else 0.
        add(name, *torus(p0 + (p1-p0)*t, tang if i % 2 == 0 else alt, R, r))

for side, hand, fore in (('L', 'Bip001 L Hand_029', 'Bip001 L Forearm_028'), ('R', 'Bip001 R Hand_046', 'Bip001 R Forearm_045')):
    newset('wrist'+side, hand)
    shackle('wrist'+side, hand, fore, 0.058, 0.021)
    c = jpos(hand); c[1] -= 0.075
    hang('wrist'+side, c, 5, 0.05, 0.016, 0.082)
for side, foot, calf in (('L', 'Bip001 L Foot_05', 'Bip001 L Calf_04'), ('R', 'Bip001 R Foot_012', 'Bip001 R Calf_011')):
    newset('ankle'+side, foot)
    c0 = jpos(foot); c0 = c0 + np.array([0., 0.02, 0.])
    add('ankle'+side, *torus(c0, jdir(calf), 0.07, 0.024))
aL = jpos('Bip001 L Foot_05'); aR = jpos('Bip001 R Foot_012')
newset('anklechain', ('split', 'Bip001 L Foot_05', 'Bip001 R Foot_012'))
pts = []
for i in range(5):
    t = i/4
    p = aL + (aR-aL)*t; p[1] = 0.09
    pts.append(p)
for i, p in enumerate(pts):
    tang = pts[min(i+1, 4)] - pts[max(i-1, 0)]; tang = tang/np.linalg.norm(tang)
    alt = np.cross(tang, [0., 0., 1.]); alt = alt/max(np.linalg.norm(alt), 1e-9)
    add('anklechain', *torus(p, tang if i % 2 == 0 else alt, 0.042, 0.014))
newset('collar', 'Bip001 Neck_018')
shackle('collar', 'Bip001 Neck_018', 'Bip001 Neck_018', 0.115, 0.03)
c = jpos('Bip001 Neck_018') + FACE*0.115; c[1] -= 0.1
hang('collar', c, 3, 0.05, 0.016, 0.082)
cl_ = jpos('Bip001 L Clavicle_026') + FACE*0.15
cr_ = jpos('Bip001 R Clavicle_043') + FACE*0.15
pel = jpos('Bip001 Pelvis_01')
pl_ = pel + np.array([0.12, 0.02, 0.]) + FACE*0.16
pr_ = pel + np.array([-0.12, 0.02, 0.]) + FACE*0.16
newset('chest1', 'Bip001 Spine1_017'); line('chest1', cl_, pr_, 6, 0.045, 0.014)
newset('chest2', 'Bip001 Spine1_017'); line('chest2', cr_, pl_, 6, 0.045, 0.014)

out = {}
for name, (vs, ns_, ixs, joint) in sets.items():
    V = np.concatenate(vs); N = np.concatenate(ns_); I = np.concatenate(ixs)
    Vl = V; Nl = N  # accessor space == glTF world space (measured: hand centroid ~= joint world)
    out[name] = (Vl.astype('float32'), Nl.astype('float32'), I.astype('uint32'))
    print(name, "verts", len(Vl))
np.savez(base + '/_df_tools/chains.npz',
         **{k: v[0] for k, v in out.items()},
         **{k+'_n': v[1] for k, v in out.items()},
         **{k+'_i': v[2] for k, v in out.items()},
         **{k+'_j': np.array(v if isinstance(v, str) else 'split') for k, v in
            [(n, sets[n][3]) for n in out]})
joints = {n: (sets[n][3] if isinstance(sets[n][3], str) else sets[n][3][1] + '|' + sets[n][3][2]) for n in out}
np.savez(base + '/_df_tools/chains_joints.npz', **{k: np.array(v) for k, v in joints.items()})
np.savez(base + '/_df_tools/chains_meta.npz', aL_local=aL, aR_local=aR)
print("saved chains npz; aL", aL, "aR", aR)
