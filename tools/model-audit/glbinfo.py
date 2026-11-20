"""GLB summary

Nodes, skins, animation names and joint names of one GLB.
Usage: python3 tools/model-audit/glbinfo.py MODEL.glb

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys, pygltflib, numpy as np
g = pygltflib.GLTF2().load(sys.argv[1])
print('nodes', len(g.nodes), 'skins', len(g.skins), 'anims', [a.name for a in g.animations][:40])
names = {i:n.name for i,n in enumerate(g.nodes)}
parent = {}
for i,n in enumerate(g.nodes):
    for c in (n.children or []): parent[c]=i
if g.skins:
    s=g.skins[0]
    print('skin joints', len(s.joints))
    for j in s.joints[:60]:
        n=g.nodes[j]
        print(f"  {n.name:30s} parent={names.get(parent.get(j))!s:28s} t={np.round(n.translation,3).tolist() if n.translation else None} r={np.round(n.rotation,3).tolist() if n.rotation else None} s={n.scale}")
# root nodes
sc = g.scenes[g.scene or 0]
for r in sc.nodes:
    n=g.nodes[r]; print('root', n.name, n.translation, n.rotation, n.scale, n.children)
