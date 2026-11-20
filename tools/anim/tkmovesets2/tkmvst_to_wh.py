#!/usr/bin/env python3
"""tkmvst_to_wh.py — Tekken 7 .tkmvst (TKMovesets2) -> Western Heart mapping tool.

Reads a TKMovesets2 `.tkmvst` moveset file (Tekken 7, gameId 0) and resolves
a throw into its TRIPLE, all inside the THROWER's moveset:

  1. thrower's grab     — the throw move's own animation (Move.anim_addr)
  2. thrower's throw     — the throw move's CANCEL rows whose requirement is a
                           throw-hit condition (3/4/5/6/27) -> target move id
  3. victim's receiver  — the throw move's HitCondition -> ReactionList ->
                           reaction move ids (standing/crouch/left/right/back)

Plus the throw-camera Extra Move Property rows on the throw move, and a
validator for an existing Western Heart wh-anim/1 clip against the mapped move.

WHAT THIS TOOL DOES NOT DO (deliberately):
  It does NOT decode 0x64/0xC8 animation blobs into joint rotations. The blob
  layout (type byte, bone count, frame count, byte size) is read faithfully
  from TKMovesets2 `Utils/AnimationReader.hpp` (`ReadAnimationLayoutFrom`),
  but the per-frame delta decode lives in `TAnimUtils::ParseAnimation0x64`
  (`Utils/Animations_T_x64.cpp`) and in WH's own game-sampler path
  (`tools/anim/t7_anim64_to_c8.py`, game's own sampler RVA 0x73ea30).
  Re-implementing that decoder from scratch is out of scope by design:
  the known-good decode is the reference implementation, not a rewrite.

Spec sources (vendored beside this file):
  docs/file-formats.md   (.tkmvst container, header, blocks, CRC coverage)
  docs/t7-structures.md   (MovesetInfo, 19 tables, Move 0xB0, Cancel 0x28,
                            HitCondition 0x18, Reactions 0x70, terminators)
  editor_t7_requirements.txt  (requirement condition ids -> labels)
  editor_t7_properties.txt    (extra move property ids -> labels)

Usage:
  python3 tkmvst_to_wh.py summary <file.tkmvst>
  python3 tkmvst_to_wh.py triple <file.tkmvst> <move_id> [--json]
  python3 tkmvst_to_wh.py layout <anim_blob.bin>
  python3 tkmvst_to_wh.py validate <file.tkmvst> <move_id> <clip.json>
      [--skeleton skeleton.json] [--json]

Move ids may be decimal (1785) or hex (0x6f9). Requires the game only in
the sense that a real .tkmvst can only be produced by extracting from a
running / installed Tekken 7 (TKMovesets2); this tool itself needs no game.
"""

import json
import lzma
import math
import struct
import sys
import zlib
from pathlib import Path

MISSING = 0xFFFFFFFFFFFFFFFF

# ---------------------------------------------------------------------------
# .tkmvst header (TKMovesetHeader, 256 bytes; file-formats.md)
# ---------------------------------------------------------------------------

def _cstr(raw):
    return raw.split(b"\x00", 1)[0].decode("utf-8", "replace")


class TkmvstError(Exception):
    pass


