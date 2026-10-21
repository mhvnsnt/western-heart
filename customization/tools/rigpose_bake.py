#!/usr/bin/env python3
"""rigpose_bake.py — Rig & Pose Studio bake stage for the Creation Suite.

Applies the `rig` section of a per-attire customization.json to a base GLB
and writes the baked GLB. This is the owner's manual rig/pose control made
real: every edit the suite's rig/pose mode can express is replayed here,
deterministically, from the saved JSON — edit → save → reload → bake
reproduces the identical file.

Supported `rig` operations (schema: customization/CUSTOMIZATION-JSON-SCHEMA.md
§ Rig & Pose):

  bones: { "<bone name>": {
      "offset":  {"pos":[x,y,z], "rot_deg":[pitch,yaw,roll], "scale":[x,y,z]},
      "visible": true|false            # bone shown in suite (editor-only)
  }}
  add_bones:    [{"name":..., "parent":..., "head":[x,y,z], "tail":[x,y,z]}]
  remove_bones: ["<bone name>", ...]   # skin joints re-mapped; verts bound
                                       # only to a removed bone fall back to
                                       # its parent (weights renormalized)
  weights:      [{"bone":..., "center":[x,y,z], "radius":r,
                  "strength":0..1, "mode":"add"|"set"}]   # brush strokes,
                                       # replayed in order, deterministic
  visibility:   {"<mesh or node name>": true|false}        # false = excluded
                                       # from the baked scene
  pose:         {"<bone name>": {"rot_deg":[pitch,yaw,roll],
                                 "pos":[x,y,z]}}          # a static pose
                                       # baked INTO the rest pose (stance)

Math contract: after any rest edit, every skin's inverseBindMatrices are
RECOMPUTED from the edited node world rests (IBM = inverse(world rest)), so
the skinned mesh is untouched in world space by rest edits alone — the edit
changes what the skeleton's zero-pose IS, which is exactly what fixing a
drifted rest frame means. Pose entries are applied as rest edits too (a
baked stance), which is how a stance set in the studio reaches the game.

Usage:
  python3 rigpose_bake.py --base IN.glb --custom CUSTOMIZATION.json \
      --out OUT.glb [--report REPORT.json]
Stdlib + numpy. Never modifies --base.
"""
import argparse, json, math, struct, sys
import numpy as np

# ---------- GLB container ----------
def load_glb(path):
    data = open(path, "rb").read()
    magic, _ver, _total = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError("not a GLB")
    clen, _ct = struct.unpack_from("<II", data, 12)
    js = json.loads(data[20:20 + clen])
    off = 20 + clen
    binchunk = b""
    if off < len(data):
        blen, _bt = struct.unpack_from("<II", data, off)
        binchunk = bytearray(data[off + 8: off + 8 + blen])
    return js, binchunk

def save_glb(path, js, binchunk):
    jb = json.dumps(js, separators=(",", ":")).encode()
    jb += b" " * ((4 - len(jb) % 4) % 4)
    bb = bytes(binchunk)
    bb += b"\x00" * ((4 - len(bb) % 4) % 4)
    total = 12 + 8 + len(jb) + 8 + len(bb)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A)); f.write(jb)
        f.write(struct.pack("<II", len(bb), 0x004E4942)); f.write(bb)

# ---------- accessors ----------
CTYPE = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2),
         5125: ("I", 4), 5126: ("f", 4)}
RTYPE = {v[0]: k for k, v in CTYPE.items()}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

