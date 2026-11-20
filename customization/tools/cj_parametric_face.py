#!/usr/bin/env python3
"""CJ Parametric Face Rig — GNM-style parametric controls for Cape Jones' cartoon face.

Technique studied from Google GNM-Head (Apache 2.0, tools/pulled/GNM/):
a grouped expression parameter vector driving the face. Adapted, not copied:
- GNM's 383 PCA components  ->  ~20 named cartoon params (animator-grade)
- GNM's semantic sampler    ->  cj_face_presets.PRESETS + blend_presets()
- GNM's 4 groups            ->  EYES / BROW / LOWER FACE / TONGUE / IRIS
- GNM's iris param          ->  pupil_toggle (canon: white eyes default)

Canon guards (LOCKED):
- White eyes by default; pupils only on emphasis beats.
- The 17 mouth meshes stay a HARD-CUT swap set (mouth_index int). The parametric
  layer drives jaw/smile/frown TRANSFORMS on the mouth holders, never blends
  mouth geometry.
- Space Ghost / Aqua Teen comedic range: exaggerated, never realistic.

Builds on cj_mouth_kit.blend (procedural kit). Output: cj_face_parametric.blend.

Usage (Blender 4.0.2 headless):
    xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender \\
        -b --python cj_parametric_face.py
"""
import bpy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import cj_face_presets as presets  # noqa: E402

KIT = os.path.join(HERE, "cj_mouth_kit.blend")
OUT = os.path.join(HERE, "cj_face_parametric.blend")

# param: (default, min, max, group, description)
PARAM_DEFS = [
    ("blink_L", 0.0, 0.0, 1.0, "EYES", "left lid close (1 = shut)"),
    ("blink_R", 0.0, 0.0, 1.0, "EYES", "right lid close (1 = shut)"),
    ("wide", 0.0, 0.0, 1.0, "EYES", "eyes widen (surprise)"),
    ("squint_L", 0.0, 0.0, 1.0, "EYES", "left squint"),
    ("squint_R", 0.0, 0.0, 1.0, "EYES", "right squint"),
    ("look_x", 0.0, -1.0, 1.0, "EYES", "pupil dart horizontal"),
    ("look_y", 0.0, -1.0, 1.0, "EYES", "pupil dart vertical"),
    ("brow_L", 0.0, -1.0, 1.0, "BROW", "left mask brow (-1 angry … +1 raised)"),
    ("brow_R", 0.0, -1.0, 1.0, "BROW", "right mask brow (-1 angry … +1 raised)"),
    ("brow_squeeze", 0.0, 0.0, 1.0, "BROW", "brows pull toward center"),
    ("jaw_open", 0.0, 0.0, 1.0, "LOWER", "jaw drop exaggeration"),
    ("smile", 0.0, 0.0, 1.0, "LOWER", "mouth widen / smile"),
    ("frown", 0.0, 0.0, 1.0, "LOWER", "mouth narrow + downturn"),
    ("grimace", 0.0, 0.0, 1.0, "LOWER", "strain grimace"),
    ("smirk_L", 0.0, 0.0, 1.0, "LOWER", "left corner lift"),
    ("smirk_R", 0.0, 0.0, 1.0, "LOWER", "right corner lift"),
    ("mouth_shift_x", 0.0, -1.0, 1.0, "LOWER", "mouth slide L/R (GNM MOUTH_LEFT/RIGHT)"),
    ("tongue_out", 0.0, 0.0, 1.0, "TONGUE", "tongue protrude"),
    ("tongue_side", 0.0, -1.0, 1.0, "TONGUE", "tongue flick L/R"),
    ("pupil_toggle", 0.0, 0.0, 1.0, "IRIS", "0 = white eyes (default), 1 = pupils (emphasis)"),
]

C_TONGUE = (0.72, 0.25, 0.32, 1.0)
C_BLACK = (0.02, 0.02, 0.02, 1.0)


# ---------------------------------------------------------------- helpers
def float_prop(ob, name, default, minv, maxv, desc):
    ob[name] = default
    ui = ob.id_properties_ui(name)
    ui.update(min=minv, max=maxv, description=desc)


def add_driver(obj, data_path, index, expr, varmap):
    """varmap: {varname: (id_object, data_path)}"""
    fcu = obj.driver_add(data_path, index)
    d = fcu.driver
    d.type = 'SCRIPTED'
    for vn, (idt, dp) in varmap.items():
        v = d.variables.new()
        v.name = vn
        v.type = 'SINGLE_PROP'
        v.targets[0].id = idt
        v.targets[0].data_path = '["%s"]' % dp
    d.expression = expr
    return fcu