def parse_header(data):
    if len(data) < 256 or data[0:4] != b"TKM2":
        raise TkmvstError("not a .tkmvst file (missing TKM2 signature)")
    hdr = {}
    hdr["version_string"] = _cstr(data[0x04:0x20])
    hdr["game_id"] = struct.unpack_from("<H", data, 0x40)[0]
    hdr["minor_version"] = struct.unpack_from("<H", data, 0x42)[0]
    hdr["header_size"] = struct.unpack_from("<I", data, 0x44)[0]
    hdr["block_list"] = struct.unpack_from("<I", data, 0x48)[0]
    hdr["block_list_size"] = struct.unpack_from("<I", data, 0x4C)[0]
    hdr["moveset_data_start"] = struct.unpack_from("<I", data, 0x50)[0]
    hdr["moveset_data_size"] = struct.unpack_from("<Q", data, 0x58)[0]
    hdr["compression"] = data[0x60]
    hdr["crc32"] = struct.unpack_from("<I", data, 0x64)[0]
    hdr["orig_crc32"] = struct.unpack_from("<I", data, 0x68)[0]
    hdr["character_id"] = struct.unpack_from("<I", data, 0x80)[0]
    hdr["origin"] = _cstr(data[0x90:0xB0])
    hdr["target_character"] = _cstr(data[0xB0:0xD0])
    hdr["orig_character_name"] = _cstr(data[0xD0:0xF0])
    hdr["conversion_origin"] = struct.unpack_from("<H", data, 0xF8)[0]
    if hdr["header_size"] < 0xD0:
        raise TkmvstError(f"header_size too small: {hdr['header_size']}")
    if hdr["game_id"] != 0:
        raise TkmvstError(
            f"this tool handles Tekken 7 files only (gameId 0); got gameId {hdr['game_id']}")
    if hdr["block_list_size"] != 8:
        raise TkmvstError(
            f"T7 files have 8 blocks; block_list_size is {hdr['block_list_size']}")
    return hdr


def decompress_payload(data, hdr):
    comp = hdr["compression"]
    start = hdr["moveset_data_start"]
    raw = data[start:]
    if comp == 0:
        return raw
    if comp == 2:  # LZMA, one .xz stream
        try:
            out = lzma.decompress(raw)
        except lzma.LZMAError as exc:
            raise TkmvstError(f"LZMA payload failed to decompress: {exc}")
        if hdr["moveset_data_size"] and len(out) != hdr["moveset_data_size"]:
            raise TkmvstError(
                f"LZMA size mismatch: got {len(out)}, header says "
                f"{hdr['moveset_data_size']}")
        return out
    if comp == 1:
        raise TkmvstError(
            "payload uses LZ4 compression (type 1); install python-lzma or "
            "re-export the moveset uncompressed (TKMovesets2 headless: "
            "--compression none). No LZ4 decode is attempted here.")
    if comp == 3:
        raise TkmvstError(
            "payload uses Compact+Zstd (type 3); re-export the moveset "
            "uncompressed or as LZMA. No Zstd decode is attempted here.")
    raise TkmvstError(f"unknown compressionType {comp}")


def check_crc32(payload, blocks, hdr):
    """CRC coverage per docs/file-formats.md: one empty property entry, then
    payload[0, tableBlock), the table, the MOTA list, the moveset block, the
    animation block and the MOTA block. Name + movelist blocks NOT covered.
    Returns (expected, actual, ok). Warning-only: a mismatch never blocks
    triple resolution."""
    table_block = blocks[1]
    mota_list_off = 0x280
    crc = zlib.crc32(b"\x00" * 8)
    crc = zlib.crc32(payload[0:table_block], crc)
    crc = zlib.crc32(payload[table_block:table_block + 0x130], crc)
    crc = zlib.crc32(payload[mota_list_off:mota_list_off + 0x68], crc)
    for i in (4, 5, 6):
        s, e = blocks[i], blocks[i + 1] if i + 1 < 8 else len(payload)
        crc = zlib.crc32(payload[s:e], crc)
    return hdr["crc32"], crc & 0xFFFFFFFF, hdr["crc32"] == (crc & 0xFFFFFFFF)


# ---------------------------------------------------------------------------
# Animation layout — faithful port of TAnimUtils::ReadAnimationLayoutFrom
# (TKMovesets2 Utils/AnimationReader.hpp). Layout ONLY; no frame decode.
# ---------------------------------------------------------------------------

