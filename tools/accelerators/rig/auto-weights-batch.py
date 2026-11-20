#!/usr/bin/env python3
"""
auto-weights-batch.py — STAGE 3: RIGGING (runs inside headless Blender).

For every model file in <indir> (GLB/FBX):
  1. import it into a fresh scene
  2. find the armature + mesh objects
  3. parent each unparented mesh to the armature with AUTOMATIC weights
     (Blender bone-heat: bpy.ops.object.parent_set(type='ARMATURE_AUTO'))
  4. export to <outdir>/<name>.glb

This is the fast automatic pass — bone-heat skinning, no GUI. For the full
GameRig pipeline (cage fitting, weight painting, validation) see
tools/auto_rig/. This stage gets a model rigged overnight; artists refine.

Usage (headless):
  blender -b --python auto-weights-batch.py -- --indir <dir> --outdir <dir>
      [--reweight] [--suffix .rigged]

--reweight: redo weights even if the mesh is already parented to an armature.
Writes a per-file report line: vertex groups created per mesh.
"""
import argparse
import os
import sys
import traceback

import bpy


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--indir", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--reweight", action="store_true")
    p.add_argument("--suffix", default="")
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


def auto_weight(indir, outdir, reweight, suffix):
    files = sorted(f for f in os.listdir(indir)
                   if os.path.splitext(f)[1].lower() in (".glb", ".fbx"))
    if not files:
        print(f"NO FILES in {indir}")
        return 1
    n_ok, n_fail, n_skip = 0, 0, 0
    for fname in files:
        src = os.path.join(indir, fname)
        stem = os.path.splitext(fname)[0]
        dest = os.path.join(outdir, stem + suffix + ".glb")
        try:
            reset_scene()
            import_model(src)
            armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
            meshes = [o for o in bpy.data.objects if o.type == "MESH"]
            if not armatures:
                print(f"SKIP {fname}: no armature in file"); n_skip += 1; continue
            if not meshes:
                print(f"SKIP {fname}: no mesh in file"); n_skip += 1; continue
            arm = armatures[0]
            if len(armatures) > 1:
                print(f"WARN {fname}: {len(armatures)} armatures, using '{arm.name}'")
            todo = [m for m in meshes
                    if reweight or not (m.parent_type == "ARMATURE" and m.parent == arm)]
            groups_report = [f"{m.name}:already-parented" for m in meshes if m not in todo]
            if todo:
                for m in todo:  # clear old parenting before re-weighting
                    bpy.ops.object.select_all(action="DESELECT")
                    m.select_set(True)
                    bpy.context.view_layer.objects.active = m
                    bpy.ops.object.parent_clear(type="CLEAR")
                # batch pattern (from tools/auto_rig/backends/blender_heat.py):
                # select armature + meshes, ARMATURE ACTIVE -> automatic weights
                bpy.ops.object.select_all(action="DESELECT")
                arm.select_set(True)
                for m in todo:
                    m.select_set(True)
                bpy.context.view_layer.objects.active = arm
                bpy.ops.object.parent_set(type="ARMATURE_AUTO")
                # fixup: bone heat can leave verts unweighted on disconnected
                # islands; unweighted verts crash the glTF exporter. Assign
                # them to the nearest bone head with weight 1.0.
                bones = [(b.name, arm.data.bones[b.name].head_local)
                         for b in arm.data.bones]
                for m in todo:
                    fixed = 0
                    for v in m.data.vertices:
                        if not v.groups:
                            co = m.matrix_world @ v.co
                            bn, _ = min(bones, key=lambda b: (b[1] - co).length)
                            vg = m.vertex_groups.get(bn) or m.vertex_groups.new(name=bn)
                            vg.add([v.index], 1.0, "REPLACE")
                            fixed += 1
                    n_groups = len(m.vertex_groups)
                    groups_report.append(f"{m.name}:{n_groups}vgroups"
                                         + (f"+{fixed}fixed" if fixed else ""))
            bpy.ops.export_scene.gltf(filepath=dest, export_format="GLB")
            print(f"OK {fname} -> {os.path.basename(dest)} [{' '.join(groups_report)}]")
            n_ok += 1
        except Exception:
            print(f"FAIL {fname}")
            traceback.print_exc()
            n_fail += 1
    print(f"==> rigging: {n_ok} ok, {n_skip} skipped, {n_fail} failed ({len(files)} files)")
    return 1 if n_fail else 0


def main():
    a = parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    sys.exit(auto_weight(a.indir, a.outdir, a.reweight, a.suffix))


main()
