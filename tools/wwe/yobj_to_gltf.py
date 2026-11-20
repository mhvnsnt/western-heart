#!/usr/bin/env python3
"""YOBJ -> glTF 2.0 (.glb) converter for WWE 2K19 character models.

Usage: python3 yobj_to_gltf.py <model.yobj> <out.glb> [--no-morphs]

Emits one mesh per YOBJ sub-object (positions, normals, UVs, skin
weights, triangle indices), a skin over the full bone table (joint
bind positions measured as weighted vertex centroids -- the
anatomically correct pivots), and morph targets for the facial
emote heads where present. Units are metres (source is cm x0.01);
the source frame (x lateral, y up-negative, z depth) maps to glTF
(x, -y, -z).

Known v1 limits (see docs/YOBJ-YANM.md): joint rotations are
identity (bind pose renders correctly; the rotation fields are not
decoded yet), no textures are embedded (the name->DDS mapping lives
in the ch PACs, not yet unpacked here).
"""

import argparse
import json
import math
import struct

from yobj import load

SCALE = 0.01


def to_gltf_pos(p):
    """File coords (x, y up-neg, z) -> glTF (x, -y, -z), metres."""
    return (p[0] * SCALE, -p[1] * SCALE, -p[2] * SCALE)


def to_gltf_dir(v):
    """Direction (normal): same rotation, no scale, renormalised."""
    x, y, z = v[0], -v[1], -v[2]
    n = math.sqrt(x * x + y * y + z * z)
    if n == 0:
        return (0.0, 0.0, 0.0)
    return (x / n, y / n, z / n)


class GlbBuilder:
    def __init__(self):
        self.buf = bytearray()
        self.accessors = []
        self.buffer_views = []

    def add_data(self, data, target=None):
        while len(self.buf) % 4:
            self.buf.append(0)
        off = len(self.buf)
        self.buf += data
        bv = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target is not None:
            bv["target"] = target
        self.buffer_views.append(bv)
        return len(self.buffer_views) - 1

    def add_accessor(self, bv, component_type, count, type_, min_=None,
                     max_=None):
        acc = {"bufferView": bv, "componentType": component_type,
               "count": count, "type": type_}
        if min_ is not None:
            acc["min"] = min_
            acc["max"] = max_
        self.accessors.append(acc)
        return len(self.accessors) - 1

    def vec3(self, items, target=34962):
        data = struct.pack(f"<{len(items) * 3}f",
                           *[c for v in items for c in v])
        bv = self.add_data(data, target)
        mn = [min(v[i] for v in items) for i in range(3)]
        mx = [max(v[i] for v in items) for i in range(3)]
        return self.add_accessor(bv, 5126, len(items), "VEC3", mn, mx)

    def vec2(self, items, target=34962):
        data = struct.pack(f"<{len(items) * 2}f",
                           *[c for v in items for c in v])
        bv = self.add_data(data, target)
        mn = [min(v[i] for v in items) for i in range(2)]
        mx = [max(v[i] for v in items) for i in range(2)]
        return self.add_accessor(bv, 5126, len(items), "VEC2", mn, mx)

    def uvec4(self, items, target=34962):
        data = struct.pack(f"<{len(items) * 4}H",
                           *[c for v in items for c in v])
        bv = self.add_data(data, target)
        return self.add_accessor(bv, 5123, len(items), "VEC4")

    def vec4f(self, items, target=34962):
        data = struct.pack(f"<{len(items) * 4}f",
                           *[c for v in items for c in v])
        bv = self.add_data(data, target)
        return self.add_accessor(bv, 5126, len(items), "VEC4")

    def indices(self, faces):
        flat = [i for tri in faces for i in tri]
        if flat and max(flat) < 65536:
            data = struct.pack(f"<{len(flat)}H", *flat)
            bv = self.add_data(data, 34963)
            return self.add_accessor(bv, 5123, len(flat), "SCALAR")
        data = struct.pack(f"<{len(flat)}I", *flat)
        bv = self.add_data(data, 34963)
        return self.add_accessor(bv, 5125, len(flat), "SCALAR")

    def mat4s(self, mats):
        data = struct.pack(f"<{len(mats) * 16}f",
                           *[c for m in mats for c in m])
        bv = self.add_data(data)
        return self.add_accessor(bv, 5126, len(mats), "MAT4")


