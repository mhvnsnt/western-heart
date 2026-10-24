#!/usr/bin/env python3
"""Tekken 3 -> glTF importer (Western Heart Lab).

Reads the owner's own Tekken 3 teardown data:
  * KMD (3DMK) model: 27 rows -> 18 rigid body parts, parent hierarchy, faces
  * a posed stance OBJ produced by teardown/tekken3/tools/local/pose_assemble.py
    (bit-exact AnimDecodePose port) -- used to recover each part's real stance
    transform by rigid (Kabsch) fit, sub-unit RMS.
Outputs a skinned glTF on the WH-Canonical-22 skeleton (rigid weights: each
vertex 100% on its part's bone), bind pose = the T3 stance, world-aligned
joints, feet on the floor, facing +Z, plus authored combat clips.

Usage: t3_to_gltf.py fighter <kmd> <stance.obj> <out.glb> [--palette king]
       t3_to_gltf.py stage <stage.obj> <out.glb>
"""
import argparse, json, math, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t3_common import kmd_parse, PART_ROW, NPARTS, load_obj_parts, kabsch
from gltf_write import GLB
import clips as CL

UNIT = 1 / 1000.0  # T3 units -> meters (King hips 1.13 m)
def conv(p):  # T3 (+Y down) -> glTF (+Y up), proper rotation (180 deg about X)
    p = np.asarray(p, float); return np.stack([p[..., 0], -p[..., 1], -p[..., 2]], -1) * UNIT

PALETTES = {"king": {"Head": (0.85, 0.62, 0.20), "Chest": (0.80, 0.58, 0.45), "Hips": (0.10, 0.15, 0.45),
                     "Shoulder": (0.80, 0.58, 0.45), "Arm": (0.80, 0.58, 0.45), "ForeArm": (0.78, 0.56, 0.43), "Hand": (0.15, 0.15, 0.15),
                     "UpLeg": (0.10, 0.15, 0.45), "Leg": (0.12, 0.18, 0.50), "Foot": (0.08, 0.08, 0.08)}}

