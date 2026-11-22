"""Asmik LZSS decoder, ported from VPWStudio Helpers/AsmikLzss.cs (MIT).

Format: byte0 == 0x00 (compressed marker), bytes1-3 = BE decompressed size,
then the LZSS stream. If byte0 != 0x00 the data is returned unchanged.
"""
import struct


def asmik_decode(raw):
    if not raw or raw[0] != 0x00:
        return raw
    file_len = struct.unpack('>I', raw[:4])[0]
    out = bytearray()
    ip = 4
    cmd = 0
    n = len(raw)
    while len(out) < file_len:
        cmd >>= 1
        if cmd < 2:
            if ip >= n:
                break
            cmd = raw[ip] | 0x0100
            ip += 1
        if cmd & 1:
            if ip >= n:
                break
            out.append(raw[ip])
            ip += 1
        else:
            if ip + 1 >= n:
                break
            p = raw[ip]
            l = raw[ip + 1]
            ip += 2
            p |= ((l << 4) & 0x0F00)
            l &= 0x0F
            p += 0x12
            p &= 0x0FFF
            c = len(out) & 0x0FFF
            p -= c
            if p >= 0:
                p -= 0x1000
            p += len(out)
            for _ in range(l + 3):
                out.append(out[p] if p >= 0 else 0)
                p += 1
    return bytes(out)
