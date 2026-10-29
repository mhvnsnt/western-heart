#!/usr/bin/env python3
"""No Mercy animation keyframe bank extractor.

Source: WWF No Mercy (USA) (Rev-A).z64
Animations live in the ROM FileTable (ROM 0x16C31D8, 19459 entries of
u32 BE: (location & 0xFFFFFFFE) | encoded-bit; FirstFile = 0x1BD150).
GAME-EXACT (W3c, 2026-10-21): proven from the game's own decompiled code
(FUN_80003ab0 loads the table from ROM 0x16C31D8 and computes addresses
as (entry & ~1) + 0x1BD150; FUN_80003bd0 treats file IDs as 1-BASED,
valid 1..0x4C02, table index = fid-1) and corroborated by VPWStudio
DefaultGameData.cs NoMercy_NTSC_U_11. The previous constants
(0x16C3238 / 0x1BD1B0, 0-based) were the NTSC_U_10 pairing and read
game file fid+0x19 spliced at +0x60 — see
docs/anim/AKI-BAKE-ROCK-2026-10-21.md (W3b addendum, Finding 1).
  FirstAnimationFileID = 0x2DD9, FirstMoveAnimationID = 0x3322
  (per AKI-Club/VPWStudio DefaultGameData.cs).
AkiAnimation format (per VPWStudio AkiAnimation.cs):
  4 bytes Toki2, then N x 0x62 (98)-byte frames.
  Each frame = 20x PivotRotation (4B: [PivotX s12][Rotation u10]
  [PivotZ s10] — W3b Finding 2: the 12/8/12 split was wrong; on the
  stance control clip only 12/10/10 makes every channel smooth) +
  6x MovementXYZ (3B), in fixed order:
  Pelvis, OverallMovement, LowerAb, LowerAbMovement, UpperBody,
  UpperBodyMovement, Neck, Head, LowerLeftLeg, UpperLeftLeg,
  LeftLegMovement, LeftFoot, LeftHand, LeftFingers, LowerLeftArm,
  UpperLeftArm, LeftArmMovement, LowerRightLeg, UpperRightLeg,
  RightLegMovement, RightFoot, LowerRightArm, RightHand, RightFingers,
  UpperRightArm, RightArmMovement.
Move linkage (VPWStudio MenuItems_Moves.cs): move menu entries carry
AnimID = animation file ID - 0x3322 ("animation ID (-3322)").

Usage:
  anim_extract.py info <fileid>        # print toki2 + frame count
  anim_extract.py json <fileid> <out>  # dump decoded frames to JSON
  anim_extract.py survey               # frame-count histogram 0x2DD9..0x3360
"""
import json, struct, sys, os

ROM = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'WWF No Mercy (USA) (Rev-A).z64')
FT = 0x16C31D8
FIRST = 0x1BD150
FIRST_ANIM = 0x2DD9
FIRST_MOVE_ANIM = 0x3322

ORDER = [
    ("Pelvis", "PR"), ("OverallMovement", "OM"), ("LowerAb", "PR"),
    ("LowerAbMovement", "MV"), ("UpperBody", "PR"), ("UpperBodyMovement", "MV"),
    ("Neck", "PR"), ("Head", "PR"), ("LowerLeftLeg", "PR"), ("UpperLeftLeg", "PR"),
    ("LeftLegMovement", "MV"), ("LeftFoot", "PR"), ("LeftHand", "PR"),
    ("LeftFingers", "PR"), ("LowerLeftArm", "PR"), ("UpperLeftArm", "PR"),
    ("LeftArmMovement", "MV"), ("LowerRightLeg", "PR"), ("UpperRightLeg", "PR"),
    ("RightLegMovement", "MV"), ("RightFoot", "PR"), ("LowerRightArm", "PR"),
    ("RightHand", "PR"), ("RightFingers", "PR"), ("UpperRightArm", "PR"),
    ("RightArmMovement", "MV"),
]

def _s12(v):
    return v - 0x1000 if v & 0x800 else v

def _s10(v):
    return v - 0x400 if v & 0x200 else v

def decode_pr(b):
    # [PivotX s12][Rotation u10][PivotZ s10] over the big-endian word.
    w = int.from_bytes(b, 'big')
    px = _s12(w >> 20)
    r = (w >> 10) & 0x3FF          # unsigned, 1024 = full turn
    pz = _s10(w & 0x3FF)
    return {"pivot": [px, pz], "rot": r}

def decode_om(b):
    ox = _s12((b[0] << 4) | ((b[1] & 0xF0) >> 4))
    oy = ((b[1] & 0x0F) << 4) | ((b[2] & 0xF0) >> 4)
    oz = _s12(((b[2] & 0x0F) << 8) | b[3])
    return {"overall": [ox, oy, oz]}

def decode_frame(fr):
    out = {}
    o = 0
    for name, kind in ORDER:
        if kind == "PR":
            out[name] = decode_pr(fr[o:o + 4]); o += 4
        elif kind == "OM":
            out[name] = decode_om(fr[o:o + 4]); o += 4
        else:
            out[name] = {"move": [fr[o], fr[o + 1], fr[o + 2]]}; o += 3
    assert o == 0x62, o
    return out

class FileTable:
    def __init__(self, data):
        self.data = data
    def entry(self, i):
        v = struct.unpack('>I', self.data[FT + i * 4:FT + i * 4 + 4])[0]
        return (v & 0xFFFFFFFE, bool(v & 1))
    def get(self, fid):
        # File IDs are 1-based (FUN_80003bd0): table index = fid - 1.
        loc, enc = self.entry(fid - 1)
        nloc, _ = self.entry(fid)
        return self.data[FIRST + loc:FIRST + nloc], enc

def load_anim(data, fid):
    raw, enc = FileTable(data).get(fid)
    assert not enc, "encoded (LZSS) file not handled"
    toki2 = raw[:4].hex()
    frames = [decode_frame(raw[4 + f * 98:4 + (f + 1) * 98])
              for f in range((len(raw) - 4) // 98)]
    return {"file_id": hex(fid), "toki2": toki2, "frames": frames,
            "nframes": len(frames)}

def main():
    data = open(ROM, 'rb').read()
    cmd = sys.argv[1]
    if cmd == 'info':
        fid = int(sys.argv[2], 16)
        a = load_anim(data, fid)
        print(f"file {fid:04X}: toki2={a['toki2']} frames={a['nframes']}")
    elif cmd == 'json':
        fid = int(sys.argv[2], 16)
        a = load_anim(data, fid)
        json.dump(a, open(sys.argv[3], 'w'), indent=1)
        print(f"wrote {sys.argv[3]} ({a['nframes']} frames)")
    elif cmd == 'survey':
        from collections import Counter
        c = Counter()
        fid = FIRST_ANIM
        while True:
            raw, _ = FileTable(data).get(fid)
            if len(raw) < 4:
                break
            c[(len(raw) - 4) // 98] += 1
            fid += 1
            if fid > 0x3400:
                break
        for fr in sorted(c):
            print(f"{fr:4d} frames: {c[fr]}")
        print(f"range {FIRST_ANIM:04X}..{fid - 1:04X}")

if __name__ == '__main__':
    main()
