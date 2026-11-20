#!/usr/bin/env python3
"""Decode Tekken 5 Devil Within gym motion files (.dat) into per-joint keyframe curves.

KEYFRAME FORMAT — cracked 2026-11-08 (see DW-DECODE-LOG.md §keyframe):
  header (16 x u16 LE @0): [1]=bones, [2]=frames, [3]=frame0_size (bytes),
      [5]=16528 const, [7]=STEP FLAG (8192 = keyframes every 2nd frame,
      0 = every frame), [10]=bones*128, [12]=field12 (frames*bones*12 for
      standard clips; smaller for 19 sparse clips — layout unaffected),
      [14]=68 (35-bone) / 180 (init_obj) / 15 (djin).
  sub-header @32 (4 x u32): record_table_off (=72), bone_table_off,
      data_off, field3 (again). Magic GYM1 @64.
  record table @72, 16 bytes/bone: channel pair, type (low byte = channel
      kind: 3=scale 3xfloat32, 7=rotation 3xi16, 11=position 3xfloat32 mm;
      high byte = flag), index (records pair up), cumulative data offset
      (x2, identical) WITHIN one frame block.
  bone table @bone_off: u16 hierarchy paths separated by 0xFFFF, terminated
      by 0xFFFE + 0xFFFF.
  data @data_off: n_kf FULL frame blocks of frame0_size bytes + zero trailer
      (0-12 bytes). n_kf = frames if step==1 else frames//2+1.
      Keyframe k is at frame k*step; for step-2 clips the last keyframe
      index is 2*(n_kf-1) (equals the header frame count when even).
  rotation decode: angles = i16 * pi/32768 rad (i16 * 180/32768 deg),
      R = Ry(t0) * Rx(t1) * Rz(t2) (file triple order). Validated: a stance
      clip decodes to max 0.95 deg change per keyframe step across all 24
      rotation bones x 75 steps (wrong conventions give 138-177 deg jumps);
      a fast transform clip decodes to a smooth ease-in/peak/ease-out arc
      (3.4-26.7 deg/keyframe step, no jumps). The convention is determined
      up to a global axis relabeling; positions are Y-up (bone1 height
      ~1011 mm on Y), which supports t0=yaw, t1=pitch, t2=roll.
  position decode: 3 x float32, millimetres, absolute, Y-up.
  scale decode: 3 x float32, near 1.0.

Output: dw-motion-curves.json — per DW clip, per bone, per keyframe values.
Rotations stored as Euler degrees in FILE order (t0,t1,t2) with the
convention above; the consumer applies R = Ry(t0)*Rx(t1)*Rz(t2).
Positions in mm, scales unitless. Keyframe frame indices included.

Usage: python3 gym_keyframes.py <romd_out_dir> <dw-motion-index.json> <out.json>
"""
import json, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))  # gym_parse.py sits beside this tool
from gym_parse import KIT, INIT_OBJ, DW_SINGLES

DEG = 180.0 / 32768.0

def parse_gym_full(path):
    d = path.read_bytes()
    h = struct.unpack_from('<16H', d, 0)
    bones, frames, field3, field12 = h[1], h[2], h[3], h[12]
    step_flag = h[7]
    step = 1 if step_flag == 0 else 2
    sub = struct.unpack_from('<4I', d, 32)
    rec_off, bone_off, data_off = sub[0], sub[1], sub[2]
    recs = []
    for i in range(bones):
        r = struct.unpack_from('<8H', d, rec_off + i * 16)
        off = r[4] | (r[5] << 16)
        recs.append({'bone': i, 'type_low': r[2] & 0xFF,
                     'type_high': (r[2] >> 8) & 0xFF, 'index': r[3],
                     'offset': off})
    sizes = []
    for i, r in enumerate(recs):
        n = (recs[i + 1]['offset'] - r['offset']) if i + 1 < len(recs) \
            else (12 if r['type_low'] in (3, 11) else 6)
        sizes.append(n)
    frame0_size = recs[-1]['offset'] + sizes[-1] if recs else 0
    bt = list(struct.unpack_from(f'<{(data_off - bone_off) // 2}H', d, bone_off)) \
        if data_off > bone_off else []
    chains = []
    cur = []
    for v in bt:
        if v == 0xFFFF:
            if cur:
                chains.append(cur)
                cur = []
        elif v == 0xFFFE:
            if cur:
                chains.append(cur)
                cur = []
            break
        else:
            cur.append(v)
    if cur:
        chains.append(cur)
    data = d[data_off:]
    n_kf = frames if step == 1 else frames // 2 + 1
    # Keyframe k is at frame k*step. For step-2 clips the last keyframe index
    # is 2*(n_kf-1), which equals the header frame count when the count is
    # even (the header count is the last frame index / interval count, not
    # the point count). Evidence: on cyclic step-2 clips (walk/run) the last
    # keyframe step is ~0.7-0.9x the median step, i.e. a full 2-frame
    # interval, not a 1-frame interval (~0.5x). Do NOT force it to frames-1.
    kf_frames = [k * step for k in range(n_kf)]
    return {
        'bones': bones, 'frames': frames, 'field3': field3, 'field12': field12,
        'step_flag': step_flag, 'step': step, 'frame0_size': frame0_size,
        'record_table_off': rec_off, 'bone_table_off': bone_off,
        'data_off': data_off, 'n_keyframes': n_kf, 'keyframe_frames': kf_frames,
        'chains': chains, 'recs': recs, 'sizes': sizes, 'data': data,
        'trailer_bytes': len(data) - n_kf * frame0_size,
    }

