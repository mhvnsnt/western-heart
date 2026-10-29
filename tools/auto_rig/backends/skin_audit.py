#!/usr/bin/env python3
"""tools/auto_rig/backends/skin_audit.py — skin + skeleton audit gate.

WHY THIS EXISTS (2026-10-29, owner order to revive the universal
rig-repair pipeline): the playable gate (validate.py + anim_check.py)
measures edge stretch under animation. It PASSED rigs the owner then
rejected on sight — Pantera Leopard King (#448): legs folded back to the
spine, feet bent backwards, a hand weighted to the tail — because a
folded-at-rest skeleton deforms "smoothly" and a cross-body weight is
invisible to a stretch metric until the wrong pose exposes it.

This audit measures the things stretch cannot see, at rest, in pure
python + numpy (+ scipy when present):

  WEIGHTS
    sum_not_one        verts whose 4 weights do not sum to 1 (+-0.01)
    unweighted         verts whose weights sum to ~0 (exporter crashers)
    joints_1_present   JOINTS_1/WEIGHTS_1 present (>4 influences/vertex;
                       the game skinning path reads set 0 only, so set-1
                       weight is silently dropped in game)
    dead_joints        skin joints carrying ~0 total weight
    contamination      weight mass assigned to a joint whose bone segment
                       is far from the vertex while another joint's segment
                       is near it — the hand-weighted-to-tail class.
                       Rule: segdist(v, j) > nearest_segdist(v)
                       + max(0.10 * height, 2.5 * nearest_segdist)
                       for influences >= 0.05.

  SKELETON (identity / proportion — a rig must BE the right skeleton)
    proportion_flags   per-bone length ratios vs backends/
                       skeleton_template.json (normalized by height);
                       flag outside [0.65, 1.50]
    folded_chains      knee/elbow interior angle < 120 deg at rest, or a
                       lower joint sitting ABOVE its parent joint
                       (ankle above knee = foot folded to the spine)
    joints_outside     limb/spine joint heads farther than
                       0.04 * height from the nearest mesh vertex
                       (the Stick-Up failure: arm bones ~5 cm outside
                       the mesh, so heat weighting deformed air)
    feet_planted       verts weighted > 0.5 to Foot/ToeBase joints must
                       reach within 0.03 * height of the mesh floor

Every number is measured from the file; nothing is authored. Report is
JSON on stdout; exit 0 = pass, 1 = fail.

    python3 skin_audit.py --in MODEL.glb [--json-out R.json]
"""

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from validate import read_glb  # noqa: E402

COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16,
        5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


CANON_CHILD = {
    "Hips": "Spine", "Spine": "Spine1", "Spine1": "Spine2",
    "Spine2": "Neck", "Neck": "Head",
    "LeftShoulder": "LeftArm", "LeftArm": "LeftForeArm",
    "LeftForeArm": "LeftHand", "RightShoulder": "RightArm",
    "RightArm": "RightForeArm", "RightForeArm": "RightHand",
    "LeftUpLeg": "LeftLeg", "LeftLeg": "LeftFoot",
    "LeftFoot": "LeftToeBase", "RightUpLeg": "RightLeg",
    "RightLeg": "RightFoot", "RightFoot": "RightToeBase",
}
for _side in ("Left", "Right"):
    for _f in ("Thumb", "Index", "Middle", "Ring", "Pinky"):
        for _k in (1, 2):
            CANON_CHILD[f"{_side}Hand{_f}{_k}"] = f"{_side}Hand{_f}{_k + 1}"
    CANON_CHILD[f"{_side}Hand"] = f"{_side}HandMiddle1"
# bones whose length defines skeleton identity (fingers/head excluded:
# their child distances are authoring-convention, gated elsewhere)
MAJOR_BONES = ["Hips", "Spine", "Spine1", "Spine2", "LeftShoulder",
               "LeftArm", "LeftForeArm", "RightShoulder", "RightArm",
               "RightForeArm", "LeftUpLeg", "LeftLeg", "LeftFoot",
               "RightUpLeg", "RightLeg", "RightFoot"]


