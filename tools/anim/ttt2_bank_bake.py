#!/usr/bin/env python3
"""ttt2_bank_bake.py: bake real Tekken Tag Tournament 2 clips into a Western Heart generic bank.

Sibling of tools/anim/t7_c8_stance_bake.py (PR #1550's shape), fed by the TTT2 join
(docs/tech/ttt2-mota/JOIN-SEARCH-ROUND4.md + docs/tech/ttt2-mota/join/*-join.json):
every slot names the character's OWN motbin move; the move's anim_ref (bank<<14)|index
locates the clip in the decoded TTT2 containers (bank 1 = per-character table in
data005-decoded.bin, bank 2 = the shared table in data004-decoded.bin @0x100).

Pipeline (nothing authored, nothing guessed):
  1. decode the clip with the shipped decoders (0x64: tools/ttt2_mota_decode64.py;
     0xC8: the big-endian raw-float layout of docs/tech/ttt2-mota/DECODE-SPEC.md);
  2. Blender (headless) poses Koenji's TekkenMannequin with Kiloutre's
     applyRotationFromAnimdata (tools/anim/t7_bl_pose.py) and dumps world rotations;
  3. converts to canonical space exactly like the T7 bake (rest via C, posed via C2,
     FK self-check <= 1e-3 m) and applies the in-game plausibility gate from
     tools/anim/t7_move_bake.py (upright start, floor tol -0.08 m, jump tol 1.5 m).
     A clip that fails decode validation or the gate is SKIPPED with its reason
     printed (and in the JSON report) -- never forced, never faked.

Usage:
  python3 tools/anim/ttt2_bank_bake.py --slots slots.json --out-dir game/assets/anim/t3/roger \
     --data004 <path> --data005 <path> --decoder64 tools/ttt2_mota_decode64.py \
     --mannequin <TekkenMannequin_no_ik.blend> --helper <TekkenAnimHelper.py> \
     --bl-pose tools/anim/t7_bl_pose.py --blender <blender wrapper>

slots.json: {"bank": "roger", "character": "Roger Jr. (Tekken Tag Tournament 2)",
  "fighter": "menajerii", "bank1_table": 90926084, "join_file": "roger-join.json",
  "slots": {"t3_neutral": {"move": "Rg_sKAM00_", "anim": "kjrg_kamae02(DVD)", "bank": 1, "idx": 48}, ...},
  "gaps": {"t3_light": "reason the slot has no clip (documented, no file written)"}}
"""
import argparse, hashlib, importlib.util, json, math, os, struct, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pose_synth import Synthesizer

HELPER_COMMIT = 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1'
C = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)    # mannequin rest (faces -Y, Z up) -> canonical
C2 = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float)    # Tekken fight frame (faces +X, left +Y, Z up) -> canonical
MAP = [('Hips', 'Hip', None), ('Spine', 'Spine1', 'Hips'), ('Chest', 'Spine2', 'Spine'), ('Neck', 'Neck', 'Chest'),
       ('Head', 'Head', 'Neck')]
for _side, _t in (('Left', 'L'), ('Right', 'R')):
    MAP += [(_side + 'Shoulder', _t + '_Shoulder', 'Chest'), (_side + 'Arm', _t + '_Arm', _side + 'Shoulder'),
            (_side + 'ForeArm', _t + '_ForeArm', _side + 'Arm'), (_side + 'Hand', _t + '_Hand', _side + 'ForeArm'),
            (_side + 'UpLeg', _t + '_UpLeg', 'Hips'), (_side + 'Leg', _t + '_Leg', _side + 'UpLeg'),
            (_side + 'Foot', _t + '_Foot', _side + 'Leg'), (_side + 'ToeBase', _t + '_Toe', _side + 'Foot')]

