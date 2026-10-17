#!/usr/bin/env python3
"""armpit.py - armpit weight de-bleed + sharpen (numpy + scipy only).

DECISION (documents the research track's bake-vs-export-time question):
Blender's Corrective Smooth is a *deformation-time* mesh smoother. Baking it
into the rest-pose vertex positions is a no-op (there is no distortion at
rest), and export-time modifier state does not transfer to game engines.
The engine-compatible fix for armpit stretch is therefore weight-side, not
mesh-side:

  1. DE-BLEED: verts far from the arm bone segment (e.g. 18 cm away on the
     lat/back) must not carry arm weights. k-NN / heat skinning bleeds arm
     weights onto torso skin; when the arm rotates, those verts are torn
     between arm and torso (measured 24-29x edge stretch on STICK-UP).
     Arm weights decay smoothly to zero beyond --bleed-dist (default 0.14 m)
     of the shoulder->elbow->wrist segments, redistributed to torso bones.
  2. SHARPEN: inside the armpit transition zone the arm/torso blend is made
     narrower (contrast p=--sharpen, default 1.6): the deltoid cap follows the
     arm, the trap/lat stays with the torso, with a tight band between.
  3. Topology smooth (2 iters) + normalize + max 4 influences.

This is the same class of fix as the transfer's --limb-separate (topology +
skeleton geometry, fully automatic), not hand-painted weights.

usage:
  armpit.py --in MODEL.glb --out MODEL_armpit.glb --report armpit.json [--force]
"""
import sys, os, json, struct
import numpy as np
from scipy.sparse import diags

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest import GLBDoc, CT, NC  # noqa: E402
from rig_repair import weld, topo, match_joints  # noqa: E402


