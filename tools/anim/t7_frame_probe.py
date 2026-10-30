#!/usr/bin/env python3
"""t7_frame_probe.py: evidence tool for the T7 0x64 joint-frame question (docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md).

Reads the raw T7 files from the private GRE checkout (never copies them into this repo) and prints the measurements
the findings doc is built on:

  channels <rotsm.arc>                per-channel p5/p50/p95 of the 23-bone 0xC8 clips vs the 0x64 clips in one bank
  stance   <mot.json> <rotsm.arc>     the character's 0xC8 standing stance (frame 1) vs the median first frame of its
                                      0x64 attacks (the only same-pose pair in the files: the stance is 0xC8, attacks 0x64)
  hinge    <SK_CH_*_bdu_1p.glb>       on the character's own T7 skeleton (pakchunk0 export), which way a hinge value
                                      bends the forearm / shin about each bind-local axis (anatomy: hand forward, foot back)

Slot -> bone map is Kiloutre's applyRotationFromAnimdata (BlenderTekkenDirect, TekkenAnimHelper.py). Decoding uses
tools/anim/t7_anim64.py. Read-only: writes nothing unless --out is given.
"""
import argparse, json, math, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import Anim64, mota_anims  # noqa: E402

SLOT_BONE = {3: 'BASE', 4: 'Spine1', 5: 'Hip', 7: 'Neck', 8: 'Head', 9: 'R_Shoulder', 10: 'R_Arm', 11: 'R_ForeArm',
             12: 'R_Hand', 13: 'L_Shoulder', 14: 'L_Arm', 15: 'L_ForeArm', 16: 'L_Hand', 17: 'R_UpLeg', 18: 'R_Leg',
             19: 'R_Foot', 20: 'L_UpLeg', 21: 'L_Leg', 22: 'L_Foot'}
CH = ['mvX', 'mvY', 'mvZ', 'posX', 'posY', 'posZ', 'b2x', 'b2y', 'b2z']
for s in range(3, 23):
    n = SLOT_BONE.get(s, 'slot%d' % s)
    CH += ['%s.%s' % (n, a) for a in 'xyz']


def clips(path):
    """Yield (mota_offset, index, fmt, bone_count, frames[69]) for every clip in a MOTA-bearing file."""
    d = open(path, 'rb').read()
    for m in re.finditer(b'MOTA', d):
        M = m.start()
        try:
            offs = mota_anims(d, M)
        except Exception:  # noqa: BLE001 - not a real MOTA header
            continue
        for i, o in enumerate(offs):
            o += M
            t = d[o + 1] if d[o] == 0 else d[o]
            try:
                if t == 0x64:
                    a = Anim64(d, o)
                    yield M, i, '0x64', a.nb, [sum((b for b in f[:23]), []) for f in a.frames()]
                elif t == 0xC8:
                    e = '<' if d[o] != 0 else '>'
                    nb = struct.unpack_from(e + 'H', d, o + 2)[0]
                    n = struct.unpack_from(e + 'I', d, o + 4)[0]
                    p = o + 8 + 4 * nb
                    yield M, i, '0xC8', nb, [list(struct.unpack_from(e + '%df' % (3 * nb), d, p + 12 * nb * k))[:69] for k in range(n)]
            except Exception:  # noqa: BLE001 - truncated clip
                continue


def pct(vals, q):
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(q * len(vals)))]


def cmd_channels(a):
    c8 = [c for c in clips(a.arc) if c[2] == '0xC8' and c[3] == 23]
    c64 = [c for c in clips(a.arc) if c[2] == '0x64' and c[3] >= 23]
    print('23-bone clips: 0xC8 %d, 0x64 %d' % (len(c8), len(c64)))
    rows = []
    for ch in range(69):
        v8 = [f[ch] for c in c8 for f in c[4]]
        v6 = [f[ch] for c in c64 for f in c[4]]
        r = [CH[ch]] + ([pct(v8, q) for q in (.05, .5, .95)] if v8 else [None] * 3) + [pct(v6, q) for q in (.05, .5, .95)]
        rows.append(r)
        print('%-14s 0xC8 %s | 0x64 %8.3f %8.3f %8.3f' % (r[0], ' '.join('%8.3f' % x for x in r[1:4]) if v8 else '   (none)', *r[4:]))
    return rows


