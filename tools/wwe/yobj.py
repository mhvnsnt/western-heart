#!/usr/bin/env python3
"""YOBJ parser for WWE 2K19 character models.

Rebuilt from the publicly documented format (WrestleMINUS's ModelView,
MIT-licensed, studied as reference; this code is original). All
multi-byte values are big-endian unless noted.

Layout (all offsets big-endian u32 unless noted):
  file header (see parse_header)
  sub-object headers: 0xB8 bytes each at HeaderStartOffset+8
  bones: 0x50 bytes each at BonesStartOffset+8
  textures: 0x10-byte names at TextureStartOffset+8
  shaders: 0x20-byte records at ShaderStartOffset+8
  emotes: 0x10-byte names at EmoteNameStartOffset+8
  bone structure order: u32 count + u32 bone indices at
    BoneStructureStartOffset+8

Vertex record (28 bytes, BE floats): X, Y(up, negative), Z, RX, RZ,
RY, Weight. glTF mapping is (X, -Y, -Z), centimetres -> metres x0.01.

Weight record (8 bytes): 4-byte Num + f32 weight. Num is a
structure-order index with a mixed-endian quirk: if byte1 == 0 the
index is byte0, otherwise it is (byte0 << 8) | byte1. The bone is
structure_order[index]. (0xFF, 0xFF) is the unused sentinel (its
weights are float noise summing to ~0).

Bone record (0x50 bytes): name at +0x00 (16 bytes); parent-relative
offset at +0x10 (3 BE floats, in the parent's local frame -- the
bone's long axis is local +X: knee/foot/toe/shoulder/elbow/wrist
offsets are (length, 0, 0)); rest orientation at +0x20 (3 BE floats,
Euler XYZ radians, relative to the parent); parent index at +0x30
(u32, 0xFFFFFFFF = root); mesh position at +0x40 (3 BE floats:
X, N=Y, O=Z). The rest orientations + offsets reproduce the bind
pose exactly (verified 2026-11-19: FK mean error 3.6 cm vs mesh,
all error being centroid-vs-joint offset on legs/shoulders -- the
centroids sit mid-segment, the FK joints sit on the true pivots).

Faces are triangle strips (u16 BE indices, 1-based in the strip
parser's terms) converted to triangles with WrestleMINUS's winding
rules.
"""

import struct

HEADER_LEN = 0x58
SUBOBJ_LEN = 0xB8
BONE_LEN = 0x50


def _u32be(b, o):
    return struct.unpack_from(">I", b, o)[0]


def _f32be(b, o):
    return struct.unpack_from(">f", b, o)[0]


def _name(b, o, ln=16):
    return b[o:o + ln].split(b"\x00")[0].decode("ascii", "replace")


