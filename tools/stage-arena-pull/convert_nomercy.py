#!/usr/bin/env python3
"""WWF No Mercy arena assemblies -> game-ready GLB.

Reads teardown/wwf-no-mercy/arenas/<name>.obj (+ sidecar <name>.vc with
per-vertex RGB 0-255, one "r g b" line per vertex) and writes
game/assets/stages/nomercy/<name>.glb.

- One GLTF mesh per OBJ `g` group (group name preserved as mesh name so the
  reskin pipeline can target pieces, e.g. Titan_Tron, Ring_Mat).
- Flat (per-face) normals -> authentic N64 hard-surface look.
- Vertex colors from the .vc sidecar (COLOR_0, linear 0-1).
- UVs preserved (TEXCOORD_0) for the future texture-pairing lane.
- Uniform world scale: 0.007 (ring mat 1040 units -> 7.28 m).
- Y offset: the fighting surface (largest-area near-horizontal level in the
  upper half of the model) is translated to y=0 so fighters spawn on it.

Usage:
    python3 convert_nomercy.py <arenas_dir> <out_dir>
Default arenas_dir reads from the git object store via `git show`
(see --git-ref) so no working-tree checkout of teardown/ is needed.
"""
import argparse
import json
import os
import struct
import subprocess
import sys

import numpy as np

SCALE = 0.007  # N64 units -> meters (ring mat 1040u ~= 7.28m)

ARENAS = [
    "arena_raw", "arena_smackdown", "arena_royal_rumble", "arena_wrestlemania",
    "arena_king_of_the_ring", "arena_summerslam", "arena_survivor_series",
    "arena_backlash", "arena_armageddon", "arena_no_mercy", "arena_cage",
    "backstage_bar_lounge", "backstage_boiler_room", "backstage_hallway",
    "backstage_locker_room", "backstage_parking_lot", "lobby",
]

# Groups dropped from ring arenas: the ROM stores these as local templates
# (no placement data) or with junk coordinates — see
# teardown/wwf-no-mercy/arenas/ARENAS.md caveat 2. Ropes never existed in the
# ROM (procedural at runtime); the game builder re-adds posts+ropes.
import re as _re
DROP_RES = [_re.compile(p, _re.I) for p in
            (r"ring_step", r"ring_post", r"turnbuckle", r"apron",
             r"cage_piece", r"announce_table", r"ladder_match")]
RING_ARENAS = {n for n in ARENAS if n.startswith("arena_")}


def keep_group(arena, gname):
    if arena in RING_ARENAS and any(p.search(gname) for p in DROP_RES):
        return False
    return True


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, check=True)
    return r.stdout


def parse_obj(text):
    """Return (verts Nx3, uvs Nx2, groups=[(name, [(vi,vti)...] tris)])."""
    verts, uvs = [], []
    groups, cur = [], None
    for line in text.splitlines():
        if not line or line[0] == "#":
            continue
        if line.startswith("g "):
            cur = (line[2:].strip(), [])
            groups.append(cur)
        elif line.startswith("v "):
            p = line.split()
            verts.append((float(p[1]), float(p[2]), float(p[3])))
        elif line.startswith("vt"):
            p = line.split()
            uvs.append((float(p[1]), float(p[2])))
        elif line.startswith("f "):
            assert cur is not None, "face before any group"
            tri = []
            for tok in line.split()[1:]:
                vi, vti = tok.split("/")[:2]
                tri.append((int(vi) - 1, int(vti) - 1 if vti else -1))
            assert len(tri) == 3, f"non-triangle face: {line[:60]}"
            cur[1].append(tri)
    return np.array(verts, np.float32), np.array(uvs, np.float32), groups


def fighting_surface_y(verts, groups):
    """Y (pre-scale) of the fighting surface -> translated to y=0.

    Name-driven first (ring mat / room floor groups are labeled), because
    some template pieces (ring steps, titan tron) carry junk coordinates
    with huge bogus areas (see teardown ARENAS.md caveat 2).
    """
    lname = [(g[0].lower(), g[1]) for g in groups]

    def group_max_y(pred):
        best = None
        for name, tris in lname:
            if pred(name) and tris:
                ys = verts[[t[0] for tri in tris for t in tri]][:, 1]
                top = float(ys.max())
                if best is None or top > best:
                    best = top
        return best

    y = group_max_y(lambda n: "ring_mat" in n)
    if y is not None:
        return y
    y = group_max_y(lambda n: "_floor" in n and "floormat" not in n
                    and "outside" not in n)
    if y is not None:
        return y
    # Fallback: largest-area near-horizontal level below the 70th %ile of y.
    levels = {}
    for _, tris in groups:
        for tri in tris:
            p = verts[[t[0] for t in tri]]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            area = 0.5 * np.linalg.norm(n)
            if area == 0:
                continue
            n /= (2 * area)
            if abs(n[1]) > 0.9:  # near-horizontal
                key = round(float(p[:, 1].mean()) / 10.0) * 10.0
                levels[key] = levels.get(key, 0.0) + area
    if not levels:
        return float(verts[:, 1].min())
    cap = np.percentile(list(levels), 70)
    cands = {k: v for k, v in levels.items() if k <= cap}
    return max(cands, key=lambda k: cands[k])