def decode_clip(path):
    p = parse_gym_full(path)
    data, f0sz = p['data'], p['frame0_size']
    bones_out = []
    for r, n in zip(p['recs'], p['sizes']):
        keys = []
        for k in range(p['n_keyframes']):
            base = k * f0sz + r['offset']
            chunk = data[base:base + n]
            if r['type_low'] in (3, 11) and len(chunk) == 12:
                vals = [round(v, 3) for v in struct.unpack('<3f', chunk)]
                keys.append(vals)
            elif r['type_low'] == 7 and len(chunk) == 6:
                i16 = struct.unpack('<3h', chunk)
                keys.append([round(v * DEG, 2) for v in i16])
            else:
                keys.append(None)
        chan = {3: 'scale', 7: 'rotation_deg', 11: 'position_mm'}.get(r['type_low'], 'unknown')
        bones_out.append({'bone': r['bone'], 'channel': chan, 'keys': keys})
    return p, bones_out

def main():
    out_dir, index_path, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    idx = json.loads(index_path.read_text())
    clips = []
    problems = []
    for group in idx['groups']:
        gid = group['id']
        for f in group['files']:
            name = f['name']
            if not name.startswith('gym_'):
                continue
            pth = out_dir / name
            if gid == 'init_obj':
                kit_id, kit_name, role = INIT_OBJ.get(
                    name, ('unassigned', 'TK kit — unassigned', 'UNMEASURED'))
            elif gid == 'dw_singles':
                kit_id, kit_name, role = DW_SINGLES.get(
                    name, ('unassigned', 'unassigned', 'UNMEASURED'))
            else:
                kit_id, kit_name, role = KIT.get(
                    gid, ('unassigned', 'unassigned kit', 'UNMEASURED'))
            entry = {'source_file': name, 'group': gid,
                     'canon_kit_id': kit_id, 'canon_kit': kit_name}
            if not pth.exists():
                entry['status'] = 'MISSING — no file data in TK5DATA2'
                clips.append(entry)
                continue
            try:
                p, bones_out = decode_clip(pth)
                n_none = sum(1 for b in bones_out for k in b['keys'] if k is None)
                trail = p['data'][p['n_keyframes'] * p['frame0_size']:]
                entry.update({
                    'status': 'decoded',
                    'frames': p['frames'], 'step': p['step'],
                    'n_keyframes': p['n_keyframes'],
                    'keyframe_frames': p['keyframe_frames'],
                    'bones': p['bones'], 'frame0_size': p['frame0_size'],
                    'trailer_bytes': p['trailer_bytes'],
                    'trailer_all_zero': all(b == 0 for b in trail),
                    'none_keys': n_none,
                    'chains': p['chains'],
                    'curves': bones_out,
                })
                if n_none or not all(b == 0 for b in trail):
                    problems.append(name)
            except Exception as e:
                entry['status'] = f'DECODE ERROR: {e}'
                problems.append(name)
            clips.append(entry)
    out = {
        'format': 'western-heart dw-motion-curves v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'decode': ('Per-joint keyframe curves. Rotation: Euler degrees in file order '
                   '(t0,t1,t2), R = Ry(t0)*Rx(t1)*Rz(t2), angles = i16 * 180/32768. '
                   'Position: mm, absolute, Y-up. Scale: unitless, near 1.0. '
                   'Keyframes every 2nd frame (step flag 8192) or every frame '
                   '(step flag 0); keyframe k is at frame k*step. '
                   'Convention determined up to a global axis relabeling; see '
                   'DW-DECODE-LOG.md keyframe section for the validation.'),
        'clips_total': len(clips),
        'clips_decoded': sum(1 for c in clips if c.get('status') == 'decoded'),
        'clips_missing': sum(1 for c in clips if c.get('status', '').startswith('MISSING')),
        'problems': problems,
        'clips': clips,
    }
    out_path.write_text(json.dumps(out, separators=(',', ':')))
    print(f"clips={len(clips)} decoded={out['clips_decoded']} missing={out['clips_missing']} problems={problems}")
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == '__main__':
    main()
