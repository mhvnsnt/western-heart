#!/usr/bin/env python3
"""rig_repair.py - universal weight-paint repair / transfer for skinned GLBs.

Ported from Bannon PR #77 (tools/rig_repair) into the universal rig-repair
pipeline, with the Track-1 (2026-10-14) fixes:

  * multi-mesh / multi-primitive: every primitive of every mesh is processed.
    PR #77 silently read only meshes[0].primitives[0] (data-integrity bug).
  * multi-buffer GLBs + EXT_meshopt_compression decoded via ingest.py
    (pure Python, `meshopt` pip package). PR #77 crashed with
    "ValueError: buffer is smaller than requested size".
  * KHR_draco_mesh_compression raises a clear DracoError (no pure-Python
    decoder exists); the pipeline routes those models through Blender ingest.
  * transfer is de-hardcoded: output mesh name comes from the TARGET
    (PR #77 hardcoded "STICKUP_HQ"); extensionsUsed/extensionsRequired are
    preserved (PR #77 dropped e.g. EXT_texture_webp); --limb-separate uses
    tolerant joint-name matching and SKIPS LOUDLY (report entry, no crash)
    when the skeleton is not Mixamo-compatible.

usage:
  rig_repair.py detect  MODEL.glb [--json out.json]
  rig_repair.py transfer --target HQ.glb --source RIGGED.glb --out OUT.glb [--report r.json]
                         [--k 6] [--smooth 3] [--island-frac 0.002]
                         [--limb-separate] [--cut-fused] [--force]

detect   : zero-weight verts, weight-sum error, >4 influences, NaN, open/boundary
           edges (holes), non-manifold edges, disconnected islands (on position-
           welded topology) and floating parts (small islands far from the body),
           seam tears (welded verts whose weights disagree). Aggregated over ALL
           primitives; per-primitive breakdown in the JSON report.
transfer : takes the geometry + textures of TARGET and the skeleton/IBMs of
           SOURCE (both in the same bind space), then:
             1. re-transfers weights from SOURCE body surface (k-NN inverse-distance),
             2. welds: every vertex sharing a position gets identical weights,
             3. small/floating islands are bound rigidly to the body at their attach point,
             4. --limb-separate: topology-based arm/body separation (see below),
             5. Laplacian smooth on welded topology, normalize, limit to 4 influences.
           The original files are never modified; OUT must be a new path.
Requires numpy + scipy only.
"""
import sys, json, struct, argparse, os, re
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, csr_matrix, diags
from scipy.sparse.csgraph import connected_components

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest import GLBDoc, DracoError  # noqa: E402

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}


def norm(n):
    n = re.sub(r"^mixamorig\d*[:_]?", "", n or "", flags=re.I)
    return n.replace(".", "").replace(" ", "").lower()


def weld(P, tol=1e-6):
    q = np.round(P / tol).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    return inv.ravel()


def topo(F, wid, nW):
    Fw = wid[F]
    e = np.concatenate([Fw[:, [0, 1]], Fw[:, [1, 2]], Fw[:, [2, 0]]])
    e = e[e[:, 0] != e[:, 1]]
    es = np.sort(e, 1)
    u, cnt = np.unique(es, axis=0, return_counts=True)
    A = coo_matrix((np.ones(len(u)), (u[:, 0], u[:, 1])), shape=(nW, nW)).tocsr()
    A = A + A.T
    return u, cnt, A


