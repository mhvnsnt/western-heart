#!/usr/bin/env python3
"""tools/auto_rig/anim_check.py — headless retarget/animation validator.

Reads a GLB's animations, evaluates forward kinematics per frame (pure
python + numpy, no Blender), and flags the three retarget failure modes that
keep recurring in WH mocap retargets (2026-10-19):

  1. BONE-LENGTH VARIANCE — bones are rigid. If any bone's length varies more
     than --bone-var (default 2%) of its rest length across frames, the
     retarget is baking scale keys onto bones, animating the wrong nodes, or
     carrying a Z-up/Y-up (or rest-pose) mismatch. This is the signature of the
     "triangular tearing / stretching" renders.

  2. VERTEX TEARING — per-vertex frame-to-frame displacement spikes. A vertex
     that jumps > --tear-m (default 0.35 m) between consecutive sampled frames,
     or that moves > --tear-k x the frame's median vertex displacement (and
     > 0.10 m), means a skinning/bind disaster (unweighted vert snapping to
     origin, mismatched inverse-bind matrices, one-frame teleport). Reported
     with the mesh, frame, vertex index and its joint weights so the bad
     binding is diagnosable.

  3. EDGE STRETCH (p99.9) — triangle-edge length ratio vs the rest pose across
     all sampled frames; fail if p99.9 > --edge-max (default 2.5). This is the
     gate check #5 documented in validate.py's docstring, implemented here.

  4. ROOT OFFSET — the root joint's world position drifting > --root-max
     (default 1.0 m) from its bind position across the animation means a scene
     placement (or Y-up/Z-up mismatch) was baked into the clip; clips that
     teleport the character between animations fail. Joint translation drift
     is reported per joint (rotation-only joints must not translate).

Also reports ANIMATION ON WRONG NODES: channels targeting nodes that are not
joints and not ancestors of any joint do nothing at runtime (a found root
cause of the 2026-10-19 stretching incidents).

glTF animation semantics honored: translation/rotation/scale channels with
STEP, LINEAR and CUBICSPLINE interpolation; node-local matrix override.

Usage:
    python3 anim_check.py --in MODEL.glb [--anim NAME] [--json-out R.json]
        [--bone-var 0.02] [--tear-m 0.35] [--tear-k 8] [--edge-max 2.5]
        [--max-frames 120] [--quiet]
Exit 0 = pass, 1 = fail. Always writes a JSON report to stdout (--json-out too).

This is the headless, CI-friendly complement to the Blender-side retarget
backends in tools/auto_rig/backends/. It validates the OUTPUT of a retarget
(the shipped GLB), not the retargeting process itself.
"""

import argparse
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import read_glb  # noqa: E402  (reuses the auto_rig GLB reader)

try:
    import numpy as np
except ImportError:
    sys.stderr.write("anim_check.py requires numpy\n")
    sys.exit(2)

_COMP = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
         5125: ("I", 4), 5126: ("f", 4)}
