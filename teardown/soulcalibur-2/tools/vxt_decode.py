#!/usr/bin/env python3
"""SCII VXT texture decoder (phase 13).

Format (derived from the XBE relocator FUN_00025300 decompile, GRE phase-2
hunt8, + byte-level size accounting against idx47 VMX#1's VXT section):
  VXT header: magic 'VXT.', version byte 2 @+4, reloc list like VMX,
  texture count u16 @+8, records ptr u32 @+0x0c (VXT-relative).
  Texture record (36 B):
    +0x00 u32 palette-struct ptr (0 = none; struct = {data ptr, count<=0x100})
    +0x04 u32 common dword (0x241b typical; not needed for decode)
    +0x08 u32 flags (0xa2 when 2 mip levels present, else 0)
    +0x0c u16 width, u16 height
    +0x10 u32 pixel-data offset (VXT-relative)
    +0x14 u32 Xbox D3DFORMAT: 12=DXT1, 14=DXT3, 15=DXT5
    +0x18 u16 width, u16 height (descriptor copy)
    +0x1c u16 mip levels present (1 or 2 in fighter sets)
    +0x1e u16 flags (bit2 set => relocator skips data upload)
  Pixel data: Xbox-swizzled DXT blocks (block grid w/4 x h/4, element =
  one 8 B (DXT1) or 16 B (DXT3/5) block), mip levels stored consecutively.
"""
import struct, sys
import numpy as np

FMT = {11: ('P8', None), 12: ('DXT1', 8), 14: ('DXT3', 16), 15: ('DXT5', 16)}

def parse_vxt(buf, base=0):
    assert buf[base:base+4] == b'VXT.', buf[base:base+4]
    cnt = struct.unpack_from('<H', buf, base+8)[0]
    rec0 = struct.unpack_from('<I', buf, base+0x0c)[0]
    recs = []
    for i in range(cnt):
        r = base + rec0 + i*36
        pal, _common, fl08 = struct.unpack_from('<3I', buf, r)
        w, h = struct.unpack_from('<2H', buf, r+0x0c)
        data, fmt = struct.unpack_from('<2I', buf, r+0x10)
        w2, h2 = struct.unpack_from('<2H', buf, r+0x18)
        mips = struct.unpack_from('<H', buf, r+0x1c)[0]
        flags = struct.unpack_from('<H', buf, r+0x1e)[0]
        recs.append(dict(idx=i, pal=pal, fl08=fl08, w=w, h=h, data=data,
                         fmt=fmt, w2=w2, h2=h2, mips=mips, flags=flags))
    return recs