def detect_prim(P, F, W, J):
    """Detect defects on ONE primitive. Returns a dict of metrics."""
    r = {"verts": int(len(P)), "tris": int(len(F))}
    if W is not None:
        W = W.astype(np.float64)
        s = W.sum(1)
        r.update(zero_weight_verts=int((s < 1e-6).sum()),
                 weight_sum_maxdev=float(np.abs(s - 1).max()),
                 nan=int(np.isnan(W).sum()),
                 verts_over_4_influences=int(((W > 1e-4).sum(1) > 4).sum()))
    wid = weld(P)
    nW = wid.max() + 1
    u, cnt, A = topo(F, wid, nW)
    r["boundary_edges_holes"] = int((cnt == 1).sum())
    r["nonmanifold_edges"] = int((cnt > 2).sum())
    nc, lab = connected_components(A, directed=False)
    sizes = np.bincount(lab)
    main = sizes.argmax()
    r["islands"] = int(nc)
    r["main_island_frac"] = float(sizes[main] / nW)
    Pw = np.zeros((nW, 3))
    Pw[wid] = P
    H = P[:, 1].max() - P[:, 1].min()
    tree = cKDTree(Pw[lab == main])
    small = np.where(sizes < 0.002 * nW)[0]
    fl = 0
    for c in small:
        dist, _ = tree.query(Pw[lab == c], k=1)
        if dist.min() > 0.01 * H:
            fl += 1
    r["small_islands"] = int(len(small))
    r["floating_parts"] = int(fl)
    if W is not None and J is not None:
        J = J.astype(np.int64)
        nj = int(J.max()) + 1
        dense = np.zeros((len(P), nj), np.float32)
        np.add.at(dense, (np.arange(len(P))[:, None], J), W)
        m = np.zeros((nW, nj))
        np.add.at(m, wid, dense)
        m /= np.bincount(wid, minlength=nW)[:, None]
        r["seam_tear_verts"] = int((np.abs(dense - m[wid]).sum(1) > 0.05).sum())
    return r


def detect(path):
    doc = GLBDoc(path)
    prims = []
    agg = {"file": path, "primitives": 0, "verts": 0, "tris": 0,
           "zero_weight_verts": 0, "nan": 0, "boundary_edges_holes": 0,
           "nonmanifold_edges": 0, "islands": 0, "small_islands": 0,
           "floating_parts": 0, "seam_tear_verts": 0,
           "weight_sum_maxdev": 0.0, "verts_over_4_influences": 0}
    for name, pi, attrs, idx in doc.primitives():
        P, F = attrs["POSITION"].astype(np.float64), idx.reshape(-1, 3)
        W = attrs.get("WEIGHTS_0")
        J = attrs.get("JOINTS_0")
        r = detect_prim(P, F, W, J)
        r["mesh"] = name
        r["prim_index"] = pi
        prims.append(r)
        agg["primitives"] += 1
        for k in ("verts", "tris", "zero_weight_verts", "nan",
                  "boundary_edges_holes", "nonmanifold_edges", "islands",
                  "small_islands", "floating_parts", "seam_tear_verts",
                  "verts_over_4_influences"):
            agg[k] += r.get(k, 0)
        agg["weight_sum_maxdev"] = max(agg["weight_sum_maxdev"], r.get("weight_sum_maxdev", 0.0))
    agg["per_primitive"] = prims
    if agg["primitives"] > 1:
        agg["note"] = (f"multi-primitive model: metrics aggregated over "
                       f"{agg['primitives']} primitives (PR #77 read only the first)")
    return agg


# --------------------------------------------------------------------------
# tolerant joint-name matching (de-hardcodes the Mixamo-only limb_separate)

