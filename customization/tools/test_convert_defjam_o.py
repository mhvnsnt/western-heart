#!/usr/bin/env python3
"""Tests for convert_defjam_o.py + eagl_shps.py (J4 Phase V).

Run directly:  python3 test_convert_defjam_o.py
(pytest cannot start on the dev box — tempdir unavailable — so this
file is a plain script with assert-based checks and a PASS summary,
same convention as test_eagl_refpack.py.)

All fixtures are SYNTHETIC (built in this file): a minimal MIPS ELF32
relocatable carrying a Morph object with known Coordinates/Normals
strip blocks, RefPack-wrapped with a literal-only stream; and a
minimal SHPS image with known pixels. No game data is needed.
"""

import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_defjam_o as C  # noqa: E402
import eagl_shps as S  # noqa: E402

PASS = []


def check(name, cond):
    assert cond, f"FAIL: {name}"
    PASS.append(name)


# ------------------------------------------------------- RefPack wrap

def refpack_wrap_literal(raw: bytes) -> bytes:
    """Literal-only RefPack stream (valid per the published spec)."""
    assert len(raw) % 4 == 0
    out = bytearray(b"\x10\xfb" + len(raw).to_bytes(3, "big"))
    i = 0
    while i < len(raw):
        n = min(112, len(raw) - i)  # 0xE0|((n-4)>>2) must stay < 0xFC
        if len(raw) - i - n in (1, 2, 3):  # keep last chunk >= 4
            n -= 4
        out.append(0xE0 | ((n - 4) >> 2))
        out += raw[i:i + n]
        i += n
    out.append(0xFC)
    return bytes(out)


# ------------------------------------------------------ synthetic ELF

def build_synthetic_o() -> bytes:
    """ELF with .data: strings + Morph + Coordinates/Normals streams.

    Coordinates: strip0 = 4 verts, strip1 = 3 verts (known positions).
    Normals: 2 strips, 6xi16 records (payload arbitrary for framing).
    """
    ddata = bytearray(0x400)
    # strings
    s_morph = 0x100
    s_coord = 0x110
    s_norm = 0x120
    ddata[s_morph:s_morph + 6] = b"Morph\0"
    ddata[s_coord:s_coord + 12] = b"Coordinates\0"
    ddata[s_norm:s_norm + 8] = b"Normals\0"
    morph = 0x140
    coords_obj = morph + 0x1C
    # Morph root: name ptr @+0, 0 @+4, 1 @+8, ptr @+0xC, ptr @+0x10,
    # 0 @+0x14, stream count 2 @+0x18
    struct.pack_into("<I", ddata, morph + 0x0C, morph)
    struct.pack_into("<I", ddata, morph + 0x10, morph + 8)
    struct.pack_into("<I", ddata, morph + 0x18, 2)

    def stream_obj(off, name_off, strips, marker, rec_i16, first_count):
        struct.pack_into("<I", ddata, off + 0x00, name_off)
        struct.pack_into("<II", ddata, off + 0x04, 1, 0)
        struct.pack_into("<I", ddata, off + 0x0C, len(strips))
        struct.pack_into("<hh", ddata, off + 0x10, first_count, marker)
        pos = off + 0x14
        for k, records in enumerate(strips):
            flat = [v for rec in records for v in rec]
            struct.pack_into("<6h", ddata, pos, len(records), 0, 0, 0, k, 0)
            struct.pack_into(f"<{len(flat)}h", ddata, pos + 12, *flat)
            data_i16 = len(flat) + (len(flat) & 1)  # format pad (odd counts)
            if k < len(strips) - 1:  # final block: no trailer/marker
                struct.pack_into("<hh", ddata, pos + 12 + 2 * data_i16,
                                 777, marker)
                pos += 12 + 2 * data_i16 + 4
            else:
                pos += 12 + 2 * data_i16
        return pos

    coord_strips = [
        [(100, 200, 300), (-400, 500, -600), (700, -800, 900),
         (-1000, 1100, -1200)],
        [(10, 20, 30), (40, 50, 60), (70, 80, 90)],
    ]
    end = stream_obj(coords_obj, s_coord, coord_strips, -8192, 3, 7)
    norm_obj = end
    norm_strips = [
        [(1, 2, 3, 4, 5, 6)] * 4,
        [(7, 8, 9, 10, 11, 12)] * 3,
    ]
    stream_obj(norm_obj, s_norm, norm_strips, -16384, 6, 14)

    # sections: null, .data, .shstrtab, .strtab, .symtab, .rel.data
    shstr = b"\0.data\0.shstrtab\0.strtab\0.symtab\0.rel.data\0"
    name_off = {".data": 1, ".shstrtab": 7, ".strtab": 17,
                ".symtab": 25, ".rel.data": 33}
    body = bytearray()
    body += b"\x7fELF" + bytes([1, 1, 1, 0]) + bytes(8)  # ident
    # e_type=1, e_machine=8, e_version=1, entry=0, phoff=0, shoff=later
    body += struct.pack("<HHIIIII", 1, 8, 1, 0, 0, 0, 0)
    body += struct.pack("<HHHHHH", 52, 0, 0, 40, 6, 2)  # ehsize..shstrndx
    assert len(body) == 52
    data_off = len(body)
    body += ddata
    shstr_off = len(body)
    body += shstr
    while len(body) % 4:
        body += b"\0"
    strtab_off = len(body)
    body += b"\0"
    symtab_off = len(body)
    body += bytes(16)  # one null symbol
    rel_off = len(body)
    relocs = [(morph, s_morph), (morph + 0x0C, morph),
              (coords_obj, s_coord), (norm_obj, s_norm)]
    for roff, addend in relocs:
        body += struct.pack("<II", roff, (1 << 8) | 2)
    shoff = len(body)
    secs = [
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (name_off[".data"], 1, 0, 0, data_off, len(ddata), 0, 0, 4, 0),
        (name_off[".shstrtab"], 3, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0),
        (name_off[".strtab"], 3, 0, 0, strtab_off, 1, 0, 0, 1, 0),
        (name_off[".symtab"], 2, 0, 0, symtab_off, 16, 3, 1, 4, 16),
        (name_off[".rel.data"], 9, 0, 0, rel_off, len(relocs) * 8, 4, 1, 4, 8),
    ]
    for s in secs:
        body += struct.pack("<IIIIIIIIII", *s)
    struct.pack_into("<I", body, 32, shoff)
    while len(body) % 4:
        body += b"\0"
    return bytes(body)