def import_fighter(kmd_path, stance_path, out, palette="king"):
    k = kmd_parse.parse_kmd(Path(kmd_path).read_bytes())
    st = load_obj_parts(stance_path)
    verts, faces, part_of_v, pivots, parents, rms = {}, {}, {}, {}, {}, {}
    for p in range(NPARTS):
        row = k["rows"][PART_ROW[p]]
        parents[p] = row["parent"]
        if not row["verts"]:
            continue
        A = np.array(row["verts"], float)
        R, t, e = kabsch(A, st[p]); rms[p] = e
        verts[p] = A @ R.T + t
        pivots[p] = t
        nv = len(A); faces[p] = [f for f in row["faces"] if all(0 <= i < nv for i in f) and len(set(f)) == 3]
    pivots[0] = pivots[2].copy()  # root = pelvis pivot
    P = {p: conv(v) for p, v in pivots.items()}
    V = {p: conv(v) for p, v in verts.items()}
    # facing: lateral = shoulder line; forward chosen so the head mesh (muzzle) leads
    lat = P[9] - P[13]; lat[1] = 0; lat /= np.linalg.norm(lat)
    fwd = np.cross(lat, [0, 1, 0]); fwd /= np.linalg.norm(fwd)
    if np.dot(V[17].mean(0) - P[17], fwd) < 0: fwd = -fwd
    ang = math.atan2(fwd[0], fwd[2])  # rotate so fwd -> +Z
    c, s = math.cos(-ang), math.sin(-ang); Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    allv = np.concatenate(list(V.values()))
    off = np.array([P[0][0], 0, P[0][2]])
    tf = lambda x: (x - off) @ Ry.T
    P = {p: tf(v) for p, v in P.items()}; V = {p: tf(v) for p, v in V.items()}
    floor = min(v[:, 1].min() for v in V.values())
    P = {p: v - [0, floor, 0] for p, v in P.items()}; V = {p: v - [0, floor, 0] for p, v in V.items()}
    A_, B_ = ("Left", "Right") if P[9][0] > 0 else ("Right", "Left")
    C_, D_ = ("Left", "Right") if P[3][0] > 0 else ("Right", "Left")
    rmap = json.load(open(Path(__file__).resolve().parents[1] / "skeleton/retarget_maps.json"))["tekken3_rigid27"]["map"]
    name = {int(kk[4:]): vv.format(A=A_, B=B_, C=C_, D=D_) for kk, vv in rmap.items()}
    # canonical bones present for this fighter, parent per T3 hierarchy
    bones = list(range(NPARTS))
    bname = [name[p] for p in bones]
    bparent = [(-1 if parents[p] < 0 else parents[p]) for p in bones]
    piv = np.array([P[p] for p in bones])
    g = GLB()
    pal = PALETTES.get(palette, PALETTES["king"])
    def colour(n):
        for key in sorted(pal, key=len, reverse=True):
            if n.endswith(key): return pal[key]
        return (0.6, 0.6, 0.6)
    pos, col, jnt, idx = [], [], [], []
    for p in bones:
        if p not in V: continue
        base = len(pos)
        for v in V[p]:
            pos.append(v); col.append(colour(bname[p]) + (1.0,)); jnt.append((p, 0, 0, 0))
        for f in faces[p]:
            idx.append([base + f[0], base + f[1], base + f[2]])
    pos = np.array(pos, np.float32); idx = np.array(idx, np.uint16).reshape(-1)
    nrm = np.zeros_like(pos); tri = idx.reshape(-1, 3)
    fn = np.cross(pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]])
    for i in range(3): np.add.at(nrm, tri[:, i], fn)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    w = np.zeros((len(pos), 4), np.float32); w[:, 0] = 1
    g.j["materials"].append({"name": "t3_vertex_colour", "doubleSided": True, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0, "roughnessFactor": 0.8}})
    attrs = {"POSITION": g.acc(pos, "VEC3", 34962, True), "NORMAL": g.acc(nrm.astype(np.float32), "VEC3", 34962),
             "COLOR_0": g.acc(np.array(col, np.float32), "VEC4", 34962),
             "JOINTS_0": g.acc(np.array(jnt, np.uint8), "VEC4", 34962), "WEIGHTS_0": g.acc(w, "VEC4", 34962)}
    g.j["meshes"].append({"name": "body", "primitives": [{"attributes": attrs, "indices": g.acc(idx, "SCALAR", 34963), "material": 0}]})
    # bone nodes (local translation = pivot - parent pivot, rest rotation identity)
    nodes = []
    for i, p in enumerate(bones):
        loc = piv[i] - (piv[bparent[i]] if bparent[i] >= 0 else 0)
        nodes.append(g.node(name=bname[i], translation=[float(x) for x in loc]))
    for i in range(len(bones)):
        ch = [nodes[c] for c in range(len(bones)) if bparent[c] == i]
        if ch: g.j["nodes"][nodes[i]]["children"] = ch
    ibm = np.array([np.eye(4) for _ in bones], np.float32)
    for i in range(len(bones)): ibm[i][:3, 3] = -piv[i]
    ibm = np.ascontiguousarray(ibm.transpose(0, 2, 1).reshape(len(bones), 16))
    g.j["skins"] = [{"name": "WH-Canonical-22", "joints": nodes, "skeleton": nodes[0], "inverseBindMatrices": g.acc(ibm, "MAT4")}]
    meshnode = g.node(name="body", mesh=0, skin=0)
    top = g.node(name="Fighter", children=[nodes[0], meshnode])
    g.j["scenes"][0]["nodes"] = [top]
    # animations
    rig = {"names": bname, "parent": bparent, "pivot": piv}
    g.j["animations"] = []
    for clipname, clip in CL.build_all(rig).items():
        ch, smp = [], []
        for bi, (times, quats, trans) in clip.items():
            ta = g.acc(np.array(times, np.float32), "SCALAR", None, True)
            smp.append({"input": ta, "output": g.acc(np.array(quats, np.float32), "VEC4"), "interpolation": "LINEAR"})
            ch.append({"sampler": len(smp) - 1, "target": {"node": nodes[bi], "path": "rotation"}})
            if trans is not None:
                smp.append({"input": ta, "output": g.acc(np.array(trans, np.float32), "VEC3"), "interpolation": "LINEAR"})
                ch.append({"sampler": len(smp) - 1, "target": {"node": nodes[bi], "path": "translation"}})
        g.j["animations"].append({"name": clipname, "channels": ch, "samplers": smp})
    g.j["extras"] = {"source": str(kmd_path), "stance": str(stance_path), "kabsch_rms_t3_units": {bname[p]: round(e, 3) for p, e in rms.items()},
                     "provenance": "third-party (Namco Tekken 3) via owner's own disc teardown -- PRIVATE LAB ONLY"}
    g.save(out)
    return {"bones": bname, "verts": int(len(pos)), "tris": int(len(idx) // 3), "max_rms": max(rms.values()), "height_m": float(pos[:, 1].max())}

def import_stage(obj, out, radius_m=30.0):
    v, f = [], []
    for line in open(obj):
        if line.startswith("v "): v.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "): f.append([int(x.split("/")[0]) - 1 for x in line.split()[1:4]])
    v = conv(np.array(v)) / UNIT
    r = np.hypot(v[:, 0], v[:, 2]).max(); v = v * (radius_m / r)
    hmin, hmax = v[:, 1].min(), v[:, 1].max()
    t = ((v[:, 1] - hmin) / max(hmax - hmin, 1e-6))[:, None]
    col = np.concatenate([(1 - t) * [0.55, 0.42, 0.30] + t * [0.25, 0.30, 0.55], np.ones((len(v), 1))], 1).astype(np.float32)
    g = GLB()
    g.j["materials"].append({"name": "panorama", "doubleSided": True, "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 1}, "emissiveFactor": [0.2, 0.2, 0.2]})
    idx = np.array(f, np.uint16).reshape(-1)
    g.j["meshes"].append({"name": "panorama", "primitives": [{"attributes": {"POSITION": g.acc(v.astype(np.float32), "VEC3", 34962, True), "COLOR_0": g.acc(col, "VEC4", 34962)}, "indices": g.acc(idx, "SCALAR", 34963), "material": 0}]})
    g.j["scenes"][0]["nodes"] = [g.node(name="panorama", mesh=0)]
    g.j["extras"] = {"source": str(obj), "note": "T3 stage panorama geometry; texture atlas not yet decoded (vertex colours)", "provenance": "third-party (Namco) PRIVATE LAB ONLY"}
    g.save(out); return {"verts": len(v), "tris": len(f)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("kind"); ap.add_argument("args", nargs="+"); ap.add_argument("--palette", default="king")
    a = ap.parse_args()
    print(json.dumps(import_fighter(*a.args, palette=a.palette) if a.kind == "fighter" else import_stage(*a.args), indent=1))
