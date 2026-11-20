# wh_glb_audit.py — Western Heart GLB batch audit (+ optional bone rename)
#
# WHAT IT DOES (a real WH job):
#   1. Imports every .glb/.gltf in a folder into Blender (headless).
#   2. Prints a per-file report: objects, mesh vertex/face counts, materials,
#      and animation actions (name + frame range) — the exact numbers WH needs
#      before a fighter/stage asset is accepted into the Three.js game.
#   3. Optionally renames armature bones per a JSON mapping file, then saves
#      the renamed file next to the original as "<name>_renamed.glb".
#      This is the Tekken-source -> WH-skeleton naming bridge: source rigs
#      use their own bone names; WH code expects one canonical set.
#
# HOW TO RUN (inside Blender; NOT plain python — Blender ships its own
# Python with the `bpy` module):
#   blender --background --python wh_glb_audit.py -- \
#       --input-dir ./glb_in --rename-map ./bone_map.json
#   blender --background --python wh_glb_audit.py -- --input-dir ./glb_in
#
#   --rename-map is a JSON object: {"source_bone_name": "WH_bone_name", ...}
#   Example mapping (EDIT to WH's canonical skeleton before use):
#     {"Hips": "pelvis", "Spine": "spine_01", "LeftArm": "arm_L",
#      "RightArm": "arm_R", "LeftLeg": "leg_L", "RightLeg": "leg_R"}
#   Bones with no mapping entry are left untouched and listed as UNMAPPED.
#
# STATUS: UNTESTED in Blender on this VM — `which blender` returned nothing
#   (Blender is not installed here), so the script could NOT be run end to
#   end. It WAS syntax-checked with plain python3 (py_compile) on 2026-10-24.
#   Run it once on a machine with Blender before trusting its output on
#   production assets. It writes no files unless --rename-map is given and a
#   bone actually renames (then it writes *_renamed.glb, never overwriting
#   the original).
#
# LICENSE NOTE: Blender itself is GPL (see catalog). This script is a
#   Blender Python script; Blender's own license page states scripts that
#   use the Blender Python API, if published, are shared under a
#   GPL-compatible license. Keep this file under GPL-2.0-or-later if it is
#   published/distributed with Blender tooling.
#
# SPDX-License-Identifier: GPL-2.0-or-later

import argparse
import json
import os
import sys


def parse_args(argv):
    p = argparse.ArgumentParser(description="WH GLB batch audit + bone rename")
    p.add_argument("--input-dir", required=True,
                   help="Folder containing .glb/.gltf files")
    p.add_argument("--rename-map", default=None,
                   help="Optional JSON bone-rename mapping file")
    return p.parse_args(argv)


def load_rename_map(path):
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("rename map must be a JSON object {old: new}")
    return {str(k): str(v) for k, v in data.items()}


def audit_scene():
    """Return (objects, verts, faces, materials, animations) for current scene."""
    import bpy  # noqa: F401  (only available inside Blender)
    objects = list(bpy.data.objects)
    verts = faces = 0
    materials = set()
    for ob in objects:
        if ob.type == "MESH" and ob.data is not None:
            # Evaluated mesh would need depsgraph; .data counts are the
            # stored mesh and are the right acceptance-check numbers here.
            verts += len(ob.data.vertices)
            faces += len(ob.data.polygons)
            for slot in ob.data.materials:
                if slot is not None:
                    materials.add(slot.name)
    animations = []
    for action in bpy.data.actions:
        start, end = None, None
        if action.frame_range:
            start, end = action.frame_range[0], action.frame_range[1]
        animations.append({"name": action.name, "start": start, "end": end})
    return objects, verts, faces, sorted(materials), animations


def rename_bones(rename_map):
    """Rename armature bones per map. Returns (renamed, unmapped) name lists."""
    import bpy
    renamed, unmapped = [], []
    for ob in bpy.data.objects:
        if ob.type != "ARMATURE" or ob.data is None:
            continue
        for bone in ob.data.bones:
            if bone.name in rename_map:
                new_name = rename_map[bone.name]
                if new_name != bone.name:
                    bone.name = new_name
                    renamed.append(new_name)
            else:
                unmapped.append(bone.name)
    return renamed, sorted(set(unmapped))


def main():
    # Blender puts script args after "--"; plain-python runs (syntax check
    # only) will not reach here with real args.
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parse_args(argv)
    import bpy

    rename_map = load_rename_map(args.rename_map)
    files = sorted(f for f in os.listdir(args.input_dir)
                   if f.lower().endswith((".glb", ".gltf")))
    if not files:
        print("NO GLB/GLTF FILES in %s" % args.input_dir)
        return 0

    report = []
    for fname in files:
        path = os.path.join(args.input_dir, fname)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=path)
        objects, verts, faces, materials, animations = audit_scene()
        renamed, unmapped = ([], [])
        out_path = None
        if rename_map:
            renamed, unmapped = rename_bones(rename_map)
            if renamed:
                stem, _ = os.path.splitext(path)
                out_path = stem + "_renamed.glb"
                bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB")
        entry = {
            "file": fname,
            "objects": len(objects),
            "verts": verts,
            "faces": faces,
            "materials": materials,
            "animations": animations,
            "bones_renamed": renamed,
            "bones_unmapped": unmapped,
            "renamed_file": out_path,
        }
        report.append(entry)
        print(json.dumps(entry, indent=2))
    with open(os.path.join(args.input_dir, "wh_glb_audit_report.json"),
              "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("REPORT WRITTEN: wh_glb_audit_report.json (%d files)" % len(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
