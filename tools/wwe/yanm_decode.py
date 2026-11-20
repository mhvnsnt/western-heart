#!/usr/bin/env python3
"""YANM keyframe decoder for WWE 2K19 animation clips.

Extends yanm.py (structure) with the decoded keyframe value format,
reverse-engineered 2026-11-19 from the 18,862-clip moves pack:

  Frame count: every Part A and Part B (except J_Hips Part B) is a
  sequence of 4-byte records (v0, v1, v2, dt). dt is the number of
  frames until the next keyframe; the dts of any part sum to the
  clip's total frame count. Validated: 197/200 sampled clips have
  ALL parts agreeing on exactly one total (3 edge cases: 2-bone
  clips and one clip with a part summing to 2x). The vector bone's
  parts are (0,0,0,0),(0,0,0,frames) -- a second, independent
  confirmation of the frame count.

  Part A values: 3 signed bytes, ABSOLUTE per-keyframe values,
  smooth over time (max ~4 units/frame). Interpreted as Euler
  rotation angles, 1 unit = 360/256 degrees. (Blender validation:
  see yanm_to_gltf.py / docs.)

  Part B values (4-byte records): same dt structure, but the values
  jump up to ~45 units/frame -- NOT a direct spatial signal in the
  Part A unit. Meaning still open (see docs/YOBJ-YANM.md "Part B").

  J_Hips Part B: 8-byte records (3 x i16 BE + u16 dt). The length
  field counts 8-byte records, so the true byte span is length*8
  -- TWICE what yanm.py's length*4 gives. (This decoder used to
  read only half the track, which is why the u16 column did not
  sum to the frame count.) The u16 dts sum to the clip's frame
  count; each record is the root DISPLACEMENT over
  [frame, frame+dt), so the position is the forward cumulative
  sum, scaled by the first trailing float of the J_Hips entry
  (cm/unit), with the absolute start in the next three trailing
  floats. Full decode: yanm_root.py (see docs/YOBJ-YANM.md
  "Root motion").

  Knee entries (StartingID 0x0001): the data index lives at +0xC
  (not +8); data starts at index+8, confirmed by both neighbours.
  The +8 field is (0x03C9, keyframe_count 55/56?). The 404-byte
  knee data block is NOT 4-byte records (no window sums to the
  frame count under any dt byte position). Format open.

  Bone hashes (position-mapped from the standard 23-bone clips,
  order matches the YOBJ skeleton): J_Leg_L/R CCB8C530/CCB8C52E,
  J_Knee_L/R EC2C1192/EC2C118C, J_Foot_L/R FD6851FA/FD6851E4,
  J_Toe_L/R 4DF84531/4DF8452F, J_Clavicle_R D153E37D,
  J_Shoulder_R A46A2F5D, J_Elbow_R 6742F8B4, J_Wrist_R D4C27044.
  0DAECC2D (twin of Ch_rotation 0DAECC2E, same clips, adjacent
  entry) is still unnamed -- likely the character-position twin
  of the character-rotation track.

Usage:
  yanm_decode.py <clip.yanm> [--json]   # print frame count + tracks
"""

import json
import math
import struct
import sys

from yanm import YANM, BONE_HASHES

# Position-mapped hashes (see module docstring).
BONE_HASHES.update({
    0xD153E37D: "J_Clavicle_R",
    0xA46A2F5D: "J_Shoulder_R",
    0x6742F8B4: "J_Elbow_R",
    0xD4C27044: "J_Wrist_R",
    0xCCB8C530: "J_Leg_L",
    0xEC2C1192: "J_Knee_L",
    0xFD6851FA: "J_Foot_L",
    0x4DF84531: "J_Toe_L",
    0xCCB8C52E: "J_Leg_R",
    0xEC2C118C: "J_Knee_R",
    0xFD6851E4: "J_Foot_R",
    0x4DF8452F: "J_Toe_R",
})

DEG_PER_UNIT = 360.0 / 256.0


def _s8(b):
    return b - 256 if b >= 128 else b


def parse_records(data):
    """4-byte records -> [(frame, v0, v1, v2), ...]; frame is the
    absolute frame of the keyframe (cumulative dt)."""
    keys = []
    frame = 0
    for i in range(0, len(data) - 3, 4):
        keys.append((frame, _s8(data[i]), _s8(data[i + 1]),
                     _s8(data[i + 2])))
        frame += data[i + 3]
    return keys, frame