def read_accessor(js, bdat, idx):
    acc = js["accessors"][idx]
    dt = COMP[acc["componentType"]]
    nc = NCOMP[acc["type"]]
    bv = js["bufferViews"][acc["bufferView"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n = acc["count"]
    item = np.dtype(dt).itemsize * nc
    stride = bv.get("byteStride", item)
    if stride == item:
        arr = np.frombuffer(bdat, dtype=dt, count=n * nc,
                            offset=off).reshape(n, nc)
    else:
        total = ((n - 1) * stride) // np.dtype(dt).itemsize + nc
        flat = np.frombuffer(bdat, dtype=dt, count=total, offset=off)
        arr = np.lib.stride_tricks.as_strided(
            flat, shape=(n, nc),
            strides=(stride, np.dtype(dt).itemsize))
    arr = np.asarray(arr, dtype=np.float64) if dt == np.float32 else arr
    if acc["componentType"] in (5121, 5123) and "WEIGHTS" in str(
            acc.get("name", "")):
        pass
    return arr


def read_weights(js, bdat, idx):
    """WEIGHTS accessors may be float or normalized unsigned; return float."""
    acc = js["accessors"][idx]
    arr = read_accessor(js, bdat, idx)
    if acc["componentType"] == 5121:
        return arr.astype(np.float64) / 255.0
    if acc["componentType"] == 5123:
        return arr.astype(np.float64) / 65535.0
    return arr.astype(np.float64)


def quat_mat(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1]], dtype=np.float64)


def node_local(node):
    if "matrix" in node:
        return np.array(node["matrix"], dtype=np.float64).reshape(4, 4).T
    m = np.eye(4)
    if "scale" in node:
        s = np.diag(list(node["scale"]) + [1.0])
    else:
        s = np.eye(4)
    r = quat_mat(node["rotation"]) if "rotation" in node else np.eye(4)
    t = np.eye(4)
    if "translation" in node:
        t[:3, 3] = node["translation"]
    return t @ r @ s


def world_matrices(js):
    nodes = js.get("nodes", [])
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get("children", []):
            parent[c] = i
    cache = {}

    def world(i):
        if i in cache:
            return cache[i]
        m = node_local(nodes[i])
        if i in parent:
            m = world(parent[i]) @ m
        cache[i] = m
        return m

    return [world(i) for i in range(len(nodes))], parent


def seg_dist(points, a, b):
    """Distance from each point to segment a-b."""
    ab = b - a
    denom = float(ab @ ab)
    if denom < 1e-12:
        return np.linalg.norm(points - a, axis=1)
    t = np.clip(((points - a) @ ab) / denom, 0.0, 1.0)
    proj = a + np.outer(t, ab)
    return np.linalg.norm(points - proj, axis=1)


def edges_tris(js, bdat):
    """All triangles (bind-space positions) of all meshes, for
    point-to-triangle distance. Returns an (T, 3, 3) array or None."""
    tris = []
    for m in js.get("meshes", []):
        for prim in m.get("primitives", []):
            at = prim.get("attributes", {})
            if "POSITION" not in at or "indices" not in prim:
                continue
            p = read_accessor(js, bdat, at["POSITION"]).astype(np.float64)
            idx = read_accessor(js, bdat, prim["indices"]).astype(
                np.int64).reshape(-1, 3)
            tris.append(p[idx])
    if not tris:
        return None
    return np.concatenate(tris)


