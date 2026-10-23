#!/usr/bin/env python3
"""tools/model-audit/rig_overlay.py — bind-pose overlay: the mesh with its skeleton drawn on top.

Owner 2026-10-22: "Need to get the bind pose overlays and heat mapping and skinning and rigging ... fully done
for every character every glb model". One image per model, front (X-Y) and side (Z-Y) views of the bind pose:
mesh vertices coloured by their dominant bone (the weight map), bones as black lines, Left* joints red and
Right* joints blue. A skeleton outside its mesh, a backwards toe, a Left bone in the right limb or a hand
weighted to the tail is visible at a glance.

    python3 tools/model-audit/rig_overlay.py OUT.png MODEL.glb [--fit fit.json]

--fit draws the joints from a tools/auto_rig/refit_skeleton.py result (green) over the model's own skeleton.
Plain glTF only (decode meshopt first).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig_qa as R  # noqa: E402


def skeleton(js, blob):
    sk = js["skins"][0]
    joints = sk["joints"]
    ibm = R.accessor(js, blob, sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    jpos = np.array([np.linalg.inv(m)[:3, 3] for m in ibm])
    cn = [R.canon(js["nodes"][j].get("name", "")) for j in joints]
    par = {}
    for i, j in enumerate(joints):
        for c in js["nodes"][j].get("children", []):
            if c in joints:
                par[joints.index(c)] = i
    return jpos, cn, par


def mesh(js, blob):
    V, D = [], []
    for nd in js["nodes"]:
        if "mesh" not in nd or nd.get("skin") is None:
            continue
        for pr in js["meshes"][nd["mesh"]]["primitives"]:
            at = pr["attributes"]
            if "JOINTS_0" not in at:
                continue
            V.append(R.accessor(js, blob, at["POSITION"]))
            jt = R.accessor(js, blob, at["JOINTS_0"]).astype(int)
            wt = R.accessor(js, blob, at["WEIGHTS_0"])
            D.append(jt[np.arange(len(jt)), wt.argmax(1)])
    return np.vstack(V), np.concatenate(D)


def draw(out, path, fit=None, title=None):
    js, blob = R.read_glb(path)
    jpos, cn, par = skeleton(js, blob)
    V, D = mesh(js, blob)
    s = np.linspace(0, len(V) - 1, min(len(V), 50000)).astype(int)
    cmap = plt.get_cmap("tab20")
    fig, axes = plt.subplots(1, 2, figsize=(13, 7.5))
    for ax, (a, lab) in zip(axes, ((0, "front X-Y (+X = image right)"), (2, "side Z-Y (+Z = image right)"))):
        ax.scatter(V[s, a], V[s, 1], s=0.25, c=[cmap(d % 20) for d in D[s]], alpha=0.45, linewidths=0)
        for c, p in par.items():
            ax.plot([jpos[c, a], jpos[p, a]], [jpos[c, 1], jpos[p, 1]], "k-", lw=1.4)
        for i, n in enumerate(cn):
            col = "red" if n.startswith("Left") else "blue" if n.startswith("Right") else "black"
            ax.plot(jpos[i, a], jpos[i, 1], "o", ms=2.5, color=col)
            if n in ("LeftHand", "RightHand", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase", "Head",
                     "Hips", "LeftForeArm", "RightForeArm", "LeftLeg", "RightLeg", "Tail4"):
                ax.annotate(n, (jpos[i, a], jpos[i, 1]), fontsize=7, color=col)
        if fit:
            F = {j["name"]: np.array(j["pos"]) for j in fit["joints"]}
            for j in fit["joints"]:
                if j["parent"] in F:
                    p = F[j["parent"]]
                    ax.plot([j["pos"][a], p[a]], [j["pos"][1], p[1]], "-", color="limegreen", lw=1.8)
            for nm, t in fit.get("leaf_tail", {}).items():
                ax.plot([F[nm][a], t[a]], [F[nm][1], t[1]], "-", color="limegreen", lw=1.8)
        ax.set_aspect("equal")
        ax.set_title(lab, fontsize=9)
    fig.suptitle(title or os.path.relpath(path), fontsize=10)
    plt.tight_layout()
    plt.savefig(out, dpi=80)
    plt.close(fig)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    fit = json.load(open(sys.argv[sys.argv.index("--fit") + 1])) if "--fit" in sys.argv else None
    if fit:
        a = [x for x in a if x != sys.argv[sys.argv.index("--fit") + 1]]
    draw(a[0], a[1], fit)
    print(a[0])


if __name__ == "__main__":
    main()
