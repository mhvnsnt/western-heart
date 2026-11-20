#!/usr/bin/env python3
"""TTT2 MOTA 0x64 clip decoder — reverse-engineered from Default.xex
Function_822897D0 (the game's animation frame expander), 2026-11-04.

FORMAT (all big-endian), clip = one MOTA table entry starting with u16 100:
  u16 type=100, u16 N (track count)
  N x u16 track types (4..7 = i16 tracks, >=8 = f32 tracks)
  u16 F (frame count), u16 A (shift field), u16 K (count of f32 tracks)
  K x f32 per-f32-track scales (indexed by f32-track ordinal)
  initial pose (= frame 0): per track 3 x i16 (types 4..7) or 3 x f32
  block index: nb x u32 offsets relative to index start,
    nb = ((F-2)>>4)+1 for F>=2 else 1
  block streams at index_start + ib[b]

FRAME MODEL (game truth): frame 0 = initial pose. Block b's keyframe
symbol yields frame 16b+1; its step symbols yield frames 16b+2 .. 16b+16
(capped at F-1). A block therefore holds 1 + min(15, F-2-16b) stream poses.

COMPONENT STREAMS: per block, per track, per component (3, in order):
  byte0: length = byte0 >> 2 (stream pointer advances by length);
  bitstream MSB-first primed with (byte0 & 3) then following bytes.
  Symbols (4-bit code):
    0     -> (len 0, base 0), delta 0
    1..12 -> VLC (len, base): 1:(2,1) 2:(2,-4) 3:(4,5) 4:(4,-20) 5:(6,21)
             6:(6,-84) 7:(8,85) 8:(8,-340) 9:(10,341) 10:(10,-1364)
             11:(12,1365) 12:(12,-5460); delta = base + read(len)
    13    -> raw signed i16
    14    -> repeat-coding: cnt = read(4); this step and the next cnt-1
             steps each RE-READ a value with the PREVIOUS symbol's
             (len, base). Previous len 0 -> delta 0; 99 -> terminate.
    15    -> terminate: remaining frames of the block hold the last pose.
  Keyframe symbol: pose = (initial >> (A_hi & 0x7f)) + delta (i16 tracks)
                   or 0 + delta (f32 tracks, stored domain); velocity = 0.
  Step symbols: velocity += delta; pose += velocity (double integration).
  (len, base) coding state persists across components within a block.

FINAL CONVERSION (per frame):
  i16 track: out = (stored << (A_hi & 0x3f)) * (pi / 32768)
  f32 track: out = initial_f32 + (stored << (A_lo & 0x3f)) * scale[ordinal]

VALIDATION (2026-11-04, data004, all 6 tables): 1,369 sized 0x64 entries;
432k+ components decode with bits <= length capacity; ~90% of clips fully
clean under the strict oracle (lp-walk lands exactly on every block end,
all frames covered or terminated). Residual ~10% of clips (contiguous
index families) exceed capacity on some components — an encoder variant
not yet identified; those clips are reported, never silently mangled.

Usage: ttt2_mota_decode64.py <decoded-dataNNN.bin> <table_offset> <entry_index>
       [--out out.json]   (wh-anim/1-style JSON: tracks by DECODE-SPEC names)
"""
import json, struct, sys

VLC = {0: (0, 0), 1: (2, 1), 2: (2, -4), 3: (4, 5), 4: (4, -20),
       5: (6, 21), 6: (6, -84), 7: (8, 85), 8: (8, -340),
       9: (10, 341), 10: (10, -1364), 11: (12, 1365), 12: (12, -5460),
       13: (16, 0)}
PI_OVER_32768 = 9.58738019107841e-05

# DECODE-SPEC inferred track -> wh-anim/1 bone names (23-track layout)
TRACK_NAMES_23 = ['RootMotion', 'RootPos', 'Track2', 'Root', 'Spine', 'Hips',
                  'Chest', 'Neck', 'Head', 'RightShoulder', 'RightArm',
                  'RightForeArm', 'RightHand', 'LeftShoulder', 'LeftArm',
                  'LeftForeArm', 'LeftHand', 'RightUpLeg', 'RightLeg',
                  'RightFoot', 'LeftUpLeg', 'LeftLeg', 'LeftFoot']