def cmd_stance(a):
    mv = json.load(open(a.motjson))['moves']
    by_clip = {}
    for M, i, fmt, nb, fr in clips(a.arc):
        if M == min(m.start() for m in re.finditer(b'MOTA', open(a.arc, 'rb').read())):
            by_clip[i] = (fmt, nb, fr)
    stance = [m for m in mv if m['name'].endswith('sKAM00_') and (m['anim_id'] & 0xC000) == 0x4000]
    if not stance:
        sys.exit('no <code>_sKAM00_ stance move in the 0x4000 bank')
    sc = by_clip[stance[0]['anim_id'] & 0x3FFF]
    print('stance move %s -> anim %s fmt %s (%d frames)' % (stance[0]['name'], stance[0]['anim'], sc[0], len(sc[2])))
    firsts = [by_clip[m['anim_id'] & 0x3FFF][2][0] for m in mv if m.get('damage') and (m['anim_id'] & 0xC000) == 0x4000
              and by_clip.get(m['anim_id'] & 0x3FFF, ('', 0))[0] == '0x64' and by_clip[m['anim_id'] & 0x3FFF][1] == 23]
    print('0x64 attacks (23-bone) whose first frame is compared: %d' % len(firsts))
    out = []
    for ch in range(69):
        vals = [f[ch] for f in firsts]
        out.append([CH[ch], sc[2][0][ch], pct(vals, .5), pct(vals, .25), pct(vals, .75)])
        print('%-14s stance(%s) f1 %9.3f | 0x64 attack f1 median %9.3f  IQR %8.3f..%8.3f' % (CH[ch], sc[0], *out[-1][1:]))
    return out


def _glb_skeleton(path):
    b = open(path, 'rb').read()
    j = json.loads(b[20:20 + struct.unpack_from('<I', b, 12)[0]])
    nodes = j['nodes']
    par = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
    return nodes, par


def _qm(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def _mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _mv(A, v):
    return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]


def _axis_rot(axis, a):
    c, s = math.cos(a), math.sin(a)
    if axis == 0: return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if axis == 1: return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def cmd_hinge(a):
    nodes, par = _glb_skeleton(a.glb)
    idx = {n.get('name'): i for i, n in enumerate(nodes)}
    memo = {}

    def world(i, override=None):
        key = (i, None if override is None else tuple(map(tuple, override[1])), None if override is None else override[0])
        n = nodes[i]
        R = _qm(n.get('rotation', [0, 0, 0, 1]))
        if override and override[0] == i:
            R = _mm(R, override[1])
        t = n.get('translation', [0, 0, 0])
        if i in par:
            PR, PP = world(par[i], override)
            return _mm(PR, R), [PP[k] + _mv(PR, t)[k] for k in range(3)]
        return R, list(t)
    eye = idx['L_Eye_Joint']
    fwd = world(eye)[1][2] - world(idx['Head'])[1][2]
    print('facing: the eyes sit %+.3f m along world Z from the head joint -> forward = %sZ' % (fwd, '+' if fwd > 0 else '-'))
    sign = 1 if fwd > 0 else -1
    rows = []
    for bone, child, want in (('R_ForeArm', 'R_Hand', +1), ('L_ForeArm', 'L_Hand', +1), ('R_Leg', 'R_Foot', -1), ('L_Leg', 'L_Foot', -1)):
        bi, ci = idx[bone], idx[child]
        base = world(ci)[1]
        for axis in range(3):
            moved = world(ci, (bi, _axis_rot(axis, 0.5)))[1]
            dz = (moved[2] - base[2]) * sign
            rows.append([bone, 'XYZ'[axis], round(dz, 4)])
            print('%-10s +0.5 rad about bind-local %s moves %s forward by %+.3f m (anatomy wants %s)' % (
                bone, 'XYZ'[axis], child, dz, 'forward' if want > 0 else 'backward'))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('channels'); p.add_argument('arc')
    p = sp.add_parser('stance'); p.add_argument('motjson'); p.add_argument('arc')
    p = sp.add_parser('hinge'); p.add_argument('glb')
    ap.add_argument('--out')
    a = ap.parse_args()
    rows = {'channels': cmd_channels, 'stance': cmd_stance, 'hinge': cmd_hinge}[a.cmd](a)
    if a.out:
        json.dump(rows, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
