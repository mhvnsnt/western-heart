#!/usr/bin/env python3
"""Tearing check: CPU-skin every skinned primitive at one clip frame and report the worst
triangle-edge stretch (posed length / rest length, edges >= 5 mm). A clean skin stays near 1.

usage: stretch_check.py file.glb clip [frame]"""
import sys
import numpy as np
from swap_lr_joints import load, view


def qm(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def main():
    f, clip = sys.argv[1], sys.argv[2]
    t = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    j, b = load(f)
    N = j["nodes"]
    par = {c: i for i, n in enumerate(N) for c in n.get("children", [])}
    a = next(x for x in j["animations"] if x["name"] == clip)
    ch = {"rotation": {}, "translation": {}, "scale": {}}
    for c in a["channels"]:
        v = view(j, b, a["samplers"][c["sampler"]]["output"])[2] if j["accessors"][a["samplers"][c["sampler"]]["output"]]["type"] != "SCALAR" else None
        if v is not None: ch[c["target"]["path"]][c["target"]["node"]] = v[min(t, len(v) - 1)]
    def loc(i):
        n = N[i]; M = np.eye(4)
        M[:3, :3] = qm(ch["rotation"].get(i, n.get("rotation", [0, 0, 0, 1]))) @ np.diag(ch["scale"].get(i, n.get("scale", [1, 1, 1])))
        M[:3, 3] = ch["translation"].get(i, n.get("translation", [0, 0, 0])); return M
    memo = {}
    def W(i):
        if i not in memo: memo[i] = (W(par[i]) if i in par else np.eye(4)) @ loc(i)
        return memo[i]
    sk = j["skins"][0]
    ibm = view(j, b, sk["inverseBindMatrices"])[2].reshape(-1, 4, 4).transpose(0, 2, 1)
    Mj = np.array([W(i) @ ibm[k] for k, i in enumerate(sk["joints"])])
    worst = []
    for mi, n in enumerate(N):
        if "mesh" not in n: continue
        for pr in j["meshes"][n["mesh"]]["primitives"]:
            at = pr["attributes"]
            if "JOINTS_0" not in at or "indices" not in pr: continue
            P = view(j, b, at["POSITION"])[2]; J = view(j, b, at["JOINTS_0"])[2].astype(int); Wt = view(j, b, at["WEIGHTS_0"])[2]
            Ph = np.c_[P, np.ones(len(P))]
            S = np.einsum("vk,vkij,vj->vi", Wt, Mj[J], Ph)[:, :3]
            I = view(j, b, pr["indices"])[2] if False else None
            A = j["accessors"][pr["indices"]]; bv = j["bufferViews"][A["bufferView"]]
            dt = {5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[A["componentType"]]
            o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
            I = np.frombuffer(bytes(b[o:o + np.dtype(dt).itemsize * A["count"]]), dt).reshape(-1, 3)
            r = []
            for e0, e1 in ((0, 1), (1, 2), (2, 0)):
                l0 = np.linalg.norm(P[I[:, e0]] - P[I[:, e1]], axis=1); l1 = np.linalg.norm(S[I[:, e0]] - S[I[:, e1]], axis=1)
                r.append(l1[l0 > 5e-3] / l0[l0 > 5e-3])
            r = np.concatenate(r)
            worst.append((float(r.max()), float(np.percentile(r, 99.9)), n["name"]))
    worst.sort(reverse=True)
    for w in worst[:4]: print(f"  max stretch {w[0]:7.2f}  p99.9 {w[1]:5.2f}  {w[2]}")
    print(f"WORST {worst[0][0]:.2f}")


if __name__ == "__main__":
    main()
