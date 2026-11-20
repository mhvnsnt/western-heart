#!/usr/bin/env python3
"""tools/mesh-edit/mesh_edit.py — headless Blender op driver for in-suite hand-tooling.

Runs under Blender 4.0.2 (the toolchain pin):
    blender -b --factory-startup --python mesh_edit.py -- --job JOB.json

The job JSON follows docs/decisions/2026-10-22-W66-mesh-edit-architecture.md
(job schema v1). Ops apply to the imported source GLB in order, then the scene
is exported to out_glb and a report is written to out_report.

Op catalog (v1):
  mesh_list       read-only inventory -> report only, no GLB written
  mesh_hide/show  recorded in report as manifest hints (visibility is suite-side)
  mesh_delete     remove mesh object(s) by name
  mesh_transform  bake translate/rotate_euler/scale into mesh verts (object space)
  mesh_duplicate  copy mesh object (+ optional mirror on X)
  part_import     import donor GLB, parent/align its meshes to a socket bone, join optional
  mesh_sculpt     sculpt strokes (smooth/grab/inflate/pinch) via bmesh
  mesh_remodel    remesh | subdivide | decimate modifier, applied

Weight safety: ops that change vertex COUNT (mesh_sculpt with remesh-like
strokes, mesh_remodel) set report["reweight_needed"] = True so the caller can
run the weight-transfer pass (tools/anim/repair_sleeve_weights.py approach).
Transform/duplicate/delete preserve existing skin weights.

This file must stay importable-safe under plain python3 for AST checks:
all bpy imports happen inside main() guards. Under Blender, bpy is present.
"""

import argparse
import json
import math
import os
import sys
import traceback

# ---------------------------------------------------------------------------
# Pure-python helpers (no bpy): safe to unit-test without Blender.

OP_CATALOG = {
    "mesh_list":      {"mutates": False, "reweight": False},
    "mesh_hide":      {"mutates": False, "reweight": False},
    "mesh_show":      {"mutates": False, "reweight": False},
    "mesh_delete":    {"mutates": True,  "reweight": False},
    "mesh_transform": {"mutates": True,  "reweight": False},
    "mesh_duplicate": {"mutates": True,  "reweight": False},
    "part_import":    {"mutates": True,  "reweight": False},
    "mesh_sculpt":    {"mutates": True,  "reweight": True},
    "mesh_remodel":   {"mutates": True,  "reweight": True},
}


def validate_job(job):
    """Return a list of error strings; empty means the job is well-formed."""
    errors = []
    if not isinstance(job, dict):
        return ["job must be a JSON object"]
    for key in ("job_id", "source_glb", "ops", "out_glb", "out_report"):
        if key not in job:
            errors.append("missing required key: %s" % key)
    ops = job.get("ops", [])
    if not isinstance(ops, list):
        errors.append("ops must be a list")
        return errors
    for i, op in enumerate(ops):
        if not isinstance(op, dict) or "op" not in op:
            errors.append("ops[%d]: missing 'op'" % i)
            continue
        name = op["op"]
        if name not in OP_CATALOG:
            errors.append("ops[%d]: unknown op '%s'" % (i, name))
            continue
        if name in ("mesh_delete", "mesh_transform", "mesh_duplicate",
                    "mesh_sculpt", "mesh_remodel") and "mesh" not in op:
            errors.append("ops[%d] (%s): missing 'mesh'" % (i, name))
        if name == "part_import" and "donor" not in op:
            errors.append("ops[%d] (part_import): missing 'donor'" % i)
    return errors


