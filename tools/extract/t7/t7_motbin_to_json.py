#!/usr/bin/env python3
"""Convert a TEKKEN 7 tkdata mothead/bin/<code>mot.bin (moveset) to JSON.

usage: t7_motbin_to_json.py <code>mot.bin out.json [--fighter NAME]

Format (verified on leemot/bobmot/asamot, T7 v5.x tkdata):
  0x000 MovesetInfo header (TKMovesets Structs_t7.h layout): string offsets for
        name/creator/date/fulldate at 0x08..0x20, aliases 0x28..0x150
  0x150 MovesetTable: 19 x (u64 offset, u64 count); offsets relative to BASE
  BASE = 0x2E8: string pool, then the lists back to back
  Inside structs, list references are INDEXES into the target list (not offsets);
  name/anim-name fields are string-pool offsets.
Struct layouts follow Kiloutre/TKMovesets (GPL-3.0) Structs_t7.h; this file only
reads them. No game data is embedded here.
Output: {"meta", "moves":[...summary per move...], "raw": {every list, all fields}}
The "moves" summary mirrors the repo's frame-data-t7 shape (notation, hit_level,
startup, active, damage) so existing loaders can consume it.
"""
import sys, struct, json
BASE = 0x2E8
LISTS = ['reactions', 'requirements', 'hit_conditions', 'projectiles', 'pushbacks',
         'pushback_extradata', 'cancels', 'group_cancels', 'cancel_extradata',
         'extra_move_properties', 'move_start_props', 'move_end_props', 'moves',
         'voiceclips', 'input_sequences', 'inputs', 'parry_related', 'camera_data',
         'throw_cameras']
# (struct fmt, field names); sizes checked against table spacing at runtime
FMT = {
 'requirements': ('<II', ['condition', 'param']),
 'cancels': ('<IIQQIIIHH', ['direction', 'button', 'requirements_idx', 'extradata_idx',
             'detection_start', 'detection_end', 'starting_frame', 'move_id', 'cancel_option']),
 'cancel_extradata': ('<I', ['value']),
 'pushbacks': ('<HHIQ', ['duration', 'displacement', 'num_of_loops', 'extradata_idx']),
 'pushback_extradata': ('<H', ['value']),
 'hit_conditions': ('<QIIQ', ['requirements_idx', 'damage', 'unk_0xC', 'reactions_idx']),
 'reactions': ('<7Q6HII14H', ['front_pushback', 'backturned_pushback', 'left_side_pushback',
               'right_side_pushback', 'front_counterhit_pushback', 'downed_pushback', 'block_pushback',
               'front_direction', 'back_direction', 'left_side_direction', 'right_side_direction',
               'front_counterhit_direction', 'downed_direction', 'unk_0x44', 'unk_0x48',
               'vertical_pushback', 'standing_moveid', 'default_moveid', 'crouch_moveid',
               'counterhit_moveid', 'crouch_counterhit_moveid', 'left_side_moveid',
               'crouch_left_side_moveid', 'right_side_moveid', 'crouch_right_side_moveid',
               'backturned_moveid', 'crouch_backturned_moveid', 'block_moveid', 'crouch_block_moveid']),
 'extra_move_properties': ('<III', ['starting_frame', 'id', 'value']),
 'move_start_props': ('<QII', ['requirements_idx', 'extraprop', 'value']),
 'move_end_props': ('<QII', ['requirements_idx', 'extraprop', 'value']),
 'voiceclips': ('<I', ['id']),
 'input_sequences': ('<HHIQ', ['input_window_frames', 'input_amount', 'unk_0x4', 'input_idx']),
 'inputs': ('<II', ['direction', 'button']),
 'moves': ('<QQQIIQQiiQiIQIHhHHhhQiIIIQQQQiIIIhHi',
           ['name', 'anim_name', 'anim_id', 'vuln', 'hitlevel', 'cancel_idx', 'cancel2_idx',
            'u_0x30', 'u_0x34', 'cancel3_idx', 'u_0x40', 'u_0x44', 'cancel4_idx', 'u_0x50',
            'transition', 'u_0x56', 'moveId_val1', 'moveId_val2', 'u_0x5C', 'u_0x5E',
            'hit_condition_idx', 'anim_len', 'airborne_start', 'airborne_end', 'ground_fall',
            'voiceclip_idx', 'extra_prop_idx', 'start_prop_idx', 'end_prop_idx', 'u_0x98',
            'hitbox_location', 'first_active_frame', 'last_active_frame', 'u_0xA8', 'distance', 'u_0xAC']),
}
DIRS = {0x2: 'd/b', 0x4: 'd', 0x8: 'd/f', 0x10: 'b', 0x20: 'n', 0x40: 'f', 0x80: 'u/b', 0x100: 'u', 0x200: 'u/f'}
NULL = 0xFFFFFFFFFFFFFFFF  # index fields: all-ones = none

