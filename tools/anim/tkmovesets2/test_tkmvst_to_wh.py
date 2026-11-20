#!/usr/bin/env python3
"""Tests for tkmvst_to_wh.py — all fixtures built in memory, no disk writes.

Builds a minimal but spec-conformant Tekken 7 .tkmvst (TKM2 header, 8
blocks, uncompressed) modelling King's front 1+3 throw with the REAL King
move ids (1785 throw, 2125 throw-motion, 2400 receiver), then asserts the
throw triple resolves exactly as the conflict resolution says it must:

  throw move 1785 -> cancel on requirement 3 (Throw Hit Forward)
                     -> 2125 (thrower's throw motion)
  throw move 1785 -> HitCondition -> ReactionList standing
                     -> 2400 (victim's receiver, in the SAME moveset)
  throw move 1785 -> ExtraMoveProperty 0x83C3 present (balcony-break EMP,
                     must be reported, must NOT be mistaken for the receiver)

Also covers: alias resolution via current_aliases, the 0x64/0xC8 layout
reader (happy path + rejection paths + big-endian swapped blob), and the
wh-anim/1 clip validator (ok case + frame-mismatch case).

Run:  python3 test_tkmvst_to_wh.py
Exit 0 = all assertions passed. No files are read or written.
"""

import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tkmvst_to_wh as T

MISSING = 0xFFFFFFFFFFFFFFFF


def u16(v):
    return struct.pack("<H", v)


def u32(v):
    return struct.pack("<I", v)


def u64(v):
    return struct.pack("<Q", v)


def c8_blob(bones, frames):
    """Minimal valid 0xC8 blob (header + zeroed frames)."""
    size = 8 + bones * 4 + bones * 12 * frames
    b = bytearray(size)
    b[0:2] = u16(0xC8)
    b[2:4] = u16(bones)
    b[4:8] = u32(frames)
    return bytes(b)