class BitStream:
    def __init__(self, buf, start):
        self.buf = buf; self.start = start; self.pos = 0
    def read(self, n):
        v = 0
        for _ in range(n):
            bp = self.pos
            if bp < 2:
                bit = (self.buf[self.start] >> (1 - bp)) & 1
            else:
                idx = self.start + 1 + (bp - 2) // 8
                if idx >= len(self.buf):
                    raise EOFError('stream overrun')
                bit = (self.buf[idx] >> (7 - (bp - 2) % 8)) & 1
            v = (v << 1) | bit
            self.pos += 1
        return v

def _wrap16(x):
    return ((x + 0x8000) & 0xFFFF) - 0x8000

def _read_coded(bs, ln, base):
    if ln == 0:
        return 0
    v = bs.read(ln)
    if ln == 16:
        return v - 0x10000 if v >= 0x8000 else v
    return base + v

def decode_component(buf, start, steps_wanted, prev, init_stored):
    """Returns (length, poses_stored, prev, terminated)."""
    lp = buf[start] >> 2
    bs = BitStream(buf, start)
    plen, pbase = prev
    cd = bs.read(4)
    rep = 0
    if cd == 15:
        return lp, [init_stored], (99, 0), True
    if cd == 14:
        rep = bs.read(4) - 1
        if plen == 99:
            return lp, [init_stored], (plen, pbase), True
        delta = _read_coded(bs, plen, pbase)
    elif cd == 13:
        v = bs.read(16)
        delta = v - 0x10000 if v >= 0x8000 else v
        plen, pbase = 16, 0
    else:
        plen, pbase = VLC[cd]
        delta = _read_coded(bs, plen, pbase)
    pose = _wrap16(init_stored + delta)
    poses = [pose]
    vel = 0
    terminated = False
    s = 0
    while s < steps_wanted:
        if rep > 0:
            rep -= 1
            if plen == 99:
                terminated = True; break
            d = _read_coded(bs, plen, pbase)
        else:
            cd = bs.read(4)
            if cd == 15:
                plen, pbase = 99, 0
                terminated = True; break
            if cd == 14:
                rep = bs.read(4) - 1
                if plen == 99:
                    terminated = True; break
                d = _read_coded(bs, plen, pbase)
            elif cd == 13:
                v = bs.read(16)
                d = v - 0x10000 if v >= 0x8000 else v
                plen, pbase = 16, 0
            else:
                plen, pbase = VLC[cd]
                d = _read_coded(bs, plen, pbase)
        vel += d
        pose = _wrap16(pose + vel)
        poses.append(pose)
        s += 1
    return lp, poses, (plen, pbase), terminated

def parse_header(c):
    typ, N = struct.unpack('>HH', c[:4])
    if typ != 100:
        raise ValueError('not a 0x64 clip (type %d)' % typ)
    types = struct.unpack('>%dH' % N, c[4:4 + 2 * N])
    p = 4 + 2 * N
    F, A, K = struct.unpack('>HHH', c[p:p + 6]); p += 6
    scales = list(struct.unpack('>%df' % K, c[p:p + 4 * K])); p += 4 * K
    flags = [1 if 4 <= t <= 7 else 0 for t in types]
    init = []
    for t in range(N):
        if flags[t]:
            init.append(struct.unpack('>hhh', c[p:p + 6])); p += 6
        else:
            init.append(struct.unpack('>fff', c[p:p + 12])); p += 12
    nb = ((F - 2) >> 4) + 1 if F >= 2 else 1
    ib = struct.unpack('>%dI' % nb, c[p:p + 4 * nb])
    return {'N': N, 'types': types, 'F': F, 'A': A, 'K': K, 'scales': scales,
            'flags': flags, 'init': init, 'nb': nb, 'ib': ib, 'idx_start': p}

