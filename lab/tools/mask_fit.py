#!/usr/bin/env python3
"""Bannon mask: fit per-skeleton head-socket presets, check follow/clip/pop, render proof sheet.

Socket = the rig's head bone. Preset = local transform (offset, rotation quat xyzw, uniform
scale) of the mask relative to that bone's rest frame, so it works for world-aligned
(canonical) and oriented (Mixamo/Bannon) joints alike.
Usage: mask_fit.py manifest.json proof.png
"""
import json, sys
from pathlib import Path
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf_eval import Gltf, qmat
from mesh_info import load
from clips import quat
LAB = Path(__file__).resolve().parents[1]
MASK = LAB / "game/attire/bannon_mask/bannon_mask.glb"
RIGS = [
    ("wh_canonical_t3", LAB / "game/assets/t3_king.glb", "Head", np.array([0, 0, 1.0]), True),
    ("wh_canonical_autorig", LAB / "game/assets/pantera_leoman.glb", "Head", np.array([0, 0, 1.0]), True),
    ("mixamo", LAB.parent / "game/assets/models/pantera.glb", "Head", None, False),
    ("bannon_mixamo58", Path("/workspace/western-heart-lab/src/BANNON_rigged.glb"), "mixamorig:Head", None, False),
]
_, MP, MT = load(MASK)
MASK_TO_Z = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], float)
MPz = MP @ MASK_TO_Z.T; MASK_H = np.ptp(MPz[:, 1])

def head_info(g, bone):
    ms = g.skinned_meshes(); m = dict(ms[0])
    if len(ms) > 1:
        off = np.cumsum([0] + [len(x["pos"]) for x in ms[:-1]])
        m = {"node": ms[0]["node"], "skin": ms[0]["skin"], "pos": np.concatenate([x["pos"] for x in ms]), "joints": np.concatenate([x["joints"] for x in ms]),
             "weights": np.concatenate([x["weights"] for x in ms]), "idx": np.concatenate([x["idx"] + o for x, o in zip(ms, off)])}
    sk = g.j["skins"][m["skin"]]
    names = [g.nodes[j].get("name") for j in sk["joints"]]; hi = names.index(bone)
    rest = g.skin_pose(m)
    m["bind_ok"] = bool(np.abs(rest - m["pos"]).max() < 1e-3 * max(1.0, np.abs(m["pos"]).max())) or len(g.j.get("animations", [])) > 0
    if not m["bind_ok"]: rest = m["pos"].copy()   # broken bind: fit to the authored mesh
    dom = m["joints"][np.arange(len(m["joints"])), m["weights"].argmax(1)]
    hv = rest[dom == hi]; W = g.world(); hb = W[sk["joints"][hi]]
    return m, sk, hi, rest, dom, hv, hb

def fit(rid, path, bone, facing):
    g = Gltf(path); m, sk, hi, rest, dom, hv, hb = head_info(g, bone)
    H = np.ptp(rest[:, 1])
    if facing is None:
        nm = [g.nodes[j].get("name", "") for j in sk["joints"]]; W = g.world()
        toe = [W[sk["joints"][i]][:3, 3] for i, n in enumerate(nm) if n.endswith("LeftToeBase")]
        foot = [W[sk["joints"][i]][:3, 3] for i, n in enumerate(nm) if n.endswith("LeftFoot")]
        f = (toe[0] - foot[0]) if toe and foot else np.array([0, 0, 1.0]); f[1] = 0; facing = f / np.linalg.norm(f)
    yaw = np.arctan2(facing[0], facing[2]); c, s = np.cos(yaw), np.sin(yaw); Rw = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    hh = max(np.ptp(hv[:, 1]), 0.10 * H) if len(hv) else 0.13 * H
    centre = (hv.min(0) + hv.max(0)) / 2 if len(hv) else hb[:3, 3] + [0, 0.06 * H, 0]
    scale = 1.18 * hh / MASK_H
    world_pos = centre + Rw @ np.array([0, 0.0, 0.02 * hh])
    sb = np.linalg.norm(hb[:3, 0]); Rb = hb[:3, :3] / sb
    off = Rb.T @ (world_pos - hb[:3, 3]) / sb
    rot = Rb.T @ Rw @ MASK_TO_Z
    return {"rig": rid, "bone": bone, "offset": [round(float(x), 5) for x in off], "rotation": [round(float(x), 6) for x in quat(rot)],
            "scale": round(float(scale / sb), 6), "fit": {"head_height_m": round(float(hh), 4), "rig_height_m": round(float(H), 3)}}

def mask_world(g, sk, hi, preset, over=None):
    hb = g.world(over)[sk["joints"][hi]]
    L = np.eye(4); L[:3, :3] = qmat(preset["rotation"]) * preset["scale"]; L[:3, 3] = preset["offset"]
    M = hb @ L
    return MP @ M[:3, :3].T + M[:3, 3], M

