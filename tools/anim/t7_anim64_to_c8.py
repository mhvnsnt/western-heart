#!/usr/bin/env python3
"""tools/anim/t7_anim64_to_c8.py — turn Tekken 7 0x64 (compressed) clips into 0xC8-convention values, through the
game's OWN sampler, so every 0x64 attack can use the proven 0xC8 bake path (Kiloutre's applier on the mannequin).

Why: every T7 attack is 0x64 (King: 422 of his 23-bone attack clips) and the community had no 0x64 -> pose path
(docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md). Read from TekkenGame-Win64-Shipping.exe (2026-11-01):
  * 0x64 rotation bones are AXIS-ANGLE: axis = R_y(Y) R_x(X) (0,0,1), q = (axis sin(Z/2), cos(Z/2));
  * 0xC8 rotation bones are Euler: q = q_X(-X) q_Y(-Y) q_Z(-Z) (fitted on the game's sampler to 7e-8);
  * both formats land in the same bone space: King's 0xC8 stance vs the first frame of 120 of his 0x64 attacks
    agree per bone within the attacks' own spread (forearms 2-4 deg, neck 6, knees 4-12).
This tool samples each 0x64 clip with the game's sampler (tools/anim/exe_re/emulate_sampler.py, Unicorn; frame t =
0..length-1, frame 0 = the base pose: the community decoder differs from the game on frame 1 only), then writes each
rotation as the 0xC8 Euler triple that rebuilds the same quaternion, and each position bone as (x, y, z).

    python3 -I tools/anim/t7_anim64_to_c8.py EXE ARC --check 8      # round-trip 8 clips through the 0xC8 path
    library: frames = convert(arc_path, clip_index, exe)            # [[69 floats] per frame], like decode_c8
The exe stays private (GRE release t7-shipping-exe-20261031); never commit it or anything copied out of it.
"""
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'exe_re'))
import numpy as np  # noqa: E402

_SAMPLERS = {}


def sampler(exe):
    if exe not in _SAMPLERS:
        import emulate_sampler as E
        _SAMPLERS[exe] = E.Sampler(exe)
    return _SAMPLERS[exe]


def quat_to_mat(q):
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def c8_euler(q):
    """(X, Y, Z) with q = q_X(-X) q_Y(-Y) q_Z(-Z), i.e. R = Rx(a) Ry(b) Rz(c) with a, b, c = -X, -Y, -Z."""
    R = quat_to_mat(np.asarray(q, dtype=np.float64))
    b = math.asin(max(-1.0, min(1.0, R[0, 2])))
    a = math.atan2(-R[1, 2], R[2, 2])
    c = math.atan2(-R[0, 1], R[0, 0])
    return (-a, -b, -c)


def clip_offsets(data):
    from t7_anim64 import mota_anims
    m = re.search(b'MOTA', data).start()
    return [m + o for o in mota_anims(data, m)]


def convert_bytes(data, o, exe, nbones=23):
    """0x64 clip at offset o -> (frames, desc): frames = [[3*nbones floats]], 0xC8 value convention."""
    import emulate_sampler as E
    from t7_anim64 import Anim64
    t = data[o + 1] if data[o] == 0 else data[o]
    if t != 0x64:
        raise ValueError('clip at %#x is format %#x, not 0x64' % (o, t))
    a = Anim64(data, o)
    le = E.anim64_to_le(data, o)
    S = sampler(exe)
    frames = []
    for fr in range(a.length):
        q, _ = S.sample(le, float(fr))
        vals = []
        for j, d in enumerate(a.desc[:nbones]):
            vals.extend(c8_euler(q[j]) if 4 <= d <= 7 else (float(q[j][0]), float(q[j][1]), float(q[j][2])))
        frames.append(vals)
    return frames, list(a.desc)


def convert(arc, idx, exe, nbones=23):
    data = open(arc, 'rb').read()
    return convert_bytes(data, clip_offsets(data)[idx], exe, nbones)[0]


def check(exe, arc, n):
    """Round trip: 0x64 clip -> 0xC8 values -> the game's 0xC8 sampler -> same quaternions as the game's 0x64 sampler."""
    import emulate_sampler as E
    data = open(arc, 'rb').read()
    S = sampler(exe)
    done, worst = 0, 0.0
    for o in sorted(set(clip_offsets(data))):
        t = data[o + 1] if data[o] == 0 else data[o]
        if t != 0x64:
            continue
        frames, desc = convert_bytes(data, o, exe, nbones=10_000)
        nb = len(desc)
        c8 = E.c8_clip(np.array(frames, dtype=np.float64).reshape(len(frames), nb, 3), desc)
        le = E.anim64_to_le(data, o)
        err = 0.0
        for fr in range(0, len(frames), max(1, len(frames) // 6)):
            q64, _ = S.sample(le, float(fr))
            qc8, _ = S.sample(bytes(c8), float(fr))
            for j, d in enumerate(desc):
                if 4 <= d <= 7:
                    err = max(err, min(np.abs(q64[j] - qc8[j]).max(), np.abs(q64[j] + qc8[j]).max()))
                else:
                    err = max(err, np.abs(q64[j][:3] - qc8[j][:3]).max() / (1 + np.abs(q64[j][:3]).max()))
        print('clip @%#x: %d bones, %d frames, round-trip max error %.2e' % (o, nb, len(frames), err))
        worst = max(worst, err)
        done += 1
        if done >= n:
            break
    print('worst %.2e over %d clips' % (worst, done))
    return worst


if __name__ == '__main__':
    if len(sys.argv) >= 5 and sys.argv[3] == '--check':
        sys.exit(0 if check(sys.argv[1], sys.argv[2], int(sys.argv[4])) < 1e-4 else 1)
    print(__doc__)