def read_anim_layout(blob, offset=0):
    """Return {type, bones, frames, size, swapped, base_pose} for the
    animation starting at blob[offset]. Raises ValueError on bad data."""
    if len(blob) - offset < 8:
        raise ValueError("animation blob truncated (< 8 bytes)")
    tag = struct.unpack_from("<H", blob, offset)[0]
    swapped = tag in (0x6400, 0xC800)
    fmt = "<H" if not swapped else ">H"

    def u16(at):
        return struct.unpack_from(fmt, blob, offset + at)[0]

    def u32(at):
        return struct.unpack_from("<I" if not swapped else ">I", blob, offset + at)[0]

    typ = u16(0)
    bones = u16(2)
    if typ not in (0x64, 0xC8) or bones == 0 or bones > 255:
        raise ValueError(f"invalid animation type 0x{typ:02x} / bones {bones}")
    if typ == 0xC8:
        frames = u32(4)
        if not frames:
            raise ValueError("0xC8 animation has no frames")
        size = 8 + bones * 4 + bones * 12 * frames
        if size > len(blob) - offset:
            raise ValueError("0xC8 animation frames are truncated")
        return {"type": 0xC8, "bones": bones, "frames": frames,
                "size": size, "swapped": swapped,
                "base_pose": 8 + bones * 4}
    # 0x64
    descriptors = 4
    post = 4 + bones * 2
    frames = u16(post)
    float_bones = u16(post + 4)
    if not frames or float_bones > bones:
        raise ValueError("invalid 0x64 frame or float-bone count")
    floating = 0
    for i in range(bones):
        if not (4 <= u16(4 + i * 2) <= 7):
            floating += 1
    if floating != float_bones:
        raise ValueError("0x64 float-bone descriptors disagree with header")
    base_pose = post + 6 + float_bones * 4
    keyframes = base_pose + bones * 6 + float_bones * 6
    if post + (keyframes - post) > len(blob) - offset:
        raise ValueError("0x64 animation truncated before keyframes")
    chunks = (frames + 14) // 16
    if keyframes + chunks * 4 > len(blob) - offset:
        raise ValueError("0x64 keyframe table truncated")
    size = keyframes
    for chunk in range(chunks):
        koff = u32(keyframes + chunk * 4)
        if koff < chunks * 4 or koff > len(blob) - offset - keyframes:
            raise ValueError("invalid 0x64 keyframe offset")
        cursor = keyframes + koff
        for _ in range(bones * 3):
            if cursor >= len(blob) - offset:
                raise ValueError("0x64 keyframe channel truncated")
            length = blob[offset + cursor] >> 2
            if length == 0:
                raise ValueError("0x64 channel has zero length")
            if cursor + length > len(blob) - offset:
                raise ValueError("0x64 channel overruns blob")
            cursor += length
        size = max(size, cursor)
    return {"type": 0x64, "bones": bones, "frames": frames,
            "size": size, "swapped": swapped, "base_pose": base_pose}


# ---------------------------------------------------------------------------
# T7 payload parsing (docs/t7-structures.md)
# ---------------------------------------------------------------------------

# table index -> (name, stride) in MovesetInfo.table order
TABLES = [
    ("reactions", 0x70),
    ("requirement", 0x08),
    ("hitCondition", 0x18),
    ("projectile", 0xA8),
    ("pushback", 0x10),
    ("pushbackExtradata", 0x02),
    ("cancel", 0x28),
    ("groupCancel", 0x28),
    ("cancelExtradata", 0x04),
    ("extraMoveProperty", 0x0C),
    ("moveBeginningProp", 0x10),
    ("moveEndingProp", 0x10),
    ("move", 0xB0),
    ("voiceclip", 0x04),
    ("inputSequence", 0x10),
    ("input", 0x08),
    ("unknownParryRelated", 0x04),
    ("cameraData", 0x0C),
    ("throwCameras", 0x10),
]

# Throw-hit requirement conditions (editor_t7_requirements.txt; embedded so
# the tool works even without the vendored table files beside it).
THROW_HIT_CONDITIONS = {
    3: "Throw Hit Forward (Standing)",
    4: "Throw Hit Backward (Standing)",
    5: "Throw Hit Left Side (Standing)",
    6: "Throw Hit Right Side (Standing)",
    27: "Airborne Throw Hit Forward (Face Up)",
}