_TYPE_N = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_accessor(js, bdat, idx):
    """Return a numpy view/array for accessor idx."""
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    fmt, size = _COMP[acc["componentType"]]
    n = _TYPE_N[acc["type"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or n * size
    count = acc["count"]
    raw = np.frombuffer(bdat, dtype=np.uint8, count=count * stride, offset=off)
    if stride == n * size and fmt in ("f",):
        arr = raw.view(np.float32).reshape(count, n) if n > 1 else raw.view(np.float32)
    else:
        arr = np.zeros((count, n if n > 1 else 1), dtype=np.float64)
        dt = np.dtype("<" + fmt)
        for i in range(count):
            arr[i] = np.frombuffer(raw, dtype=dt, count=n,
                                   offset=i * stride).astype(np.float64)
        if n == 1:
            arr = arr[:, 0]
    if acc.get("normalized"):
        arr = arr / float({"b": 127, "B": 255, "h": 32767, "H": 65535}[fmt])
    return arr


def quat_to_mat(q):
    x, y, z, w = q
    n = x * x + y * y + z * z + w * w
    if n < 1e-12:
        return np.eye(3)
    s = 2.0 / n
    return np.array([
        [1 - s * (y * y + z * z), s * (x * y - z * w), s * (x * z + y * w)],
        [s * (x * y + z * w), 1 - s * (x * x + z * z), s * (y * z - x * w)],
        [s * (x * z - y * w), s * (y * z + x * w), 1 - s * (x * x + y * y)],
    ])


def node_local_matrix(node):
    """Local 4x4 for a node from TRS or explicit matrix."""
    if "matrix" in node:
        return np.asarray(node["matrix"], dtype=np.float64).reshape(4, 4).T
    t = np.asarray(node.get("translation", [0, 0, 0]), dtype=np.float64)
    q = np.asarray(node.get("rotation", [0, 0, 0, 1]), dtype=np.float64)
    s = np.asarray(node.get("scale", [1, 1, 1]), dtype=np.float64)
    m = np.eye(4)
    m[:3, :3] = quat_to_mat(q) * s
    m[:3, 3] = t
    return m


def topo_order(nodes, roots):
    order, seen = [], set()

    def visit(i):
        if i in seen:
            return
        seen.add(i)
        order.append(i)
        for c in nodes[i].get("children", []):
            visit(c)

    for r in roots:
        visit(r)
    for i in range(len(nodes)):
        if i not in seen:
            visit(i)
    return order


def sample_channel(times, values, path, interp, t):
    n = len(times)
    if t <= times[0]:
        i, f = 0, 0.0
    elif t >= times[-1]:
        i, f = n - 2 if n > 1 else 0, 1.0
    else:
        i = int(np.searchsorted(times, t, side="right")) - 1
        f = (t - times[i]) / max(times[i + 1] - times[i], 1e-12)
    if interp == "STEP" or n == 1:
        return _out(values, path, interp, i, 0.0, 1.0)
    dt = times[i + 1] - times[i] if i + 1 < n else 1.0
    return _out(values, path, interp, i, f, dt)


def _out(values, path, interp, i, f, dt):
    if interp == "CUBICSPLINE":
        # values[k] = (in-tangent, value, out-tangent) per keyframe (glTF spec)
        v0, t0_out = values[i][1], values[i][2]
        v1, t1_in = values[i + 1][1], values[i + 1][0]
        h00 = 2 * f ** 3 - 3 * f ** 2 + 1
        h10 = f ** 3 - 2 * f ** 2 + f
        h01 = -2 * f ** 3 + 3 * f ** 2
        h11 = f ** 3 - f ** 2
        v = (h00 * v0 + h10 * dt * t0_out + h01 * v1 + h11 * dt * t1_in)
        if path == "rotation":
            nrm = np.linalg.norm(v)
            v = v / nrm if nrm > 1e-12 else np.array([0, 0, 0, 1.0])
        return v
    v0, v1 = values[i], values[min(i + 1, len(values) - 1)]
    if path == "rotation":
        # slerp
        d = float(np.dot(v0, v1))
        if d < 0:
            v1, d = -v1, -d
        d = min(max(d, -1.0), 1.0)
        if d > 0.9995:
            v = v0 + f * (v1 - v0)
        else:
            th = np.arccos(d)
            s = np.sin(th)
            v = (np.sin((1 - f) * th) / s) * v0 + (np.sin(f * th) / s) * v1
        return v / np.linalg.norm(v)
    return (1 - f) * v0 + f * v1


class AnimModel:
    """GLB + skin + animation sampler evaluation, headless."""

    def __init__(self, path):
        self.path = path
        self.js, self.bdat = read_glb(path)
        self.nodes = self.js.get("nodes", [])
        self.roots = [i for i, nd in enumerate(self.nodes)]
        childed = set()
        for nd in self.nodes:
            childed.update(nd.get("children", []))
        self.roots = [i for i in range(len(self.nodes)) if i not in childed]
        self.order = topo_order(self.nodes, self.roots)
        self.skins = self.js.get("skins", [])
        self.joint_nodes = self.skins[0]["joints"] if self.skins else []
        self.joint_set = set(self.joint_nodes)
        # ancestors of joints (root motion etc. legitimately lives here)
        self.joint_ancestors = set()
        parent = {}
        for i, nd in enumerate(self.nodes):
            for c in nd.get("children", []):
                parent[c] = i
        for j in self.joint_nodes:
            p = parent.get(j)
            while p is not None:
                self.joint_ancestors.add(p)
                p = parent.get(p)
        # skinned primitive data (first skinned primitive found)
        self.pos = self.idx = self.joints = self.weights = None
        self.ibm = None
        self._load_skin_data()

    def _load_skin_data(self):
        # ALL skinned primitives (multi-part exports like pantera.glb have
        # ~18; checking only the first would miss a torn part mesh)
        self.prims = []
        for mesh in self.js.get("meshes", []):
            for prim in mesh.get("primitives", []):
                at = prim.get("attributes", {})
                if "JOINTS_0" in at and "POSITION" in at:
                    pos = np.asarray(
                        read_accessor(self.js, self.bdat, at["POSITION"]),
                        dtype=np.float64).reshape(-1, 3)
                    idx = None
                    if "indices" in prim:
                        idx = np.asarray(
                            read_accessor(self.js, self.bdat, prim["indices"]),
                            dtype=np.int64).reshape(-1)
                    joints = np.asarray(
                        read_accessor(self.js, self.bdat, at["JOINTS_0"]),
                        dtype=np.int64).reshape(-1, 4)
                    w = np.asarray(read_accessor(self.js, self.bdat,
                                                 at["WEIGHTS_0"]),
                                   dtype=np.float64).reshape(-1, 4)
                    ws = w.sum(axis=1, keepdims=True)
                    ws[ws == 0] = 1.0
                    self.prims.append({"pos": pos, "idx": idx,
                                       "joints": joints, "weights": w / ws})
        if self.prims:
            p0 = self.prims[0]
            self.pos, self.idx = p0["pos"], p0["idx"]
            self.joints, self.weights = p0["joints"], p0["weights"]
        if self.skins and "inverseBindMatrices" in self.skins[0]:
            # glTF MAT4 accessors are COLUMN-major: transpose each matrix.
            self.ibm = np.asarray(read_accessor(
                self.js, self.bdat, self.skins[0]["inverseBindMatrices"]),
                dtype=np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
        elif self.joint_nodes:
            self.ibm = np.repeat(np.eye(4)[None], len(self.joint_nodes), 0)

    def bind_world(self):
        """World matrices at bind (authored node transforms, no animation)."""
        out, par = {}, {}
        for i, nd in enumerate(self.nodes):
            for c in nd.get("children", []):
                par[c] = i
        for i in self.order:
            m = node_local_matrix(self.nodes[i])
            out[i] = (out[par[i]] @ m) if i in par else m
        return out

    def animation_frames(self, anim, max_frames):
        """Collect per-node TRS samplers; return (times, list of (node, path, times, values, interp))."""
        samplers = anim.get("samplers", [])
        chans = []
        for ch in anim.get("channels", []):
            tgt = ch.get("target", {})
            node, path = tgt.get("node"), tgt.get("path")
            if node is None or path not in ("translation", "rotation", "scale"):
                continue
            s = samplers[ch["sampler"]]
            times = np.asarray(read_accessor(self.js, self.bdat, s["input"]),
                               dtype=np.float64).ravel()
            vals = np.asarray(read_accessor(self.js, self.bdat, s["output"]),
                              dtype=np.float64)
            per = 3 if path == "translation" else (4 if path == "rotation" else 3)
            mult = 3 if s.get("interpolation") == "CUBICSPLINE" else 1
            vals = vals.reshape(-1, mult * per)
            if s.get("interpolation") == "CUBICSPLINE":
                vals = vals.reshape(-1, 3, per)
            chans.append((node, path, times, vals,
                          s.get("interpolation", "LINEAR")))
        times = np.unique(np.concatenate([c[2] for c in chans])) if chans else np.array([0.0])
        if len(times) > max_frames:
            sel = np.linspace(0, len(times) - 1, max_frames).astype(int)
            times = times[np.unique(sel)]
        return times, chans

    def eval_world(self, chans, t):
        """World matrices for all nodes at time t."""
        # current local values
        loc = {}
        for i, nd in enumerate(self.nodes):
            loc[i] = (np.asarray(nd.get("translation", [0, 0, 0]), float),
                      np.asarray(nd.get("rotation", [0, 0, 0, 1]), float),
                      np.asarray(nd.get("scale", [1, 1, 1]), float),
                      "matrix" in nd and np.asarray(nd["matrix"], float).reshape(4, 4).T or None)
        for node, path, times, vals, interp in chans:
            v = sample_channel(times, vals, path, interp, t)
            tr, ro, sc, mx = loc[node]
            if path == "translation":
                tr = v
            elif path == "rotation":
                ro = v
            else:
                sc = v
            loc[node] = (tr, ro, sc, None)
        world, par = {}, {}
        for i, nd in enumerate(self.nodes):
            for c in nd.get("children", []):
                par[c] = i
        for i in self.order:
            tr, ro, sc, mx = loc[i]
            if mx is not None:
                m = mx
            else:
                m = np.eye(4)
                m[:3, :3] = quat_to_mat(ro) * sc
                m[:3, 3] = tr
            world[i] = (world[par[i]] @ m) if i in par else m
        return world

    def bone_pairs(self):
        pairs = []
        for j in self.joint_nodes:
            for c in self.nodes[j].get("children", []):
                if c in self.joint_set:
                    pairs.append((self.nodes[j].get("name", f"j{j}"),
                                  self.nodes[c].get("name", f"j{c}"), j, c))
        return pairs


def check_animation(model, anim, args):
    name = anim.get("name", "?")
    rep = {"name": name, "frames": 0, "pass": True, "failures": []}
    times, chans = model.animation_frames(anim, args.max_frames)
    rep["frames"] = len(times)

    # wrong-node detection (before any math)
    animated = {c[0] for c in chans}
    wrong = sorted(n for n in animated
                   if n not in model.joint_set and n not in model.joint_ancestors)
    rep["channels_on_non_joint_nodes"] = [
        model.nodes[n].get("name", f"node{n}") for n in wrong]
    if wrong:
        rep["failures"].append(
            f"{len(wrong)} channel(s) animate nodes that are neither joints "
            f"nor joint ancestors (do nothing at runtime): "
            f"{rep['channels_on_non_joint_nodes'][:6]}")
    static_joints = [model.nodes[j].get("name", f"j{j}")
                     for j in model.joint_nodes if j not in animated]
    rep["unanimated_joints"] = len(static_joints)

    if not model.joint_nodes:
        rep["failures"].append("no skins/joints: nothing to check")
        rep["pass"] = False
        return rep

    bind = model.bind_world()
    jp = {j: (bind[j][:3, 3]) for j in model.joint_nodes}
    pairs = model.bone_pairs()
    # bone identity = (parent joint name, child joint name): a parent with
    # several joint children (Hips->both legs, Hand->5 fingers) must NEVER
    # share one min/max bucket, or cross-bone length differences read as
    # per-frame variance.
    rest_len = {(pname, cname): float(np.linalg.norm(jp[c] - jp[p]))
                for pname, cname, p, c in pairs}
    bone_min = {b: float("inf") for b in rest_len}
    bone_max = {b: 0.0 for b in rest_len}
    bone_sum = {b: 0.0 for b in rest_len}
    n_frames = max(len(times), 1)

    # per-frame FK (bone lengths) — cheap, use every sampled frame
    for t in times:
        w = model.eval_world(chans, t)
        pos = {j: w[j][:3, 3] for j in model.joint_nodes}
        for pname, cname, p, c in pairs:
            L = float(np.linalg.norm(pos[c] - pos[p]))
            key = (pname, cname)
            if L < bone_min[key]:
                bone_min[key] = L
            if L > bone_max[key]:
                bone_max[key] = L
            bone_sum[key] += L

    bones, flagged, rest_flagged = {}, [], []
    for (pname, cname), r in rest_len.items():
        bname = f"{pname}->{cname}"
        if r < 1e-9:
            continue
        key = (pname, cname)
        var = (bone_max[key] - bone_min[key]) / r
        mean = bone_sum[key] / n_frames
        rest_dev = abs(mean - r) / r
        bones[bname] = {"rest_m": round(r, 4),
                        "min_m": round(bone_min[key], 4),
                        "max_m": round(bone_max[key], 4),
                        "mean_m": round(mean, 4),
                        "var": round(var, 4),
                        "rest_dev": round(rest_dev, 4)}
        if var > args.bone_var:
            flagged.append((bname, var))
        elif rest_dev > args.bone_var:
            rest_flagged.append((bname, rest_dev))
    # 4. ROOT-OFFSET / joint translation drift: joints other than the root
    #    should animate by ROTATION, not translation (translation keys on
    #    mid-chain joints = BVH-style retarget baked wrong for a game rig).
    #    The root joint's world position wandering far from its bind position
    #    (e.g. a scene placement baked into one clip, as in pantera.glb Idle
    #    vs its Run/Walk/TPose) teleports the character between clips.
    joint_par = {}
    for j in model.joint_nodes:
        joint_par[j] = None
    for j in model.joint_nodes:
        for c in model.nodes[j].get("children", []):
            if c in model.joint_set:
                joint_par[c] = j
    root_joint = next(j for j in model.joint_nodes if joint_par[j] is None)
    root_dev = 0.0
    joint_devs = {}
    for t in times:
        w = model.eval_world(chans, t)
        for j in model.joint_nodes:
            d = float(np.linalg.norm(w[j][:3, 3] - jp[j]))
            if d > joint_devs.get(j, 0.0):
                joint_devs[j] = d
    root_dev = joint_devs.get(root_joint, 0.0)
    rep["root_joint"] = model.nodes[root_joint].get("name", f"j{root_joint}")
    rep["root_max_dev_m"] = round(root_dev, 4)
    rep["joint_trans_devs"] = sorted(
        [{"joint": model.nodes[j].get("name", f"j{j}"),
          "max_dev_m": round(d, 4)} for j, d in joint_devs.items()],
        key=lambda x: -x["max_dev_m"])[:8]
    if root_dev > args.root_max:
        rep["failures"].append(
            f"root joint '{rep['root_joint']}' wanders {root_dev:.2f} m from "
            f"its bind position (> {args.root_max} m) — scene placement baked "
            f"into the clip, or Y-up/Z-up root mismatch")
    rep["bones_checked"] = len(bones)
    rep["bones"] = bones
    rep["bones_flagged"] = [{"bone": b, "var": round(v, 4)}
                            for b, v in sorted(flagged, key=lambda x: -x[1])]
    rep["bones_rest_deviant"] = [{"bone": b, "rest_dev": round(v, 4)}
                                 for b, v in sorted(rest_flagged, key=lambda x: -x[1])]
    if flagged:
        worst = max(flagged, key=lambda x: x[1])
        rep["failures"].append(
            f"{len(flagged)} bone(s) vary > {args.bone_var * 100:.1f}% of rest "
            f"length across frames (worst: {worst[0]} "
            f"{worst[1] * 100:.1f}%) — rigid bones must not stretch")
    if rest_flagged:
        worst = max(rest_flagged, key=lambda x: x[1])
        rep["failures"].append(
            f"{len(rest_flagged)} bone(s) hold a mean length "
            f"> {args.bone_var * 100:.1f}% off their rest length through the "
            f"whole animation (worst: {worst[0]} "
            f"{worst[1] * 100:.1f}%) — baked scale or rest-pose mismatch")

    # skinned vertex tearing + edge stretch — across ALL skinned primitives
    tearing = {"max_disp_m": 0.0, "spikes": []}
    edge_p999 = None
    if model.prims and model.ibm is not None:
        jidx = np.array(model.joint_nodes)
        # FK once per frame (shared by every mesh part), skin matrices too
        frame_worlds = [model.eval_world(chans, t) for t in times]
        frame_skin = [np.stack([w[int(j)] @ model.ibm[k]
                                for k, j in enumerate(jidx)])
                      for w in frame_worlds]
        bind_skin = np.stack([bind[int(j)] @ model.ibm[k]
                              for k, j in enumerate(jidx)])

        # model scale for the edge filter: skinned rest bbox across all prims
        rest_bbox = []
        for prim in model.prims:
            pos_h = np.concatenate([prim["pos"], np.ones((len(prim["pos"]), 1))], 1)
            sk = _skin(model, bind_skin, prim, pos_h)
            rest_bbox.append(sk)
        rest_bbox = np.concatenate(rest_bbox)
        model_height = float((rest_bbox.max(0) - rest_bbox.min(0)).max())
        edge_min = max(0.001, 0.005 * model_height)  # below this, ratios are noise
        rep["model_height_m"] = round(model_height, 3)

        ratios = []
        rep["meshes_checked"] = len(model.prims)
        edge_worst = 0.0
        edge_worst_mesh = None
        for mi, prim in enumerate(model.prims):
            pos_h = np.concatenate(
                [prim["pos"], np.ones((len(prim["pos"]), 1))], 1)
            edges = None
            if prim["idx"] is not None:
                tris = prim["idx"].reshape(-1, 3)
                e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]],
                                    tris[:, [2, 0]]])
                e = np.sort(e, 1)
                edges = np.unique(e, axis=0)
            # rest-pose SKINNED positions (bind world * inverse-bind * pos)
            skin_rest = _skin(model, bind_skin, prim, pos_h)
            if edges is not None:
                rest_e = np.linalg.norm(
                    skin_rest[edges[:, 0]] - skin_rest[edges[:, 1]], axis=1)
                keep = rest_e >= edge_min
                edges = edges[keep]
                rest_e = rest_e[keep]
            prev = None  # tearing compares CONSECUTIVE frames only
            for fi in range(len(times)):
                t = times[fi]
                cur = _skin(model, frame_skin[fi], prim, pos_h)
                if prev is not None:
                    disp = np.linalg.norm(cur - prev, axis=1)
                    med = float(np.median(disp))
                    # A vertex tears if it jumps an inhuman distance in one
                    # step (> tear_m at the sampled rate), OR if it is a
                    # strong local outlier in an otherwise calm frame
                    # (> tear_k x frame median, and > 0.10 m so subdivision
                    # noise on dense meshes never trips it).
                    bad = np.nonzero((disp > args.tear_m) |
                                     ((disp > args.tear_k * med) &
                                      (disp > 0.10)))[0]
                    md = float(disp.max())
                    if md > tearing["max_disp_m"]:
                        tearing["max_disp_m"] = round(md, 4)
                    for v in bad[:10]:
                        tearing["spikes"].append({
                            "mesh": mi,
                            "time": round(float(t), 4),
                            "vertex": int(v),
                            "disp_m": round(float(disp[v]), 4),
                            "frame_median_m": round(med, 5),
                            # the vertex's own joints: JOINTS_0 slot -> skin joint -> node
                            # (indexing jidx by the SLOT number named skin joints 0-3, i.e.
                            # "Hips, Spine" for every vertex; fixed 2026-10-31)
                            "joints": [model.nodes[int(jidx[int(prim["joints"][v][k])])].get(
                                "name", f"j{int(jidx[int(prim['joints'][v][k])])}")
                                for k in np.nonzero(
                                    prim["weights"][v] > 1e-4)[0][:4]],
                            "weights": [round(float(x), 3) for x in
                                        prim["weights"][v][
                                            prim["weights"][v] > 1e-4][:4]],
                        })
                if edges is not None:
                    el = np.linalg.norm(cur[edges[:, 0]] - cur[edges[:, 1]],
                                        axis=1)
                    ratios.append(el / rest_e)
                prev = cur
        if ratios:
            allr = np.concatenate(ratios)
            edge_p999 = float(np.percentile(allr, 99.9))
            rep["edge_stretch_p999"] = round(edge_p999, 3)
            rep["edge_stretch_max"] = round(float(allr.max()), 3)
            rep["edge_min_m"] = edge_min
            if edge_p999 > args.edge_max:
                rep["failures"].append(
                    f"p99.9 triangle-edge stretch {edge_p999:.2f} > {args.edge_max} "
                    f"(rest-pose ratio; edges < {edge_min * 1000:.1f} mm excluded)")
        else:
            rep["edge_stretch_p999"] = None
    else:
        rep["note"] = "no skinned mesh data; tearing/edge checks skipped"
    rep["tearing"] = tearing
    if tearing["spikes"]:
        rep["failures"].append(
            f"{len(tearing['spikes'])} vertex displacement spike(s) "
            f"(> {args.tear_m} m in one step, or > {args.tear_k}x the frame "
            f"median and > 0.10 m) — tearing")
    rep["pass"] = not rep["failures"]
    return rep


