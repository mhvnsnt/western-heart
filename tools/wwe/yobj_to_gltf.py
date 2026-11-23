#!/usr/bin/env python3
"""YOBJ -> glTF 2.0 (.glb) converter for WWE 2K19 character models.

Usage: python3 yobj_to_gltf.py <model.yobj> <out.glb> [--no-morphs]

Emits one mesh per YOBJ sub-object (positions, normals, UVs, skin
weights, triangle indices), a skin over the full bone table, and
morph targets for the facial emote heads where present. Units are
metres (source is cm x0.01); the source frame (x lateral, y
up-negative, z depth) maps to glTF (x, -y, -z).

v2 skeleton (2026-11-19): joints use the true bind pose decoded
from the bone records -- parent-relative offsets (+0x10) and rest
orientations (+0x20, Euler XYZ) -- instead of the v1 centroid
positions + identity rotations. The FK reproduces the true joint
pivots (knee height 58.2 cm, wrist within 2 cm of its centroid);
inverse bind matrices are the full inverse of each joint's world
transform. Morph bones (m###_####, parentless leaves driving the
face) keep centroid positions + identity rotations: their offsets
are not mesh positions. Animation-ready: a YANM clip's per-joint
rotation is R_rest @ R_anim (see yanm_to_gltf.py).

Known v1 limits (see docs/YOBJ-YANM.md): no textures are embedded
(the name->DDS mapping lives in the ch PACs, not yet unpacked here).
"""

import argparse
import json
import math
import re
import struct

from yobj import load

SCALE = 0.01
MORPH_RE = re.compile(r"^m\d")


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


def mat_to_gltf(m):
    """File-frame 3x3 rotation -> glTF frame: C @ M @ C with
    C = diag(1,-1,-1) (a 180-degree rotation about X, so this is a
    proper conjugation, not a reflection)."""
    c = (1.0, -1.0, -1.0)
    return [[c[i] * m[i][j] * c[j] for j in range(3)] for i in range(3)]


