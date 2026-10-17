#!/usr/bin/env python3
"""
T-POSE RENDER PIPELINE — one command: model file + character name -> white-void + styled PNGs.

    ./render.py <model.fbx|.glb|.obj> <character-name> [--attire p1] [--facing +x] [--outdir DIR] [--white-only] [--styled-only]

When run directly, this launches Blender headless with the right environment
(xvfb, libEGL, clean PYTHONPATH). When run inside Blender via -P, it performs
the render. Do not invoke the Blender half manually.

Spec: western-heart docs/tpose-refs/MUSE_TPOSE_SPEC.md
  - 2048x2048 PNG, 1:1, pure white #FFFFFF, orthographic, Workbench FLAT+TEXTURE
  - Framing: ortho scale = 1.12 x max(span), ~5% margin, hands/feet/hair fully inside
  - Margin check: no non-white pixel within 40px of any edge
  - Naming: <outdir>/<character>/<attire>_front.png (+ _side.png, + _styled.png)

Owner laws honored: full arm span framing, VOID WHITE version for Tripo/image-to-3D,
unique filenames (never overwrite: existing files get -v2, -v3 suffixes).
Fidelity: no stylization on the white version — clean accurate render of the model as-is.
"""
import os, sys, subprocess, shutil

BLENDER = os.path.expanduser("~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")
EGL_LIB = os.path.expanduser("~/workspace/tools/libegl1/usr/lib/x86_64-linux-gnu")

def launch():
    if "--blender" in sys.argv:
        run_blender()
        return
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    lp = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = EGL_LIB + (":" + lp if lp else "")
    cmd = ["xvfb-run", "-a", "env", "-u", "PYTHONPATH",
           BLENDER, "-b", "--factory-startup",
           "-P", os.path.abspath(__file__), "--", "--blender"] + args
    # pass through our env additions: xvfb-run -> env chain
    full = ["env"] + [f"LD_LIBRARY_PATH={env['LD_LIBRARY_PATH']}"] + cmd
    r = subprocess.run(full, env={**os.environ, "LD_LIBRARY_PATH": env["LD_LIBRARY_PATH"]})
    sys.exit(r.returncode)