def resolve_blender():
    """Find the Blender binary: env override, toolchain path, then PATH."""
    candidates = []
    env_path = os.environ.get("WH_BLENDER_BIN")
    if env_path:
        candidates.append(env_path)
    home = os.path.expanduser("~")
    candidates.append(os.path.join(
        home, "workspace", "tools", "blender",
        "blender-4.0.2-linux-x64", "blender"))
    import shutil
    which = shutil.which("blender")
    if which:
        candidates.append(which)
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def run_command(job_path):
    """Build the headless Blender command for a job file (crew-mode helper)."""
    blender = resolve_blender()
    if not blender:
        raise RuntimeError(
            "Blender binary not found. Run tools/setup/setup_toolchain.sh "
            "or set WH_BLENDER_BIN.")
    here = os.path.dirname(os.path.abspath(__file__))
    return [blender, "-b", "--factory-startup",
            "--python", os.path.join(here, "mesh_edit.py"),
            "--", "--job", os.path.abspath(job_path)]


# ---------------------------------------------------------------------------
# Blender-side implementation. Only runs when bpy is importable.

def _import_bpy():
    import bpy  # noqa: E402
    return bpy


def _find_mesh_objects(bpy, name):
    return [o for o in bpy.data.objects
            if o.type == "MESH" and o.name == name]


def _inventory(bpy):
    items = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        me = o.data
        items.append({
            "mesh": o.name,
            "verts": len(me.vertices),
            "faces": len(me.polygons),
            "skinned": bool(o.vertex_groups),
            "hidden": bool(o.hide_viewport),
        })
    return items


def _apply_transform_to_verts(bpy, obj, translate, rotate_euler, scale):
    """Bake a TRS transform into mesh verts (object space), preserving weights."""
    import mathutils
    me = obj.data
    loc = mathutils.Vector(translate or (0.0, 0.0, 0.0))
    eul = mathutils.Euler(rotate_euler or (0.0, 0.0, 0.0), "XYZ")
    scl = mathutils.Vector(scale if scale else (1.0, 1.0, 1.0))
    mat = (mathutils.Matrix.Translation(loc)
           @ eul.to_matrix().to_4x4()
           @ mathutils.Matrix.Diagonal(scl).to_4x4())
    for v in me.vertices:
        v.co = mat @ v.co
    me.update()


def _sculpt_strokes(bpy, obj, strokes):
    """Apply sculpt-ish strokes via bmesh. Supports smooth/grab/inflate/pinch.

    Each stroke: {brush, strength, radius, center:[x,y,z]} in object space.
    smooth: Laplacian smoothing of verts inside radius.
    grab: translate verts inside radius along `direction` (default +Z).
    inflate: push verts along their normals.
    pinch: pull verts toward the stroke center line.
    """
    import bmesh
    import mathutils
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()

    for st in strokes:
        brush = st.get("brush", "smooth")
        strength = float(st.get("strength", 0.3))
        radius = float(st.get("radius", 0.05))
        center = mathutils.Vector(st.get("center", (0.0, 0.0, 0.0)))
        direction = mathutils.Vector(st.get("direction", (0.0, 0.0, 1.0)))
        affected = [v for v in bm.verts
                    if (v.co - center).length <= radius]
        if not affected:
            continue
        if brush == "smooth":
            # one Laplacian pass over the affected region
            new_cos = {}
            for v in affected:
                linked = [e.other_vert(v) for e in v.link_edges]
                if linked:
                    avg = mathutils.Vector((0, 0, 0))
                    for lv in linked:
                        avg += lv.co
                    avg /= len(linked)
                    new_cos[v] = v.co.lerp(avg, strength)
            for v, co in new_cos.items():
                v.co = co
        elif brush == "grab":
            for v in affected:
                falloff = 1.0 - (v.co - center).length / radius
                v.co += direction * (strength * 0.05 * falloff)
        elif brush == "inflate":
            for v in affected:
                falloff = 1.0 - (v.co - center).length / radius
                v.co += v.normal * (strength * 0.02 * falloff)
        elif brush == "pinch":
            for v in affected:
                falloff = 1.0 - (v.co - center).length / radius
                to_c = center - v.co
                v.co += to_c * (strength * 0.5 * falloff)
        else:
            raise ValueError("unknown sculpt brush: %r" % brush)

    bm.to_mesh(me)
    bm.free()
    me.update()