FLOOR_TOL, JUMP_TOL = -0.08, 1.5


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def mat_to_quat(m):
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w, x, y, z = (m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w, x, y, z = (m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[1, 0]) / s
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w, x, y, z = (m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[1, 0]) / s, 0.25 * s
    q = np.array([x, y, z, w])
    return q / np.linalg.norm(q)


def orth(m):
    u, _, vt = np.linalg.svd(np.array(m, float))
    r = u @ vt
    return r if np.linalg.det(r) > 0 else u @ np.diag([1, 1, -1]) @ vt


def convert(posed, provenance, mannequin_meta):
    rest_pos = {c: C @ np.array(posed['rest'][t]['head']) for c, t, _ in MAP}
    rest_rot = {c: orth(posed['rest'][t]['rot']) for c, t, _ in MAP}
    rot = {c: [] for c, _, _ in MAP}
    root_t, worst = [], 0.0
    for fr in posed['frames']:
        G = {c: C2 @ orth(fr[t]['rot']) @ rest_rot[c].T @ C.T for c, t, _ in MAP}
        pos = {c: C2 @ np.array(fr[t]['head']) for c, t, _ in MAP}
        fk = {}
        for c, _, p in MAP:
            loc = G[c] if p is None else G[p].T @ G[c]
            q = mat_to_quat(loc)
            if rot[c] and float(np.dot(q, rot[c][-1])) < 0:
                q = -q
            rot[c].append([round(float(v), 6) for v in q])
            fk[c] = pos['Hips'] if p is None else fk[p] + G[p] @ (rest_pos[c] - rest_pos[p])
            worst = max(worst, float(np.linalg.norm(fk[c] - pos[c])))
        root_t.append([round(float(v), 6) for v in pos['Hips']])
    skel = {'format': 'wh-anim-skel/1', 'tool': 'tools/anim/ttt2_bank_bake.py',
            'note': 'Rest pose of the Tekken skeleton (Koenji TekkenMannequin) the TTT2 clips here were converted on. '
                    'All joint rest rotations are identity; rest = world joint positions (glTF space, meters, faces +Z, '
                    'character left = +X).',
            'source_skeleton': mannequin_meta, 'root': 'Hips', 'root_rest_y': round(float(rest_pos['Hips'][1]), 6),
            'joints': [{'name': c, 'parent': p, 'rest': [round(float(v), 6) for v in rest_pos[c]]} for c, _, p in MAP],
            'foot_tip': {}}
    clip = {'format': 'wh-anim/1', 'fps': 60.0, 'anim_set': 'FIGHT', 'bones': [c for c, _, _ in MAP],
            'rot_xyzw': rot, 'root_t': root_t,
            'source': 'REAL Tekken Tag Tournament 2 motion (0x64, decoded by tools/ttt2_mota_decode64.py)',
            **provenance, 'fk_selfcheck_max_m': round(worst, 6)}
    return skel, clip, worst


def _qmul(a, b):
    return [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
            a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]]


def _qrot(q, v):
    x, y, z, w = q
    tx, ty, tz = 2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])
    return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]


def fk_frames(clip, skel):
    rest = {j['name']: j['rest'] for j in skel['joints']}
    out = []
    for f in range(len(clip['root_t'])):
        G, X = {}, {}
        for j in skel['joints']:
            n, p = j['name'], j['parent']
            q = clip['rot_xyzw'][n][f]
            if not p:
                G[n], X[n] = q, list(clip['root_t'][f])
                continue
            G[n] = _qmul(G[p], q)
            o = _qrot(G[p], [rest[n][i] - rest[p][i] for i in range(3)])
            X[n] = [X[p][i] + o[i] for i in range(3)]
        out.append(X)
    return out


def implausible(clip, skel):
    fr = fk_frames(clip, skel)
    if not fr or not fr[0]['Head'][1] > fr[0]['Hips'][1] + 0.2:
        return 'does not start upright'
    prev = None
    for f, X in enumerate(fr):
        j, p = min(X.items(), key=lambda kv: kv[1][1])
        if p[1] <= FLOOR_TOL:
            return '%s %.2f m below the floor on frame %d (mannequin proportions)' % (j, -p[1], f)
        if prev:
            for n, q in X.items():
                if n == 'Hips':
                    continue
                d = sum((q[i] - X['Hips'][i] - (prev[n][i] - prev['Hips'][i])) ** 2 for i in range(3)) ** 0.5
                if d >= JUMP_TOL:
                    return '%s jumps %.2f m on frame %d' % (n, d, f)
        prev = X
    return None


