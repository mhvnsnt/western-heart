#!/usr/bin/env python3
"""Merge Wolf's missing head (kao/face) into the body OBJ.

VF5 PS3 splits per-fighter geometry across itm*.obj.bin files with TWO
different vertex-header layouts:

1. "chunk table" layout (e.g. wolitm000): u32 chunk count @+0x04, chunk
   bases @+0x40+i*4, vertex header at chunk_base+0x54 with
   vcount @+0x20, pos_rel @+0x24, end_rel @+0x28.
   -> handled by tools/vf5/vf5extract.py

2. "bare header" layout (e.g. wolitm001): header structs start ~0x94;
   each header has vcount @+0x20, pos_rel @+0x24, end_rel @+0x28 with
   pos buffer at header+pos_rel. Vertex coords are in the SAME model
   space as the body. Index strips are u16 runs located elsewhere in
   the file (scan for runs with max < vcount).

Wolf's itm000 (body) contains NO face geometry -- only an eye band
(chunk1, 168 verts). His kao (face) mesh is in wolitm001:
  verts: 928 @ file+0x558 (header @0x94: vc=928, pos_rel=0x4c4)
  indices: u16 strip @ 0x12704, 2322 entries, max 927

Usage: merge_wol_head.py <body.obj> <out.obj>
Appends the face verts/faces to the body OBJ (index-shifted).
"""
import struct
import sys

import os
SRC = os.environ.get("VF5_WOLITM001",
                     os.path.expanduser("~/workspace/vf5-work/extracted/wolitm/wolitm001_obj.bin"))


def main():
    body_path, out_path = sys.argv[1], sys.argv[2]
    d = open(SRC, "rb").read()
    assert struct.unpack("<I", d[:4])[0] == 0x05062500, "bad magic"

    vbase = 0x558
    vc_full = 928
    verts_all = [struct.unpack("<3f", d[vbase + v * 12:vbase + v * 12 + 12])
                 for v in range(vc_full)]
    # Last 7 verts (indices 921-927) are NOT face geometry -- stray verts
    # near the hip (x ~-0.8, y ~0.35); keeping them stretches giant
    # triangles across the render. Drop them.
    keep = list(range(921))
    remap = {old: new for new, old in enumerate(keep)}
    verts = [verts_all[v] for v in keep]
    vc = len(keep)
    ib, ilen = 0x12704, 2322
    idx = list(struct.unpack("<%dH" % ilen, d[ib:ib + ilen * 2]))

    def strip_to_tris(idxs):
        tris = []
        for i in range(len(idxs) - 2):
            a, b, c = idxs[i], idxs[i + 1], idxs[i + 2]
            if a == b or b == c or a == c:
                continue
            tris.append((a, b, c) if i % 2 == 0 else (b, a, c))
        return tris

    tris = [t for t in strip_to_tris([v for v in idx if v < vc_full])
            if all(v < 921 for v in t)]
    tris = [[remap[v] for v in t] for t in tris]
    print(f"face: {vc} verts, {len(tris)} tris (7 stray verts dropped)")

    body = open(body_path).read().rstrip("\n").split("\n")
    nv = sum(1 for l in body if l.startswith("v "))
    out = body + ["g face"]
    for x, y, z in verts:
        out.append(f"v {x:.6f} {y:.6f} {z:.6f}")
    for a, b, c in tris:
        out.append(f"f {a + nv + 1} {b + nv + 1} {c + nv + 1}")
    open(out_path, "w").write("\n".join(out) + "\n")
    print(f"merged: body {nv} verts + face {vc} verts -> {out_path}")


if __name__ == "__main__":
    main()