def write_glb(path, prims):
    """prims: list of dicts {name, pos (N,3) f32, nrm (N,3) f32,
    col (N,3) f32, uv (N,2) f32}. Non-indexed triangles."""
    blob = bytearray()
    meshes, accessors, bvs = [], [], []

    def add_acc(data, ctype, count, mn, mx):
        off = len(blob)
        blob.extend(data.tobytes())
        while len(blob) % 4:
            blob.append(0)
        accessors.append({
            "bufferView": len(bvs), "componentType": ctype,
            "count": count, "type": {"SCALAR": "SCALAR", "VEC2": "VEC2",
                                    "VEC3": "VEC3"}["VEC3" if data.shape[1] == 3
                                                    else "VEC2"],
            "min": mn, "max": mx})
        bvs.append({"buffer": 0, "byteOffset": off,
                    "byteLength": len(data.tobytes())})
        return len(accessors) - 1

    for prim in prims:
        n = len(prim["pos"])
        i_p = add_acc(prim["pos"].astype("<f4"), 5126, n,
                      prim["pos"].min(0).tolist(), prim["pos"].max(0).tolist())
        i_n = add_acc(prim["nrm"].astype("<f4"), 5126, n,
                      prim["nrm"].min(0).tolist(), prim["nrm"].max(0).tolist())
        attrs = {"POSITION": i_p, "NORMAL": i_n}
        if prim.get("col") is not None:
            i_c = add_acc(prim["col"].astype("<f4"), 5126, n,
                          prim["col"].min(0).tolist(), prim["col"].max(0).tolist())
            attrs["COLOR_0"] = i_c
        if prim.get("uv") is not None:
            i_t = add_acc(prim["uv"].astype("<f4"), 5126, n,
                          prim["uv"].min(0).tolist(), prim["uv"].max(0).tolist())
            attrs["TEXCOORD_0"] = i_t
        meshes.append({"name": prim["name"],
                       "primitives": [{"attributes": attrs,
                                       "material": 0, "mode": 4}]})

    gltf = {
        "asset": {"version": "2.0",
                  "generator": "wh-stage-arena-pull convert_nomercy.py"},
        "scene": 0, "scenes": [{"nodes": list(range(len(meshes)))}],
        "nodes": [{"mesh": i, "name": m["name"]} for i, m in enumerate(meshes)],
        "meshes": meshes,
        "materials": [{"name": "nomercy_vc",
                       "pbrMetallicRoughness": {
                           "baseColorFactor": [1, 1, 1, 1],
                           "metallicFactor": 0.0, "roughnessFactor": 0.92},
                       "vertexColor": True}],
        "accessors": accessors, "bufferViews": bvs,
        "buffers": [{"byteLength": len(blob)}],
    }
    # wire bufferView->buffer
    js = json.dumps(gltf, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)


def convert(name, obj_bytes, vc_bytes):
    verts, uvs, groups = parse_obj(obj_bytes.decode("utf-8", "replace"))
    groups = [(g, t) for g, t in groups if keep_group(name, g)]
    vc_lines = vc_bytes.decode().split()
    assert len(vc_lines) == 3 * len(verts), \
        f"{name}: vc count {len(vc_lines)//3} != verts {len(verts)}"
    vcol = (np.array(vc_lines, np.float32).reshape(-1, 3) / 255.0)
    y_floor = fighting_surface_y(verts, groups)

    prims = []
    for gname, tris in groups:
        if not tris:
            continue
        idx = np.array([[t[k][0] for k in range(3)] for t in tris])
        uv_idx = np.array([[t[k][1] for k in range(3)] for t in tris])
        p = verts[idx.reshape(-1)].reshape(-1, 3, 3)
        e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
        n = np.cross(e1, e2)
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        n = (n / ln)[:, None, :].repeat(3, axis=1).reshape(-1, 3)
        pos = (p.reshape(-1, 3) - np.array([0, y_floor, 0], np.float32)) * SCALE
        col = vcol[idx.reshape(-1)]
        uv = None
        if len(uvs) and (uv_idx >= 0).all():
            uv = uvs[uv_idx.reshape(-1)]
        prims.append({"name": gname, "pos": pos.astype(np.float32),
                      "nrm": n.astype(np.float32), "col": col.astype(np.float32),
                      "uv": uv.astype(np.float32) if uv is not None else None})
    return prims, y_floor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="origin/main")
    ap.add_argument("--arenas-dir", default=None,
                    help="read .obj/.vc from disk instead of git")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--only", default=None, help="comma-separated arena names")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    names = args.only.split(",") if args.only else ARENAS
    manifest = {}
    for name in names:
        if args.arenas_dir:
            with open(os.path.join(args.arenas_dir, name + ".obj"), "rb") as f:
                obj_b = f.read()
            with open(os.path.join(args.arenas_dir, name + ".vc"), "rb") as f:
                vc_b = f.read()
        else:
            obj_b = git_show(args.git_ref, f"teardown/wwf-no-mercy/arenas/{name}.obj")
            vc_b = git_show(args.git_ref, f"teardown/wwf-no-mercy/arenas/{name}.vc")
        prims, y_floor = convert(name, obj_b, vc_b)
        out = os.path.join(args.out_dir, name + ".glb")
        write_glb(out, prims)
        ntri = sum(len(p["pos"]) // 3 for p in prims)
        manifest[name] = {
            "glb": os.path.basename(out),
            "bytes": os.path.getsize(out),
            "groups": len(prims),
            "tris": ntri,
            "y_floor_units": y_floor,
            "scale": SCALE,
        }
        print(f"{name}: {len(prims)} groups, {ntri} tris, "
              f"{os.path.getsize(out)} bytes -> {out}")
    with open(os.path.join(args.out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("wrote manifest.json")


if __name__ == "__main__":
    main()
