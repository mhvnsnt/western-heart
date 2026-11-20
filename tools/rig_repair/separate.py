#!/usr/bin/env python3
"""separate.py - standalone limb/body weight separation (numpy + scipy only).

The topology-based arm/body separation from rig_repair.transfer
(--limb-separate), as a STANDALONE stage that runs on any already-weighted
model. This fixes the "hands glued to hips/legs" defect class (verts >25 cm
from their dominant bone, e.g. 812 hand verts weighted 0.89 to the leg on
STICK-UP v1) WITHOUT needing a transfer source model.

It must run AFTER the skeleton refit (it decides arm-vs-body from the CURRENT
bone positions) and BEFORE/INSTEAD-OF a full re-skin (a re-skin would replace
the corrected assignments).

usage:
  separate.py --in MODEL.glb --out MODEL_sep.glb --report separate.json [--force]

Inputs are never modified; --out must be a new path. The output keeps the
input's skeleton, IBMs, meshes, materials and textures; only WEIGHTS_0 changes
(smoothed + normalized + max 4 influences afterwards, same as transfer).
"""
import sys, os, json, struct
import numpy as np
from scipy.sparse import diags

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest import GLBDoc  # noqa: E402
from rig_repair import weld, topo, limb_separate  # noqa: E402
from scipy.sparse.csgraph import connected_components  # noqa: E402