def notation(direc, btn):
    d = '/'.join(v for k, v in DIRS.items() if direc & k) if direc < 0x400 else f'0x{direc:x}'
    b = '+'.join(str(i + 1) for i in range(4) if btn & (1 << i))
    if btn & 0x10: b = (b + '+' if b else '') + 'tag'
    return '+'.join(x for x in (d if d and d != 'n' else '', b) if x)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    fighter = sys.argv[sys.argv.index('--fighter') + 1] if '--fighter' in sys.argv else None
    d = open(src, 'rb').read()
    def s(o):
        o += BASE; return d[o:d.index(b'\0', o)].decode('latin1')
    tab = [struct.unpack_from('<QQ', d, 0x150 + 16 * i) for i in range(len(LISTS))]
    raw, sizes = {}, {}
    for i, (nm, (off, cnt)) in enumerate(zip(LISTS, tab)):
        nxt = sorted(o for o, c in tab if o > off)
        span = (nxt[0] if nxt else len(d) - BASE) - off
        if nm not in FMT or cnt == 0:
            sizes[nm] = span // cnt if cnt else 0
            raw[nm] = {'count': cnt, 'offset': off, 'bytes_hex': d[BASE + off:BASE + off + span].hex() if cnt and span < 1 << 20 else None}
            continue
        f, names = FMT[nm]; sz = struct.calcsize(f)
        stride = span // cnt
        assert stride >= sz, (nm, stride, sz)
        sizes[nm] = stride
        raw[nm] = [dict(zip(names, struct.unpack_from(f, d, BASE + off + k * stride))) for k in range(cnt)]
    for m in raw['moves']:
        m['name'] = s(m['name']); m['anim_name'] = s(m['anim_name'])
    def cancels_from(idx):
        out = []
        while idx < len(raw['cancels']):
            c = raw['cancels'][idx]; out.append(c); idx += 1
            if c['direction'] == 0x8000 and c['button'] == 0: break  # list terminator
        return out
    moves = []
    for i, m in enumerate(raw['moves']):
        hc = raw['hit_conditions'][m['hit_condition_idx']] if m['hit_condition_idx'] < len(raw['hit_conditions']) else None
        moves.append({
            'id': i, 'name': m['name'], 'anim': m['anim_name'], 'anim_id': m['anim_id'],
            'hit_level_raw': m['hitlevel'], 'vuln_raw': m['vuln'],
            'startup': m['first_active_frame'] or None,
            'active_frames': [m['first_active_frame'], m['last_active_frame']] if m['first_active_frame'] else None,
            'total_frames': m['anim_len'] or None,  # 0 in file; filled from the anim at runtime
 'damage': hc['damage'] if hc else None,
            'airborne': [m['airborne_start'], m['airborne_end']] if m['airborne_start'] else None,
            'transition': m['transition'], 'distance': m['distance'],
            'cancels': [{'input': notation(c['direction'], c['button']), 'direction_raw': c['direction'],
                         'button_raw': c['button'], 'move_id': c['move_id'],
                         'window': [c['detection_start'], c['detection_end']], 'starting_frame': c['starting_frame'],
                         'requirements_idx': c['requirements_idx'], 'option': c['cancel_option']}
                        for c in (cancels_from(m['cancel_idx']) if m['cancel_idx'] != NULL else [])],
        })
    meta = {'source': 'TEKKEN 7 tkdata.bin mothead/bin (owner Steam copy)', 'file': src.split('/')[-1],
            'fighter': fighter, 'character_name': s(struct.unpack_from('<Q', d, 8)[0]),
            'creator': s(struct.unpack_from('<Q', d, 16)[0]), 'date': s(struct.unpack_from('<Q', d, 24)[0]),
            'fulldate': s(struct.unpack_from('<Q', d, 32)[0]),
            'counts': {n: c for n, (o, c) in zip(LISTS, tab)}, 'strides': sizes,
            'schema': 'wh-t7-motbin-json/1', 'converter': 'western-heart tools/extract/t7/t7_motbin_to_json.py'}
    json.dump({'meta': meta, 'moves': moves, 'raw': raw}, open(dst, 'w'), separators=(',', ':'))
    print(meta['character_name'], len(moves), 'moves', sum(len(m['cancels']) for m in moves), 'cancel refs')

if __name__ == '__main__':
    main()