_CANDS = {
    # (left_names, right_names)
    "arm": (["leftarm", "upperarm_l", "l_upperarm", "arm_l", "leftupperarm", "upper_arm_l"],
            ["rightarm", "upperarm_r", "r_upperarm", "arm_r", "rightupperarm", "upper_arm_r"]),
    "forearm": (["leftforearm", "forearm_l", "l_forearm", "leftlowerarm", "lower_arm_l"],
                ["rightforearm", "forearm_r", "r_forearm", "rightlowerarm", "lower_arm_r"]),
    "hand": (["lefthand", "hand_l", "l_hand", "leftwrist", "wrist_l"],
             ["righthand", "hand_r", "r_hand", "rightwrist", "wrist_r"]),
    "shoulder": (["leftshoulder", "shoulder_l", "l_shoulder", "clavicle_l"],
                 ["rightshoulder", "shoulder_r", "r_shoulder", "clavicle_r"]),
    "upleg": (["leftupleg", "thigh_l", "l_thigh", "upperleg_l", "leftthigh"],
              ["rightupleg", "thigh_r", "r_thigh", "upperleg_r", "rightthigh"]),
    "leg": (["leftleg", "shin_l", "l_shin", "calf_l", "lowerleg_l", "leftshin"],
            ["rightleg", "shin_r", "r_shin", "calf_r", "lowerleg_r", "rightshin"]),
    "foot": (["leftfoot", "foot_l", "l_foot"],
             ["rightfoot", "foot_r", "r_foot"]),
    "toebase": (["lefttoebase", "toebase_l", "l_toebase", "toes_l"],
                ["righttoebase", "toebase_r", "r_toebase", "toes_r"]),
}
_TRUNK = {"hips": ["hips", "pelvis", "root"],
          "spine": ["spine", "spine_01", "waist"],
          "spine1": ["spine1", "spine_02", "chest"],
          "spine2": ["spine2", "spine_03", "upperchest"],
          "neck": ["neck"], "head": ["head"]}
_FINGERS = ("index", "middle", "ring", "pinky", "thumb")


def match_joints(names):
    """names: list of raw joint node names. Returns (ix, chains, ok, note).
    ix: normalized-name -> joint index. chains: dict with left/right arm+leg
    chains and trunk bones, or None entries when not found."""
    ix = {}
    for i, n in enumerate(names):
        ix.setdefault(norm(n), i)
    chains = {}
    ok = True
    missing = []
    for part, (lc, rc) in _CANDS.items():
        for side, cands in (("left", lc), ("right", rc)):
            hit = next((ix[c] for c in cands if c in ix), None)
            chains[f"{side}_{part}"] = hit
            if hit is None and part in ("arm", "forearm", "hand"):
                ok = False
                missing.append(f"{side}_{part}")
    for bone, cands in _TRUNK.items():
        hit = next((ix[c] for c in cands if c in ix), None)
        chains[bone] = hit
        if hit is None and bone in ("hips", "spine"):
            ok = False
            missing.append(bone)
    # finger chains: normalized names containing a finger word + side marker
    fingers = []
    for i, n in enumerate(names):
        nn = norm(n)
        side = "left" if nn.startswith("left") or nn.endswith("_l") or nn.endswith(".l") else \
               "right" if nn.startswith("right") or nn.endswith("_r") or nn.endswith(".r") else None
        if side and any(f in nn for f in _FINGERS):
            fingers.append((i, side, nn))
    chains["fingers"] = fingers
    note = ("all key chains found" if ok
            else f"MISSING joint chains for limb-separate: {', '.join(missing)}")
    return ix, chains, ok, note


BAND = None


