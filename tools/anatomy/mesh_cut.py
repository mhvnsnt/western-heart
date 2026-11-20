#!/usr/bin/env python3
"""Runtime mesh bisection for dissectible anatomy (Open3D backend).

Cuts a triangle mesh along a plane -> two sealed solids -> assigns
sub-materials (BONE core / MUSCLE / FAT / SKIN) on the cut faces by radial
distance from a bone centerline -> exports a GLB with one primitive per
(layer, side) so the game can toggle layers (X-ray, dissection views).

Pipeline per cut plane:
  1. boolean split with Open3D tensor geometry: the mesh is intersected
     with an oversized half-space box on each side of the plane. Boolean
     ops seal the cut faces automatically (closed solids out).
  2. cut-face detection: faces ~coplanar with the cut plane whose normal
     is ~parallel to the plane normal are the fresh cap.
  3. radial material assignment on cap faces: for each cap-face centroid,
     distance d to the bone centerline segment ab ->
         d < r_bone   -> BONE
         d < r_muscle -> MUSCLE
         d < r_fat    -> FAT
         else         -> SKIN
  4. GLB export (pygltflib): original surface keeps the input material;
     each (side, layer) cap region becomes its own primitive with the
     layer material.

Multiple --plane flags bisect sequentially (each piece is cut again).

Source: isl-org/Open3D (MIT), boolean ops from o3d.t.geometry.

Usage:
  python3 mesh_cut.py --in limb.glb --out limb_cut.glb \\
      --plane 0,0,0,0,1,0            # point(0,0,0) normal(0,1,0) \\
      --center-a 0,-0.5,0 --center-b 0,0.5,0 \\
      --r-bone 0.03 --r-muscle 0.07 --r-fat 0.09
  python3 mesh_cut.py --in limb.obj --out limb_cut.glb --plane ...

Inputs: .glb (first mesh primitive) or .obj. Output: .glb.
"""
import argparse
import math
import os
import struct
import sys

import numpy as np

try:
    import open3d as o3d
except ImportError:
    sys.exit("open3d is required: pip install open3d")

SCHEMA = "wh.anatomy-cut/1"
BIG = 10.0  # half-space box half-extent (mesh units; must exceed mesh size)


# ----------------------------------------------------------------------------
# mesh IO
# ----------------------------------------------------------------------------

def load_obj(path):
    verts, tris = [], []
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                verts.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = [int(p.split("/")[0]) - 1 for p in line.split()[1:4]]
                tris.append(idx)
    return np.asarray(verts, dtype=np.float64), np.asarray(tris, dtype=np.int64)


def load_glb(path):
    from pygltflib import GLTF2
    g = GLTF2().load(path)
    blob = g.binary_blob()
    prim = g.meshes[0].primitives[0]
    comp = {5126: ("f", 4)}
    type_n = {"VEC3": 3, "SCALAR": 1}

    def read_acc(i):
        acc = g.accessors[i]
        bv = g.bufferViews[acc.bufferView]
        fmt, sz = comp[acc.componentType]
        n = type_n[acc.type]
        off = (bv.byteOffset or 0) + (acc.byteOffset or 0)
        out = np.zeros((acc.count, n))
        for k in range(acc.count):
            chunk = blob[off + k * sz * n: off + (k + 1) * sz * n]
            out[k] = struct.unpack("<" + fmt * n, chunk)
        return out[:, 0] if n == 1 else out

    pos = read_acc(prim.attributes.POSITION)
    idx = read_acc(prim.indices).astype(np.int64).reshape(-1, 3)
    return pos, idx