def convert(yobj_path, out_path, with_morphs=True):
    y = load(yobj_path)
    centroids = y.bone_centroids()

    # Joint bind positions in glTF coords (metres). Centroids are
    # measured; bones without influence fall back to the N/O floats
    # (Y/Z exact, X unknown -> 0).
    joint_pos = []
    for b in y.bones:
        c = centroids.get(b["index"])
        if c is not None:
            joint_pos.append(to_gltf_pos(c))
        else:
            joint_pos.append((0.0, -b["n"] * SCALE, -b["o"] * SCALE))

    # Parent map: file parents, with every root (except bone 0)
    # parented under bone 0 ('vector') so the skin has one root.
    parent_of = {}
    for b in y.bones:
        p = b["parent"]
        if b["index"] == 0:
            parent_of[0] = None
        elif p is None:
            parent_of[b["index"]] = 0
        else:
            parent_of[b["index"]] = p

    b = GlbBuilder()
    meshes = []
    materials = []
    for sub in y.subobjects:
        vc = sub["verts"]
        base = y.read_positions(sub, 0)
        pos = [to_gltf_pos(p) for p in base]
        nor = [to_gltf_dir(n) for n in y.read_normals(sub)]
        uvs = y.read_uvs(sub)
        weights = y.read_weights(sub)
        faces = y.read_faces(sub)
        pos_acc = b.vec3(pos)
        nor_acc = b.vec3(nor)
        uv_acc = b.vec2(uvs)
        idx_acc = b.indices(faces)
        joints0 = []
        weights0 = []
        joints1 = []
        weights1 = []
        need_set1 = False
        for slots in weights:
            j0 = [0, 0, 0, 0]
            w0 = [0.0, 0.0, 0.0, 0.0]
            j1 = [0, 0, 0, 0]
            w1 = [0.0, 0.0, 0.0, 0.0]
            for k, (bone, w) in enumerate(slots[:8]):
                if k < 4:
                    j0[k] = bone
                    w0[k] = w
                else:
                    j1[k - 4] = bone
                    w1[k - 4] = w
                    need_set1 = True
            joints0.append(j0)
            weights0.append(w0)
            joints1.append(j1)
            weights1.append(w1)
        attrs = {"POSITION": pos_acc, "NORMAL": nor_acc,
                 "TEXCOORD_0": uv_acc,
                 "JOINTS_0": b.uvec4(joints0),
                 "WEIGHTS_0": b.vec4f(weights0)}
        if need_set1:
            attrs["JOINTS_1"] = b.uvec4(joints1)
            attrs["WEIGHTS_1"] = b.vec4f(weights1)
        targets = []
        target_names = []
        if with_morphs and sub["heads"] > 1:
            for h in range(1, sub["heads"]):
                hp = y.read_positions(sub, h)
                deltas = [tuple(to_gltf_pos(hp[i])[k] - pos[i][k]
                                for k in range(3)) for i in range(vc)]
                targets.append({"POSITION": b.vec3(deltas)})
            if sub["heads"] - 1 == y.emote_count:
                target_names = list(y.emotes)
            else:
                target_names = [f"head_{h}"
                                for h in range(1, sub["heads"])]
        mat_idx = len(materials)
        materials.append({
            "name": f"{sub['shader']}_mat{sub['material']}",
            "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1],
                                     "metallicFactor": 0.0,
                                     "roughnessFactor": 0.9},
            "extras": {"yobj_shader": sub["shader"],
                       "yobj_material": sub["material"],
                       "yobj_subobject": sub["index"]},
        })
        prim = {"attributes": attrs, "indices": idx_acc,
                "material": mat_idx}
        if targets:
            prim["targets"] = targets
        mesh = {"name": f"sub{sub['index']:02d}_{sub['shader']}",
                "primitives": [prim]}
        if target_names:
            mesh["extras"] = {"targetNames": target_names}
        meshes.append(mesh)

    # Skin: inverse bind matrices are pure translations (rotations
    # are identity in v1), so IBM = translate(-joint_pos).
    ibms = []
    for (x, yy, z) in joint_pos:
        ibms.append([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                     -x, -yy, -z, 1])
    ibm_acc = b.mat4s(ibms)

    # Nodes: joints first (node index == bone index), then mesh nodes.
    nodes = []
    children = {i: [] for i in range(y.bone_count)}
    for i, p in parent_of.items():
        if p is not None:
            children[p].append(i)
    for bone in y.bones:
        i = bone["index"]
        p = parent_of[i]
        px, py, pz = joint_pos[i]
        if p is not None:
            qx, qy, qz = joint_pos[p]
            px, py, pz = px - qx, py - qy, pz - qz
        node = {"name": bone["name"],
                "translation": [px, py, pz]}
        if children[i]:
            node["children"] = children[i]
        nodes.append(node)
    mesh_node_indices = []
    for mi, mesh in enumerate(meshes):
        nodes.append({"name": mesh["name"], "mesh": mi, "skin": 0})
        mesh_node_indices.append(len(nodes) - 1)

    skins = [{"inverseBindMatrices": ibm_acc,
              "joints": list(range(y.bone_count)),
              "skeleton": 0,
              "name": "yobj_skeleton"}]
    scenes = [{"nodes": [0] + mesh_node_indices}]
    gltf = {"asset": {"version": "2.0",
                      "generator": "yobj_to_gltf (wwe2k19 toolchain)"},
            "scene": 0, "scenes": scenes, "nodes": nodes,
            "meshes": meshes, "materials": materials, "skins": skins,
            "accessors": b.accessors, "bufferViews": b.buffer_views,
            "buffers": [{"byteLength": len(b.buf)}]}

    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    while len(js) % 4:
        js += b" "
    while len(b.buf) % 4:
        b.buf.append(0)
    total = 12 + 8 + len(js) + 8 + len(b.buf)
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack("<II", len(b.buf), 0x004E4942))
        f.write(bytes(b.buf))
    n_tris = sum(len(y.read_faces(s)) for s in y.subobjects)
    n_morphs = sum(max(0, s["heads"] - 1) for s in y.subobjects)
    print(f"wrote {out_path}: {len(meshes)} meshes, "
          f"{sum(s['verts'] for s in y.subobjects)} verts, "
          f"{n_tris} tris, {y.bone_count} joints, "
          f"{n_morphs} morph targets")


def main():
    ap = argparse.ArgumentParser(description="Convert a WWE 2K19 YOBJ "
                                             "model to glTF 2.0 (.glb).")
    ap.add_argument("yobj", help="input .yobj file")
    ap.add_argument("glb", help="output .glb file")
    ap.add_argument("--no-morphs", action="store_true",
                    help="skip facial morph targets")
    args = ap.parse_args()
    convert(args.yobj, args.glb, with_morphs=not args.no_morphs)


if __name__ == "__main__":
    main()
