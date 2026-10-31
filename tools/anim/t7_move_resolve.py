#!/usr/bin/env python3
"""t7_move_resolve.py: map a Western Heart moveset's Tekken 7 moves to the base character's REAL T7 motbin moves
(and the clips they play), by the game's own cancel graph, verified by exact T7 frame data. Read-only.

Nothing is guessed. A moveset row maps to a motbin move only when BOTH hold:
  1. input path: the row's input, pressed from the neutral stance (<code>_sKAM00_), reaches that motbin move
     through the stance's cancel list, with group cancels expanded in place (cmd 0x800B -> group_cancels from index
     move_id, ending at cmd 0x800C);
  2. frame data: the motbin move's damage and first active frame equal the row's T7 frame data
     (t7_damage_raw's first value, t7_startup_frames).
Several matching cancels can lead to different moves (requirement-gated variants, e.g. rage or story versions).
A row maps only if every candidate passing both checks plays the same clip; otherwise it is reported ambiguous and
keeps its current animation.

Scope v1: single-input rows from neutral (direction + buttons, e.g. b+2, d/f+1+2, 1+2, u/f+4). Strings, stance
prefixes (WS, FC, SS, BT, ...) and motion inputs (f,F; qcf) are reported as 'not single-input' for now.

Cancel command (u64): low 32 bits = direction mask (0x2 d/b, 0x4 d, 0x8 d/f, 0x10 b, 0x20 n, 0x40 f, 0x80 u/b,
0x100 u, 0x200 u/f; 0 = any; >= 0x8000 = special), high 32 bits = buttons (bit 0 = 1/LP, 1 = 2/RP, 2 = 3/LK,
3 = 4/RK; 0x40000000 = press flag). Bank rule for a move's clip: anim_id & 0xC000 -> 0x4000 <code>rotsm.arc,
0x8000 common.arc, 0x0000 <code>mot.bin (first MOTA block), index anim_id & 0x3FFF.

usage: python3 tools/anim/t7_move_resolve.py <GRE>/teardown/tekken7-steam/tkdata/mothead <code> \\
           game/assets/movesets/<fighter>.json [out.json]
"""
import json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import mota_anims  # noqa: E402

DIRS = {'d/b': 0x2, 'd': 0x4, 'd/f': 0x8, 'b': 0x10, 'f': 0x40, 'u/b': 0x80, 'u': 0x100, 'u/f': 0x200}
NEUTRAL = 0x20
GROUP_REF, GROUP_END = 0x800B, 0x800C
BANK = {0x4000: 'rotsm', 0x8000: 'common', 0x0000: 'motbin'}


def first_int(s):
    m = re.search(r'-?\d+', str(s if s is not None else ''))
    return int(m.group(0)) if m else None


def parse_single(inp):
    """'d/f+1+2' -> (0x8, 0b0011); '1+2' -> (NEUTRAL, 0b0011); None when not a single neutral-stance input."""
    s = str(inp or '').strip().lower().replace(' ', '')
    if not s or ',' in s or '(' in s or '~' in s or ':' in s or '*' in s or '_' in s:
        return None
    parts = s.split('+')
    d = NEUTRAL
    if parts[0] in DIRS:
        d = DIRS[parts.pop(0)]
    btn = 0
    for p in parts:
        if p not in ('1', '2', '3', '4'): return None
        btn |= 1 << (int(p) - 1)
    return (d, btn) if btn else None


