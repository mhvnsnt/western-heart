#!/usr/bin/env python3
"""Round 11 Job 2 overlay: idx00 slot-10 mesh points + corrected (r11)
skeleton joints/edges, front view; also r10-convention joints for contrast."""
import struct, sys, os, json, math, glob, importlib.util
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'
spec = importlib.util.spec_from_file_location('j2f', '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round11-evidence/j2_followup.py')
# reuse parse/compose by exec of the file's defs only: simpler to re-define imports
sys.path.insert(0, '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools')
spec9 = importlib.util.spec_from_file_location('r9', '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/r9_ndpp_decode.py')
r9 = importlib.util.module_from_spec(spec9); spec9.loader.exec_module(r9)

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

def get_slot(data, k):
    off, sz = slots_of(data)[k]; return data[off:off + sz]

def glb_world(path):
    d = open(path, 'rb').read()
    ln, typ = struct.unpack_from('<II', d, 12)
    g = json.loads(d[20:20 + ln]); nodes = g['nodes']
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []): parent[c] = i
    def q2R(q):
        x, y, z, w = q
        return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    W = [None] * len(nodes)
    def solve(i):
        if W[i] is not None: return W[i]
        nd = nodes[i]
        t = nd.get('translation', [0,0,0]); q = nd.get('rotation', [0,0,0,1]); s = nd.get('scale', [1,1,1])
        R = q2R(q); M = [[R[r][c]*s[c] for c in range(3)] for r in range(3)]
        if i not in parent: W[i] = (M, tuple(t))
        else:
            Mp, tp = solve(parent[i])
            Mw = [[sum(Mp[r][k]*M[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
            tw = tuple(tp[r] + sum(Mp[r][k]*t[k] for k in range(3)) for r in range(3))
            W[i] = (Mw, tw)
        return W[i]
    for i in range(len(nodes)): solve(i)
    return [w[1] for w in W], parent, [nd.get('name') for nd in nodes]

data = open(os.path.join(DEC, 'idx00_entry454.bin'), 'rb').read()
verts, tris, *_ = r9.decode_mesh(get_slot(data, 10))
M = '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/models'
w_new, parent, names = glb_world(os.path.join(M, 'idx00_skeleton_r11.glb'))
w_old, _, _ = glb_world(os.path.join(M, 'idx00_skeleton_r10.glb'))

fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharex=True, sharey=True)
for ax, W, title in ((axes[0], w_old, 'r10 shipped GLB walk (TRS compounding)'),
                     (axes[1], w_new, 'r11 corrected GLB walk (TR bind pose)')):
    ax.scatter([v[0] for v in verts], [v[1] for v in verts], s=2, c='#888888', alpha=0.5)
    for i, p in parent.items():
        ax.plot([W[p][0], W[i][0]], [W[p][1], W[i][1]], c='#d62728', lw=0.7)
    ax.scatter([w[0] for w in W], [w[1] for w in W], s=6, c='#d62728')
    ax.set_title(title, fontsize=10); ax.set_aspect('equal'); ax.grid(alpha=0.3)
    ax.axhline(0, c='k', lw=0.5)
plt.tight_layout()
out = '/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round11-evidence/r11_idx00_skeleton_overlay.png'
plt.savefig(out, dpi=110)
print('saved', out)
ashi = names.index('ASHI_R_jnt')
print('r10 walk ASHI_R y =', round(w_old[ashi][1], 1), '| r11 walk ASHI_R y =', round(w_new[ashi][1], 1))
