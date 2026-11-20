#!/usr/bin/env python3
"""Bit-exact Tekken 3 animation sampling for the USA release (SLUS_004.02).

Literal port of n0madic/tekken3remake's motion.py spline machinery, rebound
to the verified USA table addresses (see usa_tables.py). n0madic verified
this algorithm against the game's AnimDecodePose in a CPU harness with zero
mismatches (Japan Rev.1); the USA tables were verified by content 2026-10-13
(weight curves match the analytic B-spline basis; A[0] = 65536/6 exactly).

Prefer this over pose_sample_analytic.py: the analytic version mis-models
the game's first-segment weights (up to ~40 units / 0.2 deg error on
first-segment interiors) and skips the game's even-quantization of `local`.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(RESEARCH))
import motion  # noqa: E402  (AnimStream/parse_anim/parse_bank/MotionBank)

from usa_tables import USA_SPLINE_TABLE_BASE, USA_CHANNEL_SHIFT

EXE_BASE = 0x80010000
EXE_HEADER = 0x800


class UsaSplineTables:
    """motion.SplineTables rebound to the USA SPLINE_TABLE_BASE."""

    def __init__(self, exe: bytes) -> None:
        start = USA_SPLINE_TABLE_BASE - 0x40
        end = USA_SPLINE_TABLE_BASE + 0x620
        self.base = start
        self.blob = exe[start - EXE_BASE + EXE_HEADER: end - EXE_BASE + EXE_HEADER]

    def u8(self, addr: int) -> int:
        return self.blob[addr - self.base]

    def u16(self, addr: int) -> int:
        return struct.unpack_from("<H", self.blob, addr - self.base)[0]


def s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def s16(v: int) -> int:
    v &= 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def spline_sample(keys: list[int], frame: int, frames: int, shift: int,
                  tab: UsaSplineTables) -> int:
    """Literal port of AnimSplineSample (USA tables)."""
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
    t9 = USA_SPLINE_TABLE_BASE
    if local:
        if length - 16 <= 0:
            idx = tab.u8(t9 + length * 32 + local - 0x21)
        else:
            idx = tab.u8(t9 - length * 32 - local + 0x420)
        local = idx << 1
    t8 = t9 + local
    t9 = t9 - local
    v1 = 0
    if t6 == 0:
        lo = tab.u16(t9 + 0x300) * (t3 - t1)
        a1 = tab.u16(t9 + 0x504)
        v0 = lo
    else:
        lo = tab.u16(t8 + 0x200) * (t0 - t1)
        if t7 != last:
            v1 = lo
            lo = tab.u16(t9 + 0x300) * (t3 - t1)
            a1 = tab.u16(t9 + 0x402)
            v0 = lo + v1
        else:
            a1 = tab.u16(t9 + 0x504) + tab.u16(t9 + 0x300) + 0x2AAB
            v0 = lo
    v0 += a1 * (t2 - t1)
    v0 = s32(v0) >> 16
    return s32(v0 + t1)


def sample_channel(stream: motion.AnimStream, ch: int, frame: int,
                   tab: UsaSplineTables,
                   channel_shift: list[int] = motion.CHANNEL_SHIFT) -> int:
    """Value of one channel at 0-based `frame`, as AnimDecodePose writes it."""
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
        v = spline_sample(keys, f, n, channel_shift[ch], tab)
    return s16(v << 1)


def sample_pose(stream: motion.AnimStream, frame: int, tab: UsaSplineTables,
                channel_shift: list[int] = motion.CHANNEL_SHIFT,
                channels: int = motion.POSE_CHANNELS) -> list[int]:
    return [sample_channel(stream, ch, frame, tab, channel_shift) for ch in range(channels)]


def load_channel_shift(exe: bytes) -> list[int]:
    off = USA_CHANNEL_SHIFT - EXE_BASE + EXE_HEADER
    return list(exe[off:off + 49])
