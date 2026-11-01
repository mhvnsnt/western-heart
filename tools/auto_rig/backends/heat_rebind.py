#!/usr/bin/env python3
"""tools/auto_rig/backends/heat_rebind.py — stage 2 of the skeleton refit: armature + bone-heat skin (Blender).

Takes a model GLB (rigged or static) and a joint fit from tools/auto_rig/refit_skeleton.py. Drops the model's
old skeleton and skin, builds the fitted skeleton (canonical WH joint names, mesh facing +Z, Left* = the
character's left), skins the mesh with Blender bone heat (automatic weights; dense Tripo meshes through the
voxel-remesh proxy of gamerig_backend.heat_via_proxy) and exports a GLB. The input file is never modified.

    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup --python heat_rebind.py -- \\
        --in MODEL.glb --fit fit.json --out MODEL-refit.glb [--metrics-out m.json] [--height 2.0] [--donor BVH]

Plain glTF in (decode meshopt first). No animations are exported: the game drives every fighter with the
decoded Tekken 3 banks retargeted at runtime (game/js/t3anims.js).

--donor BVH|GLB bakes ONE test clip (gamerig_backend.transfer_clip, world-space rotation deltas) so the repo's
deformation gates can measure the skin: anim_check.py (edge stretch p99.9 <= 2.5) and smooth_weights.py need an
embedded clip. rig_tripo_static.py uses the CMU 135_04 boxing window (--clip-start 240 --clip-frames 72
--clip-step 4); strip the clip before shipping (the game never plays it).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def continuous_limit(mesh_obj, limit=4):
    """Limit every vertex to `limit` influences CONTINUOUSLY: subtract the (limit+1)-th largest weight from the top
    `limit`, renormalize. Blender's vertex_group_limit_total drops the 5th bone outright, so neighbours whose 4th/5th
    bones swap rank keep different bones and tear (measured on Negativo 2026-11-01: the whole strict-stretch plateau;
    attire 2 started smoothing at p99.9 9.39). Here a bone reaches 0 exactly where it leaves the top `limit`.
    Returns how many vertices had more than `limit` influences."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    dl = bm.verts.layers.deform.active
    n = 0
    if dl is not None:
        for v in bm.verts:
            d = v[dl]
            if len(d) <= limit:
                continue
            items = sorted(d.items(), key=lambda kv: -kv[1])
            t = items[limit][1]
            top = [(g, w - t) for g, w in items[:limit]]
            s = sum(w for _, w in top)
            if s <= 1e-9:
                top, s = items[:limit], sum(w for _, w in items[:limit]) or 1.0
            d.clear()
            for g, w in top:
                if w > 0:
                    d[g] = w / s
            n += 1
    bm.to_mesh(mesh_obj.data)
    bm.free()
    mesh_obj.data.update()
    return n


def gl2bl(p):
    """glTF (Y-up) -> Blender (Z-up) coordinates."""
    from mathutils import Vector
    return Vector((p[0], -p[2], p[1]))


