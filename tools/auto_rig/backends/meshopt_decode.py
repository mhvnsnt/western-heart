#!/usr/bin/env python3
"""tools/auto_rig/backends/meshopt_decode.py — EXT_meshopt_compression
decode stage for the auto_rig audit path.

WHY THIS EXISTS (2026-10-31, rig-continuation stage 2): 16 of the 66
roster GLBs in the 2026-10-30 rig audit sweep were AUDIT-ERROR — not
verdicts. They are gltfpack-style files whose accessors address a
meshopt-compressed fallback buffer; skin_audit reads physical buffer
offsets (numpy.frombuffer) and throws ValueError ("offset must be
non-negative...", "buffer is smaller than requested size"). Until a
decode stage existed these rigs were unmeasurable, which is itself a
100%-readiness blocker (sweep recommendation #6).

WHAT IT DOES: detects EXT_meshopt_compression in the GLB header JSON
(extensionsUsed / extensionsRequired / per-buffer extension), and
decodes with gltfpack in no-quantization mode:

    gltfpack -i in.glb -o out.glb -noq

-noq writes plain float32 attributes with no KHR_mesh_quantization
and no EXT_meshopt_compression, i.e. exactly the physical layout
skin_audit's accessor reader assumes. The DECODED file is an audit
input only — it is never shipped and never replaces the roster file;
the shipping decision on re-encode vs decoded is a separate stage.

Provenance: decode route proven 2026-10-30 on Baek attire1 via
gltf-transform copy (docs/handoffs/RIGFIX-BAEK-2026-10-30.md);
gltfpack -noq proven equivalent-for-audit 2026-10-31 on armor-king
attire1 model-rigged (decoded 5660 verts / 49 joints, audit produced
a real FAIL verdict with sane measures) and on Baek attire1
(89,580,040 B decoded).

    python3 meshopt_decode.py --in MODEL.glb [--out DECODED.glb]
    python3 meshopt_decode.py --in MODEL.glb --check   # exit 0 plain, 3 meshopt
"""

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys

MESHOPT_EXT = "EXT_meshopt_compression"


def glb_json(path):
    """Parse only the GLB header JSON chunk (cheap; no accessor reads,
    so it works on meshopt files that crash the accessor reader)."""
    with open(path, "rb") as f:
        head = f.read(20)
        if len(head) < 20 or head[:4] != b"glTF":
            raise ValueError("not a GLB file")
        jlen = struct.unpack("<I", head[12:16])[0]
        jdat = f.read(jlen)
    return json.loads(jdat)


def is_meshopt_js(js):
    exts = set(js.get("extensionsUsed", [])) | \
        set(js.get("extensionsRequired", []))
    if MESHOPT_EXT in exts:
        return True
    for buf in js.get("buffers", []):
        if MESHOPT_EXT in (buf.get("extensions") or {}):
            return True
    for bv in js.get("bufferViews", []):
        if MESHOPT_EXT in (bv.get("extensions") or {}):
            return True
    return False


def is_meshopt(path):
    return is_meshopt_js(glb_json(path))


def find_gltfpack():
    """gltfpack binary: $WH_GLTFPACK, then the workspace tools install
    (~/workspace/tools/gltfpack/gltfpack), then PATH."""
    env = os.environ.get("WH_GLTFPACK")
    if env and os.path.isfile(env) and os.access(env, os.X_OK):
        return env
    home = os.path.expanduser("~/workspace/tools/gltfpack/gltfpack")
    if os.path.isfile(home) and os.access(home, os.X_OK):
        return home
    return shutil.which("gltfpack")


def decode(path, out_path=None, gltfpack=None, timeout=900):
    """Decode a meshopt GLB to a plain GLB. Returns the output path.
    Raises on tool failure or if the output still carries meshopt."""
    gltfpack = gltfpack or find_gltfpack()
    if not gltfpack:
        raise RuntimeError(
            "gltfpack not found (set WH_GLTFPACK or install to "
            "~/workspace/tools/gltfpack/gltfpack)")
    if out_path is None:
        base, ext = os.path.splitext(path)
        out_path = base + ".decoded" + (ext or ".glb")
    r = subprocess.run([gltfpack, "-i", path, "-o", out_path, "-noq"],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("gltfpack failed on %s: %s" %
                           (path, (r.stderr or r.stdout).strip()[:500]))
    if is_meshopt(out_path):
        raise RuntimeError(
            "gltfpack output still EXT_meshopt_compression: %s" % out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true",
                    help="only report: exit 0 if plain, 3 if meshopt")
    a = ap.parse_args()
    meshopt = is_meshopt(a.inp)
    if a.check:
        print("%s: %s" % (a.inp,
                          "EXT_meshopt_compression" if meshopt else "plain"))
        sys.exit(3 if meshopt else 0)
    if not meshopt:
        print("%s: plain (no decode needed)" % a.inp)
        if a.out and os.path.abspath(a.out) != os.path.abspath(a.inp):
            shutil.copyfile(a.inp, a.out)
            print(a.out)
        sys.exit(0)
    out = decode(a.inp, a.out)
    print(out)
    sys.exit(0)


if __name__ == "__main__":
    main()
