#!/usr/bin/env python3
"""VPW2 params: full 50-parameter decoder.

Translates the ROM params decoder (0x80006608, jump table at ROM 0x4B400)
case by case. Input: the 60-byte temp buffer from vpw2_params.unpack_params.
Output: 50 u16 parameters, exactly as the game computes them.

Bitfield note: params 0,1,2,5,6,8,9,15,16,35 decode one-hot/priority
fields from the u32 at temp[48]. That u32 is 0 for all 98 shipped
wrestlers (the two 1-bit reads that feed it are both 0), so those params
are constants for the shipped roster — they are almost certainly
edit-mode/CAW flags. The decoder is implemented faithfully anyway.
"""
import struct


def s8(b):
    return b - 256 if b >= 128 else b


def decode_params(temp):
    """temp: 60-byte buffer from unpack_params -> list of 50 ints (u16)."""
    assert len(temp) == 60
    bf = struct.unpack_from(">I", temp, 48)[0]
    p = [0] * 50

    def prio(pairs, default=0):
        # pairs: [(bit, value)] in code order; later set bits win
        v = default
        for bit, val in pairs:
            if bf & (1 << bit):
                v = val
        return v

    p[0] = prio([(0, 0), (1, 1), (2, 2)])
    p[1] = prio([(3, 0), (5, 1), (4, 2), (7, 3), (9, 4)])
    p[2] = prio([(10, 0), (11, 1), (12, 2)])
    p[3] = temp[0] - 1
    p[4] = s8(temp[1])
    p[5] = 0 if bf & (1 << 13) else 1
    p[6] = 1 if bf & (1 << 14) else 0
    p[7] = s8(temp[22])
    p[8] = prio([(15, 1), (16, 2), (17, 3), (18, 4), (19, 5)])
    p[9] = 3 if not (bf & 0x700000) else prio([(20, 0), (21, 1), (22, 2)])
    p[10] = s8(temp[23])
    # case 11: remap of temp[3]
    t3 = s8(temp[3])
    if t3 == 4:
        p[11] = 1
    elif t3 >= 5 and t3 == 6:
        p[11] = 2
    else:
        p[11] = 0
    # case 12: remap of temp[2]
    t2 = s8(temp[2])
    if t2 == 1:
        p[12] = 0
    elif t2 < 2:
        p[12] = 3 if t2 == 0 else 0
    elif t2 == 2:
        p[12] = 1
    elif t2 == 3:
        p[12] = 2
    else:
        p[12] = 0
    p[13] = s8(temp[5])
    p[14] = s8(temp[7]) - 1
    p[15] = prio([(23, 0), (24, 1)])
    p[16] = prio([(25, 0), (26, 1)])
    p[17] = s8(temp[20])
    p[18] = s8(temp[6])
    p[19] = s8(temp[9])
    p[20] = s8(temp[8])
    for i in range(21, 31):
        p[i] = s8(temp[i - 11])  # p21..p30 <- temp[10..19]
    p[31] = struct.unpack_from(">H", temp, 40)[0]
    p[32] = struct.unpack_from(">H", temp, 42)[0]
    p[33] = struct.unpack_from(">H", temp, 44)[0]
    p[34] = struct.unpack_from(">H", temp, 46)[0]
    p[35] = 0 if bf & (1 << 27) else 1
    p[36] = s8(temp[21])
    p[37] = s8(temp[24])
    p[38] = s8(temp[25])
    p[39] = s8(temp[26])
    p[40] = struct.unpack_from(">H", temp, 28)[0]
    p[41] = s8(temp[30])
    p[42] = s8(temp[31])
    p[43] = struct.unpack_from(">H", temp, 32)[0]
    p[44] = s8(temp[34])
    p[45] = s8(temp[35])
    p[46] = s8(temp[36])
    p[47] = s8(temp[37])
    p[48] = s8(temp[38])
    p[49] = s8(temp[39])
    return [v & 0xFFFF for v in p]


STYLE_ONEHOT = {1: "wrestling", 2: "combo", 4: "shoot"}


def style_from_params(params):
    """Style lives in param 34's low byte, bits 0-2, one-hot."""
    return STYLE_ONEHOT.get(params[34] & 7)
