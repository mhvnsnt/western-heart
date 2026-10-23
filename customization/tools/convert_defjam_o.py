#!/usr/bin/env python3
"""Def Jam: Fight for NY CAW part converter (J4 Phase V).

Converts a CAW part `.o` file (EA EAGL object, RefPack-wrapped) into a
glTF binary (.glb), and the part's sibling `.ssh` SHPS texture into a
PNG. Format: teardown/def-jam-fight-for-ny/EAGL-FORMAT-SPEC.md (the
vertex-stream closure is in the Phase V amendment of that spec).

Proven layout used here (evidence in the spec):

  .o --RefPack--> MIPS ELF32 relocatable; .data holds a Morph object:
    root @ "Morph" string target, stream count, then stream objects.
  stream object (32-byte header):
    +0x00 name pointer (relocated; "Coordinates" or "Normals")
    +0x04 1, +0x08 0
    +0x0C u32 strip count
    +0x10 i16 count field, i16 stream marker
          (Coordinates: -8192 / 0xE000; Normals: -16384 / 0xC000)
    +0x14 first strip block (blocks then follow back to back)
  strip block:
    6 x i16 header (vertex count, 0, 0, 0, strip index, 0)
    vertex records (Coordinates: 3 x i16 position; Normals: 6 x i16)
    one pad i16 iff the record area is odd-length in i16 (Coordinates
    with an odd vertex count), then -- on non-final blocks only --
    i16 trailer (undecoded) + i16 stream marker. The final block's
    data ends exactly on the next stream object / end of .data.
  Topology: triangle strips (the compiled _C variant's descriptor
  tables carry the same per-strip vertex counts in the same order,
  and its GeoPrimState is PT_TRIANGLESTRIP).

Positions are quantized i16 in a part-local frame (x mirrored about 0,
z the long axis). POS_SCALE and the axis map below are conversion
choices, documented in the spec: raw i16 / 1024, (x, y, z) ->
(x, z, -y) into glTF's right-handed Y-up frame.

Normals: the file's own Normals stream is framed exactly like the
Coordinates stream, but its payload is a high-entropy encoding that
the PS2 VU1 microcode consumes (byte entropy 7.29 bits/byte, zero
correlation with positions); it is NOT plain i16 vectors and is not
decoded here. GLB normals are computed from the strip geometry
(area-weighted smooth normals) instead -- the standard fallback, and
the catalog records normals_source=computed_from_geometry.

UVs: the A/B .o files carry no STQ/UV stream (CVertexInformation's
m_pSTQ lives in the compiled _C GeoPrim variant, whose packed layout
is still open). The decoded texture PNG is emitted next to the GLB
and referenced from the catalog, but is deliberately NOT bound as a
GLB image: binding a texture without UVs would be fabricating data.

The _C files (compiled GeoPrim variants, ~112 symbols, float-packed
streams) are detected and reported as status=compiled_variant, never
misparsed.

Usage:
  convert_defjam_o.py convert <part.o> <out.glb> [--ssh <tex.ssh>]
                          [--texture-out <tex.png>]
  convert_defjam_o.py batch --src-root <dir> --out-dir <dir>
                          [--index <PARTS-INDEX.json>] [--limit N]
                          [--force]

Batch mode walks *.o under --src-root (or the index's file list),
writes <out-dir>/<slot>/<stem>.glb + texture PNGs when a sibling
*_A01_01.ssh exists, and (re)builds <out-dir>/CATALOG.json in the
registry shape ({parts: [...]}) that
packages/creation-suite/src/catalogs.js merges.
"""

from __future__ import annotations

import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagl_refpack import refpack_decompress, find_refpack_offset  # noqa: E402
from eagl_shps import parse_shps, write_png  # noqa: E402

POS_SCALE = 1.0 / 1024.0
STREAM_RECORD_I16 = {"Coordinates": 3, "Normals": 6}
STREAM_MARKER = {"Coordinates": -8192, "Normals": -16384}


class DefJamError(ValueError):
    pass


