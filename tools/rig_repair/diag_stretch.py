#!/usr/bin/env python3
"""diag_stretch.py - find WHERE the worst stretch happens: rest position +
top weighted bones of the most-stretched edges under a clip."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "rigcheck"))
from rig_check import Character, Clip, apply_clip  # noqa: E402
import tempfile

MODEL = sys.argv[1]; CLIP = sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 20
tmp = tempfile.mkdtemp()
ch = Character(MODEL, tmp); ch.retarget = "aligned"; ch.facing_axis = "+X"
c = Clip("jab", CLIP, tmp)

# frame of max stretch
ts = np.linspace(0, c.dur, 16)
worst = (0, None, None)
for t in ts:
    V, W, _ = apply_clip(ch, c, float(t))
    for k, d in enumerate(V):
        e, L0 = ch.edges[k]
        r = np.linalg.norm(d[e[:, 0]] - d[e[:, 1]], axis=1) / np.maximum(L0, 1e-9)
        m = r.max()
        if m > worst[0]:
            worst = (m, float(t), k)
print(f"worst stretch {worst[0]:.1f} at t={worst[1]:.2f} prim {worst[2]}")
V, W, _ = apply_clip(ch, c, worst[1])
k = worst[2]; d = ch.m.prims[k]
e, L0 = ch.edges[k]
P0 = ch.V0[k]
r = np.linalg.norm(V[k][e[:, 0]] - V[k][e[:, 1]], axis=1) / np.maximum(L0, 1e-9)
top = np.argsort(-r)[:N]
Jn = [ch.g.name[i] for i in ch.m.skins[d["skin"]]["joints"]] if d.get("skin") is not None else []
print(f"{'edge':>6} {'ratio':>7} {'rest_mid':>28} top bones")
for i in top:
    a, b = e[i]
    mid = (P0[a] + P0[b]) / 2
    # weights of vert a
    if "J" in d:
        ji = d["J"][a]; w = d["W"][a]
        o = np.argsort(-w)[:3]
        bones = ",".join(f"{Jn[ji[x]].split(':')[-1]}:{w[x]:.2f}" for x in o if w[x] > 0.01)
    else:
        bones = "-"
    print(f"{i:6d} {r[i]:7.1f} ({mid[0]:+.2f},{mid[1]:+.2f},{mid[2]:+.2f}) {bones}")
import shutil; shutil.rmtree(tmp, ignore_errors=True)