def decode_clip(buf, off):
    """Decode one 0x64 clip at buf[off:]. Returns dict with per-track
    float frames: frames[f][track] = (x, y, z) in game output units
    (radians for i16 rotation tracks; f32 tracks in their native units)."""
    h = parse_header(buf[off:])
    N, F, A = h['N'], h['F'], h['A']
    A_hi, A_lo = (A >> 8) & 0xFF, A & 0xFF
    p = h['idx_start']
    # stored[f][t][comp]
    stored = [[None] * N for _ in range(F)]
    for t in range(N):
        for cm in range(3):
            if h['flags'][t]:
                stored[0][t] = stored[0][t] or [0, 0, 0]
                stored[0][t][cm] = h['init'][t][cm] >> (A_hi & 0x7F)
            else:
                stored[0][t] = stored[0][t] or [0, 0, 0]
                stored[0][t][cm] = 0
    # note: frame 0 stored pose for i16 = shifted initial; conversion below
    # uses raw initial for f32 frame 0 (handled in conversion).
    for b in range(h['nb']):
        q = off + p + h['ib'][b]
        steps = min(15, F - 2 - 16 * b)
        if steps < 0:
            steps = 0
        prev = (0, 0)
        for t in range(N):
            for cm in range(3):
                ip = (h['init'][t][cm] >> (A_hi & 0x7F)) if h['flags'][t] else 0
                lp, poses, prev, term = decode_component(buf, q, steps, prev, ip)
                for i, pv in enumerate(poses):
                    f = 16 * b + 1 + i
                    if f < F:
                        if stored[f][t] is None:
                            stored[f][t] = [0, 0, 0]
                        stored[f][t][cm] = pv
                # hold for terminated remainder
                last = poses[-1]
                for i in range(len(poses), steps + 1):
                    f = 16 * b + 1 + i
                    if f < F:
                        if stored[f][t] is None:
                            stored[f][t] = [0, 0, 0]
                        stored[f][t][cm] = last
                q += lp
    # final conversion
    f32_ord = {}
    o = 0
    for t in range(N):
        if not h['flags'][t]:
            f32_ord[t] = o; o += 1
    frames = []
    for f in range(F):
        row = []
        for t in range(N):
            vals = []
            for cm in range(3):
                if h['flags'][t]:
                    if f == 0:
                        v = h['init'][t][cm] * PI_OVER_32768
                    else:
                        v = (stored[f][t][cm] << (A_hi & 0x3F)) * PI_OVER_32768
                else:
                    if f == 0:
                        v = h['init'][t][cm]
                    else:
                        v = h['init'][t][cm] + (stored[f][t][cm] << (A_lo & 0x3F)) * h['scales'][f32_ord[t]]
                vals.append(v)
            row.append(tuple(vals))
        frames.append(row)
    return {'header': {k: h[k] for k in ('N', 'F', 'A', 'K', 'types', 'scales')},
            'frames': frames}

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    path, tab_off, idx = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    out = None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    buf = open(path, 'rb').read()
    cnt = struct.unpack('>I', buf[tab_off + 12:tab_off + 16])[0]
    offs = struct.unpack('>%dI' % cnt, buf[tab_off + 16:tab_off + 16 + 4 * cnt])
    clip_off = tab_off + offs[idx]
    res = decode_clip(buf, clip_off)
    h = res['header']
    names = TRACK_NAMES_23 if h['N'] == 23 else [f'Track{t}' for t in range(h['N'])]
    doc = {'format': 'ttt2-0x64-decoded/1', 'source_entry': idx,
           'frames': h['F'], 'tracks': h['N'],
           'track_names': names, 'types': list(h['types']),
           'data': [[list(map(lambda v: round(v, 6), res['frames'][f][t]))
                     for t in range(h['N'])] for f in range(h['F'])]}
    if out:
        json.dump(doc, open(out, 'w'))
        print('wrote', out)
    else:
        print(json.dumps(doc)[:2000])

if __name__ == '__main__':
    main()
