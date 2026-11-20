#!/usr/bin/env python3
"""convert_no_mercy_parts.py — OBJ -> GLB conversion for No Mercy CAW parts.

Runs INSIDE Blender (the operation's production converter):

  xvfb-run -a env -u PYTHONPATH <blender> -b \
      --python customization/tools/convert_no_mercy_parts.py -- <repo_root>

For every mesh_part in customization/parts/no-mercy/CATALOG.json:
  * imports the AKI-export OBJ (positions + UVs; the source has no normals)
  * applies the file's own header scale (`# scale=N` in the OBJ comment):
    glTF coordinates = raw / N, so every part lands in one consistent
    AKI model space (final rig scaling is the bake lane's step)
  * embeds the `.vc` vertex-color sidecar as a COLOR_0 attribute
    (values are N64 0..63 per channel, normalized /63) when its line
    count matches the OBJ vertex count
  * shades flat (use_smooth=False) — the N64 faceted look, and the only
    honest shading for normal-less source geometry
  * exports GLB to the path the catalog promises (entry["glb"])

Writes customization/parts/no-mercy/conversion-report.json and stamps
each catalog entry's conversion.status. Per-file failures are recorded
in the report and never abort the batch.
"""
import json
import os
import re
import sys

import bpy
from mathutils import Matrix


def parse_scale(obj_path):
    with open(obj_path, "r", errors="replace") as f:
        head = f.read(2048)
    m = re.search(r"scale=(\d+(?:\.\d+)?)", head)
    return float(m.group(1)) if m else 1.0


def read_vc(vc_path, nverts):
    if not os.path.exists(vc_path):
        return None
    rows = []
    with open(vc_path, "r", errors="replace") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    rows.append(tuple(float(x) / 63.0 for x in parts[:3]))
                except ValueError:
                    return None
    return rows if len(rows) == nverts else None


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        pass  # orphan cleanup handled by Blender between files; keep simple


def convert_one(repo_root, entry):
    src = os.path.join(repo_root, entry["file"])
    dst = os.path.join(repo_root, entry["glb"])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    scale = parse_scale(src)
    clean_scene()
    bpy.ops.wm.obj_import(filepath=src)
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objs:
        return {"status": "failed", "error": "no mesh imported"}
    obj = objs[0]
    mesh = obj.data
    nverts_in = len(mesh.vertices)
    if scale and scale != 1.0:
        s = 1.0 / scale
        mesh.transform(Matrix.Diagonal((s, s, s, 1.0)))
    vc = read_vc(os.path.splitext(src)[0] + ".vc", nverts_in)
    vc_applied = False
    if vc is not None:
        attr = mesh.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
        for i, rgb in enumerate(vc):
            attr.data[i].color = (rgb[0], rgb[1], rgb[2], 1.0)
        mesh.color_attributes.active_color = attr
        vc_applied = True
    for poly in mesh.polygons:
        poly.use_smooth = False
    mesh.update()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=dst,
        export_format="GLB",
        export_apply=True,
        export_yup=True,
    )
    return {
        "status": "converted",
        "scale_used": scale,
        "verts": nverts_in,
        "faces": len(mesh.polygons),
        "vertex_colors": vc_applied,
        "glb_bytes": os.path.getsize(dst),
    }


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    repo_root = os.path.abspath(argv[0]) if argv else os.getcwd()
    cat_path = os.path.join(repo_root, "customization", "parts", "no-mercy", "CATALOG.json")
    catalog = json.load(open(cat_path))
    report = {"tool": "customization/tools/convert_no_mercy_parts.py", "results": {}}
    ok = fail = 0
    for entry in catalog["parts"]:
        if entry.get("part_class") != "mesh_part":
            continue
        try:
            res = convert_one(repo_root, entry)
        except Exception as e:  # record and keep going — batch discipline
            res = {"status": "failed", "error": f"{type(e).__name__}: {e}"}
        report["results"][entry["id"]] = res
        entry["conversion"]["status"] = res["status"]
        if res["status"] == "converted":
            ok += 1
        else:
            fail += 1
    report["summary"] = {"converted": ok, "failed": fail}
    with open(os.path.join(repo_root, "customization", "parts", "no-mercy", "conversion-report.json"), "w") as f:
        json.dump(report, f, indent=1)
        f.write("\n")
    with open(cat_path, "w") as f:
        json.dump(catalog, f, indent=1)
        f.write("\n")
    print(f"[convert_no_mercy_parts] converted={ok} failed={fail}")


if __name__ == "__main__":
    main()
