#!/usr/bin/env python3
"""
tkm2_decode.py - Python decoder for TKMovesets2 `.tkmvst` moveset files (TKM2 container).

Grounding (vendored upstream, GPL-3.0, Kiloutre/TKMovesets):
  tools/open-source/tkmovesets/TKMovesets2/LocalStorage/MovesetStructs.h
      -> TKMovesetHeader (the TKM2 file header), TKMovesetProperty, compression enum
  tools/open-source/tkmovesets/TKMovesets2/GameSpecific/Structures/Structs_t7.h
      -> StructsT7::TKMovesetHeaderBlocks, MovesetInfo, MovesetTable, Move,
         HitCondition, Requirement, Cancel, Reactions, Pushback, Projectile, ...
  tools/open-source/tkmovesets/TKMovesets2/GameSpecific/Extractors/Extractor_t7/Extractor_t7.cpp
      -> on-disk block order, offset semantics, pointer-to-index conversion
  tools/open-source/tkmovesets/TKMovesets2/GameSpecific/Extractors/Extractor.hpp
      -> TO_INDEX macro: in-file pointer fields are LIST INDEXES (-1 = null),
         except move name fields (byte offsets into the name block) and
         move anim fields (byte offsets into the animation block).

Scope of this version:
  * Full container decode for any gameId (header, properties, block list).
  * Full inner decode for Tekken 7 extractions (GameId_T7 = 0, StructsT7 layout):
    MovesetInfo, MovesetTable (19 lists), Move list with names resolved from the
    name block, damage resolved through HitCondition, plus Requirement / Cancel /
    Reactions / Pushback / ExtraMoveProperty / OtherMoveProperty / InputSequence /
    Input / Voiceclip / Projectile / CameraData / ThrowCamera lists.
  * Other gameIds (T8/TTT2/TREV/T6/T5) use different per-game struct headers
    (Structs_t8.h / Structs_ttt2.h / Structs_t6.h / Structs_t5.h). Their inner
    layouts are NOT decoded yet; the decoder still emits header + block map and
    stops with a clear message instead of guessing offsets.

Stdlib only. Usage:
  python3 tkm2_decode.py <file.tkmvst> [--out decoded.json] [--max-moves N]
"""

import argparse
import json
import struct
import sys
import zlib

# ---------------------------------------------------------------------------
# TKMovesetHeader (MovesetStructs.h) - MSVC x64 natural alignment, 256 bytes.
# Offsets (verified field-by-field against the header declaration order):
#   0   char     _signature[4]        "TKM2"
#   4   char     version_string[28]
#   32  Byte     gameVersionHash[32]
#   64  uint16   gameId               (GameIDs.hpp: 0=T7 1=T8 2=TTT2 3=TREV 4=T6 5=T5)
#   66  uint16   minorVersion
#   68  uint32   header_size          (align8(sizeof(header)) = 256)
#   72  uint32   block_list           absolute file offset of the block offset list
#   76  uint32   block_list_size      number of blocks (8 for T7)
#   80  uint32   moveset_data_start   absolute file offset of moveset data
#   88  uint64   moveset_data_size    uncompressed data size; 0 if not compressed
#   96  uint8    compressionType      0=None 1=LZ4 2=LZMA
#   100 uint32   crc32
#   104 uint32   orig_crc32
#   112 uint64   date                 unix seconds
#   120 uint64   extraction_date      unix seconds
#   128 uint32   characterId
#   136 uint64   flags                (bit0 = MovesetModified, bit1 = Debug)
#   144 char     origin[32]
#   176 char     target_character[32]
#   208 char     orig_character_name[32]
#   240 uint64   game_specific_flags
#   248 uint16   conversion_origin
#   250 padding to 256
# ---------------------------------------------------------------------------
HEADER_FMT = "<4s28s32sHHIIII4xQB3xII4xQQI4xQ32s32s32sQH6x"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
assert HEADER_SIZE == 256, HEADER_SIZE

GAME_IDS = {0: "T7", 1: "T8", 2: "TTT2", 3: "TREV", 4: "T6", 5: "T5"}
COMPRESSION = {0: "None", 1: "LZ4", 2: "LZMA"}

# StructsT7::TKMovesetHeaderBlocks - block order inside moveset data.
BLOCK_NAMES_T7 = [
    "movesetInfoBlock", "tableBlock", "motalistsBlock", "nameBlock",
    "movesetBlock", "animationBlock", "motaBlock", "movelistBlock",
]