class NonRefPackError(DefJamError):
    """The file carries no valid RefPack record (other container or
    corrupt extraction — a population found in the 311/312 families
    during the Phase B batch; classified, never guessed at)."""


# ---------------------------------------------------------------- ELF

def parse_elf(data: bytes) -> dict:
    if data[:4] != b"\x7fELF":
        raise DefJamError("decompressed data is not ELF")
    e_shoff, = struct.unpack("<I", data[32:36])
    e_shentsize, e_shnum, e_shstrndx = struct.unpack("<HHH", data[46:52])
    raw_secs = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        raw_secs.append(struct.unpack("<IIIIIIIIII", data[off:off + 40]))

    def sec_bytes(s):
        return data[s[4]:s[4] + s[5]]

    shstr = sec_bytes(raw_secs[e_shstrndx])

    def name_of(s):
        end = shstr.index(b"\0", s[0])
        return shstr[s[0]:end].decode("latin1")

    secs = {}
    for s in raw_secs:
        secs[name_of(s)] = s
    out = {"sections": secs}
    if ".data" in secs:
        out["data"] = sec_bytes(secs[".data"])
    if ".symtab" in secs and ".strtab" in secs:
        sym, strt = secs[".symtab"], secs[".strtab"]
        strb = sec_bytes(strt)
        symbols = []
        for i in range(sym[5] // 16):
            noff, val, size, info, other, shndx = struct.unpack(
                "<IIIBBH", data[sym[4] + i * 16:sym[4] + i * 16 + 16])
            end = strb.index(b"\0", noff) if noff else noff
            symbols.append({
                "name": strb[noff:end].decode("latin1") if noff else "",
                "value": val, "size": size})
        out["symbols"] = symbols
    if ".rel.data" in secs and ".data" in secs:
        rel = secs[".rel.data"]
        relocs = {}
        for i in range(rel[5] // 8):
            roff, rinfo = struct.unpack(
                "<II", data[rel[4] + i * 8:rel[4] + i * 8 + 8])
            addend = struct.unpack(
                "<I", out["data"][roff:roff + 4])[0] if roff + 4 <= len(out["data"]) else None
            relocs[roff] = {"sym": rinfo >> 8, "type": rinfo & 0xFF,
                            "addend": addend}
        out["relocs"] = relocs
    return out


def _data_string(ddata: bytes, off: int) -> str:
    if off is None or off >= len(ddata):
        return ""
    end = ddata.find(b"\0", off)
    if end < 0:
        return ""
    return ddata[off:end].decode("latin1")


# ------------------------------------------------------------- streams

def find_stream_objects(elf: dict) -> dict:
    """Locate the Morph stream objects via their relocated name ptrs."""
    ddata = elf["data"]
    found = {}
    for roff, rel in elf.get("relocs", {}).items():
        name = _data_string(ddata, rel["addend"])
        if name in STREAM_RECORD_I16:
            if roff + 0x20 <= len(ddata):
                one, zero = struct.unpack("<II", ddata[roff + 4:roff + 12])
                if one == 1 and zero == 0:
                    found[name] = roff
    return found


def parse_stream(elf: dict, obj_off: int, stream_name: str) -> dict:
    """Walk one stream's strip blocks. Returns strips of raw records.

    Each record is a tuple of STREAM_RECORD_I16[stream_name] i16s.
    Raises DefJamError on any framing violation (bad header zeros,
    bad strip index, wrong end marker)."""
    ddata = elf["data"]
    rec_i16 = STREAM_RECORD_I16[stream_name]
    marker = STREAM_MARKER[stream_name]
    strips_count, = struct.unpack("<I", ddata[obj_off + 0x0C:obj_off + 0x10])
    count_field, mark_field = struct.unpack(
        "<hh", ddata[obj_off + 0x10:obj_off + 0x14])
    if mark_field != marker:
        raise DefJamError(
            f"{stream_name}: header marker {mark_field} != {marker}")
    pos = obj_off + 0x14
    strips = []
    trailers = []
    last_idx = -1
    for k in range(strips_count):
        if pos + 12 > len(ddata):
            raise DefJamError(f"{stream_name}: strip {k} header overruns .data")
        hdr = struct.unpack("<6h", ddata[pos:pos + 12])
        count, z1, z2, z3, idx, z5 = hdr
        # The header index is the SOURCE strip id: it normally equals
        # the block position, but parts exist (e.g. V2CP_111_0015)
        # whose ids have gaps (0..26, 28 — 28 blocks, ids spanning a
        # dropped strip). Require strictly increasing ids, not
        # positional equality.
        if count <= 0 or z1 or z2 or z3 or z5 or idx <= last_idx:
            raise DefJamError(
                f"{stream_name}: strip {k} header {hdr} malformed")
        last_idx = idx
        n_i16 = count * rec_i16
        # Coordinates records are 3 x i16; an odd vertex count leaves
        # the data area odd-length, and the format pads it with one
        # extra i16 BEFORE the trailer (proven on real parts: for odd
        # counts the end marker sits 2 bytes later than the unpadded
        # position; even counts have no pad). Normals records are
        # 6 x i16 (always even) and never pad.
        data_i16 = n_i16 + (n_i16 & 1)
        d0 = pos + 12
        d1 = d0 + 2 * data_i16
        if d1 > len(ddata):
            raise DefJamError(f"{stream_name}: strip {k} data overruns .data")
        flat = struct.unpack(f"<{n_i16}h", ddata[d0:d0 + 2 * n_i16])
        records = [tuple(flat[i * rec_i16:(i + 1) * rec_i16])
                   for i in range(count)]
        if k < strips_count - 1:
            # Non-final blocks end with (trailer i16, stream marker).
            # The FINAL block has neither: its data ends exactly on
            # the next stream object (or the end of .data) -- proven
            # on every sample part.
            if d1 + 4 > len(ddata):
                raise DefJamError(
                    f"{stream_name}: strip {k} trailer overruns .data")
            trailer, endmark = struct.unpack("<hh", ddata[d1:d1 + 4])
            if endmark != marker:
                raise DefJamError(
                    f"{stream_name}: strip {k} end marker "
                    f"{endmark} != {marker}")
            trailers.append(trailer)
            block_bytes = 12 + 2 * data_i16 + 4
        else:
            block_bytes = 12 + 2 * data_i16
        strips.append(records)
        pos += block_bytes
    return {
        "strips": strips,
        "trailers": trailers,
        "count_field": count_field,
        "strip_count": strips_count,
        "end_offset": pos,
        "data_start": obj_off + 0x20,
    }


def parse_part(raw: bytes) -> dict:
    """Full parse of one .o file's bytes (still RefPack-wrapped)."""
    off = find_refpack_offset(raw)
    if off < 0:
        raise NonRefPackError("no valid RefPack record found")
    dec = refpack_decompress(raw[off:])
    elf = parse_elf(dec)
    if "data" not in elf:
        raise DefJamError("ELF has no .data section")
    streams = find_stream_objects(elf)
    if "Coordinates" not in streams:
        symnames = [s["name"] for s in elf.get("symbols", [])]
        if any("GeoPrimState" in n for n in symnames):
            return {"kind": "compiled_variant", "elf": elf}
        if any("PosePaletteBank" in n for n in symnames):
            # e.g. V2CP_532_*_C_F.o: a pose-palette object, no mesh.
            return {"kind": "pose_palette_only", "elf": elf}
        raise DefJamError("no Coordinates stream object found")
    coords = parse_stream(elf, streams["Coordinates"], "Coordinates")
    result = {"kind": "morph", "elf": elf, "coords": coords,
              "stream_offsets": streams}
    if "Normals" in streams:
        result["normals"] = parse_stream(elf, streams["Normals"], "Normals")
        if coords["end_offset"] != streams["Normals"]:
            raise DefJamError(
                f"Coordinates stream ends at {coords['end_offset']:#x}, "
                f"Normals object at {streams['Normals']:#x}")
    return result


# ----------------------------------------------------------------- GLB

def build_glb(part: dict, mesh_name: str) -> bytes:
    """Positions + computed smooth normals + strip indices, one mesh."""
    strips = part["coords"]["strips"]
    positions = []
    indices = []
    for strip in strips:
        base = len(positions)
        for (x, y, z) in strip:
            positions.append((x * POS_SCALE, z * POS_SCALE, -y * POS_SCALE))
        for i in range(len(strip) - 2):
            a, b, c = base + i, base + i + 1, base + i + 2
            if i % 2 == 1:
                a, b = b, a
            indices.extend((a, b, c))
    # area-weighted smooth normals
    normals = [[0.0, 0.0, 0.0] for _ in positions]
    for t in range(0, len(indices), 3):
        ia, ib, ic = indices[t:t + 3]
        ax, ay, az = positions[ia]
        bx, by, bz = positions[ib]
        cx, cy, cz = positions[ic]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        for i in (ia, ib, ic):
            normals[i][0] += nx
            normals[i][1] += ny
            normals[i][2] += nz
    for n in normals:
        ln = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
        if ln > 0:
            n[0], n[1], n[2] = n[0] / ln, n[1] / ln, n[2] / ln
        else:
            n[0], n[1], n[2] = 0.0, 1.0, 0.0
    pos_flat = [c for p in positions for c in p]
    nrm_flat = [c for n in normals for c in n]
    bin_parts = []
    bin_data = bytearray()

    def add_view(data: bytes, target: int):
        start = len(bin_data)
        bin_data.extend(data)
        while len(bin_data) % 4:
            bin_data.append(0)
        return {"buffer": 0, "byteOffset": start, "byteLength": len(data),
                "target": target}

    pos_bytes = struct.pack(f"<{len(pos_flat)}f", *pos_flat)
    nrm_bytes = struct.pack(f"<{len(nrm_flat)}f", *nrm_flat)
    idx_bytes = struct.pack(f"<{len(indices)}I", *indices)
    v_pos = add_view(pos_bytes, 34962)
    v_nrm = add_view(nrm_bytes, 34962)
    v_idx = add_view(idx_bytes, 34963)
    mins = [min(p[i] for p in positions) for i in range(3)]
    maxs = [max(p[i] for p in positions) for i in range(3)]
    gltf = {
        "asset": {"version": "2.0",
                  "generator": "convert_defjam_o.py (western-heart J4)"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": mesh_name}],
        "meshes": [{"name": mesh_name, "primitives": [{
            "attributes": {"POSITION": 0, "NORMAL": 1},
            "indices": 2,
            "material": 0,
        }]}],
        "materials": [{"name": "defjam_clay",
                       "pbrMetallicRoughness": {
                           "baseColorFactor": [0.8, 0.8, 0.8, 1.0],
                           "metallicFactor": 0.0,
                           "roughnessFactor": 0.9},
                       "doubleSided": True}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(positions),
             "type": "VEC3", "min": mins, "max": maxs},
            {"bufferView": 1, "componentType": 5126, "count": len(positions),
             "type": "VEC3"},
            {"bufferView": 2, "componentType": 5125, "count": len(indices),
             "type": "SCALAR"},
        ],
        "bufferViews": [v_pos, v_nrm, v_idx],
        "buffers": [{"byteLength": len(bin_data)}],
    }
    js = json.dumps(gltf, sort_keys=True, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    out = bytearray()
    out += struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_data))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(bin_data), 0x004E4942) + bin_data
    return bytes(out)


