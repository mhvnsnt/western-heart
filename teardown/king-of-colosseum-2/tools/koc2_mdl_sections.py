#!/usr/bin/env python3
"""Parse KoC2 .mdl model files (kc2fire001/fileNNNNN.bin) into sections.

Section structure (verified 2026-11-19, lane W2):
  Each section: u32 size, u32 type, u32 a (0, except type 4 has 1),
  u32 b, then 3x (x,y,z,w) float vectors at +16 (per-part transform;
  identity (0,0,0,1)x3 on section 0, non-identity on mesh parts),
  then payload. Sections tile the file; a trailer of a repeated u16
  (0x1066/0x1067, 16-96 bytes) follows the last section.
  Types: 0 = skeleton/bones? (~4/file), 1 = mesh parts (~12/file),
  2 = exactly 1/file, 4 = exactly 1/file (last).
  Field b ~= 2.4x section size — hypothesis: unpacked VU-memory size
  (VIF unpack expansion); NOT verified.
  Payload from ~+0x88 is VIF/GIF DMA packet data (u16 components,
  0x1000 = fixed-point 1.0 markers, repeated 6-word chunks = shared
  vertices). Vertex/face extraction is still open (needs a VIF
  unpack interpreter).

Usage: koc2_mdl_sections.py <file.bin> [file2.bin ...]
"""
import struct
import sys


def parse_sections(d):
    secs = []
    off = 0
    while off + 16 <= len(d):
        size, typ, a, b = struct.unpack_from("<IIII", d, off)
        if size < 16 or off + size > len(d):
            break
        secs.append((off, size, typ, a, b))
        off += size
    return secs, off


def describe(path):
    d = open(path, "rb").read()
    secs, end = parse_sections(d)
    print(f"{path}: {len(d)} bytes, {len(secs)} sections, "
          f"trailer {len(d) - end} bytes "
          f"({d[end:end + 8].hex() if end < len(d) else '-'})")
    for off, size, typ, a, b in secs:
        vecs = [struct.unpack_from("<ffff", d, off + 16 + i * 16)
                for i in range(3)]
        print(f"  @{off:#06x} size={size:6d} type={typ} a={a} "
              f"b={b:#x} (b/size={b / size:.2f}) "
              f"vecs={[(round(x, 3), round(y, 3), round(z, 3), round(w, 3)) for x, y, z, w in vecs]}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        describe(p)
