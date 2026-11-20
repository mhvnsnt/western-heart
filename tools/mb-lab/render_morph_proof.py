"""render_morph_proof.py — render proof frames of a baked template's morph targets (Cycles CPU, headless).

    blender -b --factory-startup --python tools/mb-lab/render_morph_proof.py -- \
        --glb /tmp/wh-morph-bake/powerhouse.raw.glb --out /tmp/proof --set template: \
        --set heavy:b_weight=1,b_belly=1,b_chest=1 --set face:f_jaw_w=1,f_nose_w=1 [--face]

Imports the UNPACKED bake (Blender's glTF importer has no meshopt decoder; the packed file carries the same
targets, checked by tools/mb-lab/morph_glb_report.mjs), sets the shape keys exactly as the suite sets
morphTargetInfluences (value > 0 -> '<id>+', value < 0 -> '<id>-' at |value|) and renders one PNG per --set.
The suite's own WebGL view cannot be screenshotted on the software-GL build box (draw calls stall), so this is
the visual proof; the in-suite proof is numeric (tools/creation-suite/morph_probe.cjs).
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--glb", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--face", action="store_true", help="frame the head instead of the full body")
    ap.add_argument("--res", type=int, default=420)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.glb)
    body = max((o for o in bpy.data.objects if o.type == "MESH" and o.data.shape_keys),
               key=lambda o: len(o.data.vertices))
    keys = body.data.shape_keys.key_blocks
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.samples = 24
    scn.cycles.device = "CPU"
    scn.cycles.use_denoising = False  # Debian build has no OpenImageDenoise
    scn.render.resolution_x = a.res
    scn.render.resolution_y = int(a.res * (1.0 if a.face else 1.45))
    scn.render.film_transparent = False
    world = bpy.data.worlds.new("w"); scn.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    for name, loc, en in (("key", (2.5, -3.0, 3.2), 220), ("fill", (-3.0, -2.0, 1.6), 80), ("rim", (0.0, 3.0, 2.5), 140)):
        L = bpy.data.lights.new(name, "AREA"); L.energy = en; L.size = 2.5
        o = bpy.data.objects.new(name, L); o.location = loc; scn.collection.objects.link(o)
        o.rotation_euler = (Vector((0, 0, 1.1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    if a.face:
        tgt, dist, cam.data.lens = Vector((0, 0, 1.66)), 0.75, 60
    else:
        tgt, dist, cam.data.lens = Vector((0, 0, 0.95)), 3.6, 45
    ang = math.radians(28)
    cam.location = tgt + Vector((math.sin(ang) * dist, -math.cos(ang) * dist, 0.05 if a.face else 0.15))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    for spec in a.set:
        name, _, vals = spec.partition(":")
        for k in keys:
            if k.name != "Basis":
                k.value = 0.0
        for kv in filter(None, vals.split(",")):
            sid, v = kv.split("="); v = float(v)
            kb = keys.get(sid + ("+" if v > 0 else "-"))
            if kb is None:
                raise SystemExit(f"no shape key for {sid}")
            kb.value = abs(v)
        scn.render.filepath = os.path.join(a.out, name + ".png")
        bpy.ops.render.render(write_still=True)
        print("[proof] wrote", scn.render.filepath, flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