def main():
    import bpy
    from mathutils import Matrix, Vector
    import gamerig_backend as G

    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--fit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--metrics-out", default=None)
    ap.add_argument("--voxel", type=float, default=G.HEAT_PROXY["voxel"])
    ap.add_argument("--proxy-faces", type=int, default=G.HEAT_PROXY["faces"])
    ap.add_argument("--height", type=float, default=None,
                    help="scale mesh + skeleton uniformly so the mesh is this tall (m). The game renders a fighter at "
                         "its GLB's own size (bodyScale defaults to 1): match the model being replaced")
    ap.add_argument("--donor", default=None, help="BVH/GLB to bake one deformation test clip from (gate only)")
    ap.add_argument("--clip", default="CMU135_04_boxing")
    ap.add_argument("--clip-start", type=int, default=240)
    ap.add_argument("--clip-frames", type=int, default=72)
    ap.add_argument("--clip-step", type=int, default=4)
    a = ap.parse_args(argv)
    fit = json.load(open(a.fit))
    G.HEAT_PROXY["voxel"] = a.voxel
    G.HEAT_PROXY["faces"] = a.proxy_faces
    metrics = {"input": a.inp, "fit": a.fit}

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.inp)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if not meshes:
        raise RuntimeError("no meshes imported from %s (meshopt? decode first)" % a.inp)
    # 1. meshes back to their bind shape, unparented, transforms applied, old weights dropped
    for m in meshes:
        for md in list(m.modifiers):
            if md.type == "ARMATURE":
                m.modifiers.remove(md)
        mw = m.matrix_world.copy()
        m.parent = None
        m.matrix_world = mw
        m.vertex_groups.clear()
    bpy.ops.object.select_all(action="DESELECT")
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in arms:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.context.scene.objects):  # empties left over from the old node tree
        if o.type == "EMPTY":
            bpy.data.objects.remove(o, do_unlink=True)
    # 2. same turn + floor as the fit (rotation about glTF +Y == Blender +Z)
    import math
    rot = Matrix.Rotation(math.radians(fit["mesh_rot_y_deg"]), 4, "Z")
    for m in meshes:
        m.data.transform(rot)
    zmin = min((v.co.z for m in meshes for v in m.data.vertices))
    for m in meshes:
        m.data.transform(Matrix.Translation((0, 0, -zmin)))
        m.data.update()
    mn = [min(v.co[k] for m in meshes for v in m.data.vertices) for k in range(3)]
    mx = [max(v.co[k] for m in meshes for v in m.data.vertices) for k in range(3)]
    metrics["mesh_bbox_blender"] = [mn, mx]
    if abs(mx[2] - fit["height_m"]) > 0.01:
        raise RuntimeError("mesh height %.3f != fit height %.3f — fit made from a different mesh/orientation"
                           % (mx[2], fit["height_m"]))
    k = 1.0
    if a.height:  # uniform scale of the mesh AND every fitted position (the fit is in the unscaled mesh's metres)
        k = a.height / mx[2]
        for m in meshes:
            m.data.transform(Matrix.Scale(k, 4))
            m.data.update()
        metrics["scaled_to_height_m"] = a.height
        metrics["scale_factor"] = k

    # 3. armature from the fit
    J = {j["name"]: j for j in fit["joints"]}
    kids = {}
    for j in fit["joints"]:
        kids.setdefault(j["parent"], []).append(j["name"])
    MAIN = {"Hips": "Spine", "Spine2": "Neck", "Neck": "Head"}
    for s in ("Left", "Right"):
        MAIN[s + "Hand"] = s + "HandMiddle1"
        MAIN[s + "Foot"] = s + "ToeBase"
    H = fit["height_m"]
    arm_data = bpy.data.armatures.new("Armature")
    rig = bpy.data.objects.new("Armature", arm_data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for j in fit["joints"]:
        b = arm_data.edit_bones.new(j["name"])
        b.head = gl2bl(j["pos"]) * k
        eb[j["name"]] = b
    for j in fit["joints"]:
        n, b = j["name"], eb[j["name"]]
        ch = [c for c in kids.get(n, []) if c in J]
        if n in fit.get("leaf_tail", {}):
            tail = gl2bl(fit["leaf_tail"][n]) * k
        elif MAIN.get(n) in J:
            tail = gl2bl(J[MAIN[n]]["pos"]) * k
        elif len(ch) == 1:
            tail = gl2bl(J[ch[0]]["pos"]) * k
        elif ch:
            tail = sum((gl2bl(J[c]["pos"]) for c in ch), Vector()) * k / len(ch)
        elif n == "Head":
            tail = b.head + Vector((0, 0, 0.1 * H * k))
        else:  # leaf: continue the parent's direction for half its length
            p = J[j["parent"]]["pos"]
            d = b.head - gl2bl(p) * k
            tail = b.head + d * 0.5
        if (tail - b.head).length < 0.005:
            tail = b.head + Vector((0, 0, 0.02))
        b.tail = tail
    for j in fit["joints"]:
        if j["parent"] in eb:
            eb[j["name"]].parent = eb[j["parent"]]
            eb[j["name"]].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm_data.bones:
        b.use_deform = True
    metrics["bones"] = len(arm_data.bones)

    # 4. bone heat (proxy for dense meshes) + nearest-bone fixup
    metrics["unweighted_fixed"] = G.skin_meshes(rig, meshes)
    metrics["heat_proxy"] = G.PROXY_STATS
    for m in meshes:
        if not any(md.type == "ARMATURE" for md in m.modifiers):
            mw = m.matrix_world.copy()
            m.parent = rig
            m.matrix_world = mw
            md = m.modifiers.new("Armature", "ARMATURE")
            md.object = rig
        bpy.ops.object.select_all(action="DESELECT")
        m.select_set(True)
        bpy.context.view_layer.objects.active = m
        metrics.setdefault("continuous_limit_verts", 0)
        metrics["continuous_limit_verts"] += continuous_limit(m, 4)  # before Blender's hard cut (now a no-op)
        bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
        bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

    # 4b. optional deformation test clip (the rig's joints already carry the canonical names transfer_clip maps to)
    if a.donor:
        G.DONOR_TO_DEF = {c: c for c in G.DONOR_TO_DEF}
        name, nframes, npairs = G.transfer_clip(rig, a.donor, a.clip, clip_start=a.clip_start,
                                                clip_frames=a.clip_frames, clip_step=a.clip_step)
        metrics["test_clip"] = {"action": name, "frames": nframes, "bones": npairs, "donor": a.donor}

    # 5. export (skin; animation only when a test clip was baked)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.ops.export_scene.gltf(filepath=a.out, export_format="GLB", use_selection=True,
                              export_skins=True, export_def_bones=False, export_animations=bool(a.donor),
                              export_yup=True)
    metrics["out"] = a.out
    metrics["out_bytes"] = os.path.getsize(a.out)
    if a.metrics_out:
        json.dump(metrics, open(a.metrics_out, "w"), indent=1, default=str)
    print("HEAT_REBIND", json.dumps({k: metrics[k] for k in ("bones", "unweighted_fixed", "out_bytes")}))


if __name__ == "__main__":
    main()
