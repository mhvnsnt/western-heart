"""skin_donor.py — donor-surface skin-weight transfer for df_rig_bake.

Replaces Blender bone-heat, which fails outright on Tripo multi-shell
statics ("Bone Heat Weighting: failed to find solution" -> the stock
fallback pins every vertex rigidly to its nearest bone head = tearing).

Method (deterministic, production-standard data transfer):
  1. Import the donor (Iori) and normalize it into the target's frame
     with the backend's own normalize_and_face (same estimator on both
     models, so the frames coincide by construction).
  2. Resolve every donor vertex group to a DEF bone name of the new rig:
     Bip001->canonical->DEF bridge first, then nearest mapped ancestor
     on the donor armature (hair/cloth chains root to head/pelvis/...).
     Unresolvable groups are dropped.
  3. Join the donor meshes, build a BVHTree of the donor surface.
  4. For each target vertex: nearest donor face + barycentric interp of
     that face's verts' weights -> smooth weights, top-4, normalized.
  5. Parent the target meshes to the new rig; stragglers (no donor face
     found / empty weights) get nearest-bone-head fixup.
"""

import math

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree


def _def_for_bip(gb, inv_bip_map, name):
    canon = inv_bip_map.get(name)
    if canon is None and name.rsplit("_", 1)[-1].isdigit():
        # import-dedup variants like "Bip001 Head_019_0"
        canon = inv_bip_map.get(name.rsplit("_", 1)[0])
    if canon is None:
        return None
    return gb.DONOR_TO_DEF.get(canon)


def _get_group(mesh, cache, name):
    vg = cache.get(name)
    if vg is None:
        for g in mesh.vertex_groups:
            if g.name == name:
                vg = g
                break
        if vg is None:
            vg = mesh.vertex_groups.new(name=name)
        cache[name] = vg
    return vg