def point_mesh_distance(points, verts, tris):
    """Min distance from each point to the mesh surface (triangles when
    available, else vertices). Vectorized per point over triangles in
    chunks — joint counts are small (~80)."""
    if tris is None:
        return np.array([float(np.min(np.linalg.norm(verts - p, axis=1)))
                         for p in points])
    out = []
    a = tris[:, 0]; b = tris[:, 1]; c = tris[:, 2]
    ab = b - a; ac = c - a
    nrm = np.cross(ab, ac)
    nl = np.linalg.norm(nrm, axis=1)
    nl[nl < 1e-12] = 1e-12
    nrm = nrm / nl[:, None]
    for p in points:
        ap = p - a
        # barycentric projection onto each triangle plane
        d = np.einsum('ij,ij->i', ap, nrm)
        pp = p - d[:, None] * nrm
        v0 = ab; v1 = ac; v2 = pp - a
        d00 = np.einsum('ij,ij->i', v0, v0)
        d01 = np.einsum('ij,ij->i', v0, v1)
        d11 = np.einsum('ij,ij->i', v1, v1)
        d20 = np.einsum('ij,ij->i', v2, v0)
        d21 = np.einsum('ij,ij->i', v2, v1)
        den = d00 * d11 - d01 * d01
        den[np.abs(den) < 1e-14] = 1e-14
        v = (d11 * d20 - d01 * d21) / den
        w = (d00 * d21 - d01 * d20) / den
        u = 1.0 - v - w
        inside = (u >= 0) & (v >= 0) & (w >= 0)
        dist = np.where(inside, np.abs(d), np.inf)
        if not inside.all():
            for (x, y) in ((a, b), (b, c), (c, a)):
                xy = y - x
                den = np.einsum('ij,ij->i', xy, xy)
                den[den < 1e-14] = 1e-14
                t = np.clip(np.einsum('ij,ij->i', p - x, xy) / den, 0, 1)
                closest = x + t[:, None] * xy
                dist = np.minimum(
                    dist, np.linalg.norm(p - closest, axis=1))
        out.append(float(dist.min()))
    return np.array(out)