# StructsT7::MovesetTable - 19 entries of (uint64 offset, uint64 count).
# Offsets are relative to the START OF THE MOVESET BLOCK (Extractor_t7
# FillMovesetTables subtracts the reactions list address from every entry).
TABLE_ENTRIES_T7 = [
    ("reactions", 112), ("requirement", 8), ("hitCondition", 24),
    ("projectile", 168), ("pushback", 16), ("pushbackExtradata", 2),
    ("cancel", 40), ("groupCancel", 40), ("cancelExtradata", 4),
    ("extraMoveProperty", 12), ("moveBeginningProp", 16),
    ("moveEndingProp", 16), ("move", 176), ("voiceclip", 4),
    ("inputSequence", 16), ("input", 8), ("unknownParryRelated", 4),
    ("cameraData", 12), ("throwCameras", 16),
]
TABLE_FMT_T7 = "<" + "QQ" * 19
TABLE_SIZE_T7 = struct.calcsize(TABLE_FMT_T7)
assert TABLE_SIZE_T7 == 304

# StructsT7::MovesetInfo prefix: offsetof(MovesetInfo, table) = 336 bytes.
MOVESET_INFO_PREFIX_SIZE = 336

# StructsT7_gameAddr::Move - 176 bytes. In-file pointer fields are indexes
# (TO_INDEX) except name/anim fields (byte offsets, see module docstring).
MOVE_FMT = (
    "<QQQII"          # name_off, anim_name_off, anim_off, vuln, hitlevel
    "qqiiqiiqI"        # cancel, cancel_0x28, _0x30, _0x34, cancel_0x38, _0x40, _0x44, cancel_0x48, _0x50
    "HhHHhh"           # transition, _0x56, moveId_val1, moveId_val2, _0x5C, _0x5E
    "q"                # hit_condition index
    "iIII"             # anim_len, airborne_start, airborne_end, ground_fall
    "qqqq"             # voiceclip, extra_move_property, move_start_prop, move_end_prop (indexes)
    "iIII"             # _0x98, hitbox_location, first_active_frame, last_active_frame
    "hHi"              # _0xA8, distance, _0xAC
)
MOVE_SIZE = struct.calcsize(MOVE_FMT)
assert MOVE_SIZE == 176, MOVE_SIZE

HITCOND_FMT = "<qIIq"          # requirement idx, damage, _0xC, reactions idx
assert struct.calcsize(HITCOND_FMT) == 24
REQ_FMT = "<II"                # condition, param (union u32/i32/f32)
CANCEL_FMT = "<QqqIIIHH"       # command, req idx, extradata idx, det start/end, starting frame, move id, option
assert struct.calcsize(CANCEL_FMT) == 40
REACTIONS_FMT = "<7q6HII16H4x"  # 7 pushback idx, 6 directions, _0x44, _0x48, 16 moveids
assert struct.calcsize(REACTIONS_FMT) == 112, struct.calcsize(REACTIONS_FMT)
PUSHBACK_FMT = "<HHIq"         # duration, displacement, num_of_loops, extradata idx
assert struct.calcsize(PUSHBACK_FMT) == 16
EXTRAPROP_FMT = "<III"         # starting_frame, id, value
OTHERPROP_FMT = "<qII"         # requirement idx, extraprop, value
assert struct.calcsize(OTHERPROP_FMT) == 16
INPUTSEQ_FMT = "<HHiq"         # input_window_frames, input_amount, _0x4, input idx
assert struct.calcsize(INPUTSEQ_FMT) == 16