def clear_drivers(obj):
    if obj.animation_data:
        obj.animation_data_clear()


def clear_subtree(obj):
    clear_drivers(obj)
    for c in obj.children:
        clear_subtree(c)


def hide_with_driver(obj, driver_id, prop, index):
    """Visibility driver on obj AND all descendants.

    Blender's hide_render on a parent does NOT hide children in renders
    (viewport-only propagation), so every descendant needs its own driver.
    """
    for dp in ("hide_viewport", "hide_render"):
        d = obj.driver_add(dp).driver
        d.type = 'SCRIPTED'
        v = d.variables.new()
        v.name = "idx"
        v.type = 'SINGLE_PROP'
        v.targets[0].id = driver_id
        v.targets[0].data_path = '["%s"]' % prop
        d.expression = "idx != %d" % index
    for c in obj.children:
        hide_with_driver(c, driver_id, prop, index)


def eye_side(group):
    return -1 if "_L" in group.name else 1


# ---------------------------------------------------------------- main
def main():
    if not os.path.exists(KIT):
        raise SystemExit("missing kit blend: %s (run build_mouthkit.py first)" % KIT)
    bpy.ops.wm.open_mainfile(filepath=KIT)

    socket = bpy.data.objects["CJ_FaceSocket"]

    # --- param holder (the GNM-style expression vector) ---
    params = bpy.data.objects.new("CJ_FaceParams", None)
    bpy.context.scene.collection.objects.link(params)
    params.parent = socket
    for name, default, minv, maxv, _grp, desc in PARAM_DEFS:
        float_prop(params, name, default, minv, maxv, desc)

    P = lambda dp: (params, dp)  # noqa: E731

    # --- re-wire eyes: kill old eye_index drivers, add parametric ones ---
    eyes = bpy.data.objects["CJ_Eyes"]
    closed = bpy.data.objects["CJ_Eye_Closed"]
    clear_subtree(eyes)

    for grp in (bpy.data.objects["CJ_Eye_L"], bpy.data.objects["CJ_Eye_R"]):
        sx = eye_side(grp)
        bl, sq = "blink_L" if sx < 0 else "blink_R", "squint_L" if sx < 0 else "squint_R"
        pupil = None
        for child in grp.children:
            if "pupil" in child.name:
                pupil = child
            elif child.name.startswith("white"):
                # vertical squash: blink shuts, squint narrows, wide opens
                add_driver(child, "scale", 1,
                           "(1-0.92*%s)*(1-0.55*%s)*(1+0.35*wide)" % (bl, sq),
                           {bl: P(bl), sq: P(sq), "wide": P("wide")})
                add_driver(child, "scale", 0,
                           "(1-0.10*%s)*(1+0.30*wide)" % bl,
                           {bl: P(bl), "wide": P("wide")})
                # fully shut eyes hide the cards (lash lines take over)
                for dp in ("hide_viewport", "hide_render"):
                    add_driver(child, dp, -1, "%s>0.97" % bl, {bl: P(bl)})
        if pupil is not None:
            bx, bz = pupil.location.x, pupil.location.z
            # eye-darts: pupils slide inside the white cards
            add_driver(pupil, "location", 0, "%.4f+0.030*look_x" % bx,
                       {"look_x": P("look_x")})
            add_driver(pupil, "location", 2, "%.4f+0.016*look_y" % bz,
                       {"look_y": P("look_y")})
            # pupils only on emphasis beats, and never on a shut eye
            for dp in ("hide_viewport", "hide_render"):
                add_driver(pupil, dp, -1, "(pt<0.5) or (%s>0.9)" % bl,
                           {"pt": P("pupil_toggle"), bl: P(bl)})
    # lash lines: one per eye, shown when that eye is shut
    for lash in closed.children:
        bl = "blink_L" if lash.location.x < 0 else "blink_R"
        for dp in ("hide_viewport", "hide_render"):
            add_driver(lash, dp, -1, "%s<0.9" % bl, {bl: P(bl)})

    # --- mask brows (sheet 05: "the mask's dynamic movement") ---
    black_mat = bpy.data.materials["CJ_Mouth_Black"]
    brows = []
    for sx, tag in ((-1, "CJ_Brow_L"), (1, "CJ_Brow_R")):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(sx * 0.088, 0.037, 0.160))
        b = bpy.context.object
        b.name = tag
        b.scale = (0.064, 0.015, 1.0)
        b.rotation_euler = (math.pi / 2, sx * 0.22, 0)
        b.data.materials.append(black_mat)
        b.parent = socket
        bn = "brow_L" if sx < 0 else "brow_R"
        base_tilt = sx * 0.22
        # angry (-1): inner end drops; raised (+1): whole brow lifts
        add_driver(b, "rotation_euler", 1, "%.4f+(-1.0*%.1f)*0.55*%s" % (base_tilt, sx, bn),
                   {bn: P(bn)})
        add_driver(b, "location", 2, "0.160+0.022*%s" % bn, {bn: P(bn)})
        add_driver(b, "location", 0, "%.4f+(-1.0*%.1f)*0.022*sqz" % (sx * 0.088, sx),
                   {"sqz": P("brow_squeeze")})
        brows.append(b)

    # --- parametric transforms on the mouth swap-set holders ---
    mouths = [o for o in bpy.data.objects if o.name.startswith("CJ_Mouth_0")
              or o.name.startswith("CJ_Mouth_1")]
    mouth_driver = bpy.data.objects["CJ_MouthDriver"]
    for i, m in enumerate(sorted(mouths, key=lambda o: o.name)):
        vm = {
            "jaw": P("jaw_open"), "sm": P("smile"), "fr": P("frown"),
            "gr": P("grimace"), "shx": P("mouth_shift_x"),
            "smL": P("smirk_L"), "smR": P("smirk_R"),
        }
        # visibility on the WHOLE subtree (Blender hide_render does not
        # propagate parent->children in renders); replaces the kit's
        # holder-only drivers.
        clear_drivers(m)
        for c in m.children:
            clear_drivers(c)
        hide_with_driver(m, mouth_driver, "mouth_index", i)
        add_driver(m, "scale", 2, "1+0.35*jaw", vm)
        add_driver(m, "scale", 0, "1+0.28*sm+0.12*gr-0.08*fr", vm)
        add_driver(m, "location", 0, "0.035*shx", vm)
        add_driver(m, "location", 2, "-0.012*jaw-0.010*fr+0.006*sm", vm)
        add_driver(m, "rotation_euler", 1, "0.20*(smL-smR)", vm)

    # --- tongue (GNM's 32 tongue params, cartoon edition: 2) ---
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.030, 0.772))
    tongue = bpy.context.object
    tongue.name = "CJ_Tongue"
    tongue.scale = (0.030, 0.028, 1.0)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    tmat = bpy.data.materials.new("CJ_Tongue_Mat")
    tmat.use_nodes = True
    tmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = C_TONGUE
    tongue.data.materials.append(tmat)
    tongue.parent = socket
    tongue.rotation_euler = (math.pi / 2, 0, 0)
    tongue.shape_key_add(name="Basis")
    k_out = tongue.shape_key_add(name="Out")
    k_l = tongue.shape_key_add(name="Side_L")
    k_r = tongue.shape_key_add(name="Side_R")
    for v, b in zip(k_out.data, tongue.data.vertices):
        v.co.y = b.co.y + 0.9   # local +Y (out toward viewer after rotation)
        v.co.z = b.co.z - 0.35
    for v, b in zip(k_l.data, tongue.data.vertices):
        v.co.x = b.co.x - 0.8
    for v, b in zip(k_r.data, tongue.data.vertices):
        v.co.x = b.co.x + 0.8
    sk = tongue.data.shape_keys
    kb = sk.key_blocks
    add_driver(kb["Out"], "value", -1, "tongue_out", {"tongue_out": P("tongue_out")})
    add_driver(kb["Side_L"], "value", -1, "max(-1.0*tongue_side,0)",
               {"tongue_side": P("tongue_side")})
    add_driver(kb["Side_R"], "value", -1, "max(tongue_side,0)",
               {"tongue_side": P("tongue_side")})
    for dp in ("hide_viewport", "hide_render"):
        add_driver(tongue, dp, -1, "tongue_out<0.02", {"tongue_out": P("tongue_out")})

    # --- store the preset table inside the blend for animators ---
    txt = bpy.data.texts.new("CJ_FACE_PRESETS")
    with open(os.path.join(HERE, "cj_face_presets.py")) as f:
        txt.write(f.read())

    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT, "| params:", len(PARAM_DEFS),
          "| mouths:", len(mouths), "| presets:", len(presets.PRESETS))


if __name__ == "__main__":
    main()
