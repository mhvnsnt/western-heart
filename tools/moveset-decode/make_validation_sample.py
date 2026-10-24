#!/usr/bin/env python3
"""
make_validation_sample.py - builds a SPEC-BUILT TKM2 validation fixture.

*** THIS DOES NOT EXTRACT ANYTHING FROM ANY GAME. ***
No real .tkmvst sample exists on this machine (see sample/README.md for the
search evidence). This builder constructs a minimal binary directly from the
struct specifications in the vendored TKMovesets sources
(MovesetStructs.h + Structs_t7.h + Extractor_t7.cpp), writing every field at
explicit byte offsets taken from those headers - it deliberately does NOT
import tkm2_decode, so decoding this file with tkm2_decode.py and comparing
against ground_truth.json is a genuine field-for-field check of the decoder.

The character ("ValidationVera", characterId 999) and all move names
(VAL_ prefix) are fictional and invented for this fixture.

Layout follows ExtractorT7::Extract exactly:
  [TKMovesetHeader 256][TKMovesetProperty list][block offset list][moveset data]
  moveset data = movesetInfo | table | motaList | names | moveset | anims | mota | movelist
  every block 8-byte aligned; in-move pointer fields stored as list indexes
  (TO_INDEX, -1 = null); move names as byte offsets into the name block;
  table offsets relative to the moveset block start.
"""

import json
import struct
import sys
import zlib

# ---- explicit offsets from MovesetStructs.h (TKMovesetHeader) ----
H_SIGNATURE = 0        # char[4] "TKM2"
H_VERSION = 4          # char[28]
H_GAMEVERSIONHASH = 32  # Byte[32]
H_GAMEID = 64          # uint16 (0 = T7, GameIDs.hpp)
H_MINORVERSION = 66    # uint16
H_HEADER_SIZE = 68     # uint32
H_BLOCK_LIST = 72      # uint32
H_BLOCK_LIST_SIZE = 76  # uint32
H_DATA_START = 80      # uint32
H_DATA_SIZE = 88       # uint64
H_COMPRESSION = 96     # uint8 (0 = None)
H_CRC32 = 100          # uint32
H_ORIG_CRC32 = 104     # uint32
H_DATE = 112           # uint64
H_EXTRACTION_DATE = 120  # uint64
H_CHARACTERID = 128    # uint32
H_FLAGS = 136          # uint64
H_ORIGIN = 144         # char[32]
H_TARGET = 176         # char[32]
H_ORIGCHAR = 208       # char[32]
H_GAMESPECIFIC = 240   # uint64
H_CONVERSION = 248     # uint16
HEADER_SIZE = 256

# ---- explicit sizes from Structs_t7.h ----
SZ_MOVE = 176
SZ_HITCOND = 24
SZ_REQ = 8
SZ_CANCEL = 40
SZ_REACTIONS = 112
SZ_PUSHBACK = 16
SZ_PUSHBACK_EXTRA = 2
SZ_CANCEL_EXTRA = 4
SZ_EXTRAPROP = 12
SZ_OTHERPROP = 16
SZ_VOICECLIP = 4
SZ_INPUTSEQ = 16
SZ_INPUT = 8
SZ_PARR = 4
SZ_CAMDATA = 12
SZ_THROWCAM = 16
SZ_PROJECTILE = 168
SZ_TABLE = 304
SZ_INFO_PREFIX = 336
SZ_MOTALIST = 13 * 8

TABLE_ORDER = [  # StructsT7::MovesetTable declaration order
    ("reactions", SZ_REACTIONS), ("requirement", SZ_REQ),
    ("hitCondition", SZ_HITCOND), ("projectile", SZ_PROJECTILE),
    ("pushback", SZ_PUSHBACK), ("pushbackExtradata", SZ_PUSHBACK_EXTRA),
    ("cancel", SZ_CANCEL), ("groupCancel", SZ_CANCEL),
    ("cancelExtradata", SZ_CANCEL_EXTRA), ("extraMoveProperty", SZ_EXTRAPROP),
    ("moveBeginningProp", SZ_OTHERPROP), ("moveEndingProp", SZ_OTHERPROP),
    ("move", SZ_MOVE), ("voiceclip", SZ_VOICECLIP),
    ("inputSequence", SZ_INPUTSEQ), ("input", SZ_INPUT),
    ("unknownParryRelated", SZ_PARR), ("cameraData", SZ_CAMDATA),
    ("throwCameras", SZ_THROWCAM),
]