def limb_separate(names, ibm, Pw, Dw, Adj=None):
    """Topology-based arm/body weight separation. Joint names are matched
    tolerantly (see match_joints). Returns (Dw, moved, skipped_reason).
    skipped_reason is None on success, else a LOUD string for the report."""
    ix, chains, ok, note = match_joints(names)
    if not ok:
        return Dw, 0, f"limb-separate SKIPPED (not Mixamo-compatible): {note}"
    bp = np.linalg.inv(ibm)[:, :3, 3]

    def seg(a_key, b_key, arm_side):
        a, b = chains.get(a_key), chains.get(b_key)
        if a is None or b is None:
            return None
        return (a, bp[a], bp[b], arm_side)

    segs = []
    for side in ("left", "right"):
        for a_, b_, arm in ((f"{side}_arm", f"{side}_forearm", side),
                            (f"{side}_forearm", f"{side}_hand", side),
                            (f"{side}_hand", None, side),   # hand->fingers handled below
                            (f"{side}_shoulder", f"{side}_arm", None),
                            (f"{side}_upleg", f"{side}_leg", None),
                            (f"{side}_leg", f"{side}_foot", None),
                            (f"{side}_foot", f"{side}_toebase", None)):
            if b_ is None:
                # hand segment: hand joint -> first finger joint of that side
                fh = [(i, bp[i]) for i, s, _ in chains["fingers"] if s == side]
                if chains[f"{side}_hand"] is not None and fh:
                    i0 = min(fh, key=lambda t: np.linalg.norm(t[1] - bp[chains[f"{side}_hand"]]))[0]
                    segs.append((chains[f"{side}_hand"], bp[chains[f"{side}_hand"]], bp[i0], side))
            else:
                s = seg(a_, b_, arm)
                if s:
                    segs.append(s)
    for a_, b_ in (("hips", "spine"), ("spine", "spine1"), ("spine1", "spine2"),
                   ("spine2", "neck"), ("neck", "head")):
        s = seg(a_, b_, None)
        if s:
            segs.append(s)

    D = np.full((len(Pw), len(segs)), np.inf)
    for k, (_, A, C, _) in enumerate(segs):
        ab = C - A
        t = np.clip(((Pw - A) @ ab) / max(ab @ ab, 1e-12), 0, 1)
        D[:, k] = np.linalg.norm(Pw - (A + t[:, None] * ab), axis=1)
    best = D.argmin(1)

    def arm_cols(side):
        cols = [chains[f"{side}_{part}"] for part in ("arm", "forearm", "hand")]
        cols += [i for i, s, _ in chains["fingers"] if s == side]
        return [c for c in cols if c is not None]

    armset = {s: arm_cols(s) for s in ("left", "right")}
    aw = {s: Dw[:, armset[s]].sum(1) for s in armset}
    tot = aw["left"] + aw["right"]
    moved = 0
    locked = np.zeros(len(Pw), bool)
    if Adj is not None:
        ylim = min(bp[chains["left_arm"]][1], bp[chains["right_arm"]][1])
        while True:   # highest cut height where both arms separate from the body column
            ylim -= 0.02
            sub = np.where(Pw[:, 1] < ylim)[0]
            As = Adj[sub][:, sub]
            ncs, ls = connected_components(As, directed=False)
            sz = np.bincount(ls)
            if (sz > 0.01 * len(sub)).sum() >= 3 or ylim < bp[chains["hips"]][1]:
                break
        print("limb_separate: arm cut height", round(float(ylim), 3), file=sys.stderr)
        body = set(np.argsort(-sz)[:1])  # largest = legs+hips column
        if not body:
            # Small/above-hips primitive: no verts below the cut. Skip loudly
            # instead of crashing with StopIteration. Merge-audit fix 2026-10-15.
            print("limb_separate: no below-cut verts (small/above-hips primitive); "
                  "skipping arm-cut loudly", file=sys.stderr)
            return Dw, int(moved), "no_below_cut_verts"
        armsegs = [(k, sg) for k, sg in enumerate(segs) if sg[3]]
        allseg = [(b_, a_, c_) for _, (b_, a_, c_, _) in armsegs]
        for c in range(ncs):
            if c in body or sz[c] < 20:
                continue
            vv = sub[ls == c]
            Q = Pw[vv]
            Dd = np.stack([np.linalg.norm(
                Q - (a_ + np.clip(((Q - a_) @ (c_ - a_)) / max((c_ - a_) @ (c_ - a_), 1e-12),
                                   0, 1)[:, None] * (c_ - a_)), axis=1)
                for _, a_, c_ in allseg], 1)
            bi = np.array([b_ for b_, _, _ in allseg])[Dd.argmin(1)]
            armw = sum(Dw[vv][:, armset[s]].sum(1) for s in armset)
            bad = armw < 0.95
            Dw[vv[bad]] = 0
            Dw[vv[bad], bi[bad]] = 1
            moved += bad.sum()
            locked[vv] = True
        bodyv = sub[ls == next(iter(body))]
        sl = bodyv[Pw[bodyv, 1] > ylim - 0.03]
        zt = np.abs(Pw[sl, 2] - Pw[sl, 2].mean()).max() if len(sl) else 0.15
        global BAND
        BAND = (float(ylim), float(min(bp[chains["left_arm"]][1], bp[chains["right_arm"]][1])), float(zt))
        band = np.where((Pw[:, 1] >= ylim) & (Pw[:, 1] < BAND[1]) & (np.abs(Pw[:, 2]) > zt))[0]
        for s, sgn in (("left", 1), ("right", -1)):
            vv = band[np.sign(Pw[band, 2]) == np.sign(bp[chains[f"{s}_arm"]][2])]
            armw = Dw[vv][:, armset[s]].sum(1)
            bad = armw < 0.95
            Dw[vv[bad]] = 0
            Dw[vv[bad], chains[f"{s}_arm"]] = 1
            moved += bad.sum()
            locked[vv] = True
        print("limb_separate: band", BAND, file=sys.stderr)
    for k, (bone, _, _, arm) in enumerate(segs):
        sel = best == k
        bad = sel & ~locked & ((aw[arm] < 0.5) if arm else (tot > 0.5))
        Dw[bad] = 0
        Dw[bad, bone] = 1
        moved += bad.sum()
    return Dw, int(moved), None