def cstr(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace")


def read_cstr_at(buf: bytes, off: int):
    if off < 0 or off >= len(buf):
        return None
    end = buf.find(b"\x00", off)
    if end == -1:
        end = len(buf)
    s = buf[off:end]
    try:
        return s.decode("utf-8")
    except UnicodeDecodeError:
        return None


class TKM2Error(Exception):
    pass


def parse_header(data: bytes):
    if len(data) < HEADER_SIZE:
        raise TKM2Error(f"file too small for TKMovesetHeader ({len(data)} < 256)")
    v = struct.unpack_from(HEADER_FMT, data, 0)
    hdr = {
        "signature": v[0].decode("ascii", errors="replace"),
        "version_string": cstr(v[1]),
        "game_version_hash_hex": v[2].hex(),
        "game_id": v[3],
        "game": GAME_IDS.get(v[3], f"unknown({v[3]})"),
        "minor_version": v[4],
        "header_size": v[5],
        "block_list_offset": v[6],
        "block_list_size": v[7],
        "moveset_data_start": v[8],
        "moveset_data_size": v[9],
        "compression_type": v[10],
        "compression": COMPRESSION.get(v[10], f"unknown({v[10]})"),
        "crc32": f"{v[11]:08X}",
        "orig_crc32": f"{v[12]:08X}",
        "date": v[13],
        "extraction_date": v[14],
        "character_id": v[15],
        "flags": v[16],
        "origin": cstr(v[17]),
        "target_character": cstr(v[18]),
        "orig_character_name": cstr(v[19]),
        "game_specific_flags": v[20],
        "conversion_origin": v[21],
    }
    # TKMovesetHeader::ValidateHeader()
    if hdr["signature"] != "TKM2":
        raise TKM2Error(f"bad signature {hdr['signature']!r}, expected 'TKM2'")
    if hdr["block_list_size"] == 0:
        raise TKM2Error("ValidateHeader: block_list_size == 0")
    if hdr["block_list_offset"] < hdr["header_size"]:
        raise TKM2Error("ValidateHeader: block_list < header_size")
    if hdr["moveset_data_start"] <= hdr["block_list_offset"]:
        raise TKM2Error("ValidateHeader: moveset_data_start <= block_list")
    return hdr


def parse_properties(data: bytes, hdr):
    """TKMovesetProperty list {int32 id; int32 value} between header and block list."""
    props = []
    off = hdr["header_size"]
    end = hdr["block_list_offset"]
    while off + 8 <= end:
        pid, val = struct.unpack_from("<ii", data, off)
        props.append({"id": pid, "value": val})
        off += 8
        if pid == 0:  # TKMovesetProperty_END
            break
    return props


def parse_block_list(data: bytes, hdr):
    n = hdr["block_list_size"]
    off = hdr["block_list_offset"]
    if off + 8 * n > len(data):
        raise TKM2Error("block list runs past end of file")
    offsets = list(struct.unpack_from(f"<{n}Q", data, off))
    return offsets


def get_block(data: bytes, hdr, offsets, idx):
    """Block bytes: from moveset_data_start + offsets[idx] to the next block (or EOF / data end)."""
    start = hdr["moveset_data_start"] + offsets[idx]
    if idx + 1 < len(offsets):
        end = hdr["moveset_data_start"] + offsets[idx + 1]
    else:
        end = len(data)
    if start > len(data):
        raise TKM2Error(f"block {idx} starts past EOF")
    return data[start:end], start


def unpack_list(block: bytes, base_off: int, count: int, fmt: str, size: int):
    out = []
    for i in range(count):
        out.append(struct.unpack_from(fmt, block, base_off + i * size))
    return out


def decode_t7(data: bytes, hdr, offsets):
    """Full StructsT7 inner decode. Returns dict; raises TKM2Error on inconsistency."""
    if len(offsets) != 8:
        raise TKM2Error(f"T7 block list size is 8, got {len(offsets)}")
    blocks = {}
    block_file_offsets = {}
    for i, name in enumerate(BLOCK_NAMES_T7):
        b, fo = get_block(data, hdr, offsets, i)
        blocks[name] = b
        block_file_offsets[name] = fo

    # --- MovesetInfo prefix (336 bytes) ---
    info_raw = blocks["movesetInfoBlock"][:MOVESET_INFO_PREFIX_SIZE]
    if len(info_raw) < MOVESET_INFO_PREFIX_SIZE:
        raise TKM2Error("movesetInfoBlock smaller than MovesetInfo prefix (336)")
    name_block = blocks["nameBlock"]
    # MovesetInfo string fields are offsets relative to the in-game moveset base;
    # the name block was extracted starting at moveset base + 0x2E5
    # (ExtractorT7::CopyNameBlock: movesetAddr + 0x2E8 - (len("Tkm:") - 1)).
    NAME_BLOCK_GAME_BASE = 0x2E5

    def info_string(field_off):
        (ptr,) = struct.unpack_from("<Q", info_raw, field_off)
        if ptr == 0 or ptr == 0xFFFFFFFFFFFFFFFF:
            return None, ptr
        rel = ptr - NAME_BLOCK_GAME_BASE
        s = read_cstr_at(name_block, rel) if 0 <= rel < len(name_block) else None
        return s, ptr

    char_name, char_name_raw = info_string(8)
    char_creator, char_creator_raw = info_string(16)
    date_s, date_raw = info_string(24)
    fulldate_s, fulldate_raw = info_string(32)
    orig_aliases = list(struct.unpack_from("<56H", info_raw, 40))
    curr_aliases = list(struct.unpack_from("<56H", info_raw, 152))
    moveset_info = {
        "character_name": char_name, "character_name_offset_raw": char_name_raw,
        "character_creator": char_creator, "character_creator_offset_raw": char_creator_raw,
        "date_string": date_s, "fulldate_string": fulldate_s,
        "orig_aliases_first8": orig_aliases[:8],
        "current_aliases_first8": curr_aliases[:8],
    }

    # --- MovesetTable (in tableBlock; entries relative to movesetBlock start) ---
    table_raw = blocks["tableBlock"][:TABLE_SIZE_T7]
    if len(table_raw) < TABLE_SIZE_T7:
        raise TKM2Error("tableBlock smaller than MovesetTable (304)")
    tv = struct.unpack(TABLE_FMT_T7, table_raw)
    table = {}
    for i, (name, size) in enumerate(TABLE_ENTRIES_T7):
        table[name] = {"offset_in_moveset_block": tv[2 * i], "count": tv[2 * i + 1],
                       "struct_size": size}

    ms = blocks["movesetBlock"]

    def check_range(entry, name):
        e = table[entry]
        need = e["offset_in_moveset_block"] + e["count"] * e["struct_size"]
        if need > len(ms):
            raise TKM2Error(
                f"table entry {name}: offset+count*size = {need} exceeds movesetBlock {len(ms)}")

    for name, _ in TABLE_ENTRIES_T7:
        check_range(name, name)

    # --- Sub-lists needed to resolve move fields ---
    def list_offsets(entry):
        e = table[entry]
        return e["offset_in_moveset_block"], e["count"]

    hc_off, hc_count = list_offsets("hitCondition")
    hit_conditions = []
    for v in unpack_list(ms, hc_off, hc_count, HITCOND_FMT, 24):
        hit_conditions.append({"requirement_index": v[0], "damage": v[1],
                               "_0xC_int": v[2], "reactions_index": v[3]})

    req_off, req_count = list_offsets("requirement")
    requirements = []
    for v in unpack_list(ms, req_off, req_count, REQ_FMT, 8):
        requirements.append({
            "condition": v[0], "param_unsigned": v[1],
            "param_signed": struct.unpack("<i", struct.pack("<I", v[1]))[0],
            "param_float": struct.unpack("<f", struct.pack("<I", v[1]))[0],
        })

    # --- Moves ---
    mv_off, mv_count = list_offsets("move")
    moves = []
    for idx, v in enumerate(unpack_list(ms, mv_off, mv_count, MOVE_FMT, MOVE_SIZE)):
        name = read_cstr_at(name_block, v[0])
        anim_name = read_cstr_at(name_block, v[1])
        hc_idx = v[20]
        damage = None
        if 0 <= hc_idx < len(hit_conditions):
            damage = hit_conditions[hc_idx]["damage"]
        moves.append({
            "index": idx,
            "name": name,
            "anim_name": anim_name,
            "name_offset_in_name_block": v[0],
            "anim_offset_in_animation_block": v[2],
            "vuln": v[3],
            "hitlevel": v[4],
            "cancel_index": v[5],
            "transition": v[14],
            "move_id_val1": v[16],
            "move_id_val2": v[17],
            "hit_condition_index": hc_idx,
            "damage": damage,
            "anim_len_frames": v[21],
            "airborne_start": v[22],
            "airborne_end": v[23],
            "ground_fall": v[24],
            "voiceclip_index": v[25],
            "extra_move_property_index": v[26],
            "hitbox_location": v[30],
            "first_active_frame": v[31],
            "last_active_frame": v[32],
            "distance": v[34],
        })

    return {
        "moveset_info": moveset_info,
        "block_file_offsets": block_file_offsets,
        "block_sizes_on_disk": {k: len(v) for k, v in blocks.items()},
        "table": table,
        "hit_conditions": hit_conditions,
        "requirements": requirements,
        "moves": moves,
    }


def decode(path: str):
    with open(path, "rb") as f:
        data = f.read()
    hdr = parse_header(data)
    result = {
        "file": path,
        "file_size": len(data),
        "header": hdr,
        "properties": parse_properties(data, hdr),
    }
    if hdr["compression_type"] != 0:
        result["decode_status"] = (
            f"compressed ({hdr['compression']}); container header decoded, "
            "payload decompression not attempted by this stdlib-only decoder "
            "(LZ4 is not in the Python stdlib; LZMA payload byte layout needs a "
            "real compressed sample to verify against - see README limits)"
        )
        return result
    offsets = parse_block_list(data, hdr)
    result["block_offsets_relative_to_moveset_data_start"] = offsets
    if hdr["game_id"] == 0:  # GameId_T7
        result["t7"] = decode_t7(data, hdr, offsets)
        result["decode_status"] = "full T7 decode"
    else:
        result["decode_status"] = (
            f"container decoded; inner moveset layout for {hdr['game']} uses a "
            "different per-game struct header (see README) and is not decoded yet"
        )
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Decode a TKMovesets2 .tkmvst (TKM2) file to JSON")
    ap.add_argument("file")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    ap.add_argument("--max-moves", type=int, default=None,
                    help="trim the moves array in the output (file itself is fully parsed)")
    args = ap.parse_args(argv)
    try:
        result = decode(args.file)
    except (TKM2Error, struct.error) as e:
        print(f"tkm2_decode: error: {e}", file=sys.stderr)
        return 1
    if args.max_moves is not None and "t7" in result:
        total = len(result["t7"]["moves"])
        result["t7"]["moves"] = result["t7"]["moves"][: args.max_moves]
        result["t7"]["moves_total"] = total
    text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
