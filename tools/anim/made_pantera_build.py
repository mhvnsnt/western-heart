#!/usr/bin/env python3
"""Build Pantera's 3 MADE ADAPT clips from the decoded T3 King bank.

MADE, not decoded: each output is a real decoded T3 King clip transformed
by a documented piecewise time-warp (see docs/anim/MADE-PANTERA-2026-10-24.md).
Nothing here claims to be decoded motion.

Usage:
  python3 tools/anim/made_pantera_build.py \
    --bank game/assets/anim/t3/king_on_pantera_leoman \
    --out game/assets/anim/made/pantera

Inputs read from --bank: rows.pack.json, t3_grab.json, skeleton.json.
Outputs: made_pantera_honest-hold.json, made_pantera_tail-tip-lunge.json,
made_pantera_battle-itself.json (wh-anim/1: bones, rot_xyzw, root_t, fps).

Warp anchors are MEASURED: forward kinematics over the bank skeleton's
rest pose (identity rest rotations); extension = hand-to-Chest distance
per frame; peak = argmax. The warp maps source [0..peak] onto the move's
startup, holds the peak through its active frames, and maps [peak..end]
onto its recovery. Battle Itself additionally repeats its strike segment
3x across active+recovery (same-arm repeat; no mirror transform is
shipped — see the Pantera doc) and pitches the head back up to 18 deg
during windup for the roar.

Validation (run automatically): wh-anim/1 shape, 22 bones, equal
rot/root lengths, unit quaternions, finite values, and output durations
within 1 frame of the move totals. This is structural validation only —
NOT play verification.
"""
import argparse, base64, json, math, os, sys

BONES_EXPECTED = 22


def quat_mul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return [aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz]


def quat_norm(q):
    n = math.sqrt(sum(x * x for x in q)) or 1.0
    return [x / n for x in q]


def quat_conj(q):
    return [-q[0], -q[1], -q[2], q[3]]


def quat_rot(v, q):
    q = quat_norm(q)
    r = quat_mul(quat_mul(q, [v[0], v[1], v[2], 0.0]), quat_conj(q))
    return r[:3]


def slerp(a, b, t):
    a = quat_norm(a); b = quat_norm(b)
    d = sum(x * y for x, y in zip(a, b))
    if d < 0:
        b = [-x for x in b]; d = -d
    if d > 0.9995:
        return quat_norm([a[i] + t * (b[i] - a[i]) for i in range(4)])
    th = math.acos(min(1, max(-1, d))); s = math.sin(th)
    return quat_norm([(math.sin((1 - t) * th) / s) * a[i] +
                      (math.sin(t * th) / s) * b[i] for i in range(4)])


def sample_track(frames, t):
    if t <= 0:
        return frames[0]
    if t >= len(frames) - 1:
        return frames[-1]
    i = int(math.floor(t)); f = t - i
    return slerp(frames[i], frames[i + 1], f)


def sample_root(root, t):
    comps = [[r[c] for r in root] for c in range(3)]
    out = []
    for comp in comps:
        if t <= 0:
            out.append(comp[0])
        elif t >= len(comp) - 1:
            out.append(comp[-1])
        else:
            i = int(math.floor(t)); f = t - i
            out.append(comp[i] * (1 - f) + comp[i + 1] * f)
    return out


def b64i16(s):
    raw = base64.b64decode(s)
    return [(raw[i] | (raw[i + 1] << 8)) - 0x10000
            if (raw[i] | (raw[i + 1] << 8)) >= 0x8000
            else (raw[i] | (raw[i + 1] << 8))
            for i in range(0, len(raw), 2)]


def decode_row(pack, rec):
    q = b64i16(rec['q']); rx = b64i16(rec['rx'])
    ry = b64i16(rec['ry']); rz = b64i16(rec['rz'])
    nb = len(pack['bones']); n = rec['n']; rot = {}
    for bi, b in enumerate(pack['bones']):
        arr = []
        for f in range(n):
            o = (f * nb + bi) * 4
            arr.append([q[o] / 32767, q[o + 1] / 32767,
                        q[o + 2] / 32767, q[o + 3] / 32767])
        rot[b] = arr
    root = [[rx[f] / 1000, ry[f] / 1000, rz[f] / 1000] for f in range(n)]
    return {'format': 'wh-anim/1', 'fps': pack['fps'], 'bones': pack['bones'],
            'rot_xyzw': rot, 'root_t': root, 'bank': pack['bank'],
            'slot': rec['slot'], 'move_row': int(rec['move_row'])}