CHARACTER = "ValidationVera"
MOVES = [
    # name, anim_name, vuln, hitlevel, cancel_idx, transition, hc_idx, damage_via_hc,
    # anim_len, air_start, air_end, ground_fall, voice_idx, extra_idx, hitbox, first, last, distance
    ("VAL_jab", "VAL_jab_anim", 0, 2, 0, 32769, 0, 12, 35, 0, 0, 0, 0, 0, 21, 10, 12, 0),
    ("VAL_elbow_smash", "VAL_elbow_anim", 0, 2, 1, 32770, 1, 20, 41, 0, 0, 0, -1, 1, 22, 13, 15, 0),
    ("VAL_launcher_upper", "VAL_launcher_anim", 0, 1, 2, 32771, 2, 35, 58, 20, 45, 30, 1, -1, 23, 27, 29, 10),
]
HITCONDS = [  # (requirement_idx, damage, reactions_idx)
    (0, 12, 0), (-1, 20, 0), (1, 35, -1),
]
REQUIREMENTS = [  # (condition, param_u32)
    (1100, 7), (2200, struct.unpack("<I", struct.pack("<f", 1.5))[0]),
    (3300, struct.unpack("<I", struct.pack("<i", -5))[0]), (0, 0),
]


def align8(n):
    return n if n % 8 == 0 else n + (8 - n % 8)


