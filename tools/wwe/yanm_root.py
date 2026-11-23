#!/usr/bin/env python3
"""J_Hips root-motion decoder for WWE 2K19 YANM clips.

Decodes the root-motion track (J_Hips Part B, or the third pair on
StartingID 0x5100 clips), reverse-engineered 2026-11-19 from the
18,862-clip moves pack. This is the track W4 left open ("J_Hips
Part B (root motion): format open") -- it is now decoded and
validated (see docs/YOBJ-YANM.md "Root motion (decoded)").

FORMAT
------
  Records: 8 bytes, big-endian: (i16 dx, i16 dy, i16 dz, u16 dt).
  The length field counts 8-byte records: the true byte span is
  length * 8, i.e. TWICE what yanm.py's length*4 gives. (W4's
  hips_b_track read only half the track, which is why its u16
  column did not sum to the frame count.)
  dt = frames until the next keyframe; the dts sum to the clip's
  frame count (274/279 primary clips exactly; the rest are
  trimmed takes whose track runs past the clip end -- see below).
  Record 0 is always (0, 0, 0, dt=0): the track starts at the
  origin. Record i sits at frame sum(dt[0..i-1]).
  Value = root DISPLACEMENT over [frame_i, frame_i + dt_i), so
  value/dt is the per-frame velocity (smooth: ~5x smoother than
  the raw values across 279 clips) and the position at keyframe i
  is the forward cumulative sum of the values before i. The
  backward reading is ruled out: record 1 sits at frame 0 with a
  nonzero value, a nonzero displacement over a zero-length
  interval under the backward reading.
  Scale: the first trailing float of the J_Hips entry is cm per
  unit (~0.0002-0.0006, per clip). Absolute start position: the
  next three trailing floats (cm) in the shared pair frame.
  Trailing floats live at +0x18 on 0x28-long entries (0x4100,
  root motion in Part B) and at +0x20 on 0x30-long entries
  (0x5100, root motion in the third pair at +0x18; Part B there
  is 4-byte records, a different track).

COORDINATES (cm, shared pair frame, 60 fps assumed)
---------------------------------------------------
  x = lateral, y = vertical (+down), z = forward.
  Origin: the receiver's start ground position (receivers start
  at x ~= 0, z ~= 0). y ~= 3-10 standing, ~= 90-95 lying flat
  (hips height above the mat is about 96 - y cm, +/-10 cm).
  Both performers' clips share the frame: the attacker runs
  toward the receiver in it (median approach-angle error 15.5
  deg over 19 running/dive moves), and paired clips swap
  positions exactly as the move demands (german suplex, suplex).

VALIDATION (see docs/YOBJ-YANM.md for the full list)
----------------------------------------------------
  Run-up: running big boot covers 2.6 m at 2.8-4.6 m/s. Moonwalk
  glides 2.2 m at 0.6-0.9 m/s. In-place dance stays within 32 cm.
  Lying receivers end at y +48..+92 cm (drop to the mat);
  standing receivers end at y -8..+9 cm. Spear: attacker starts
  2.6 m out, runs through the receiver, ends standing 1.4 m
  past; receiver ends lying at y 94.5. Vertical suplex receiver
  is held at ~184 cm, then slammed to y 95.5.

EDGE CASES
----------
  Trimmed takes (eye_rake): the track's dt-sum (169) exceeds the
  clip length (98/153) -- the source take was longer. Records
  past the clip end are flagged (truncated=True) and excluded
  from sampling; records within the clip are valid.
  0x5100 clips (Suplex 7 receiver): root motion is the third
  pair, not Part B. Handled here; 3 of 279 primary clips.
  Saturated record: every clip carries exactly one record with
  |value| == 32766 (0x7FFE) in one channel. Meaning OPEN (tested
  2026-11-19: not the speed peak, landing frame, max-inclination
  frame, acceleration peak, or a shared event frame). Max-speed
  metrics must use smoothed speeds -- the raw 1-frame speed at
  that record is a spike, not a sustained velocity. If the value
  is a clamp, the position error it introduces is bounded by
  ~one record's displacement (~5 cm).

Usage:
  yanm_root.py <clip.yanm> [--json]   # print root trajectory
"""

import json
import struct
import sys

J_HIPS_HASH = 0xF91A7A26