# ---------------------------------------------------------------- blender half
def run_blender():
    import bpy, math, re, json
    from mathutils import Vector, Matrix
    a = sys.argv[sys.argv.index("--blender")+1:]
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("model"); p.add_argument("character")
    p.add_argument("--attire", default="p1")
    p.add_argument("--facing", default="+x", choices=["+x","-x","+y","-y"])
    p.add_argument("--outdir", default=os.path.expanduser("~/workspace/tpose-renders"))
    p.add_argument("--white-only", action="store_true")
    p.add_argument("--styled-only", action="store_true")
    ns = p.parse_args(a)

    src = os.path.abspath(ns.model)
    character = re.sub(r"[^a-z0-9-]", "-", ns.character.lower())
    outdir = os.path.join(os.path.abspath(os.path.expanduser(ns.outdir)), character)
    os.makedirs(outdir, exist_ok=True)

    def unique(base):
        # UNIQUE FILENAMES LAW: never overwrite
        if not os.path.exists(base + ".png"):
            return base
        i = 2
        while os.path.exists(f"{base}-v{i}.png"):
            i += 1
        return f"{base}-v{i}"

    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = os.path.splitext(src)[1].lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=src, ignore_leaf_bones=True)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=src)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=src)
    else:
        print(f"FAIL: unsupported extension {ext}"); sys.exit(1)
    sc = bpy.context.scene
    for o in sc.objects:
        if o.animation_data:
            o.animation_data_clear()

    # --- armature: reset to rest, try T-pose if needed ---
    arms = [o for o in sc.objects if o.type == "ARMATURE"]
    posed = []
    for arm in arms:
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        for pb in arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.location = (0, 0, 0)
        bpy.context.view_layer.update()
        # T-pose the arm chains (Mixamo / Tekken8 / XNALara names)
        order = sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive))
        pat = re.compile(
            r"(l|r)_(upperarm|lowerarm|hand)"
            r"|(left|right)(arm|forearm|hand)"
            r"|(mixamorig:)?(left|right)(arm|forearm|hand)"
            r"|(upperarm|lowerarm|forearm|hand)[._](l|r)"
            r"|bip01_[lr]_(upperarm|forearm|hand)"
            r"|arm[ _](left|right)[ _](shoulder[ _][123]|elbow|wrist)", re.I)
        for pb in order:
            if not pat.fullmatch(pb.name):
                continue
            n = pb.name.lower()
            if "right" in n or re.search(r"(^|_)r[_.]", n):
                s = -1
            elif "left" in n or re.search(r"(^|_)l[_.]", n):
                s = 1
            else:
                continue
            bpy.context.view_layer.update()
            mw = arm.matrix_world @ pb.matrix
            head = mw.translation
            kids = [k for k in pb.children
                    if re.search(r"arm|hand|wrist|elbow", k.name, re.I)
                    and not re.search(r"twt|twist|mus|drv|adr|pmp|adj|unused|sleeve|lace|finger", k.name, re.I)]
            if re.search(r"hand", n) or not kids:
                continue
            tail = arm.matrix_world @ kids[0].head
            cur = tail - head
            if cur.length < 1e-6:
                continue
            # only rotate if not already roughly horizontal
            horiz = Vector((cur.x, cur.y, 0))
            if horiz.length > 1e-6 and abs(cur.z) / cur.length < 0.15:
                continue  # already T-posed
            sx = 1 if head.x > 0 else -1
            tgt = Vector((sx, 0, 0))
            q = cur.normalized().rotation_difference(tgt)
            R = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head)
            pb.matrix = arm.matrix_world.inverted() @ R @ mw
            posed.append(pb.name)
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()

    # --- drop stray import primitives ---
    for o in list(sc.objects):
        if o.type == "MESH" and re.match(r"(icosphere|cube|plane|sphere|cylinder)$", o.name, re.I):
            bpy.data.objects.remove(o)
    bpy.context.view_layer.update()

    # --- bounds ---
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in sc.objects:
        if o.type != "MESH":
            continue
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        pts += [e.matrix_world @ v.co for v in m.vertices]
        e.to_mesh_clear()
    if not pts:
        print("FAIL: no mesh geometry"); sys.exit(1)
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2
    d = mx - mn
    D = 10 * max(d)

    # --- camera rig ---
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.clip_end = 100 * max(d)
    # facing -> (front_loc, front_rot, front_span), (side_loc, side_rot, side_span)
    F = {
        "+x": (((mn.x-D, c.y, c.z), (math.pi/2, 0, -math.pi/2), max(d.y, d.z)),
               ((c.x, mn.y-D, c.z), (math.pi/2, 0, 0),          max(d.x, d.z))),
        "-x": (((mx.x+D, c.y, c.z), (math.pi/2, 0, math.pi/2),  max(d.y, d.z)),
               ((c.x, mx.y+D, c.z), (math.pi/2, 0, math.pi),    max(d.x, d.z))),
        "+y": (((c.x, mx.y+D, c.z), (math.pi/2, 0, math.pi),    max(d.x, d.z)),
               ((mx.x+D, c.y, c.z), (math.pi/2, 0, math.pi/2),  max(d.y, d.z))),
        "-y": (((c.x, mn.y-D, c.z), (math.pi/2, 0, 0),          max(d.x, d.z)),
               ((mn.x-D, c.y, c.z), (math.pi/2, 0, -math.pi/2), max(d.y, d.z))),
    }
    (floc, frot, fspan), (sloc, srot, sspan) = F[ns.facing]

    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    sc.render.resolution_x = sc.render.resolution_y = 2048
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    try:
        sc.display.render_aa = "8"
    except Exception:
        pass

    report = {"model": src, "character": character, "attire": ns.attire,
              "facing": ns.facing, "armatures": len(arms), "posed_bones": posed,
              "bbox": [[mn.x, mn.y, mn.z], [mx.x, mx.y, mx.z]]}

    def shoot(view, loc, rot, span, suffix):
        cam.location = loc
        cam.rotation_euler = rot
        cam.data.ortho_scale = span * 1.12
        base = unique(os.path.join(outdir, f"{ns.attire}_{view}{suffix}"))
        sc.render.filepath = base + ".png"
        bpy.ops.render.render(write_still=True)
        return base + ".png"

    outputs = []
    if not ns.styled_only:
        # WHITE: Workbench flat, pure white world
        w.color = (1, 1, 1)
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light = "FLAT"; sh.color_type = "TEXTURE"
        sh.show_shadows = False; sh.show_cavity = False
        sh.background_type = "WORLD"
        outputs.append(shoot("front", floc, frot, fspan, ""))
        outputs.append(shoot("side", sloc, srot, sspan, ""))

    if not ns.white_only:
        # STYLED: Cycles, soft studio — accurate, no stylization
        sc.render.engine = "CYCLES"
        sc.cycles.samples = 64
        sc.cycles.use_adaptive_sampling = True
        w.color = (0.92, 0.92, 0.94)
        w.use_nodes = True
        bg = w.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[0].default_value = (0.92, 0.92, 0.94, 1)
            bg.inputs[1].default_value = 1.0
        # 3-point lights
        for name, loc, energy in (("key", (c.x-3, c.y-4, c.z+5), 800),
                                  ("fill", (c.x+4, c.y-2, c.z+2), 300),
                                  ("rim", (c.x, c.y+5, c.z+3), 500)):
            ld = bpy.data.lights.new(name, "POINT")
            ld.energy = energy
            lo = bpy.data.objects.new(name, ld)
            lo.location = loc
            sc.collection.objects.link(lo)
        outputs.append(shoot("front", floc, frot, fspan, "_styled"))
        outputs.append(shoot("side", sloc, srot, sspan, "_styled"))

    # --- margin check (>=40px) on white renders ---
    report["margin_check"] = {}
    try:
        import numpy as np
        from PIL import Image
        for f in outputs:
            if "_styled" in f:
                continue
            a = np.asarray(Image.open(f).convert("RGB"))
            y, x = np.where(a.min(2) < 245)
            if len(x) == 0:
                report["margin_check"][os.path.basename(f)] = "blank?"
                continue
            m = [int(x.min()), int(2047 - x.max()), int(y.min()), int(2047 - y.max())]
            report["margin_check"][os.path.basename(f)] = m + ["PASS" if min(m) >= 40 else "FAIL"]
    except ImportError:
        report["margin_check"] = {"note": "PIL/numpy not in Blender python; check margins externally"}

    rep_path = unique(os.path.join(outdir, f"{ns.attire}_report"))
    with open(rep_path + ".json", "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    print("DONE", json.dumps({"outputs": outputs, "margins": report["margin_check"]}, default=str))

if __name__ == "__main__":
    launch()
