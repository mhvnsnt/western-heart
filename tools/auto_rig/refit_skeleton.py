#!/usr/bin/env python3
"""tools/auto_rig/refit_skeleton.py — fit a canonical fighter skeleton INSIDE a mesh, from the mesh itself.

Owner 2026-10-22: "Need to get the bind pose overlays and heat mapping and skinning and rigging and boning
fully done for every character every glb model and fix for every second skeleton rig and base". The rig
check (tools/model-audit/rig_qa.py) found skeletons sitting outside their meshes (Pantera Leopard King:
every joint ~0.25 m behind the body, toes pointing backwards, Left* bones in the mesh's right limbs). Bone
heat / any weighting then deforms the mesh around joints that are not in it.

This is stage 1 (numpy only): joint positions. Stage 2, tools/auto_rig/backends/heat_rebind.py (Blender),
builds the armature from the JSON written here and skins it with bone heat.

Method (every number comes from the mesh or the template file; nothing is authored):
  * template skeleton = a skinned game GLB's joints (default game/assets/models/pantera.glb, King's 49-joint
    canonical skeleton), read from its inverse bind matrices; turned to face +Z with Left* on +X (the
    character's left) when its toes point -Z — so names always match anatomy;
  * scaled to the mesh height, then each joint re-centred in the mesh's own cross-section at that joint:
      spine chain + legs: horizontal slab at the joint height, local window around the start point,
                          centre = middle of the window's extent (2 refinement passes);
      arms (T-pose):      vertical slab across the arm at the joint's x;
      ankle:              the shin just above the ankle (the boot's toe box would pull it forward);
      toe:                72% of the way from heel to toe tip along the sole;
      fingers:            carried with the hand;
  * an optional tail chain (Tail1..TailN parented to Hips) is fitted along the tail's medial curve:
    geodesic distance over a k-NN graph of the tail vertices (from the input skin's tail weights), binned
    centroids, joints at equal arc length.

    python3 tools/auto_rig/refit_skeleton.py --mesh MODEL.glb --out fit.json [--template T.glb]
        [--facing +Z|-Z|+X|-X] [--tail-joints 4]

Plain glTF only (decode meshopt first: tools/anim/gltf_codec.mjs decode).
"""
import argparse
import json
import os
import re
import struct
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools", "model-audit"))
import rig_qa  # noqa: E402  (read_glb, accessor, canon)

ROT_Y = {"+Z": 0, "-Z": 180, "+X": -90, "-X": 90}  # degrees about +Y that turn the mesh to face +Z


