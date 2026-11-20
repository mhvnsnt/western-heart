#!/usr/bin/env python3
"""
retarget_tekken.py — retarget Tekken 7/8 skeletal animation onto Western Heart
rigs, headless (blender -b --python).

KEY FACT (research finding): every Tekken character shares ONE base skeleton
(SKT_CH_base_Skeleton in T7; T8's naming is near-identical). Retargeting is
1:1 bone-name matching through tools/retarget/tekken-bonemap.json — no
Cascadeur, no per-character presets.

Method: studio-standard "rest-relative delta" retarget (same as
tools/anim-retarget/retarget_blender.py). Per mapped bone, per frame:
    T_pose_world = T_rest_world @ S_rest_world^-1 @ S_pose_world
so the target reproduces the source bone's deformation relative to its own
rest pose. Root translation is scaled by the hip-height ratio.

Source: FBX/BVH/GLB carrying a T7-skeleton animation (e.g. TKMovesets
BlenderTekkenAnimationImporter output, UModel .psk/.fbx exports).
Target: a WH-rigged GLB (Mixamo49 game models like pantera.glb), or
  --target-canonical to procedurally build the lab WH-Canonical-22 rig.

Single clip:
  blender -b --python tools/retarget/retarget_tekken.py -- \\
      --source anims/king_punch.fbx \\
      --target game/assets/models/pantera.glb \\
      --out    game/assets/models/pantera@Punch.glb \\
      --map tekken7_to_mixamo49 --in-place

Overnight batch (no GUI):
  blender -b --python tools/retarget/retarget_tekken.py -- \\
      --batch tools/retarget/batches/king.json

Batch manifest: {"clips": [{"source": ..., "target": ..., "out": ...,
"clip": "Punch", "map": "tekken7_to_mixamo49", "in_place": true}], "defaults": {...}}
Each clip also writes <out>.report.json with mapped/dropped bone counts.
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BONEMAP = os.path.join(HERE, "tekken-bonemap.json")


def _find_canonical():
    cands = [
        # repo layout: tools/retarget/*.py -> <repo>/lab/skeleton/...
        os.path.abspath(os.path.join(HERE, "..", "..", "lab", "skeleton",
                                     "canonical_skeleton.json")),
        # dev checkout next to the fix2 clones
        os.path.expanduser("~/workspace/fix2/western-heart/lab/skeleton/"
                           "canonical_skeleton.json"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit("canonical_skeleton.json not found; tried: "
                     + ", ".join(cands))


CANONICAL_JSON = _find_canonical()

# T7 export variants seen in the wild (Base/BASE, Head/HEAD)
T7_ALIASES = {"BASE": "Base", "Head": "Head", "HEAD": "Head"}


# ---------------------------------------------------------------- args

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", help="FBX/BVH/GLB with the T7-skeleton animation")
    p.add_argument("--target", help="WH-rigged GLB (the mesh + skeleton)")
    p.add_argument("--target-canonical", action="store_true",
                   help="build the lab WH-Canonical-22 rig instead of --target")
    p.add_argument("--out", help="output animated GLB")
    p.add_argument("--bonemap", default=DEFAULT_BONEMAP)
    p.add_argument("--map", default="tekken7_to_mixamo49",
                   choices=["tekken7_to_wh_canonical", "tekken7_to_mixamo49"])
    p.add_argument("--clip-name", default=None)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--in-place", action="store_true",
                   help="zero Hips translation (in-place clip)")
    p.add_argument("--batch", help="batch manifest JSON for overnight runs")
    return p.parse_args(argv)


# ---------------------------------------------------------------- helpers

def deselect_all():
    bpy.ops.object.select_all(action="DESELECT")


def clean_scene(fps):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.render.fps = fps


def _new_armatures(before):
    after = set(bpy.context.scene.objects)
    new = [o for o in after - before if o.type == "ARMATURE"]
    if not new:
        raise SystemExit("no armature found in imported file")
    new.sort(key=lambda a: len(a.data.bones), reverse=True)
    return new[0]


def import_source(path):
    before = set(bpy.context.scene.objects)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".bvh":
        bpy.ops.import_anim.bvh(filepath=path)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        raise SystemExit(f"unsupported source format: {ext}")
    # Take the largest *newly imported* armature (the scene may already
    # hold other armatures, e.g. a previously imported source).
    return _new_armatures(before)


def import_target_glb(path):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return _new_armatures(before)


def build_canonical_rig(bonemap):
    """Procedurally build the WH-Canonical-22 armature.

    Hierarchy (parent links) comes from the authoritative lab canonical
    skeleton (lab/skeleton/canonical_skeleton.json). Rest positions come
    from the T7 base skeleton (tekken_skeleton_base.json) mapped through
    the bone map, converted UE Z-up -> Blender Z-up (x,y,z) -> (y,x,z).
    Proportions follow the T7 reference character; the rest-relative
    retarget makes exact proportions non-critical.
    """
    skel_path = os.path.join(HERE, "tekken_skeleton_base.json")
    with open(skel_path) as f:
        t7 = json.load(f)
    t7_pos = {b["name"]: b["rest_pos"] for b in t7["bones"]}
    with open(CANONICAL_JSON) as f:
        canon = json.load(f)["bones"]
    inv = {v: k for k, v in bonemap.items()}  # WH -> T7

    def conv(p):
        return (p[1], p[0], p[2])

    bpy.ops.object.armature_add(enter_editmode=True)
    arm_obj = bpy.context.object
    arm_obj.name = "WH-Canonical-22"
    adata = arm_obj.data
    adata.name = "WH-Canonical-22"
    adata.edit_bones.remove(adata.edit_bones[0])
    eb = {}

    def emit(wn):
        if wn in eb:
            return
        spec = next(b for b in canon if b["name"] == wn)
        if spec["parent"]:
            emit(spec["parent"])
        t7n = inv.get(wn)
        b = adata.edit_bones.new(wn)
        if t7n and t7n in t7_pos:
            head = conv(t7_pos[t7n])
        else:
            # fall back: offset from parent
            ph = eb[spec["parent"]].head if spec["parent"] in eb else (0, 0, 1)
            head = (ph[0], ph[1], ph[2] - 0.1)
        # tail: position of the first mapped child, else -Z nub
        tail = None
        for c in canon:
            if c["parent"] == wn:
                ct7 = inv.get(c["name"])
                if ct7 and ct7 in t7_pos:
                    tail = conv(t7_pos[ct7])
                    break
        if tail is None or math.dist(head, tail) < 1e-4:
            tail = (head[0], head[1], head[2] - 0.08)
        b.head = head
        b.tail = tail
        if spec["parent"] and spec["parent"] in eb:
            b.parent = eb[spec["parent"]]
            b.use_connect = False
        eb[wn] = b

    for spec in canon:
        emit(spec["name"])
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def rest_world(arm, bone_name):
    b = arm.data.bones[bone_name]
    return arm.matrix_world @ b.matrix_local


def hip_height(arm, names=("Hips", "Hip", "mixamorig:Hips")):
    for n in names:
        b = arm.data.bones.get(n)
        if b is not None:
            return (arm.matrix_world @ b.head_local).z
    return 1.0


def normalize_t7(name):
    return T7_ALIASES.get(name, name)


# ---------------------------------------------------------------- one clip

def retarget_one(source, target, out, bonemap_path, map_name, clip_name,
                 fps, in_place, target_canonical=False):
    with open(bonemap_path) as f:
        bm = json.load(f)
    bone_map = bm[map_name]

    clean_scene(fps)
    scene = bpy.context.scene

    src_arm = import_source(source)
    tgt_arm = build_canonical_rig(bone_map) if target_canonical \
        else import_target_glb(target)

    for arm in (src_arm, tgt_arm):
        arm.location = (0, 0, 0)
        arm.rotation_euler = (0, 0, 0)
        arm.scale = (1, 1, 1)
    bpy.context.view_layer.update()

    src_bones = {b.name: b for b in src_arm.data.bones}
    tgt_bones = {b.name: b for b in tgt_arm.data.bones}

    # Precompute rest data for the local-space retarget.
    # For each mapped pair we need source/target rest + parent rest.
    src_par = {}
    for s_name in src_bones:
        b = src_arm.data.bones[s_name]
        src_par[s_name] = b.parent.name if b.parent else None
    tgt_par = {}
    for t_pb in tgt_arm.pose.bones:
        tgt_par[t_pb.name] = t_pb.parent.name if t_pb.parent else None

    pairs = []  # (s_name, t_name, S_rest, SP_rest, T_rest, TP_rest, s_par, t_par)
    unmapped_src, missing_tgt = [], []
    ident = Matrix.Identity(4)
    for s_name in src_bones:
        t_name = bone_map.get(normalize_t7(s_name), bone_map.get(s_name))
        if not t_name:
            unmapped_src.append(s_name)
            continue
        if t_name not in tgt_bones:
            missing_tgt.append((s_name, t_name))
            continue
        S_rest = rest_world(src_arm, s_name)
        s_par = src_par[s_name]
        SP_rest = rest_world(src_arm, s_par) if s_par else ident
        T_rest = rest_world(tgt_arm, t_name)
        t_par = tgt_par[t_name]
        TP_rest = rest_world(tgt_arm, t_par) if t_par else ident
        pairs.append((s_name, t_name, S_rest, SP_rest, T_rest, TP_rest,
                      s_par, t_par))
    print(f"mapped {len(pairs)} bones; dropped {len(unmapped_src)} source "
          f"helpers; {len(missing_tgt)} map targets missing on target rig")

    # Target-parent-first order for the pose solve.
    mapped_t = {t for _, t, *_ in pairs}
    ordered, done = [], set()

    def emit(t_name):
        if t_name in done:
            return
        p = tgt_par.get(t_name)
        if p and p in mapped_t:
            emit(p)
        done.add(t_name)
        ordered.append(t_name)

    for _, t_name, *_ in pairs:
        emit(t_name)
    by_t = {p[1]: p for p in pairs}

    src_ad = src_arm.animation_data
    src_action = src_ad.action if src_ad else None
    if src_action is None:
        raise SystemExit("source armature has no action — nothing to retarget")
    f_start, f_end = [int(x) for x in src_action.frame_range]
    nframes = f_end - f_start + 1
    print(f"source frames {f_start}..{f_end} @ {fps}fps")

    root_scale = hip_height(tgt_arm) / max(hip_height(src_arm), 1e-6)
    print(f"root motion scale: {root_scale:.3f}")

    deselect_all()
    tgt_arm.select_set(True)
    bpy.context.view_layer.objects.active = tgt_arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in tgt_arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    tgt_action = bpy.data.actions.new(
        name=clip_name or os.path.splitext(os.path.basename(source))[0])
    tgt_arm.animation_data_create()
    tgt_arm.animation_data.action = tgt_action

    for frame in range(f_start, f_end + 1):
        scene.frame_set(frame)
        # Read the source pose from the evaluated depsgraph (robust against
        # stale pose reads on the first frame after mode changes).
        depsgraph = bpy.context.evaluated_depsgraph_get()
        depsgraph.update()
        src_eval = depsgraph.objects.get(src_arm.name)
        # Local-space rest-relative retarget (parent-relative, so unanimated
        # children stay locally static even when the parent moves):
        #   delta   = (SP_rest^-1 @ S_rest)^-1 @ (SP_pose^-1 @ S_pose)
        #   T_pose  = TP_pose @ (TP_rest^-1 @ T_rest) @ delta
        # Process target-parents first so TP_pose is available.
        M_of = {}
        for t_name in ordered:
            (s_name, _, S_rest, SP_rest, T_rest, TP_rest, s_par,
             t_par) = by_t[t_name]
            s_pb = src_eval.pose.bones[s_name]
            S_pose = s_pb.matrix
            SP_pose = (src_eval.pose.bones[s_par].matrix if s_par
                       else ident)
            delta = ((SP_rest.inverted() @ S_rest).inverted()
                     @ (SP_pose.inverted() @ S_pose))
            TP_pose = M_of.get(t_par, TP_rest)
            M = TP_pose @ (TP_rest.inverted() @ T_rest) @ delta
            loc, rot, scl = M.decompose()
            if t_name in ("Hips", "Root"):
                if in_place:
                    # keep rotation, pin translation to bind pose
                    bind = T_rest.decompose()[0]
                    M = (Matrix.Translation(bind) @ rot.to_matrix().to_4x4()
                         @ Matrix.Diagonal(scl).to_4x4())
                else:
                    # scale root translation by hip-height ratio
                    M = (Matrix.Translation(loc * root_scale)
                         @ rot.to_matrix().to_4x4()
                         @ Matrix.Diagonal(scl).to_4x4())
            M_of[t_name] = M
        # Armature-space -> parent-relative matrix_basis, then key.
        # (PoseBone.matrix is read-only; assigning it is undefined behavior.
        #  Verified composition: pb.matrix == parent.matrix
        #      @ parent.bone.matrix_local^-1 @ pb.bone.matrix_local
        #      @ pb.matrix_basis.)
        for t_name in ordered:
            t_pb = tgt_arm.pose.bones[t_name]
            M = M_of[t_name]
            par = t_pb.parent
            if par is None:
                basis = t_pb.bone.matrix_local.inverted() @ M
            else:
                Mpar = M_of.get(par.name, par.matrix)
                basis = (Mpar @ par.bone.matrix_local.inverted()
                         @ t_pb.bone.matrix_local).inverted() @ M
            t_pb.matrix_basis = basis
            t_pb.keyframe_insert(data_path="location", frame=frame)
            t_pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            t_pb.keyframe_insert(data_path="scale", frame=frame)
    bpy.ops.object.mode_set(mode="OBJECT")

    def is_target_side(o):
        while o is not None:
            if o == tgt_arm:
                return True
            o = o.parent
        return False

    deselect_all()
    for o in list(bpy.context.scene.objects):
        if not is_target_side(o):
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()

    # Purge the source action (and any other orphans): only the retargeted
    # action may ship, otherwise reimport assigns the wrong action.
    for act in list(bpy.data.actions):
        if act != tgt_action:
            bpy.data.actions.remove(act)
    for _ in range(3):  # flush orphan datablocks
        bpy.ops.outliner.orphans_purge(do_recursive=True)

    deselect_all()
    for o in bpy.context.scene.objects:
        keep = (o == tgt_arm) or (o.parent is not None and o.parent == tgt_arm)
        o.select_set(bool(keep))
    tgt_arm.select_set(True)
    bpy.context.view_layer.objects.active = tgt_arm
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_frame_range=True,
        export_anim_single_armature=True,
        export_skins=True,
        export_morph=False,
    )
    report = {
        "source": source, "target": target, "out": out,
        "map": map_name, "clip": tgt_action.name,
        "frames": [f_start, f_end], "nframes": nframes, "fps": fps,
        "mapped_bones": len(pairs),
        "mapped": sorted(f"{p[0]}->{p[1]}" for p in pairs),
        "dropped_source_bones": sorted(unmapped_src),
        "map_targets_missing_on_target": sorted(f"{s}->{t}" for s, t in missing_tgt),
        "root_motion_scale": root_scale,
        "in_place": in_place,
    }
    with open(out + ".report.json", "w") as f:
        json.dump(report, f, indent=1)
    print(f"WROTE {out} ({nframes} frames, {len(pairs)} bones)")


# ---------------------------------------------------------------- batch

def run_batch(manifest_path):
    with open(manifest_path) as f:
        man = json.load(f)
    defaults = man.get("defaults", {})
    clips = man.get("clips", [])
    print(f"batch: {len(clips)} clips from {manifest_path}")
    results = []
    for i, c in enumerate(clips):
        print(f"\n=== clip {i + 1}/{len(clips)}: {c.get('clip', c.get('source'))} ===")
        kw = dict(defaults)
        kw.update(c)
        try:
            retarget_one(
                source=kw["source"],
                target=kw.get("target"),
                out=kw["out"],
                bonemap_path=kw.get("bonemap", DEFAULT_BONEMAP),
                map_name=kw.get("map", "tekken7_to_mixamo49"),
                clip_name=kw.get("clip"),
                fps=int(kw.get("fps", 30)),
                in_place=bool(kw.get("in_place", False)),
                target_canonical=bool(kw.get("target_canonical", False)),
            )
            results.append({"clip": kw.get("clip"), "ok": True, "out": kw["out"]})
        except SystemExit as e:
            print(f"FAILED: {e}")
            results.append({"clip": kw.get("clip"), "ok": False, "error": str(e)})
        except Exception as e:  # noqa: BLE001 — batch must survive one bad clip
            print(f"FAILED: {type(e).__name__}: {e}")
            results.append({"clip": kw.get("clip"), "ok": False,
                            "error": f"{type(e).__name__}: {e}"})
    ok = sum(1 for r in results if r["ok"])
    print(f"\nbatch done: {ok}/{len(clips)} ok")
    summary_path = os.path.splitext(manifest_path)[0] + ".summary.json"
    with open(summary_path, "w") as f:
        json.dump({"manifest": manifest_path, "ok": ok,
                   "total": len(clips), "results": results}, f, indent=1)
    print(f"summary: {summary_path}")


def main():
    args = parse_args()
    if args.batch:
        run_batch(args.batch)
        return
    if not args.source or not args.out:
        raise SystemExit("--source and --out required (or --batch)")
    if not args.target and not args.target_canonical:
        raise SystemExit("--target or --target-canonical required")
    retarget_one(args.source, args.target, args.out, args.bonemap, args.map,
                 args.clip_name, args.fps, args.in_place,
                 target_canonical=args.target_canonical)


if __name__ == "__main__":
    main()
