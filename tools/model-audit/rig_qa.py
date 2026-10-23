#!/usr/bin/env python3
"""tools/model-audit/rig_qa.py — structural rig QA for skinned fighter GLBs (2026-10-22, Claude session).

Owner 2026-10-22: "all the mismatches all the left arm being labeled as the right arm and the legs being
twisted ... the hand looks weighted to the tail". This measures those defects from the file itself, per model:

  * facing: the mesh's forward axis from the feet (toe vertices lead the ankle joints) — +Z or -Z;
  * sides per chain: with that facing, the character's left is +X (+Z facing) or -X (-Z facing); every
    Left*/Right* arm and leg joint is checked against it separately, so an arm swap and a leg swap are
    told apart (the runtime retarget swaps sides as a whole, from the arms only);
  * knee direction: the knee should sit forward of the hip-ankle line (a backwards knee = twisted leg);
  * weight bleed: vertices whose dominant bone is far from them while another bone is close, grouped
    by (dominant bone -> nearest bone), e.g. hand verts dominated by a tail bone.

Plain glTF only. Meshopt (Tripo/gltfpack) files: decode first with tools/anim/gltf_codec.mjs.

    python3 tools/model-audit/rig_qa.py MODEL.glb [MODEL2.glb ...] [--json out.json]
"""
import json
import re
import struct
import sys

import numpy as np