def level_size(w, h, fmt):
    if fmt == 11:  # P8: 1 byte per pixel
        return w * h
    _name, bs = FMT[fmt]
    return ((max(1, w//4)) * (max(1, h//4)) * bs)

def rec_size(rec):
    total, w, h = 0, rec['w'], rec['h']
    for _ in range(max(1, rec['mips'])):
        total += level_size(w, h, rec['fmt'])
        w, h = max(1, w//2), max(1, h//2)
    return total

# --- Xbox swizzle (documented NV2A/D3D8 tiled layout) -------------------
def _fill_pattern(pattern, value):
    # Canonical Xbox swizzle bit-spread: walk pattern bits ascending;
    # for each set pattern bit, consume the next bit of value.
    result, bit = 0, 1
    while value:
        if pattern & bit:
            if value & 1:
                result |= bit
            value >>= 1
        bit <<= 1
    return result

def _gen_masks(w, h):
    x, y, bit, mask = 0, 0, 1, 1
    while bit < w or bit < h:
        if bit < w:
            x |= mask; mask <<= 1
        if bit < h:
            y |= mask; mask <<= 1
        bit <<= 1
    return x, y

def unswizzle(buf, w, h, elem):
    """buf: swizzled bytes for a w x h grid of elem-byte elements.
    Returns linear row-major bytes."""
    mx, my = _gen_masks(w, h)
    out = bytearray(len(buf))
    for j in range(h):
        for i in range(w):
            off = _fill_pattern(mx, i) | _fill_pattern(my, j)
            out[(j*w+i)*elem:(j*w+i+1)*elem] = buf[off*elem:(off+1)*elem]
    return bytes(out)

# --- DXT decode -----------------------------------------------------------
def _c565(c):
    r, g, b = (c >> 11) & 31, (c >> 5) & 63, c & 31
    return (r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)

def dxt_decode(blocks, w, h, fmt):
    """blocks: linear bytes of the block grid; returns RGBA uint8 (h,w,4)."""
    bw, bh = max(1, w//4), max(1, h//4)
    img = np.zeros((bh*4, bw*4, 4), dtype=np.uint8)
    _name, bs = FMT[fmt]
    for by in range(bh):
        for bx in range(bw):
            blk = blocks[(by*bw+bx)*bs:(by*bw+bx+1)*bs]
            if fmt == 12:  # DXT1
                alpha_part, abits = None, 0
                cdata = blk
            else:
                abits = int.from_bytes(blk[:8], 'little')
                cdata = blk[8:]
                alpha_part = abits
            c0, c1 = struct.unpack_from('<2H', cdata, 0)
            idx = struct.unpack_from('<I', cdata, 4)[0]
            p0, p1 = _c565(c0), _c565(c1)
            if fmt == 12 and c0 <= c1:
                pal = [p0, p1,
                       tuple((p0[k]+p1[k])//2 for k in range(3)),
                       (0, 0, 0)]
                alphas = [255, 255, 255, 0]
            else:
                pal = [p0, p1,
                       tuple((2*p0[k]+p1[k])//3 for k in range(3)),
                       tuple((p0[k]+2*p1[k])//3 for k in range(3))]
                alphas = [255]*4
            for py in range(4):
                for px in range(4):
                    sel = (idx >> (2*(py*4+px))) & 3
                    r, g, b = pal[sel]
                    if fmt == 12:
                        a = alphas[sel]
                    elif fmt == 14:  # DXT3: explicit 4-bit alpha
                        a4 = (abits >> (4*(py*4+px))) & 0xF
                        a = a4 << 4 | a4
                    else:  # DXT5: interpolated alpha
                        a0, a1 = blk[0], blk[1]
                        ab = int.from_bytes(blk[2:8], 'little')
                        asel = (ab >> (3*(py*4+px))) & 7
                        if a0 > a1:
                            atab = [a0, a1] + [((7-k)*a0 + k*a1)//7 for k in range(1, 7)] if False else None
                            atab = [a0, a1, (6*a0+a1)//7, (5*a0+2*a1)//7, (4*a0+3*a1)//7,
                                    (3*a0+4*a1)//7, (2*a0+5*a1)//7, (a0+6*a1)//7]
                        else:
                            atab = [a0, a1, (4*a0+a1)//5, (3*a0+2*a1)//5, (2*a0+3*a1)//5,
                                    (a0+4*a1)//5, 0, 255]
                        a = atab[asel]
                    img[by*4+py, bx*4+px] = (r, g, b, a)
    return img[:h, :w]

def decode_texture(buf, vxt_base, rec, unsw=False):
    if rec['fmt'] == 11:  # P8 paletted: 1 B/px indices, palette via rec+0x00
        pp, pc = struct.unpack_from('<2I', buf, vxt_base + rec['pal'])
        pal = np.frombuffer(buf[vxt_base+pp: vxt_base+pp+pc*4], dtype=np.uint8).reshape(pc, 4)
        # palette entries stored B,G,R,A (Xbox D3DCOLOR memory order)
        rgba = np.stack([pal[:, 2], pal[:, 1], pal[:, 0], pal[:, 3]], axis=1)
        idx = np.frombuffer(buf[vxt_base+rec['data']: vxt_base+rec['data'] + rec['w']*rec['h']],
                            dtype=np.uint8)
        # P8 pixel data is stored Xbox-swizzled (proven: idx632 tex02 ear /
        # skin and idx944 tex06 Spawn emblem decode coherent only unswizzled,
        # while DXT records in the same archives decode coherent linear).
        raw = unswizzle(bytes(idx), rec['w'], rec['h'], 1)
        idx = np.frombuffer(raw, dtype=np.uint8)
        return rgba[idx].reshape(rec['h'], rec['w'], 4).copy()
    name, bs = FMT[rec['fmt']]
    bw, bh = max(1, rec['w']//4), max(1, rec['h']//4)
    n = bw*bh*bs
    raw = buf[vxt_base+rec['data']: vxt_base+rec['data']+n]
    if unsw:
        raw = unswizzle(raw, bw, bh, bs)
    return dxt_decode(raw, rec['w'], rec['h'], rec['fmt'])

if __name__ == '__main__':
    from PIL import Image
    d = open(sys.argv[1], 'rb').read()
    vmx = int(sys.argv[2], 0)
    v = vmx + struct.unpack_from('<I', d, vmx+0x18)[0]
    recs = parse_vxt(d, v)
    for i in [int(x) for x in sys.argv[3].split(',')]:
        rec = recs[i]
        for mode in ('unsw', 'lin'):
            img = decode_texture(d, v, rec, unsw=(mode == 'unsw'))
            Image.fromarray(img, 'RGBA').save(f'vxt_tex{i:02d}_{mode}.png')
            print('wrote', f'vxt_tex{i:02d}_{mode}.png', rec['w'], rec['h'], FMT[rec['fmt']][0])