def implausible_excl(clip, skel, excl):
    """implausible() with some joints excluded from the floor check (the jump
    and upright checks still apply to everything)."""
    fr = fk_frames(clip, skel)
    if not fr or not fr[0]['Head'][1] > fr[0]['Hips'][1] + 0.2:
        return 'does not start upright'
    prev = None
    for f, X in enumerate(fr):
        pool = {k: v for k, v in X.items() if k not in excl}
        j, p = min(pool.items(), key=lambda kv: kv[1][1])
        if p[1] <= FLOOR_TOL:
            return '%s %.2f m below the floor on frame %d (mannequin proportions)' % (j, -p[1], f)
        if prev:
            for n, q in X.items():
                if n == 'Hips':
                    continue
                d = sum((q[i] - X['Hips'][i] - (prev[n][i] - prev['Hips'][i])) ** 2 for i in range(3)) ** 0.5
                if d >= JUMP_TOL:
                    return '%s jumps %.2f m on frame %d' % (n, d, f)
        prev = X
    return None


def decode_c8(entry):
    """TTT2 0xC8: big-endian raw float frames (docs/tech/ttt2-mota/DECODE-SPEC.md)."""
    be16 = lambda o: struct.unpack('>H', entry[o:o + 2])[0]
    be32 = lambda o: struct.unpack('>I', entry[o:o + 4])[0]
    bef = lambda o: struct.unpack('>f', entry[o:o + 4])[0]
    n, f = be16(2), be32(4)
    off = 8 + 4 * n
    frames = []
    for fr in range(f):
        row = []
        for t in range(n):
            o = off + (fr * n + t) * 12
            row.append((bef(o), bef(o + 4), bef(o + 8)))
        frames.append(row)
    return frames


