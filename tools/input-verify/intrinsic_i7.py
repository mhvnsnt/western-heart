#!/usr/bin/env python3
"""Item 7 diagnostic 2: INTRINSIC swing of each effective stance clip on its own
source skeleton (identity rest rotations, rest positions from skeleton.json),
composed with the game's own FK convention (bankFacing in t3anims.js):
G(j) = G(parent) * q(j). Reports, per side: shoulder WORLD angle vs bind,
shoulder LOCAL angle vs bind, and Chest WORLD angle — at the gate's sample
time (0.05 s) and as whole-clip max/mean."""
import json, math, sys, urllib.request

BASE = 'http://127.0.0.1:8841/game/'
CASES = {
    # fighter: (skeleton path, stance clip path, kind)
    'pantera':    ('assets/anim/t7/king/skeleton.json',       'assets/anim/t7/king/stance.json', 'T7'),
    'pond':       ('assets/anim/t7/raven/skeleton.json',      'assets/anim/t7/raven/stance.json', 'T7'),
    'ryusan':     ('assets/anim/t7/luckychloe/skeleton.json', 'assets/anim/t7/luckychloe/stance.json', 'T7'),
    'tobi':       ('assets/anim/t7/hwoarang/skeleton.json',   'assets/anim/t7/hwoarang/stance.json', 'T7'),
    'negativo':   ('assets/anim/t7/negan/skeleton.json',      'assets/anim/t7/negan/stance.json', 'T7'),
    'purplerain': ('assets/anim/t7/lee/skeleton.json',        'assets/anim/t7/lee/stance.json', 'T7'),
    'demonio':    ('assets/anim/t3/jin/skeleton.json',        'assets/anim/t3/jin/t3_neutral.json', 'T3'),
    'megami':     ('assets/anim/t3/jun/skeleton.json',        'assets/anim/t3/jun/t3_neutral.json', 'T3'),
    'menajerii':  ('assets/anim/t3/roger/skeleton.json',      'assets/anim/t3/roger/t3_neutral.json', 'T3'),
    'chatur':     ('assets/anim/t3/ogre/skeleton.json',       'assets/anim/t3/ogre/t3_neutral.json', 'T3'),
    'star':       ('assets/anim/t3/xiaoyu/skeleton.json',     'assets/anim/t3/xiaoyu/t3_neutral.json', 'T3'),
    'awapop':     ('assets/anim/t3/nina/skeleton.json',       'assets/anim/t3/nina/t3_neutral.json', 'T3'),
}

def fetch(p):
    with urllib.request.urlopen(BASE + p, timeout=120) as r:
        return json.loads(r.read().decode())

def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return [aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw,
            aw*bw - ax*bx - ay*by - az*bz]

def ang(q):
    w = min(1.0, abs(q[3]))
    return 2 * math.acos(w)

def measure(fid, skel_p, clip_p, kind):
    skel = fetch(skel_p); data = fetch(clip_p)
    joints = skel['joints']; order = [j['name'] for j in joints]
    par = {j['name']: j['parent'] for j in joints}
    rot = data['rot_xyzw']; fps = data.get('fps', 30.0)
    n = max((len(v) for v in rot.values() if v), default=0)
    f_gate = min(n - 1, max(0, round(0.05 * fps)))
    rows = []
    for f in range(n):
        G = {}
        for name in order:
            arr = rot.get(name)
            q = arr[min(f, len(arr) - 1)] if arr else [0, 0, 0, 1]
            p = par[name]
            G[name] = qmul(G[p], q) if p and p in G else list(q)
        rows.append({
            'Lw': ang(G['LeftShoulder']), 'Rw': ang(G['RightShoulder']),
            'Ll': ang(rot['LeftShoulder'][min(f, len(rot['LeftShoulder']) - 1)]) if 'LeftShoulder' in rot else None,
            'Rl': ang(rot['RightShoulder'][min(f, len(rot['RightShoulder']) - 1)]) if 'RightShoulder' in rot else None,
            'chestW': ang(G['Chest']) if 'Chest' in G else None,
        })
    def agg(key):
        vals = [r[key] for r in rows if r[key] is not None]
        return {'gate': round(rows[f_gate][key], 2), 'max': round(max(vals), 2), 'mean': round(sum(vals) / len(vals), 2)} if vals else None
    out = {'fighter': fid, 'kind': kind, 'frames': n, 'fps': fps, 'gateFrame': f_gate,
           'worldL': agg('Lw'), 'worldR': agg('Rw'), 'localL': agg('Ll'), 'localR': agg('Rl'), 'chestWorld': agg('chestW')}
    print(json.dumps(out), flush=True)
    return out

results = {}
for fid, (s, c, k) in CASES.items():
    if len(sys.argv) > 1 and fid not in sys.argv[1].split(','):
        continue
    try:
        results[fid] = measure(fid, s, c, k)
    except Exception as e:
        print(fid, 'ERROR', str(e)[:160], flush=True)
json.dump(results, open('intrinsic-i7.json', 'w'), indent=1)
print('saved intrinsic-i7.json')
