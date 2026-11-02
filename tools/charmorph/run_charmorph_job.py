#!/usr/bin/env python3
"""run_charmorph_job.py — headless CharMorph Vitruvian base import.

Runs in two modes, mirroring tools/mpfb2/run_mpfb2_job.py:

1. Via the job queue (tools/suite-jobs/run_job.py), which imports this
   module in plain Python and calls run_job(spec, log). Run_job.py's
   default convention resolves tool "charmorph" to this file
   (tools/charmorph/run_charmorph_job.py) — no override needed.
   This module imports `bpy` ONLY inside the Blender-inner function.

2. Inside Blender (spawned by mode 1):
       blender -b --python tools/charmorph/run_charmorph_job.py -- --inner \\
           --spec <spec.json>

Spec params:
    character: must be "vitruvian" — the only base wired in this
               family (CC0). Other CharMorph bases (Antonia/Reom
               CC-BY, MB-Lab base AGPL) are NOT wired here and are
               rejected, so a CC-BY/AGPL base can never slip through
               under this family's CC0 label.

What the Blender-inner run actually does — and what it does not:
  - It locates characters/vitruvian/char.blend + config.yaml (per
    CharMorph's docs, every character lives in
    ./characters/<name> with char.blend + config.yaml). If they are
    missing — the normal state after a bare addon checkout, because
    Vitruvian ships via CharMorph 0.4's in-Blender downloader or the
    CharMorph-db library — it FAILS with downloader instructions.
    It never exports a substitute mesh.
  - If present, it links the stored base objects from char.blend
    with Blender's own library linking (bpy.data.libraries.load)
    and exports them as GLB with Blender's own gltf exporter.
  - It does NOT run CharMorph's morph UI, finalize step, or Rigify
    generation (CharMorph's README: the rig is added only at
    finalization). Those are the next suite stages: finalize in
    Blender (Rigify), then the WH GameRig retarget — documented in
    tools/charmorph/README.md, not faked inside this job.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

WIRED_CHARACTER = "vitruvian"


def validate_spec(spec):
    """Pure-Python spec validation. Returns (params, out)."""
    params = spec.get("params", {})
    if not isinstance(params, dict):
        raise RuntimeError("spec params must be an object")
    if params.get("character") != WIRED_CHARACTER:
        raise RuntimeError(
            f"only character {WIRED_CHARACTER!r} is wired in this family; "
            f"got {params.get('character')!r}")
    out = spec.get("out")
    if not out:
        raise RuntimeError("spec needs 'out'")
    return params, out


def find_charmorph(params):
    """Resolve the CharMorph vendor checkout (addon __init__.py)."""
    cands = []
    if params.get("charmorph_dir"):
        cands.append(params["charmorph_dir"])
    if os.environ.get("CHARMORPH_DIR"):
        cands.append(os.environ["CHARMORPH_DIR"])
    cands.append(os.path.join(HERE, "vendor", "CharMorph"))
    cands.append(os.path.join(REPO, "tools", "charmorph", "vendor", "CharMorph"))
    for cand in cands:
        if cand and os.path.isfile(os.path.join(cand, "__init__.py")):
            return cand
    raise RuntimeError(
        "CharMorph not found. Run: bash tools/charmorph/fetch-charmorph.sh "
        "(looked for <vendor>/CharMorph/__init__.py)")


def find_character(addon_dir, character):
    """Locate a downloaded character (char.blend + config.yaml).

    CharMorph's docs put every character in ./characters/<name>;
    the checkout layout varies (data/ submodule vs addon data dir),
    so every plausible root is checked and the missing case reports
    all of them — never a silent fallback to another character.
    """
    roots = [
        os.path.join(addon_dir, "data", "characters"),
        os.path.join(addon_dir, "characters"),
        os.path.join(addon_dir, "data"),
    ]
    tried = []
    for root in roots:
        char_dir = os.path.join(root, character)
        blend = os.path.join(char_dir, "char.blend")
        cfg = os.path.join(char_dir, "config.yaml")
        tried.append(char_dir)
        if os.path.isfile(blend) and os.path.isfile(cfg):
            return blend, cfg
    raise RuntimeError(
        f"CharMorph character {character!r} not downloaded. "
        "Use CharMorph 0.4's in-Blender character downloader (or the "
        f"CharMorph-db library) so one of these exists with char.blend "
        f"+ config.yaml: {tried}")


def run_job(spec, log=print):
    """Job-queue entry point (plain Python). Spawns Blender headless."""
    import shutil
    import subprocess
    import tempfile
    params, out = validate_spec(spec)
    addon_dir = find_charmorph(params)
    blend, _cfg = find_character(addon_dir, params["character"])
    log(f"CharMorph addon: {addon_dir}")
    log(f"Vitruvian char.blend: {blend}")
    blender = params.get("blender") or os.environ.get("CHARMORPH_BLENDER") \
        or shutil.which("blender")
    if not blender or not os.path.isfile(blender):
        raise RuntimeError(
            "no Blender binary found. Set params.blender, "
            "CHARMORPH_BLENDER, or put blender on PATH. (CharMorph 0.4 "
            "targets Blender 4.4 per upstream; WH 4.0.2 compatibility "
            "is NOT verified — the job fails at addon load if it "
            "does not load, it does not claim a version works.)")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump({"params": params, "out": out, "blend": blend}, fh)
        spec_path = fh.name
    try:
        cmd = [blender, "-b", "--factory-startup", "--python", __file__,
               "--", "--inner", "--spec", spec_path]
        log("running: " + " ".join(cmd))
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        log(r.stdout[-4000:])
        if r.returncode != 0:
            raise RuntimeError(f"Blender CharMorph run failed:\n{r.stderr[-4000:]}")
    finally:
        try:
            os.unlink(spec_path)
        except OSError:
            pass
    if not os.path.isfile(out):
        raise RuntimeError(f"Blender run finished but {out} was not written")
    return out


def blender_inner(spec_path):
    """Runs INSIDE Blender: link the stored base, export GLB."""
    import bpy
    with open(spec_path) as fh:
        data = json.load(fh)
    out, blend = data["out"], data["blend"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    linked = []
    with bpy.data.libraries.load(blend, link=True) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
        linked = list(data_to.objects)
    if not linked:
        raise RuntimeError(f"no objects linked from {blend}")
    meshes = [o for o in linked if o.type == "MESH"]
    print(f"linked {len(linked)} objects ({len(meshes)} meshes) from {blend}")
    bpy.ops.object.select_all(action="DESELECT")
    for o in linked:
        o.select_set(True)
    bpy.context.view_layer.objects.active = linked[0]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB",
                              use_selection=True)
    print(f"WROTE {out}")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    with open(a.spec) as fh:
        spec = json.load(fh)
    if a.out:
        spec["out"] = a.out
    return run_job(spec, print)


if __name__ == "__main__":
    if "--inner" in sys.argv:
        idx = sys.argv.index("--inner")
        rest = sys.argv[idx + 1:]
        spec_path = rest[rest.index("--spec") + 1]
        blender_inner(spec_path)
    else:
        main()