# ------------------------------------------------------------- drivers

def convert_one(o_path: str, glb_path: str, ssh_path: str = None,
                texture_out: str = None) -> dict:
    raw = open(o_path, "rb").read()
    try:
        part = parse_part(raw)
    except NonRefPackError:
        return {"file": os.path.basename(o_path),
                "status": "no_valid_refpack_record"}
    stem = os.path.splitext(os.path.basename(o_path))[0]
    if part["kind"] in ("compiled_variant", "pose_palette_only"):
        return {"file": os.path.basename(o_path), "status": part["kind"]}
    glb = build_glb(part, stem)
    os.makedirs(os.path.dirname(os.path.abspath(glb_path)), exist_ok=True)
    # Verified write (VM write-flush flakiness: write -> read back ->
    # size + magic check -> one retry).
    for _attempt in range(2):
        with open(glb_path, "wb") as f:
            f.write(glb)
            f.flush()
            os.fsync(f.fileno())
        try:
            with open(glb_path, "rb") as f:
                head = f.read(4)
            if os.path.getsize(glb_path) == len(glb) and head == b"glTF":
                break
        except OSError:
            pass
    else:
        raise DefJamError(f"verified write failed for {glb_path}")
    nverts = sum(len(s) for s in part["coords"]["strips"])
    info = {"file": os.path.basename(o_path), "status": "converted",
            "glb": glb_path, "vertices": nverts,
            "strips": part["coords"]["strip_count"],
            "triangles": (nverts - 2 * part["coords"]["strip_count"]),
            "normals_source": "computed_from_geometry",
            "uv_status": "absent_in_o_file"}
    if ssh_path and texture_out:
        # Texture failure must not fail a good geometry conversion
        # (the 361 family: geometry converted, texture needed the
        # partial-page rule). Record it in the info instead.
        try:
            sraw = open(ssh_path, "rb").read()
            soff = find_refpack_offset(sraw)
            if soff < 0:
                raise DefJamError("texture has no valid RefPack record")
            img = parse_shps(refpack_decompress(sraw[soff:]))
            write_png(texture_out, img["width"], img["height"],
                      img["rgba"])
            info["texture"] = texture_out
            info["texture_size"] = [img["width"], img["height"]]
        except Exception as e:
            info["texture_error"] = f"{type(e).__name__}: {e}"
    return info


