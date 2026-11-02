#!/usr/bin/env python3
"""bake_morph_templates.py — re-bake the creation-suite template bodies WITH
real morph targets (glTF blend shapes) for every BODY MORPHING / FACE
DEFORMATION slider.

Why (2026-11-01): the 9 template GLBs in customization/templates/meshes/ were
baked with every shape key applied, so the suite's body/face sliders could only
scale bones. Worse, the old bake passed the template's Age/Mass/Tone as
character_data morph names (they are MB-Lab *meta* properties), so nothing was
applied and all six male templates were byte-for-byte the same mesh, and all
three female ones too. This bake:

  1. starts an MB-Lab lab session for the template's character (m_ca01/f_ca01),
  2. applies the template body through MB-Lab's real AGE / FAT / MUSCLE
     transformations (obj.character_age/mass/tone, range -1..1),
  3. for every slider in customization/templates/morph-sliders.json captures the
     mesh at the template's own property value +span and -span (span 0.5 by
     default; meta weight/tone clamped to +-meta_max) and stores the vertex
     deltas against the template shape,
  4. finalizes the character (MB-Lab 71-joint skeleton fitted to THIS body),
  5. writes the deltas as shape keys '<id>+' / '<id>-' and exports a GLB with
     glTF morph targets (positions only; sparse accessors where smaller).

Size budget is handled after export by tools/mb-lab/pack_morph_templates.mjs
(gltfpack: quantized morph deltas + meshopt compression).

Run INSIDE Blender (4.3.2 verified headless on linux-arm64, Debian package):
    blender -b --factory-startup --python tools/mb-lab/bake_morph_templates.py -- \
        --template powerhouse --out /tmp/powerhouse.glb [--mblab-dir DIR]

Licence note: MB-Lab code is GPL-3.0, its database (the morph data baked
here) is AGPL-3.0, so the output GLBs are AGPL-3.0 like the old templates;
this script + body-templates.json + morph-sliders.json are the corresponding
source.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)


def log(*a):
    print("[bake]", *a, flush=True)


def load_json(rel):
    with open(os.path.join(REPO, rel)) as fh:
        return json.load(fh)


def slider_list(cat):
    out = []
    for w in cat["windows"]:
        for g in w["groups"]:
            for s in g["sliders"]:
                out.append(dict(s, window=w["key"], group=g["key"]))
    return out


def main(argv):
    import bpy
    import numpy as np
    import run_mblab_job as R

    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mblab-dir", default=os.environ.get(
        "MBLAB_DIR", os.path.join(HERE, "vendor", "MB-Lab")))
    ap.add_argument("--eps", type=float, default=1e-5,
                    help="per-vertex delta below this is treated as zero")
    ap.add_argument("--report", default=None, help="write a JSON report here")
    a = ap.parse_args(argv)

    templates = {t["id"]: t for t in load_json(
        "customization/templates/body-templates.json")["templates"]}
    tpl = templates[a.template]
    cat = load_json("customization/templates/morph-sliders.json")
    sliders = slider_list(cat)

    t0 = time.time()
    mb = R.load_mblab(a.mblab_dir)
    scn = bpy.context.scene
    scn.mblab_character_name = tpl["mb_lab"]["character"]
    mb.start_lab_session()
    h = mb.mblab_humanoid
    obj = h.get_object()
    log("session", tpl["mb_lab"]["character"], obj.name,
        len(obj.data.vertices), "verts", f"{time.time()-t0:.1f}s")

    def coords():
        n = len(obj.data.vertices)
        buf = np.empty(n * 3, dtype=np.float64)
        obj.data.vertices.foreach_get("co", buf)
        return buf.reshape(n, 3)

    META = {"age": ("character_age", "AGE"),
            "mass": ("character_mass", "FAT"),
            "tone": ("character_tone", "MUSCLE")}

    def set_meta(key, val):
        attr, tr = META[key]
        setattr(obj, attr, float(val))  # property update may already run it
        h.calculate_transformation(tr)   # idempotent: works on last_ delta

    # --- 2. template body through the real MB-Lab transformations ---
    m = {k.lower(): v for k, v in (tpl["mb_lab"].get("morphs") or {}).items()}
    meta_vals = {k: float(m.get(k, 0.0)) for k in ("age", "mass", "tone")}
    for k in ("age", "mass", "tone"):
        set_meta(k, meta_vals[k])
    h.update_character(mode="update_all")
    base = coords()
    base_cd = dict(h.character_data)
    log("template meta", meta_vals)

    # --- 3. capture per-slider deltas ---
    # Each slider spans +-`span` MB-Lab units AROUND THE TEMPLATE's own value
    # (0 = template shape). The template transforms already push region
    # Mass/Tone past 1.0 (MB-Lab allows -5..5 and extrapolates), so a fixed
    # 0..1 capture left some '+' targets empty and let Tone -1 blow the belly
    # out by 0.4 m. A relative span keeps every target non-empty and sane.
    span = float(cat.get("span", 0.5))
    META_MAX = float(cat.get("meta_max", 1.25))
    deltas = {}
    report = {"template": a.template, "character": tpl["mb_lab"]["character"],
              "meta": meta_vals, "verts": int(len(base)), "sliders": {},
              "mb_values": {}}
    for s in sliders:
        mbp = s["mb"]
        pair = {}
        if mbp.startswith("meta:"):
            key = mbp.split(":", 1)[1]
            v0 = meta_vals[key]
            for sign, val in (("+", min(META_MAX, v0 + span)),
                              ("-", max(-META_MAX, v0 - span))):
                set_meta(key, val)
                pair[sign] = coords() - base
            set_meta(key, meta_vals[key])
            # meta transforms rewrite character_data: restore exactly
            for k, v in base_cd.items():
                h.character_data[k] = v
            h.update_character(mode="update_all")
        else:
            if mbp not in h.character_data:
                raise RuntimeError(f"slider {s['id']}: MB-Lab property {mbp!r} "
                                   f"not in {tpl['mb_lab']['character']}")
            v0 = h.character_data[mbp]
            for sign, val in (("+", v0 + span), ("-", v0 - span)):
                h.character_data[mbp] = val
                h.update_character(mode="update_all")
                pair[sign] = coords() - base
            h.character_data[mbp] = v0
            h.update_character(mode="update_all")
        drift = float(np.abs(coords() - base).max())
        if drift > 1e-4:
            raise RuntimeError(f"slider {s['id']}: restore drift {drift}")
        report["mb_values"][s["id"]] = round(float(
            meta_vals[mbp[5:]] if mbp.startswith("meta:") else v0), 4)
        info = {}
        for sign, d in pair.items():
            mag = np.linalg.norm(d, axis=1)
            nz = int((mag > a.eps).sum())
            info[sign] = {"max_m": round(float(mag.max()), 5), "nonzero": nz}
            if nz:
                deltas[s["id"] + sign] = np.where(mag[:, None] > a.eps, d, 0.0)
        report["sliders"][s["id"]] = info
    log("captured", len(deltas), "targets", f"{time.time()-t0:.1f}s")

    # --- 4. finalize (skeleton fitted to this body) ---
    bpy.ops.mbast.finalize_character()
    body = None
    for o in bpy.data.objects:
        if o.type == "MESH" and len(o.data.vertices) == len(base):
            body = o
    if body is None:
        raise RuntimeError("finalized body mesh not found")
    bpy.context.view_layer.objects.active = body
    if body.data.shape_keys:
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
    n = len(body.data.vertices)
    fin = np.empty(n * 3)
    body.data.vertices.foreach_get("co", fin)
    fin = fin.reshape(n, 3)
    off = float(np.abs(fin - base).max())
    log("finalized", body.name, "max |final-base| =", off)
    report["finalize_offset_m"] = off
    if off > 1e-3:
        raise RuntimeError("finalized mesh does not match captured base")

    # drop modifiers other than the armature (the old bake applied them at
    # export; with shape keys glTF export cannot apply them)
    for mod in list(body.modifiers):
        if mod.type != "ARMATURE":
            log("remove modifier", mod.type)
            body.modifiers.remove(mod)
    # keep only the first UV map (the old GLBs shipped 5 identical-purpose sets)
    while len(body.data.uv_layers) > 1:
        body.data.uv_layers.remove(body.data.uv_layers[-1])

    # --- 5. shape keys ---
    body.shape_key_add(name="Basis", from_mix=False)
    for name, d in deltas.items():
        k = body.shape_key_add(name=name, from_mix=False)
        k.data.foreach_set("co", (fin + d).astype(np.float32).ravel())
        k.slider_min, k.slider_max = 0.0, 1.0
    log("shape keys", len(deltas))

    keep = {body} | {o for o in bpy.data.objects if o.type == "ARMATURE"}
    for o in list(bpy.data.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(a.out), export_format="GLB",
        export_yup=True, export_apply=False,
        export_morph=True, export_morph_normal=False,
        export_morph_tangent=False, export_try_sparse_sk=True,
        export_image_format="JPEG", export_jpeg_quality=88,
        export_animations=False)
    report["out_bytes"] = os.path.getsize(a.out)
    report["targets"] = sorted(deltas)
    log("exported", a.out, report["out_bytes"], "bytes", f"{time.time()-t0:.1f}s")
    if a.report:
        with open(a.report, "w") as fh:
            json.dump(report, fh, indent=1)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