def cut_fused(names, ibm, T, wid, Dw_w, keep_r=0.45):
    """Cut A-pose fusion between arms and torso (experimental, off by default).
    Kept from PR #77; joint lookup is now tolerant."""
    ix, chains, ok, note = match_joints(names)
    if not ok:
        raise ValueError(f"cut_fused needs Mixamo-compatible joints: {note}")
    bp = np.linalg.inv(ibm)[:, :3, 3]
    P = T["POSITION"].astype(np.float64)
    N = T["NORMAL"].astype(np.float64) if "NORMAL" in T else None
    UV = T.get("TEXCOORD_0", T.get("TEXCOORD0", np.zeros((len(P), 2)))).astype(np.float64)
    F = T["IDX"]
    lab = np.zeros(len(Dw_w), np.int8)
    for code, s in ((1, "left"), (2, "right")):
        cols = [chains[f"{s}_{p}"] for p in ("arm", "forearm", "hand")]
        cols += [i for i, sd, _ in chains["fingers"] if sd == s]
        cols = [c for c in cols if c is not None]
        lab[Dw_w[:, cols].sum(1) > 0.5] = code
    Lt = lab[wid[F]]
    mixed = ~((Lt[:, 0] == Lt[:, 1]) & (Lt[:, 1] == Lt[:, 2]))
    C = P[F].mean(1)
    cut = mixed.copy()
    for code, s in ((1, "left"), (2, "right")):
        a0, a1 = bp[chains[f"{s}_arm"]], bp[chains[f"{s}_forearm"]]
        r = keep_r * np.linalg.norm(a1 - a0)
        side = mixed & (Lt == code).any(1)
        near = np.linalg.norm(C - a0, axis=1) < r
        if BAND is not None:
            near = ~((C[:, 1] >= BAND[0]) & (C[:, 1] < BAND[1] - 0.02))
        cut[side & near] = False
    Fk = F[~cut]
    Fw = wid[Fk]
    e = np.concatenate([Fk[:, [0, 1]], Fk[:, [1, 2]], Fk[:, [2, 0]]])
    ew = wid[e]
    key = np.sort(ew, 1)
    u, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    bnd = e[cnt[inv.ravel()] == 1]
    Fall = wid[F]
    ea = np.sort(np.concatenate([Fall[:, [0, 1]], Fall[:, [1, 2]], Fall[:, [2, 0]]]), 1)
    ua, ca = np.unique(ea, axis=0, return_counts=True)
    orig_b = set(map(tuple, ua[ca == 1]))
    bnd = np.array([b for b in bnd if tuple(sorted((wid[b[0]], wid[b[1]]))) not in orig_b])
    nxt = {}
    for a_, b_ in bnd:
        nxt[wid[a_]] = (wid[b_], a_, b_)
    P2, N2, UV2 = [P], [N if N is not None else np.zeros_like(P)], [UV]
    newF = []
    nv = len(P)
    seen = set()
    loops = 0
    Dvert = Dw_w[wid]
    extraD = []
    for start in list(nxt):
        if start in seen:
            continue
        loop = []
        cur = start
        while cur in nxt and cur not in seen:
            seen.add(cur)
            w2, a_, b_ = nxt[cur]
            loop.append((a_, b_))
            cur = w2
        if len(loop) < 3 or cur != start:
            continue
        vs = np.array([a_ for a_, _ in loop])
        c = P[vs].mean(0)
        P2.append(c[None])
        nn = N2[0][vs].mean(0) if N is not None else np.array([0, 1, 0])
        nl = np.linalg.norm(nn)
        N2.append((nn / max(nl, 1e-9))[None])
        UV2.append(UV[vs[np.argmin(np.linalg.norm(P[vs] - c, axis=1))]][None])
        extraD.append(Dvert[vs].mean(0))
        for a_, b_ in loop:
            newF.append((b_, a_, nv))
        nv += 1
        loops += 1
    Pn = np.concatenate(P2)
    Nn = np.concatenate(N2)
    UVn = np.concatenate(UV2)
    Dn = np.concatenate([Dvert, np.array(extraD).reshape(-1, Dvert.shape[1])])
    Fn = np.concatenate([Fk, np.array(newF, np.int64).reshape(-1, 3)])
    return Pn, Nn, UVn, Fn, Dn, dict(cut_tris=int(cut.sum()), caps=loops, cap_tris=len(newF))