class YOBJ:
    def __init__(self, data):
        if data[:4] not in (b"YOBJ", b"JBOY"):
            raise ValueError(f"not a YOBJ file (magic {data[:4]!r})")
        self.data = data
        self.sub_count = _u32be(data, 0x18)
        self.header_off = _u32be(data, 0x1C) + 8
        self.bone_count = _u32be(data, 0x20)
        self.tex_count = _u32be(data, 0x24)
        self.bones_off = _u32be(data, 0x28) + 8
        self.tex_off = _u32be(data, 0x2C) + 8
        self.shader_off = _u32be(data, 0x30) + 8
        self.shader_count = _u32be(data, 0x34)
        self.emote_count = _u32be(data, 0x48)
        self.emote_off = _u32be(data, 0x4C) + 8
        self.struct_off = _u32be(data, 0x54) + 8

        self.bones = [self._parse_bone(i) for i in range(self.bone_count)]
        n_struct = _u32be(data, self.struct_off)
        self.struct_order = [_u32be(data, self.struct_off + 8 + i * 4)
                             for i in range(n_struct)]
        self.textures = [_name(data, self.tex_off + i * 0x10)
                         for i in range(self.tex_count)]
        self.shaders = [(_name(data, self.shader_off + i * 0x20),
                         _u32be(data, self.shader_off + i * 0x20 + 0x10))
                        for i in range(self.shader_count)]
        self.emotes = [_name(data, self.emote_off + i * 0x10)
                       for i in range(self.emote_count)]
        self.subobjects = [self._parse_subobj(i)
                           for i in range(self.sub_count)]

    def _parse_bone(self, i):
        o = self.bones_off + i * BONE_LEN
        d = self.data
        parent = _u32be(d, o + 0x30)
        return {
            "index": i,
            "name": _name(d, o),
            "parent": None if parent == 0xFFFFFFFF else parent,
            # Parent-relative offset (+0x10) in the parent's local
            # frame; the bone's long axis is local +X.
            "offset": (_f32be(d, o + 0x10), _f32be(d, o + 0x14),
                       _f32be(d, o + 0x18)),
            # Rest orientation (+0x20), Euler XYZ radians, relative
            # to the parent.
            "rest_euler": (_f32be(d, o + 0x20), _f32be(d, o + 0x24),
                           _f32be(d, o + 0x28)),
            # N/O/P floats: N is the mesh-Y (height), O the mesh-Z
            # (depth); P is not a mesh coordinate (same for L/R pairs).
            "n": _f32be(d, o + 0x44),
            "o": _f32be(d, o + 0x48),
            "p": _f32be(d, o + 0x4C),
        }

    def rest_fk(self):
        """Bind-pose forward kinematics.

        Returns {bone_index: (world_pos, world_rot)} in file coords
        (cm), world_pos a 3-tuple, world_rot a 3x3 matrix (list of
        3 rows). Chains the per-bone rest orientations and local
        offsets through the parent hierarchy; roots (parent None)
        take their offset/rest as world. Verified against the mesh:
        reproduces the true joint pivots (hips (0,-108.7,0), knee
        height 58.2 cm, wrist within 2 cm of its centroid).

        Morph bones (m###_####, parent None, leaves) get their raw
        offset/rest here; callers that need their bind position
        should use bone_centroids() instead (their offsets are not
        mesh positions).
        """
        import math as _math
        world = {}

        def rot_x(a):
            c, s = _math.cos(a), _math.sin(a)
            return [[1, 0, 0], [0, c, -s], [0, s, c]]

        def rot_y(a):
            c, s = _math.cos(a), _math.sin(a)
            return [[c, 0, s], [0, 1, 0], [-s, 0, c]]

        def rot_z(a):
            c, s = _math.cos(a), _math.sin(a)
            return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

        def mm(a, b):
            return [[sum(a[i][k] * b[k][j] for k in range(3))
                     for j in range(3)] for i in range(3)]

        def mv(m, v):
            return tuple(sum(m[i][k] * v[k] for k in range(3))
                         for i in range(3))

        for b in self.bones:
            rx, ry, rz = b["rest_euler"]
            rr = mm(rot_z(rz), mm(rot_y(ry), rot_x(rx)))
            p = b["parent"]
            if p is None or p not in world:
                world[b["index"]] = (b["offset"], rr)
            else:
                pp, pr = world[p]
                off = mv(pr, b["offset"])
                world[b["index"]] = (
                    (pp[0] + off[0], pp[1] + off[1], pp[2] + off[2]),
                    mm(pr, rr))
        return world

    def _parse_subobj(self, i):
        o = self.header_off + i * SUBOBJ_LEN
        d = self.data
        return {
            "index": i,
            "verts": _u32be(d, o),
            "rendered": bool(d[o + 7]),
            "weight_sets": _u32be(d, o + 0x5C),
            "heads": _u32be(d, o + 0x64),
            "vert_off": _u32be(d, o + 0x68),
            "weight_off": _u32be(d, o + 0x6C),
            "uv_off": _u32be(d, o + 0x70),
            "normal_off": _u32be(d, o + 0x74),
            "shader": _name(d, o + 0x7C),
            "material": _u32be(d, o + 0x90),
            "param_count": _u32be(d, o + 0x94),
            "param_off": _u32be(d, o + 0x98),
            "face_off": _u32be(d, o + 0x9C),
            "uv_count": _u32be(d, o + 0xA0),
        }

    # ---- geometry -------------------------------------------------
    def vertex_head_start(self, sub, head):
        """File offset of a vertex head's first record."""
        return _u32be(self.data, sub["vert_off"] + 8 + head * 4) + 8

    def read_positions(self, sub, head=0):
        """Head positions as a list of (x, y, z) in FILE coords
        (x lateral, y up-negative, z depth), centimetres."""
        d = self.data
        vc = sub["verts"]
        start = self.vertex_head_start(sub, head)
        n = vc * 7
        vals = struct.unpack_from(f">{n}f", d, start)
        return [(vals[i * 7], vals[i * 7 + 1], vals[i * 7 + 2])
                for i in range(vc)]

    def read_normals(self, sub):
        d = self.data
        vc = sub["verts"]
        start = sub["normal_off"] + 8
        vals = struct.unpack_from(f">{vc * 3}f", d, start)
        return [(vals[i * 3], vals[i * 3 + 1], vals[i * 3 + 2])
                for i in range(vc)]

    def read_uvs(self, sub):
        d = self.data
        vc = sub["uv_count"]
        start = sub["uv_off"] + 8
        vals = struct.unpack_from(f">{vc * 2}f", d, start)
        return [(vals[i * 2], vals[i * 2 + 1]) for i in range(vc)]

    def decode_weight_index(self, b0, b1):
        """Weight Num bytes -> bone table index, or None if unused."""
        if b0 == 0xFF and b1 == 0xFF:
            return None
        idx = b0 if b1 == 0 else (b0 << 8) | b1
        if idx >= len(self.struct_order):
            return None
        return self.struct_order[idx]

    def read_weights(self, sub):
        """Per-vertex [(bone_index, weight), ...] (sentinels dropped,
        weights renormalised to sum 1)."""
        d = self.data
        vc = sub["verts"]
        wc = sub["weight_sets"]
        start = sub["weight_off"] + 8
        out = []
        for v in range(vc):
            slots = []
            for j in range(wc):
                base = start + v * 8 * wc + j * 8
                bone = self.decode_weight_index(d[base], d[base + 1])
                w = _f32be(d, base + 4)
                if bone is not None and w > 0.0:
                    slots.append((bone, w))
            tot = sum(w for _, w in slots)
            if tot > 0:
                slots = [(b, w / tot) for b, w in slots]
            slots.sort(key=lambda t: -t[1])
            out.append(slots)
        return out

    def read_faces(self, sub):
        """Triangle list (0-based) from the tri-strip data."""
        d = self.data
        face_off = sub["face_off"] + 8
        count = _u32be(d, face_off + 4)

        def idx(i):
            return struct.unpack_from(">H", d, face_off + 12 + i * 2)[0] + 1

        strips = []
        fi = 0
        while fi < count - 3:
            strip = []
            buffer_face = False
            while fi < count - 4:
                tv = idx(fi)
                if len(strip) == 0:
                    if buffer_face:
                        strip.append(0)
                        buffer_face = False
                    strip.append(tv)
                    fi += 1
                elif len(strip) in (1, 2):
                    if tv in strip:
                        break
                    strip.append(tv)
                    fi += 1
                else:
                    if strip[-1] == tv:
                        strips.append(strip)
                        break
                    elif strip[-2] == tv:
                        fi -= 1
                        buffer_face = True
                        strips.append(strip)
                        break
                    else:
                        strip.append(tv)
                        fi += 1
            if fi == count - 4:
                strip.append(idx(fi))
                strips.append(strip)
                fi += 1
        faces = []
        for strip in strips:
            s = list(strip)
            cw = True
            if s and s[0] == 0:
                s.pop(0)
                cw = True
            elif len(s) % 2 == 1:
                cw = False
            for i in range(len(s) - 2):
                if s[i] == 0:
                    continue
                if not cw:
                    tri = (s[i], s[i + 1], s[i + 2]) if i % 2 == 1 else \
                        (s[i], s[i + 2], s[i + 1])
                else:
                    tri = (s[i], s[i + 2], s[i + 1]) if i % 2 == 1 else \
                        (s[i], s[i + 1], s[i + 2])
                faces.append((tri[0] - 1, tri[1] - 1, tri[2] - 1))
        return faces

    def bone_centroids(self):
        """Weighted vertex centroid per bone, in file coords (cm).
        Measured from the mesh itself; the anatomically correct bind
        position for each joint. Bones with no influence get None."""
        acc = {}
        for sub in self.subobjects:
            pos = self.read_positions(sub, 0)
            weights = self.read_weights(sub)
            for v, slots in enumerate(weights):
                x, y, z = pos[v]
                for bone, w in slots:
                    a = acc.setdefault(bone, [0.0, 0.0, 0.0, 0.0])
                    a[0] += x * w
                    a[1] += y * w
                    a[2] += z * w
                    a[3] += w
        out = {}
        for bone, (sx, sy, sz, sw) in acc.items():
            if sw > 0:
                out[bone] = (sx / sw, sy / sw, sz / sw)
        return out


def load(path):
    with open(path, "rb") as f:
        return YOBJ(f.read())


if __name__ == "__main__":
    import sys
    y = load(sys.argv[1])
    print(f"sub-objects: {y.sub_count}  bones: {y.bone_count}  "
          f"textures: {y.tex_count}  shaders: {y.shader_count}  "
          f"emotes: {y.emote_count}  struct order: {len(y.struct_order)}")
    tot_v = tot_f = 0
    for s in y.subobjects:
        faces = y.read_faces(s)
        tot_v += s["verts"]
        tot_f += len(faces)
        print(f"  sub{s['index']:2d}: verts={s['verts']:5d} heads={s['heads']:3d} "
              f"weights={s['weight_sets']} tris={len(faces):5d} "
              f"shader={s['shader']} mat={s['material']}")
    print(f"total verts: {tot_v}  total tris: {tot_f}")
