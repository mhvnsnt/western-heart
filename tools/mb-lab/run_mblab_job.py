#!/usr/bin/env python3
"""run_mblab_job.py — headless MB-Lab character generation for Blender 4.0.2.

Runs INSIDE Blender:
    blender -b --python tools/mb-lab/run_mblab_job.py -- \
        --spec <spec.json> --out <file.glb> [--mblab-dir <path>]

Or via the job queue (tools/suite-jobs/run_job.py), which calls run_job(spec, log).

Spec params:
    character: MB-Lab character id, e.g. "male_01"/"female_01" (listed at runtime)
    phenotype: phenotype db name (optional, e.g. "european")
    seed:      int — deterministic randomize pass (optional)
    morphs:    {morph_name: value} — direct character_data overrides, matched
               case-insensitively against the live morph database
    expression: expression preset name (optional)
    finalize:  bool (default true) — convert to standard Blender model
"""
import argparse
import importlib.util
import json
import os
import sys

MBLAB_DIR = os.environ.get(
    "MBLAB_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "MB-Lab"),
)


def load_mblab(mblab_dir):
    import bpy
    init_py = os.path.join(mblab_dir, "__init__.py")
    if not os.path.isfile(init_py):
        raise RuntimeError(
            f"MB-Lab not found at {mblab_dir}. Run: bash tools/mb-lab/fetch-mb-lab.sh")
    # Headless Blender needs the addon enabled through the real addon system
    # (preferences lookup uses __package__); a bare importlib load leaves
    # bpy.context.preferences.addons empty and start_lab_session() crashes.
    # So: link it into the user addons dir under a valid module name and
    # enable it properly.
    addons_dir = os.path.join(
        bpy.utils.resource_path("USER"), "scripts", "addons")
    os.makedirs(addons_dir, exist_ok=True)
    link = os.path.join(addons_dir, "mblab")
    try:
        if os.path.islink(link) or os.path.exists(link):
            os.remove(link)
        os.symlink(mblab_dir, link)
    except OSError:
        pass  # already fine
    bpy.ops.preferences.addon_enable(module="mblab")
    import mblab as mod  # noqa: E402
    return mod