def _skin(model, skin_m, prim, pos_h):
    """skinned = sum_i w_i * skin_m[j_i] @ pos  (skin_m precomputed per frame)."""
    J = skin_m.shape[0]
    ji = np.clip(prim["joints"], 0, J - 1)
    M = skin_m[ji]  # V,4,4,4
    out = np.einsum("vijk,vk->vij", M, pos_h)  # V,4,4 (joint transforms of pos)
    skinned = np.einsum("vij,vi->vj", out, prim["weights"])  # V,4
    return skinned[:, :3]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--anim", default=None, help="check only this animation")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--bone-var", type=float, default=0.02)
    ap.add_argument("--tear-m", type=float, default=0.35)
    ap.add_argument("--tear-k", type=float, default=8.0)
    ap.add_argument("--edge-max", type=float, default=2.5)
    ap.add_argument("--root-max", type=float, default=1.0,
                    help="max root-joint bind-position drift (m) before flagging")
    ap.add_argument("--max-frames", type=int, default=120)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    model = AnimModel(a.inp)
    anims = model.js.get("animations", [])
    if a.anim:
        anims = [x for x in anims if x.get("name") == a.anim]
        if not anims:
            sys.stderr.write(f"animation {a.anim!r} not found\n")
            sys.exit(2)
    report = {"file": a.inp, "animations": {}, "pass": True,
              "thresholds": {"bone_var": a.bone_var, "tear_m": a.tear_m,
                             "tear_k": a.tear_k, "edge_max": a.edge_max,
                             "max_frames": a.max_frames}}
    for anim in anims:
        r = check_animation(model, anim, a)
        report["animations"][anim.get("name", "?")] = r
        if not r["pass"]:
            report["pass"] = False
    if not anims:
        report["pass"] = False
        report["error"] = "no animations in file"
    out = json.dumps(report, indent=2)
    if not a.quiet:
        print(out)
    if a.json_out:
        with open(a.json_out, "w") as f:
            f.write(out)
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