def mat_to_quat(m):
    """3x3 rotation matrix -> (x, y, z, w) quaternion."""
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        return ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s,
                (m[1][0] - m[0][1]) / s, 0.25 * s)
    if m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        return (0.25 * s, (m[0][1] + m[1][0]) / s,
                (m[0][2] + m[2][0]) / s, (m[2][1] - m[1][2]) / s)
    if m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        return ((m[0][1] + m[1][0]) / s, 0.25 * s,
                (m[1][2] + m[2][1]) / s, (m[0][2] - m[2][0]) / s)
    s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
    return ((m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s,
            0.25 * s, (m[1][0] - m[0][1]) / s)


def euler_xyz_mat(rx, ry, rz):
    """Euler XYZ (intrinsic X then Y then Z) -> 3x3 matrix."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rxm = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    rym = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rzm = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mm(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3))
                 for j in range(3)] for i in range(3)]

    return mm(rzm, mm(rym, rxm))


def invert_rt(rot, pos):
    """Inverse of a rigid transform (3x3 rot, 3-vector pos) as a
    column-major 4x4 list for glTF inverseBindMatrices."""
    # R^-1 = R^T; t' = -R^T @ t.
    rt = [[rot[j][i] for j in range(3)] for i in range(3)]
    tp = tuple(-sum(rt[i][k] * pos[k] for k in range(3))
               for i in range(3))
    return [rt[0][0], rt[1][0], rt[2][0], 0.0,
            rt[0][1], rt[1][1], rt[2][1], 0.0,
            rt[0][2], rt[1][2], rt[2][2], 0.0,
            tp[0], tp[1], tp[2], 1.0]


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


def build_skeleton(y):
    """Joint bind data for the glTF skin.

    Returns (joint_local, joint_world, parent_override) where
    joint_local[i] is the node's local (translation,
    rotation-quat-or-None) in glTF coords (metres), joint_world[i]
    is the joint's world (rot3, pos3) in glTF coords (metres) for
    the inverse bind matrices, and parent_override maps morph bone
    indices to their nearest skeleton bone (see below).

    Skeleton bones use the decoded bind pose (local offset +
    rest orientation). Morph bones (m###_####) are parentless
    leaves in the file, but they carry heavy skin weights all over
    the body (435 vertices are 100% morph-weighted) -- leaving
    them parented to the root rips the mesh apart the moment the
    skeleton animates, because the morph bones stay in world
    space while the body moves. They are therefore parented to
    their nearest skeleton bone (by bind-pose distance) with a
    local transform that reproduces their exact world bind pose
    (centroid position, identity rotation), so they rigidly follow
    the body part they sit on. The bind pose is unchanged (IBMs
    are the world-transform inverses); the deformation is an
    approximation until the morph bones' true runtime parenting
    is decoded.
    """
    centroids = y.bone_centroids()
    fk = y.rest_fk()
    skel_idx = [b["index"] for b in y.bones
                if not MORPH_RE.match(b["name"]) and b["index"] != 0]
    joint_local = []
    joint_world = []
    parent_override = {}
    for b in y.bones:
        i = b["index"]
        if MORPH_RE.match(b["name"]):
            c = centroids.get(i)
            if c is not None:
                pos = to_gltf_pos(c)
            else:
                pos = (0.0, -b["n"] * SCALE, -b["o"] * SCALE)
                c = (0.0, b["n"], b["o"])
            # Nearest skeleton bone by bind-pose distance.
            best, best_d = None, None
            for j in skel_idx:
                wp, _ = fk[j]
                d = ((c[0] - wp[0]) ** 2 + (c[1] - wp[1]) ** 2 +
                     (c[2] - wp[2]) ** 2)
                if best_d is None or d < best_d:
                    best, best_d = j, d
            parent_override[i] = best
            # Local transform relative to that bone: world rotation
            # is identity, world position is the centroid.
            pw, pr = fk[best]
            # rel = R_parent^-1 @ (centroid - parent_pos), file coords
            rel = (c[0] - pw[0], c[1] - pw[1], c[2] - pw[2])
            rt = [[pr[j][k] for j in range(3)] for k in range(3)]
            loc = tuple(sum(rt[r][k] * rel[k] for k in range(3))
                        for r in range(3))
            joint_local.append((to_gltf_pos(loc),
                                mat_to_quat(mat_to_gltf(rt))))
            joint_world.append(([[1, 0, 0], [0, 1, 0], [0, 0, 1]], pos))
        else:
            # Local translation = parent-frame offset, converted.
            t = to_gltf_pos(b["offset"])
            rr = euler_xyz_mat(*b["rest_euler"])
            q = mat_to_quat(mat_to_gltf(rr))
            joint_local.append((t, q))
            wpos, wrot = fk[i]
            joint_world.append((mat_to_gltf(wrot), to_gltf_pos(wpos)))
    return joint_local, joint_world, parent_override


def build_gltf(yobj_path, with_morphs=True):
    """Build the glTF dict + buffer builder for a YOBJ. Returns
    (gltf, builder, yobj). Callers may add animations to the dict
    before write_glb()."""
    y = load(yobj_path)
    joint_local, joint_world, parent_override = build_skeleton(y)

    # Parent map: file parents, with every root (except bone 0)
    # parented under bone 0 ('vector') so the skin has one root --
    # except morph bones, which attach to their nearest skeleton
    # bone (see build_skeleton).
    parent_of = {}
    for b in y.bones:
        p = b["parent"]
        if b["index"] == 0:
            parent_of[0] = None
        elif b["index"] in parent_override:
            parent_of[b["index"]] = parent_override[b["index"]]
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

    # Skin: inverse bind matrices are the full inverse of each
    # joint's world transform (rotation + translation).
    ibms = [invert_rt(rot, pos) for rot, pos in joint_world]
    ibm_acc = b.mat4s(ibms)

    # Nodes: joints first (node index == bone index), then mesh nodes.
    nodes = []
    children = {i: [] for i in range(y.bone_count)}
    for i, p in parent_of.items():
        if p is not None:
            children[p].append(i)
    for bone in y.bones:
        i = bone["index"]
        t, q = joint_local[i]
        node = {"name": bone["name"],
                "translation": [t[0], t[1], t[2]]}
        if q is not None:
            node["rotation"] = [q[0], q[1], q[2], q[3]]
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
    return gltf, b, y


def write_glb(gltf, b, out_path):
    gltf["buffers"] = [{"byteLength": len(b.buf)}]
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


def convert(yobj_path, out_path, with_morphs=True):
    gltf, b, y = build_gltf(yobj_path, with_morphs)
    write_glb(gltf, b, out_path)
    n_tris = sum(len(y.read_faces(s)) for s in y.subobjects)
    n_morphs = sum(max(0, s["heads"] - 1) for s in y.subobjects)
    print(f"wrote {out_path}: {len(gltf['meshes'])} meshes, "
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
