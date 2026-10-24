#!/usr/bin/env python3
"""Unit tests for render-prep: synthetic GLBs with known defects must be
caught; a clean GLB must pass. No network, no Blender, no large files."""
import importlib.util
import io
import json
import os
import struct
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "render_prep", os.path.join(_here, "render-prep.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
validate_bytes = _mod.validate_bytes

try:
    from PIL import Image
except ImportError:
    print("Pillow required for tests"); sys.exit(1)


def _jpeg(w=8, h=8, color=(200, 30, 30)):
    im = Image.new("RGB", (w, h), color)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def _glb(json_dict, bin_data):
    js = json.dumps(json_dict).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    binp = bin_data + b"\x00" * ((4 - len(bin_data) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(binp)
    return (b"glTF" + struct.pack("<II", 2, total)
            + struct.pack("<I4s", len(js), b"JSON") + js
            + struct.pack("<I4s", len(binp), b"BIN\x00") + binp)


def _tri_mesh(positions, tex_bytes=None, bounds=None):
    pos = b"".join(struct.pack("<3f", *p) for p in positions)
    idx = struct.pack("<3H", 0, 1, 2)
    bin_data = pos + idx + (tex_bytes or b"")
    js = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(bin_data)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos), "target": 34962},
            {"buffer": 0, "byteOffset": len(pos), "byteLength": len(idx), "target": 34963},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions),
             "type": "VEC3", "min": bounds[0], "max": bounds[1]},
            {"bufferView": 1, "componentType": 5123, "count": 3,
             "type": "SCALAR"},
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0},
                                     "indices": 1}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    if tex_bytes is not None:
        js["bufferViews"].append(
            {"buffer": 0, "byteOffset": len(pos) + len(idx),
             "byteLength": len(tex_bytes)})
        js["images"] = [{"name": "albedo", "mimeType": "image/jpeg",
                         "bufferView": 2}]
    return _glb(js, bin_data)


def good():
    return _tri_mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                     tex_bytes=_jpeg(),
                     bounds=([0, 0, 0], [1, 1, 0]))


def truncated_jpeg():
    full = _jpeg()
    return _tri_mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                     tex_bytes=full[:-40],  # chopped: EOI marker gone
                     bounds=([0, 0, 0], [1, 1, 0]))


def bad_magic_jpeg():
    full = _jpeg()
    return _tri_mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                     tex_bytes=b"NOTAJPEG" + full[8:],
                     bounds=([0, 0, 0], [1, 1, 0]))


def garbage_bounds():
    return _tri_mesh([(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                     tex_bytes=_jpeg(),
                     bounds=([-3.4028235e38] * 3, [3.4028235e38] * 3))


def nan_bytes():
    return _tri_mesh([(float("nan"), 0, 0), (1, 0, 0), (0, 1, 0)],
                     tex_bytes=_jpeg(),
                     bounds=([0, 0, 0], [1, 1, 0]))


CASES = [
    ("good", good(), True),
    ("truncated-jpeg", truncated_jpeg(), False),
    ("bad-magic-jpeg", bad_magic_jpeg(), False),
    ("garbage-bounds", garbage_bounds(), False),
    ("nan-bytes", nan_bytes(), False),
]

if __name__ == "__main__":
    failures = 0
    for name, data, want_ok in CASES:
        rep = validate_bytes(data, f"<synthetic:{name}>")
        got_ok = rep.ok
        status = "PASS" if got_ok == want_ok else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"[{status}] {name}: expected ok={want_ok}, got ok={got_ok}")
        if got_ok != want_ok:
            for e in rep.errors:
                print(f"       {e}")
        elif not want_ok and not rep.errors:
            print("       (no error reported for a bad case!)")
            failures += 1
    print("ALL TESTS PASSED" if failures == 0 else f"{failures} TEST FAILURES")
    sys.exit(1 if failures else 0)
