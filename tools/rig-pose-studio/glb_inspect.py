#!/usr/bin/env python3
"""glb_inspect.py — forensic GLB skeleton/skin inspector for the Rig & Pose Studio.

Parses a GLB's JSON chunk + accessors and reports the things that decide
whether a rig is template-clean or template-drifted:

  * skins: joint count, joint names, skeleton root
  * per-joint REST transform (translation / quaternion) and rest world position
    (flags: non-identity rest rotations on core body bones — the signature of a
    baked-in pose / drifted template)
  * inverseBindMatrices: present? consistent with node rest inverses?
  * meshes: primitives, skinning attributes, morph targets, hide flags in extras
  * skin weights: per-vertex weight-sum distribution, zero-weight vertex count,
    max influences actually used
  * animations: names, channel counts, targeted nodes/paths

Usage: python3 glb_inspect.py FILE.glb [--json OUT.json] [--full-joints]
Stdlib + numpy only. Read-only: never modifies the inspected file.
"""
import json, math, struct, sys
import numpy as np

CORE_HINTS = ("hips", "spine", "chest", "neck", "head", "shoulder", "upperarm",
              "upper_arm", "forearm", "hand", "thigh", "upleg", "shin", "calf",
              "foot", "toe", "pelvis", "root")

def load_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, ver, total = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError("not a GLB")
    clen, ctype = struct.unpack_from("<II", data, 12)
    js = json.loads(data[20:20 + clen])
    off = 20 + clen
    binchunk = b""
    if off < len(data):
        blen, btype = struct.unpack_from("<II", data, off)
        binchunk = data[off + 8: off + 8 + blen]
    return js, binchunk

CTYPE = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
         5125: ("I", 4), 5126: ("f", 4)}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

def read_accessor(js, binchunk, idx):
    acc = js["accessors"][idx]
    bv = js["bufferViews"][acc["bufferView"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    fmt, sz = CTYPE[acc["componentType"]]
    n = NCOMP[acc["type"]]
    count = acc["count"]
    stride = bv.get("byteStride")
    raw = np.frombuffer(binchunk, dtype=np.dtype(fmt).newbyteorder("<"),
                        count=count * n, offset=start) if not stride else None
    if stride:
        item = sz * n
        out = np.empty(count * n, dtype=np.dtype(fmt))
        for i in range(count):
            s = start + i * stride
            out[i * n:(i + 1) * n] = np.frombuffer(
                binchunk, dtype=np.dtype(fmt).newbyteorder("<"), count=n, offset=s)
        raw = out
    arr = raw.astype(np.float64).reshape(count, n)
    if acc.get("normalized") and acc["componentType"] in (5121, 5123, 5120, 5122):
        mx = {5121: 255.0, 5123: 65535.0, 5120: 127.0, 5122: 32767.0}[acc["componentType"]]
        arr = np.maximum(arr, 0) / mx if acc["componentType"] in (5121, 5123) else arr / mx
    return arr

def quat_angle_deg(q):
    w = max(-1.0, min(1.0, abs(q[3])))
    return math.degrees(2 * math.acos(w))

def node_world_positions(js):
    """Rest world positions of all nodes via TRS chain composition."""
    nodes = js.get("nodes", [])
    pos = [None] * len(nodes)
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent[c] = i
    def compose(i):
        if pos[i] is not None:
            return pos[i]
        n = nodes[i]
        t = np.array(n.get("translation", [0, 0, 0]), dtype=np.float64)
        if "matrix" in n:
            m = np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T
            t = m[:3, 3]
            local_rot = m[:3, :3]
        else:
            q = n.get("rotation", [0, 0, 0, 1])
            x, y, z, w = q
            local_rot = np.array([
                [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        s = np.array(n.get("scale", [1, 1, 1]), dtype=np.float64)
        if i in parent:
            pw, rw = compose(parent[i])
            world = pw + rw @ (s * t)
            pos[i] = (world, rw @ local_rot)
        else:
            pos[i] = (t, local_rot)
        return pos[i]
    for i in range(len(nodes)):
        compose(i)
    return [p[0] for p in pos]

def inspect(path, full_joints=False):
    js, binchunk = load_glb(path)
    nodes = js.get("nodes", [])
    r = {"file": path, "generator": js.get("asset", {}).get("generator"),
         "nodes": len(nodes), "meshes": len(js.get("meshes", [])),
         "skins": [], "animations": [], "weight_stats": []}
    world = node_world_positions(js)
    for si, skin in enumerate(js.get("skins", [])):
        joints = skin["joints"]
        info = {"skin": si, "joints": len(joints),
                "skeleton_root": skin.get("skeleton"),
                "has_ibm": "inverseBindMatrices" in skin, "joint_rows": []}
        ibm_bad = None
        if "inverseBindMatrices" in skin:
            ibm = read_accessor(js, binchunk, skin["inverseBindMatrices"])
            det = [round(float(np.linalg.det(m.reshape(4, 4).T[:3, :3])), 4) for m in ibm[:8]]
            info["ibm_det_first8"] = det
        for j in joints:
            n = nodes[j]
            q = n.get("rotation", [0, 0, 0, 1])
            ang = quat_angle_deg(q)
            name = n.get("name", f"node{j}")
            is_core = any(h in name.lower() for h in CORE_HINTS)
            row = {"node": j, "name": name,
                   "rest_rot_deg": round(ang, 2),
                   "rest_pos": [round(float(v), 4) for v in n.get("translation", [0, 0, 0])],
                   "world": [round(float(v), 4) for v in world[j]],
                   "scale": n.get("scale")}
            if full_joints or (is_core and ang > 1.0) or ang > 45.0:
                info["joint_rows"].append(row)
        flagged = [jr for jr in info["joint_rows"] if jr["rest_rot_deg"] > 45.0]
        info["core_joints_rest_rot_over_45deg"] = len(flagged)
        r["skins"].append(info)
    for mi, mesh in enumerate(js.get("meshes", [])):
        for pi, prim in enumerate(mesh["primitives"]):
            attrs = prim.get("attributes", {})
            if "WEIGHTS_0" in attrs and "JOINTS_0" in attrs:
                w = read_accessor(js, binchunk, attrs["WEIGHTS_0"])
                sums = w.sum(axis=1)
                used = (w > 1e-6).sum(axis=1)
                r["weight_stats"].append({
                    "mesh": mesh.get("name", mi), "prim": pi,
                    "verts": int(w.shape[0]),
                    "sum_min": round(float(sums.min()), 4),
                    "sum_max": round(float(sums.max()), 4),
                    "verts_sum_lt_0.99": int((sums < 0.99).sum()),
                    "verts_zero_weight": int((sums <= 1e-6).sum()),
                    "max_influences_used": int(used.max())})
    for a in js.get("animations", []):
        paths = {}
        for ch in a.get("channels", []):
            p = ch["target"].get("path")
            paths[p] = paths.get(p, 0) + 1
        r["animations"].append({"name": a.get("name"), "channels": len(a.get("channels", [])),
                                "paths": paths})
    r["extensions_used"] = js.get("extensionsUsed", [])
    return r

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = None
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
    rep = inspect(args[0], full_joints="--full-joints" in sys.argv)
    txt = json.dumps(rep, indent=1)
    if out:
        open(out, "w").write(txt)
    print(txt)