COMP = {5126: np.float32, 5123: np.uint16, 5121: np.uint8, 5125: np.uint32, 5122: np.int16, 5120: np.int8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    blob = b[20 + n + 8:]
    return js, blob


def accessor(js, blob, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    nc = NC[a["type"]]
    dt = np.dtype(COMP[a["componentType"]])
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or nc * dt.itemsize
    if stride == nc * dt.itemsize:
        out = np.frombuffer(blob, dt, a["count"] * nc, off).reshape(a["count"], nc)
    else:
        out = np.stack([np.frombuffer(blob, dt, nc, off + k * stride) for k in range(a["count"])])
    out = out.astype(np.float64)
    if a.get("normalized") and a["componentType"] in (5121, 5123):
        out /= 255.0 if a["componentType"] == 5121 else 65535.0
    return out


def canon(name):
    n = re.sub(r"^mixamorig[:_]?", "", name)
    n = re.sub(r"_\d+$", "", n)
    return n


def qa(path):
    js, blob = read_glb(path)
    if js.get("extensionsUsed") and "EXT_meshopt_compression" in js["extensionsUsed"]:
        return {"model": path, "error": "meshopt-compressed: decode with tools/anim/gltf_codec.mjs first"}
    skins = js.get("skins") or []
    if not skins:
        return {"model": path, "error": "no skin (static)"}
    sk = skins[0]
    joints = sk["joints"]
    ibm = accessor(js, blob, sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    # bind-pose joint positions = inverse of the inverse bind matrices (mesh space)
    jpos = np.array([np.linalg.inv(m)[:3, 3] for m in ibm])
    names = [js["nodes"][j].get("name", f"j{j}") for j in joints]
    cn = [canon(n) for n in names]
    idx = {c: i for i, c in enumerate(cn) if c not in ()}
    # vertices (first skinned primitive set)
    V, D = [], []
    for nd in js["nodes"]:
        if "mesh" not in nd or nd.get("skin") is None:
            continue
        for pr in js["meshes"][nd["mesh"]]["primitives"]:
            at = pr["attributes"]
            if "JOINTS_0" not in at:
                continue
            pos = accessor(js, blob, at["POSITION"])
            jt = accessor(js, blob, at["JOINTS_0"]).astype(int)
            wt = accessor(js, blob, at["WEIGHTS_0"])
            V.append(pos)
            D.append(jt[np.arange(len(jt)), wt.argmax(1)])
    if not V:
        return {"model": path, "error": "no skinned primitives"}
    V = np.vstack(V)
    D = np.concatenate(D)
    rep = {"model": path, "joints": len(joints), "verts": int(len(V))}
    # facing from feet: toe vertices (dominant foot/toe bones) lead the ankle joints
    feet = [i for i, c in enumerate(cn) if re.search(r"(Foot|Toe)", c)]
    ankles = [idx[c] for c in ("LeftFoot", "RightFoot") if c in idx]
    facing = None
    if feet and ankles:
        fv = V[np.isin(D, feet)]
        if len(fv):
            dz = fv[:, 2].mean() - jpos[ankles, 2].mean()
            facing = "+Z" if dz > 0 else "-Z"
            rep["feet_dz_m"] = round(float(dz), 4)
    rep["facing"] = facing
    left_sign = 1 if facing != "-Z" else -1     # character's left: +X when facing +Z
    sides = {}
    for chain, parts in (("arm", ("Shoulder", "Arm", "ForeArm", "Hand")), ("leg", ("UpLeg", "Leg", "Foot", "ToeBase"))):
        res = []
        for p in parts:
            l, r = idx.get("Left" + p), idx.get("Right" + p)
            if l is None or r is None:
                continue
            res.append("ok" if (jpos[l, 0] - jpos[r, 0]) * left_sign > 0 else "SWAPPED")
        sides[chain] = sorted(set(res)) if res else ["n/a"]
    rep["sides"] = sides
    knees = {}
    for s in ("Left", "Right"):
        if all(s + p in idx for p in ("UpLeg", "Leg", "Foot")):
            h, k, a = jpos[idx[s + "UpLeg"]], jpos[idx[s + "Leg"]], jpos[idx[s + "Foot"]]
            d = a - h
            t = np.dot(k - h, d) / max(np.dot(d, d), 1e-9)
            bend = k - (h + t * d)
            fwd = 1 if facing != "-Z" else -1
            knees[s] = "forward" if bend[2] * fwd > 0.002 else ("BACKWARD" if bend[2] * fwd < -0.002 else "straight")
    rep["knees"] = knees
    # weight bleed: dominant bone far, another bone near (segment distance to each joint's child)
    child = {}
    for i, j in enumerate(joints):
        for c in js["nodes"][j].get("children", []):
            if c in joints:
                child.setdefault(i, []).append(joints.index(c))
    segs = []
    for i in range(len(joints)):
        for c in child.get(i, [None]):
            segs.append((i, jpos[i], jpos[c] if c is not None else jpos[i]))
    sample = np.arange(len(V)) if len(V) <= 60000 else np.linspace(0, len(V) - 1, 60000).astype(int)
    P = V[sample]
    dist = np.full((len(P), len(joints)), np.inf)
    for i, a, b in segs:
        ab = b - a
        L2 = max(np.dot(ab, ab), 1e-12)
        t = np.clip(((P - a) @ ab) / L2, 0, 1)
        d = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
        dist[:, i] = np.minimum(dist[:, i], d)
    near = dist.argmin(1)
    dn = dist[np.arange(len(P)), near]
    dd = dist[np.arange(len(P)), D[sample]]
    height = float(V[:, 1].max() - V[:, 1].min()) or 1.0
    bleed = (dd > 3 * dn + 0.05 * height)
    pairs = {}
    for dom, nb in zip(D[sample][bleed], near[bleed]):
        k = f"{cn[dom]} -> near {cn[nb]}"
        pairs[k] = pairs.get(k, 0) + 1
    scale = len(V) / len(P)
    rep["weight_bleed_verts"] = int(bleed.sum() * scale)
    rep["weight_bleed_top"] = {k: int(v * scale) for k, v in sorted(pairs.items(), key=lambda x: -x[1])[:8]}
    return rep


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    if out in args:
        args.remove(out)
    reps = [qa(p) for p in args]
    for r in reps:
        print(json.dumps(r, indent=1))
    if out:
        json.dump(reps, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