def transfer(a):
    jt_doc, js_doc = GLBDoc(a.target), GLBDoc(a.source)
    jt, js = jt_doc.json, js_doc.json
    nj = len(js["skins"][0]["joints"])
    names = [js["nodes"][k].get("name", f"joint_{k}") for k in js["skins"][0]["joints"]]
    ibm = js_doc.accessor(js["skins"][0]["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)

    # source skin -> dense weights per source vert
    sprims = list(js_doc.primitives())
    if not sprims:
        raise ValueError("source has no mesh primitives")
    _, _, S, _ = sprims[0]
    Ps = S["POSITION"].astype(np.float64)
    Js = S["JOINTS_0"].astype(np.int64)
    Ws = S["WEIGHTS_0"].astype(np.float64)
    Ds = np.zeros((len(Ps), nj))
    np.add.at(Ds, (np.arange(len(Ps))[:, None], Js), Ws)
    Ds /= np.maximum(Ds.sum(1, keepdims=True), 1e-9)
    Ds32 = Ds.astype(np.float32)

    out_prims = []   # (mesh_name, P, N, UV, F, J4, W4, material)
    report_prims = []
    for mname, pi, T, Fidx in jt_doc.primitives():
        Pt = T["POSITION"].astype(np.float64)
        F = Fidx.reshape(-1, 3)
        H = Pt[:, 1].max() - Pt[:, 1].min()
        wid = weld(Pt)
        nW = wid.max() + 1
        Pw = np.zeros((nW, 3))
        Pw[wid] = Pt
        # 1. transfer on welded verts (chunked k-NN inverse-distance)
        dist, ix = cKDTree(Ps).query(Pw, k=a.k)
        w = 1.0 / np.maximum(dist, 1e-5) ** 2
        w /= w.sum(1, keepdims=True)
        Dw = np.zeros((nW, nj), np.float32)
        for c0 in range(0, nW, 100000):
            Dw[c0:c0 + 100000] = np.einsum(
                "nk,nkj->nj", w[c0:c0 + 100000].astype(np.float32), Ds32[ix[c0:c0 + 100000]])
        # 2. islands -> rigid bind at attach point
        u, cnt, A = topo(F, wid, nW)
        nc, lab = connected_components(A, directed=False)
        sizes = np.bincount(lab)
        main = sizes.argmax()
        mi = np.where(lab == main)[0]
        tree = cKDTree(Pw[mi])
        fixed_isl = 0
        for c in np.where(sizes < a.island_frac * nW)[0]:
            vv = np.where(lab == c)[0]
            dd, nn = tree.query(Pw[vv], k=1)
            anchor = mi[nn[dd.argmin()]]
            Dw[vv] = Dw[anchor]
            fixed_isl += 1
        # 3. limb separation (tolerant joint matching; loud skip if incompatible)
        limb_moved, limb_skip = 0, None
        if a.limb_separate:
            Dw, limb_moved, limb_skip = limb_separate(names, ibm, Pw, Dw, A)
        # 4. smooth on welded topology
        deg = np.asarray(A.sum(1)).ravel()
        Lr = diags(1 / np.maximum(deg, 1)) @ A
        for _ in range(a.smooth):
            Dw = 0.5 * Dw + 0.5 * (Lr @ Dw)
        cutinfo = None
        if a.cut_fused:
            Pn, Nn, UVn, Fn, Dv, cutinfo = cut_fused(names, ibm, T, wid, Dw)
            P4, N4 = Pn.astype(np.float32), Nn.astype(np.float32)
            UV4 = UVn.astype(np.float32)
            Fn4 = Fn
        else:
            P4 = T["POSITION"].astype(np.float32)
            N4 = T["NORMAL"].astype(np.float32) if "NORMAL" in T else None
            UV4 = T.get("TEXCOORD_0", T.get("TEXCOORD0"))
            UV4 = UV4.astype(np.float32) if UV4 is not None else None
            Dv = Dw[wid]
            Fn4 = F
        # limit 4 + normalize
        top = np.argsort(-Dv, 1)[:, :4]
        tw = np.take_along_axis(Dv, top, 1)
        tw[tw < 1e-3] = 0
        tw /= np.maximum(tw.sum(1, keepdims=True), 1e-9)
        J4 = top.astype(np.uint8 if nj < 256 else np.uint16)
        W4 = tw.astype(np.float32)
        out_prims.append((mname, P4, N4, UV4, Fn4, J4, W4))
        report_prims.append({"mesh": mname, "prim_index": pi, "verts": int(len(P4)),
                             "islands": int(nc), "islands_bound_rigid": fixed_isl,
                             "limb_separate_moved": limb_moved,
                             "limb_separate_skipped": limb_skip, "cut_fused": cutinfo})

    # build output = source JSON (skeleton, skin, IBMs) + target geometry/material/textures.
    # Mesh names come from the TARGET (PR #77 hardcoded "STICKUP_HQ").
    out = json.loads(json.dumps(js))
    blob = bytearray()
    out["bufferViews"] = []
    out["accessors"] = []

    def addbv(data, target=None):
        while len(blob) % 4:
            blob.append(0)
        bv = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
        if target:
            bv["target"] = target
        blob.extend(bytes(data))
        out["bufferViews"].append(bv)
        return len(out["bufferViews"]) - 1

    def addacc(arr, ct, typ, target=None, mm=False):
        arr = np.ascontiguousarray(arr)
        a_ = {"bufferView": addbv(arr.tobytes(), target), "componentType": ct,
              "count": int(arr.shape[0]), "type": typ}
        if mm:
            a_["min"] = arr.min(0).tolist()
            a_["max"] = arr.max(0).tolist()
        out["accessors"].append(a_)
        return len(out["accessors"]) - 1

    def copyacc(i):
        a_ = dict(js["accessors"][i])
        data = js_doc.buffer_view_bytes(a_["bufferView"])
        a_["bufferView"] = addbv(data)
        out["accessors"].append(a_)
        return len(out["accessors"]) - 1

    for sk in out["skins"]:
        sk["inverseBindMatrices"] = copyacc(sk["inverseBindMatrices"])
    for an in out.get("animations", []):
        for sm in an["samplers"]:
            sm["input"] = copyacc(sm["input"])
            sm["output"] = copyacc(sm["output"])
    # group primitives by mesh name, preserving target mesh order
    meshes = []
    seen = {}
    for (mname, P4, N4, UV4, Fn4, J4, W4) in out_prims:
        attrs = {"POSITION": addacc(P4, 5126, "VEC3", 34962, True),
                 "JOINTS_0": addacc(J4, 5121 if J4.dtype == np.uint8 else 5123, "VEC4", 34962),
                 "WEIGHTS_0": addacc(W4, 5126, "VEC4", 34962)}
        if N4 is not None:
            attrs["NORMAL"] = addacc(N4, 5126, "VEC3", 34962)
        if UV4 is not None:
            attrs["TEXCOORD_0"] = addacc(UV4, 5126, "VEC2", 34962)
        prim = {"attributes": attrs,
                "indices": addacc(Fn4.astype(np.uint32).ravel()[:, None], 5125, "SCALAR", 34963),
                "mode": 4}
        if mname not in seen:
            seen[mname] = len(meshes)
            meshes.append({"name": mname, "primitives": []})
        meshes[seen[mname]]["primitives"].append(prim)
    out["meshes"] = meshes
    out["materials"] = jt["materials"]
    out["samplers"] = jt.get("samplers", [])
    out["textures"] = jt["textures"]
    out["images"] = []
    for im in jt["images"]:
        data = jt_doc.buffer_view_bytes(im["bufferView"])
        out["images"].append({"mimeType": im["mimeType"], "bufferView": addbv(data)})
    # preserve target extensions (PR #77 dropped them, e.g. EXT_texture_webp)
    for k in ("extensionsUsed", "extensionsRequired"):
        vals = [e for e in jt.get(k, []) if e != "EXT_meshopt_compression"]
        if vals:
            out[k] = vals
        else:
            out.pop(k, None)
    out["asset"] = {"version": "2.0", "generator": "rig-repair pipeline transfer v2 (universal)"}
    while len(blob) % 4:
        blob.append(0)
    out["buffers"] = [{"byteLength": len(blob)}]
    jb = json.dumps(out, separators=(",", ":")).encode()
    jb += b" " * (-len(jb) % 4)
    assert not os.path.exists(a.out) or a.force, "refusing to overwrite " + a.out
    with open(a.out, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 28 + len(jb) + len(blob)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)
    rep = {"target": a.target, "source": a.source, "out": a.out, "joints": nj,
           "primitives": report_prims,
           "before_target": detect(a.target), "before_source": detect(a.source),
           "after": detect(a.out)}
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "before_target"
                      and k != "before_source" and k != "after"}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    d = sp.add_parser("detect")
    d.add_argument("model")
    d.add_argument("--json")
    t = sp.add_parser("transfer")
    for k in ("target", "source", "out"):
        t.add_argument("--" + k, required=True)
    t.add_argument("--report")
    t.add_argument("--k", type=int, default=6)
    t.add_argument("--smooth", type=int, default=3)
    t.add_argument("--island-frac", type=float, default=0.002)
    t.add_argument("--force", action="store_true")
    t.add_argument("--limb-separate", action="store_true")
    t.add_argument("--cut-fused", action="store_true")
    a = ap.parse_args()
    if a.cmd == "detect":
        r = detect(a.model)
        print(json.dumps({k: v for k, v in r.items() if k != "per_primitive"}, indent=1))
        if r.get("note"):
            print("NOTE:", r["note"], file=sys.stderr)
        if a.json:
            json.dump(r, open(a.json, "w"), indent=1)
    elif a.cmd == "transfer":
        transfer(a)
    else:
        ap.print_help()
        sys.exit(2)