def skin_via_donor(gb, rig, meshes, donor_path, height, bip_map,
                   stance_basis=None):
    stats = {}
    rig_bones = {b.name for b in rig.data.bones if b.use_deform}

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=donor_path)
    new_objs = [o for o in bpy.data.objects if o not in before]
    d_meshes = [o for o in new_objs if o.type == "MESH"
                and len(o.vertex_groups) > 0]
    d_arm = next((o for o in new_objs if o.type == "ARMATURE"), None)
    if not d_meshes:
        raise RuntimeError("donor import produced no skinned meshes")
    stats["donor_meshes"] = [(m.name, len(m.data.vertices))
                             for m in d_meshes]

    _xs, _ys, _zs = gb.mesh_world_stats(d_meshes)
    stats["donor_height_raw"] = round(float(_zs.max() - _zs.min()), 3)
    _norm = gb.normalize_and_face(d_meshes, height)
    stats["donor_yaw_deg"] = round(_norm["yaw_deg"], 2)

    inv_bip = {v: k for k, v in bip_map.items()}
    arm_bones = {}
    if d_arm is not None:
        arm_bones = {b.name: b for b in d_arm.data.bones}

    def resolve(name):
        d = _def_for_bip(gb, inv_bip, name)
        if d:
            return d
        b = arm_bones.get(name)
        while b is not None:
            d = _def_for_bip(gb, inv_bip, b.name)
            if d:
                return d
            b = b.parent
        return None

    dropped = []
    for m in d_meshes:
        plan = [(vg.name, resolve(vg.name)) for vg in list(m.vertex_groups)]
        for old, new in plan:
            if old not in m.vertex_groups:
                continue
            vg = m.vertex_groups[old]
            if new is None or new not in rig_bones:
                dropped.append(old)
                m.vertex_groups.remove(vg)
            elif new == old:
                pass
            elif new in m.vertex_groups:
                tgt = m.vertex_groups[new]
                oi = vg.index
                for v in m.data.vertices:
                    for g in v.groups:
                        if g.group == oi:
                            tgt.add([v.index], g.weight, "ADD")
                m.vertex_groups.remove(vg)
            else:
                vg.name = new
    stats["dropped_groups"] = dropped

    for m in d_meshes:
        for mod in list(m.modifiers):
            if mod.type == "ARMATURE":
                m.modifiers.remove(mod)
    if d_arm is not None:
        bpy.data.objects.remove(d_arm, do_unlink=True)

    bpy.ops.object.select_all(action="DESELECT")
    for m in d_meshes:
        m.select_set(True)
    # join INTO the largest skinned mesh: joining into a group-less base
    # can drop the other meshes' vertex-group assignments
    base = max(d_meshes, key=lambda m: len(m.data.vertices))
    bpy.context.view_layer.objects.active = base
    if len(d_meshes) > 1:
        bpy.ops.object.join()
    donor = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True,
                                   scale=True)

    dmesh = donor.data
    gname = [vg.name for vg in donor.vertex_groups]
    dverts_w = [[(gname[g.group], g.weight) for g in v.groups
                 if g.weight > 0.0] for v in dmesh.vertices]
    n_weighted = sum(1 for w in dverts_w if w)
    stats["donor_weighted_verts"] = n_weighted
    print("SKINDBG joined donor: verts=%d groups=%d weighted=%d polys=%d"
          % (len(dmesh.vertices), len(gname), n_weighted,
             len(dmesh.polygons)), flush=True)
    if n_weighted == 0:
        raise RuntimeError("joined donor lost all skin weights")
    dco = [v.co for v in dmesh.vertices]
    _boxes = {"thighL": lambda p: 0.03 < p[0] < 0.2 and 0.6 < p[2] < 0.95,
              "armL": lambda p: 0.25 < p[0] < 0.55 and 1.38 < p[2] < 1.5,
              "hair": lambda p: p[2] > 1.62}
    from collections import Counter as _Counter
    for _bn, _bf in _boxes.items():
        _cnt = _Counter()
        for _vi, _wlist in enumerate(dverts_w):
            if _wlist and _bf(dco[_vi]):
                _cnt[max(_wlist, key=lambda e: e[1])[0]] += 1
        print("SKINDBG donor %s: %s" % (_bn, _cnt.most_common(4)),
              flush=True)
    polys = dmesh.polygons
    tree = BVHTree.FromPolygons([v.co for v in dmesh.vertices],
                                [p.vertices for p in polys],
                                all_triangles=True)

    # deform bone world heads for the straggler fixup
    rmw = rig.matrix_world
    heads = [(b.name, rmw @ b.head_local) for b in rig.data.bones
             if b.use_deform]

    # Matched-pose transfer: the donor surface is bound IN Iori's
    # stance while the target rests in a T-pose, so nearest-face on
    # rest coords binds whole regions to whatever stance part happens
    # to be nearest (arm verts -> thigh bones, hair -> arms). Pose the
    # target verts INTO the stance first (capsule weights + the
    # stance bone matrices, pure numpy) and query the BVH with the
    # posed coords; weights are per-vertex and stay valid at rest.
    Mbone = {}
    seg_names = []
    segA = None
    segB = None
    if stance_basis:
        for pb in rig.pose.bones:
            pb.rotation_mode = "QUATERNION"
            if pb.name in stance_basis:
                pb.rotation_quaternion = stance_basis[pb.name]
        bpy.context.view_layer.update()
        rmw_np = np.array(rig.matrix_world, dtype=np.float64)
        rmw_inv = np.linalg.inv(rmw_np)
        _A = []
        _B = []
        for b in rig.data.bones:
            if not b.use_deform:
                continue
            S = np.array(rig.pose.bones[b.name].matrix,
                         dtype=np.float64)
            Mbone[b.name] = rmw_np @ S @ np.array(
                b.matrix_local.inverted(), dtype=np.float64) @ rmw_inv
            seg_names.append(b.name)
            _A.append(np.array(rmw @ b.head_local, dtype=np.float64))
            _B.append(np.array(rmw @ b.tail_local, dtype=np.float64))
        for pb in rig.pose.bones:
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        bpy.context.view_layer.update()
        segA = np.array(_A)
        segB = np.array(_B)
        print("SKINDBG stance posing ready: %d bone matrices"
              % len(Mbone), flush=True)

    def prep_pose(P):
        """(posed_coords, capsule_weights, seg_distances) for the
        mesh verts P (world, rest). Capsule weights: sharp inverse
        kernel over DEF bone SEGMENT distances — anatomically sane by
        construction (side-correct, nothing binds across the body);
        used to pose the mesh into the stance AND as the fallback
        wherever the surface transfer is untrustworthy."""
        if not Mbone:
            return P, None, None
        n = len(P)
        D = np.empty((n, len(seg_names)), dtype=np.float64)
        for j in range(len(seg_names)):
            a = segA[j]
            ab = segB[j] - a
            L2 = float(ab @ ab)
            if L2 <= 0.0:
                t = np.zeros(n)
            else:
                t = np.clip(((P - a) @ ab) / L2, 0.0, 1.0)
            c = a + t[:, None] * ab
            D[:, j] = np.linalg.norm(P - c, axis=1)
        k = min(4, len(seg_names))
        idx = np.argpartition(D, k - 1, axis=1)[:, :k]
        dk = np.take_along_axis(D, idx, axis=1)
        w = 1.0 / (dk + 0.025) ** 2.5
        w = w / w.sum(axis=1, keepdims=True)
        cap = [[(seg_names[jj], float(ww))
                for jj, ww in zip(idx[i], w[i]) if ww > 1e-4]
               for i in range(n)]
        Marr = np.stack([Mbone[nm] for nm in seg_names])
        Mk = Marr[idx]
        Ph = np.concatenate([P, np.ones((n, 1))], axis=1)
        tr = np.einsum("nkij,nj->nki", Mk, Ph)[:, :, :3]
        return np.einsum("nk,nki->ni", w, tr), cap, D

    seg_index = {nm: j for j, nm in enumerate(seg_names)}

    total_fixed = 0
    total_capfb = 0
    total_verts = 0
    for mesh in meshes:
        n = len(mesh.data.vertices)
        total_verts += n
        co = np.empty(n * 3, dtype=np.float64)
        mesh.data.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        M = np.array(mesh.matrix_world, dtype=np.float64)
        co = co @ M[:3, :3].T + M[:3, 3]

        qco, cap_w, segD = prep_pose(co)
        if mesh is meshes[0] and Mbone:
            _qc = _Counter()
            for _vi in range(n):
                _p = qco[_vi]
                if 0.03 < _p[0] < 0.2 and 0.6 < _p[2] < 0.95:
                    _qc["thighL_posed"] += 1
            print("SKINDBG target posed-in-thighL-box: %s (of %d verts)"
                  % (dict(_qc), n), flush=True)
        cache = {}
        if mesh is meshes[0]:
            print("SKINDBG target world bbox: min=%s max=%s | donor "
                  "sample vert=%s" % (co.min(0).round(3).tolist(),
                                      co.max(0).round(3).tolist(),
                                      [round(float(c), 3) for c in dco[0]]),
                  flush=True)
            hits = 0
            for i in range(min(n, 2000)):
                _l, _n2, _f, _d = tree.find_nearest(tuple(co[i]))
                if _f is not None:
                    hits += 1
            print("SKINDBG find_nearest hits in first 2000: %d" % hits,
                  flush=True)
        for i in range(n):
            loc, _nrm, fi, _dist = tree.find_nearest(tuple(qco[i]))
            pw = None
            if fi is not None:
                vs = polys[fi].vertices
                a, b, c = dco[vs[0]], dco[vs[1]], dco[vs[2]]
                v0 = b - a
                v1 = c - a
                v2 = loc - a
                d00 = v0.dot(v0)
                d01 = v0.dot(v1)
                d11 = v1.dot(v1)
                d20 = v2.dot(v0)
                d21 = v2.dot(v1)
                den = d00 * d11 - d01 * d01
                if abs(den) < 1e-14:
                    bary = (1.0, 0.0, 0.0)
                else:
                    bv = (d11 * d20 - d01 * d21) / den
                    bw = (d00 * d21 - d01 * d20) / den
                    bu = 1.0 - bv - bw
                    bu = max(0.0, min(1.0, bu))
                    bv = max(0.0, min(1.0, bv))
                    bw = max(0.0, min(1.0, bw))
                    s = bu + bv + bw
                    bary = (bu / s, bv / s, bw / s)
                acc = {}
                for bk, vi in zip(bary, vs):
                    if bk <= 0.0:
                        continue
                    for name, wt in dverts_w[vi]:
                        acc[name] = acc.get(name, 0.0) + bk * wt
                if acc:
                    top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
                    s = sum(w for _, w in top)
                    if s > 0:
                        pw = [(name, w / s) for name, w in top]
            # trust composition: the surface transfer is detailed
            # but can bind a vert to a bone whose segment is nowhere
            # near it (cross-body assignments from the stance-bound
            # donor). Trust it only when every bone it names passes
            # near the vert; otherwise fall back to the capsule
            # weights, which are anatomically sane by construction.
            final = None
            if pw:
                if segD is not None:
                    dmin = float(segD[i].min())
                    if all(nm not in seg_index
                           or segD[i][seg_index[nm]] <= dmin + 0.12
                           for nm, _w in pw):
                        final = pw
                else:
                    final = pw
            if final is None and cap_w is not None:
                final = cap_w[i]
                total_capfb += 1
            if final:
                for name, w in final:
                    _get_group(mesh, cache, name).add([i], float(w),
                                                      "REPLACE")
            else:
                # straggler: nearest deform bone head, rigid
                from mathutils import Vector
                p = Vector(co[i])
                bn, bd = None, None
                for name, h in heads:
                    d = (h - p).length_squared
                    if bd is None or d < bd:
                        bd, bn = d, name
                if bn is not None:
                    _get_group(mesh, cache, bn).add([i], 1.0, "REPLACE")
                    total_fixed += 1

        if not any(mod.type == "ARMATURE" and mod.object == rig
                   for mod in mesh.modifiers):
            mod = mesh.modifiers.new("Armature", "ARMATURE")
            mod.object = rig
        world = mesh.matrix_world.copy()
        mesh.parent = rig
        mesh.matrix_parent_inverse = rig.matrix_world.inverted()
        mesh.matrix_world = world

    # side-consistency repair: the donor is bound IN Iori's stance
    # (arms hanging close across the body), so nearest-face transfer
    # can assign a target vert to the OPPOSITE side's arm/leg bones —
    # those verts then fly across the body when the limbs move. A vert
    # clearly on one side of the sagittal plane is never skinned to
    # the other side's bones in a sane rig: swap its .L/.R weights.
    import os
    if os.environ.get("DF_NO_SWAP"):
        stats["side_swapped"] = -1
        stats["segment_capped"] = -1
        stats["unweighted_fixed"] = total_fixed
        stats["skinned_via"] = "donor-bvh-polyinterp"
        bpy.data.objects.remove(donor, do_unlink=True)
        return stats

    def _swap_side(nm):
        if nm.endswith(".L"):
            return nm[:-2] + ".R"
        if nm.endswith(".R"):
            return nm[:-2] + ".L"
        return None

    total_swapped = 0
    for mesh in meshes:
        n = len(mesh.data.vertices)
        co = np.empty(n * 3, dtype=np.float64)
        mesh.data.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        M = np.array(mesh.matrix_world, dtype=np.float64)
        wx = co @ M[:3, :3].T + M[:3, 3]
        gname = [vg.name for vg in mesh.vertex_groups]
        cache = {nm: mesh.vertex_groups[nm] for nm in gname}
        for v in mesh.data.vertices:
            if not v.groups:
                continue
            dom = max(v.groups, key=lambda e: e.weight)
            dn = gname[dom.group]
            x = float(wx[v.index][0])
            if not ((dn.endswith(".L") and x < -0.02)
                    or (dn.endswith(".R") and x > 0.02)):
                continue
            entries = [(gname[g.group], g.weight) for g in v.groups]
            if not any(_swap_side(nm) for nm, _w in entries):
                continue
            for nm, _w in entries:
                cache[nm].remove([v.index])
            for nm, w in entries:
                sn = _swap_side(nm) or nm
                if sn not in cache:
                    cache[sn] = mesh.vertex_groups.new(name=sn)
                cache[sn].add([v.index], float(w), "REPLACE")
            total_swapped += 1
    stats["side_swapped"] = total_swapped
    print("SKINDBG side_swapped=%d" % total_swapped, flush=True)

    if os.environ.get("DF_NO_CAP"):
        stats["segment_capped"] = -1
        stats["unweighted_fixed"] = total_fixed
        stats["skinned_via"] = "donor-bvh-polyinterp"
        bpy.data.objects.remove(donor, do_unlink=True)
        return stats

    # segment-distance cap: surface transfer can bind a vert to a
    # bone whose segment passes nowhere near it (hair over the
    # shoulders picking up arm weights from the donor's stance-bound
    # surface). Drop any weight whose bone segment is much farther
    # from the vert than the vert's own nearest weighted segment.
    from mathutils import Vector

    def _seg_dist(p, a, b):
        ab = b - a
        t = 0.0
        if ab.length_squared > 0.0:
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        return (a + ab * t - p).length

    segs = {}
    for b in rig.data.bones:
        if b.use_deform:
            segs[b.name] = (rmw @ b.head_local, rmw @ b.tail_local)
    total_capped = 0
    for mesh in meshes:
        n = len(mesh.data.vertices)
        co = np.empty(n * 3, dtype=np.float64)
        mesh.data.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        M = np.array(mesh.matrix_world, dtype=np.float64)
        wco = co @ M[:3, :3].T + M[:3, 3]
        gname = [vg.name for vg in mesh.vertex_groups]
        cache = {nm: mesh.vertex_groups[nm] for nm in gname}
        for v in mesh.data.vertices:
            if not v.groups:
                continue
            entries = [(gname[g.group], g.weight) for g in v.groups
                       if gname[g.group] in segs]
            if len(entries) < 2:
                continue
            p = Vector(wco[v.index])
            dists = {nm: _seg_dist(p, segs[nm][0], segs[nm][1])
                     for nm, _w in entries}
            dmin = min(dists.values())
            keep = [(nm, w) for nm, w in entries
                    if dists[nm] <= dmin + 0.15]
            if len(keep) == len(entries):
                continue
            if not keep:
                keep = [min(entries, key=lambda e: dists[e[0]])]
            for nm, _w in entries:
                cache[nm].remove([v.index])
            s = sum(w for _nm, w in keep)
            for nm, w in keep:
                cache[nm].add([v.index], float(w / s), "REPLACE")
            total_capped += 1
    stats["segment_capped"] = total_capped
    print("SKINDBG segment_capped=%d" % total_capped, flush=True)

    # anatomical weight sanitizer (stance-fix, 2026-10-21). The
    # shipped skin measured ~94% capsule-fallback verts: the capsule
    # kernel is chain-blind, so chest verts ended up dominated by the
    # SHOULDER bones (wolf chest core: RightShoulder 24%), hair/mane
    # verts carried 20-31% shoulder/spine/arm weight (yanked sideways
    # under animation = the twisting, clipping hair), and torso verts
    # blended hips+neck+shoulders at once (the crumple). Fix: every
    # vert keeps only weights inside the anatomical chain set of its
    # dominant bone, with opposite-side limb weights zeroed; verts in
    # the head zone keep head+neck only. Deterministic post-pass on
    # whatever the transfer produced.
    import os as _os2
    _SAN_SKIP = bool(_os2.environ.get("DF_NO_SANITIZE"))
    if _SAN_SKIP:
        print("SKINDBG sanitizer DISABLED (DF_NO_SANITIZE): "
              "pass-through mask", flush=True)
    import re as _re
    _TOKENS = (("shoulder", "shoulder"), ("upper_arm", "arm"),
               ("forearm", "forearm"), ("palm", "hand"),
               ("hand", "hand"), ("thumb", "finger"),
               ("f_index", "finger"), ("f_middle", "finger"),
               ("f_ring", "finger"), ("f_pinky", "finger"),
               ("thigh", "thigh"), ("shin", "shin"), ("foot", "foot"),
               ("toe", "toe"), ("breast", "breast"),
               ("pelvis", "spine"))

    def _classify(nm):
        m = _re.search(r"\.(L|R)(\.|$)", nm)
        side = m.group(1) if m else None
        if nm.startswith("DEF-spine"):
            mm = _re.search(r"\.(\d{3})$", nm)
            lev = int(mm.group(1)) if mm else 0
            if lev <= 3:
                return ("spine", side, lev)
            if lev == 4:
                return ("neck", side, lev)
            return ("head", side, lev)
        for tok, chain in _TOKENS:
            if tok in nm:
                return (chain, side, 0)
        return (None, side, 0)

    _bone_parent = {b.name: (b.parent.name if b.parent else None)
                    for b in rig.data.bones}
    _bone_cls = {}

    def _cls(nm):
        if nm in _bone_cls:
            return _bone_cls[nm]
        c = _classify(nm)
        seen = nm
        while c[0] is None and _bone_parent.get(seen) is not None:
            seen = _bone_parent[seen]
            c2 = _classify(seen)
            c = (c2[0], c[1] if c[1] is not None else c2[1], c2[2])
        _bone_cls[nm] = c
        return c

    _ALLOWED = {
        "head": {"head", "neck"},
        "neck": {"neck", "head", "spine", "shoulder"},
        "spine": {"spine", "neck", "shoulder", "breast"},
        "breast": {"breast", "spine", "shoulder"},
        "shoulder": {"shoulder", "spine", "neck", "arm", "forearm",
                     "hand", "finger"},
        "arm": {"shoulder", "arm", "forearm", "hand", "finger"},
        "forearm": {"arm", "forearm", "hand", "finger"},
        "hand": {"forearm", "hand", "finger"},
        "finger": {"forearm", "hand", "finger"},
        "thigh": {"thigh", "shin", "spine"},
        "shin": {"thigh", "shin", "foot"},
        "foot": {"shin", "foot", "toe"},
        "toe": {"shin", "foot", "toe"},
    }
    _LIMB = {"shoulder", "arm", "forearm", "hand", "finger", "thigh",
             "shin", "foot", "toe", "breast"}
    _LEG = {"thigh", "shin", "foot", "toe"}
    _neck_head = None
    for _b in rig.data.bones:
        if _cls(_b.name)[0] == "neck":
            _neck_head = rmw @ _b.head_local
            break
    san_masks = {}
    total_sanitized = 0
    mass_dropped = 0.0
    for mesh in meshes:
        n = len(mesh.data.vertices)
        G = len(mesh.vertex_groups)
        if G == 0 or n == 0:
            continue
        gname = [vg.name for vg in mesh.vertex_groups]
        cls = [_cls(nm) for nm in gname]
        chains = [c[0] for c in cls]
        if any(c is None for c in chains):
            print("SKINDBG sanitizer: unclassified groups %s"
                  % [gname[i] for i, c in enumerate(chains)
                     if c is None], flush=True)
            continue
        W = np.zeros((n, G), dtype=np.float64)
        for v in mesh.data.vertices:
            for g in v.groups:
                W[v.index, g.group] = g.weight
        dom = W.argmax(axis=1)
        dom_chain = [chains[int(j)] for j in dom]
        dom_side = [cls[int(j)][1] for j in dom]
        dom_level = [cls[int(j)][2] for j in dom]
        # v2: state 0=ban, 1=allow, 2=bridge (kept but weight-capped).
        # v1's hard zeroing tore the waist/armpit/neck seams (disjoint
        # weight sets on adjacent verts = edge-stretch spikes, waist
        # band p99 3.5 -> 13.6 measured). Bridge bones keep a capped
        # gradient across the hip and shoulder seams while banned
        # chains (cross-side limbs, cross-limb, head-zone violations)
        # stay at zero.
        state = np.zeros((n, G), dtype=np.uint8)
        capv = np.full((n, G), 0.20, dtype=np.float64)
        if _SAN_SKIP:
            state[:, :] = 1
        for i in range(n):
            if _SAN_SKIP:
                break
            dc = dom_chain[i]
            allow = _ALLOWED.get(dc, set(chains))
            ds = dom_side[i]
            dl = dom_level[i]
            for j in range(G):
                cj = chains[j]
                sj = cls[j][1]
                lj = cls[j][2]
                if (ds is not None and sj is not None and sj != ds
                        and cj in _LIMB):
                    continue
                if cj in allow:
                    if (dc in _LEG and cj == "spine" and lj > 0
                            and "pelvis" not in gname[j]):
                        if lj == 1:
                            state[i, j] = 2
                        continue
                    state[i, j] = 1
                    continue
                if dc == "spine" and dl <= 1 and cj == "thigh":
                    state[i, j] = 2
                elif dc == "spine" and dl >= 2 and cj == "arm":
                    state[i, j] = 2
                elif dc in ("arm", "forearm") and cj == "spine" \
                        and lj == 3:
                    state[i, j] = 2
        hz_rows = np.zeros(n, dtype=bool)
        if _neck_head is not None and not _SAN_SKIP:
            co = np.empty(n * 3, dtype=np.float64)
            mesh.data.vertices.foreach_get("co", co)
            co = co.reshape(n, 3)
            M = np.array(mesh.matrix_world, dtype=np.float64)
            wco = co @ M[:3, :3].T + M[:3, 3]
            hz = (wco[:, 2] > float(_neck_head.z) - 0.005) & (
                (wco[:, 0] - float(_neck_head.x)) ** 2
                + (wco[:, 1] - float(_neck_head.y)) ** 2 < 0.35 ** 2)
            hz_rows = hz
            head_cols = [j for j in range(G)
                         if chains[j] in ("head", "neck")]
            sp3_cols = [j for j in range(G)
                        if chains[j] == "spine" and cls[j][2] == 3]
            for i in np.nonzero(hz)[0]:
                state[i, :] = 0
                state[i, head_cols] = 1
                for j in sp3_cols:
                    state[i, j] = 2
                    capv[i, j] = 0.15
            print("SKINDBG sanitizer head-zone verts: %d"
                  % int(hz.sum()), flush=True)
        mask = state > 0
        dropped = W * (~mask)
        mass_dropped += float(dropped.sum())
        W2 = W * mask
        empty = W2.sum(axis=1) <= 0
        if empty.any():
            neck_cols = [j for j in range(G) if chains[j] == "neck"]
            for i in np.nonzero(empty)[0]:
                if hz_rows[i] and neck_cols:
                    W2[i, neck_cols[0]] = 1.0
                else:
                    W2[i, int(dom[i])] = 1.0
        for _ in range(2):
            W2 = np.where(state == 2, np.minimum(W2, capv), W2)
            W2 = W2 / np.maximum(W2.sum(axis=1, keepdims=True), 1e-12)
        san_masks[id(mesh)] = mask
        cache = {nm: mesh.vertex_groups[nm] for nm in gname}
        changed = 0
        for i in range(n):
            row = W2[i]
            keep = [int(j) for j in row.argsort()[::-1][:4]
                    if row[j] >= 0.01]
            if not keep:
                keep = [int(row.argmax())]
            old = [g.group for g in mesh.data.vertices[i].groups]
            if set(old) == set(keep) and all(
                    abs(float(row[j]) - dict(
                        (g.group, g.weight)
                        for g in mesh.data.vertices[i].groups
                        ).get(j, 0.0)) < 1e-6 for j in keep):
                continue
            s = sum(float(row[j]) for j in keep)
            for gj in old:
                cache[gname[gj]].remove([i])
            for j in keep:
                cache[gname[j]].add([i], float(row[j] / s), "REPLACE")
            changed += 1
        total_sanitized += changed
        print("SKINDBG sanitizer mesh=%s changed=%d/%d"
              % (mesh.name, changed, n), flush=True)
    stats["sanitized_verts"] = total_sanitized
    stats["sanitized_mass_dropped"] = round(mass_dropped, 1)
    print("SKINDBG sanitized total=%d mass=%.1f"
          % (total_sanitized, mass_dropped), flush=True)

    # weight smoothing: hard weight transitions across a joint line
    # (ankle, armpit) concentrate edge stretch on a few edges.
    # Spread each vert's weights toward its edge-neighbors' average
    # (2 passes) so deformation gradients cover a few cm of surface.
    for mesh in meshes:
        n = len(mesh.data.vertices)
        G = len(mesh.vertex_groups)
        if G == 0 or n == 0:
            continue
        W = np.zeros((n, G), dtype=np.float64)
        orig_nz = []
        for v in mesh.data.vertices:
            nz = []
            for g in v.groups:
                W[v.index, g.group] = g.weight
                nz.append(g.group)
            orig_nz.append(nz)
        e = np.array([tuple(ed.vertices) for ed in mesh.data.edges],
                     dtype=np.int64)
        if len(e) == 0:
            continue
        src = np.concatenate([e[:, 0], e[:, 1]])
        dst = np.concatenate([e[:, 1], e[:, 0]])
        counts = np.maximum(np.bincount(src, minlength=n), 1)
        for _ in range(2):
            S = np.zeros_like(W)
            np.add.at(S, src, W[dst])
            W = 0.65 * W + 0.35 * (S / counts[:, None])
        # smoothing must not re-import bones the sanitizer banned
        # (that is exactly how cross-chain weights used to creep
        # back): restrict the smoothed weights to the allowed set.
        _mask = san_masks.get(id(mesh))
        if _mask is not None and _mask.shape == W.shape:
            _pre = W.copy()
            W = W * _mask
            _rs = W.sum(axis=1)
            _bad = _rs <= 0
            if _bad.any():
                W[_bad] = _pre[_bad] * _mask[_bad]
                _rs = W.sum(axis=1)
            W = W / np.maximum(_rs, 1e-12)[:, None]
        gname = [vg.name for vg in mesh.vertex_groups]
        cache = {nm: mesh.vertex_groups[nm] for nm in gname}
        for i in range(n):
            row = W[i]
            if row.max() <= 0:
                continue
            keep = [int(j) for j in row.argsort()[::-1][:4]
                    if row[j] >= 0.01]
            if not keep:
                keep = [int(row.argmax())]
            s = sum(float(row[j]) for j in keep)
            if s <= 0:
                continue
            for gj in orig_nz[i]:
                cache[gname[gj]].remove([i])
            for j in keep:
                cache[gname[j]].add([i], float(row[j] / s), "REPLACE")
    stats["smoothed"] = True
    print("SKINDBG smoothed", flush=True)

    stats["unweighted_fixed"] = total_fixed
    stats["capsule_fallback"] = total_capfb
    stats["skinned_via"] = "donor-bvh-polyinterp"
    bpy.data.objects.remove(donor, do_unlink=True)
    if total_verts and total_fixed > 0.05 * total_verts:
        raise RuntimeError(
            "donor transfer covered too few verts: %d/%d fell back to "
            "rigid fixup" % (total_fixed, total_verts))
    return stats
