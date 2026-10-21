#!/usr/bin/env python3
"""tools/auto_rig/validate.py — the playable gate for auto-rigged models.

A model ships into game/js/assets.js MODEL_URLS only if ALL of these hold:
  1. valid glTF 2.0 parse
  2. >= 1 skinned mesh (mesh with JOINTS_0 + skin)
  3. required Mixamo-style bones present (see backends/retarget.py)
  4. height 1.5 - 2.2 m (feet at y=0, head top in range)
  5. p99.9 triangle-edge stretch < 2.5 on the standard clips (when provided)

Usage:
    python3 validate.py --in MODEL.glb [--clips CLIPS_DIR] [--json-out R.json]
Exit 0 = pass, 1 = fail. Always writes a JSON report to stdout.
"""

import argparse
import json
import os
import struct
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from backends.retarget import canonicalize, gate_bones  # noqa: E402


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        raise ValueError("not a GLB file")
    jlen = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    boff = 20 + jlen
    blen = 0
    if len(data) > boff + 8 and data[boff + 4:boff + 8] == b"BIN\x00":
        blen = struct.unpack("<I", data[boff:boff + 4])[0]
        bdat = data[boff + 8:boff + 8 + blen]
    else:
        bdat = b""
    return js, bdat


def joint_names(js):
    skins = js.get("skins", [])
    if not skins:
        return []
    joints = skins[0].get("joints", [])
    nodes = js.get("nodes", [])
    return [nodes[j].get("name", "") for j in joints if j < len(nodes)]


def mesh_height(js, bdat):
    """Height from POSITION vertex data (accessor min/max not trusted —
    Blender's exporter sometimes writes zeroed bounds), aggregated over
    EVERY primitive of EVERY mesh. Measuring only meshes[0] under-reads
    multi-part models (e.g. SFMLab-style part exports whose torso primitive
    spans y 0.93-1.72 while the full figure spans 0-1.8) and false-fails
    them at this gate — pose-isolation lane, 2026-10-21."""
    try:
        import numpy as np
        mn_y = None
        mx_y = None
        for m in js.get("meshes", []):
            for prim in m.get("primitives", []):
                attrs = prim.get("attributes", {})
                if "POSITION" not in attrs:
                    continue
                acc = js["accessors"][attrs["POSITION"]]
                if acc.get("componentType") != 5126:  # float32 only
                    continue
                bv = js["bufferViews"][acc["bufferView"]]
                off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
                n = acc["count"]
                stride = bv.get("byteStride", 12)
                if stride == 12:
                    arr = np.frombuffer(bdat, dtype=np.float32, count=n * 3,
                                        offset=off).reshape(n, 3)
                    ys = arr[:, 1]
                else:
                    ys = np.empty(n, dtype=np.float32)
                    for i in range(n):
                        ys[i] = np.frombuffer(
                            bdat, dtype=np.float32, count=3,
                            offset=off + i * stride)[1]
                lo, hi = float(ys.min()), float(ys.max())
                mn_y = lo if mn_y is None else min(mn_y, lo)
                mx_y = hi if mx_y is None else max(mx_y, hi)
        if mn_y is None:
            return None, None
        return mx_y - mn_y, mn_y
    except (KeyError, IndexError, ImportError):
        return None, None


def check(path, clips_dir=None):
    report = {"file": path, "checks": {}, "pass": False}
    try:
        js, bdat = read_glb(path)
    except Exception as e:  # noqa: BLE001
        report["error"] = str(e)
        return report

    # 1. valid glTF
    report["checks"]["valid_gltf"] = True

    # 2. skinned mesh present
    skinned = any(
        "JOINTS_0" in p.get("attributes", "")
        for m in js.get("meshes", []) for p in m.get("primitives", [])
    ) and bool(js.get("skins"))
    report["checks"]["skinned_mesh"] = skinned

    # 3. canonical bones
    names = joint_names(js)
    mapping, unmapped = canonicalize(names)
    missing = gate_bones(mapping.values())
    report["checks"]["bones_present"] = len(missing) == 0
    report["missing_bones"] = missing
    report["unmapped_bones"] = unmapped[:20]

    # 4. height
    height, foot_y = mesh_height(js, bdat)
    report["height_m"] = round(height, 3) if height else None
    report["checks"]["height_ok"] = height is not None and 1.5 <= height <= 2.2
    report["foot_y"] = round(foot_y, 4) if foot_y is not None else None

    # 5. stretch gate: implemented by anim_check.py (bone-length variance,
    #    vertex tearing, p99.9 edge stretch) over the supplied clips GLB(s);
    #    without clips we report unknown, not fail.
    if clips_dir:
        import glob as _glob
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "anim_check", os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "anim_check.py"))
        _ac = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_ac)
        clip_files = sorted(_glob.glob(os.path.join(clips_dir, "*.glb")))
        clip_files = clip_files or [clips_dir]
        clip_reps = {}
        all_ok = bool(clip_files)
        for cf in clip_files:
            class _A:  # anim_check thresholds = the gate defaults
                bone_var, tear_m, tear_k, edge_max, root_max, max_frames = \
                    0.02, 0.35, 8.0, 2.5, 1.0, 120
            try:
                _m = _ac.AnimModel(cf)
                for _anim in _m.js.get("animations", []):
                    _r = _ac.check_animation(_m, _anim, _A())
                    clip_reps[f"{os.path.basename(cf)}:{_anim.get('name', '?')}"] = {
                        "pass": _r["pass"], "failures": _r["failures"],
                        "edge_stretch_p999": _r.get("edge_stretch_p999"),
                        "bones_flagged": len(_r.get("bones_flagged") or [])}
                    all_ok = all_ok and _r["pass"]
            except Exception as e:  # noqa: BLE001
                clip_reps[os.path.basename(cf)] = {"pass": False,
                                                  "error": str(e)}
                all_ok = False
        report["clips"] = clip_reps
        report["checks"]["stretch_ok"] = all_ok
    else:
        report["checks"]["stretch_ok"] = "unknown (no clips supplied)"

    report["pass"] = all(v is True for v in report["checks"].values()
                         if v != "unknown (no clips supplied)")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--clips", default=None,
                    help="dir of animation GLBs (or one GLB) for the stretch gate")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    rep = check(a.inp, clips_dir=a.clips)
    out = json.dumps(rep, indent=2)
    print(out)
    if a.json_out:
        open(a.json_out, "w").write(out)
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
