#!/usr/bin/env python3
"""tools/auto_rig/backends/blender_heat.py — CPU auto-rig via Blender bone heat.

Expects a NORMALIZED mesh (see normalize.py): feet at y=0, height matched to
the skeleton, Y-up glTF space. This script only rigs:

  1. Import the normalized GLB into Blender.
  2. Build the canonical WH skeleton from skeleton_template.json
     (Y-up, facing -Z), rotated to --mesh-facing, converted to Blender Z-up.
  3. Parent meshes to the armature with automatic weights (heat diffusion =
     Baran & Popovic 2007 skinning, battle-tested inside Blender).
  4. Export GLB with the skin.

Run:
    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup \
        --python blender_heat.py -- --in NORM.glb --out RIGGED.glb \
        [--mesh-facing -Z]
"""

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# rotation about Y mapping template facing (-Z) to the mesh facing
FACING_YAW = {"-Z": 0.0, "+Z": math.pi, "+X": -math.pi / 2, "-X": math.pi / 2}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--mesh-facing", default="-Z", choices=list(FACING_YAW))
    ap.add_argument("--max-influences", type=int, default=4,
                    help="cap skinning influences per vertex (WH standard: 4, "
                         "glTF vec4 + UE4; 0 = no cap)")
    ap.add_argument("--template",
                    default=os.path.join(HERE, "skeleton_template.json"))
    return ap.parse_args(argv)


def yaw(p, ang):
    x, y, z = p
    c, s = math.cos(ang), math.sin(ang)
    return (x * c + z * s, y, -x * s + z * c)


def gltf_to_blender(p):
    """Y-up glTF -> Z-up Blender: (x, y, z) -> (x, -z, y)."""
    x, y, z = p
    return (x, -z, y)


def main():
    import bpy  # noqa: E402

    a = parse_args()
    tpl = json.load(open(a.template))
    yaw_ang = FACING_YAW[a.mesh_facing]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.inp)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("no meshes imported from %s" % a.inp)

    # build armature from the rotated, converted template
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm = bpy.context.object
    arm.name = "WH_Skeleton"
    eb = arm.data.edit_bones
    eb.remove(eb[0])
    created = {}
    for j in tpl["joints"]:
        head = gltf_to_blender(yaw(j["head"], yaw_ang))
        tail = gltf_to_blender(yaw(j["tail"], yaw_ang))
        b = eb.new(j["name"])
        b.head, b.tail = head, tail
        created[j["name"]] = b
    for j in tpl["joints"]:
        if j.get("parent"):
            created[j["name"]].parent = created[j["parent"]]
    bpy.ops.object.mode_set(mode="OBJECT")

    # parent + heat weights
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")

    # weight conventions: island fixup (was inline here; moved verbatim into
    # weight_conventions.py) + normalize-all-verts. Same defaults as before.
    sys.path.insert(0, HERE)
    import weight_conventions
    weight_conventions.apply(meshes, arm, max_influences=a.max_influences)
    bpy.ops.object.select_all(action="DESELECT")

    bpy.ops.export_scene.gltf(
        filepath=a.out,
        export_format="GLB",
        export_skins=True,
        export_animations=False,
        export_yup=True,
    )
    print("AUTO_RIG_OK", a.out)


if __name__ == "__main__":
    main()
