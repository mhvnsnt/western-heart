#!/usr/bin/env python3
"""Sample a Tekken 3 motion-bank pose WITHOUT the Japan Rev.1 EXE tables.

n0madic/tekken3remake's tools/research/motion.py is a literal port of the
game's AnimDecodePose, but its B-spline weight tables are read from the
Japan Rev.1 executable (SPLINE_TABLE_BASE 0x80096B40). Our disc is the USA
release (SLUS_004.02) and we do not have the JP EXE, so the tables are
unavailable.

This module re-implements ONLY the weight lookup analytically:
- The tables hold the uniform cubic B-spline basis (documented in
  n0madic docs/research/formats/animation.md):
      B0(u) = (1-u)^3/6, B1(u) = (3u^3-6u^2+4)/6,
      B2(u) = (-3u^3+3u^2+3u+1)/6, B3(u) = u^3/6,  u = local/length
- Frame 0 of a segment uses the game's documented MODIFIED first-segment
  weights (1/6, 4/6, 1/6) -- exactly as AnimSplineSample does when
  t6 == 0 and local == 0.
- The game additionally quantizes `local` to an even value via the byte
  index table; we use the exact local time instead.

Accuracy: table rounding + the local-time quantization mean values can
differ from the hardware by ~1-2 units (out of 65536). For bind-pose
extraction that is ~0.01 degrees -- irrelevant. The channel topology,
key-frame walk, channel mirroring (odd channels are stored reversed),
and the c==0/1/2/n fast paths are identical to the verified port.

Usage:
    python3 tools/local/pose_sample_analytic.py <divmot.bin> <slot> <frame>
        --out pose.json
Prints the 49-channel pose vector (s16, already doubled, as the game
writes it) and optionally saves it as JSON.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(RESEARCH))
import motion  # noqa: E402  -- verified parser + channel layout only

# Modified first-segment weights at t=0, in 1/65536 units (doc: "1/6, 4/6, 1/6").
W_FIRST_B = round(4 / 6 * 65536)  # multiplies (P[1]-P[0])
W_FIRST_C = round(1 / 6 * 65536)  # multiplies (P[2]-P[0])


def s16(v: int) -> int:
    v &= 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def spline_sample_analytic(keys: list[int], frame: int, frames: int, shift: int) -> int:
    """AnimSplineSample with the EXE weight tables replaced by the analytic
    uniform cubic B-spline basis. `keys` are the channel's s16 words."""
    last = frames - 1
    t6 = t7 = 0
    t0 = keys[0]
    t4 = keys[1]
    ki = 2
    t1 = t0
    t3 = ((t4 >> 5) << shift) + t1
    t4 &= 0x1F
    t2 = t3
    while True:
        t7 += t4 + 1
        t2 = t3
        if t7 == last:
            break
        t4 = keys[ki]
        ki += 1
        t3 += (t4 >> 5) << shift
        t5 = frame - t7
        t4 &= 0x1F
        if t5 <= 0:
            break
        t6 = t7
        t0, t1 = t1, t2
    local = frame - t6
    length = t7 - t6
    if t6 == 0 and local == 0:
        # First segment at t=0: game's modified weights (1/6, 4/6, 1/6).
        v0 = W_FIRST_C * (t3 - t1) + W_FIRST_B * (t2 - t1)
        v0 = s32(v0) >> 16  # arithmetic shift, like MIPS sra
        return s32(v0 + t1)
    # Interior/last segment: standard uniform cubic B-spline basis.
    # (The game quantizes `local` to even and reads precomputed table
    # weights; the analytic basis matches to ~1-2 units.)
    u = local / length if length else 0.0
    b0 = (1 - u) ** 3 / 6
    b1 = (3 * u ** 3 - 6 * u ** 2 + 4) / 6
    b2 = (-3 * u ** 3 + 3 * u ** 2 + 3 * u + 1) / 6
    b3 = u ** 3 / 6
    return s32(round(b0 * t0 + b1 * t1 + b2 * t2 + b3 * t3))


def sample_channel_analytic(stream: "motion.AnimStream", ch: int, frame: int) -> int:
    n = stream.frames
    frame = min(max(frame, 0), n - 1)
    f = n - (frame + 1) if ch & 1 else frame
    c = stream.counts[ch]
    keys = stream.channels[ch]
    if c == 0:
        return 0
    if c == 1:
        v = keys[0]
    elif c == 2:
        t = keys[1] * f
        if n > 9:
            t >>= 5
        v = (keys[0] & 0xFFFF) + t
    elif c == n:
        v = keys[f]
    else:
        v = spline_sample_analytic(keys, f, n, motion.CHANNEL_SHIFT[ch])
    return s16(v << 1)


def sample_pose_analytic(stream: "motion.AnimStream", frame: int,
                         channels: int = motion.POSE_CHANNELS) -> list[int]:
    return [sample_channel_analytic(stream, ch, frame) for ch in range(channels)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bank", type=Path, help="divmotNN.bin motion bank")
    ap.add_argument("slot", type=int, help="move-index slot (0-2 = stance moves)")
    ap.add_argument("frame", type=int, nargs="?", default=0, help="frame to sample")
    ap.add_argument("--out", type=Path, default=None, help="write pose JSON here")
    args = ap.parse_args()

    data = args.bank.read_bytes()
    bank = motion.parse_bank(data)
    row_no = bank.move_index[args.slot]
    row = bank.move_row(row_no)
    anim_word = row[0]
    if anim_word >= motion.COMMON_FLAG:
        raise SystemExit("slot refers to the divmot99 common bank -- extract it first")
    stream = motion.parse_anim(data, bank.anim_offset(anim_word))
    pose = sample_pose_analytic(stream, args.frame)

    names = (["root_x", "root_y", "root_z"]
             + [f"ik{i}_{ax}" for i in range(4) for ax in "xyz"]
             + [f"swivel{i}" for i in range(4)]
             + [f"joint{j}_{ax}" for j in range(10) for ax in "xyz"])
    rec = {
        "bank_type": bank.type_code,
        "slot": args.slot,
        "move_row": row_no,
        "frame": args.frame,
        "stream_frames": stream.frames,
        "pose_channels": dict(zip(names, pose)),
        "pose_raw": pose,
        "note": ("analytic B-spline weights (no JP EXE tables); "
                 "~1-2 units vs hardware; odd channels stored reversed"),
    }
    if args.out:
        args.out.write_text(json.dumps(rec, indent=1))
        print("wrote", args.out)
    print("pose:", pose)
    # Human-readable angle summary for the 10 Euler joints (65536 = 360 deg).
    angs = pose[19:49]
    print("euler joints (deg):",
          [f"{a / 65536 * 360:+.1f}" for a in angs])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
