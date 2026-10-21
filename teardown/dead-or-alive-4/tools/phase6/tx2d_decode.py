"""DOA4 TX2D full decode for one package window.
Descriptor = X360 texture fetch constant at desc words 7,8,9 (Xenia
xe_gpu_texture_fetch_t, BSD): dword0 tiled(bit31)+pitch[30:22]<<5 (pixels),
dword1 format[5:0] (18=DXT1, 20=DXT4_5, 6=8_8_8_8) + endian[7:6] +
base_address[31:12] (4K pages, image space), dword2 size_2d (pixels, minus-1).
Pool file base = xp + align_up(xpr2_header_f1, 0x1000); tex file offset =
pool base + base_address. Data is X360-tiled (Xenia Tiled2D port) with
16-bit endian swap for DXT formats.
"""
import numpy as np, struct, sys, os
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from tx2d_try import untile, swap16
from tx2d_fast import decode_dxt1_fast

def decode_dxt5_fast(blocks):
    hb, wb = blocks.shape[:2]
    a0 = blocks[..., 0].astype(np.float32); a1 = blocks[..., 1].astype(np.float32)
    abits = np.zeros((hb, wb), dtype=np.uint64)
    for i in range(6): abits |= blocks[..., 2 + i].astype(np.uint64) << (8 * i)
    b = blocks.astype(np.uint16)
    c0 = b[..., 8] | (b[..., 9] << 8); c1 = b[..., 10] | (b[..., 11] << 8)
    bits = (blocks[..., 12].astype(np.uint32) | (blocks[..., 13].astype(np.uint32) << 8) |
            (blocks[..., 14].astype(np.uint32) << 16) | (blocks[..., 15].astype(np.uint32) << 24))
    def rgb(c):
        r = ((c >> 11) & 31).astype(np.float32) * 255 / 31
        g = ((c >> 5) & 63).astype(np.float32) * 255 / 63
        bl = (c & 31).astype(np.float32) * 255 / 31
        return np.stack([r, g, bl], axis=-1)
    C0, C1 = rgb(c0), rgb(c1)
    pal = np.stack([C0, C1, (2 * C0 + C1) / 3, (C0 + 2 * C1) / 3], axis=-2)
    alphas = np.zeros((hb, wb, 8), dtype=np.float32)
    alphas[..., 0] = a0; alphas[..., 1] = a1
    gt = a0 > a1
    for i in range(1, 7):
        alphas[..., 1 + i] = np.where(gt, ((7 - i) * a0 + i * a1) / 7, ((5 - i) * a0 + i * a1) / 5 if i <= 4 else (0 if i == 5 else 255))
    px = np.zeros((hb, wb, 4, 4, 4), dtype=np.float32)
    for n in range(16):
        py, pxx = n // 4, n % 4
        sel = ((bits >> (2 * n)) & 3)
        asel = ((abits >> (3 * n)) & 7).astype(int)
        px[:, :, py, pxx, :3] = pal[np.arange(hb)[:, None], np.arange(wb)[None, :], sel]
        px[:, :, py, pxx, 3] = alphas[np.arange(hb)[:, None], np.arange(wb)[None, :], asel]
    return px.transpose(0, 2, 1, 3, 4).reshape(hb * 4, wb * 4, 4).astype(np.uint8)

def parse_tx2d(d, xp):
    def u32(o): return struct.unpack('>I', d[o:o + 4])[0]
    hdr_f1 = u32(xp + 4)
    recs = []; pos = xp
    while pos < len(d) - 16:
        m = d[pos:pos + 4]
        if m in (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF'):
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16]); recs.append((m.decode(), f1, f2, f3)); pos += 16
        elif m == b'\x00' * 4: pos += 16
        else: break
    pool = xp + ((hdr_f1 + 0xFFF) & ~0xFFF)
    out = []
    for (m, f1, f2, f3) in recs:
        if m != 'TX2D': continue
        w = struct.unpack('>10I', d[xp + f1:xp + f1 + 40])
        dw0, dw1, dw2 = w[7], w[8], w[9]
        fmt = dw1 & 0x3F; endian = (dw1 >> 6) & 3; base = (dw1 >> 12) << 12
        pitch_px = ((dw0 >> 22) & 0x1FF) << 5; tiled = dw0 >> 31
        wp = (dw2 & 0x1FFF) + 1; hp = ((dw2 >> 13) & 0x1FFF) + 1
        out.append(dict(fmt=fmt, endian=endian, base=base, pitch_px=pitch_px, tiled=tiled, w=wp, h=hp, pool=pool))
    return out

def decode_tex(d, t):
    fmt, wp, hp = t['fmt'], t['w'], t['h']
    off = t['pool'] + t['base']
    if fmt == 18:  # DXT1
        wb, hb = max(wp // 4, 1), max(hp // 4, 1)
        pitch_b = max(t['pitch_px'] // 4, wb)
        need = pitch_b * max(hb, 32) * 8
        raw = swap16(d[off:off + need]) if t['endian'] == 1 else d[off:off + need]
        blocks = untile(raw, wb, hb, pitch_b, 8) if t['tiled'] else np.frombuffer(raw, dtype=np.uint8).reshape(hb, wb, 8)
        img = decode_dxt1_fast(blocks)
        return np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
    if fmt == 20:  # DXT5
        wb, hb = max(wp // 4, 1), max(hp // 4, 1)
        pitch_b = max(t['pitch_px'] // 4, wb)
        need = pitch_b * max(hb, 32) * 16
        raw = swap16(d[off:off + need]) if t['endian'] == 1 else d[off:off + need]
        blocks = untile(raw, wb, hb, pitch_b, 16) if t['tiled'] else np.frombuffer(raw, dtype=np.uint8).reshape(hb, wb, 16)
        return decode_dxt5_fast(blocks)
    if fmt == 6:  # 8_8_8_8, size/pitch in pixels, 4B/px, tiled at pixel granularity
        pitch_px = max(t['pitch_px'], wp)
        need = pitch_px * max(hp, 32) * 4
        raw = d[off:off + need]
        if t['endian'] == 2:  # 8in32: reverse bytes within each dword
            raw = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4)[:, ::-1].tobytes()
        if t['tiled']:
            px = untile(raw, wp, hp, pitch_px, 4)
            return px[:, :, [2, 1, 0, 3]].copy()
        a = np.frombuffer(raw, dtype=np.uint8).reshape(max(hp, 32), pitch_px, 4)[:hp, :wp]
        return a[:, :, [2, 1, 0, 3]].copy()
    raise ValueError(f'fmt {fmt} not handled')

if __name__ == '__main__':
    from PIL import Image
    winf, xp, outdir = sys.argv[1], int(sys.argv[2], 16), sys.argv[3]
    d = open(winf, 'rb').read()
    os.makedirs(outdir, exist_ok=True)
    texs = parse_tx2d(d, xp)
    print('pool base', hex(texs[0]['pool']) if texs else None, 'textures', len(texs))
    for i, t in enumerate(texs):
        try:
            img = decode_tex(d, t)
            Image.fromarray(img).save(os.path.join(outdir, f'tex{i:02d}_f{t["fmt"]}_{t["w"]}x{t["h"]}.png'))
            print(i, 'fmt', t['fmt'], t['w'], 'x', t['h'], 'base', hex(t['base']), 'OK')
        except Exception as e:
            print(i, 'fmt', t['fmt'], t['w'], 'x', t['h'], 'base', hex(t['base']), 'FAIL', e)