def extension_peak(clip, skel, hand, ref='Chest'):
    rest = {j['name']: j['rest'] for j in skel['joints']}
    parent = {j['name']: j['parent'] for j in skel['joints']}
    order = [j['name'] for j in skel['joints']]
    n = len(clip['rot_xyzw']['Root'])
    wq = {}; wp = {}
    for j in order:
        qs = clip['rot_xyzw'][j]; par = parent[j]
        if par is None:
            wq[j] = [quat_norm(q) for q in qs]
            wp[j] = [list(clip['root_t'][f]) for f in range(n)]
        else:
            off = [rest[j][i] - rest[par][i] for i in range(3)]
            wq[j] = [quat_norm(quat_mul(wq[par][f], quat_norm(qs[f])))
                     for f in range(n)]
            wp[j] = [[wp[par][f][i] + quat_rot(off, wq[par][f])[i]
                      for i in range(3)] for f in range(n)]
    d = [math.dist(wp[hand][f], wp[ref][f]) for f in range(n)]
    return max(range(n), key=lambda i: d[i]), d


def warp_clip(src, startup_s, active_s, recovery_s, peak,
              repeat_strike=None, head_roar_deg=0.0):
    fps = 30.0
    total = startup_s + active_s + recovery_s
    n_out = max(8, int(round(total * fps)))
    n_wind = int(round(startup_s * fps)); n_act = int(round(active_s * fps))
    n_rec = n_out - n_wind - n_act
    times = []
    for i in range(n_wind):
        times.append(peak * (i / max(1, n_wind - 1)) if n_wind > 1 else 0.0)
    times.extend([float(peak)] * n_act)
    src_n = len(src['rot_xyzw']['Root'])
    if repeat_strike:
        s0, s1, cnt = repeat_strike
        seg_len = s1 - s0
        per = max(2, n_rec // (cnt + 1))
        rec_times = []
        for _ in range(cnt):
            for k in range(per):
                rec_times.append(s0 + seg_len * (k / max(1, per - 1)))
        tail_n = n_rec - len(rec_times)
        for k in range(tail_n):
            rec_times.append(s1 + (src_n - 1 - s1) * (k / max(1, tail_n - 1))
                             if tail_n > 1 else float(s1))
        times.extend(rec_times[:n_rec])
    else:
        for i in range(n_rec):
            times.append(peak + (src_n - 1 - peak) * (i / max(1, n_rec - 1))
                         if n_rec > 1 else float(peak))
    times = times[:n_out]
    out_rot = {b: [sample_track(src['rot_xyzw'][b], t) for t in times]
               for b in src['bones']}
    out_root = [sample_root(src['root_t'], t) for t in times]
    if head_roar_deg:
        for i in range(n_out):
            if i < n_wind:
                a = -math.radians(head_roar_deg) * (i / max(1, n_wind - 1))
            elif i < n_wind + n_act:
                a = -math.radians(head_roar_deg)
            else:
                a = -math.radians(head_roar_deg) * (
                    1 - (i - n_wind - n_act) / max(1, n_rec - 1))
            roar = [math.sin(a / 2), 0, 0, math.cos(a / 2)]
            out_rot['Head'][i] = quat_norm(quat_mul(roar, out_rot['Head'][i]))
    return {'format': 'wh-anim/1', 'fps': 30.0, 'bones': src['bones'],
            'rot_xyzw': out_rot, 'root_t': out_root}


def validate(path, expect_frames):
    d = json.load(open(path))
    assert d['format'] == 'wh-anim/1' and d['fps'] == 30.0
    assert d['provenance'] == 'MADE' and 'MADE' in d['source']
    assert len(d['bones']) == BONES_EXPECTED
    n = len(d['rot_xyzw']['Root'])
    assert n == expect_frames, (path, n, expect_frames)
    assert len(d['root_t']) == n
    for b in d['bones']:
        assert len(d['rot_xyzw'][b]) == n, (path, b)
        for q in d['rot_xyzw'][b]:
            assert all(math.isfinite(x) for x in q)
            assert abs(math.sqrt(sum(x * x for x in q)) - 1) < 1e-3
    assert all(all(math.isfinite(x) for x in r) for r in d['root_t'])
    print(f'OK {os.path.basename(path)}: {n} frames, '
          f'{n / 30.0:.3f}s, MADE-labelled')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bank', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    pack = json.load(open(os.path.join(args.bank, 'rows.pack.json')))
    grab = json.load(open(os.path.join(args.bank, 't3_grab.json')))
    skel = json.load(open(os.path.join(args.bank, 'skeleton.json')))
    row111 = decode_row(pack, pack['rows']['111'])
    row220 = decode_row(pack, pack['rows']['220'])
    pk_g, _ = extension_peak(grab, skel, 'RightHand')
    pk_111, _ = extension_peak(row111, skel, 'RightHand')
    pk_220, _ = extension_peak(row220, skel, 'LeftHand')
    print(f'measured peaks: grab={pk_g} row111={pk_111} row220={pk_220}')
    os.makedirs(args.out, exist_ok=True)
    specs = []
    hold = warp_clip(grab, 0.32, 0.05, 0.90, pk_g)
    hold.update({
        'source': 'MADE — adapted from REAL decoded T3 King grab '
                  '(t3_grab.json, move_row 230, bank divmot03_king.bin); '
                  'NOT a decoded move',
        'made_from': 't3:king:row:230',
        'made_method': 'ADAPT: piecewise time-warp anchored on measured '
                       'RightHand-extension peak; grip held through active frames',
        'move': 'wh:pantera:sig:honest-hold', 'input_lp': 'LP1+RK4',
        'provenance': 'MADE'})
    specs.append(('made_pantera_honest-hold.json', hold, 38))
    lunge = warp_clip(row111, 0.22, 0.017, 0.72, pk_111)
    lunge.update({
        'source': 'MADE — adapted from REAL decoded T3 King f+2 row 111 '
                  '(armR forward strike, bank divmot03_king.bin); '
                  'NOT a decoded move',
        'made_from': 't3:king:row:111',
        'made_method': 'ADAPT: piecewise time-warp anchored on measured '
                       'RightHand-extension peak; filed limb armR + forward '
                       'motion match; see spec for the f+LP1 vs armR conflict',
        'move': 'wh:pantera:sig:tail-tip-lunge', 'input_lp': 'f+LP1',
        'provenance': 'MADE'})
    specs.append(('made_pantera_tail-tip-lunge.json', lunge, 29))
    battle = warp_clip(row220, 0.30, 0.20, 1.05, pk_220,
                       repeat_strike=(pk_220,
                                      min(pk_220 + 9,
                                          len(row220['rot_xyzw']['Root']) - 1),
                                      3),
                       head_roar_deg=18.0)
    battle.update({
        'source': 'MADE — adapted from REAL decoded T3 King 1+2 row 220 '
                  '(LP1+RP2, armL, startup 0.30s matches signature startup; '
                  'bank divmot03_king.bin); NOT a decoded move',
        'made_from': 't3:king:row:220',
        'made_method': 'ADAPT: piecewise time-warp + strike-segment x3 '
                       'flurry repeat + roar head-pitch during windup; '
                       'same-arm repeat (mirror transform unverified, NOT shipped)',
        'move': 'wh:pantera:sig:battle-itself', 'input_lp': 'LP1+RP2',
        'provenance': 'MADE'})
    specs.append(('made_pantera_battle-itself.json', battle, 46))
    for name, clip, frames in specs:
        p = os.path.join(args.out, name)
        json.dump(clip, open(p, 'w'))
        validate(p, frames)
    print('All MADE clips built and validated (structural only, not played).')


if __name__ == '__main__':
    main()