def build():
    # ---------- name block ----------
    name_block = bytearray()
    name_off = {}

    def add_name(s):
        off = len(name_block)
        name_block.extend(s.encode("ascii") + b"\x00")
        return off

    char_name_off = add_name(CHARACTER)
    creator_off = add_name("ValidationFixture")
    date_off = add_name("20/10/2026")
    fulldate_off = add_name("20/10/2026 08:00:00")
    for m in MOVES:
        name_off[m[0]] = add_name(m[0])
        name_off[m[1]] = add_name(m[1])
    while len(name_block) % 8:
        name_block.append(0)

    # ---------- moveset block (lists in table order, contiguous) ----------
    counts = {
        "reactions": 1, "requirement": len(REQUIREMENTS),
        "hitCondition": len(HITCONDS), "projectile": 1, "pushback": 2,
        "pushbackExtradata": 2, "cancel": 3, "groupCancel": 1,
        "cancelExtradata": 2, "extraMoveProperty": 2, "moveBeginningProp": 1,
        "moveEndingProp": 1, "move": len(MOVES), "voiceclip": 2,
        "inputSequence": 1, "input": 2, "unknownParryRelated": 1,
        "cameraData": 1, "throwCameras": 1,
    }
    offsets = {}
    cursor = 0
    for name, size in TABLE_ORDER:
        offsets[name] = cursor
        cursor += size * counts[name]
    ms = bytearray(cursor)

    # reactions[0]: 7 pushback indexes, 6 directions, 16 moveids (offsets per Structs_t7.h)
    struct.pack_into("<7q", ms, offsets["reactions"] + 0, 0, 1, 0, 0, 0, -1, 1)
    struct.pack_into("<6H", ms, offsets["reactions"] + 56, 1, 2, 3, 4, 5, 6)
    struct.pack_into("<16H", ms, offsets["reactions"] + 76,
                     100, 101, 102, 103, 104, 105, 106, 107,
                     108, 109, 110, 111, 112, 113, 114, 115)
    # requirements
    for i, (cond, param) in enumerate(REQUIREMENTS):
        struct.pack_into("<II", ms, offsets["requirement"] + i * SZ_REQ, cond, param)
    # hit conditions: requirement idx (q), damage (I), _0xC (I), reactions idx (q)
    for i, (rq, dmg, rx) in enumerate(HITCONDS):
        struct.pack_into("<qIIq", ms, offsets["hitCondition"] + i * SZ_HITCOND, rq, dmg, 0, rx)
    # projectile[0]: vfx_id@0, delay@24, velocities@28/32, duration@40, hit_level@56,
    # hit_condition idx@96, cancel idx@104, can_hitbox_connect@120, gravity@132
    struct.pack_into("<I", ms, offsets["projectile"] + 0, 4242)
    struct.pack_into("<I", ms, offsets["projectile"] + 24, 5)
    struct.pack_into("<I", ms, offsets["projectile"] + 56, 2)
    struct.pack_into("<q", ms, offsets["projectile"] + 96, 1)
    struct.pack_into("<q", ms, offsets["projectile"] + 104, 0)
    # pushbacks
    struct.pack_into("<HHIq", ms, offsets["pushback"] + 0, 10, 120, 1, 0)
    struct.pack_into("<HHIq", ms, offsets["pushback"] + 16, 12, 140, 1, 1)
    struct.pack_into("<H", ms, offsets["pushbackExtradata"] + 0, 55)
    struct.pack_into("<H", ms, offsets["pushbackExtradata"] + 2, 66)
    # cancels: command(Q) req(q) extra(q) det_start(I) det_end(I) start_frame(I) move_id(H) option(H)
    for i in range(3):
        struct.pack_into("<QqqIIIHH", ms, offsets["cancel"] + i * SZ_CANCEL,
                         0x100 + i, 0 if i == 0 else -1, 0, 1, 30, 5, 100 + i, 0)
    struct.pack_into("<QqqIIIHH", ms, offsets["groupCancel"], 0x200, -1, -1, 1, 99, 1, 200, 0)
    struct.pack_into("<I", ms, offsets["cancelExtradata"] + 0, 777)
    struct.pack_into("<I", ms, offsets["cancelExtradata"] + 4, 888)
    # extra move properties: starting_frame, id, value
    struct.pack_into("<III", ms, offsets["extraMoveProperty"] + 0, 3, 5001, 42)
    struct.pack_into("<III", ms, offsets["extraMoveProperty"] + 12, 6, 5002, 43)
    struct.pack_into("<qII", ms, offsets["moveBeginningProp"], 2, 881, 9)
    struct.pack_into("<qII", ms, offsets["moveEndingProp"], -1, 881, 10)
    # moves (offsets per Structs_t7.h Move declaration; see tkm2_decode.py header comment)
    anim_offsets = [0, 32, 32]
    for i, m in enumerate(MOVES):
        base = offsets["move"] + i * SZ_MOVE
        struct.pack_into("<Q", ms, base + 0, name_off[m[0]])       # name_addr -> name block offset
        struct.pack_into("<Q", ms, base + 8, name_off[m[1]])       # anim_name_addr
        struct.pack_into("<Q", ms, base + 16, anim_offsets[i])     # anim_addr -> animation block offset
        struct.pack_into("<I", ms, base + 24, m[2])                # vuln
        struct.pack_into("<I", ms, base + 28, m[3])                # hitlevel
        struct.pack_into("<q", ms, base + 32, m[4])                # cancel index
        struct.pack_into("<q", ms, base + 40, -1)
        struct.pack_into("<q", ms, base + 56, -1)
        struct.pack_into("<q", ms, base + 72, -1)
        struct.pack_into("<H", ms, base + 84, m[5])                # transition
        struct.pack_into("<H", ms, base + 88, i + 1)               # moveId_val1
        struct.pack_into("<H", ms, base + 90, 999)                 # moveId_val2 (fictional char id)
        struct.pack_into("<q", ms, base + 96, m[6])                # hit_condition index
        struct.pack_into("<i", ms, base + 104, m[8])               # anim_len
        struct.pack_into("<I", ms, base + 108, m[9])               # airborne_start
        struct.pack_into("<I", ms, base + 112, m[10])              # airborne_end
        struct.pack_into("<I", ms, base + 116, m[11])              # ground_fall
        struct.pack_into("<q", ms, base + 120, m[12])              # voiceclip index
        struct.pack_into("<q", ms, base + 128, m[13])              # extra_move_property index
        struct.pack_into("<q", ms, base + 136, 0 if i == 0 else -1)  # move_start prop
        struct.pack_into("<q", ms, base + 144, 0 if i == 0 else -1)  # move_end prop
        struct.pack_into("<I", ms, base + 156, m[14])              # hitbox_location
        struct.pack_into("<I", ms, base + 160, m[15])              # first_active_frame (startup)
        struct.pack_into("<I", ms, base + 164, m[16])              # last_active_frame
        struct.pack_into("<H", ms, base + 170, m[17])              # distance
    struct.pack_into("<I", ms, offsets["voiceclip"] + 0, 6001)
    struct.pack_into("<I", ms, offsets["voiceclip"] + 4, 6002)
    struct.pack_into("<HHIq", ms, offsets["inputSequence"], 12, 2, 0, 0)
    struct.pack_into("<Q", ms, offsets["input"] + 0, 0x11)
    struct.pack_into("<Q", ms, offsets["input"] + 8, 0x22)
    struct.pack_into("<I", ms, offsets["cameraData"] + 4, 0)  # (fields left zero except marker below)
    struct.pack_into("<H", ms, offsets["cameraData"] + 6, 7001)
    struct.pack_into("<Qq", ms, offsets["throwCameras"], 1, 0)

    # ---------- movesetInfo prefix ----------
    info = bytearray(SZ_INFO_PREFIX)
    info[2] = 1  # isInitialized
    NAME_GAME_BASE = 0x2E5  # ExtractorT7::CopyNameBlock base (see decoder)
    struct.pack_into("<Q", info, 8, NAME_GAME_BASE + char_name_off)
    struct.pack_into("<Q", info, 16, NAME_GAME_BASE + creator_off)
    struct.pack_into("<Q", info, 24, NAME_GAME_BASE + date_off)
    struct.pack_into("<Q", info, 32, NAME_GAME_BASE + fulldate_off)
    struct.pack_into("<56H", info, 40, *([100 + i for i in range(56)]))
    struct.pack_into("<56H", info, 152, *([100 + i for i in range(56)]))

    # ---------- table block ----------
    table = bytearray()
    for name, _size in TABLE_ORDER:
        table += struct.pack("<QQ", offsets[name], counts[name])
    assert len(table) == SZ_TABLE

    motalist = bytearray(struct.pack("<13q", *([-1] * 13)))
    anim_block = bytearray(64)
    anim_block[0] = 0x64  # animation type marker byte (TAnimUtils 0x64 family)
    mota_block = bytearray(8)
    movelist_block = bytearray(8)

    # ---------- assemble moveset data with 8-aligned block offsets ----------
    data_blocks = [bytes(info), bytes(table), bytes(motalist), bytes(name_block),
                   bytes(ms), bytes(anim_block), bytes(mota_block), bytes(movelist_block)]
    block_offsets = []
    cur = 0
    for b in data_blocks:
        block_offsets.append(cur)
        cur += align8(len(b))

    # ---------- header + properties + block list ----------
    properties = struct.pack("<ii", 0, 0)  # single TKMovesetProperty_END
    block_list_off = HEADER_SIZE + align8(len(properties))       # 264
    data_start = block_list_off + align8(8 * 8)                  # 328

    crc = 0
    for blk in [properties, data_blocks[0], data_blocks[1], data_blocks[2],
                data_blocks[4], data_blocks[5], data_blocks[6]]:
        crc = zlib.crc32(blk, crc)
    crc &= 0xFFFFFFFF

    header = bytearray(HEADER_SIZE)
    header[H_SIGNATURE:H_SIGNATURE + 4] = b"TKM2"
    header[H_VERSION:H_VERSION + 3] = b"1.0"
    struct.pack_into("<H", header, H_GAMEID, 0)                  # GameId_T7
    struct.pack_into("<H", header, H_MINORVERSION, 0)
    struct.pack_into("<I", header, H_HEADER_SIZE, HEADER_SIZE)
    struct.pack_into("<I", header, H_BLOCK_LIST, block_list_off)
    struct.pack_into("<I", header, H_BLOCK_LIST_SIZE, 8)
    struct.pack_into("<I", header, H_DATA_START, data_start)
    struct.pack_into("<Q", header, H_DATA_SIZE, 0)               # uncompressed
    header[H_COMPRESSION] = 0
    struct.pack_into("<I", header, H_CRC32, crc)
    struct.pack_into("<I", header, H_ORIG_CRC32, crc)
    struct.pack_into("<Q", header, H_DATE, 1760889600)
    struct.pack_into("<Q", header, H_EXTRACTION_DATE, 1760889600)
    struct.pack_into("<I", header, H_CHARACTERID, 999)
    struct.pack_into("<Q", header, H_FLAGS, 0)
    header[H_ORIGIN:H_ORIGIN + 8] = b"Tekken 7"
    header[H_TARGET:H_TARGET + len(CHARACTER)] = CHARACTER.encode()
    header[H_ORIGCHAR:H_ORIGCHAR + len(CHARACTER)] = CHARACTER.encode()

    out = bytearray()
    out += header
    out += properties
    while len(out) % 8:
        out.append(0xDD)  # extractor pads with 0xDD (Helpers::align8Bytes)
    out += struct.pack("<8Q", *block_offsets)
    while len(out) % 8:
        out.append(0xDD)
    assert len(out) == data_start, len(out)
    for b in data_blocks:
        out += b
        while len(out) % 8:
            out.append(0xDD)

    truth = {
        "character": CHARACTER, "character_id": 999, "game": "T7", "game_id": 0,
        "origin": "Tekken 7", "crc32": f"{crc:08X}",
        "moves": [
            {"name": m[0], "anim_name": m[1], "damage": m[7],
             "first_active_frame": m[15], "last_active_frame": m[16],
             "anim_len_frames": m[8], "hitbox_location": m[14],
             "hit_condition_index": m[6], "cancel_index": m[4],
             "transition": m[5]}
            for m in MOVES
        ],
        "table_counts": counts,
    }
    return bytes(out), truth


if __name__ == "__main__":
    sample_path = sys.argv[1] if len(sys.argv) > 1 else "spec_validation_sample.tkmvst"
    truth_path = sys.argv[2] if len(sys.argv) > 2 else "ground_truth.json"
    blob, truth = build()
    with open(sample_path, "wb") as f:
        f.write(blob)
    with open(truth_path, "w") as f:
        json.dump(truth, f, indent=2)
    print(f"built {sample_path} ({len(blob)} bytes), crc32={truth['crc32']}")