def read_acc(js, buf, idx):
    acc = js["accessors"][idx]; bv = js["bufferViews"][acc["bufferView"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    fmt, sz = CTYPE[acc["componentType"]]; n = NCOMP[acc["type"]]
    dt = np.dtype(fmt).newbyteorder("<")
    stride = bv.get("byteStride")
    if stride and stride != sz * n:
        out = np.empty((acc["count"], n), dtype=np.float64)
        for i in range(acc["count"]):
            out[i] = np.frombuffer(buf, dtype=dt, count=n, offset=start + i * stride)
        arr = out
    else:
        arr = np.frombuffer(buf, dtype=dt, count=acc["count"] * n,
                            offset=start).astype(np.float64).reshape(acc["count"], n)
    if acc.get("normalized") and acc["componentType"] in (5121, 5123):
        arr = arr / (255.0 if acc["componentType"] == 5121 else 65535.0)
    return arr

def append_acc(js, buf, arr, acc_type, component="f"):
    """Append a new accessor+bufferView holding arr (float32 or uint16)."""
    arr = np.asarray(arr)
    if component == "f":
        raw = arr.astype("<f4").tobytes(); ct = 5126
    else:
        raw = arr.astype("<u2").tobytes(); ct = 5123
    pad = (4 - len(buf) % 4) % 4
    if pad: buf.extend(b"\x00" * pad)
    off = len(buf); buf.extend(raw)
    js.setdefault("bufferViews", []).append(
        {"buffer": 0, "byteOffset": off, "byteLength": len(raw)})
    js.setdefault("accessors", []).append(
        {"bufferView": len(js["bufferViews"]) - 1, "componentType": ct,
         "count": int(arr.shape[0]), "type": acc_type})
    return len(js["accessors"]) - 1

def write_acc_inplace(js, buf, idx, arr, component="f"):
    acc = js["accessors"][idx]; bv = js["bufferViews"][acc["bufferView"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    if component == "f":
        raw = np.asarray(arr).astype("<f4").tobytes()
    else:
        raw = np.asarray(arr).astype("<u2").tobytes()
    assert len(raw) <= bv["byteLength"], "replacement larger than original accessor"
    buf[start:start + len(raw)] = raw

# ---------- math ----------
def euler_deg_to_quat(pitch, yaw, roll):
    """XYZ intrinsic euler degrees -> quaternion [x,y,z,w] (suite convention:
    pitch about X, yaw about Y, roll about Z, applied Z then Y then X)."""
    def q(axis, deg):
        h = math.radians(deg) / 2.0
        s, c = math.sin(h), math.cos(h)
        return np.array([s if axis == 0 else 0, s if axis == 1 else 0,
                         s if axis == 2 else 0, c], dtype=np.float64)
    def mul(a, b):
        x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
        return np.array([w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                         w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                         w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
                         w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2])
    return mul(mul(q(0, pitch), q(1, yaw)), q(2, roll))

def quat_mul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return np.array([w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
                     w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2])

def quat_to_mat(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])

def node_local_mat(n):
    if "matrix" in n:
        return np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T.copy()
    m = np.eye(4)
    m[:3, :3] = quat_to_mat(n.get("rotation", [0, 0, 0, 1])) @ np.diag(n.get("scale", [1, 1, 1]))
    m[:3, 3] = n.get("translation", [0, 0, 0])
    return m

def world_mats(js):
    nodes = js["nodes"]; parent = {}
    for i, n in enumerate(nodes):
        for c in n.get("children", []):
            parent[c] = i
    world = [None] * len(nodes)
    def comp(i):
        if world[i] is None:
            lm = node_local_mat(nodes[i])
            world[i] = comp(parent[i]) @ lm if i in parent else lm
        return world[i]
    for i in range(len(nodes)):
        comp(i)
    return world

# ---------- bake ----------
def bake(base_path, custom, out_path):
    js, buf = load_glb(base_path)
    nodes = js["nodes"]
    by_name = {}
    for i, n in enumerate(nodes):
        if "name" in n:
            by_name.setdefault(n["name"], i)
    rig = custom.get("rig", {}) or {}
    report = {"ops": [], "warnings": []}

    def node_of(name):
        if name not in by_name:
            report["warnings"].append(f"bone not found: {name}")
            return None
        return by_name[name]

    # 1) add bones (parents must exist; head is parent-local)
    for spec in rig.get("add_bones", []):
        p = node_of(spec["parent"])
        if p is None: continue
        head = np.array(spec["head"], dtype=np.float64)
        idx = len(nodes)
        nodes.append({"name": spec["name"], "translation": head.tolist()})
        nodes[p].setdefault("children", []).append(idx)
        by_name[spec["name"]] = idx
        for skin in js.get("skins", []):
            if p in skin["joints"]:
                skin["joints"].append(idx)
        report["ops"].append(f"add_bone {spec['name']} parent={spec['parent']}")

    # helper: apply a local TRS offset to a node (decompose-safe: we rewrite
    # the node's TRS from its current local matrix with the offset applied
    # in local space: L' = L @ Offset)
    def apply_offset(ni, off):
        n = nodes[ni]
        lm = node_local_mat(n)
        om = np.eye(4)
        if "rot_deg" in off:
            om[:3, :3] = quat_to_mat(euler_deg_to_quat(*off["rot_deg"]))
        if "scale" in off:
            om[:3, :3] = om[:3, :3] @ np.diag(off["scale"])
        if "pos" in off:
            om[:3, 3] = off["pos"]
        new = lm @ om
        # decompose (uniform-ish scale assumed; take column norms)
        rot = new[:3, :3]
        sc = np.linalg.norm(rot, axis=0)
        rot = rot / sc
        # rotation matrix -> quaternion
        tr = np.trace(rot)
        if tr > 0:
            s = math.sqrt(tr + 1.0) * 2; q = np.array([(rot[2,1]-rot[1,2])/s, (rot[0,2]-rot[2,0])/s, (rot[1,0]-rot[0,1])/s, 0.25*s])
        elif rot[0,0] > rot[1,1] and rot[0,0] > rot[2,2]:
            s = math.sqrt(1.0 + rot[0,0] - rot[1,1] - rot[2,2]) * 2; q = np.array([0.25*s, (rot[0,1]+rot[1,0])/s, (rot[0,2]+rot[2,0])/s, (rot[2,1]-rot[1,2])/s])
        elif rot[1,1] > rot[2,2]:
            s = math.sqrt(1.0 + rot[1,1] - rot[0,0] - rot[2,2]) * 2; q = np.array([(rot[0,1]+rot[1,0])/s, 0.25*s, (rot[1,2]+rot[2,1])/s, (rot[0,2]-rot[2,0])/s])
        else:
            s = math.sqrt(1.0 + rot[2,2] - rot[0,0] - rot[1,1]) * 2; q = np.array([(rot[0,2]+rot[2,0])/s, (rot[1,2]+rot[2,1])/s, 0.25*s, (rot[1,0]-rot[0,1])/s])
        q = q / np.linalg.norm(q)
        n.pop("matrix", None)
        n["translation"] = new[:3, 3].tolist()
        n["rotation"] = q.tolist()
        n["scale"] = sc.tolist()

    # 2) bone rest offsets + pose (pose entries are rest edits = baked stance)
    for section in ("bones", "pose"):
        for name, spec in (rig.get(section, {}) or {}).items():
            ni = node_of(name)
            if ni is None: continue
            off = spec.get("offset", spec) if section == "bones" else spec
            apply_offset(ni, {k: off[k] for k in ("pos", "rot_deg", "scale") if k in off})
            report["ops"].append(f"{section} offset {name}")

    # 3) remove bones (after offsets; re-map skin joints + weights fallback)
    removed = {}
    for name in rig.get("remove_bones", []):
        ni = node_of(name)
        if ni is None: continue
        removed[name] = ni
    if removed:
        parent = {}
        for i, n in enumerate(nodes):
            for c in n.get("children", []):
                parent[c] = i
        for skin in js.get("skins", []):
            joints = skin["joints"]
            remap = {}
            keep = []
            for old_i, jn in enumerate(joints):
                nm = nodes[jn].get("name")
                if nm in removed:
                    # fallback: nearest ancestor that is also a joint & kept
                    p = parent.get(jn); fb = None
                    while p is not None:
                        if p in joints and nodes[p].get("name") not in removed:
                            fb = keep.index(p) if p in keep else None
                            if fb is None:
                                fb = joints.index(p)
                            break
                        p = parent.get(p)
                    remap[old_i] = fb
                else:
                    remap[old_i] = len(keep); keep.append(jn)
            skin["joints"] = [joints[k] for k in keep] if False else keep
            skin["_remap"] = remap
        # fix JOINTS_0 / merge weights of removed into fallback
        for mesh in js.get("meshes", []):
            for prim in mesh["primitives"]:
                at = prim.get("attributes", {})
                if "JOINTS_0" not in at: continue
                for skin in js.get("skins", []):
                    if "_remap" not in skin: continue
                    remap = skin["_remap"]
                    jj = read_acc(js, buf, at["JOINTS_0"]).astype(int)
                    ww = read_acc(js, buf, at["WEIGHTS_0"]).copy()
                    nj = np.zeros_like(jj); nw = np.zeros_like(ww)
                    for c in range(jj.shape[1]):
                        for v in range(jj.shape[0]):
                            tgt = remap.get(int(jj[v, c]))
                            if tgt is None:
                                continue
                            # accumulate into the slot already holding tgt, else this slot
                            slot = c
                            for s2 in range(nw.shape[1]):
                                if nw[v, s2] > 0 and nj[v, s2] == tgt:
                                    slot = s2; break
                            else:
                                nj[v, c] = tgt; slot = c
                            nj[v, slot] = tgt; nw[v, slot] += ww[v, c]
                    sums = nw.sum(axis=1, keepdims=True); sums[sums == 0] = 1
                    nw = nw / sums
                    write_acc_inplace(js, buf, at["JOINTS_0"], nj, "u")
                    write_acc_inplace(js, buf, at["WEIGHTS_0"], nw, "f")
        for skin in js.get("skins", []):
            skin.pop("_remap", None)
        for name, ni in removed.items():
            for n in nodes:
                if "children" in n and ni in n["children"]:
                    n["children"].remove(ni)
            report["ops"].append(f"remove_bone {name}")

    # 4) weight brush strokes (world-space sphere falloff on bind positions)
    strokes = rig.get("weights", []) or []
    if strokes:
        world = world_mats(js)
        for mesh in js.get("meshes", []):
            for prim in mesh["primitives"]:
                at = prim.get("attributes", {})
                if "JOINTS_0" not in at or "POSITION" not in at: continue
                pos = read_acc(js, buf, at["POSITION"])
                jj = read_acc(js, buf, at["JOINTS_0"]).astype(int)
                ww = read_acc(js, buf, at["WEIGHTS_0"]).copy()
                skin = js["skins"][0]
                joint_node = skin["joints"]
                for st in strokes:
                    bi = node_of(st["bone"])
                    if bi is None or bi not in joint_node: continue
                    bslot_joint = joint_node.index(bi)
                    ctr = np.array(st["center"]); rad = float(st["radius"])
                    d = np.linalg.norm(pos - ctr, axis=1)
                    fall = np.clip(1.0 - d / rad, 0, 1) ** 2 * float(st["strength"])
                    for v in range(pos.shape[0]):
                        if fall[v] <= 0: continue
                        cur = {int(jj[v, c]): ww[v, c] for c in range(jj.shape[1]) if ww[v, c] > 0}
                        if st.get("mode") == "set":
                            cur = {bslot_joint: 1.0} if fall[v] >= 0.999 else cur
                            if fall[v] < 0.999:
                                tgt = fall[v]
                                cur = {k: val * (1 - tgt) for k, val in cur.items()}
                                cur[bslot_joint] = cur.get(bslot_joint, 0) + tgt
                        else:
                            tgt = fall[v] * (1.0 - cur.get(bslot_joint, 0.0))
                            cur = {k: val * (1 - tgt) for k, val in cur.items()}
                            cur[bslot_joint] = cur.get(bslot_joint, 0) + tgt
                        top = sorted(cur.items(), key=lambda kv: -kv[1])[:4]
                        tot = sum(val for _, val in top) or 1.0
                        for c in range(4):
                            if c < len(top):
                                jj[v, c], ww[v, c] = top[c][0], top[c][1] / tot
                            else:
                                jj[v, c], ww[v, c] = 0, 0.0
                    report["ops"].append(f"weight stroke {st['bone']} verts={int((fall>0).sum())}")
                write_acc_inplace(js, buf, at["JOINTS_0"], jj, "u")
                write_acc_inplace(js, buf, at["WEIGHTS_0"], ww, "f")

    # 5) visibility: drop hidden meshes/nodes from scenes
    vis = rig.get("visibility", {}) or {}
    if vis:
        hidden_nodes = set()
        for i, n in enumerate(nodes):
            if n.get("name") in vis and not vis[n["name"]]:
                hidden_nodes.add(i)
        for mi, mesh in enumerate(js.get("meshes", [])):
            if mesh.get("name") in vis and not vis[mesh["name"]]:
                for n in nodes:
                    if n.get("mesh") == mi:
                        hidden_nodes.add(nodes.index(n))
        for sc in js.get("scenes", []):
            sc["nodes"] = [x for x in sc.get("nodes", []) if x not in hidden_nodes]
        for n in nodes:
            if "children" in n:
                n["children"] = [c for c in n["children"] if c not in hidden_nodes]
        report["ops"].append(f"visibility hidden={sorted(hidden_nodes)}")

    # 6) recompute IBMs from edited world rests
    world = world_mats(js)
    for skin in js.get("skins", []):
        ibms = []
        for jn in skin["joints"]:
            ibms.append(np.linalg.inv(world[jn]).T.reshape(-1))
        ibm_arr = np.array(ibms, dtype=np.float64).reshape(len(skin["joints"]), 16)
        new_idx = append_acc(js, buf, ibm_arr, "MAT4", "f")
        skin["inverseBindMatrices"] = new_idx
    report["ops"].append("ibm recomputed for all skins")

    if js.get("buffers"):
        js["buffers"][0]["byteLength"] = len(buf)
    save_glb(out_path, js, buf)
    return report

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--custom", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report")
    a = ap.parse_args()
    custom = json.load(open(a.custom))
    rep = bake(a.base, custom, a.out)
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps(rep, indent=1))
