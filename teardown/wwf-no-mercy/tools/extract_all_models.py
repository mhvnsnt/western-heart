#!/usr/bin/env python3
"""Bulk-extract WWF No Mercy AkiModel meshes to Wavefront OBJ.

Source: WWF No Mercy (USA) (Rev-A).z64
FileTable @0x16C31D8, FirstFile @0x1BD150 (= VPWStudio NoMercy_NTSC_U_11).
Model list: every file labeled AkiModel in VPWStudio's FileTableDB
(NoMercy.txt, MIT) — 3,586 meshes.

AkiModel format (VPWStudio DataStructures/AKI/AkiModel.cs):
  u8 Scale, u8 numVerts (bit7 = model type), u8 numFaces (bit7 = ?),
  u8 VertexInfluence, s8 OffsetX/Y/Z, u8 TextureSize (nibbles *8),
  then numVerts x AkiVertex (s8 X/Y/Z, u8 U/V, u8 R/G/B = 8 bytes),
  then numFaces x AkiFace (u8 v1/v2/v3).

OBJ export: v (x+offx)*(scale+1) etc. (per VPWStudio WriteWavefrontObj),
vt u,v normalized by TextureSize nibbles (x8), f v/vt.
Vertex colors are preserved in a sidecar .vc file (r g b per vertex)
since OBJ has no official vertex-color support.

Output:
  <outdir>/<category>/model_XXXX.obj (+ .vc), category from DB [bracket]
  <outdir>/manifest.json  (file_id, label, category, nverts, nfaces,
                           scale, offsets, valid)

Usage: extract_all_models.py <filedb.txt> <outdir>
"""
import json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anim_extract import FileTable
from lzss import asmik_decode  # shared decoder module

ROM = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'WWF No Mercy (USA) (Rev-A).z64')

def s8(v):
    return v - 0x100 if v & 0x80 else v

def parse_model(dec):
    if len(dec) < 8:
        return None
    scale = dec[0]
    nv = dec[1] & 0x7F
    model_type = dec[1] & 0x80
    nf = dec[2] & 0x7F
    vinf = dec[3]
    ox, oy, oz = s8(dec[4]), s8(dec[5]), s8(dec[6])
    tsize = dec[7]
    tsx = ((tsize & 0xF0) >> 4) * 8 or 64
    tsy = (tsize & 0x0F) * 8 or 64
    expect = 8 + nv * 8 + nf * 3
    # some files have a single trailing 0x00 pad byte
    if expect != len(dec) and not (expect == len(dec) - 1 and dec[-1] == 0):
        return None
    verts = []
    o = 8
    for _ in range(nv):
        x, y, z = s8(dec[o]), s8(dec[o + 1]), s8(dec[o + 2])
        u, vv = dec[o + 3], dec[o + 4]
        r, g, b = dec[o + 5], dec[o + 6], dec[o + 7]
        verts.append((x, y, z, u, vv, r, g, b))
        o += 8
    faces = []
    for _ in range(nf):
        faces.append((dec[o], dec[o + 1], dec[o + 2]))
        o += 3
    return {"scale": scale, "nverts": nv, "nfaces": nf,
            "model_type": model_type, "vinf": vinf,
            "offset": [ox, oy, oz], "texsize": [tsx, tsy],
            "verts": verts, "faces": faces}

def write_obj(path, m):
    s1 = m["scale"] + 1
    ox, oy, oz = m["offset"]
    tsx, tsy = m["texsize"]
    with open(path, 'w') as f:
        f.write(f"# WWF No Mercy AkiModel exported by extract_all_models.py\n")
        f.write(f"# scale={m['scale']} vinf={m['vinf']} model_type={m['model_type']:02x}\n")
        for (x, y, z, u, vv, r, g, b) in m["verts"]:
            f.write(f"v {(x + ox) * s1} {(y + oy) * s1} {(z + oz) * s1}\n")
        for (x, y, z, u, vv, r, g, b) in m["verts"]:
            f.write(f"vt {u / tsx:.6f} {1.0 - vv / tsy:.6f}\n")
        for (a, b, c) in m["faces"]:
            # OBJ indices are 1-based; guard against out-of-range refs
            nv = m["nverts"]
            if a < nv and b < nv and c < nv:
                f.write(f"f {a + 1}/{a + 1} {b + 1}/{b + 1} {c + 1}/{c + 1}\n")
    with open(path[:-4] + '.vc', 'w') as f:
        for (x, y, z, u, vv, r, g, b) in m["verts"]:
            f.write(f"{r} {g} {b}\n")

def load_db(path):
    models = {}
    for l in open(path):
        s = l.strip()
        if not s or s.startswith('#'):
            continue
        m = re.match(r'(?:\d+:)?([0-9A-Fa-f]{2,})=AkiModel;(.*)$', s)
        if m:
            models[int(m.group(1), 16)] = m.group(2).strip()
    return models

def category_of(label):
    m = re.match(r'\[([^\]]*)\]', label)
    if not m:
        return 'unlabeled'
    c = m.group(1).strip().lower().replace(' ', '_')
    return c or 'unlabeled'

def main():
    db_path, outdir = sys.argv[1], sys.argv[2]
    models = load_db(db_path)
    data = open(ROM, 'rb').read()
    ft = FileTable(data)
    manifest = {"models": [], "unparseable": []}
    n_ok = 0
    for fid in sorted(models):
        label = models[fid]
        cat = category_of(label)
        raw, enc = ft.get(fid)
        dec = asmik_decode(raw) if enc else raw
        m = parse_model(dec)
        sub = os.path.join(outdir, cat)
        os.makedirs(sub, exist_ok=True)
        if m is None:
            manifest["unparseable"].append({"file_id": hex(fid),
                                            "label": label,
                                            "declen": len(dec)})
            continue
        fn = f"model_{fid:04X}.obj"
        write_obj(os.path.join(sub, fn), m)
        n_ok += 1
        manifest["models"].append({
            "file": f"{cat}/{fn}", "file_id": hex(fid), "label": label,
            "nverts": m["nverts"], "nfaces": m["nfaces"],
            "scale": m["scale"], "offset": m["offset"],
            "model_type": hex(m["model_type"]),
        })
    json.dump(manifest, open(os.path.join(outdir, 'manifest.json'), 'w'), indent=1)
    print(f"exported {n_ok} models, {len(manifest['unparseable'])} unparseable")

if __name__ == '__main__':
    main()