def check(path, bone, preset, clips=("idle", "walk_fwd", "light", "medium", "heavy", "hit", "block")):
    g = Gltf(path); m, sk, hi, rest, dom, hv, hb = head_info(g, bone)
    names = [a["name"] for a in g.j.get("animations", [])]
    neck = [k for k, j in enumerate(sk["joints"]) if g.nodes[j].get("name", "").endswith("Neck")]
    body = ~np.isin(dom, [hi] + neck)
    def inside(P, M):
        loc = (np.c_[P[body], np.ones(body.sum())] @ np.linalg.inv(M).T)[:, :3]
        return (np.abs(loc - cen) < half).all(1)
    rep = {"frames": 0, "max_relative_drift": 0.0, "max_step_m": 0.0, "max_body_verts_inside": 0}
    lo, hi_ = MP.min(0), MP.max(0); cen = (lo + hi_) / 2; half = (hi_ - lo) / 2 * 0.85
    base = inside(rest, mask_world(g, sk, hi, preset, None)[1]); rep["static_overlap_verts"] = int(base.sum())
    for c in clips:
        if c not in names: continue
        ai = names.index(c); L = g.anim_len(ai); prev = None
        for t in np.arange(0, L + 1e-6, 1 / 60):
            over = g.sample(ai, t); P = g.skin_pose(m, over)
            mw, M = mask_world(g, sk, hi, preset, over)
            rel = np.linalg.inv(g.world(over)[sk["joints"][hi]]) @ M
            if prev is not None:
                rep["max_relative_drift"] = max(rep["max_relative_drift"], float(np.abs(rel - prev[0]).max()))
                rep["max_step_m"] = max(rep["max_step_m"], float(np.linalg.norm(mw.mean(0) - prev[1])))
            prev = (rel, mw.mean(0))
            rep["max_body_verts_inside"] = max(rep["max_body_verts_inside"], int((inside(P, M) & ~base).sum())); rep["frames"] += 1
    rep["pop_ok"] = rep["max_relative_drift"] < 1e-5 and rep["max_step_m"] < 0.12
    rep["clip_ok"] = rep["max_body_verts_inside"] <= max(20, int(0.002 * body.sum()))
    rep["pass"] = rep["pop_ok"] and rep["clip_ok"]
    return rep

def render(entries, out):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    cols = []
    for rid, path, bone, preset, specs in entries:
        g = Gltf(path); names = [a["name"] for a in g.j.get("animations", [])]
        for sp in specs:
            over = None if sp == "rest" else g.sample(names.index(sp.split(":")[0]), float(sp.split(":")[1]))
            cols.append((rid, g, bone, preset, sp, over))
    fig = plt.figure(figsize=(2.6 * len(cols), 6.2))
    for c, (rid, g, bone, preset, sp, over) in enumerate(cols):
        m, sk, hi, rest, dom, hv, hb = head_info(g, bone); P = g.skin_pose(m, over) if m["bind_ok"] else rest; mw, _ = mask_world(g, sk, hi, preset, over)
        lo = P.min(0); hi_ = P.max(0); cen = (lo + hi_) / 2; r = max(hi_ - lo) / 2
        for row, (el, az) in enumerate(((8, -60), (8, 20))):
            ax = fig.add_subplot(2, len(cols), row * len(cols) + c + 1, projection="3d")
            tri = m["idx"].reshape(-1, 3)[::2]
            ax.add_collection3d(Poly3DCollection(P[tri][:, :, [0, 2, 1]], facecolor=(0.75, 0.65, 0.5), edgecolor="none", alpha=0.9))
            ax.add_collection3d(Poly3DCollection(mw[MT[::3]][:, :, [0, 2, 1]], facecolor=(0.85, 0.1, 0.1), edgecolor="none"))
            ax.set_xlim(cen[0] - r, cen[0] + r); ax.set_ylim(cen[2] - r, cen[2] + r); ax.set_zlim(cen[1] - r, cen[1] + r)
            ax.view_init(el, az); ax.set_axis_off(); ax.set_title(f"{rid}\n{sp}", fontsize=7)
    plt.tight_layout(); plt.savefig(out, dpi=75)

if __name__ == "__main__":
    man = json.load(open(sys.argv[1])); presets = {}; checks = {}
    for rid, path, bone, facing, anim in RIGS:
        if not Path(path).exists(): continue
        p = fit(rid, path, bone, facing); presets[rid] = p
        if anim: checks[rid] = check(path, bone, p)
        print(rid, json.dumps(p["fit"]), checks.get(rid))
    man["presets"] = presets; man["follow_checks"] = checks
    json.dump(man, open(sys.argv[1], "w"), indent=1)
    if len(sys.argv) > 2:
        ents = [(rid, path, bone, presets[rid], ["idle:0.5", "walk_fwd:0.2", "light:0.45"] if anim else ["rest"]) for rid, path, bone, facing, anim in RIGS if rid in presets]
        render(ents, sys.argv[2])
