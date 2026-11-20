"""Render skinned GLB poses (front + side) to PNG with matplotlib. preview.py model.glb out.png [clip:t ...]"""
import sys, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0, __file__.rsplit("/", 1)[0]); from gltf_eval import Gltf
g = Gltf(sys.argv[1]); names = [a["name"] for a in g.j.get("animations", [])]
specs = sys.argv[3:] or ["rest"]
fig = plt.figure(figsize=(3 * len(specs), 6))
for c, sp in enumerate(specs):
    over = None
    if sp != "rest":
        n, t = sp.split(":"); over = g.sample(names.index(n), float(t))
    for m in g.skinned_meshes():
        P = g.skin_pose(m, over); tri = m["idx"].reshape(-1, 3)
        for r, (el, az) in enumerate(((5, -90), (5, 0))):
            ax = fig.add_subplot(2, len(specs), r * len(specs) + c + 1, projection="3d")
            ax.add_collection3d(Poly3DCollection(P[tri][:, :, [0, 2, 1]], facecolor="tan", edgecolor="k", linewidths=0.1))
            ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(0, 2); ax.view_init(el, az); ax.set_title(sp, fontsize=8); ax.set_box_aspect((1, 1, 1))
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=70)
