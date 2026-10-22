#!/usr/bin/env python3
"""
cleanup-batch.py — STAGE 4: CLEANUP (runs inside headless Blender).

For every model file in <indir> (GLB/FBX), per mesh, in order:
  1. weld duplicate verts            (bmesh remove_doubles, --merge-dist)
  2. delete loose verts/edges        (edit-mode delete_loose)
  3. recalculate normals outward     (edit-mode normals_make_consistent)
  4. decimate                        (DECIMATE modifier, --decimate RATIO; 0 skips)
  5. triangulate                      (optional --triangulate)

Exports to <outdir>/<name>.glb with a per-file before/after report
(verts/tris). Armatures, vertex groups and animations pass through untouched.

Usage (headless):
  blender -b --python cleanup-batch.py -- --indir <dir> --outdir <dir>
      [--decimate 0.5] [--merge-dist 0.0001] [--triangulate] [--no-normals]
"""
import argparse
import os
import sys
import traceback

import bmesh
import bpy


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--indir", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--decimate", type=float, default=0.5,
                   help="decimate ratio 0..1 (0 = skip)")
    p.add_argument("--merge-dist", type=float, default=0.0001)
    p.add_argument("--triangulate", action="store_true")
    p.add_argument("--no-normals", action="store_true",
                   help="skip the recalculate-normals step")
    return p.parse_args(argv)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_model(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".glb":
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    else:
        raise ValueError(f"unsupported extension: {ext}")


def mesh_stats(obj):
    me = obj.data
    return len(me.vertices), len(me.polygons)


def clean_mesh(obj, a):
    """obj: mesh object, active and in OBJECT mode on entry."""
    v0, p0 = mesh_stats(obj)

    # 1. weld doubles via bmesh (stable across Blender versions)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=a.merge_dist)
    if a.triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

    # 2+3. loose cleanup + normals need edit mode
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.delete_loose()
    if not a.no_normals:
        bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # 4. decimate (keeps vertex groups / armature binding)
    if a.decimate and a.decimate > 0 and a.decimate < 1:
        mod = obj.modifiers.new("accel-decimate", "DECIMATE")
        mod.ratio = a.decimate
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)

    v1, p1 = mesh_stats(obj)
    return (v0, p0, v1, p1)


def run(a):
    files = sorted(f for f in os.listdir(a.indir)
                   if os.path.splitext(f)[1].lower() in (".glb", ".fbx"))
    if not files:
        print(f"NO FILES in {a.indir}")
        return 1
    n_ok, n_fail = 0, 0
    for fname in files:
        src = os.path.join(a.indir, fname)
        stem = os.path.splitext(fname)[0]
        dest = os.path.join(a.outdir, stem + ".glb")
        try:
            reset_scene()
            import_model(src)
            reports = []
            for obj in [o for o in bpy.data.objects if o.type == "MESH"]:
                v0, p0, v1, p1 = clean_mesh(obj, a)
                reports.append(f"{obj.name}:{v0}v/{p0}p->{v1}v/{p1}p")
            bpy.ops.export_scene.gltf(filepath=dest, export_format="GLB")
            print(f"OK {fname} -> {os.path.basename(dest)} [{' '.join(reports)}]")
            n_ok += 1
        except Exception:
            print(f"FAIL {fname}")
            traceback.print_exc()
            n_fail += 1
    print(f"==> cleanup: {n_ok} ok, {n_fail} failed ({len(files)} files)")
    return 1 if n_fail else 0


def main():
    a = parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    sys.exit(run(a))


main()