def rot_y(deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def node_world(js):
    N = js["nodes"]
    par = {c: i for i, n in enumerate(N) for c in n.get("children", [])}

    def local(i):
        n = N[i]
        if "matrix" in n:
            return np.array(n["matrix"], float).reshape(4, 4).T
        x, y, z, w = n.get("rotation", [0, 0, 0, 1])
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        M = np.eye(4)
        M[:3, :3] = R @ np.diag(n.get("scale", [1, 1, 1]))
        M[:3, 3] = n.get("translation", [0, 0, 0])
        return M

    cache = {}

    def world(i):
        if i not in cache:
            cache[i] = (world(par[i]) if i in par else np.eye(4)) @ local(i)
        return cache[i]
    return world


def load_mesh(path):
    """All mesh vertices in bind space (skinned) or world space (static), plus per-vertex tail weight."""
    js, blob = rig_qa.read_glb(path)
    if "EXT_meshopt_compression" in (js.get("extensionsUsed") or []):
        sys.exit(f"{path}: meshopt-compressed — decode first (tools/anim/gltf_codec.mjs decode)")
    world = node_world(js)
    V, TW = [], []
    tail_names = re.compile(r"^Tail\d+$")
    for i, nd in enumerate(js["nodes"]):
        if "mesh" not in nd:
            continue
        skin = js["skins"][nd["skin"]] if nd.get("skin") is not None else None
        names = [rig_qa.canon(js["nodes"][j].get("name", "")) for j in skin["joints"]] if skin else []
        tail_ids = [k for k, n in enumerate(names) if tail_names.match(n)]
        for pr in js["meshes"][nd["mesh"]]["primitives"]:
            at = pr["attributes"]
            P = rig_qa.accessor(js, blob, at["POSITION"])
            if skin is None:  # static: place by its node transform
                M = world(i)
                P = P @ M[:3, :3].T + M[:3, 3]
            V.append(P)
            if skin is not None and tail_ids and "JOINTS_0" in at:
                J = rig_qa.accessor(js, blob, at["JOINTS_0"]).astype(int)
                W = rig_qa.accessor(js, blob, at["WEIGHTS_0"])
                TW.append(sum((W * (J == t)).sum(1) for t in tail_ids))
            else:
                TW.append(np.zeros(len(P)))
    return np.vstack(V), np.concatenate(TW)


def load_template(path):
    js, blob = rig_qa.read_glb(path)
    sk = js["skins"][0]
    J = sk["joints"]
    N = js["nodes"]
    ibm = rig_qa.accessor(js, blob, sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    pos = {rig_qa.canon(N[j]["name"]): np.linalg.inv(m)[:3, 3] for j, m in zip(J, ibm)}
    par = {c: i for i, n in enumerate(N) for c in n.get("children", [])}
    parent = {rig_qa.canon(N[j]["name"]): (rig_qa.canon(N[par[j]]["name"]) if par.get(j) in J else None) for j in J}
    order = [rig_qa.canon(N[j]["name"]) for j in J]
    return order, parent, pos


def swap_side(n):
    return re.sub(r"^(Left|Right)", lambda m: "Right" if m.group(1) == "Left" else "Left", n)


def window_mid(P, axes, start, half, passes=3):
    """Middle of the extent of the points P (already sliced to a slab) inside a moving window."""
    c = np.array(start, float)
    sel = None
    for _ in range(passes):
        m = np.all(np.abs(P[:, axes] - c) <= half, axis=1)
        if m.sum() < 8:
            break
        sel = P[m][:, axes]
        c = (sel.min(0) + sel.max(0)) / 2
    return c, (0 if sel is None else len(sel))


def write_static(src, dst):
    """Copy of a GLB with its skin, skeleton and animations removed: every mesh node at the scene root with
    an identity transform, so the vertices sit exactly in their bind pose (skinned) or keep their placement
    baked by node transforms (static input is copied as-is). Buffers are untouched; unused accessors stay."""
    js, blob = rig_qa.read_glb(src)
    skinned = any(nd.get("skin") is not None for nd in js["nodes"] if "mesh" in nd)
    if skinned:
        mesh_nodes = []
        for i, nd in enumerate(js["nodes"]):
            if "mesh" in nd and nd.get("skin") is not None:
                for k in ("skin", "rotation", "translation", "scale", "matrix", "children"):
                    nd.pop(k, None)
                mesh_nodes.append(i)
        for nd in js["nodes"]:
            if "children" in nd:
                nd["children"] = [c for c in nd["children"] if c not in mesh_nodes]
        js["scenes"] = [{"name": "static", "nodes": mesh_nodes}]
        js["scene"] = 0
        js.pop("skins", None)
        js.pop("animations", None)
        for m in js["meshes"]:
            for pr in m["primitives"]:
                for k in [k for k in pr["attributes"] if k.startswith(("JOINTS_", "WEIGHTS_"))]:
                    pr["attributes"].pop(k)
    jb = json.dumps(js, separators=(",", ":")).encode()
    jb += b" " * (-len(jb) % 4)
    bb = blob + b"\0" * (-len(blob) % 4)
    total = 12 + 8 + len(jb) + 8 + len(bb)
    with open(dst, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A) + jb)
        f.write(struct.pack("<II", len(bb), 0x004E4942) + bb)
    return skinned


def fit(mesh_path, template_path, facing=None, tail_joints=4):
    V, TW = load_mesh(mesh_path)
    if facing is None:
        facing = "+Z"
    R = rot_y(ROT_Y[facing])
    V = V @ R.T
    V[:, 1] -= V[:, 1].min()           # feet on the floor
    cx = (V[:, 0].min() + V[:, 0].max()) / 2
    H = V[:, 1].max()
    tail = TW > 0.3
    body = V[~tail]

    order, parent, T = load_template(template_path)
    T = {k: v.copy() for k, v in T.items()}
    # template facing from its own toes: turn to +Z (Left* then lies on +X = the character's left)
    toe_dz = np.mean([T[s + "ToeBase"][2] - T[s + "Foot"][2] for s in ("Left", "Right") if s + "ToeBase" in T])
    turned = bool(toe_dz < 0)
    if turned:
        T = {k: v * np.array([-1, 1, -1]) for k, v in T.items()}
    relabelled = bool(T["LeftArm"][0] < T["RightArm"][0])
    if relabelled:  # Left* on the character's right even after facing +Z: mirrored names, relabel
        T = {swap_side(k): v for k, v in T.items()}
        parent = {swap_side(k): (swap_side(v) if v else None) for k, v in parent.items()}
        order = [swap_side(k) for k in order]
    # scale by mesh heights (the template's own skinned mesh, feet to head top)
    TV, _ = load_mesh(template_path)
    t_floor = TV[:, 1].min()
    s = H / max(TV[:, 1].max() - t_floor, 1e-6)
    T = {k: np.array([(v[0] - T["Hips"][0]) * s + cx, (v[1] - t_floor) * s, v[2] * s]) for k, v in T.items()}

    out = {}
    notes = {}
    # torso depth centre at hip height gives the start offset for every joint's window
    hip_slab = body[np.abs(body[:, 1] - T["Hips"][1]) < 0.01 * H]
    core = hip_slab[np.abs(hip_slab[:, 0] - cx) < 0.08 * H]
    z0 = (core[:, 2].min() + core[:, 2].max()) / 2 if len(core) > 8 else T["Hips"][2]
    dz = z0 - T["Hips"][2]
    notes["template_turned_180"] = turned
    notes["template_relabelled_LR"] = relabelled
    notes["scale"] = round(float(s), 4)
    notes["start_offset_z_m"] = round(float(dz), 4)

    def hslab(y, w=0.008):
        return body[np.abs(body[:, 1] - y) < w * H]

    # spine chain: x on the body's mid-plane, z centred in the torso slab
    for j in ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"):
        if j not in T:
            continue
        y = T[j][1]
        sl = hslab(y)
        c, n = window_mid(sl, [0, 2], [cx, T[j][2] + dz], [0.09 * H, 0.2 * H])
        out[j] = np.array([cx, y, c[1]])
        notes[j] = int(n)
    # legs
    for side in ("Left", "Right"):
        for j, yoff in (("UpLeg", 0.0), ("Leg", 0.0), ("Foot", 0.03)):
            name = side + j
            y = T[name][1]
            sl = hslab(y + yoff * H)
            c, n = window_mid(sl, [0, 2], [T[name][0], T[name][2] + dz], [0.06 * H, 0.1 * H])
            out[name] = np.array([c[0], y, c[1]])
            notes[name] = int(n)
        # toe: along the sole, 72% heel -> tip (facing +Z: tip = max z)
        a = out[side + "Foot"]
        sole = body[(body[:, 1] < 0.03 * H) & (np.abs(body[:, 0] - a[0]) < 0.06 * H) & (np.abs(body[:, 2] - a[2]) < 0.2 * H)]
        if len(sole) > 8:
            zb, zt = sole[:, 2].min(), sole[:, 2].max()
            xm = (sole[:, 0].min() + sole[:, 0].max()) / 2
            out[side + "ToeBase"] = np.array([xm, T[side + "ToeBase"][1], zb + 0.72 * (zt - zb)])
            notes[side + "ToeBase"] = {"heel_z": round(float(zb), 3), "tip_z": round(float(zt), 3)}
        else:
            out[side + "ToeBase"] = T[side + "ToeBase"] + np.array([0, 0, dz])
    # arms (T-pose): vertical slabs across the arm
    for side in ("Left", "Right"):
        for j in ("Arm", "ForeArm", "Hand"):
            name = side + j
            x = T[name][0]
            sl = body[np.abs(body[:, 0] - x) < 0.008 * H]
            sl = sl[sl[:, 1] > T["Spine1"][1]]
            c, n = window_mid(sl, [1, 2], [T[name][1], T[name][2] + dz], [0.06 * H, 0.12 * H])
            out[name] = np.array([x, c[0], c[1]])
            notes[name] = int(n)
        sh = side + "Shoulder"
        if sh in T:
            arm = out[side + "Arm"]
            out[sh] = np.array([T[sh][0], arm[1] + (T[sh][1] - T[side + "Arm"][1]), (out["Spine2"][2] + arm[2]) / 2])
        # fingers ride with the hand
        dh = out[side + "Hand"] - T[side + "Hand"]
        for k in T:
            if k.startswith(side + "Hand") and k != side + "Hand":
                out[k] = T[k] + dh
    # anything left (template extras) rides with its parent's shift
    for k in order:
        k2 = k
        if k2 not in out:
            if k2 not in T:
                continue
            p = parent.get(k2) if k2 in parent else None
            out[k2] = T[k2] + (out[p] - T[p] if p in out and p in T else np.array([0, 0, dz]))

    joints = [{"name": k, "parent": parent.get(k), "pos": [round(float(x), 5) for x in out[k]]} for k in order if k in out]
    leaf_tail = {}
    # tail chain from the input skin's tail weights
    if tail.sum() > 200 and tail_joints > 0:
        from scipy.sparse.csgraph import dijkstra
        from scipy.sparse import coo_matrix
        from scipy.spatial import cKDTree
        P = V[tail]
        if len(P) > 6000:
            P = P[np.linspace(0, len(P) - 1, 6000).astype(int)]
        kd = cKDTree(P)
        d, nb = kd.query(P, k=9)
        rows = np.repeat(np.arange(len(P)), 8)
        G = coo_matrix((d[:, 1:].ravel() + 1e-9, (rows, nb[:, 1:].ravel())), shape=(len(P), len(P))).tocsr()
        root = int(np.argmin(np.linalg.norm(P - out["Hips"], axis=1)))
        g = dijkstra(G, directed=False, indices=root)
        ok = np.isfinite(g)
        P, g = P[ok], g[ok]
        bins = np.linspace(0, g.max(), 25)
        cent = [P[(g >= a) & (g < b)].mean(0) for a, b in zip(bins[:-1], bins[1:]) if ((g >= a) & (g < b)).sum() > 3]
        cent = np.array(cent)
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(cent, axis=0), axis=1))]
        L = seg[-1]
        at = lambda u: np.array([np.interp(u * L, seg, cent[:, k]) for k in range(3)])
        prev = "Hips"
        for i in range(tail_joints):
            nm = f"Tail{i + 1}"
            joints.append({"name": nm, "parent": prev, "pos": [round(float(x), 5) for x in at(i / tail_joints)]})
            prev = nm
        leaf_tail[prev] = [round(float(x), 5) for x in at(1.0)]
        notes["tail"] = {"verts": int(tail.sum()), "length_m": round(float(L), 3), "root": [round(float(x), 3) for x in cent[0]]}
    return {
        "format": "wh-refit/1",
        "tool": "tools/auto_rig/refit_skeleton.py",
        "mesh": mesh_path, "template": template_path,
        "mesh_facing_in": facing, "mesh_rot_y_deg": ROT_Y[facing],
        "height_m": round(float(H), 4),
        "space": "glTF (Y-up, metres), mesh facing +Z, character's left = +X, feet at y=0",
        "joints": joints, "leaf_tail": leaf_tail, "notes": notes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=os.path.join(REPO, "game", "assets", "models", "pantera.glb"))
    ap.add_argument("--facing", choices=sorted(ROT_Y), default="+Z")
    ap.add_argument("--tail-joints", type=int, default=4)
    ap.add_argument("--static-out", default=None, help="also write the mesh without skin (bind pose) for stage 2")
    a = ap.parse_args()
    res = fit(a.mesh, a.template, a.facing, a.tail_joints)
    if a.static_out:
        write_static(a.mesh, a.static_out)
        res["static_mesh"] = a.static_out
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("height_m", "notes")}, indent=1)[:3000])


if __name__ == "__main__":
    main()