def load_mesh(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".obj":
        return load_obj(path)
    if ext == ".glb":
        return load_glb(path)
    raise ValueError(f"unsupported input: {ext} (want .obj or .glb)")


# ----------------------------------------------------------------------------
# bisection
# ----------------------------------------------------------------------------

def _to_tensor(verts, tris):
    m = o3d.t.geometry.TriangleMesh(
        o3d.core.Device("CPU:0"))
    m.vertex.positions = o3d.core.Tensor(verts.astype(np.float32))
    m.triangle.indices = o3d.core.Tensor(tris.astype(np.int64))
    return m


def _halfspace_box(point, normal, sign):
    """Oversized box covering the half-space sign*dot(x-p, n) >= 0."""
    n = normal / (np.linalg.norm(normal) + 1e-12)
    # box local +Z will map to sign*n; box spans z in [0, 2*BIG]
    z = sign * n
    # build orthonormal basis
    up = np.array([0.0, 1.0, 0.0]) if abs(z[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = np.cross(up, z); x /= np.linalg.norm(x) + 1e-12
    y = np.cross(z, x)
    R = np.stack([x, y, z], axis=1)
    box = o3d.t.geometry.TriangleMesh.create_box(
        width=2 * BIG, height=2 * BIG, depth=2 * BIG)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = point - x * BIG - y * BIG  # box corner at plane, extends +z
    box.transform(T)
    return box


def bisect(verts, tris, point, normal):
    """Split mesh along plane -> (pos_verts, pos_tris, neg_verts, neg_tris).

    If the plane misses the mesh bounding box, returns the mesh as the
    positive piece and an empty negative piece (no-op cut).
    """
    n = normal / (np.linalg.norm(normal) + 1e-12)
    sd = (verts - point) @ n
    if sd.min() > 0 or sd.max() < 0:
        # plane does not intersect the mesh: nothing to cut
        empty = (np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64))
        return (verts, tris), empty
    mesh = _to_tensor(verts, tris)
    box_pos = _halfspace_box(point, normal, +1.0)
    pos = mesh.boolean_intersection(box_pos)
    neg = mesh.boolean_difference(box_pos)
    out = []
    for part in (pos, neg):
        v = part.vertex.positions.numpy().astype(np.float64)
        t = part.triangle.indices.numpy().astype(np.int64)
        out.append((v, t))
    return out[0], out[1]


# ----------------------------------------------------------------------------
# cap detection + radial layer assignment
# ----------------------------------------------------------------------------

def face_data(verts, tris):
    v0, v1, v2 = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    centroids = (v0 + v1 + v2) / 3.0
    normals = np.cross(v1 - v0, v2 - v0)
    lens = np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    return centroids, normals / lens


def find_cap_faces(verts, tris, point, normal, plane_eps=1e-3):
    """Faces created by the boolean seal: ~on the plane, normal ~±plane n."""
    n = normal / (np.linalg.norm(normal) + 1e-12)
    centroids, normals = face_data(verts, tris)
    dist = np.abs((centroids - point) @ n)
    align = np.abs(normals @ n)
    return np.where((dist < plane_eps) & (align > 0.9))[0]


def seg_distance(pts, a, b):
    ab = b - a
    denom = float(ab @ ab) + 1e-12
    t = np.clip((pts - a) @ ab / denom, 0.0, 1.0)
    proj = a + t[:, None] * ab
    return np.linalg.norm(pts - proj, axis=1)


LAYER_ORDER = ["BONE", "MUSCLE", "FAT", "SKIN"]
LAYER_COLORS = {
    "BONE":   (0.92, 0.88, 0.78, 1.0),
    "MUSCLE": (0.72, 0.14, 0.12, 1.0),
    "FAT":    (0.96, 0.82, 0.48, 1.0),
    "SKIN":   (0.85, 0.64, 0.52, 1.0),
}


def assign_layers(centroids, cap_idx, a, b, r_bone, r_muscle, r_fat):
    d = seg_distance(centroids[cap_idx], a, b)
    layers = np.empty(len(cap_idx), dtype=object)
    layers[d < r_bone] = "BONE"
    layers[(d >= r_bone) & (d < r_muscle)] = "MUSCLE"
    layers[(d >= r_muscle) & (d < r_fat)] = "FAT"
    layers[d >= r_fat] = "SKIN"
    return layers


# ----------------------------------------------------------------------------
# GLB export (one primitive per (side, region))
# ----------------------------------------------------------------------------

def export_glb(pieces, path):
    """pieces: list of dicts {verts, tris, mat_name}. Writes .glb."""
    from pygltflib import (GLTF2, BufferView, Accessor, Mesh, Primitive,
                           Node, Scene, Material, PbrMetallicRoughness)
    blob = bytearray()
    buffer_views, accessors, primitives = [], [], []
    mat_index = {}
    materials = []

    def get_mat(name):
        if name not in mat_index:
            c = LAYER_COLORS.get(name, (0.8, 0.8, 0.8, 1.0))
            mat_index[name] = len(materials)
            materials.append(Material(
                pbrMetallicRoughness=PbrMetallicRoughness(
                    baseColorFactor=list(c), metallicFactor=0.0,
                    roughnessFactor=0.9),
                name=f"WH_{name}"))
        return mat_index[name]

    def add_array(arr, comp_type, type_str):
        fmt = {5126: "f", 5123: "H", 5125: "I"}[comp_type]
        n = {"VEC3": 3, "SCALAR": 1}[type_str]
        raw = struct.pack("<" + fmt * arr.size, *arr.flatten().tolist())
        bv_offset = len(blob)
        blob.extend(raw)
        while len(blob) % 4:
            blob.append(0)
        buffer_views.append(BufferView(buffer=0, byteOffset=bv_offset,
                                       byteLength=len(raw)))
        # count = number of scalars (for indices: 3 per triangle)
        count = arr.size if type_str == "SCALAR" else len(arr)
        accessors.append(Accessor(
            bufferView=len(buffer_views) - 1,
            componentType=comp_type, count=count, type=type_str,
            min=arr.min(axis=0).tolist() if n > 1 else [float(arr.min())],
            max=arr.max(axis=0).tolist() if n > 1 else [float(arr.max())]))
        return len(accessors) - 1

    for piece in pieces:
        v, t, mat = piece["verts"], piece["tris"], piece["mat"]
        if len(t) == 0:
            continue
        # compact vertices
        used, remap = np.unique(t.flatten(), return_inverse=True)
        vv = v[used].astype(np.float32)
        tt = remap.reshape(-1, 3).astype(np.uint32)
        pa = add_array(vv, 5126, "VEC3")
        ia = add_array(tt, 5125, "SCALAR")
        primitives.append(Primitive(attributes={"POSITION": pa},
                                    indices=ia,
                                    material=get_mat(mat)))

    g = GLTF2()
    g.bufferViews = buffer_views
    g.accessors = accessors
    g.materials = materials
    g.meshes = [Mesh(primitives=primitives, name="wh_anatomy_cut")]
    g.nodes = [Node(mesh=0, name="cut")]
    g.scenes = [Scene(nodes=[0])]
    g.scene = 0
    g.asset = {"version": "2.0", "generator": "wh-mesh_cut"}
    g.buffers = [__import__("pygltflib").Buffer(byteLength=len(blob))]
    g.set_binary_blob(bytes(blob))
    g.save_binary(path)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def parse_plane(s):
    v = [float(x) for x in s.split(",")]
    assert len(v) == 6, "--plane needs px,py,pz,nx,ny,nz"
    return np.array(v[:3]), np.array(v[3:])


def parse_v3(s):
    return np.array([float(x) for x in s.split(",")])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True, help="output .glb")
    ap.add_argument("--plane", action="append", required=True,
                    help="px,py,pz,nx,ny,nz (repeatable)")
    ap.add_argument("--center-a", required=True, help="bone centerline start")
    ap.add_argument("--center-b", required=True, help="bone centerline end")
    ap.add_argument("--r-bone", type=float, required=True)
    ap.add_argument("--r-muscle", type=float, required=True)
    ap.add_argument("--r-fat", type=float, required=True)
    ap.add_argument("--plane-eps", type=float, default=1e-3)
    a = ap.parse_args()

    verts, tris = load_mesh(a.inp)
    print(f"loaded {a.inp}: {len(verts)} verts, {len(tris)} tris")
    ca, cb = parse_v3(a.center_a), parse_v3(a.center_b)

    pieces = [(verts, tris, None, None)]  # (verts, tris, point, normal)
    for ps in a.plane:
        point, normal = parse_plane(ps)
        nxt = []
        for v, t, _, _ in pieces:
            (pv, pt), (nv, nt) = bisect(v, t, point, normal)
            nxt.append((pv, pt, point, normal))
            nxt.append((nv, nt, point, normal))
        pieces = nxt

    out_pieces = []
    stats = {}
    for v, t, point, normal in pieces:
        if len(t) == 0 or point is None:
            # no-op cut (plane missed) -> keep surface as-is
            if len(t):
                out_pieces.append({"verts": v, "tris": t, "mat": "SKIN"})
                stats["SKIN_surface"] = stats.get("SKIN_surface", 0) + len(t)
            continue
        centroids, _ = face_data(v, t)
        cap = find_cap_faces(v, t, point, normal, a.plane_eps)
        is_cap = np.zeros(len(t), dtype=bool)
        is_cap[cap] = True
        # surface keeps SKIN (original) material; cap gets radial layers
        out_pieces.append({"verts": v, "tris": t[~is_cap], "mat": "SKIN"})
        if len(cap):
            layers = assign_layers(centroids, cap, ca, cb,
                                   a.r_bone, a.r_muscle, a.r_fat)
            for layer in LAYER_ORDER:
                sel = cap[layers == layer]
                if len(sel):
                    out_pieces.append({"verts": v, "tris": t[sel],
                                       "mat": layer})
                    stats[layer] = stats.get(layer, 0) + len(sel)
        stats["SKIN_surface"] = stats.get("SKIN_surface", 0) + int((~is_cap).sum())

    export_glb(out_pieces, a.out)
    print(f"wrote {a.out}: " +
          ", ".join(f"{k}={v}" for k, v in stats.items()))


if __name__ == "__main__":
    main()
