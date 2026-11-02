#!/usr/bin/env python3
"""run_mpfb2_job.py — headless MPFB2 character generation for Blender 4.2+.

Runs in two modes:

1. Via the job queue (tools/suite-jobs/run_job.py), which imports this
   module in plain Python and calls run_job(spec, log). That path
   validates the spec, resolves a Blender 4.2+ binary and the MPFB2
   vendor checkout, then spawns Blender headless for the real work.
   This module imports `bpy` ONLY inside the Blender-inner function,
   so importing it outside Blender is safe.

2. Inside Blender (spawned by mode 1):
       blender -b --python tools/mpfb2/run_mpfb2_job.py -- --inner \\
           --spec <spec.json> --out <file.glb>

   The inner path follows MPFB2's own script_samples
   (makehumancommunity/mpfb2, script_samples/01, 02, 04, 10):
   HumanService.create_human(), HumanObjectProperties.set_value() for
   the macro attributes, TargetService.reapply_macro_details(), and
   HumanService.add_builtin_rig() for the optional rig. The dynamic
   import quirk from those samples is copied verbatim, because MPFB2
   as a Blender extension does not sit at a fixed module path.

Spec params:
    macro: {gender, age, muscle, weight, height, proportions, ...}
           MPFB2 macro attributes, each 0..1. Per MPFB2's
           docs/entities/objectproperties.md: gender 0.0 = fully
           female, 1.0 = fully male; all other macro attributes
           default 0.5. Keys outside that set are rejected.
    rig:   null (no rig; the WH GameRig stage rigs the exported base
           later) | "game_engine" | "rigify.human" (Rigify metarig +
           generated control rig, following script sample 04; needs
           the Rigify addon enabled in that Blender).

What this job does NOT do: it does not apply skin/eyes/clothes asset
packs (script sample 10 needs the makehuman_system_assets pack, which
is not fetched here), and it does not strip MPFB helper geometry —
the export chain (glTF-Transform) is the stage for that. The GLB it
writes is the MPFB2 base as generated, exported with Blender's own
gltf exporter. Skin/asset steps are a follow-up job, not silently
skipped inside this one.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

MACRO_KEYS = {
    "gender", "age", "muscle", "weight", "height",
    "proportions", "cupsize", "firmness",
}
RIGS = {None, "game_engine", "rigify.human"}


def validate_spec(spec):
    """Pure-Python spec validation. Returns (params, out). Raises on bad input."""
    params = spec.get("params", {})
    if not isinstance(params, dict):
        raise RuntimeError("spec params must be an object")
    macro = params.get("macro")
    if not isinstance(macro, dict) or not macro:
        raise RuntimeError("spec params.macro must be a non-empty object")
    unknown = sorted(set(macro) - MACRO_KEYS)
    if unknown:
        raise RuntimeError(f"unknown MPFB2 macro attributes: {unknown}")
    for k, v in macro.items():
        if not 0.0 <= float(v) <= 1.0:
            raise RuntimeError(f"macro {k}={v} outside 0..1")
    rig = params.get("rig")
    if rig not in RIGS:
        raise RuntimeError(f"unsupported rig {rig!r}; use one of {sorted(map(str, RIGS))}")
    out = spec.get("out")
    if not out:
        raise RuntimeError("spec needs 'out'")
    return params, out


def parse_blender_version(text):
    """Parse 'Blender X.Y.Z ...' from `blender --version` output."""
    m = re.search(r"Blender\s+(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        raise RuntimeError(f"could not parse Blender version from: {text[:200]!r}")
    return tuple(int(g) for g in m.groups())


def find_blender(params, log=print):
    """Resolve a Blender >= 4.2 binary. MPFB2 needs Blender 4.2+ (extension
    platform); the WH 4.0.2 pipeline standard does NOT run it."""
    cands = []
    if params.get("blender"):
        cands.append(params["blender"])
    if os.environ.get("MPFB2_BLENDER"):
        cands.append(os.environ["MPFB2_BLENDER"])
    cands.append(os.path.join(REPO, "tools", "mpfb2", "vendor", "blender42", "blender"))
    cands.append(os.path.join(HERE, "vendor", "blender42", "blender"))
    which = shutil.which("blender")
    if which:
        cands.append(which)
    for cand in cands:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            ver = parse_blender_version(
                subprocess.run([cand, "--version"], capture_output=True,
                               text=True, timeout=60).stdout)
            if ver < (4, 2, 0):
                raise RuntimeError(
                    f"Blender {'.'.join(map(str, ver))} at {cand} is below "
                    "4.2 — MPFB2 does not run on it. Fetch one with: "
                    "bash tools/mpfb2/fetch-mpfb2.sh --with-blender")
            log(f"Blender {'.'.join(map(str, ver))} at {cand}")
            return cand
    raise RuntimeError(
        "no Blender 4.2+ found. Fetch one with: "
        "bash tools/mpfb2/fetch-mpfb2.sh --with-blender "
        "(or set MPFB2_BLENDER / params.blender)")


def find_mpfb2(params):
    """Resolve the MPFB2 vendor checkout. Returns its directory."""
    cands = []
    if params.get("mpfb2_dir"):
        cands.append(params["mpfb2_dir"])
    if os.environ.get("MPFB2_DIR"):
        cands.append(os.environ["MPFB2_DIR"])
    cands.append(os.path.join(HERE, "vendor"))
    cands.append(os.path.join(REPO, "tools", "mpfb2", "vendor"))
    for cand in cands:
        if cand and os.path.isfile(os.path.join(cand, "mpfb", "__init__.py")):
            return cand
    raise RuntimeError(
        "MPFB2 not found. Run: bash tools/mpfb2/fetch-mpfb2.sh "
        "(looked for <vendor>/mpfb/__init__.py)")


def run_job(spec, log=print):
    """Job-queue entry point (plain Python). Spawns Blender headless."""
    params, out = validate_spec(spec)
    mpfb2_dir = find_mpfb2(params)
    blender = find_blender(params, log)
    log(f"MPFB2 vendor: {mpfb2_dir}")
    # Hand the spec to the Blender-inner run via a temp file so the
    # inner script sees exactly the validated spec.
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump({"params": params, "out": out, "mpfb2_dir": mpfb2_dir}, fh)
        spec_path = fh.name
    try:
        cmd = [blender, "-b", "--factory-startup", "--python", __file__,
               "--", "--inner", "--spec", spec_path]
        log("running: " + " ".join(cmd))
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        log(r.stdout[-4000:])
        if r.returncode != 0:
            raise RuntimeError(f"Blender MPFB2 run failed:\n{r.stderr[-4000:]}")
    finally:
        try:
            os.unlink(spec_path)
        except OSError:
            pass
    if not os.path.isfile(out):
        raise RuntimeError(f"Blender run finished but {out} was not written")
    return out


def blender_inner(spec_path):
    """Runs INSIDE Blender. Follows MPFB2 script_samples 01/02/04."""
    import bpy
    with open(spec_path) as fh:
        data = json.load(fh)
    params, out, mpfb2_dir = data["params"], data["out"], data["mpfb2_dir"]
    macro, rig = params["macro"], params.get("rig")

    # Enable the MPFB2 extension/addon. Nightly zips unpack as mpfb/;
    # extension-platform installs register as bl_ext.blender_org.mpfb.
    import addon_utils
    sys.path.append(mpfb2_dir)
    enabled = False
    for mod in ("bl_ext.blender_org.mpfb", "mpfb"):
        try:
            addon_utils.enable(mod)
            enabled = True
            print(f"MPFB2 enabled as {mod}")
            break
        except Exception as e:  # noqa: BLE001
            print(f"MPFB2 enable as {mod} failed: {e}")
    if not enabled:
        raise RuntimeError("could not enable MPFB2 in this Blender")

    # Dynamic-import quirk, copied from MPFB2 script_samples.
    import importlib

    def dynamic_import(absolute_package_str, key):
        for amod in sys.modules:
            if amod.endswith(absolute_package_str):
                mpfb_mod = importlib.import_module(amod)
                if not hasattr(mpfb_mod, key):
                    raise AttributeError(
                        f"Module {amod} does not have attribute {key}")
                return getattr(mpfb_mod, key)
        raise ValueError(
            f"No module found with name ending in {absolute_package_str}")

    HumanService = dynamic_import("mpfb.services.humanservice", "HumanService")
    TargetService = dynamic_import("mpfb.services.targetservice", "TargetService")
    HumanObjectProperties = dynamic_import(
        "mpfb.entities.objectproperties", "HumanObjectProperties")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    human = HumanService.create_human()
    for key, value in macro.items():
        HumanObjectProperties.set_value(key, float(value), entity_reference=human)
    TargetService.reapply_macro_details(human)
    print(f"MPFB2 human: {len(human.data.vertices)} verts, macro={macro}")

    if rig == "game_engine":
        HumanService.add_builtin_rig(human, "game_engine")
    elif rig == "rigify.human":
        RigService = dynamic_import("mpfb.services.rigservice", "RigService")
        SystemService = dynamic_import("mpfb.services.systemservice", "SystemService")
        if not SystemService.check_for_rigify():
            raise RuntimeError("Rigify addon is not enabled in this Blender")
        metarig = HumanService.add_builtin_rig(human, "rigify.human")
        RigService.generate_rigify_rig(metarig, meta_rig_action="delete")

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
    print(f"WROTE {out}")


def main(argv=None):
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
