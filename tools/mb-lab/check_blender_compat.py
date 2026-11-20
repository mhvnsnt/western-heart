#!/usr/bin/env python3
"""check_blender_compat.py — report MB-Lab/Blender compatibility HONESTLY.

MB-Lab 1.8.1 needs Blender 4.0+ and was verified headless on the WH
pipeline standard, Blender 4.0.2. Blender 5.2.3 is the WH rig/render
standard, but MB-Lab on 5.x is NOT verified until a vendor checkout +
5.x bake passes. This tool does not paper over that gap: it reports
one of three verdicts and nothing stronger.

    python3 tools/mb-lab/check_blender_compat.py --blender <path-to-blender>
    python3 tools/mb-lab/check_blender_compat.py --blender <path> --try-enable
    python3 tools/mb-lab/check_blender_compat.py --blender <path> --json

Verdicts:
  "unverified: vendor missing" — no MB-Lab checkout at
      tools/mb-lab/vendor/MB-Lab (or --mblab-dir). Nothing about this
      Blender version is claimed, in either direction.
  "incompatible: blender < 4.0" — MB-Lab 1.8.x needs Blender 4.0+.
  "candidate: vendor present" — the checkout exists and the Blender
      is >= 4.0, but a headless bake has still not been run, so
      compatibility is still NOT claimed.
  With --try-enable and a vendor checkout, Blender is run headless
  with a tiny script that enables the mblab addon the same way
  run_mblab_job.py does; only an explicit ENABLED marker upgrades
  the verdict to "addon-enabled" — which still is not a bake claim.
  A bake claim requires run_mblab_job.py to produce a GLB on that
  Blender, which this tool never asserts.

Pure Python (no bpy import here); the --try-enable probe runs inside
Blender as a temp script. Exit 0 always on a completed check; exit 2
only if the Blender binary itself cannot be run.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_VENDOR = os.path.join(HERE, "vendor", "MB-Lab")


def parse_blender_version(text):
    m = re.search(r"Blender\s+(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        raise RuntimeError(f"could not parse Blender version from: {text[:200]!r}")
    return tuple(int(g) for g in m.groups())


def try_enable(blender, mblab_dir):
    """Run Blender headless; try to enable mblab. Returns (ok, output)."""
    probe = (
        "import bpy, sys, os, addon_utils\n"
        f"mblab_dir = {mblab_dir!r}\n"
        "addons_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'addons')\n"
        "os.makedirs(addons_dir, exist_ok=True)\n"
        "link = os.path.join(addons_dir, 'mblab')\n"
        "try:\n"
        "    (os.remove(link) if (os.path.islink(link) or os.path.exists(link)) else None)\n"
        "    os.symlink(mblab_dir, link)\n"
        "except OSError:\n"
        "    pass\n"
        "sys.path.append(addons_dir)\n"
        "addon_utils.modules_refresh()\n"
        "bpy.ops.preferences.addon_enable(module='mblab')\n"
        "print('MBLAB_ENABLED')\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(probe)
        probe_path = fh.name
    try:
        r = subprocess.run([blender, "-b", "--factory-startup", "--python",
                            probe_path], capture_output=True, text=True,
                           timeout=600)
        out = r.stdout + r.stderr
        return ("MBLAB_ENABLED" in out and r.returncode == 0), out
    finally:
        try:
            os.unlink(probe_path)
        except OSError:
            pass


def check(blender, mblab_dir, try_enable_flag=False):
    if not (os.path.isfile(blender) and os.access(blender, os.X_OK)):
        raise RuntimeError(f"Blender binary not executable: {blender}")
    r = subprocess.run([blender, "--version"], capture_output=True,
                       text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"{blender} --version failed: {r.stderr[:500]}")
    version = parse_blender_version(r.stdout)
    init_present = os.path.isfile(os.path.join(mblab_dir, "__init__.py"))
    result = {
        "blender": blender,
        "blender_version": ".".join(map(str, version)),
        "mblab_dir": mblab_dir,
        "mblab_present": init_present,
    }
    if not init_present:
        result["verdict"] = ("unverified: vendor missing — run "
                             "bash tools/mb-lab/fetch-mb-lab.sh first; "
                             "no claim is made about this Blender version")
        return result
    if version < (4, 0, 0):
        result["verdict"] = "incompatible: MB-Lab 1.8.x needs Blender 4.0+"
        return result
    if not try_enable_flag:
        result["verdict"] = ("candidate: vendor present, Blender >= 4.0, "
                             "but no headless bake run — compatibility "
                             "NOT claimed")
        return result
    ok, out = try_enable(blender, mblab_dir)
    result["addon_enable_output_tail"] = out[-1000:]
    result["verdict"] = ("addon-enabled (bake still required for a "
                         "compatibility claim)" if ok else
                         "addon-enable-failed on this Blender")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--blender", required=True)
    ap.add_argument("--mblab-dir", default=DEFAULT_VENDOR)
    ap.add_argument("--try-enable", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        result = check(a.blender, a.mblab_dir, a.try_enable)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(result, indent=1))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
