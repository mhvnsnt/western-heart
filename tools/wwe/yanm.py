#!/usr/bin/env python3
"""YANM parser for WWE 2K19 animation clips.

Rebuilt from the publicly documented format (WrestleMINUS's
AnimationView, MIT-licensed, studied as reference; this code is
original). All header fields are big-endian.

Layout:
  0x00  "YANM"
  0x04  u32 BE total length
  0x0A  u16 BE bone-entry count (entries follow at 0x10; the file
        holds count-1 entries -- the loop runs 0..count-2)
  0x10  bone entries, chained: each entry's length is the u16 BE at
        its +2 (0x30 or 0x18 bytes)

Bone entry:
  +0x00  u16 BE StartingID (0x4000/0x4100/0x5000/0x5100 seen in
         2K19 clips; 0x0001 marks a special record type whose +8
         fields are NOT (index, length) pairs)
  +0x02  u16 BE header length (0x10 = Part A only, 0x18 = A+B,
         0x28/0x30 = A+B+extra bytes)
  +0x04  i32 BE bone hash (see BONE_HASHES; only 14 are known from
         WrestleMINUS -- the rest are reported as hex)
  +0x08  u32 BE Part A index (data starts at index+8)
  +0x0C  u32 BE Part A length in 4-byte units
  +0x10  u32 BE Part B index (absent on 0x10-long entries)
  +0x14  u32 BE Part B length in 4-byte units

Part lengths are x4 bytes (NOT x8 as WrestleMINUS assumes): the
gaps between consecutive part indices equal length*4 for every
part checked (e.g. Part B len 39 fills the 156 bytes before the
next part). One exception seen: J_Hips' Part B in one clip spans
352 bytes for length 44 (x8) -- see docs/YOBJ-YANM.md.

Channel header part (A or B, see StartingID):
  +0/+2/+4  u16 LE X/Y/Z translation present (1) or absent (0xFF00)
  +8/+10/+12  u16 LE X/Y/Z rotation present or absent
  +14  u16 BE frame count

This parser reads the structure (bones, channels, frame counts) and
exposes the raw keyframe blobs. The keyframe VALUE decode (turning
the 8-byte / 20-byte chunks into per-frame rotations/translations)
is the remaining reverse-engineering step -- see docs/YOBJ-YANM.md
for the build plan and the clues found so far.
"""

import json
import struct

# Bone hashes known from WrestleMINUS's YANMBone enum (the rest of
# that enum is sequential ordinals, not hashes).
BONE_HASHES = {
    0x0C5879E5: "vector",
    0xF91A7A26: "J_Hips",
    0x0DAECC2E: "Ch_rotation",
    0x3D185308: "J_Spine1",
    0xF9D973BE: "J_Head",
    0xF91972B1: "J_Neck",
    0xD153E363: "J_Clavicle_L",
    0xA46A2F43: "J_Shoulder_L",
    0x6742F8AA: "J_Elbow_L",
    0xD4C2705A: "J_Wrist_L",
    0xB10CEB4C: "J_MiddleF0_L",
    0xB10CAB4C: "J_MiddleF1_L",
    0xB10C6B4C: "J_MiddleF2_L",
    0xB10C2B4C: "J_MiddleF3_L",
}


def _u16be(b, o):
    return struct.unpack_from(">H", b, o)[0]


def _u32be(b, o):
    return struct.unpack_from(">I", b, o)[0]


def _u16le(b, o):
    return struct.unpack_from("<H", b, o)[0]


class YANM:
    def __init__(self, data):
        if data[:4] != b"YANM":
            raise ValueError(f"not a YANM clip (magic {data[:4]!r})")
        self.data = data
        self.total_length = _u32be(data, 4)
        self.bone_count_field = _u16be(data, 0x0A)
        self.bones = []
        off = 0x10
        for _ in range(self.bone_count_field - 1):
            if off + 0x10 > len(data):
                break
            start_id = _u16be(data, off)
            hlen = _u16be(data, off + 2)
            bone_hash = _u32be(data, off + 4)
            pa_idx = _u32be(data, off + 8)
            pa_len = _u32be(data, off + 0x0C)
            # 0x10-long entries carry Part A only; longer entries
            # also carry Part B at +0x10.
            if hlen >= 0x18:
                pb_idx = _u32be(data, off + 0x10)
                pb_len = _u32be(data, off + 0x14)
            else:
                pb_idx = pb_len = 0
            entry = {
                "starting_id": start_id,
                "header_len": hlen,
                "bone_hash": bone_hash,
                "bone": BONE_HASHES.get(bone_hash),
                "part_a": (pa_idx, pa_len * 4),
                "part_b": (pb_idx, pb_len * 4),
            }
            # NOTE: WrestleMINUS reads channel flags + frame count
            # from one of the parts (A if StartingID < 1000, else B),
            # but that read does not validate on 2K19 clips -- the
            # values come out as garbage, so the frame count is NOT
            # trusted here. The raw part bytes are exposed for the
            # keyframe decode instead (see docs/YOBJ-YANM.md).
            # Entries with StartingID 0x0001 are a special record
            # type whose +8 fields are NOT (index, length) pairs
            # (they read as absurd offsets); they are flagged and
            # their parts are not validated.
            entry["special"] = (start_id == 0x0001)
            entry["key_index"] = pb_idx
            entry["key_len"] = pb_len * 4
            entry["frames"] = 0
            # Range-check the parts against the clip's own declared
            # length (the file may carry YANMPack padding past it).
            # A few variant clips (3 of 500 sampled) carry part
            # fields that do not fit this layout at all (e.g. a
            # 0x80000000 length sentinel); those parts are flagged
            # unusable rather than failing the clip.
            limit = self.total_length or len(data)
            entry["part_a_ok"] = (pa_len == 0 or
                                  pa_idx + 8 + pa_len * 4 <= limit)
            entry["part_b_ok"] = (pb_len == 0 or
                                  pb_idx + 8 + pb_len * 4 <= limit)
            self.bones.append(entry)
            # Advance by the entry's own length, whatever it is
            # (0x10, 0x18, 0x28 and 0x30 all occur).
            if hlen < 0x10 or hlen > 0x100:
                break
            off += hlen

    @property
    def frame_count(self):
        # Unknown until the keyframe decode lands (see module doc).
        return 0

    def keyframe_bytes(self, bone_entry):
        i, n = bone_entry["key_index"], bone_entry["key_len"]
        return self.data[i + 8: i + 8 + n]

    def summary(self):
        return {
            "bytes": len(self.data),
            "bones": len(self.bones),
            "starting_ids": sorted({b["starting_id"]
                                    for b in self.bones}),
        }


def load(path):
    with open(path, "rb") as f:
        return YANM(f.read())


def main():
    import sys
    y = load(sys.argv[1])
    s = y.summary()
    print(f"{sys.argv[1]}: {s['bytes']} bytes, {s['bones']} bones, "
          f"starting IDs {[hex(x) for x in s['starting_ids']]}")
    for i, b in enumerate(y.bones):
        name = b["bone"] or f"hash_{b['bone_hash']:08X}"
        print(f"  [{i:2d}] {name:14s} id=0x{b['starting_id']:04x} "
              f"hlen=0x{b['header_len']:02x} "
              f"a={b['part_a'][0]}+{b['part_a'][1]}B "
              f"b={b['part_b'][0]}+{b['part_b'][1]}B")


if __name__ == "__main__":
    main()
