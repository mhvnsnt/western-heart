import numpy as np, struct

def decode_dxt1_fast(blocks):
    """blocks: (hb, wb, 8) uint8 -> (hb*4, wb*4, 3) uint8, vectorized."""
    hb, wb = blocks.shape[:2]
    b = blocks.astype(np.uint16)
    c0 = b[..., 0] | (b[..., 1] << 8)
    c1 = b[..., 2] | (b[..., 3] << 8)
    bits = (blocks[..., 4].astype(np.uint32) | (blocks[..., 5].astype(np.uint32) << 8) |
            (blocks[..., 6].astype(np.uint32) << 16) | (blocks[..., 7].astype(np.uint32) << 24))
    def rgb(c):
        r = ((c >> 11) & 31).astype(np.float32) * 255 / 31
        g = ((c >> 5) & 63).astype(np.float32) * 255 / 63
        bl = (c & 31).astype(np.float32) * 255 / 31
        return np.stack([r, g, bl], axis=-1)
    C0, C1 = rgb(c0), rgb(c1)
    gt = (c0 > c1)[..., None]
    C2 = np.where(gt, (2 * C0 + C1) / 3, (C0 + C1) / 2)
    C3 = np.where(gt, (C0 + 2 * C1) / 3, 0.0)
    pal = np.stack([C0, C1, C2, C3], axis=-2)  # hb,wb,4,3
    idx = ((bits[..., None] >> (2 * np.arange(16))) & 3).reshape(hb, wb, 4, 4)
    px = np.zeros((hb, wb, 4, 4, 3), dtype=np.float32)
    for n in range(16):
        py, pxx = n // 4, n % 4
        sel = (idx[:, :, py, pxx])
        px[:, :, py, pxx] = pal[np.arange(hb)[:, None], np.arange(wb)[None, :], sel]
    return px.transpose(0, 2, 1, 3, 4).reshape(hb * 4, wb * 4, 3).astype(np.uint8)

def boundary_score(img):
    """Mean pixel discontinuity across block boundaries vs within (lower ratio = coherent layout)."""
    img = img.astype(np.float32)
    hb = img.shape[0] // 4; wb = img.shape[1] // 4
    dx = np.abs(np.diff(img, axis=1)).mean(axis=(0, 2))
    dy = np.abs(np.diff(img, axis=0)).mean(axis=(1, 2))
    bx = dx[[4 * k - 1 for k in range(1, wb)]].mean() if wb > 1 else 0
    by = dy[[4 * k - 1 for k in range(1, hb)]].mean() if hb > 1 else 0
    ix = np.delete(dx, [4 * k - 1 for k in range(1, wb)]).mean()
    iy = np.delete(dy, [4 * k - 1 for k in range(1, hb)]).mean()
    return float((bx + by) / max(ix + iy, 1e-6)), float(bx + by)
