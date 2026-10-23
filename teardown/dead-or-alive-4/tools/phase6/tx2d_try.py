"""TX2D trial decode for DOA4 chrone pkg00.
Tiled-address port from Xenia (BSD-3, Copyright Ben Vanik / Xenia project):
  src/xenia/gpu/texture_address.h Tiled2D/TiledCombine, itself derived from
  crunch crn_decomp.h and AMD AddrLib (see header comments in that file).
Descriptor = X360 texture fetch constant at desc words 7,8,9
  (dword_0: tiled bit31 + pitch[30:22]<<5; dword_1: format[5:0], endian[7:6],
   base_address[31:12] in 4K pages; dword_2: size_2d width[12:0], height[25:13]).
"""
import numpy as np, struct, sys

def tiled_combine(oib, bank, pipe, y_lsb):
    return ((y_lsb << 4) | (pipe << 6) | (bank << 11) |
            (oib & 0xF) | (((oib >> 4) & 1) << 5) |
            (((oib >> 5) & 0x7) << 8) | ((oib >> 8) << 12))

def tiled2d(x, y, pitch_aligned, bpb_log2):
    outer_blocks = ((y >> 5) * (pitch_aligned >> 5) + (x >> 5)) << 6
    inner_blocks = (((y >> 1) & 0b111) << 3) | (x & 0b111)
    oib = (outer_blocks | inner_blocks) << bpb_log2
    bank = (y >> 4) & 1
    pipe = ((x >> 3) & 0b11) ^ (((y >> 3) & 1) << 1)
    return tiled_combine(oib, bank, pipe, y & 1)

_off_cache = {}
def untile(data, wb, hb, pitch_b, bpb):
    """data: tiled bytes; wb/hb: texture size in blocks; pitch_b: storage pitch in blocks.
    Returns linear block bytes (hb x wb x bpb). Vectorized gather."""
    key = (wb, hb, pitch_b, bpb)
    if key not in _off_cache:
        bpb_log2 = {8: 3, 16: 4}[bpb]
        offs = np.array([tiled2d(bx, by, pitch_b, bpb_log2)
                         for by in range(hb) for bx in range(wb)], dtype=np.int64)
        _off_cache[key] = offs
    offs = _off_cache[key]
    src = np.frombuffer(data, dtype=np.uint8)
    idx = (offs[:, None] + np.arange(bpb)[None, :]).reshape(-1)
    return src[idx].reshape(hb, wb, bpb)

def dxt_colors(c):
    r = ((c >> 11) & 31); g = ((c >> 5) & 63); b = (c & 31)
    return np.array([r * 255 // 31, g * 255 // 63, b * 255 // 31], dtype=np.int32)

def decode_dxt1(blocks):
    hb, wb = blocks.shape[:2]
    img = np.zeros((hb * 4, wb * 4, 4), dtype=np.uint8); img[..., 3] = 255
    for by in range(hb):
        for bx in range(wb):
            blk = blocks[by, bx]
            c0, c1, bits = struct.unpack('<HHI', blk[:8])
            cols = [dxt_colors(c0), dxt_colors(c1)]
            if c0 > c1:
                cols.append(((2 * cols[0] + cols[1]) // 3)); cols.append(((cols[0] + 2 * cols[1]) // 3))
            else:
                cols.append(((cols[0] + cols[1]) // 2)); cols.append(np.array([0, 0, 0]))
            cols = np.array(cols)
            for py in range(4):
                for px in range(4):
                    idx = (bits >> (2 * (py * 4 + px))) & 3
                    col = cols[idx]
                    img[by * 4 + py, bx * 4 + px, :3] = col
                    if not (c0 > c1) and idx == 3: img[by * 4 + py, bx * 4 + px, 3] = 0
    return img

def decode_dxt5(blocks):
    hb, wb = blocks.shape[:2]
    img = np.zeros((hb * 4, wb * 4, 4), dtype=np.uint8)
    for by in range(hb):
        for bx in range(wb):
            blk = blocks[by, bx]
            a0, a1 = blk[0], blk[1]
            abits = int.from_bytes(blk[2:8], 'little')
            alphas = [a0, a1]
            if a0 > a1: alphas += [ ( (7 - i) * a0 + i * a1 ) // 7 for i in range(1, 7)]
            else:
                alphas += [((5 - i) * a0 + i * a1) // 5 for i in range(1, 5)] + [0, 255]
            c0, c1, bits = struct.unpack('<HHI', blk[8:16])
            cols = [dxt_colors(c0), dxt_colors(c1)]
            cols.append(((2 * cols[0] + cols[1]) // 3)); cols.append(((cols[0] + 2 * cols[1]) // 3))
            cols = np.array(cols)
            for py in range(4):
                for px in range(4):
                    n = py * 4 + px
                    idx = (bits >> (2 * n)) & 3
                    img[by * 4 + py, bx * 4 + px, :3] = cols[idx]
                    img[by * 4 + py, bx * 4 + px, 3] = alphas[(abits >> (3 * n)) & 7]
    return img

def swap16(b):
    a = np.frombuffer(b, dtype=np.uint8).reshape(-1, 2)
    return a[:, ::-1].tobytes()

def block_coherence(blocks):
    """Mean endpoint-color distance between horizontally adjacent blocks (lower=more image-like)."""
    hb, wb = blocks.shape[:2]
    if wb < 2: return 1e9
    c0 = blocks[:, :-1].reshape(-1, blocks.shape[2]).astype(np.int32)
    c1 = blocks[:, 1:].reshape(-1, blocks.shape[2]).astype(np.int32)
    # first two bytes of each block = color0 (LE after swap)
    e0 = (c0[:, 0] | (c0[:, 1] << 8)); e1 = (c1[:, 0] | (c1[:, 1] << 8))
    d0 = np.stack([ (e0 >> 11) & 31, (e0 >> 5) & 63, e0 & 31], axis=1).astype(np.float64)
    d1 = np.stack([ (e1 >> 11) & 31, (e1 >> 5) & 63, e1 & 31], axis=1).astype(np.float64)
    return float(np.abs(d0 - d1).mean())

if __name__ == '__main__':
    d = open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone_pkg00_window.bin', 'rb').read()
    # tex2: desc idx 2 (DXT1 fmt18, base_pg 8, size 32x32 blocks, pitch field 4)
    # try every 0x1000-aligned candidate base; untile pitch candidates; score.
    wb, hb, bpb = 32, 32, 8
    size = 32 * 32 * bpb  # storage pitch 32 -> 8192; pitch 128 storage -> 32768
    results = []
    for pitch_b in (32, 128):
        need = pitch_b * 32 * bpb
        for off in range(0, len(d) - need, 0x1000):
            raw = swap16(d[off:off + need])
            blocks = untile(raw, wb, hb, pitch_b, bpb)
            sc = block_coherence(blocks)
            results.append((sc, off, pitch_b))
    results.sort()
    for r in results[:10]: print('score %.3f off %#x pitch %d' % r)
