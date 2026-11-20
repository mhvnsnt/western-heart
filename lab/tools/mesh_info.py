"""Static (unskinned) GLB inspection: world-space verts/tris/bbox and a 3-view PNG."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, __file__.rsplit("/", 1)[0]); from gltf_eval import Gltf
def load(path):
    g = Gltf(path); W = g.world(); P, T = [], []; base = 0
    for ni, n in enumerate(g.nodes):
        if "mesh" not in n: continue
        for pr in g.j["meshes"][n["mesh"]]["primitives"]:
            p = g.acc(pr["attributes"]["POSITION"]).astype(float); p = (np.c_[p, np.ones(len(p))] @ W[ni].T)[:, :3]
            t = g.acc(pr["indices"])[:, 0].reshape(-1, 3) + base; base += len(p); P.append(p); T.append(t)
    return g, np.concatenate(P), np.concatenate(T)
if __name__ == "__main__":
    g, P, T = load(sys.argv[1])
    print("verts", len(P), "tris", len(T), "min", P.min(0).round(3), "max", P.max(0).round(3), "skins", len(g.j.get("skins", [])))
    if len(sys.argv) > 2:
        fig, ax = plt.subplots(1, 3, figsize=(12, 4))
        for a, (i, j, n) in zip(ax, ((0, 1, "front X/Y"), (2, 1, "side Z/Y"), (0, 2, "top X/Z"))):
            a.scatter(P[::3, i], P[::3, j], s=0.2, c=P[::3, 2 if i != 2 else 0], cmap="viridis"); a.set_aspect("equal"); a.set_title(n)
        plt.tight_layout(); plt.savefig(sys.argv[2], dpi=60)