# Reaction move slots in tk_reaction (offsets from t7-structures.md).
# NOTE: standing is default_moveid @0x50; standing_moveid @0x4E is 0 in the
# game's movesets (Editor_t7.cpp MoveHitReactions).
REACTION_SLOTS = [
    ("standing", 0x50), ("crouch", 0x52),
    ("counterhit", 0x54), ("crouch_counterhit", 0x56),
    ("left_side", 0x58), ("crouch_left_side", 0x5A),
    ("right_side", 0x5C), ("crouch_right_side", 0x5E),
    ("backturned", 0x60), ("crouch_backturned", 0x62),
    ("block", 0x64), ("crouch_block", 0x66),
    ("wallslump", 0x68), ("downed", 0x6A),
]

REQ_END = 881          # requirement list ends on condition == 881
CANCEL_END = 0x8000    # cancel list ends on command == 0x8000
EMP_END_ID = 0         # extra property list ends on id == 0

# Extra Move Property 0x83C3 (33731) "Set opponent's move" — the EMP that
# sets the OPPONENT's move id. Documented use: balcony-break victim
# (Tag2Aliases.py 0x826e -> T7 0x83c3, nofill). It does NOT govern throw
# receivers; those come from the Reaction List (see module docstring).
EMP_SET_OPPONENT_MOVE = 0x83C3


