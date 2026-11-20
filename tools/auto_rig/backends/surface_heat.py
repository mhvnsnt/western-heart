"""backends/surface_heat.py — Surface Heat Diffuse Skinning backend.

Runs INSIDE Blender. Recomputes skin weights on an already-skeletonized
model with the vendored MIT Surface Heat Diffuse Skinning add-on
(../vendor/surface-heat-diffuse — heat diffused over the mesh surface
from each bone, so weights stop bleeding across close-but-separate
surfaces like armpits and fingers, the classic built-in bone-heat
failure).

    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup \
        --python surface_heat.py -- --in SKEL.glb --out RESKINNED.glb

If the add-on's C++ helper is missing it is built from the vendored
sources with g++ (one-time per machine). If anything in that chain is
unavailable, the script prints SURFACE_HEAT_UNAVAILABLE and exits 3 so
the caller can fall back to blender_heat.py instead of failing.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "..", "vendor", "surface-heat-diffuse")
ADDON_DIR = os.path.join(VENDOR, "addon", "surface_heat_diffuse_skinning")


def ensure_helper():
    import platform
    plat = {"Linux": "Linux", "Darwin": "MacOS",
            "Windows": "Windows"}[platform.system()]
    name = "shd"
    if plat == "Windows":
        name += ".exe"
    path = os.path.join(ADDON_DIR, "bin", plat, name)
    if os.path.exists(path):
        return path
    src = os.path.join(VENDOR, "src")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = ["g++", "-O2", "-o", path,
           os.path.join(src, "main.cpp"), os.path.join(src, "raytri.cpp"),
           os.path.join(src, "tribox.cpp")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(path):
        raise RuntimeError(f"helper build failed: {r.stderr[-400:]}")
    return path


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    a = ap.parse_args(argv)

    try:
        ensure_helper()
    except Exception as e:
        print("SURFACE_HEAT_UNAVAILABLE:", e)
        return 3

    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.inp)
    arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not arm or not meshes:
        print("SURFACE_HEAT_UNAVAILABLE: no armature/mesh in input")
        return 3
    arm = arm[0]

    # the add-on exchanges mesh data with its helper through a data/
    # scratch folder inside the add-on directory (not shipped upstream)
    os.makedirs(os.path.join(ADDON_DIR, "data"), exist_ok=True)

    # load the vendored add-on straight from its folder
    sys.path.insert(0, os.path.join(VENDOR, "addon"))
    import surface_heat_diffuse_skinning as addon
    addon.register()

    # The add-on's operator is modal (built for the UI: it launches the
    # helper, then polls it from a timer). Headless, we drive the same
    # pipeline synchronously through the operator's own methods:
    # write mesh/bone data -> run helper to completion -> read weights
    # back. Same files, same arguments, no UI shell.
    import platform as _platform
    import types as _types
    # bpy.types.Operator subclasses cannot be instantiated directly in
    # Blender 4.x; bind the add-on's pipeline methods to a plain shim
    # carrying the state they use (_objs/_permulation/.../report).
    op = _types.SimpleNamespace(
        _objs=[], _permulation=[], _selected_indices=[],
        _selected_group_index_weights=[],
        report=lambda *a, **k: None)
    for _fn in ("write_mesh_data", "write_bone_data", "read_weight_data"):
        setattr(op, _fn, _types.MethodType(
            getattr(addon.SFC_OT_ModalTimerOperator, _fn), op))
    meshes.sort(key=lambda o: o.name)
    op._objs = meshes
    data_dir = os.path.join(ADDON_DIR, "data")
    for m in meshes:
        bpy.context.view_layer.objects.active = m
        bpy.ops.object.mode_set(mode="OBJECT")
    op.write_mesh_data(meshes, os.path.join(data_dir,
                                            "untitled-mesh.txt"))
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="OBJECT")
    op.write_bone_data(arm, os.path.join(data_dir, "untitled-bone.txt"))

    scn = bpy.context.scene
    helper = os.path.join(ADDON_DIR, "bin", _platform.system(), "shd")
    os.chmod(helper, 0o755)
    cmd = [helper, "untitled-mesh.txt", "untitled-bone.txt",
           "untitled-weight.txt", str(scn.surface_resolution),
           str(scn.surface_loops), str(scn.surface_samples),
           str(scn.surface_influence), str(scn.surface_falloff),
           scn.surface_sharpness,
           "y" if scn.detect_surface_solidify else "n"]
    r = subprocess.run(cmd, cwd=data_dir, capture_output=True,
                       text=True, timeout=3600)
    weights_path = os.path.join(data_dir, "untitled-weight.txt")
    if r.returncode != 0 or not os.path.exists(weights_path):
        print("SURFACE_HEAT_UNAVAILABLE: helper failed:",
              (r.stdout + r.stderr)[-400:])
        return 3
    op.read_weight_data(meshes, weights_path)
    for m in meshes:
        if not any(md.type == "ARMATURE" and md.object == arm
                   for md in m.modifiers):
            md = m.modifiers.new("Armature", "ARMATURE")
            md.object = arm
        if m.parent != arm:
            mw = m.matrix_world.copy()
            m.parent = arm
            m.matrix_world = mw
    bpy.ops.export_scene.gltf(filepath=a.out, export_skins=True,
                              export_all_influences=False)
    print("SURFACE_HEAT_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
