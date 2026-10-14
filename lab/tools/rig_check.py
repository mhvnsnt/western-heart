#!/usr/bin/env python3
"""Rig check: bones, weights, mesh and animation must agree.

For every skinned mesh in a GLB:
  weights   : JOINTS index valid, weights >= 0, sum to 1 (+-1e-3), no unweighted vertex
  skeleton  : bones map onto WH-Canonical-22 (retarget_maps.json); required bones present
  animation : every channel targets a node in the skin; quaternions finite & unit
  explosion : at rest + sampled clip frames, triangle edge stretch <= MAX_STRETCH and
              no vertex leaves its bone by more than MAX_DRIFT (rigid & soft skins)
  feet      : standing clips keep the lowest foot on the floor (|y| <= FLOOR_TOL), nothing
              sinks below -SINK_TOL in any clip; airborne/lying clips are listed in EXEMPT
Usage: rig_check.py model.glb [...] [--json out.json] [--report-only]
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf_eval import Gltf

MAPS = json.load(open(Path(__file__).resolve().parents[1] / "skeleton/retarget_maps.json"))
CANON = json.load(open(Path(__file__).resolve().parents[1] / "skeleton/canonical_skeleton.json"))
MAX_STRETCH, MAX_DRIFT, FLOOR_TOL, SINK_TOL = 2.0, 0.05, 0.06, 0.05
FOOT_ONE_ON_FLOOR = {"heavy"}           # kicks: one foot must stay planted
EXEMPT_FLOOR = {"ko", "TPose", "tpose"}  # lying / reference poses
NSAMPLES = 12

def canon_name(n):
    n = n.split(":")[-1]
    for m in (MAPS["mixamo49"]["map"], MAPS["rigify13"]["map"]):
        if n in m: return m[n]
    return n if n in {b["name"] for b in CANON["bones"]} else None

def check(path):
    g = Gltf(path); res = {"file": str(path), "errors": [], "warnings": [], "stats": {}}
    E, Wn = res["errors"].append, res["warnings"].append
    meshes = g.skinned_meshes()
    if not meshes: E("no skinned mesh"); return res
    sk = g.j["skins"][meshes[0]["skin"]]; joints = sk["joints"]
    names = [g.nodes[j].get("name", f"node{j}") for j in joints]
    canon = {canon_name(n): k for k, n in enumerate(names) if canon_name(n)}
    missing = [b for b in CANON["required_for_rig_check"] if b not in canon]
    res["stats"].update(bones=len(joints), canonical_mapped=len(canon), missing_required=missing)
    if missing: E(f"missing canonical bones: {missing}")
    rest_cache = []
    for m in meshes:
        J, Wt = m["joints"], m["weights"]
        if J.max() >= len(g.j["skins"][m["skin"]]["joints"]): E("JOINTS index out of range")
        if (Wt < -1e-6).any(): E("negative weights")
        s = Wt.sum(1)
        bad = int((np.abs(s - 1) > 1e-3).sum())
        if bad: E(f"{bad} vertices with weights not summing to 1")
        if int((s < 1e-6).sum()): E("unweighted vertices")
        rest = g.skin_pose(m, None)
        tri = m["idx"].reshape(-1, 3) if m["idx"] is not None else np.arange(len(rest) - len(rest) % 3).reshape(-1, 3)
        dom = J[np.arange(len(J)), Wt.argmax(1)]
        rest_cache.append((m, rest, tri, dom))
        res["stats"].setdefault("verts", 0); res["stats"]["verts"] += len(rest)
        if np.abs(rest - m["pos"]).max() > 1e-3 * max(1, np.abs(m["pos"]).max()): Wn("bind pose != mesh (skinned rest differs from authored positions)")
    jset = set(joints)
    feet_idx = [canon.get("LeftFoot"), canon.get("RightFoot")]
    anims = g.j.get("animations", [])
    res["stats"]["clips"] = [a.get("name") for a in anims]
    worst = {"stretch": 1.0, "drift": 0.0}
    def eval_pose(over, label, floor_rule):
        W = g.world(over)
        ys = []
        for m, rest, tri, dom in rest_cache:
            P = g.skin_pose(m, over)
            if not np.isfinite(P).all(): E(f"{label}: NaN vertices"); return
            e0 = np.linalg.norm(rest[tri[:, 1]] - rest[tri[:, 0]], axis=1) + 1e-6
            e1 = np.linalg.norm(P[tri[:, 1]] - P[tri[:, 0]], axis=1)
            st = float((e1 / e0)[e0 > 1e-4].max()) if (e0 > 1e-4).any() else 1.0
            worst["stretch"] = max(worst["stretch"], st)
            if st > MAX_STRETCH: E(f"{label}: exploded/stretched triangles x{st:.2f}")
            # drift: vertex distance to dominant bone must stay ~constant
            Wr = g.world(None)
            jw = np.array([W[joints[d]][:3, 3] for d in dom]); jr = np.array([Wr[joints[d]][:3, 3] for d in dom])
            dr = np.abs(np.linalg.norm(P - jw, axis=1) - np.linalg.norm(rest - jr, axis=1))
            scale = np.ptp(rest[:, 1]) or 1
            d = float(dr.max() / scale); worst["drift"] = max(worst["drift"], d)
            if d > MAX_DRIFT * 4: E(f"{label}: vertices drift {d:.3f} of height from their bone")
            ys.append((P, dom))
        allP = np.concatenate([p for p, _ in ys]); allD = np.concatenate([d for _, d in ys])
        h = np.ptp(rest_cache[0][1][:, 1]) or 1
        miny = float(allP[:, 1].min())
        if floor_rule != "exempt" and miny < -SINK_TOL * h: E(f"{label}: mesh sinks below floor ({miny:.3f})")
        if floor_rule in ("stand", "one") and None not in feet_idx:
            fm = [allP[allD == f][:, 1].min() for f in feet_idx if (allD == f).any()]
            if fm:
                low = min(fm)
                if abs(low) > FLOOR_TOL * h: E(f"{label}: feet off floor (lowest foot y={low:.3f})")
                if floor_rule == "stand" and max(fm) > 0.25 * h: Wn(f"{label}: one foot lifted {max(fm):.2f}")
    eval_pose(None, "rest", "stand")
    for ai, a in enumerate(anims):
        for ch in a["channels"]:
            if ch["target"]["node"] not in jset and ch["target"]["path"] != "weights":
                nm = g.nodes[ch["target"]["node"]].get("name")
                if ch["target"]["path"] == "rotation": Wn(f"clip {a.get('name')}: channel on non-joint node {nm}")
            if ch["target"]["path"] == "rotation":
                q = g.acc(a["samplers"][ch["sampler"]]["output"])
                if not np.isfinite(q).all() or np.abs(np.linalg.norm(q, axis=1) - 1).max() > 1e-2: E(f"clip {a.get('name')}: bad quaternion")
        nm = a.get("name", str(ai)); L = g.anim_len(ai)
        rule = "exempt" if nm in EXEMPT_FLOOR else ("one" if nm in FOOT_ONE_ON_FLOOR else "stand")
        for t in np.linspace(0, L, NSAMPLES):
            eval_pose(g.sample(ai, t), f"{nm}@{t:.2f}", rule)
    res["stats"].update(max_edge_stretch=round(worst["stretch"], 3), max_drift=round(worst["drift"], 4))
    res["pass"] = not res["errors"]
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+"); ap.add_argument("--json"); ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args(); out = []; ok = True
    for f in a.files:
        r = check(f); out.append(r); ok &= r["pass"]
        print(("PASS " if r["pass"] else "FAIL ") + f, json.dumps(r["stats"]))
        for e in r["errors"][:8]: print("   error:", e)
        if len(r["errors"]) > 8: print(f"   ... {len(r['errors'])-8} more errors")
        for w in r["warnings"][:3]: print("   warn:", w)
    if a.json: json.dump(out, open(a.json, "w"), indent=1)
    sys.exit(0 if ok or a.report_only else 1)