class YANMDecoded(YANM):
    def __init__(self, data):
        super().__init__(data)
        # Frame count: the dt-sum every part agrees on (excluding
        # J_Hips Part B and special entries, which don't follow it).
        totals = {}
        for b in self.bones:
            if b["special"]:
                continue
            for which in ("part_a", "part_b"):
                idx, ln = b[which]
                if ln == 0:
                    continue
                if b["bone_hash"] == 0xF91A7A26 and which == "part_b":
                    continue  # 8-byte records, different track
                part = self.data[idx + 8: idx + 8 + ln]
                if len(part) % 4:
                    continue
                _, total = parse_records(part)
                totals[total] = totals.get(total, 0) + 1
        self._frame_count = max(totals, key=totals.get) if totals else 0
        self.frame_votes = totals
        # Resolve bone names (incl. position-mapped hashes).
        for b in self.bones:
            b["bone"] = BONE_HASHES.get(b["bone_hash"])

    @property
    def frame_count(self):
        # Overrides yanm.YANM's placeholder (which returns 0).
        return self._frame_count

    def track(self, bone_entry, which="part_a"):
        """Decoded keyframes [(frame, v0, v1, v2), ...] for one part,
        or None if the part doesn't follow the 4-byte layout
        (J_Hips Part B is 8-byte records -- see hips_b_track;
        knee entries have no index/length fields -- see knee_gap)."""
        if bone_entry["special"]:
            return None
        if (bone_entry["bone_hash"] == 0xF91A7A26
                and which == "part_b"):
            return None
        idx, ln = bone_entry[which]
        if ln == 0 or ln % 4:
            return None
        part = self.data[idx + 8: idx + 8 + ln]
        keys, total = parse_records(part)
        return keys

    def hips_b_track(self, bone_entry):
        """J_Hips Part B raw 8-byte records [(x, y, z, dt), ...]
        (3 x i16 BE + u16 BE dt). The dt column sums to the clip's
        frame count, and each record is the root displacement over
        [frame, frame+dt) -- see yanm_root.py for the full decode.

        NOTE: yanm.py stores the Part B length as length*4 (4-byte
        units), but the J_Hips Part B length field counts 8-byte
        records, so the true byte span is ln*2. Reading only ln
        bytes (the old behaviour) returns half the track.

        On 0x5100 entries (header_len 0x30) Part B is 4-byte
        records -- a different track, not root motion (the root
        motion lives in the third pair there; see yanm_root.py).
        Returns None for those."""
        if bone_entry.get("starting_id") == 0x5100:
            return None
        idx, ln = bone_entry["part_b"]
        if ln == 0 or ln % 4:
            return None
        part = self.data[idx + 8: idx + 8 + ln * 2]
        return [(struct.unpack_from(">h", part, j)[0],
                 struct.unpack_from(">h", part, j + 2)[0],
                 struct.unpack_from(">h", part, j + 4)[0],
                 struct.unpack_from(">H", part, j + 6)[0])
                for j in range(0, len(part) - 7, 8)]

    def knee_gap(self, bone_entry):
        """Raw data bytes for a special (knee) entry: the data index
        lives in the entry's +0xC field (stored here as
        part_a[1] // 4 -- yanm.py reads it as the length slot), and
        the block runs to the next part's start or the clip's
        declared length. Returns (start_offset, bytes) or None."""
        if not bone_entry["special"]:
            return None
        start = bone_entry["part_a"][1] // 4 + 8
        limit = self.total_length or len(self.data)
        end = limit
        for b in self.bones:
            for which in ("part_a", "part_b"):
                idx, ln = b[which]
                if ln and idx + 8 > start:
                    end = min(end, idx + 8)
        if start >= end or start >= len(self.data):
            return None
        return (start, self.data[start:min(end, len(self.data))])

    def sample(self, keys, frame):
        """Linearly interpolate a keyframe track at an integer frame
        (hold first/last outside the range)."""
        if not keys:
            return (0.0, 0.0, 0.0)
        if frame <= keys[0][0]:
            return tuple(float(v) for v in keys[0][1:])
        if frame >= keys[-1][0]:
            return tuple(float(v) for v in keys[-1][1:])
        for i in range(len(keys) - 1):
            f0, f1 = keys[i][0], keys[i + 1][0]
            if f0 <= frame <= f1:
                t = 0.0 if f1 == f0 else (frame - f0) / (f1 - f0)
                return tuple(keys[i][1 + c] + t * (keys[i + 1][1 + c] -
                                                   keys[i][1 + c])
                             for c in range(3))
        return tuple(float(v) for v in keys[-1][1:])

    def euler_track(self, bone_entry, which="part_a"):
        """Keyframes as (frame, rx, ry, rz) in RADIANS, Euler XYZ,
        1 unit = 360/256 degrees."""
        keys = self.track(bone_entry, which)
        if keys is None:
            return None
        return [(f, math.radians(v0 * DEG_PER_UNIT),
                 math.radians(v1 * DEG_PER_UNIT),
                 math.radians(v2 * DEG_PER_UNIT))
                for (f, v0, v1, v2) in keys]

    def summary(self):
        s = super().summary()
        s["frames"] = self.frame_count
        s["frame_votes"] = self.frame_votes
        return s


def load(path):
    with open(path, "rb") as f:
        return YANMDecoded(f.read())


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Decode a YANM clip's "
                                             "keyframes.")
    ap.add_argument("yanm", help="input .yanm file")
    ap.add_argument("--json", action="store_true",
                    help="emit the decoded tracks as JSON")
    args = ap.parse_args()
    y = load(args.yanm)
    if args.json:
        out = {"frames": y.frame_count, "bones": []}
        for b in y.bones:
            entry = {"bone": b["bone"],
                     "hash": f"{b['bone_hash']:08X}",
                     "starting_id": b["starting_id"],
                     "special": b["special"]}
            for which in ("part_a", "part_b"):
                keys = y.track(b, which)
                entry[which] = keys
            out["bones"].append(entry)
        print(json.dumps(out))
        return
    print(f"{args.yanm}: {len(y.data)} bytes, "
          f"{y.frame_count} frames (votes: {y.frame_votes})")
    for i, b in enumerate(y.bones):
        name = b["bone"] or f"hash_{b['bone_hash']:08X}"
        ka = y.track(b, "part_a")
        kb = y.track(b, "part_b")
        print(f"  [{i:2d}] {name:14s} id=0x{b['starting_id']:04x} "
              f"A={len(ka) if ka is not None else '-'} keys "
              f"B={len(kb) if kb is not None else '-'} keys")


if __name__ == "__main__":
    main()