def main():
    argv = sys.argv[1:]
    def opt(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
    IN, OUT, REP = opt("--in"), opt("--out"), opt("--report")
    assert IN and OUT and REP, "--in/--out/--report required"
    assert not os.path.exists(OUT) or "--force" in argv, f"refusing to overwrite {OUT}"

    doc = GLBDoc(IN)
    j = doc.json
    nj = len(j["skins"][0]["joints"])
    names = [j["nodes"][k].get("name", f"joint_{k}") for k in j["skins"][0]["joints"]]
    ibm = doc.accessor(j["skins"][0]["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)

    prim_reports = []
    new_weights = {}  # (mi, pi) -> (J4, W4)
    total_moved, skipped = 0, None
    for mi, m in enumerate(j["meshes"]):
        for pi, pr in enumerate(m["primitives"]):
            at = pr["attributes"]
            if "WEIGHTS_0" not in at or "JOINTS_0" not in at:
                continue
            P = doc.accessor(at["POSITION"]).astype(np.float64)
            F = doc.accessor(pr["indices"]).reshape(-1, 3).astype(np.int64)
            W = doc.accessor(at["WEIGHTS_0"]).astype(np.float64)
            J = doc.accessor(at["JOINTS_0"]).astype(np.int64)
            wid = weld(P); nW = wid.max() + 1
            Pw = np.zeros((nW, 3)); Pw[wid] = P
            Dw = np.zeros((nW, nj), np.float32)
            np.add.at(Dw, (wid[:, None], J), W)
            Dw /= np.maximum(Dw.sum(1, keepdims=True), 1e-9)
            u, cnt, A = topo(F, wid, nW)
            Dw, moved, skip = limb_separate(names, ibm, Pw, Dw, A)
            if skip and skipped is None:
                skipped = skip
            total_moved += moved
            # smooth + limit 4 + normalize (same as transfer)
            deg = np.asarray(A.sum(1)).ravel()
            Lr = diags(1 / np.maximum(deg, 1)) @ A
            for _ in range(3):
                Dw = 0.5 * Dw + 0.5 * (Lr @ Dw)
            Dv = Dw[wid]
            top = np.argsort(-Dv, 1)[:, :4]
            tw = np.take_along_axis(Dv, top, 1)
            tw[tw < 1e-3] = 0
            tw /= np.maximum(tw.sum(1, keepdims=True), 1e-9)
            new_weights[(mi, pi)] = (top.astype(np.uint8 if nj < 256 else np.uint16),
                                     tw.astype(np.float32))
            prim_reports.append({"mesh": m.get("name", f"mesh_{mi}"), "prim_index": pi,
                                 "verts": int(len(P)), "moved": int(moved)})

    # rebuild GLB: same JSON, only WEIGHTS_0/JOINTS_0 accessors replaced
    out = json.loads(json.dumps(j))
    blob = bytearray(); out["bufferViews"] = []; out["accessors"] = []
    def addbv(data, target=None):
        while len(blob) % 4: blob.append(0)
        bv = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
        if target: bv["target"] = target
        blob.extend(bytes(data)); out["bufferViews"].append(bv)
        return len(out["bufferViews"]) - 1
    def addacc(arr, ct, typ, target=None):
        arr = np.ascontiguousarray(arr)
        a_ = {"bufferView": addbv(arr.tobytes(), target), "componentType": ct,
              "count": int(arr.shape[0]), "type": typ}
        out["accessors"].append(a_); return len(out["accessors"]) - 1
    def copyacc(i):
        from ingest import CT as _CT, NC as _NC
        import numpy as _np
        a_ = dict(j["accessors"][i])
        data = doc.buffer_view_bytes(a_["bufferView"])
        off = a_.get("byteOffset", 0)
        itemsize = _np.dtype(_CT[a_["componentType"]]).itemsize * _NC[a_["type"]]
        # sparse accessors: fall back to decoded full array
        if a_.get("sparse"):
            arr = doc.accessor(i)
            data, off, itemsize = arr.tobytes(), 0, arr.nbytes
        else:
            data = data[off:off + a_["count"] * itemsize]
        a_["byteOffset"] = 0
        a_["bufferView"] = addbv(data)
        out["accessors"].append(a_)
        return len(out["accessors"]) - 1
    # copy every accessor once, remap all references (primitives, skins, anims)
    amap = {i: copyacc(i) for i in range(len(j["accessors"]))}
    for mi, m in enumerate(j["meshes"]):
        for pi, pr in enumerate(m["primitives"]):
            for attr, ai in list(pr["attributes"].items()):
                out["meshes"][mi]["primitives"][pi]["attributes"][attr] = amap[ai]
            if "indices" in pr:
                out["meshes"][mi]["primitives"][pi]["indices"] = amap[pr["indices"]]
    for si, sk in enumerate(j.get("skins", [])):
        if "inverseBindMatrices" in sk:
            out["skins"][si]["inverseBindMatrices"] = amap[sk["inverseBindMatrices"]]
    for ai, an in enumerate(j.get("animations", [])):
        for si, sm in enumerate(an["samplers"]):
            out["animations"][ai]["samplers"][si]["input"] = amap[sm["input"]]
            out["animations"][ai]["samplers"][si]["output"] = amap[sm["output"]]
    for (mi, pi), (J4, W4) in new_weights.items():
        jn = addacc(J4, 5121 if J4.dtype == np.uint8 else 5123, "VEC4", 34962)
        wn = addacc(W4, 5126, "VEC4", 34962)
        out["meshes"][mi]["primitives"][pi]["attributes"]["JOINTS_0"] = jn
        out["meshes"][mi]["primitives"][pi]["attributes"]["WEIGHTS_0"] = wn
    out["asset"] = {"version": "2.0", "generator": "rig-repair pipeline separate v1"}
    while len(blob) % 4: blob.append(0)
    out["buffers"] = [{"byteLength": len(blob)}]
    jb = json.dumps(out, separators=(",", ":")).encode(); jb += b" " * (-len(jb) % 4)
    with open(OUT, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 28 + len(jb) + len(blob)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A)); f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)
    rep = {"in": IN, "out": OUT, "verts_reassigned": int(total_moved),
           "skipped": skipped, "primitives": prim_reports}
    json.dump(rep, open(REP, "w"), indent=1)
    print(json.dumps({"verts_reassigned": int(total_moved), "skipped": skipped}))


if __name__ == "__main__":
    main()
