#!/usr/bin/env python3
"""Validate the USA spline tables: literal spline_sample port (USA addrs) vs
the analytic B-spline sampler, over every keyed channel of King's bank."""
import struct
import sys
from pathlib import Path

LOCAL = Path("/home/hatch/workspace/game-reverse-engineering/tekken3/tools/local")
RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(LOCAL))
sys.path.insert(0, str(RESEARCH))
import motion
import pose_sample_analytic as psa
from usa_tables import USA_SPLINE_TABLE_BASE

EXE = Path("/home/hatch/workspace/game-reverse-engineering/tekken3/disc/files/TEKKEN3/SLUS_004.02").read_bytes()


class UsaSplineTables:
    def __init__(self, exe: bytes) -> None:
        start = USA_SPLINE_TABLE_BASE - 0x40
        end = USA_SPLINE_TABLE_BASE + 0x620
        self.base = start
        self.blob = exe[start - 0x80010000 + 0x800: end - 0x80010000 + 0x800]

    def u8(self, addr: int) -> int:
        return self.blob[addr - self.base]

    def u16(self, addr: int) -> int:
        return struct.unpack_from("<H", self.blob, addr - self.base)[0]


def s32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def spline_sample_usa(keys, frame, frames, shift, tab) -> int:
    """motion.spline_sample with the table base rebound to the USA address."""
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


def main() -> None:
    bank = Path("/home/hatch/workspace/game-reverse-engineering/tekken3/animations/divmot03_king.bin").read_bytes()
    tab = UsaSplineTables(EXE)
    # decode a handful of move streams and compare every keyed channel sample
    worst = 0
    ncmp = 0
    tested = 0
    mb = motion.parse_bank(bank)
    for row in range(0, mb.move_count, 7):
        anim_word = mb.move_row(row)[0]
        if anim_word >= 0x40000000:
            continue
        stream = motion.parse_anim(bank, mb.anim_offset(anim_word))
        frames = stream.frames
        for ch in range(49):
            c = stream.counts[ch]
            if c <= 2 or c == frames:
                continue  # not a spline-keyed channel
            keys = stream.channels[ch]
            shift = motion.CHANNEL_SHIFT[ch]
            for f in (0, frames // 3, frames // 2, 2 * frames // 3, frames - 1):
                a = spline_sample_usa(keys, f, frames, shift, tab)
                b = psa.spline_sample_analytic(keys, f, frames, shift)
                d = abs(psa.s16(a * 2) - psa.s16(b * 2))
                worst = max(worst, d)
                ncmp += 1
        tested += 1
        if tested >= 60:
            break
    print(f"compared {ncmp} keyed-channel samples over {tested} moves: worst |diff| = {worst} (doubled s16 units)")
    assert worst <= 4, "USA spline tables diverge from analytic basis!"
    print("USA SPLINE_TABLE_BASE 0x8009671C VALIDATED")


if __name__ == "__main__":
    main()
