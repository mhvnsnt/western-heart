"""T8 join: WH unmapped move -> community T8 moveset export (Kiloutre/LukzB
TekkenMovesetExtractor JSON format), evidence-only. Mirrors the T7 join method:
(a) wavu movelist name+notation existence, (b) motbin cancel-graph chain search,
(c) fingerprint corroboration (startup+damage) between graph terminal and wavu row.
Cancel attachment: from move.cancel_idx scan cancels until the terminator entry
(command low32==0x8000 and high32==0), inclusive -- verified 100% on shaheen/king.
Cancel command decode per AliK3112 inputs.js: u64 = inputBits<<32 | directionBits.
Names de-anonymized via AliK3112 name_keys.json."""
import json, sys, collections
sys.path.insert(0, '/home/hatch/workspace/agent-ops/t7-clip-lane/worker-b/tools')
from join_engine import wh_input_canon, canon_notation, canon_step

NK = json.load(open('/tmp/t8src/alik/name_keys.json'))
DIRL = {1: 'd/b', 2: 'd', 3: 'd/f', 4: 'b', 5: 'n', 6: 'f', 7: 'u/b', 8: 'u', 9: 'u/f'}
BTNL = {0: '1', 1: '2', 2: '3', 3: '4', 4: 'H', 5: 'S', 6: 'R'}
DTAP = {0x8001: 'f', 0x8002: 'b', 0x8003: 'f', 0x8004: 'b', 0x8005: 'u', 0x8006: 'd'}

def buttons_str(bits, partial=False):
    bs = [BTNL[i] for i in range(7) if bits & (1 << i)]
    return ('|'.join(bs) if partial else '+'.join(bs)) if bs else ''

def dir_str(db):
    ds = [DIRL[i] for i in range(1, 10) if db & (1 << i)]
    return ds[0] if ds else ''

def step_str(direction, btns):
    if direction and direction != 'n':
        return canon_step(direction + ('+' + btns if btns else ''))
    return canon_step(btns) if btns else None

def decode_cancel_steps(c, data):
    """One cancel entry -> list of canonical steps it covers, or None."""
    cmd = c['command']
    ib, db = cmd >> 32, cmd & 0xffffffff
    if db == 0x8000:
        return None  # terminator / [AUTO]
    if db in DTAP:
        d = DTAP[db]
        b = buttons_str(ib & 0x7f, bool(ib & (1 << 29)))
        return [d, step_str('', b)] if b else [d, d]
    if 0x800f <= db <= 0x9000 and db - 0x800f < len(data['input_sequences']):
        seq = data['input_sequences'][db - 0x800f]
        out = []
        for e in data['input_extradata'][seq['extradata_idx']: seq['extradata_idx'] + seq['u2']]:
            d = dir_str(e['u1'])
            b = '' if (e['u2'] & (1 << 31)) else buttons_str(e['u2'] & 0x7f, bool(e['u2'] & (1 << 29)))
            s = step_str(d, b)
            if s and s != 'n':
                out.append(s)
        return out or None
    if db >= 0x8000:
        return None  # other specials (0x800e group end etc.)
    d = dir_str(db)
    b = buttons_str(ib & 0x7f, bool(ib & (1 << 29)))
    if ib & (1 << 31):
        b = ''
    s = step_str(d, b)
    return [s] if s and s != 'n' else None

def req_chain(data, idx, cap=8):
    reqs = data['requirements']
    out = []
    i = idx
    while i and i < len(reqs) and reqs[i]['req'] != 0 and len(out) < cap:
        out.append(reqs[i]['req'])
        i += 1
    return out

