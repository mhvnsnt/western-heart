#!/usr/bin/env python3
"""Rig repair case 1: a skin whose vertex JOINTS_0 indices point at the mirrored-side bone.

Detects the defect by symmetry: for every vertex with |x| > XTOL whose dominant joint is a
Left*/Right* bone, the vertex x-sign must match that bone's rest x-sign. If (almost) every such
vertex is on the wrong side, the joint indices are remapped Left<->Right by mirrored bone name.
Positions, weights, IBMs, nodes and animations are untouched. Writes a NEW file.

usage: swap_lr_joints.py in.glb out.glb
"""
import json, struct, sys
import numpy as np

XTOL = 0.15


def load(p):
    b = open(p, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    o = 20 + n
    bl = struct.unpack("<I", b[o:o + 4])[0]
    return j, bytearray(b[o + 8:o + 8 + bl])


def save(p, j, binb):
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    binb = bytes(binb) + b"\0" * (-len(binb) % 4)
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binb))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(binb), 0x004E4942) + binb
    open(p, "wb").write(out)


def view(j, binb, i):
    A = j["accessors"][i]
    bv = j["bufferViews"][A["bufferView"]]
    assert "byteStride" not in bv or bv["byteStride"] in (0, None, {5121: 4, 5123: 8, 5126: 4 * {"VEC3": 3, "VEC4": 4, "MAT4": 16}[A["type"]]}[A["componentType"]])
    n = {"VEC4": 4, "VEC3": 3, "MAT4": 16}[A["type"]]
    dt = {5126: np.float32, 5121: np.uint8, 5123: np.uint16}[A["componentType"]]
    o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
    return o, dt, np.frombuffer(bytes(binb[o:o + np.dtype(dt).itemsize * n * A["count"]]), dt).reshape(A["count"], n).copy()


def bind_x(j, binb, sk):
    _, _, ibm = view(j, binb, sk["inverseBindMatrices"])
    return np.array([np.linalg.inv(m.reshape(4, 4).T)[0, 3] for m in ibm])


def check(j, binb):
    sk = j["skins"][0]
    names = [j["nodes"][i]["name"] for i in sk["joints"]]
    bx = bind_x(j, binb, sk)
    tot = bad = 0
    for m in j["meshes"]:
        for pr in m["primitives"]:
            a = pr["attributes"]
            if "JOINTS_0" not in a: continue
            P = view(j, binb, a["POSITION"])[2]; J = view(j, binb, a["JOINTS_0"])[2]; W = view(j, binb, a["WEIGHTS_0"])[2]
            dom = J[np.arange(len(J)), W.argmax(1)]
            for v, q in zip(P, dom):
                if abs(v[0]) > XTOL and names[q][:4] in ("Left", "Righ"):
                    tot += 1; bad += int(np.sign(v[0]) != np.sign(bx[q]))
    return tot, bad


def main():
    src, dst = sys.argv[1], sys.argv[2]
    j, binb = load(src)
    tot, bad = check(j, binb)
    print(f"before: side-weighted verts {tot}, on opposite-side bone {bad}")
    if bad < 0.99 * tot:
        sys.exit("not a whole-skin L/R swap; refusing to remap")
    sk = j["skins"][0]
    names = [j["nodes"][i]["name"] for i in sk["joints"]]
    def mirror(n): return "Right" + n[4:] if n.startswith("Left") else ("Left" + n[5:] if n.startswith("Right") else n)
    # a bone with no mirrored partner keeps its index; it must carry no weight (checked below)
    lut = np.array([names.index(mirror(n)) if mirror(n) in names else k for k, n in enumerate(names)])
    lonely = {k for k, n in enumerate(names) if mirror(n) not in names and mirror(n) != n}
    done = set()
    for m in j["meshes"]:
        for pr in m["primitives"]:
            a = pr["attributes"]
            if "JOINTS_0" not in a or a["JOINTS_0"] in done: continue
            done.add(a["JOINTS_0"])
            o, dt, J = view(j, binb, a["JOINTS_0"])
            Wt = view(j, binb, a["WEIGHTS_0"])[2]
            assert not any(((J == k) & (Wt > 0)).any() for k in lonely), "weighted bone without mirror"
            J2 = lut[J].astype(dt)
            binb[o:o + J2.nbytes] = J2.tobytes()
    j.setdefault("asset", {})["extras"] = {**j["asset"].get("extras", {}), "rig_repair": "swap_lr_joints.py: JOINTS_0 Left<->Right remap (case 1)"}
    tot2, bad2 = check(j, binb)
    print(f"after:  side-weighted verts {tot2}, on opposite-side bone {bad2}")
    assert bad2 == 0
    save(dst, j, binb)


if __name__ == "__main__":
    main()