def seg_dist(P, A, B):
    ab = B - A
    t = np.clip(((P - A) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(P - (A + t[:, None] * ab), axis=1)


def main():
    argv = sys.argv[1:]
    def opt(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
    IN, OUT, REP = opt("--in"), opt("--out"), opt("--report")
    BLEED = float(opt("--bleed-dist", "0.14"))
    SHARPEN = float(opt("--sharpen", "1.6"))
    assert IN and OUT and REP, "--in/--out/--report required"
    assert not os.path.exists(OUT) or "--force" in argv, f"refusing to overwrite {OUT}"

    doc = GLBDoc(IN)
    j = doc.json
    nj = len(j["skins"][0]["joints"])
    names = [j["nodes"][k].get("name", f"joint_{k}") for k in j["skins"][0]["joints"]]
    ibm = doc.accessor(j["skins"][0]["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    bp = np.linalg.inv(ibm)[:, :3, 3]
    ix, chains, ok, note = match_joints(names)
    assert ok, f"armpit needs Mixamo-compatible joints: {note}"

    new_weights = {}
    reports = []
    for mi, m in enumerate(j["meshes"]):
        for pi, pr in enumerate(m["primitives"]):
            at = pr["attributes"]
            if "WEIGHTS_0" not in at:
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
            # light pre-smoothing (general noise); the corrections below run
            # after and are NOT smoothed over, so they stick.
            deg0 = np.asarray(A.sum(1)).ravel()
            Lr0 = diags(1 / np.maximum(deg0, 1)) @ A
            for _ in range(2):
                Dw = 0.5 * Dw + 0.5 * (Lr0 @ Dw)

            changed = 0
            # nearest bind-pose bone segment per vert (torso vs limb discriminator)
            all_segs = []
            for s in ("left", "right"):
                for a_, b_ in ((f"{s}_shoulder", f"{s}_arm"), (f"{s}_arm", f"{s}_forearm"),
                               (f"{s}_forearm", f"{s}_hand"), (f"{s}_upleg", f"{s}_leg"),
                               (f"{s}_leg", f"{s}_foot")):
                    if chains.get(a_) is not None and chains.get(b_) is not None:
                        all_segs.append((chains[a_], bp[chains[a_]], bp[chains[b_]],
                                         s if "arm" in a_ or "hand" in a_ else None))
            for a_, b_ in (("hips", "spine"), ("spine", "spine1"), ("spine1", "spine2"),
                           ("spine2", "neck")):
                if chains.get(a_) is not None and chains.get(b_) is not None:
                    all_segs.append((chains[a_], bp[chains[a_]], bp[chains[b_]], None))
            D = np.full((nW, len(all_segs)), np.inf)
            for k, (_, A_, B_, _) in enumerate(all_segs):
                D[:, k] = seg_dist(Pw, A_, B_)
            best = D.argmin(1)
            best_is_arm = np.array([all_segs[k][3] is not None for k in best])
            for side in ("left", "right"):
                acols = [chains[f"{side}_{p}"] for p in ("arm", "forearm", "hand")]
                acols = [c for c in acols if c is not None]
                if len(acols) < 2:
                    continue
                tcols = [chains[b] for b in ("spine", "spine1", "spine2", "hips")]
                tcols = [c for c in tcols if c is not None]
                segs = [(bp[chains[f"{side}_shoulder"]], bp[chains[f"{side}_arm"]])] \
                    if chains[f"{side}_shoulder"] is not None else []
                segs += [(bp[acols[i]], bp[acols[i + 1]]) for i in range(len(acols) - 1)]
                dmin = np.full(nW, np.inf)
                for A_, B_ in segs:
                    dmin = np.minimum(dmin, seg_dist(Pw, A_, B_))
                sy = bp[chains[f"{side}_arm"]][1]
                region = ((Pw[:, 1] > sy - 0.30) & (Pw[:, 1] < sy + 0.10) &
                          (np.abs(Pw[:, 2]) > 0.04) & (np.abs(Pw[:, 2]) < 0.32) &
                          (np.abs(Pw[:, 0]) < 0.28))
                # 0. torso-side verts must not carry arm weights, however close
                #    the hanging forearm passes (proximity != limb).
                armw = Dw[:, acols].sum(1)
                torso_side = region & ~best_is_arm & (armw > 0.03)
                if torso_side.any():
                    # NOTE: Dw[mask][:, cols] = x is a chained no-op (boolean
                    # getitem returns a copy). np.ix_ is required for setitem.
                    IXa = np.ix_(torso_side, acols)
                    IXt = np.ix_(torso_side, tcols)
                    removed = Dw[IXa].sum(1, keepdims=True)
                    Dw[IXa] = 0
                    tw = np.maximum(Dw[IXt].sum(1, keepdims=True), 1e-9)
                    Dw[IXt] += removed * (Dw[IXt] / tw)
                    changed += int(torso_side.sum())
                # 1. de-bleed: arm weights -> 0 beyond BLEED dist
                armw = Dw[:, acols].sum(1)
                bleed = region & (armw > 0.01) & (dmin > BLEED)
                if bleed.any():
                    f = np.clip(1 - (dmin[bleed] - BLEED) / 0.10, 0, 1)
                    IXa = np.ix_(bleed, acols)
                    IXt = np.ix_(bleed, tcols)
                    removed = Dw[IXa].sum(1, keepdims=True)
                    Dw[IXa] *= f[:, None]
                    kept = Dw[IXa].sum(1, keepdims=True)
                    # redistribute to torso bones proportionally
                    tw = np.maximum(Dw[IXt].sum(1, keepdims=True), 1e-9)
                    Dw[IXt] += (removed - kept) * (Dw[IXt] / tw)
                    changed += int(bleed.sum())
                # 2. sharpen arm-vs-torso blend inside the region
                sharp = region & (armw > 0.05) & (dmin <= BLEED)
                if sharp.any():
                    sub = np.concatenate([acols, tcols])
                    IXs = np.ix_(sharp, sub)
                    w = Dw[IXs]
                    w = np.power(np.maximum(w, 1e-9), SHARPEN)
                    w /= w.sum(1, keepdims=True)
                    Dw[IXs] = w.astype(np.float32)
            # NOTE: smoothing runs BEFORE the corrections (in the side loop
            # above). Post-correction smoothing was re-bleeding arm weights
            # onto zeroed torso verts via neighbor diffusion.
            Dv = Dw[wid]
            top = np.argsort(-Dv, 1)[:, :4]
            tw = np.take_along_axis(Dv, top, 1)
            tw[tw < 1e-3] = 0
            tw /= np.maximum(tw.sum(1, keepdims=True), 1e-9)
            new_weights[(mi, pi)] = (top.astype(np.uint8 if nj < 256 else np.uint16),
                                     tw.astype(np.float32))
            reports.append({"mesh": m.get("name", f"mesh_{mi}"), "prim_index": pi,
                            "de_bleed_verts": int(changed)})

    # rebuild (same remap pattern as separate.py)
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
        import numpy as _np
        a_ = dict(j["accessors"][i])
        data = doc.buffer_view_bytes(a_["bufferView"])
        off = a_.get("byteOffset", 0)
        itemsize = _np.dtype(CT[a_["componentType"]]).itemsize * NC[a_["type"]]
        if a_.get("sparse"):
            arr = doc.accessor(i); data, off = arr.tobytes(), 0
        else:
            data = data[off:off + a_["count"] * itemsize]
        a_["byteOffset"] = 0
        a_["bufferView"] = addbv(data); out["accessors"].append(a_)
        return len(out["accessors"]) - 1
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
    out["asset"] = {"version": "2.0", "generator": "rig-repair pipeline armpit v1"}
    while len(blob) % 4: blob.append(0)
    out["buffers"] = [{"byteLength": len(blob)}]
    jb = json.dumps(out, separators=(",", ":")).encode(); jb += b" " * (-len(jb) % 4)
    with open(OUT, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 28 + len(jb) + len(blob)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A)); f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)
    rep = {"in": IN, "out": OUT, "bleed_dist": BLEED, "sharpen": SHARPEN,
           "primitives": reports}
    json.dump(rep, open(REP, "w"), indent=1)
    print(json.dumps({"de_bleed_verts": sum(r["de_bleed_verts"] for r in reports)}))


if __name__ == "__main__":
    main()