class T8Export:
    def __init__(self, path):
        if '.zip!' in path:
            import zipfile, io
            zp, member = path.split('.zip!', 1)
            with zipfile.ZipFile(zp + '.zip') as z:
                self.data = json.load(io.BytesIO(z.read(member)))
        else:
            self.data = json.load(open(path))
        d = self.data
        self.moves = d['moves']
        cancels = d['cancels']
        self.move_cancels = []
        for m in self.moves:
            lst = []
            idx = m['cancel_idx']
            if idx < len(cancels):
                n = 0
                while idx + n < len(cancels) and n < 300:
                    c = cancels[idx + n]
                    n += 1
                    lst.append(c)
                    if (c['command'] & 0xffffffff) == 0x8000 and (c['command'] >> 32) == 0:
                        break
            self.move_cancels.append(lst)
        self.edge_by_steps = collections.defaultdict(list)
        self.incoming = collections.defaultdict(list)
        seen = set()
        def add_edge(par, c):
            steps = decode_cancel_steps(c, d)
            if not steps:
                return
            t = c['move_id']
            if t >= 0x8000 or t >= len(self.moves):
                return
            key = (par, tuple(steps), t)
            if key in seen:
                return
            seen.add(key)
            self.edge_by_steps[tuple(steps)].append((par, t, c['requirement_idx']))
            self.incoming[t].append((par, tuple(steps)))
        for i, lst in enumerate(self.move_cancels):
            for c in lst:
                add_edge(i, c)
        self.n_group = 0
        for c in d['group_cancels']:
            before = len(seen)
            add_edge(-1, c)
            if len(seen) > before:
                self.n_group += 1

    def move_name(self, i):
        m = self.moves[i]
        return NK.get(str(m['name_key'])) or m.get('name')

    def anim_name(self, i):
        m = self.moves[i]
        return NK.get(str(m['anim_key']))

    def damage(self, i):
        m = self.moves[i]
        hci = m['hit_condition_idx']
        if hci < len(self.data['hit_conditions']):
            return self.data['hit_conditions'][hci]['damage']
        return None

    def find_paths(self, steps):
        if not steps:
            return {}
        steps = tuple(steps)
        def chunks_ending_at(pos):
            out = []
            for chunk, edges in self.edge_by_steps.items():
                if pos - len(chunk) >= 0 and tuple(steps[pos - len(chunk):pos]) == chunk:
                    out.append((chunk, edges))
            return out
        sys.setrecursionlimit(10000)
        def chains_to(node, pos, depth):
            if depth > 8:
                return []
            out = []
            for chunk, edges in chunks_ending_at(pos):
                for (par, tgt, req) in edges:
                    if tgt != node:
                        continue
                    npos = pos - len(chunk)
                    if npos == 0:
                        out.append(((par, chunk, tgt, req),))
                    else:
                        for pre in chains_to(par, npos, depth + 1):
                            out.append(pre + ((par, chunk, tgt, req),))
            return out
        cand = set()
        for chunk, edges in chunks_ending_at(len(steps)):
            for (par, tgt, req) in edges:
                cand.add(tgt)
        res = {}
        for t in cand:
            chs = chains_to(t, len(steps), 0)
            if chs:
                res[t] = chs[:20]
        return res

def norm_compact_dirs(s):
    import re
    s = re.sub(r'(?<![a-zA-Z])df(?=\+|,|$)', 'd/f', s)
    s = re.sub(r'(?<![a-zA-Z])db(?=\+|,|$)', 'd/b', s)
    s = re.sub(r'(?<![a-zA-Z])uf(?=\+|,|$)', 'u/f', s)
    s = re.sub(r'(?<![a-zA-Z])ub(?=\+|,|$)', 'u/b', s)
    return s

def load_wavu(char):
    rows = json.load(open(f'/tmp/t8src/wavu/{char}.json'))
    by_steps = {}
    for r in rows:
        _, steps = canon_notation(norm_compact_dirs(r['input']))
        if not steps:
            continue
        su = None
        try:
            su = int(str(r.get('startup', '')).lstrip('i').split('~')[0].split(',')[0])
        except Exception:
            pass
        dm = None
        try:
            dm = int(str(r.get('damage', '')).split(',')[0])
        except Exception:
            pass
        by_steps.setdefault(tuple(steps), []).append(
            {'id': r['id'], 'name': r.get('name'), 'startup': su, 'damage': dm})
    return by_steps