def main(argv):
    if len(argv) >= 2 and argv[1] == "convert":
        o_path, glb_path = argv[2], argv[3]
        ssh = tex = None
        rest = argv[4:]
        for i, a in enumerate(rest):
            if a == "--ssh":
                ssh = rest[i + 1]
            elif a == "--texture-out":
                tex = rest[i + 1]
        print(json.dumps(convert_one(o_path, glb_path, ssh, tex)))
        return 0
    if len(argv) >= 2 and argv[1] == "batch":
        args = {}
        rest = argv[2:]
        for i, a in enumerate(rest):
            if a.startswith("--"):
                args[a[2:]] = rest[i + 1] if i + 1 < len(rest) else True
        src_root = args["src-root"]
        out_dir = args["out-dir"]
        limit = int(args.get("limit", 0)) or None
        force = "force" in args
        os.makedirs(out_dir, exist_ok=True)
        slot_by_file = {}
        idx_path = args.get("index")
        if idx_path and isinstance(idx_path, str) and os.path.exists(idx_path):
            with open(idx_path) as f:
                idx = json.load(f)
            for p in idx.get("parts", []):
                slot_by_file[os.path.basename(p["file_path"])] = p["slot"]
        o_files = []
        for root, _dirs, files in os.walk(src_root):
            for fn in sorted(files):
                if fn.endswith(".o"):
                    o_files.append(os.path.join(root, fn))
        o_files.sort()
        start = int(args.get("start", 0)) or 0
        if start:
            o_files = o_files[start:]
        if limit:
            o_files = o_files[:limit]
        # Merge with any existing catalog so windowed runs compose.
        parts_by_id = {}
        cat_path = os.path.join(out_dir, "CATALOG.json")
        if os.path.exists(cat_path):
            try:
                with open(cat_path) as f:
                    for p in json.load(f).get("parts", []):
                        parts_by_id[p["id"]] = p
            except (OSError, ValueError):
                parts_by_id = {}
        parts = []
        counts = {"converted": 0, "compiled_variant": 0, "error": 0,
                  "skipped_existing": 0}
        for o_path in o_files:
            stem = os.path.splitext(os.path.basename(o_path))[0]
            slot = slot_by_file.get(os.path.basename(o_path))
            if slot is None:
                slot = "unknown"
                for code, sname in (("_110_", "head"), ("_111_", "upper_body"),
                                    ("_112_", "lower_body"),
                                    ("_113_", "accessories")):
                    if code in stem:
                        slot = sname
            glb_path = os.path.join(out_dir, slot, stem + ".glb")
            if os.path.exists(glb_path) and not force:
                counts["skipped_existing"] += 1
                entry = {"id": f"defjam:{stem}.o", "name": stem,
                         "source_game": "defjam", "slot": slot,
                         "file": f"{slot}/{stem}.glb", "glb": glb_path,
                         "status": "converted",
                         "normals_source": "computed_from_geometry",
                         "uv_status": "absent_in_o_file"}
                tex_png = os.path.join(out_dir, slot, stem + ".png")
                if os.path.exists(tex_png):
                    entry["texture"] = tex_png
                parts.append(entry)
                continue
            # Textures: a part may carry several sibling .ssh
            # variants (<base>_A01_01.ssh, _A01_02.ssh, ...). Decode
            # them all; convert_one binds the first for its return
            # info, the rest are decoded here as sibling PNGs.
            base = o_path.rsplit("_", 1)[0]
            import glob as _glob
            siblings = sorted(_glob.glob(base + "_*.ssh"))
            ssh = siblings[0] if siblings else None
            tex_out = None
            if ssh:
                ssh_stem = os.path.splitext(os.path.basename(ssh))[0]
                tex_out = os.path.join(out_dir, slot, ssh_stem + ".png")
            try:
                info = convert_one(o_path, glb_path, ssh, tex_out)
                counts[info["status"]] = counts.get(info["status"], 0) + 1
                if info["status"] == "converted":
                    entry = {"id": f"defjam:{stem}.o", "name": stem,
                             "source_game": "defjam", "slot": slot,
                             "file": f"{slot}/{stem}.glb", "glb": glb_path,
                             "status": "converted",
                             "vertices": info["vertices"],
                             "normals_source": info["normals_source"],
                             "uv_status": info["uv_status"]}
                    textures = []
                    if "texture" in info:
                        textures.append(info["texture"])
                    for extra in siblings[1:]:
                        try:
                            eraw = open(extra, "rb").read()
                            eoff = find_refpack_offset(eraw)
                            if eoff < 0:
                                continue
                            eimg = parse_shps(refpack_decompress(eraw[eoff:]))
                            estem = os.path.splitext(
                                os.path.basename(extra))[0]
                            eout = os.path.join(out_dir, slot,
                                                estem + ".png")
                            write_png(eout, eimg["width"],
                                      eimg["height"], eimg["rgba"])
                            textures.append(eout)
                        except Exception:
                            counts["texture_error"] = \
                                counts.get("texture_error", 0) + 1
                    if textures:
                        entry["texture"] = textures[0]
                        if len(textures) > 1:
                            entry["textures"] = textures
                    if info.get("texture_error"):
                        entry["texture_error"] = info["texture_error"]
                    parts.append(entry)
                else:
                    parts.append({"id": f"defjam:{stem}.o", "name": stem,
                                  "source_game": "defjam", "slot": slot,
                                  "file": None, "status": info["status"]})
            except Exception as e:  # per-file isolation, status logged
                counts["error"] += 1
                parts.append({"id": f"defjam:{stem}.o", "name": stem,
                              "source_game": "defjam", "slot": slot,
                              "file": None, "status": f"error: {e}"})
        for p in parts:
            parts_by_id[p["id"]] = p
        merged = [parts_by_id[k] for k in sorted(parts_by_id)]
        # Verified write: dump to temp, read back, then rename.
        tmp_cat = cat_path + ".tmp"
        with open(tmp_cat, "w") as f:
            json.dump({"parts": merged}, f, indent=1)
            f.flush()
            os.fsync(f.fileno())
        with open(tmp_cat) as f:
            json.load(f)
        os.replace(tmp_cat, cat_path)
        print(json.dumps({"counts": counts, "total": len(o_files),
                          "catalog_total": len(merged)}))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