def run_job(spec, log=print):
    import bpy  # noqa: F401  (only importable inside Blender)
    params = spec.get("params", {})
    out = spec.get("out")
    if not out:
        raise RuntimeError("spec needs 'out'")

    mblab = load_mblab(params.get("mblab_dir", MBLAB_DIR))
    scn = bpy.context.scene

    char_id = params.get("character", "male_01")
    h0 = mblab.mblab_humanoid
    available = [c[0] for c in h0.humanoid_types] if h0.humanoid_types else []
    log(f"available characters: {available[:12]}")
    if available and char_id not in available:
        log(f"WARNING: {char_id!r} not in library, using {available[0]!r}")
        char_id = available[0]
    scn.mblab_character_name = char_id
    log(f"character: {char_id}")

    mblab.start_lab_session()
    h = mblab.mblab_humanoid
    log("lab session started")

    # phenotype (optional)
    ph = params.get("phenotype")
    if ph and hasattr(h, "phenotypes_path"):
        import glob
        cands = glob.glob(os.path.join(h.phenotypes_path, "*"))
        names = [os.path.splitext(os.path.basename(c))[0] for c in cands]
        if ph in names:
            # phenotypes apply as morph sets via the standard randomize path
            log(f"phenotype: {ph} (applied via preserve_phenotype randomize)")
            scn.mblab_preserve_phenotype = True
        else:
            log(f"WARNING: phenotype {ph!r} not found in {names[:8]}")

    # deterministic randomize pass (like the UI Generate button)
    if "seed" in params:
        import random
        random.seed(params["seed"])
        h.generate_character(0.0, False, False, False, False, False, False,
                             False, 0.0, 0.0, False)
        log(f"randomize pass with seed {params['seed']} (rnd=0 -> neutral-ish)")

    # direct morph overrides, matched case-insensitively
    morphs = params.get("morphs", {}) or {}
    if morphs:
        keys = list(h.morph_engine.morph_data.keys())
        lower = {k.lower(): k for k in keys}
        applied, missing = 0, []
        for name, val in morphs.items():
            real = lower.get(str(name).lower())
            if real is None:
                missing.append(name)
                continue
            h.morph_engine.morph_data[real] = float(val)
            applied += 1
        h.update_character()
        log(f"morphs applied: {applied}/{len(keys)} known, unknown: {missing[:10]}")

    # expression preset (optional)
    expr = params.get("expression")
    if expr and hasattr(h, "set_expression"):
        try:
            h.set_expression(expr)
            log(f"expression: {expr}")
        except Exception as e:  # noqa: BLE001
            log(f"WARNING: expression {expr!r} failed: {e}")

    if params.get("finalize", True):
        bpy.ops.mbast.finalize_character()
        log("finalized to standard Blender model")

    # --- cleanup + decimate for suite preview ---
    # Drop everything except the character mesh + its armature (kills the
    # stray Cube/camera/lights the finalize leaves behind).
    char_objs = [o for o in bpy.data.objects
                 if o.type == "MESH" and o.name.lower().startswith(
                     scn.mblab_final_prefix.lower() or "mblab")]
    if not char_objs:
        # fallback: largest mesh object
        meshes = sorted([o for o in bpy.data.objects if o.type == "MESH"],
                        key=lambda o: len(o.data.polygons) if o.data else 0)
        char_objs = meshes[-1:]
    keep = set(char_objs)
    keep |= {o for o in bpy.data.objects if o.type == "ARMATURE"}
    for o in list(bpy.data.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    body = char_objs[0]
    log(f"character mesh: {body.name} ({len(body.data.polygons)} polys)")
    ratio = float(params.get("decimate_ratio", 0.06))
    if ratio and 0 < ratio < 1:
        # Shape keys don't survive decimation cleanly: bake the current
        # (Basis) shape into the mesh, drop the keys, then decimate.
        if body.data.shape_keys:
            bpy.context.view_layer.objects.active = body
            bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
        mod = body.modifiers.new("WH_Decimate", "DECIMATE")
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.modifier_apply(modifier=mod.name)
        log(f"decimated x{ratio} -> {len(body.data.polygons)} polys")

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(out), export_format="GLB",
        export_apply=True, export_yup=True)
    log(f"exported -> {out}")
    return os.path.abspath(out)


def main(argv=None):
    # NOTE: when run under `blender -b --python`, bpy exists; otherwise this
    # entry is only used by the job queue which shells out to Blender.
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mblab-dir", default=None)
    a = ap.parse_args(argv)
    with open(a.spec) as fh:
        spec = json.load(fh)
    if a.out:
        spec["out"] = a.out
    if a.mblab_dir:
        spec.setdefault("params", {})["mblab_dir"] = a.mblab_dir
    return run_job(spec)


if __name__ == "__main__":
    # Called two ways:
    #  1. blender -b --python this.py -- --spec ... -> run inside Blender now
    #  2. imported by tools/suite-jobs/run_job.py (no bpy) -> dispatch below
    try:
        import bpy  # noqa: F401
        _IN_BLENDER = True
    except ImportError:
        _IN_BLENDER = False
    if _IN_BLENDER:
        argv = sys.argv
        if "--" in argv:
            argv = argv[argv.index("--") + 1:]
        else:
            argv = []
        main(argv)
    else:
        # no bpy: shell out to Blender (used by the job queue)
        import subprocess
        ap = argparse.ArgumentParser()
        ap.add_argument("--spec", required=True)
        ap.add_argument("--out", default=None)
        a = ap.parse_args()
        blender = os.environ.get("BLENDER", os.path.expanduser(
            "~/workspace/tools/blender/blender-4.0.2-linux-x64/blender"))
        cmd = [blender, "-b", "--python", os.path.abspath(__file__), "--",
               "--spec", os.path.abspath(a.spec)]
        if a.out:
            cmd += ["--out", a.out]
        print("spawning:", " ".join(cmd), flush=True)
        r = subprocess.run(cmd)
        sys.exit(r.returncode)