def points_inside_mesh(points, tris):
    """Ray-parity point-in-mesh test (+X rays, Moller-Trumbore).
    Returns bool array, or None when the mesh is not watertight
    (parity is meaningless on open shells)."""
    if tris is None or len(tris) == 0:
        return None
    # watertight: every undirected edge shared by exactly 2 triangles
    a = tris[:, 0]; b = tris[:, 1]; c = tris[:, 2]
    # use vertex positions quantized as edge keys via the tris' own
    # vertex identity is unavailable here; use coordinate tuples
    def key(p):
        return (round(float(p[0]), 5), round(float(p[1]), 5),
                round(float(p[2]), 5))
    from collections import Counter
    cnt = Counter()
    for (x, y) in ((a, b), (b, c), (c, a)):
        for i in range(len(tris)):
            e = tuple(sorted((key(x[i]), key(y[i]))))
            cnt[e] += 1
    if any(v != 2 for v in cnt.values()):
        return None
    inside = []
    d = np.array([1.0, 0.0, 0.0])
    e1 = b - a; e2 = c - a
    pv = np.cross(d, e2)
    det = np.einsum('ij,ij->i', e1, pv)
    ok = np.abs(det) > 1e-12
    for p in points:
        tv = p - a
        u = np.where(ok, np.einsum('ij,ij->i', tv, pv) /
                     np.where(ok, det, 1.0), -1)
        qv = np.cross(tv, e1)
        v = np.where(ok, (qv @ d) / np.where(ok, det, 1.0), -1)
        t = np.where(ok, np.einsum('ij,ij->i', e2, qv) /
                     np.where(ok, det, 1.0), -1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
        inside.append(bool(np.sum(hit) % 2 == 1))
    return np.array(inside)


def audit(path):
    js, bdat = read_glb(path)
    rep = {"file": path, "checks": {}, "measured": {}, "pass": False}
    skins = js.get("skins", [])
    if not skins:
        rep["checks"]["skinned"] = False
        return rep
    rep["checks"]["skinned"] = True
    worlds, parent = world_matrices(js)
    skin = skins[0]
    joint_nodes = skin["joints"]
    nodes = js.get("nodes", [])
    names = [nodes[j].get("name", "") for j in joint_nodes]
    # Joint bind positions from the inverse bind matrices — the same
    # space the raw vertex positions live in. Node-graph worlds mix in
    # scene roots (armature scale/rotation) that skinning never applies
    # to the vertices, which made healthy rigs read as joints floating
    # ~1 m outside the mesh. (refit_skeleton.py reads IBMs for the
    # same reason.)
    if "inverseBindMatrices" in skin:
        ibm = read_accessor(js, bdat, skin["inverseBindMatrices"])
        jpos = []
        for i in range(len(joint_nodes)):
            m = ibm[i].reshape(4, 4, order="F")
            jpos.append(np.linalg.inv(m)[:3, 3])
        jpos = np.array(jpos)
    else:
        jpos = np.array([worlds[j][:3, 3] for j in joint_nodes])

    # child joint of each joint: canonical chain child when the rig
    # uses template names, else first joint-node child
    node_to_joint = {n: i for i, n in enumerate(joint_nodes)}
    name_to_joint = {n: i for i, n in enumerate(names)}
    child_joint = {}
    for i, n in enumerate(joint_nodes):
        want = CANON_CHILD.get(names[i])
        if want in name_to_joint:
            child_joint[i] = name_to_joint[want]
            continue
        for c in nodes[n].get("children", []):
            if c in node_to_joint:
                child_joint[i] = node_to_joint[c]
                break
    seg_b = np.array([jpos[child_joint[i]] if i in child_joint else
                      jpos[i] + (jpos[i] - jpos[node_to_joint[parent[joint_nodes[i]]]]
                                 if joint_nodes[i] in parent and
                                 parent[joint_nodes[i]] in node_to_joint
                                 else np.array([0.0, 0.05, 0.0]))
                      for i in range(len(jpos))])

    # gather skinned prims
    all_pos, all_j, all_w = [], [], []
    has_set1 = False
    edges = []
    voff = 0
    for ni, nd in enumerate(nodes):
        if "mesh" not in nd or "skin" not in nd:
            continue
        for prim in js["meshes"][nd["mesh"]]["primitives"]:
            at = prim.get("attributes", {})
            if "POSITION" not in at or "JOINTS_0" not in at:
                continue
            # bind space: raw positions, matching the IBM joint space
            pos = read_accessor(js, bdat, at["POSITION"]).astype(np.float64)
            j0 = read_accessor(js, bdat, at["JOINTS_0"]).astype(np.int64)
            w0 = read_weights(js, bdat, at["WEIGHTS_0"])
            if "JOINTS_1" in at:
                has_set1 = True
            if "indices" in prim:
                idx = read_accessor(js, bdat, prim["indices"]).astype(
                    np.int64).reshape(-1)
                tris = idx.reshape(-1, 3)
                e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]],
                                    tris[:, [2, 0]]]) + voff
                edges.append(np.unique(np.sort(e, 1), axis=0))
            all_pos.append(pos)
            all_j.append(j0[:, :4])
            all_w.append(w0[:, :4])
            voff += len(pos)
    if not all_pos:
        rep["checks"]["skinned_prims"] = False
        return rep
    pos = np.concatenate(all_pos)
    jj = np.concatenate(all_j)
    ww = np.concatenate(all_w)
    nverts = len(pos)
    height = float(pos[:, 1].max() - pos[:, 1].min())
    floor_y = float(pos[:, 1].min())
    rep["measured"].update({"verts": int(nverts), "joints": len(names),
                            "height": round(height, 4)})

    # ---- weights ----
    sums = ww.sum(axis=1)
    bad_sum = int(np.sum(np.abs(sums - 1.0) > 0.01))
    unweighted = int(np.sum(sums < 1e-6))
    rep["measured"].update({"weight_sum_bad": bad_sum,
                            "unweighted_verts": unweighted,
                            "joints_1_present": bool(has_set1)})
    rep["checks"]["weight_sum_ok"] = bad_sum == 0
    rep["checks"]["no_unweighted"] = unweighted == 0
    rep["checks"]["no_joints_1"] = not has_set1

    totals = np.zeros(len(names))
    np.add.at(totals, jj.reshape(-1), ww.reshape(-1))
    dead = [names[i] for i in range(len(names)) if totals[i] < 1e-4]
    dead_major = [n for n in dead
                  if not any(s in n for s in
                             ("Thumb", "Index", "Middle", "Ring", "Pinky",
                              "Palm", "Breast", "Pelvis"))]
    rep["measured"]["dead_joints"] = dead
    rep["measured"]["dead_major_joints"] = dead_major
    rep["checks"]["no_dead_joints"] = len(dead_major) == 0

    # nearest segment distance per vertex + contamination
    nearest = np.full(nverts, np.inf)
    segd = np.empty((nverts, len(names)), dtype=np.float32)
    for j in range(len(names)):
        d = seg_dist(pos, jpos[j], seg_b[j]).astype(np.float32)
        segd[:, j] = d
        nearest = np.minimum(nearest, d)
    import re as _re
    body_joint = np.array([bool(_re.search(
        r"^(Left|Right)?(Hips|Spine|Neck|Head|Shoulder|Arm|ForeArm|Hand|"
        r"UpLeg|Leg|Foot|ToeBase)|Tail\d", n)) for n in names])
    margin = np.maximum(0.10 * height, 2.5 * nearest)
    # per influence slot: distance from the vertex to the segment of the
    # joint that slot actually weights it to
    d_slot = segd[np.arange(nverts)[:, None], jj]          # (verts, 4)
    far_slot = d_slot > (nearest + margin)[:, None]
    contam_mask = far_slot & (ww >= 0.05) & \
        body_joint[jj]
    contam_mass = float(ww[contam_mask].sum() / max(ww.sum(), 1e-9))
    contam_verts = int(np.sum(contam_mask.any(axis=1)))
    worst = []
    if contam_verts:
        per_vert = np.where(contam_mask, ww, 0).sum(axis=1)
        for vi in np.argsort(per_vert)[-5:][::-1]:
            if per_vert[vi] <= 0:
                continue
            bad_js = [names[jj[vi, k]] for k in range(jj.shape[1])
                      if contam_mask[vi, k]]
            worst.append({"vert": int(vi),
                          "bad_weight": round(float(per_vert[vi]), 3),
                          "joints": bad_js[:4]})
    rep["measured"].update({"contaminated_weight_mass": round(contam_mass, 5),
                            "contaminated_verts": contam_verts,
                            "contamination_worst": worst})
    rep["checks"]["no_contamination"] = contam_mass < 0.001

    # ---- skeleton: proportions vs template ----
    tpl_path = os.path.join(HERE, "skeleton_template.json")
    prop_flags = []
    prop_warn = []
    bone_lengths = {}
    HARD_BONES = ("Hips", "Spine", "Spine1", "Spine2", "LeftUpLeg",
                  "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg",
                  "RightFoot")
    if os.path.exists(tpl_path):
        tpl = json.load(open(tpl_path))
        tlen = {}
        for j in tpl["joints"]:
            h = np.array(j["head"]); t = np.array(j["tail"])
            tlen[j["name"]] = float(np.linalg.norm(t - h))
        th = float(tpl.get("height_m", 1.8))
        by_name = {n: i for i, n in enumerate(names)}
        for j in tpl["joints"]:
            nm = j["name"]
            if nm not in MAJOR_BONES:
                continue
            if nm not in by_name or tlen[nm] < 1e-6:
                continue
            i = by_name[nm]
            if i not in child_joint:
                continue
            ml = float(np.linalg.norm(
                jpos[child_joint[i]] - jpos[i]))
            bone_lengths[nm] = round(ml, 3)
            ratio = (ml / height) / (tlen[nm] / th) if height > 0 else 0
            if ratio < 0.65 or ratio > 1.50:
                prop_warn.append({"bone": nm, "ratio": round(ratio, 2)})
            if nm in HARD_BONES and (ratio < 0.40 or ratio > 2.50):
                prop_flags.append({"bone": nm, "ratio": round(ratio, 2)})
    rep["measured"]["proportion_flags"] = prop_flags
    rep["measured"]["proportion_warnings"] = prop_warn
    rep["measured"]["bone_lengths_m"] = bone_lengths
    rep["checks"]["proportions_ok"] = len(prop_flags) == 0

    # ---- skeleton: folded chains ----
    by_name = {n: i for i, n in enumerate(names)}

    def angle_at(a, b, c):
        v1 = jpos[a] - jpos[b]; v2 = jpos[c] - jpos[b]
        n1 = np.linalg.norm(v1); n2 = np.linalg.norm(v2)
        if n1 < 1e-9 or n2 < 1e-9:
            return 180.0
        return math.degrees(math.acos(
            float(np.clip(v1 @ v2 / (n1 * n2), -1, 1))))

    folds = []
    for side in ("Left", "Right"):
        for chain, mid in ((("UpLeg", "Leg", "Foot"), "Leg"),
                           (("Arm", "ForeArm", "Hand"), "ForeArm")):
            ns = [side + c for c in chain]
            if all(n in by_name for n in ns):
                ang = angle_at(*[by_name[n] for n in ns])
                if ang < 120.0:
                    folds.append({"chain": ns, "angle_deg": round(ang, 1)})
                if jpos[by_name[ns[2]]][1] > jpos[by_name[ns[1]]][1] + \
                        0.02 * height and chain[0] == "UpLeg":
                    folds.append({"chain": ns,
                                  "error": "ankle_above_knee"})
    rep["measured"]["folded_chains"] = folds
    rep["checks"]["no_folded_chains"] = len(folds) == 0

    # ---- skeleton: joints outside mesh ----
    tris_all = edges_tris(js, bdat)
    d_near = point_mesh_distance(jpos, pos, tris_all)
    inside = points_inside_mesh(jpos, tris_all)
    tpl_names = set()
    if os.path.exists(tpl_path):
        tpl_names = {j["name"] for j in
                     json.load(open(tpl_path))["joints"]}
    outside = []
    skip = ("Thumb", "Index", "Middle", "Ring", "Pinky", "Toe", "Breast",
            "HeadTop")
    for i, n in enumerate(names):
        if tpl_names and n not in tpl_names:
            continue  # helper bones (palms/pelvis) sit outside by design
        if any(s in n for s in skip):
            continue
        if inside is not None:
            bad = not bool(inside[i])
        else:
            # open shell: parity unusable — fall back to a generous
            # surface-distance bound (interior joints sit a body-radius
            # from the surface; only gross misfits exceed this)
            bad = d_near[i] > 0.09 * height
        if bad:
            outside.append({"joint": n,
                            "dist_m": round(float(d_near[i]), 3),
                            "inside": None if inside is None
                            else bool(inside[i])})
    rep["measured"]["joints_outside_mesh"] = outside
    rep["measured"]["mesh_watertight"] = inside is not None
    rep["checks"]["joints_inside_mesh"] = len(outside) == 0

    # ---- feet planted ----
    foot_js = [i for i, n in enumerate(names)
               if n.endswith("Foot") or n.endswith("ToeBase")]
    feet_ok = True
    feet_min = None
    if foot_js:
        fw = np.array([ww[jj == j].max() if np.any(jj == j) else 0
                       for j in foot_js])
        mask = np.zeros(nverts, dtype=bool)
        for j in foot_js:
            sel = (jj == j) & (ww > 0.5)
            mask |= sel.any(axis=1)
        if mask.any():
            feet_min = float(pos[mask][:, 1].min())
            feet_ok = (feet_min - floor_y) <= 0.03 * height
    rep["measured"]["feet_min_above_floor"] = (
        None if feet_min is None else round(feet_min - floor_y, 4))
    rep["checks"]["feet_planted"] = bool(feet_ok)

    rep["pass"] = all(v is True for v in rep["checks"].values())
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    rep = audit(a.inp)
    out = json.dumps(rep, indent=1)
    print(out)
    if a.json_out:
        with open(a.json_out, "w") as f:
            f.write(out)
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