class Moveset:
    def __init__(self, data):
        self.data = data
        self.header = parse_header(data)
        payload = decompress_payload(data, self.header)
        self.payload = payload
        bl = self.header["block_list"]
        # The block list lives at absolute file offset block_list (before
        # moveset_data_start, identical compressed or not); its 8 entries
        # are offsets relative to the payload start.
        self.blocks = list(struct.unpack_from("<8Q", data, bl))
        self._parse_tables()

    # -- low-level readers over the payload -------------------------------
    def _u16(self, off):
        return struct.unpack_from("<H", self.payload, off)[0]

    def _u32(self, off):
        return struct.unpack_from("<I", self.payload, off)[0]

    def _u64(self, off):
        return struct.unpack_from("<Q", self.payload, off)[0]

    def _parse_tables(self):
        p = self.payload
        # MovesetInfo at payload 0 (0x2E8 bytes)
        self.orig_aliases = list(struct.unpack_from("<56H", p, 0x028))
        self.current_aliases = list(struct.unpack_from("<56H", p, 0x098))
        # table: 19 x {u64 addr, u64 count} at 0x150
        self.table = []
        for i in range(19):
            addr, count = struct.unpack_from("<QQ", p, 0x150 + i * 16)
            self.table.append((addr, count))
        # MOTA list: 13 x u64 at 0x280 (offsets into the MOTA block)
        self.motas = list(struct.unpack_from("<13Q", p, 0x280))
        self.moveset_block = self.blocks[4]
        self.name_block = self.blocks[3]
        self.anim_block = self.blocks[5]
        self.mota_block = self.blocks[6]
        self.movelist_block = self.blocks[7]

    def table_rows(self, name):
        idx = next(i for i, (n, _) in enumerate(TABLES) if n == name)
        _, stride = TABLES[idx]
        addr, count = self.table[idx]
        if addr == MISSING:
            return []
        base = self.moveset_block + addr
        return [(base + r * stride, stride) for r in range(count)]

    def _name(self, off):
        if off == MISSING or off >= len(self.payload) - self.name_block:
            return None
        base = self.name_block + off
        end = self.payload.find(b"\x00", base)
        if end < 0:
            return None
        return self.payload[base:end].decode("utf-8", "replace")

    # -- moves ------------------------------------------------------------
    def move_count(self):
        return self.table[12][1]

    def get_move(self, move_id):
        """Return the move record dict for a row id (aliases NOT resolved)."""
        addr, count = self.table[12]
        if move_id >= count:
            return None
        off = self.moveset_block + addr + move_id * 0xB0
        p = self.payload
        return {
            "id": move_id,
            "name": self._name(self._u64(off + 0x00)),
            "anim_name": self._name(self._u64(off + 0x08)),
            "anim_addr": self._u64(off + 0x10),
            "vuln": self._u32(off + 0x18),
            "hitlevel": self._u32(off + 0x1C),
            "cancel_addr": self._u64(off + 0x20),
            "transition": self._u16(off + 0x54),
            "hit_condition_addr": self._u64(off + 0x60),
            "anim_len": struct.unpack_from("<i", p, off + 0x68)[0],
            "extra_move_property_addr": self._u64(off + 0x80),
            "first_active_frame": self._u32(off + 0xA0),
            "last_active_frame": self._u32(off + 0xA4),
        }

    def resolve_move_id(self, move_id):
        """Aliases (>= 0x8000) resolve against current_aliases; returns the
        row id or None when out of range."""
        if move_id >= 0x8000:
            n = move_id - 0x8000
            if n >= len(self.current_aliases):
                return None
            move_id = self.current_aliases[n]
        return move_id if move_id < self.move_count() else None

    def anim_layout(self, move):
        """Layout of the move's animation blob in the animation block."""
        addr = move["anim_addr"]
        if addr == MISSING:
            return None
        off = self.anim_block + addr
        return read_anim_layout(self.payload, off)

    # -- lists ------------------------------------------------------------
    def _req_list(self, first):
        """Requirement rows from `first` until condition == 881.
        Returns [(condition, param), ...] (the 881 terminator excluded)."""
        out = []
        addr, count = self.table[1]
        row = first
        while row < count and row < first + 512:
            off = self.moveset_block + addr + row * 0x08
            cond = self._u32(off)
            param = self._u32(off + 4)
            if cond == REQ_END:
                break
            out.append((cond, param))
            row += 1
        return out

    def cancel_list(self, move):
        """Cancel rows for a move: [{command, requirements, start, end,
        starting_frame, move_id}] until command == 0x8000."""
        first = move["cancel_addr"]
        if first == MISSING:
            return []
        addr, count = self.table[6]
        out = []
        row = first
        while row < count and row < first + 1024:
            off = self.moveset_block + addr + row * 0x28
            command = self._u64(off)
            if command == CANCEL_END:
                break
            out.append({
                "command": command,
                "requirements_addr": self._u64(off + 0x08),
                "requirements": self._req_list(self._u64(off + 0x08))
                if self._u64(off + 0x08) != MISSING else [],
                "detection_start": self._u32(off + 0x18),
                "detection_end": self._u32(off + 0x1C),
                "starting_frame": self._u32(off + 0x20),
                "move_id": self._u16(off + 0x24),
            })
            row += 1
        return out

    def extra_properties(self, move):
        """Extra Move Property rows until id == 0."""
        first = move["extra_move_property_addr"]
        if first == MISSING:
            return []
        addr, count = self.table[9]
        out = []
        row = first
        while row < count and row < first + 512:
            off = self.moveset_block + addr + row * 0x0C
            frame = self._u32(off)
            prop = self._u32(off + 4)
            value = self._u32(off + 8)
            if prop == EMP_END_ID:
                break
            out.append({"frame": frame, "property": prop, "value": value})
            row += 1
        return out

    def hit_reactions(self, move):
        """Reaction move ids for a move, via HitCondition -> Reactions.
        All ids resolve in THIS moveset (the attacker's). Returns
        {slot: {"move_id": raw, "resolved": row-or-None, "name": ...}}."""
        first = move["hit_condition_addr"]
        if first == MISSING:
            return {}
        hc_addr, hc_count = self.table[2]
        r_addr, r_count = self.table[0]
        req_addr, _ = self.table[1]
        out = {}
        row = first
        # The list runs until the row whose requirement list starts with 881.
        while row < hc_count and row < first + 64:
            off = self.moveset_block + hc_addr + row * 0x18
            req_first = self._u64(off)
            reqs = self._req_list(req_first) if req_first != MISSING else []
            damage = self._u32(off + 0x08)
            react = self._u64(off + 0x10)
            entry = {"hit_condition_row": row, "requirements": reqs,
                     "damage": damage, "reactions": {}}
            if react != MISSING and react < r_count:
                roff = self.moveset_block + r_addr + react * 0x70
                for slot, soff in REACTION_SLOTS:
                    raw = self._u16(roff + soff)
                    res = self.resolve_move_id(raw)
                    entry["reactions"][slot] = {
                        "move_id": raw, "resolved": res,
                        "name": self.get_move(res)["name"] if res is not None
                        else None}
            out.setdefault("hit_conditions", []).append(entry)
            # Default (catch-all) row: its requirement list's first row has
            # condition 881, so _req_list returned [] for a real list.
            if req_first != MISSING:
                first_cond = self._u32(
                    self.moveset_block + req_addr + req_first * 0x08)
                if first_cond == REQ_END:
                    break
            row += 1
        return out

    # -- throw triple -----------------------------------------------------
    def throw_triple(self, move_id):
        move = self.get_move(move_id)
        if move is None:
            raise TkmvstError(f"move {move_id} out of range "
                              f"(0..{self.move_count() - 1})")
        triple = {"throw_move": self._move_summary(move),
                  "thrower_throw_motion": {},
                  "victim_receiver": {},
                  "throw_camera_properties": [],
                  "notes": []}
        # 1+2. Thrower's throw motion: cancel rows on throw-hit requirements.
        for c in self.cancel_list(move):
            conds = [c0 for c0, _ in c["requirements"]]
            hits = [c0 for c0 in conds if c0 in THROW_HIT_CONDITIONS]
            if not hits:
                continue
            target = self.resolve_move_id(c["move_id"])
            for h in hits:
                triple["thrower_throw_motion"][THROW_HIT_CONDITIONS[h]] = {
                    "requirement": h,
                    "target_move_id": c["move_id"],
                    "resolved_move_id": target,
                    "move": self._move_summary(self.get_move(target))
                    if target is not None else None,
                    "detection": [c["detection_start"], c["detection_end"]],
                    "starting_frame": c["starting_frame"],
                }
        # 3. Victim's receiver: HitCondition -> ReactionList.
        triple["victim_receiver"] = self.hit_reactions(move)
        # Throw camera / EMP rows on the throw move.
        for e in self.extra_properties(move):
            triple["throw_camera_properties"].append(e)
            if e["property"] == EMP_SET_OPPONENT_MOVE:
                triple["notes"].append(
                    "EMP 0x83C3 'Set opponent's move' present (value "
                    f"{e['value']}). This property sets the OPPONENT's move "
                    "id (balcony-break victim mechanism); it is NOT the "
                    "throw receiver, which comes from the Reaction List.")
        if not triple["thrower_throw_motion"]:
            triple["notes"].append(
                "No throw-hit cancel rows found on this move; it may not be "
                "a throw, or its throw routing lives elsewhere.")
        if not triple["victim_receiver"]:
            triple["notes"].append(
                "No hit-condition / reaction data on this move; the receiver "
                "cannot be resolved from this file.")
        return triple

    def _move_summary(self, move):
        if move is None:
            return None
        try:
            layout = self.anim_layout(move)
        except ValueError as exc:
            layout = {"error": str(exc)}
        return {"id": move["id"], "name": move["name"],
                "anim_name": move["anim_name"],
                "anim_addr": move["anim_addr"],
                "anim_len_frames": move["anim_len"],
                "first_active_frame": move["first_active_frame"],
                "last_active_frame": move["last_active_frame"],
                "anim_layout": layout}

    def mota_slots(self):
        """The 13 MOTA list slots. Even slots are MOTAs inside the motbin;
        odd slots come from <code>rotsm.arc (t7-structures.md)."""
        out = []
        for i, ptr in enumerate(self.motas):
            out.append({"slot": i, "offset_in_mota_block": ptr,
                        "archive": ("motbin" if i % 2 == 0 else "rotsm.arc")
                        if ptr != MISSING else None,
                        "present": ptr != MISSING})
        return out