FIGHTERS = {
    'pantera':  ('king', '/tmp/t8src/t8_KING_v2.json', 'kaiutzi21-t8_KING_v2'),
    'phantom':  ('yoshimitsu', '/tmp/t8src/t8_YOSHIMITSU.json', 'kaiutzi21-t8_YOSHIMITSU'),
    'skull':    ('bryan', '/tmp/t8src/t8_BRYAN.json', 'kaiutzi21-t8_BRYAN'),
    'kinpo':    ('asuka', '/tmp/t8src/screw-6006.zip!TekkenMovesetExtractor/extracted_chars/t8_asukaEDIT/t8_ASUKA.json', 'tekkenmods-6006-t8_ASUKA'),
    'demonio':  ('jin', '/tmp/t8src/t8_JIN.json', 'kaiutzi21-t8_JIN'),
    'diablo':   ('heihachi', '/tmp/t8src/t8_HEIHACHI.json', 'kaiutzi21-t8_HEIHACHI'),
    'scimitar': ('shaheen', '/tmp/t8src/t8_SHAHEEN.json', 'kaiutzi21-t8_SHAHEEN'),
}

def run_fighter(wh):
    char, path, src = FIGHTERS[wh]
    ex = T8Export(path)
    wavu = load_wavu(char)
    mp = json.load(open(f'/home/hatch/workspace/agent-ops/t7-clip-lane/worker-b/{wh}-mapping.json'))
    targets = [m for m in mp['moves'] if m['status'] == 'unmapped']
    out = []
    stats = collections.Counter()
    for t in targets:
        prefixes, steps = wh_input_canon(t['wh_input'].replace('~', ','))
        rec = {'t7_id': t['t7_id'], 'wh_key': t.get('wh_key'), 'input': t['wh_input'],
               'wh_name': t.get('wh_name'),
               't7_reason': t['reason'], 'wh_prefixes': prefixes}
        wrows = wavu.get(tuple(steps), [])
        paths = ex.find_paths(steps)
        # attack-class terminals only: first_active_frame set (T7 lane's rule).
        # Exception: pure-motion notations (no button step, e.g. the crouch-dash
        # entry f,n,d,df) legitimately terminate at motion moves.
        motion_only = not any(any(ch.isdigit() for ch in s) for s in steps)
        paths = {tid: chs for tid, chs in paths.items()
                 if ex.moves[tid]['first_active_frame'] or motion_only}
        if not paths:
            rec['status'] = 'unmapped'
            rec['reason'] = 'in_t8_movelist_no_graph_path' if wrows else 'no_t8_evidence'
            if wrows:
                rec['wavu_rows'] = wrows
            stats['unmapped'] += 1
            out.append(rec)
            continue
        # fingerprint each terminal against wavu rows for this notation
        cands = []
        for tid, chains in paths.items():
            m = ex.moves[tid]
            su, dm = m['first_active_frame'] or None, ex.damage(tid)
            fp = any(w['startup'] == su and w['damage'] == dm for w in wrows)
            cands.append({'move': tid, 'name': ex.move_name(tid), 'anim': ex.anim_name(tid),
                          'startup': su, 'damage': dm, 'fingerprint_match': fp,
                          'n_chains': len(chains),
                          'chain_reqs': [req_chain(ex.data, ch[-1][3]) for ch in chains[:3]]})
        cands.sort(key=lambda c: (not c['fingerprint_match'], c['move']))
        best = cands[0]
        if wrows and not best['fingerprint_match']:
            rec['wavu_conflict'] = True
        rec['status'] = 'mapped'
        rec['grade'] = 'high' if best['fingerprint_match'] else 'medium'
        rec['t8_move_index'] = best['move']
        rec['t8_move_name'] = best['name']
        rec['t8_anim_name'] = best['anim']
        rec['startup'] = best['startup']
        rec['damage'] = best['damage']
        rec['source'] = src
        rec['evidence'] = (['wavu_fingerprint_match'] if best['fingerprint_match'] else []) + \
                          (['wavu_notation_exists'] if wrows else []) + ['export_cancel_graph_chain'] + \
                          (['graph_chain_motion_terminal'] if not best['startup'] else [])
        if len(cands) > 1:
            rec['alternates'] = cands[1:]
        if wrows:
            rec['wavu_rows'] = wrows
        stats['mapped_' + rec['grade']] += 1
        out.append(rec)
    return {'fighter': wh, 'base': char, 'source_export': src, 'targets': len(targets),
            'stats': dict(stats), 'records': out}

if __name__ == '__main__':
    wh = sys.argv[1]
    r = run_fighter(wh)
    import os
    os.makedirs('/tmp/t8src/join-out', exist_ok=True)
    json.dump(r, open(f'/tmp/t8src/join-out/{wh}-t8.json', 'w'), indent=1)
    print(wh, r['targets'], r['stats'])