def _argmax_abs(a, b, c):
    m = max(abs(a), abs(b), abs(c))
    return 0 if abs(a) == m else (1 if abs(b) == m else 2)


def _u16be(b, o):
    return struct.unpack_from(">H", b, o)[0]


def _u32be(b, o):
    return struct.unpack_from(">I", b, o)[0]


def find_hips_entry(data):
    """Walk the bone entries; return the J_Hips root-motion layout.

    Returns dict with starting_id, header_len, root_index,
    root_length (record count), floats_offset, or None if the
    clip has no J_Hips entry."""
    if data[:4] != b"YANM":
        raise ValueError(f"not a YANM clip (magic {data[:4]!r})")
    count = _u16be(data, 0x0A)
    off = 0x10
    for _ in range(count - 1):
        if off + 0x10 > len(data):
            break
        start_id = _u16be(data, off)
        hlen = _u16be(data, off + 2)
        bone_hash = _u32be(data, off + 4)
        if bone_hash == J_HIPS_HASH:
            if hlen >= 0x30:
                # 0x5100: root motion is the third pair (+0x18);
                # trailing floats at +0x20.
                idx, ln = struct.unpack_from(">II", data, off + 0x18)
                return {"starting_id": start_id, "header_len": hlen,
                        "root_index": idx, "root_length": ln,
                        "floats_offset": off + 0x20,
                        "variant": "third_pair"}
            # 0x4100: root motion is Part B (+0x10); trailing
            # floats at +0x18.
            idx, ln = struct.unpack_from(">II", data, off + 0x10)
            return {"starting_id": start_id, "header_len": hlen,
                    "root_index": idx, "root_length": ln,
                    "floats_offset": off + 0x18,
                    "variant": "part_b"}
        if hlen < 0x10 or hlen > 0x100:
            break
        off += hlen
    return None


def parse_root_records(data, index, length):
    """8-byte records -> [(frame, dx, dy, dz), ...]; frame is the
    absolute frame of the keyframe (cumulative dt)."""
    part = data[index + 8: index + 8 + length * 8]
    keys = []
    frame = 0
    dt_sum = 0
    for j in range(0, len(part) - 7, 8):
        dx, dy, dz, dt = struct.unpack_from(">hhhH", part, j)
        keys.append((frame, dx, dy, dz))
        frame += dt
        dt_sum += dt
    return keys, dt_sum


def frame_count(data):
    """Clip frame count: majority vote of the Part A/B dt-sums
    (yanm_decode's rule, excluding J_Hips Part B)."""
    # Inline vote (same rule as yanm_decode.YANMDecoded).
    from yanm import YANM
    y = YANM(data)
    totals = {}
    for b in y.bones:
        if b["special"]:
            continue
        for which in ("part_a", "part_b"):
            idx, ln = b[which]
            if ln == 0:
                continue
            if b["bone_hash"] == J_HIPS_HASH and which == "part_b":
                continue
            part = data[idx + 8: idx + 8 + ln]
            if len(part) % 4:
                continue
            total = sum(part[i + 3] for i in range(0, len(part) - 3, 4))
            totals[total] = totals.get(total, 0) + 1
    return max(totals, key=totals.get) if totals else 0


