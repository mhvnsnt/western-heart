#!/usr/bin/env python3
"""Stage reskin pipeline (Stream 3 arena pull).

Recolor variants of a stage GLB without touching the original:
  1. vertex-color tint  — multiply COLOR_0 by a palette (e.g. night/sunset)
  2. group recolor      — override COLOR_0 for named groups (e.g. Titan_Tron)
  3. material override  — emit a JSON sidecar the game can apply at load

The originals always ship; variants are additive files:
  game/assets/stages/nomercy/arena_raw.night.glb

Usage:
  python3 reskin_stage.py <in.glb> <out.glb> --tint 0.6,0.7,1.0
  python3 reskin_stage.py <in.glb> <out.glb> --group-color Titan_Tron=1,0.2,0.2
  python3 reskin_stage.py <in.glb> <out.glb> --preset night
Presets: night, sunset, bloodmoon, ultraviolet.
"""
import argparse
import json
import struct
import sys

PRESETS = {
    "night":      {"tint": (0.45, 0.55, 0.9)},
    "sunset":     {"tint": (1.0, 0.55, 0.35)},
    "bloodmoon":  {"tint": (1.0, 0.25, 0.3)},
    "ultraviolet": {"tint": (0.7, 0.3, 1.0)},
}


def read_glb(path):
    d = open(path, "rb").read()
    magic, ver, total = struct.unpack("<III", d[:12])
    assert magic == 0x46546C67, "not a GLB"
    jl, jt = struct.unpack("<II", d[12:20])
    assert jt == 0x4E4F534A
    js = json.loads(d[20:20 + jl])
    bl, bt = struct.unpack("<II", d[20 + jl:28 + jl])
    assert bt == 0x004E4942
    blob = d[28 + jl:28 + jl + bl]
    return js, blob


def main():
    import numpy as np
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("outp")
    ap.add_argument("--tint", default=None, help="r,g,b multiplier")
    ap.add_argument("--group-color", action="append", default=[],
                    help="SUBSTR=r,g,b (repeatable)")
    ap.add_argument("--preset", default=None, choices=list(PRESETS))
    args = ap.parse_args()

    tint = None
    if args.preset:
        tint = PRESETS[args.preset]["tint"]
    if args.tint:
        tint = tuple(float(x) for x in args.tint.split(","))
    group_colors = {}
    for gc in args.group_color:
        sub, rgb = gc.split("=")
        group_colors[sub.lower()] = tuple(float(x) for x in rgb.split(","))

    js, blob = read_glb(args.inp)
    blob = bytearray(blob)
    for m in js["meshes"]:
        for prim in m["primitives"]:
            ci = prim["attributes"].get("COLOR_0")
            if ci is None:
                continue
            import numpy as _np
            col = _np.frombuffer(blob, dtype="<f4",
                                 count=js["accessors"][ci]["count"] * 3,
                                 offset=js["bufferViews"][
                                     js["accessors"][ci]["bufferView"]
                                 ].get("byteOffset", 0)).reshape(-1, 3).copy()
            name = m.get("name", "").lower()
            applied = False
            for sub, rgb in group_colors.items():
                if sub in name:
                    col[:] = _np.array(rgb, dtype=_np.float32)
                    applied = True
            if tint and not applied:
                col *= _np.array(tint, dtype=_np.float32)
            _np.clip(col, 0, 1, out=col)
            a = js["accessors"][ci]
            off = js["bufferViews"][a["bufferView"]].get("byteOffset", 0)
            blob[off:off + col.nbytes] = col.astype("<f4").tobytes()
    blob = bytes(blob)
    js_s = json.dumps(js, separators=(",", ":")).encode()
    while len(js_s) % 4:
        js_s += b" "
    total = 12 + 8 + len(js_s) + 8 + len(blob)
    with open(args.outp, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js_s), 0x4E4F534A))
        f.write(js_s)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)
    print(f"reskinned {args.inp} -> {args.outp} "
          f"(tint={tint}, group_colors={list(group_colors)})")


if __name__ == "__main__":
    main()
