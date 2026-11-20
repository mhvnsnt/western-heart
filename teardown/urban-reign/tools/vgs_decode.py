#!/usr/bin/env python3
"""VGS (Namco PS2 UI screen) format decoder — Urban Reign teardown.
Parses VGS header, column table, display-list payloads, and extracts
embedded texture data to viewable PNGs.

Format (reverse-engineered 2026-10-13):
  0x00: magic 03 08 04 00
  0x04: grid width  (u16) — number of COLUMN records
  0x06: grid height (u16) — tiles per column
  0x08: u32 reserved (0)
  0x0C..0x18: section offsets (u32 x4)
  0x1C: u32 reserved (0)
  0x20: column records, W x 32 bytes:
        [0x50000000, payload_offset(u32, absolute), 0, 0,
         0x60000000, 0, 0, 0]
  payload: display list of (u64 value, u64 reg) 16-byte commands:
        reg 0x50: texture EE-RAM address
        reg 0x52: (w,h) sprite dimensions (two u32s in value)
        reg 0x60000000: end of column payload
  texture data: embedded blob (title.vgs @0x12BD0, 218984 bytes);
        8-bit indexed pixels, renders recognizably at 320px wide
        (exact CLUT/color pipeline still open).

Usage:
  python3 vgs_decode.py <file.vgs> [outdir]   # parse + dump textures
  python3 vgs_decode.py --info <file.vgs>      # header/sprites only
"""
import os, struct, sys

MAGIC = b"\x03\x08\x04\x00"
TERM = 0x60000000

def parse_vgs(path):
    d = open(path, "rb").read()
    if d[0:4] != MAGIC:
        raise ValueError(f"{path}: bad magic {d[0:4]!r}")
    W, H = struct.unpack("<HH", d[4:8])
    info = {"path": path, "size": len(d), "grid": (W, H),
            "sections": struct.unpack("<4I", d[0x0C:0x1C]),
            "columns": []}
    for c in range(W):
        off = 0x20 + c * 32
        desc, poff = struct.unpack("<II", d[off:off + 8])
        assert desc == 0x50000000, f"col{c}: bad desc {desc:#x}"
        col = {"payload_off": poff, "sprites": []}
        p = poff
        cur = {}
        for _ in range(500):
            if p + 16 > len(d):
                break
            val, reg = struct.unpack("<QQ", d[p:p + 16])
            if reg == TERM:
                break
            if reg == 0x52:
                w32, h32 = struct.unpack("<II", d[p:p + 8])
                cur["w"], cur["h"] = w32, h32
            elif reg == 0x50:
                cur["tex_addr"] = val
            elif reg == 0x53 and "w" in cur:
                col["sprites"].append(dict(cur))
                cur = {}
            p += 16
        info["columns"].append(col)
    return d, info

def find_texture_blob(d, info):
    """Heuristic: largest high-entropy region after the display lists."""
    # display lists end well before 0x10000 in practice; scan for the
    # first 256-byte window past 0x1000 that is >90% bytes >= 0x40
    # and treat the run as the texture blob. Falls back to manual.
    n = len(d)
    start = None
    for i in range(0x1000, n - 256, 16):
        w = d[i:i + 256]
        if sum(1 for b in w if b >= 0x40) > 200:
            # confirm it continues
            w2 = d[i + 256:i + 512]
            if sum(1 for b in w2 if b >= 0x40) > 150:
                start = i
                break
    return start

def decode_texture(d, outdir, base, width=320):
    from PIL import Image
    import numpy as np
    px = np.frombuffer(d[base:], dtype=np.uint8)
    W = width
    h = len(px) // W
    img = px[:W * h].reshape(h, W)
    even = img[0::2]  # deinterlace: even field is cleaner
    im = Image.frombytes("L", (W, even.shape[0]), even.tobytes())
    out = os.path.join(outdir, "texture_8bit_w%d.png" % W)
    im.save(out)
    return out

def main():
    args = sys.argv[1:]
    info_only = args and args[0] == "--info"
    if info_only:
        args = args[1:]
    path = args[0]
    outdir = args[1] if len(args) > 1 else os.path.dirname(path) or "."
    d, info = parse_vgs(path)
    W, H = info["grid"]
    print(f"{os.path.basename(path)}: {len(d)} bytes, grid {W}x{H}")
    print(f"  sections: {[hex(x) for x in info['sections']]}")
    nspr = 0
    for c, col in enumerate(info["columns"]):
        print(f"  col{c}: payload@{col['payload_off']:#x}, {len(col['sprites'])} sprites")
        for s in col["sprites"][:12]:
            print(f"    {s.get('w')}x{s.get('h')} tex={s.get('tex_addr', 0):#x}")
        nspr += len(col["sprites"])
    print(f"  total sprites: {nspr}")
    if not info_only:
        blob = find_texture_blob(d, info)
        if blob:
            print(f"  texture blob @ {blob:#x} ({len(d)-blob} bytes)")
            out = decode_texture(d, outdir, blob)
            print(f"  wrote {out}")
        else:
            print("  no texture blob found (display-list-only file)")

if __name__ == "__main__":
    main()
