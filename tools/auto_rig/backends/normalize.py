#!/usr/bin/env python3
"""tools/auto_rig/backends/normalize.py — pure-Python GLB normalization.

Bakes all node transforms into vertex positions, then in glTF Y-up space:
  - translates so the lowest vertex sits at y=0 (feet on the ground)
  - uniformly scales so the mesh height == target height

Does NOT touch facing (see blender_heat.py --mesh-facing). Does NOT rig.
Inputs are never modified; a new GLB is written.

Usage:
    python3 normalize.py --in MODEL.glb --out NORM.glb [--height 1.8]
Requires: pygltflib, numpy.
"""

import argparse
import copy

import numpy as np
from pygltflib import GLTF2


def _node_matrix(node):
    if node.matrix is not None and any(node.matrix):
        return np.array(node.matrix, dtype=np.float64).reshape(4, 4).T
    m = np.eye(4)
    if node.scale is not None and any(node.scale):
        m = np.diag([node.scale[0], node.scale[1], node.scale[2], 1.0]) @ m
    if node.rotation is not None and any(node.rotation):
        x, y, z, w = node.rotation
        r = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
            [0, 0, 0, 1],
        ])
        m = r @ m
    if node.translation is not None and any(node.translation):
        t = np.eye(4)
        t[:3, 3] = node.translation
        m = t @ m
    return m


def bake_transforms(glb):
    """Bake every node's world matrix into its mesh vertices. Returns glb."""
    world = {}

    def visit(idx, parent_m):
        node = glb.nodes[idx]
        m = parent_m @ _node_matrix(node)
        world[idx] = m
        for child in node.children or []:
            visit(child, m)

    for scene in glb.scenes:
        for root in scene.nodes or []:
            visit(root, np.eye(4))

    blob = glb.binary_blob()
    for idx, m in world.items():
        node = glb.nodes[idx]
        if node.mesh is None:
            continue
        mesh = glb.meshes[node.mesh]
        for prim in mesh.primitives:
            for attr in ("POSITION", "NORMAL"):
                ai = getattr(prim.attributes, attr, None)
                if ai is None:
                    continue
                acc = glb.accessors[ai]
                bv = glb.bufferViews[acc.bufferView]
                off = (bv.byteOffset or 0) + (acc.byteOffset or 0)
                n = acc.count
                arr = np.frombuffer(blob, dtype=np.float32, count=n * 3,
                                    offset=off).reshape(n, 3).copy()
                if attr == "POSITION":
                    hom = np.ones((n, 4))
                    hom[:, :3] = arr
                    arr = (hom @ m.T)[:, :3]
                else:
                    arr = arr @ m[:3, :3].T
                    arr /= np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
                # write back into a fresh blob copy
                blob = (blob[:off] + arr.astype(np.float32).tobytes()
                        + blob[off + n * 12:])
        # node transform now identity
        node.translation = [0, 0, 0]
        node.rotation = [0, 0, 0, 1]
        node.scale = [1, 1, 1]
        node.matrix = None
    glb.set_binary_blob(blob)
    return glb


def normalize(path_in, path_out, height=1.8):
    glb = GLTF2().load(path_in)
    glb = bake_transforms(glb)
    blob = glb.binary_blob()
    mins = np.full(3, np.inf)
    maxs = np.full(3, -np.inf)
    for mesh in glb.meshes:
        for prim in mesh.primitives:
            ai = getattr(prim.attributes, "POSITION", None)
            if ai is None:
                continue
            acc = glb.accessors[ai]
            bv = glb.bufferViews[acc.bufferView]
            off = (bv.byteOffset or 0) + (acc.byteOffset or 0)
            arr = np.frombuffer(blob, dtype=np.float32,
                                count=acc.count * 3, offset=off).reshape(-1, 3)
            mins = np.minimum(mins, arr.min(0))
            maxs = np.maximum(maxs, arr.max(0))
    h = maxs[1] - mins[1]
    if h <= 0:
        raise RuntimeError("degenerate mesh: zero height")
    s = height / h
    # translate feet to y=0, then uniform-scale about the (x,z) center so
    # the character stays centered under the skeleton (never recenter x/z
    # to the corner — the skeleton is symmetric about x=0).
    cx, cz = (mins[0] + maxs[0]) / 2.0, (mins[2] + maxs[2]) / 2.0
    blob = glb.binary_blob()
    for mesh in glb.meshes:
        for prim in mesh.primitives:
            ai = getattr(prim.attributes, "POSITION", None)
            if ai is None:
                continue
            acc = glb.accessors[ai]
            bv = glb.bufferViews[acc.bufferView]
            off = (bv.byteOffset or 0) + (acc.byteOffset or 0)
            n = acc.count
            arr = np.frombuffer(blob, dtype=np.float32, count=n * 3,
                                offset=off).reshape(n, 3).copy()
            arr[:, 1] = (arr[:, 1] - mins[1]) * s
            arr[:, 0] = cx + (arr[:, 0] - cx) * s
            arr[:, 2] = cz + (arr[:, 2] - cz) * s
            blob = (blob[:off] + arr.astype(np.float32).tobytes()
                    + blob[off + n * 12:])
            # refresh accessor bounds
            acc.min = arr.min(0).tolist()
            acc.max = arr.max(0).tolist()
    glb.set_binary_blob(blob)
    glb.save(path_out)
    return {"height_in": float(h), "scale": float(s),
            "min_in": mins.tolist(), "max_in": maxs.tolist()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--height", type=float, default=1.8)
    a = ap.parse_args()
    info = normalize(a.inp, a.out, a.height)
    print("NORMALIZE_OK", info)


if __name__ == "__main__":
    main()