# ---------------------------------------------------------------------------
# Western Heart wh-anim/1 clip validation
# ---------------------------------------------------------------------------

WH_STANDARD_BONES = [
    "Hips", "Spine", "Chest", "Neck", "Head",
    "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
    "RightShoulder", "RightArm", "RightForeArm", "RightHand",
    "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
]


def validate_wh_clip_data(clip, move, skeleton_bones=None):
    """Validate a parsed wh-anim/1 clip dict against a .tkmvst move record.
    Returns {format, fps, frames, move_anim_len, frozen_channels_identity,
    errors, warnings, ok}. `ok` is False only on hard errors; frozen
    identity channels are warnings, not errors."""
    bones_expected = skeleton_bones or WH_STANDARD_BONES
    errors = []
    warnings = []
    result = {"format": clip.get("format"),
              "fps": clip.get("fps"), "errors": errors, "warnings": warnings}
    if clip.get("format") != "wh-anim/1":
        errors.append(f"format is {clip.get('format')!r}, expected 'wh-anim/1'")
    bones = clip.get("bones", [])
    if bones != bones_expected:
        errors.append(
            f"bone list differs from skeleton: missing "
            f"{[b for b in bones_expected if b not in bones]}, extra "
            f"{[b for b in bones if b not in bones_expected]}")
    rot = clip.get("rot_xyzw", {})
    frames = None
    frozen = []
    for b in bones:
        qs = rot.get(b)
        if qs is None:
            errors.append(f"bone {b} has no rotation channel")
            continue
        if frames is None:
            frames = len(qs)
        elif len(qs) != frames:
            errors.append(f"bone {b} has {len(qs)} frames, expected {frames}")
        bad = 0
        for q in qs:
            n = math.sqrt(sum(x * x for x in q))
            if not (0.999 <= n <= 1.001) or not all(math.isfinite(x) for x in q):
                bad += 1
        if bad:
            errors.append(f"bone {b}: {bad} non-unit/non-finite quats")
        if len(set(tuple(q) for q in qs)) == 1:
            frozen.append(b)
    result["frames"] = frames
    result["move_anim_len"] = move["anim_len"]
    if frames is not None and move["anim_len"] and frames != move["anim_len"]:
        errors.append(
            f"clip has {frames} frames but the move's anim_len is "
            f"{move['anim_len']} (a mismatch means the clip is not the "
            f"whole move animation)")
    result["frozen_channels_identity"] = frozen
    if frozen:
        warnings.append(
            f"frozen identity channels: {', '.join(frozen)} — either the "
            f"source blob does not drive these joints or the bake padded "
            f"them; only a .tkmvst + skeleton bone map can tell which")
    root = clip.get("root_t")
    if root is not None and frames is not None and len(root) != frames:
        errors.append(f"root_t has {len(root)} frames, expected {frames}")
    result["ok"] = not errors
    return result