def test_synthetic_o():
    raw = refpack_wrap_literal(build_synthetic_o())
    part = C.parse_part(raw)
    check("kind is morph", part["kind"] == "morph")
    strips = part["coords"]["strips"]
    check("coords strips == 2", len(strips) == 2)
    check("strip0 verts", strips[0][0] == (100, 200, 300)
          and strips[0][3] == (-1000, 1100, -1200))
    check("strip1 verts", strips[1][2] == (70, 80, 90))
    check("coords end == normals obj",
          part["coords"]["end_offset"] == part["stream_offsets"]["Normals"])
    nrm = part["normals"]
    check("normals strips == 2", len(nrm["strips"]) == 2)
    check("normals record width 6", nrm["strips"][1][0] == (7, 8, 9, 10, 11, 12))
    glb = C.build_glb(part, "synthetic")
    check("glb magic", glb[:4] == b"glTF")
    check("glb version", struct.unpack("<I", glb[4:8])[0] == 2)
    check("glb length field", struct.unpack("<I", glb[8:12])[0] == len(glb))
    import json as _json
    jlen, jtype = struct.unpack("<II", glb[12:20])
    gltf = _json.loads(glb[20:20 + jlen])
    check("glb vertex count 7", gltf["accessors"][0]["count"] == 7)
    check("glb index count 9", gltf["accessors"][2]["count"] == 9)
    # position of vertex 0 = (x, z, -y) * scale
    bin_off = 20 + jlen + 8
    pos = struct.unpack("<3f", glb[bin_off:bin_off + 12])
    check("glb pos0 mapped+scaled",
          abs(pos[0] - 100 * C.POS_SCALE) < 1e-6
          and abs(pos[1] - 300 * C.POS_SCALE) < 1e-6
          and abs(pos[2] - (-200) * C.POS_SCALE) < 1e-6)


# ---------------------------------------------------- synthetic SHPS

def swizzle8(data: bytes, w: int, h: int) -> bytes:
    out = bytearray(len(data))
    for y in range(h):
        for x in range(w):
            block = (y & ~0xF) * w + (x & ~0xF) * 2
            swap = (((y + 2) >> 2) & 0x1) * 4
            pos_y = (((y & ~3) >> 1) + (y & 1)) & 0x7
            col = pos_y * w * 2 + ((x + swap) & 0x7) * 4
            bn = ((y >> 1) & 1) + ((x >> 2) & 2)
            out[block + col + bn] = data[y * w + x]
    return bytes(out)


def build_synthetic_shps() -> bytes:
    w = h = 16
    indices = bytes((i * 7) & 0xFF for i in range(w * h))
    pal = bytearray()
    for i in range(256):
        pal += bytes((i, 255 - i, (i * 3) & 0xFF, 0x80))
    pix_off = 0x80
    pal_hdr_off = pix_off + w * h
    total = pal_hdr_off + 16 + 1024
    out = bytearray(total)
    out[0:4] = b"SHPS"
    struct.pack_into("<II", out, 4, total, 1)
    out[12:16] = b"G359"
    out[16:20] = b"0000"
    struct.pack_into("<I", out, 20, 0x70)
    # image header at 0x70: type 2, next = pal_hdr_off - 0x70
    struct.pack_into("<I", out, 0x70, 2 | ((pal_hdr_off - 0x70) << 8))
    struct.pack_into("<HH", out, 0x74, w, h)
    out[pix_off:pix_off + w * h] = swizzle8(indices, w, h)
    out[pal_hdr_off] = 0x21
    struct.pack_into("<I", out, pal_hdr_off + 4, 0x410)
    out[pal_hdr_off + 16:pal_hdr_off + 16 + 1024] = pal
    return bytes(out)


def test_synthetic_shps():
    data = build_synthetic_shps()
    img = S.parse_shps(data)
    check("shps width/height", img["width"] == 16 and img["height"] == 16)
    check("shps type 2", img["img_type"] == 2)
    first = img["rgba"][:4]
    check("shps pixel0 = palette[0] opaque",
          first == bytes((0, 255, 0, 255)))
    p7 = img["rgba"][7 * 4:7 * 4 + 4]
    idx7 = (7 * 7) & 0xFF
    check("shps pixel7 via unswizzle",
          p7 == bytes((idx7, 255 - idx7, (idx7 * 3) & 0xFF, 255)))


def main():
    test_synthetic_o()
    test_synthetic_shps()
    print(f"PASS {len(PASS)}/{len(PASS)} checks")
    for name in PASS:
        print(f"  ok: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