def build_synthetic_tkmvst():
    # --- name block -------------------------------------------------------
    names = [b"ThrmvLB2_00\x00", b"naco_tukami2l(DVD)\x00",
             b"Kg_FLnage00_n\x00", b"nakg_nagexx0a_f(DVD)\x00",
             b"Kg_Recv_n\x00", b"recv_anim(DVD)\x00"]
    name_block = b"".join(names)
    off = {}
    pos = 0
    for i, n in enumerate(names):
        off[i] = pos
        pos += len(n)

    # --- animation block: 3 tiny 0xC8 blobs (bones=21) --------------------
    blobs = [c8_blob(21, 4), c8_blob(21, 5), c8_blob(21, 6)]
    anim_block = b"".join(blobs)
    anim_off = [0, len(blobs[0]), len(blobs[0]) + len(blobs[1])]

    # --- moveset block tables (in table order, 8-aligned) ------------------
    tables = {}

    def add(name, rows, stride):
        tables[name] = (len(tables), rows, stride)

    # reactions: 1 row; standing (default_moveid @0x50) = 2400, rest = none
    react = bytearray(0x70)
    for slot_off in (0x50, 0x58, 0x5C, 0x60):
        react[slot_off:slot_off + 2] = u16(2400)
    for slot_off in (0x52, 0x54, 0x56, 0x5A, 0x5E, 0x62, 0x64, 0x66, 0x68, 0x6A):
        react[slot_off:slot_off + 2] = u16(0xFFFF)  # no reaction -> None
    add("reactions", bytes(react), 0x70)

    # requirement rows: [0] = (3, 1536) Throw Hit Forward; [1] = (881, 0) end;
    # [2] = (881, 0) — the default hit-condition row's list (starts with 881).
    req = struct.pack("<II", 3, 1536) + struct.pack("<II", 881, 0) \
        + struct.pack("<II", 881, 0)
    add("requirement", req, 0x08)

    # hitCondition: 1 row; requirements -> row 2 (default), damage 35,
    # reactions -> row 0.
    hc = u64(2) + u32(35) + u32(0) + u64(0)
    add("hitCondition", hc, 0x18)
    add("projectile", b"", 0xA8)
    add("pushback", b"", 0x10)
    add("pushbackExtradata", b"", 0x02)

    # cancel rows: [0] throw-hit forward -> 2125 (frames 12-14);
    # [1] terminator (command 0x8000); [2] terminator (empty list for 2125/2400).
    cancel = bytearray()
    cancel += u64(0) + u64(0) + u64(0) + u32(12) + u32(14) + u32(12) + u16(2125) \
        + b"\x00\x00"
    cancel += u64(0x8000) + bytes(0x28 - 8)
    cancel += u64(0x8000) + bytes(0x28 - 8)
    add("cancel", bytes(cancel), 0x28)
    add("groupCancel", b"", 0x28)
    add("cancelExtradata", b"", 0x04)

    # extraMoveProperty: [0] frame 0x8001, id 0x83C3, value 2400; [1] id 0 end.
    emp = u32(0x8001) + u32(0x83C3) + u32(2400) + u32(0) + u32(0) + u32(0)
    add("extraMoveProperty", emp, 0x0C)
    add("moveBeginningProp", b"", 0x10)
    add("moveEndingProp", b"", 0x10)

    # move table: 2401 rows so ids 1785/2125/2400 are real rows.
    n_moves = 2401
    moves = bytearray(n_moves * 0xB0)
    for i in range(n_moves):
        base = i * 0xB0
        moves[base + 0x00:base + 0x08] = u64(MISSING)
        moves[base + 0x08:base + 0x10] = u64(MISSING)
        moves[base + 0x10:base + 0x18] = u64(MISSING)
        moves[base + 0x20:base + 0x28] = u64(MISSING)
        moves[base + 0x60:base + 0x68] = u64(MISSING)
        moves[base + 0x80:base + 0x88] = u64(MISSING)

    def set_move(mid, name_i, anim_i, anim_addr, anim_len, cancel_row,
                 hc_row, emp_row, first_active=0, last_active=0):
        base = mid * 0xB0
        moves[base + 0x00:base + 0x08] = u64(off[name_i])
        moves[base + 0x08:base + 0x10] = u64(off[anim_i])
        moves[base + 0x10:base + 0x18] = u64(anim_addr)
        moves[base + 0x20:base + 0x28] = u64(cancel_row)
        moves[base + 0x60:base + 0x68] = u64(hc_row)
        moves[base + 0x68:base + 0x6C] = struct.pack("<i", anim_len)
        moves[base + 0x80:base + 0x88] = u64(emp_row)
        moves[base + 0xA0:base + 0xA4] = u32(first_active)
        moves[base + 0xA4:base + 0xA8] = u32(last_active)

    set_move(1785, 0, 1, anim_off[0], 4, 0, 0, 0, 12, 14)
    set_move(2125, 2, 3, anim_off[1], 5, 2, MISSING, MISSING)
    set_move(2400, 4, 5, anim_off[2], 6, 2, MISSING, MISSING)
    add("move", bytes(moves), 0xB0)
    add("voiceclip", b"", 0x04)
    add("inputSequence", b"", 0x10)
    add("input", b"", 0x08)
    add("unknownParryRelated", b"", 0x04)
    add("cameraData", b"", 0x0C)
    add("throwCameras", b"", 0x10)

    # lay the moveset block out in table order, 8-aligned
    order = [n for n, _ in T.TABLES]
    moveset_block = bytearray()
    table_entries = []
    for name in order:
        _, rows, stride = tables[name]
        while len(moveset_block) % 8:
            moveset_block += b"\x00"
        table_entries.append((len(moveset_block), len(rows) // stride if stride else 0))
        moveset_block += rows
    moveset_block = bytes(moveset_block)

    # --- MovesetInfo (0x2E8) ----------------------------------------------
    info = bytearray(0x2E8)
    # current_aliases[0] = 2400 (alias 0x8000 -> receiver, for the alias test)
    struct.pack_into("<H", info, 0x098, 2400)
    for i, (addr, count) in enumerate(table_entries):
        struct.pack_into("<QQ", info, 0x150 + i * 16, addr, count)
    for i in range(13):
        struct.pack_into("<Q", info, 0x280 + i * 8,
                         0 if i in (0, 1) else MISSING)
    info = bytes(info)

    # --- payload blocks -----------------------------------------------------
    # block order: 0 movesetInfo, 1 table, 2 motalists, 3 names, 4 moveset,
    # 5 animation, 6 MOTA, 7 movelist. Blocks 1/2 are views inside block 0.
    payload_parts = []
    offsets = []
    cur = 0

    def emit(b):
        nonlocal cur
        while cur % 8:
            payload_parts.append(b"\x00")
            cur += 1
        offsets.append(cur)
        payload_parts.append(b)
        cur += len(b)

    emit(info)            # block 0 @ 0
    offsets.append(0x150)  # block 1 table (view into block 0)
    offsets.append(0x280)  # block 2 motalists (view into block 0)
    emit(name_block)      # block 3
    emit(moveset_block)   # block 4
    emit(anim_block)      # block 5
    offsets.append(cur)   # block 6 MOTA (empty)
    emit(b"\x00" * 8)     # block 7 movelist
    # offsets list must be [b0, b1, b2, b3, b4, b5, b6, b7]
    assert len(offsets) == 8, offsets
    payload = b"".join(payload_parts)
    # recompute: emit() appended in order b0, b3, b4, b5, b7 — offsets were
    # recorded in the same order with b1/b2/b6 inserted; verify monotonicity
    assert offsets[0] == 0 and offsets[3] > offsets[0]
    assert offsets[4] > offsets[3] and offsets[5] > offsets[4]
    assert offsets[7] >= offsets[5]

    # CRC per file-formats.md (warning-only in the tool, but build it right)
    table_block = 0x150
    crc = zlib.crc32(b"\x00" * 8)
    crc = zlib.crc32(payload[0:table_block], crc)
    crc = zlib.crc32(payload[table_block:table_block + 0x130], crc)
    crc = zlib.crc32(payload[0x280:0x280 + 0x68], crc)
    for i in (4, 5, 6):
        s = offsets[i]
        e = offsets[i + 1] if i + 1 < 8 else len(payload)
        crc = zlib.crc32(payload[s:e], crc)
    crc &= 0xFFFFFFFF

    # --- header + property list + block list + payload ----------------------
    header_size = 256
    prop_list = b"\x00" * 8  # END entry only
    block_list_off = header_size + len(prop_list)
    moveset_start = block_list_off + 8 * 8
    hdr = bytearray(256)
    hdr[0:4] = b"TKM2"
    hdr[0x04:0x07] = b"1.0"
    struct.pack_into("<H", hdr, 0x40, 0)       # gameId T7
    struct.pack_into("<H", hdr, 0x42, 0)       # minorVersion
    struct.pack_into("<I", hdr, 0x44, header_size)
    struct.pack_into("<I", hdr, 0x48, block_list_off)
    struct.pack_into("<I", hdr, 0x4C, 8)
    struct.pack_into("<I", hdr, 0x50, moveset_start)
    struct.pack_into("<Q", hdr, 0x58, 0)       # uncompressed
    hdr[0x60] = 0                              # compression none
    struct.pack_into("<I", hdr, 0x64, crc)
    struct.pack_into("<I", hdr, 0x68, crc)
    struct.pack_into("<I", hdr, 0x80, 2)       # characterId King
    hdr[0x90:0x9A] = b"Tekken 7\x00\x00"  # 10 bytes: slice assignment must
    hdr[0xB0:0xB5] = b"King\x00"          # not change the header length
    hdr[0xD0:0xD5] = b"King\x00"
    block_list = b"".join(u64(o) for o in offsets)
    return bytes(hdr) + prop_list + block_list + payload


def check(cond, label):
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok: {label}")


def main():
    print("building synthetic King .tkmvst (moves 1785/2125/2400) ...")
    data = build_synthetic_tkmvst()
    ms = T.Moveset(data)
    check(ms.header["game_id"] == 0, "header gameId 0 (T7)")
    check(ms.header["target_character"] == "King", "target_character King")
    check(ms.header["character_id"] == 2, "characterId 2 (King)")
    check(ms.move_count() == 2401, "move table has 2401 rows")
    exp, act, ok = T.check_crc32(ms.payload, ms.blocks, ms.header)
    check(ok, f"CRC32 matches documented coverage (0x{act:08x})")

    print("resolving throw triple for move 1785 ...")
    triple = ms.throw_triple(1785)
    check(triple["throw_move"]["name"] == "ThrmvLB2_00",
          "throw move is ThrmvLB2_00")
    check(triple["throw_move"]["anim_len_frames"] == 4,
          "throw move anim_len 4")
    check(triple["throw_move"]["anim_layout"]["type"] == 0xC8,
          "throw anim layout type 0xC8")
    check(triple["throw_move"]["anim_layout"]["bones"] == 21,
          "throw anim layout bones 21")
    check(triple["throw_move"]["anim_layout"]["frames"] == 4,
          "throw anim layout frames 4")
    fwd = triple["thrower_throw_motion"].get("Throw Hit Forward (Standing)")
    check(fwd is not None, "throw-hit forward branch exists")
    check(fwd["resolved_move_id"] == 2125,
          "forward branch resolves to move 2125")
    check(fwd["move"]["name"] == "Kg_FLnage00_n",
          "forward branch move is Kg_FLnage00_n (thrower's throw motion)")
    check(fwd["move"]["anim_len_frames"] == 5,
          "throw-motion anim_len 5")
    recv = triple["victim_receiver"]["hit_conditions"][0]["reactions"]["standing"]
    check(recv["resolved"] == 2400,
          "reaction standing resolves to move 2400 (same moveset)")
    check(recv["name"] == "Kg_Recv_n",
          "receiver move is Kg_Recv_n")
    check(any(e["property"] == 0x83C3
              for e in triple["throw_camera_properties"]),
          "EMP 0x83C3 present on the throw move")
    check(any("0x83C3" in n for n in triple["notes"]),
          "EMP note warns it is NOT the throw receiver")
    check(ms.resolve_move_id(0x8000) == 2400,
          "alias 0x8000 resolves via current_aliases to 2400")

    print("testing animation layout reader ...")
    blob64 = bytes([
        0x64, 0x00,  # type 0x64
        0x01, 0x00,  # bones 1
        0x04, 0x00,  # descriptor 4 (short)
        0x01, 0x00,  # frames 1
        0x00,        # shortShift
        0x00,        # floatShift
        0x00, 0x00,  # floatBones 0
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # base pose (6 bytes)
    ])
    lay = T.read_anim_layout(blob64)
    check(lay["type"] == 0x64 and lay["bones"] == 1 and lay["frames"] == 1,
          "minimal 0x64 layout reads (type/bones/frames)")
    check(lay["size"] == 18, "minimal 0x64 size 18 (keyframes end)")
    try:
        T.read_anim_layout(bytes([0x99, 0x00, 0x01, 0x00, 0, 0, 0, 0]))
        raise SystemExit("FAIL: bad type accepted")
    except ValueError:
        print("  ok: bad animation type rejected")
    try:
        T.read_anim_layout(c8_blob(21, 4)[:10])
        raise SystemExit("FAIL: truncated 0xC8 accepted")
    except ValueError:
        print("  ok: truncated 0xC8 rejected")
    # big-endian (swapped) 0xC8: tag 0xC800
    be = bytearray(24)
    be[0:2] = bytes([0x00, 0xC8])
    be[2:4] = bytes([0x00, 0x01])
    be[4:8] = bytes([0x00, 0x00, 0x00, 0x01])
    lay = T.read_anim_layout(bytes(be))
    check(lay["swapped"] and lay["type"] == 0xC8 and lay["frames"] == 1,
          "big-endian 0xC8 blob reads as swapped")

    print("testing wh-anim/1 clip validator ...")
    clip = {
        "format": "wh-anim/1", "fps": 60,
        "bones": list(T.WH_STANDARD_BONES),
        "rot_xyzw": {b: [[0.0, 0.0, 0.0, 1.0]] * 4
                     for b in T.WH_STANDARD_BONES},
        "root_t": [[0.0, 1.05, 0.0]] * 4,
    }
    # Hips varies so it is not frozen; Chest stays identity (frozen).
    clip["rot_xyzw"]["Hips"] = [[0.0, -0.25, 0.0, 0.968]] * 4
    clip["rot_xyzw"]["Hips"][3] = [0.0, -0.20, 0.0, 0.980]
    move = ms.get_move(1785)
    res = T.validate_wh_clip_data(clip, move)
    check(res["ok"], "synthetic clip validates ok (4 frames = anim_len)")
    check("Chest" in res["frozen_channels_identity"],
          "Chest flagged as frozen identity channel")
    check(any("frozen" in w for w in res["warnings"]),
          "frozen-channel warning present")
    # frame mismatch must be a hard error (no file needed)
    clip_bad = dict(clip)
    clip_bad["rot_xyzw"] = {b: v + [v[0]] for b, v in clip["rot_xyzw"].items()}
    clip_bad["root_t"] = clip["root_t"] + [clip["root_t"][0]]
    res_bad = T.validate_wh_clip_data(clip_bad, move)
    check(not res_bad["ok"] and any("5 frames" in e and "anim_len is 4" in e
                                    for e in res_bad["errors"]),
          "clip with 5 frames vs anim_len 4 fails with frame error")
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