class Motbin:
    def __init__(self, mothead, code):
        self.G, self.code = mothead.rstrip('/') + '/', code
        self.js = json.load(open(self.G + 'json/%s' % self._json_name()))
        self.moves = self.js['moves']
        gb = bytes.fromhex(self.js['raw']['group_cancels']['bytes_hex'])
        self.groups = [struct.unpack_from('<QQQIIIHH', gb, i * 40) for i in range(len(gb) // 40)]
        self._banks = {}

    def _json_name(self):
        for n in ('%smot.json' % self.code, '%s.json' % self.code):
            if os.path.exists(self.G + 'json/' + n): return n
        raise SystemExit('no motbin JSON for code %r under %sjson/' % (self.code, self.G))

    def stance(self):
        return next(m for m in self.moves if m['name'].endswith('_sKAM00_'))

    def expanded_cancels(self, move):
        """The move's cancel list in priority order, group cancels expanded in place: (dir, btn, move_id, req)."""
        out = []
        for c in move['cancels']:
            d, b = c['direction_raw'], c['button_raw']
            if d == GROUP_REF:
                j = c['move_id']
                while j < len(self.groups):
                    cmd, req, _ext, _ds, _de, _sf, mid, _opt = self.groups[j]
                    gd, gbt = cmd & 0xFFFFFFFF, cmd >> 32
                    if gd == GROUP_END: break
                    out.append((gd, gbt, mid, req))
                    j += 1
            elif d == 0x8000:
                break
            else:
                out.append((d, b, c['move_id'], c['requirements_idx']))
        return out

    def clip(self, move):
        aid = move['anim_id']
        sel = aid & 0xC000
        path = {0x4000: 'mask/%srotsm.arc' % self.code, 0x8000: 'mask/common.arc', 0x0000: 'bin/%smot.bin' % self.code}.get(sel)
        if not path: return {'bank': '?', 'clip': None, 'fmt': '?'}
        if path not in self._banks:
            b = open(self.G + path, 'rb').read(); m0 = re.search(b'MOTA', b).start()
            self._banks[path] = (b, m0, mota_anims(b, m0))
        b, m0, offs = self._banks[path]
        i = aid & 0x3FFF
        if i >= len(offs): return {'bank': BANK[sel], 'clip': i, 'fmt': 'out-of-range', 'file': path}
        o = m0 + offs[i]; t = b[o + 1] if b[o] == 0 else b[o]
        return {'bank': BANK[sel], 'clip': i, 'fmt': {0xC8: '0xC8', 0x64: '0x64'}.get(t, hex(t)), 'file': path}


def resolve(mb, moveset):
    st = mb.stance()
    cancels = mb.expanded_cancels(st)
    by_id = {m['id']: m for m in mb.moves}
    rows, stats = {}, {'t7_rows': 0, 'mapped': 0, 'mapped_0xC8': 0, 'ambiguous': 0, 'no_match': 0, 'not_single_input': 0}
    for key, row in moveset['moves'].items():
        if not isinstance(row, dict) or 't7_damage_raw' not in row: continue
        stats['t7_rows'] += 1
        inp = parse_single(row.get('t7_command') or row.get('input'))
        if inp is None:
            stats['not_single_input'] += 1; continue
        d, btn = inp
        dmg, su = first_int(row.get('t7_damage_raw')), first_int(row.get('t7_startup_frames'))
        path_hits = []
        for cd, cb, mid, req in cancels:
            if cd >= 0x8000 or mid >= 0x8000 or mid not in by_id: continue
            if (cb & 0xFF) != btn: continue
            if cd != 0 and not (cd & d): continue
            path_hits.append((mid, req))
        verified = []
        for mid, req in path_hits:
            m = by_id[mid]
            af = m.get('active_frames') or [None]
            if m.get('damage') == dmg and af[0] == su:
                verified.append((mid, req))
        anims = sorted({by_id[mid]['anim'] for mid, _ in verified})
        rec = {'input': row.get('input'), 't7_command': row.get('t7_command'), 'damage': dmg, 'startup': su,
               'path_candidates': len(path_hits), 'verified_candidates': [by_id[mid]['name'] for mid, _ in verified]}
        if len(anims) == 1:
            m = by_id[verified[0][0]]
            rec.update({'status': 'mapped', 'motbin_move': m['name'], 'motbin_id': m['id'], 'anim': m['anim'],
                        'active_frames': m.get('active_frames'), **mb.clip(m)})
            stats['mapped'] += 1; stats['mapped_0xC8'] += rec['fmt'] == '0xC8'
        elif len(anims) > 1:
            rec.update({'status': 'ambiguous', 'anims': anims}); stats['ambiguous'] += 1
        else:
            rec.update({'status': 'no_match'}); stats['no_match'] += 1
        rows[key] = rec
    return {'schema': 'wh-t7-move-resolve/1', 'code': mb.code, 'stance': st['name'], 'stance_cancels_expanded': len(cancels),
            'stats': stats, 'rows': rows}


def main():
    if len(sys.argv) < 4: raise SystemExit(__doc__)
    mb = Motbin(sys.argv[1], sys.argv[2])
    out = resolve(mb, json.load(open(sys.argv[3])))
    out['moveset'] = os.path.basename(sys.argv[3])
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], 'w'), indent=1)
    print(json.dumps(out['stats']))
    for k, r in out['rows'].items():
        if r['status'] == 'mapped':
            print('  %-16s %-10s -> %-20s %-28s %s#%s %s' % (k, r['input'], r['motbin_move'], r['anim'], r['bank'], r['clip'], r['fmt']))
    for k, r in out['rows'].items():
        if r['status'] != 'mapped':
            print('  %-16s %-10s %s %s' % (k, r['input'], r['status'], r.get('anims', r.get('verified_candidates'))))


if __name__ == '__main__':
    main()
