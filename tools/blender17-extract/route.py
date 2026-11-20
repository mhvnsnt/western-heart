#!/usr/bin/env python3
"""Fallback import route for BLENDER17-01 files (worker 80, 2026-10-22).

When the character creation suite / import pipeline sees the 17-byte
BLENDER17-01 header (or a zstd stream mislabeled ".blend"), it routes here
instead of failing at the GLB gate:

    detect -> decompress (zstd) -> extract.extract_blend17 ->
    build GLB (positions + UVs + indices + materials) + sidecars

The GLB is unrigged (the extractor has no skinning yet — weights and the
armature go to JSON sidecars for the rigging stage). Downstream, the normal
auto-rig pipeline (tools/auto_rig/rig_tripo_static.py) can rig it like any
other static.

Usage:
    from route import maybe_route, handle_17xx
    glb = maybe_route(src_path, work_dir)   # GLB path or None
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract as ex


def detect(path):
    return ex.detect(path)


def maybe_route(src, work_dir):
    """If src is a BLENDER17-01 (or zstd-mislabeled) file, extract + build
    GLB into work_dir and return the GLB path. Else return None."""
    kind = detect(src)
    if kind not in ('blend17-01', 'zstd'):
        return None
    return handle_17xx(src, work_dir)['glb']


def handle_17xx(src, work_dir):
    """Full fallback route. Returns dict with glb, sidecars, meshes."""
    os.makedirs(work_dir, exist_ok=True)
    ex_dir = os.path.join(work_dir, 'blend17_extract')
    os.makedirs(ex_dir, exist_ok=True)

    kind = detect(src)
    if kind == 'zstd':
        dec = os.path.join(work_dir, 'decompressed.blend')
        print(f"[blend17-route] zstd detected, decompressing -> {dec}")
        ex.decompress_zstd(src, dec)
        src = dec
    print(f"[blend17-route] extracting {src}")
    n = ex.extract_blend17(src, ex_dir, include_weights=True)
    print(f"[blend17-route] {n} meshes extracted")

    glb_path = os.path.join(work_dir, 'blend17_fallback.glb')
    meshes = build_glb_from_extract(ex_dir, glb_path)
    sidecars = sorted(
        f for f in os.listdir(ex_dir)
        if f.endswith('.json') or f.startswith('armature_'))
    return {'glb': glb_path,
            'extract_dir': ex_dir,
            'meshes': meshes,
            'sidecars': [os.path.join(ex_dir, f) for f in sidecars]}


# --------------------------------------------------------------------------
# Minimal dependency-free GLB writer (positions + uvs + indices + materials)
# --------------------------------------------------------------------------

def _parse_obj(obj_path):
    verts, uvs = [], []
    groups = []  # (matname, faces); faces = [(vids0, vtids0)]
    cur = None

    def new_group(mat):
        g = [mat, []]
        groups.append(g)
        return g

    cur = new_group('default')
    for line in open(obj_path):
        if line.startswith('v '):
            verts.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith('vt '):
            uvs.append(tuple(map(float, line.split()[1:3])))
        elif line.startswith('usemtl '):
            cur = new_group(line.split(None, 1)[1].strip())
        elif line.startswith('f '):
            vids, tids = [], []
            for p in line.split()[1:]:
                parts = p.split('/')
                vids.append(int(parts[0]) - 1)
                tids.append(int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1)
            cur[1].append((vids, tids))
    # drop empty groups
    return verts, uvs, [(m, f) for m, f in groups if f]


def _parse_mtl(mtl_path):
    mats = {}
    cur = None
    if not os.path.exists(mtl_path):
        return mats
    for line in open(mtl_path):
        if line.startswith('newmtl '):
            cur = line.split(None, 1)[1].strip()
            mats[cur] = [0.8, 0.8, 0.8]
        elif line.startswith('Kd ') and cur:
            mats[cur] = list(map(float, line.split()[1:4]))
    return mats


def build_glb_from_extract(ex_dir, glb_path):
    """Build one GLB from an extract_blend17 output dir. Returns mesh names."""
    import math
    objs = sorted(f for f in os.listdir(ex_dir) if f.endswith('.obj'))
    if not objs:
        raise RuntimeError(f"no OBJs in {ex_dir}")

    bin_blob = bytearray()
    meshes_json, nodes_json = [], []
    materials_json, mat_index = [], {}

    def alloc(data_bytes):
        off = len(bin_blob)
        # pad to 4
        bin_blob.extend(data_bytes)
        while len(bin_blob) % 4:
            bin_blob.append(0)
        return off

    accessors, bufferViews = [], []

    def add_accessor(data, comp_type, count, type_str):
        # data: bytes
        bv_off = alloc(data)
        bvi = len(bufferViews)
        bufferViews.append({"buffer": 0, "byteOffset": bv_off,
                            "byteLength": len(data)})
        acc_i = len(accessors)
        accessors.append({"bufferView": bvi, "componentType": comp_type,
                          "count": count, "type": type_str})
        return acc_i

    for oi, obj in enumerate(objs):
        obj_path = os.path.join(ex_dir, obj)
        mtl_path = os.path.splitext(obj_path)[0] + '.mtl'
        verts, uvs, groups = _parse_obj(obj_path)
        mtl_colors = _parse_mtl(mtl_path)
        if not verts:
            continue
        # per-group triangulation (fan) with per-group vertex compaction
        prims = []
        for matname, faces in groups:
            # compact vertices used by this group
            vmap,parr, narr = {}, [], []
            idx = []
            for vids, tids in faces:
                tri = []
                for k in range(1, len(vids) - 1):
                    for j in (0, k, k + 1):
                        key = (vids[j], tids[j])
                        if key not in vmap:
                            vmap[key] = len(parr)
                            parr.append(verts[vids[j]])
                            narr.append(uvs[tids[j]] if tids[j] >= 0 and uvs else (0.0, 0.0))
                        tri.append(vmap[key])
                idx.extend(tri)
            if not idx:
                continue
            pos_bytes = struct.pack(f'<{len(parr)*3}f',
                                    *[c for p in parr for c in p])
            uv_bytes = struct.pack(f'<{len(narr)*2}f',
                                   *[c for p in narr for c in p])
            idx_bytes = struct.pack(f'<{len(idx)}I', *idx)
            p_acc = add_accessor(pos_bytes, 5126, len(parr), "VEC3")
            t_acc = add_accessor(uv_bytes, 5126, len(narr), "VEC2")
            i_acc = add_accessor(idx_bytes, 5125, len(idx), "SCALAR")
            if matname not in mat_index:
                col = mtl_colors.get(matname, [0.8, 0.8, 0.8])
                mat_index[matname] = len(materials_json)
                materials_json.append({
                    "name": matname,
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [col[0], col[1], col[2], 1.0],
                        "metallicFactor": 0.0, "roughnessFactor": 0.8}})
            prims.append({"attributes": {"POSITION": p_acc, "TEXCOORD_0": t_acc},
                          "indices": i_acc,
                          "material": mat_index[matname]})
        if not prims:
            continue
        meshes_json.append({"name": os.path.splitext(obj)[0],
                            "primitives": prims})
        nodes_json.append({"mesh": len(meshes_json) - 1,
                           "name": os.path.splitext(obj)[0]})

    gltf = {
        "asset": {"version": "2.0",
                  "generator": "western-heart blend17-extract route.py"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes_json)))}],
        "nodes": nodes_json,
        "meshes": meshes_json,
        "materials": materials_json,
        "accessors": accessors,
        "bufferViews": bufferViews,
        "buffers": [{"byteLength": len(bin_blob)}],
    }
    json_bytes = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    while len(json_bytes) % 4:
        json_bytes += b' '
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_blob)
    with open(glb_path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))  # glTF
        f.write(struct.pack('<II', len(json_bytes), 0x4E4F534A))  # JSON
        f.write(json_bytes)
        f.write(struct.pack('<II', len(bin_blob), 0x004E4942))  # BIN
        f.write(bin_blob)
    print(f"[blend17-route] wrote {glb_path} "
          f"({len(meshes_json)} meshes, {len(bin_blob)} bin bytes)")
    return [m["name"] for m in meshes_json]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.blend> <work_dir>")
        sys.exit(1)
    r = handle_17xx(sys.argv[1], sys.argv[2])
    print("GLB:", r['glb'])