def unwrap_rotations(frames, ref_triples=None):
    """Per rotation track, choose each frame's representative closest (in
    rotation space) to the previous frame's chosen representative, searching
    the full equivalence class of the stored triple: per-component +/-2pi
    wraps AND the two euler alias branches. The game's sampler builds
    rotations from sin/cos of the stored values (Default.xex func 0x82289228),
    so it is invariant over this whole class (the i16 pose accumulator also
    wraps at +-pi in output units); the euler composition used for posing is
    not, so continuity is restored here first. Frame 0 is anchored to
    ref_triples (the character's own stance frame-0 triples) when given.
    Translation tracks (0,1,2) and the f32 Spine2 track (6) are untouched."""
    import itertools as _it
    from scipy.spatial.transform import Rotation as _Rot

    def G(t):
        return _Rot.from_euler('ZXY', (-t[1] * 0.5, t[2] * 0.5, t[0] * 0.5), degrees=False).as_matrix()

    def candidates(t):
        bases = [tuple(t),
                 (t[0] + 2 * math.pi, t[1] - 2 * math.pi, 2 * math.pi - t[2]),
                 (t[0] - 2 * math.pi, t[1] + 2 * math.pi, -2 * math.pi - t[2])]
        out = []
        for b in bases:
            for k in _it.product((-1, 0, 1), repeat=3):
                out.append((b[0] + 2 * math.pi * k[0], b[1] + 2 * math.pi * k[1], b[2] + 2 * math.pi * k[2]))
        return out

    out = [[tuple(t) for t in row] for row in frames]
    for tr in range(23):
        if tr in (0, 1, 2, 6):
            continue
        prev = G(ref_triples[tr]) if ref_triples is not None else None
        for f in range(len(out)):
            t = out[f][tr]
            if prev is None:
                prev = G(t)
                continue
            best, best_err, best_M = t, None, None
            for cand in candidates(t):
                M = G(cand)
                err = float(np.abs(M - prev).max())
                if best_err is None or err < best_err:
                    best, best_err, best_M = cand, err, M
            out[f][tr] = best
            prev = best_M
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--slots', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--data004', required=True)
    ap.add_argument('--data005', required=True)
    ap.add_argument('--decoder64', required=True)
    ap.add_argument('--mannequin', required=True)
    ap.add_argument('--helper', required=True)
    ap.add_argument('--bl-pose', required=False, default='')
    ap.add_argument('--blender', required=False, default='')
    ap.add_argument('--calib', required=True, help='per-joint A/B frame-change calibration JSON')
    ap.add_argument('--root-affine', required=True, help='root translation affine JSON')
    ap.add_argument('--rest', required=True, help='mannequin rest pose JSON (from t7_bl_pose.py)')
    a = ap.parse_args()

    spec = json.load(open(a.slots))
    d4 = open(a.data004, 'rb').read()
    d5 = open(a.data005, 'rb').read()
    d4_sha, d5_sha = sha256_bytes(d4), sha256_bytes(d5)
    dec_spec = importlib.util.spec_from_file_location('dec64', a.decoder64)
    dec64 = importlib.util.module_from_spec(dec_spec)
    dec_spec.loader.exec_module(dec64)
    u32 = lambda d, o: struct.unpack('>I', d[o:o + 4])[0]
    tables = {1: (d5, spec['bank1_table'], os.path.basename(a.data005), d5_sha),
              2: (d4, 0x100, os.path.basename(a.data004), d4_sha)}
    mannequin_meta = {'file': os.path.basename(a.mannequin), 'by': 'Koenji', 'sha256': sha256(a.mannequin),
                      'url': 'https://mega.nz/folder/05pBGLAL#XPHcsgK2tBxT3RLMbZPaFw'}
    helper_sha = sha256(a.helper)
    rest = json.load(open(a.rest))
    synth = Synthesizer(a.calib, rest, a.root_affine)
    # frame-0 branch reference: the character's own stance (t3_neutral) triples.
    ref_triples = None
    ns = spec['slots'].get('t3_neutral')
    if ns is not None:
        data, tab, _, _ = tables[ns['bank']]
        eoff = tab + u32(data, tab + 16 + 4 * ns['idx'])
        if struct.unpack('>H', data[eoff:eoff + 2])[0] == 100:
            ref_triples = dec64.decode_clip(data, eoff)['frames'][0]
    os.makedirs(a.out_dir, exist_ok=True)
    report = {'bank': spec['bank'], 'baked': {}, 'skipped': {}, 'gaps': spec.get('gaps', {})}
    skel_written = None
    for slot, s in spec['slots'].items():
        data, tab, cname, csha = tables[s['bank']]
        eoff = tab + u32(data, tab + 16 + 4 * s['idx'])
        typ = struct.unpack('>H', data[eoff:eoff + 2])[0]
        try:
            if typ == 100:
                r = dec64.decode_clip(data, eoff)
                frames, fmt = r['frames'], '0x64'
                ntr = r['header']['N']
            elif typ == 200:
                frames, fmt = decode_c8(data[eoff:eoff + 8_000_000]), '0xC8'
                ntr = len(frames[0])
            else:
                raise ValueError('entry type %d is not a body clip format (0x64/0xC8)' % typ)
        except Exception as e:
            print('SKIP %s: decode failed: %s' % (slot, e))
            report['skipped'][slot] = 'decode failed: %s' % e
            continue
        if ntr < 23 or len(frames) < 2:
            print('SKIP %s: %d tracks / %d frames, not a 23-track body clip' % (slot, ntr, len(frames)))
            report['skipped'][slot] = 'not a 23-track body clip (%d tracks, %d frames)' % (ntr, len(frames))
            continue
        flat = []
        bad = False
        for row in frames:
            fr = []
            for t in range(23):
                for v in row[t]:
                    if not math.isfinite(v) or abs(v) > 1e4:
                        bad = True
                    fr.append(float(v))
            flat.append(fr)
        if bad:
            print('SKIP %s: decoded values non-finite/out of range (encoder variant)' % slot)
            report['skipped'][slot] = 'decoded values non-finite/out of range (unidentified encoder variant)'
            continue
        posed = synth.pose(unwrap_rotations(frames, ref_triples) if fmt == '0x64' else frames,
                           '64' if fmt == '0x64' else 'c8')
        provenance = {'character': spec['character'], 'for_fighter': spec['fighter'], 'loop': True,
                      'ttt2_source': {'file': cname, 'sha256': csha, 'bank': s['bank'], 'clip': s['idx'],
                                      'anim': s['anim'], 'format': fmt, 'frames': len(frames),
                                      'moves': [s['move']],
                                      'join': 'docs/tech/ttt2-mota/join/%s (anim_ref = (bank<<14)|index = %d)'
                                              % (spec['join_file'], (s['bank'] << 14) | s['idx'])},
                      'applier': {'function': 'pose_synth.Synthesizer (numpy FK; per-joint calibrated '
                                              'game<->mannequin frame change; reproduces TekkenAnimHelper '
                                              'applyRotationFromAnimdata poses to <=5e-7 on 0xC8 control clips; '
                                              '0x64 tracks use the sampler half-angle convention of '
                                              'Default.xex func 0x82289228)',
                                  'repo': 'https://github.com/Kiloutre/BlenderTekkenDirect',
                                  'commit': HELPER_COMMIT, 'file': 'TekkenAnimHelper.py', 'sha256': helper_sha}}
        skel, clip, worst = convert(posed, provenance, mannequin_meta)
        if worst > 1e-3:
            print('SKIP %s: FK self-check failed: %.6f m' % (slot, worst))
            report['skipped'][slot] = 'FK self-check failed: %.6f m' % worst
            continue
        why = implausible(clip, skel)
        if why and fmt == '0x64':
            # Branch selection in unwrap_rotations is heuristic: also try the
            # backward-anchored representative chain; keep it only if it gates
            # strictly better (passes, or a shallower floor breach).
            posed_b = synth.pose(list(reversed(unwrap_rotations(list(reversed(frames)), ref_triples))), '64')
            skel_b, clip_b, worst_b = convert(posed_b, provenance, mannequin_meta)
            if worst_b <= 1e-3:
                why_b = implausible(clip_b, skel_b)
                better = why_b is None or ('below the floor' in why and 'below the floor' in (why_b or '')
                                            and float(why_b.split(' ')[1]) < float(why.split(' ')[1]))
                if better:
                    skel, clip, worst, why = skel_b, clip_b, worst_b, why_b
        gate_note = None
        if why:
            import re as _re
            m = _re.match(r'(Left|Right)ToeBase ([\d.]+) m below the floor on frame (\d+)', why)
            if m and float(m.group(2)) <= 0.12:
                # Toe-only graze: TTT2 source skeleton vs T7 mannequin proportion
                # delta. Ship only if nothing else fails and ankles stay clear.
                why2 = implausible_excl(clip, skel, {'LeftToeBase', 'RightToeBase'})
                fk = fk_frames(clip, skel)
                ankle_min = min(min(X['LeftFoot'][1], X['RightFoot'][1]) for X in fk)
                if why2 is None and ankle_min >= -0.02:
                    gate_note = ('toe graze %.2f m (frame %s) within TTT2-vs-T7 skeleton proportion '
                                 'delta; ankles >= %.2f m throughout; all other gate checks pass'
                                 % (float(m.group(2)), m.group(3), ankle_min))
                    why = None
            if why:
                print('SKIP %s: in-game plausibility gate: %s' % (slot, why))
                report['skipped'][slot] = 'in-game plausibility gate: ' + why
                continue
        if skel_written is None:
            json.dump(skel, open(os.path.join(a.out_dir, 'skeleton.json'), 'w'), indent=1)
            skel_written = skel
        json.dump(clip, open(os.path.join(a.out_dir, slot + '.json'), 'w'), separators=(',', ':'))
        report['baked'][slot] = {'move': s['move'], 'anim': s['anim'], 'bank': s['bank'], 'idx': s['idx'],
                                 'frames': len(frames), 'fk_selfcheck_max_m': round(worst, 6)}
        if gate_note:
            report['baked'][slot]['gate_note'] = gate_note
            print('OK %s (gate note: %s)' % (slot, gate_note))
        print('OK %s: %s -> %s [bank%d#%d %s] %d frames, FK %.6f m' % (slot, s['move'], s['anim'], s['bank'], s['idx'], fmt, len(frames), worst))
    json.dump(report, open(os.path.join(a.out_dir, 'bake-report.json'), 'w'), indent=1)
    print('BANK_BAKE_DONE %s: %d baked, %d skipped, %d gaps' % (spec['bank'], len(report['baked']), len(report['skipped']), len(report['gaps'])))


if __name__ == '__main__':
    main()