class RootMotion:
    """Decoded root trajectory of one YANM clip."""

    def __init__(self, data):
        self.data = data
        entry = find_hips_entry(data)
        if entry is None:
            raise ValueError("no J_Hips entry in this clip")
        self.variant = entry["variant"]
        self.starting_id = entry["starting_id"]
        fl = struct.unpack_from(">4f", data, entry["floats_offset"])
        self.scale = fl[0]              # cm per unit
        self.start = (fl[1], fl[2], fl[3])  # absolute start (cm)
        keys, dt_sum = parse_root_records(
            data, entry["root_index"], entry["root_length"])
        self.dt_sum = dt_sum
        self.frames = frame_count(data)
        self.dt_valid = (dt_sum == self.frames)
        # Truncated take: the track runs past the clip end; only
        # records within the clip are valid samples.
        self.truncated = dt_sum > self.frames
        # Forward cumulative sum -> absolute positions (cm).
        self.keyframes = []  # (frame, x, y, z)
        x = y = z = 0.0
        for i, (fr, dx, dy, dz) in enumerate(keys):
            if i > 0:
                px, py, pz = keys[i - 1][1], keys[i - 1][2], keys[i - 1][3]
                x += px * self.scale
                y += py * self.scale
                z += pz * self.scale
            self.keyframes.append((fr, self.start[0] + x,
                                   self.start[1] + y,
                                   self.start[2] + z))
        self.n_records = len(keys)
        self.n_in_clip = sum(1 for (fr, *_)
                             in self.keyframes if fr < self.frames)
        # Saturated records: exactly one per clip in all 279 primary
        # clips, always |value| 32766 (0x7FFE) in one channel. Its
        # meaning is OPEN (tested 2026-11-19: not the speed peak,
        # landing, max-inclination, acceleration peak, or a shared
        # event frame). Recorded here as an observed datum, not
        # interpreted. If it is a clamp, the position error from it
        # is bounded by ~one record's displacement (~5 cm).
        self.saturated = []
        for (fr, dx, dy, dz) in keys:
            ch = _argmax_abs(dx, dy, dz)
            val = (dx, dy, dz)[ch]
            if abs(val) >= 32766:
                self.saturated.append(
                    {"frame": fr, "channel": ("x", "y", "z")[ch],
                     "value": int(val)})

    def sample(self, frame):
        """Absolute root position (x, y, z) cm at an integer frame
        (linear interpolation between keyframes, hold ends).
        Only keyframes within the clip are used."""
        kf = [(fr, x, y, z) for (fr, x, y, z) in self.keyframes
              if fr < self.frames]
        if not kf:
            return self.start
        if frame <= kf[0][0]:
            return kf[0][1:]
        if frame >= kf[-1][0]:
            return kf[-1][1:]
        for i in range(len(kf) - 1):
            f0, f1 = kf[i][0], kf[i + 1][0]
            if f0 <= frame <= f1:
                t = 0.0 if f1 == f0 else (frame - f0) / (f1 - f0)
                return tuple(kf[i][1 + c] + t * (kf[i + 1][1 + c]
                                                 - kf[i][1 + c])
                             for c in range(3))
        return kf[-1][1:]

    def sample_all(self, n_frames=None):
        """Per-frame positions (n_frames x 3); defaults to the
        clip length."""
        n = n_frames if n_frames is not None else self.frames
        return [self.sample(f) for f in range(n)]

    def summary(self):
        return {
            "frames": self.frames,
            "variant": self.variant,
            "starting_id": hex(self.starting_id),
            "scale_cm_per_unit": self.scale,
            "start_cm": [round(v, 1) for v in self.start],
            "n_records": self.n_records,
            "n_in_clip": self.n_in_clip,
            "dt_sum": self.dt_sum,
            "dt_valid": self.dt_valid,
            "truncated": self.truncated,
            "saturated_records": self.saturated,
        }


def load(path):
    with open(path, "rb") as f:
        return RootMotion(f.read())


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Decode a YANM clip's "
                                             "root motion.")
    ap.add_argument("yanm", help="input .yanm file")
    ap.add_argument("--json", action="store_true",
                    help="emit the trajectory as JSON")
    args = ap.parse_args()
    r = load(args.yanm)
    if args.json:
        out = r.summary()
        out["keyframes"] = [
            {"frame": fr, "x_cm": round(x, 1), "y_cm": round(y, 1),
             "z_cm": round(z, 1)}
            for (fr, x, y, z) in r.keyframes if fr < r.frames]
        print(json.dumps(out))
        return
    s = r.summary()
    print(f"{args.yanm}: {s['frames']} frames, variant={s['variant']}, "
          f"scale={s['scale_cm_per_unit']:.6f} cm/unit")
    print(f"  start={s['start_cm']} cm, records={s['n_records']} "
          f"({s['n_in_clip']} in clip), dt_sum={s['dt_sum']} "
          f"({'OK' if s['dt_valid'] else 'TRUNCATED' if s['truncated'] else 'MISMATCH'})")
    kf = [(fr, x, y, z) for (fr, x, y, z) in r.keyframes
          if fr < r.frames]
    for i in range(0, len(kf), max(1, len(kf) // 10)):
        fr, x, y, z = kf[i]
        print(f"  f={fr:4d} ({x:7.1f} {y:7.1f} {z:7.1f})")
    fr, x, y, z = kf[-1]
    print(f"  f={fr:4d} ({x:7.1f} {y:7.1f} {z:7.1f})  <- end")


if __name__ == "__main__":
    main()