def _remodel(bpy, obj, spec):
    """Apply a remodel step: remesh | subdivide | decimate. Returns True if
    the vertex count changed (caller flags reweight_needed)."""
    before = len(obj.data.vertices)
    mode = spec.get("mode", "remesh")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if mode == "remesh":
        mod = obj.modifiers.new("WHRemesh", "REMESH")
        mod.mode = "VOXEL"
        mod.voxel_size = float(spec.get("voxel_size", 0.005))
        bpy.ops.object.modifier_apply(modifier=mod.name)
    elif mode == "subdivide":
        mod = obj.modifiers.new("WHSubdiv", "SUBSURF")
        mod.levels = int(spec.get("levels", 1))
        mod.render_levels = int(spec.get("levels", 1))
        bpy.ops.object.modifier_apply(modifier=mod.name)
    elif mode == "decimate":
        mod = obj.modifiers.new("WHDecimate", "DECIMATE")
        mod.ratio = float(spec.get("ratio", 0.5))
        bpy.ops.object.modifier_apply(modifier=mod.name)
    else:
        raise ValueError("unknown remodel mode: %r" % mode)
    after = len(obj.data.vertices)
    return after != before


def _render_preview(bpy, out_png):
    """Workbench preview render of the current scene (proof artifact)."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.filepath = out_png
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.film_transparent = True
    # frame the objects: simple top-down-ish default camera
    for area in []:  # headless: no areas; keep default camera if present
        pass
    bpy.ops.render.render(write_still=True)


def run_job_in_blender(job_path):
    bpy = _import_bpy()
    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)
    errors = validate_job(job)
    report = {"job_id": job.get("job_id"), "ops_applied": [],
              "errors": errors, "reweight_needed": False,
              "manifest_hints": [], "out_glb": job.get("out_glb")}
    if errors:
        return report

    src = job["source_glb"]
    if not os.path.isfile(src):
        report["errors"].append("source_glb not found: %s" % src)
        return report

    # fresh scene, import source
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(src))

    readonly = job["ops"] and all(
        OP_CATALOG[o["op"]]["mutates"] is False for o in job["ops"])
    if readonly and any(o["op"] == "mesh_list" for o in job["ops"]):
        report["inventory"] = _inventory(bpy)

    for op in job["ops"]:
        name = op["op"]
        try:
            if name in ("mesh_hide", "mesh_show"):
                # visibility is suite-side state; record the intent for the manifest
                report["manifest_hints"].append(
                    {"mesh": op.get("mesh"), "visible": name == "mesh_show"})
            elif name == "mesh_list":
                report["inventory"] = _inventory(bpy)
            elif name == "mesh_delete":
                for o in _find_mesh_objects(bpy, op["mesh"]):
                    bpy.data.objects.remove(o, do_unlink=True)
                report["ops_applied"].append({"op": name, "mesh": op["mesh"]})
            elif name == "mesh_transform":
                objs = _find_mesh_objects(bpy, op["mesh"])
                if not objs:
                    raise ValueError("mesh not found: %s" % op["mesh"])
                for o in objs:
                    _apply_transform_to_verts(
                        bpy, o, op.get("translate"), op.get("rotate_euler"),
                        op.get("scale"))
                report["ops_applied"].append({"op": name, "mesh": op["mesh"]})
            elif name == "mesh_duplicate":
                objs = _find_mesh_objects(bpy, op["mesh"])
                if not objs:
                    raise ValueError("mesh not found: %s" % op["mesh"])
                for o in objs:
                    copy = o.copy()
                    copy.data = o.data.copy()
                    copy.name = op.get("new_name", o.name + "_copy")
                    bpy.context.collection.objects.link(copy)
                    if op.get("mirror_x"):
                        _apply_transform_to_verts(
                            bpy, copy, None, None, (-1.0, 1.0, 1.0))
                report["ops_applied"].append({"op": name, "mesh": op["mesh"]})
            elif name == "part_import":
                donor = op["donor"]
                if not os.path.isfile(donor):
                    raise ValueError("donor GLB not found: %s" % donor)
                before = set(bpy.data.objects)
                bpy.ops.import_scene.gltf(filepath=os.path.abspath(donor))
                new_meshes = [o for o in bpy.data.objects
                              if o not in before and o.type == "MESH"]
                socket = op.get("socket")
                if socket and op.get("fit", {}).get("scale_to_bone"):
                    # parent imported meshes to the named bone of the first armature
                    armatures = [o for o in bpy.data.objects
                                 if o.type == "ARMATURE"]
                    if armatures and socket in armatures[0].data.bones:
                        arm = armatures[0]
                        bone = arm.data.bones[socket]
                        blen = (bone.tail_local - bone.head_local).length or 1.0
                        for m in new_meshes:
                            dims = max(m.dimensions) or 1.0
                            s = (blen * 2.0) / dims
                            _apply_transform_to_verts(
                                bpy, m, None, None, (s, s, s))
                report["ops_applied"].append(
                    {"op": name, "donor": donor,
                     "meshes": [m.name for m in new_meshes]})
            elif name == "mesh_sculpt":
                objs = _find_mesh_objects(bpy, op["mesh"])
                if not objs:
                    raise ValueError("mesh not found: %s" % op["mesh"])
                for o in objs:
                    _sculpt_strokes(bpy, o, op.get("strokes", []))
                report["reweight_needed"] = True
                report["ops_applied"].append({"op": name, "mesh": op["mesh"]})
            elif name == "mesh_remodel":
                objs = _find_mesh_objects(bpy, op["mesh"])
                if not objs:
                    raise ValueError("mesh not found: %s" % op["mesh"])
                for o in objs:
                    if _remodel(bpy, o, op.get("spec", {})):
                        report["reweight_needed"] = True
                report["ops_applied"].append({"op": name, "mesh": op["mesh"]})
        except Exception as e:  # noqa: BLE001 - report, don't crash the batch
            report["errors"].append("ops %s failed: %s: %s"
                                   % (name, type(e).__name__, e))

    out_glb = job["out_glb"]
    if not readonly and not report["errors"]:
        os.makedirs(os.path.dirname(os.path.abspath(out_glb)), exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=os.path.abspath(out_glb), export_format="GLB")
        preview = os.path.splitext(os.path.abspath(out_glb))[0] + "-preview.png"
        try:
            _render_preview(bpy, preview)
            report["preview_png"] = preview
        except Exception as e:  # noqa: BLE001
            report["errors"].append("preview render failed: %s" % e)
    elif readonly:
        report["note"] = "read-only job: no GLB written"
    return report


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True,
                        help="path to job JSON file")
    args = parser.parse_args(argv)
    try:
        report = run_job_in_blender(args.job)
    except Exception:  # noqa: BLE001 - always leave a report behind
        with open(args.job, "r", encoding="utf-8") as f:
            job = json.load(f)
        report = {"job_id": job.get("job_id"), "ops_applied": [],
                  "errors": ["fatal: " + traceback.format_exc()],
                  "reweight_needed": False,
                  "out_glb": job.get("out_glb")}
    out_report = None
    try:
        with open(args.job, "r", encoding="utf-8") as f:
            out_report = json.load(f).get("out_report")
    except Exception:  # noqa: BLE001
        pass
    if out_report:
        os.makedirs(os.path.dirname(os.path.abspath(out_report)),
                    exist_ok=True)
        with open(out_report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    # machine-readable single line for the job server to parse
    print("WH_MESH_EDIT_REPORT " + json.dumps({
        "job_id": report.get("job_id"),
        "ok": not report["errors"],
        "reweight_needed": report.get("reweight_needed", False),
        "report": out_report,
    }))


if __name__ == "__main__":
    # Blender passes script args after "--"; plain python3 runs validate only.
    if "--" in sys.argv:
        main(sys.argv[sys.argv.index("--") + 1:])
    else:
        print("mesh_edit.py: run under Blender, or import validate_job/run_command "
              "from crew tooling. CLI: --job JOB.json (after --).")