def validate_wh_clip(clip_path, move, skeleton_bones=None):
    clip = json.loads(Path(clip_path).read_text())
    result = validate_wh_clip_data(clip, move, skeleton_bones)
    result["clip"] = str(clip_path)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_move_id(text):
    return int(text, 0)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "layout":
        blob = Path(argv[2]).read_bytes()
        try:
            print(json.dumps(read_anim_layout(blob), indent=2))
        except ValueError as exc:
            print(f"layout error: {exc}", file=sys.stderr)
            return 1
        return 0
    ms = Moveset(Path(argv[2]).read_bytes())
    if cmd == "summary":
        hdr = ms.header
        exp, act, ok = check_crc32(ms.payload, ms.blocks, hdr)
        print(json.dumps({
            "file": argv[2],
            "header": {k: hdr[k] for k in (
                "version_string", "game_id", "origin", "target_character",
                "orig_character_name", "character_id", "compression",
                "conversion_origin")},
            "moves": ms.move_count(),
            "tables": {name: ms.table[i][1] for i, (name, _) in enumerate(TABLES)},
            "crc32": {"expected": exp, "actual": act, "ok": ok},
            "mota_slots": ms.mota_slots(),
        }, indent=2))
        return 0
    if cmd == "triple":
        move_id = _parse_move_id(argv[3])
        triple = ms.throw_triple(move_id)
        print(json.dumps(triple, indent=2))
        return 0
    if cmd == "validate":
        move_id = _parse_move_id(argv[3])
        clip_path = argv[4]
        skel = None
        if "--skeleton" in argv:
            sk = json.loads(Path(argv[argv.index("--skeleton") + 1]).read_text())
            skel = [j["name"] for j in sk["joints"]]
        move = ms.get_move(move_id)
        if move is None:
            print(f"move {move_id} out of range", file=sys.stderr)
            return 1
        res = validate_wh_clip(clip_path, move, skel)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
