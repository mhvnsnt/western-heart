#!/usr/bin/env python3
"""AKI N64 raw animation file -> .npy bank clip (26 joints x 3 channels).

Encoding reverse-engineered 2026-11-21 by comparing the VPW2 ROM's raw
anim file 0x27E8 against the wh-jp-clone teardown's anim_27E8.npy
(byte-exact on all 22 frames; also validated on 1A90/27E9/2056 +
a random bank sample). Frame layout per Marty Monero's AKI move-format
doc (header 4B, frame 98B, 19 bones): 19 BE u32 rotation words, each
followed by a translation block iff bit31 set (bit30=1 -> 3B relative
= 3x u8; bit30=0 -> 4B absolute = X 12-bit signed, Y 8-bit, Z 12-bit
signed). 76 + 4 + 6*3 = 98.

Rotation word -> [s12(bits31-20), u10(bits19-10), s10(bits9-0)].
(The converter masks ch0/ch2 to 10 bits, discarding the flag bits
that ride in ch0's top 2 bits; ch2's sign is undone by the same mask.)

File (pose-loop) order -> npy row:
  pelvis 0, lower_ab 2, upper_body 4, neck 6, head 7,
  lower_left_leg 8, upper_left_leg 9, left_foot 11, left_hand 12,
  left_fingers 13, lower_left_arm 14, upper_left_arm 15,
  lower_right_leg 17, upper_right_leg 18, right_foot 20,
  lower_right_arm 21, right_hand 22, right_fingers 23,
  upper_right_arm 24.
Translation blocks (by the word they follow):
  pelvis -> 1 OverallMovement, lower_ab -> 3, upper_body -> 5,
  upper_left_leg -> 10 LeftLegMovement, upper_left_arm -> 16,
  upper_right_leg -> 19, upper_right_arm -> 25.
"""
import struct
import numpy as np

FILE_TO_NPY = [0, 2, 4, 6, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 20, 21,
               22, 23, 24]
TRANS_TO_NPY = {0: 1, 1: 3, 2: 5, 6: 10, 11: 16, 13: 19, 18: 25}


def _s12(v):
    return v - 0x1000 if v & 0x800 else v


def _s10(v):
    return v - 0x400 if v & 0x200 else v


def decode_frame(f):
    """One 98-byte frame -> (26, 3) int16 array."""
    assert len(f) == 98, f'frame len {len(f)} != 98'
    out = np.zeros((26, 3), dtype=np.int16)
    off = 0
    for wi in range(19):
        w = struct.unpack('>I', f[off:off + 4])[0]
        off += 4
        row = FILE_TO_NPY[wi]
        out[row, 0] = _s12((w >> 20) & 0xFFF)
        out[row, 1] = (w >> 10) & 0x3FF
        out[row, 2] = _s10(w & 0x3FF)
        if w & 0x80000000:
            trow = TRANS_TO_NPY.get(wi)
            if w & 0x40000000:  # relative: 3 x u8
                b = f[off:off + 3]
                off += 3
                if trow is not None:
                    out[trow] = [b[0], b[1], b[2]]
            else:  # absolute: X s12, Y u8, Z s12
                aw = struct.unpack('>I', f[off:off + 4])[0]
                off += 4
                if trow is not None:
                    out[trow, 0] = _s12((aw >> 20) & 0xFFF)
                    out[trow, 1] = (aw >> 12) & 0xFF
                    out[trow, 2] = _s12(aw & 0xFFF)
    assert off == 98, f'frame walk ended at {off}, not 98'
    return out


def decode_anim(data):
    """Raw anim file bytes (4B header + 98B frames) -> (nframes, 26, 3).

    Trailing all-zero frames are padding, not motion: the header
    duration (bytes 2-3, half frames) gives the true count as
    (dur >> 1) + 1 (Monero). WM2K 0x2667 'Sliding attack' carries 2
    zero padding frames past its 13-frame duration; without the
    truncation the zero frames fail the walk (no translation flags).
    Truncation applies ONLY when the frames past the duration count
    are all zero."""
    assert len(data) >= 4 and (len(data) - 4) % 98 == 0, \
        f'bad anim len {len(data)}'
    n = (len(data) - 4) // 98
    dur = struct.unpack('>H', data[2:4])[0]
    n_dur = (dur >> 1) + 1
    if 0 < n_dur < n:
        tail = data[4 + n_dur * 98:]
        if tail == bytes(len(tail)):
            n = n_dur
    frames = [decode_frame(data[4 + i * 98: 4 + (i + 1) * 98])
              for i in range(n)]
    return np.stack(frames).astype(np.int16)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/hatch/workspace/bannon-tier0-moves/aki-n64-five')
    from aki_extract import AKIRom
    rom = AKIRom('vpw2', '/home/hatch/workspace/vpw2-hidden25-renders/'
                 'Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64')
    bank = '/home/hatch/workspace/koc2-vpw2-moveside/anim-side-by-side/' \
           'work/bank/clips'
    import random
    fids = ['27E8', '1A90', '27E9', '2056', '2317', '245A', '2E26']
    allf = [f[5:9] for f in __import__('os').listdir(bank)]
    random.seed(7)
    fids += random.sample(allf, 30)
    bad = 0
    for fid in fids:
        mine = decode_anim(rom.get(int(fid, 16)))
        ref = np.load(f'{bank}/anim_{fid}.npy')
        ok = mine.shape == ref.shape and bool(np.array_equal(mine, ref))
        if not ok:
            bad += 1
            d = np.abs(mine.astype(int) - ref.astype(int))
            print(f'{fid}: MISMATCH shape {mine.shape} vs {ref.shape} '
                  f'maxdiff {d.max()} ndiff {(d > 0).sum()}')
        else:
            print(f'{fid}: EXACT ({mine.shape[0]}f)')
    print('bad:', bad, 'of', len(fids))
