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

Scope v2 (--strings, 2026-11-10): STRING STEP rows, the T7 frame-data rows that isolate one hit of a string by
bracketing the hits before it: '(1), 2' is the 2 of 1,2; '(1), (2), 2+4' is the 2+4 of 1,2,2+4. Every step must be
a single input. The path walks the cancel graph: the bracketed prefix steps from the neutral stance through each
reached move's own expanded cancel list (every candidate is followed: prefix steps carry no frame data of their
own), then the final step must reach a move whose damage and first active frame equal the row's own T7 frame data,
exactly as in v1. Full-string rows ('1, 2' with several hits' data) and motion / stance rows stay unmapped.

Scope v3 (--motions, 2026-11-10): DASH and RUN rows, walked on King's own link tables, nothing timed by us:
  DASH  'f, F+X' / 'f, f, n, X' / '(f, F+X), Y': from the stance, the cancel whose command is 0x8001 (the
        engine's forward double tap; the same 0x8001 the stance uses for its dash_fwd slot, tools/anim/
        t7_generic_slots) reaches the dash move; 'F+X' is then the dash's own f+X cancel, 'n, X' its neutral X.
  RUN   'WR X' / 'WR+X' / 'f, f, f+X (or WR X)': the dash, then the dash's direction-only f cancel to a move other
        than itself (the run), then X from the run's own cancel list with f held.
The final move must pass the v1 frame-data check. Distance-gated rows ('(close)' / '(far)') and throws stay out.

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


def _step_hits(mb, by_id, cancels, d, btn):
    out = []
    for cd, cb, mid, req in cancels:
        if cd >= 0x8000 or mid >= 0x8000 or mid not in by_id: continue
        if (cb & 0xFF) != btn: continue
        if cd != 0 and not (cd & d): continue
        out.append(mid)
    return out


def parse_string_step(cmd):
    """'(1), (2), 2+4' -> [(NEUTRAL, 1), (NEUTRAL, 2)], (NEUTRAL, 0b1010); None unless every step is a single input,
    every step but the last is bracketed and the last is not."""
    steps = [x.strip() for x in str(cmd or '').split(',')]
    if len(steps) < 2: return None
    pre = []
    for x in steps[:-1]:
        m = re.fullmatch(r'\((.+)\)', x)
        if not m: return None
        p = parse_single(m.group(1))
        if p is None: return None
        pre.append(p)
    if steps[-1].startswith('('): return None
    last = parse_single(steps[-1])
    return (pre, last) if last else None


def resolve_strings(mb, moveset, rows, stats):
    by_id = {m['id']: m for m in mb.moves}
    cache = {}
    def cancels_of(mid):
        if mid not in cache: cache[mid] = mb.expanded_cancels(by_id[mid])
        return cache[mid]
    st = mb.stance()
    stats.update({'string_step_rows': 0, 'string_mapped': 0, 'string_ambiguous': 0, 'string_no_match': 0})
    for key, row in moveset['moves'].items():
        if not isinstance(row, dict) or 't7_damage_raw' not in row or key in rows: continue
        ps = parse_string_step(row.get('t7_command'))
        if ps is None: continue
        stats['string_step_rows'] += 1
        pre, (d, btn) = ps
        frontier, chain = [st['id']], []
        for pd, pb in pre:
            nxt = []
            for mid in frontier:
                for h in _step_hits(mb, by_id, cancels_of(mid), pd, pb):
                    if h not in nxt: nxt.append(h)
            frontier = nxt
            chain.append(sorted({by_id[m]['name'] for m in nxt}))
        dmg, su = first_int(row.get('t7_damage_raw')), first_int(row.get('t7_startup_frames'))
        path_hits, verified = [], []
        for mid in frontier:
            for h in _step_hits(mb, by_id, cancels_of(mid), d, btn):
                path_hits.append(h)
                m = by_id[h]; af = m.get('active_frames') or [None]
                if m.get('damage') == dmg and af[0] == su and h not in verified: verified.append(h)
        anims = sorted({by_id[h]['anim'] for h in verified})
        rec = {'input': row.get('input'), 't7_command': row.get('t7_command'), 'damage': dmg, 'startup': su,
               'kind': 'string_step', 'prefix_chain': chain, 'path_candidates': len(path_hits),
               'verified_candidates': [by_id[h]['name'] for h in verified]}
        if len(anims) == 1:
            m = by_id[verified[0]]
            rec.update({'status': 'mapped', 'motbin_move': m['name'], 'motbin_id': m['id'], 'anim': m['anim'],
                        'active_frames': m.get('active_frames'), **mb.clip(m)})
            stats['string_mapped'] += 1
        elif len(anims) > 1:
            rec.update({'status': 'ambiguous', 'anims': anims}); stats['string_ambiguous'] += 1
        else:
            rec.update({'status': 'no_match'}); stats['string_no_match'] += 1
        rows[key] = rec


DASH_CMD = 0x8001


def _motion_hits(mb, by_id, cancels, kind):
    out = []
    for cd, cb, mid, req in cancels:
        if mid >= 0x8000 or mid not in by_id or (cb & 0xFF): continue
        if kind == 'dash' and cd == DASH_CMD: out.append(mid)
        if kind == 'run' and cd == DIRS['f']: out.append(mid)
    return out


def parse_motion(cmd):
    """-> (prefix tokens, final (dir, btn)); tokens: 'dash' | 'run' | (dir, btn). None for anything else."""
    c = re.sub(r'\s+', ' ', str(cmd or '')).strip()
    m = re.fullmatch(r'f, f, f\+([1-4](?:\+[1-4])*) \(or WR ([1-4](?:\+[1-4])*)\)', c)
    if m and m.group(1) == m.group(2): c = 'WR ' + m.group(1)
    m = re.fullmatch(r'WR ?\+?([1-4](?:\+[1-4])*)', c)
    if m:
        p = parse_single(m.group(1)); return (['dash', 'run'], (DIRS['f'], p[1])) if p else None
    m = re.fullmatch(r'f, F\+([1-4](?:\+[1-4])*)', c)
    if m:
        p = parse_single(m.group(1)); return (['dash'], (DIRS['f'], p[1])) if p else None
    m = re.fullmatch(r'f, f, n, ([1-4](?:\+[1-4])*)', c)
    if m:
        p = parse_single(m.group(1)); return (['dash'], (NEUTRAL, p[1])) if p else None
    m = re.fullmatch(r'\(f, F\+([1-4](?:\+[1-4])*)\), (.+)', c)
    if m:
        a, b = parse_single(m.group(1)), parse_single(m.group(2))
        return (['dash', (DIRS['f'], a[1])], b) if a and b else None
    return None


def resolve_motions(mb, moveset, rows, stats):
    by_id = {m['id']: m for m in mb.moves}
    cache = {}
    def cancels_of(mid):
        if mid not in cache: cache[mid] = mb.expanded_cancels(by_id[mid])
        return cache[mid]
    st = mb.stance()
    stats.update({'motion_rows': 0, 'motion_mapped': 0, 'motion_ambiguous': 0, 'motion_no_match': 0})
    for key, row in moveset['moves'].items():
        if not isinstance(row, dict) or 't7_damage_raw' not in row or key in rows: continue
        pm = parse_motion(row.get('t7_command'))
        if pm is None: continue
        stats['motion_rows'] += 1
        pre, (d, btn) = pm
        frontier, chain = [st['id']], []
        for tok in pre:
            nxt = []
            for mid in frontier:
                if tok in ('dash', 'run'):
                    hs = [h for h in _motion_hits(mb, by_id, cancels_of(mid), tok) if tok == 'dash' or h != mid]
                else:
                    hs = _step_hits(mb, by_id, cancels_of(mid), tok[0], tok[1])
                for h in hs:
                    if h not in nxt: nxt.append(h)
            frontier = nxt
            chain.append(sorted({by_id[m]['name'] for m in nxt}))
        dmg, su = first_int(row.get('t7_damage_raw')), first_int(row.get('t7_startup_frames'))
        path_hits, verified = [], []
        for mid in frontier:
            for h in _step_hits(mb, by_id, cancels_of(mid), d, btn):
                path_hits.append(h)
                m = by_id[h]; af = m.get('active_frames') or [None]
                if dmg is not None and m.get('damage') == dmg and af[0] == su and h not in verified: verified.append(h)
        anims = sorted({by_id[h]['anim'] for h in verified})
        rec = {'input': row.get('input'), 't7_command': row.get('t7_command'), 'damage': dmg, 'startup': su,
               'kind': 'motion', 'prefix_chain': chain, 'path_candidates': len(path_hits),
               'path_moves': sorted({by_id[h]['name'] for h in path_hits}),
               'verified_candidates': [by_id[h]['name'] for h in verified]}
        if len(anims) == 1:
            m = by_id[verified[0]]
            rec.update({'status': 'mapped', 'motbin_move': m['name'], 'motbin_id': m['id'], 'anim': m['anim'],
                        'active_frames': m.get('active_frames'), **mb.clip(m)})
            stats['motion_mapped'] += 1
        elif len(anims) > 1:
            rec.update({'status': 'ambiguous', 'anims': anims}); stats['motion_ambiguous'] += 1
        else:
            rec.update({'status': 'no_match'}); stats['motion_no_match'] += 1
        rows[key] = rec


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
    strings = '--strings' in sys.argv
    if strings: sys.argv.remove('--strings')
    motions = '--motions' in sys.argv
    if motions: sys.argv.remove('--motions')
    mb = Motbin(sys.argv[1], sys.argv[2])
    ms = json.load(open(sys.argv[3]))
    out = resolve(mb, ms)
    if strings: resolve_strings(mb, ms, out['rows'], out['stats'])
    if motions: resolve_motions(mb, ms, out['rows'], out['stats'])
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
