#!/usr/bin/env python3
"""LANE 3 — Moveset wiring: extract per-fighter Tekken movelists from real T3 teardown data.

Reads teardown/tekken3/movesets/moveset_{king,jin,bryan,heihachi,xiaoyu,yoshimitsu,gunjack}.json
(real decoded T3 motion-bank data: 652 King rows etc., branch commands decoded per n0madic moves.md)
and builds one moveset JSON per Western Heart fighter:

  game/assets/movesets/{fighter_id}.json

Each moveset: basic attacks keyed by Tekken notation (1/2/3/4), throws (1+3, 2+4),
directional attacks (f+1, d/f+2...), strings (1,2 / 2,1 ...), specials (qcf+2 ...).
Frame data: 60fps T3 -> seconds. Damage scaled T3 170HP -> WH 100HP (existing convention).

Provenance is kept on every move (t3_source, t3_row, t3_command) so nothing is invented.
"""
import json, os, re, sys
from collections import defaultdict

T3DIR = os.path.expanduser('~/workspace/wh-lane3-movesets/_lane3/t3')
OUTDIR = os.path.expanduser('~/workspace/wh-lane3-movesets/game/assets/movesets')

SOURCES = ['king', 'jin', 'bryan', 'heihachi', 'xiaoyu', 'yoshimitsu', 'gunjack']

# ---------------- Tekken notation ----------------
DIRMAP = {'1': 'd/b', '2': 'd', '3': 'd/f', '4': 'b', '5': 'n',
          '6': 'f', '7': 'u/b', '8': 'u', '9': 'u/f'}
BTNM = {'LP': '1', 'RP': '2', 'LK': '3', 'RK': '4'}

def parse_command(cmd):
    """T3 decoded command string -> Tekken notation (or None if not an attack input)."""
    if not cmd or cmd in ('any-button',):
        return None
    # chord with direction: "6+LP", "1/2+RP+LK"
    m = re.fullmatch(r'([1-9](?:/[1-9])?)\+((?:LP|RP|LK|RK)(?:\+(?:LP|RP|LK|RK))*)', cmd)
    if m:
        dirs, btns = m.group(1), m.group(2)
        b = '+'.join(BTNM[x] for x in btns.split('+'))
        if '/' in dirs:
            d = '/'.join(DIRMAP[x] for x in dirs.split('/'))
        else:
            d = DIRMAP[dirs]
        if d == 'n':
            return b
        return f'{d}+{b}'
    # plain buttons / chords: "LP", "LP+LK"
    m = re.fullmatch(r'((?:LP|RP|LK|RK)(?:\+(?:LP|RP|LK|RK))*)', cmd)
    if m:
        return '+'.join(BTNM[x] for x in m.group(1).split('+'))
    # motion: "[6 5 4 1 2 6+LP](30f)"
    m = re.fullmatch(r'\[([1-9 ]+)(?:\+((?:LP|RP|LK|RK)(?:\+(?:LP|RP|LK|RK))*))?\]\((\d+)f\)', cmd)
    if m:
        seq = m.group(1).split()
        btns = m.group(2)
        b = '+' + '+'.join(BTNM[x] for x in btns.split('+')) if btns else ''
        seqn = [DIRMAP[s] for s in seq]
        # common shorthand
        s = seq
        if s == ['2', '3', '6']:
            motion = 'qcf'
        elif s == ['2', '1', '4']:
            motion = 'qcb'
        elif s == ['4', '1', '2', '3', '6']:
            motion = 'hcf'
        elif s == ['6', '3', '2', '1', '4']:
            motion = 'hcb'
        elif len(s) == 2 and s[0] == s[1] and s[0] in ('6', '4', '2', '8', '3', '1'):
            d = DIRMAP[s[0]]
            motion = {'f': 'f,F', 'b': 'b,B', 'd': 'd,D', 'u': 'u,U',
                      'd/f': 'd/f,D/F', 'd/b': 'd/b,D/B'}[d]
        elif s == ['6', '5', '6']:
            motion = 'f,n,f'
        else:
            motion = ','.join(seqn)
        return f'{motion}{b}'
    if 'any-button' in cmd:
        # "6+any-button" = while-running etc.
        m2 = re.fullmatch(r'([1-9](?:/[1-9])?)\+any-button', cmd)
        if m2:
            d = m2.group(1)
            d = '/'.join(DIRMAP[x] for x in d.split('/'))
            return {'f': 'f,F', 'd/f': 'ws', 'd': 'fc'}.get(d, d) + ',any'
        return None
    return None

# ---------------- load T3 ----------------
def load_source(name):
    d = json.load(open(f'{T3DIR}/moveset_{name}.json'))
    moves = d['moves']
    mi = d['move_index']
    def slot_to_row(slot):
        if 0 <= slot < len(mi):
            r = mi[slot]
            if isinstance(r, int) and 0 <= r < len(moves):
                return r
        return None
    # index: notation -> list of (src_row, dst_row)
    by_notation = defaultdict(list)
    for m in moves:
        src = m['row']
        for b in m.get('branches', []):
            if not b.get('entry'):
                continue
            n = parse_command(b.get('command', ''))
            if not n:
                continue
            dst = slot_to_row(b['target_slot'])
            if dst is None:
                continue
            by_notation[n].append((src, dst))
    return {'name': name, 'moves': moves, 'by_notation': by_notation}

def throw_damage(m):
    for e in m.get('events', []) or []:
        if isinstance(e, dict):
            for k in ('damage', 'dmg', 'power'):
                if k in e and isinstance(e[k], (int, float)) and e[k] > 0:
                    return int(e[k])
    return 35  # WH grappler-throw convention (documented as estimated)

def framedata(m, is_throw=False):
    af, al, sf = m['active_first'], m['active_last'], m['stream_frames']
    startup = max(0.05, af / 60.0)
    active = max(0.017, (al - af + 1) / 60.0)
    recovery = max(0.1, (sf - al) / 60.0)
    dmg = throw_damage(m) if is_throw else m['damage']
    damage = max(1, round(dmg * 100.0 / 170.0))
    return {'startup': round(startup, 3), 'active': round(active, 3),
            'recovery': round(recovery, 3), 'damage': damage,
            't3_damage': dmg}

def is_strike(m):
    return m['active_first'] > 0 and m['damage'] > 0 and m['stream_frames'] > 0

def is_throwmove(m):
    return m.get('attack_class') == 1 and m['damage'] == 0 and m['active_first'] > 0

def pick(cands, src_moves, want='fast', dmg_target=None, prefer_neutral=True, skip_rows=()):
    scored = []
    for src, dst in cands:
        if dst in skip_rows:
            continue
        m = src_moves[dst]
        if not is_strike(m):
            continue
        score = 0
        if prefer_neutral and src <= 12:
            score += 50
        elif prefer_neutral and src <= 60:
            score += 20
        if want == 'fast':
            score += max(0, 30 - m['active_first'])
        if dmg_target:
            score += max(0, 20 - abs(m['damage'] - dmg_target))
        scored.append((score, m['active_first'], dst))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return scored[0][2]

def pick_throw(cands, src_moves, skip_rows=()):
    scored = []
    for src, dst in cands:
        if dst in skip_rows:
            continue
        m = src_moves[dst]
        if not is_throwmove(m):
            continue
        score = (50 if src <= 12 else 0) + max(0, 60 - m['stream_frames'])
        scored.append((score, dst))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][1]

LIMB = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}

def move_entry(fighter_display, src_name, notation, row, cmd, m, is_throw=False, string_of=None):
    fd = framedata(m, is_throw=is_throw)
    last_btn = notation.replace(',', '').replace('+', '')[-1:]
    limb = LIMB.get(last_btn, 'armR')
    heavy = fd['damage'] >= 15 or is_throw
    entry = {
        'name': f"{fighter_display} {notation}{' throw' if is_throw else ''} (T3 {src_name} r{row})",
        'input': notation,
        't3_source': src_name, 't3_row': row, 't3_command': cmd,
        'startup': fd['startup'], 'active': fd['active'], 'recovery': fd['recovery'],
        'damage': fd['damage'], 't3_damage': fd['t3_damage'],
        'limb': limb, 'heavy': heavy,
        'knock': 6.5 if is_throw else (4.2 if limb.startswith('leg') or heavy else 2.2),
        'soulGain': 11 if heavy else 8,
    }
    if is_throw:
        entry['throw'] = True
        entry['unblockable'] = True
        entry['isGrab'] = True
        entry['note'] = 'T3 bank stores 0 damage for throws; damage follows WH grappler convention'
    if string_of:
        entry['string_hit'] = string_of
    return entry

# ---------------- roster ----------------
# fighter_id: (DISPLAY, tekken_base, t3_source, proxy_note or None)
ROSTER = {
    'pantera':   ('PANTERA', 'King', 'king', None),
    'demonio':   ('DEMONIO', 'Jin Kazama', 'jin', None),
    'phantom':   ('PHANTOM', 'Yoshimitsu', 'yoshimitsu', None),
    'diablo':    ('DIABLO', 'Heihachi', 'heihachi', None),
    'skull':     ('SKULL', 'Bryan Fury', 'bryan', None),
    'samura1':   ('SAM-UR-A1', 'Gun Jack', 'gunjack', None),
    'sakura':    ('SAKU RA', 'Xiaoyu', 'xiaoyu', None),
    'rin':       ('RIN', 'Jin Kazama', 'jin', 'soul vessel; Jin T3 data'),
    'byou':      ('BYOU', 'Lei Wulong', 'jin', 'soul vessel; Lei has no T3 bank - Jin proxy'),
    'tou':       ('TOU', 'Paul Phoenix', 'heihachi', 'soul vessel; Paul has no T3 bank - Heihachi proxy'),
    'sha':       ('SHA', 'Xiaoyu', 'xiaoyu', 'soul vessel; Xiaoyu T3 data'),
    'kai':       ('KAI', 'Eddy Gordo', 'jin', 'soul vessel; Eddy has no T3 bank - Jin proxy'),
    'jin_soul':  ('JIN', 'Yoshimitsu', 'yoshimitsu', 'soul vessel; Yoshimitsu T3 data'),
    'retsu':     ('RETSU', 'Bryan Fury', 'bryan', 'soul vessel; Bryan T3 data'),
    'zen':       ('ZEN', 'Heihachi', 'heihachi', 'soul vessel; Heihachi T3 data'),
    'gyou':      ('GYOU', 'Hwoarang', 'jin', 'soul vessel; Hwoarang has no T3 bank - Jin proxy'),
    'zui':       ('ZUI', 'Steve Fox', 'jin', 'Steve has no T3 bank - Jin proxy (fast hands)'),
    'kinpo':     ('KINPO', 'Asuka', 'jin', 'Asuka has no T3 bank - Jin proxy (Kazama style)'),
    'waterfall': ('WATERFALL', 'Josie', 'jin', 'Josie has no T3 bank - Jin proxy'),
    'kingtyrant':('KING TYRANT', 'Eddy Gordo', 'xiaoyu', 'Eddy has no T3 bank - Xiaoyu proxy (flowy/evasive)'),
    'burger':    ('BURGER', 'Bob', 'bryan', 'Bob has no T3 bank - Bryan proxy (power)'),
    'awapop':    ('AWA POP', 'Nina', 'jin', 'Nina has no T3 bank - Jin proxy'),
    'scimitar':  ('SCIMITAR', 'Shaheen', 'jin', 'Shaheen has no T3 bank - Jin proxy'),
    'purplerain':('PURPLE RAIN', 'Lee', 'jin', 'Lee has no T3 bank - Jin proxy'),
    'nightwolf': ('NIGHTWOLF', 'Julia', 'xiaoyu', 'Julia has no T3 bank - Xiaoyu proxy'),
    'dio':       ('DIO', 'Akuma', 'heihachi', 'Akuma has no T3 bank - Heihachi proxy (power shoto)'),
    'cyborgx':   ('CYBORG X', 'Alisa', 'gunjack', 'Alisa has no T3 bank - Gun Jack proxy (machine)'),
    'michiko':   ('MICHIKO', 'Katarina', 'jin', 'Katarina has no T3 bank - Jin proxy'),
    'star':      ('STAR', 'Christie', 'xiaoyu', 'Christie has no T3 bank - Xiaoyu proxy (capoeira flow)'),
    'torch':     ('TORCH', 'Anna', 'jin', 'Anna has no T3 bank - Jin proxy'),
    'bruno':     ('BRUNO', 'Miguel', 'bryan', 'Miguel has no T3 bank - Bryan proxy (brawler)'),
    'negativo':  ('N3GΔTIV0', 'Negan', 'bryan', 'Negan has no T3 bank - Bryan proxy (intimidation)'),
    'thor':      ('THOR', 'Ganryu', 'bryan', 'Ganryu has no T3 bank - Bryan proxy (sumo power)'),
    'yukihyo':   ('YUKIHYŌ', 'Armor King', 'king', 'Armor King has no T3 bank - King proxy (grappler)'),
    'slice':     ('SLICE', 'Dragunov', 'bryan', 'Dragunov has no T3 bank - Bryan proxy (commando)'),
    'docfrank':  ('DOC FRANK', 'Bosconovitch', 'gunjack', 'Bosconovitch has no T3 bank - Gun Jack proxy'),
    'sunra':     ('SUN RĀ', 'Pac-Man', 'heihachi', 'boss; Pac-Man has no bank - Heihachi proxy (boss power)'),
    'dxmmii':    ('DXMMII', 'Mokujin', 'jin', 'Mokujin mimic - Jin proxy default'),
    'realizzt':  ('REALIZZT', 'Brad Burns', 'jin', 'Brad Burns (VF5) has no T3 bank - Jin proxy (hands)'),
    'rave':      ('RAVE', 'Lei Wulong', 'xiaoyu', 'Lei has no T3 bank - Xiaoyu proxy (stance dance)'),
    'kutz':      ('KUTZ', 'Goh Hinogami', 'king', 'Goh (VF5) has no T3 bank - King proxy (judo/grappler)'),
    'chordz':    ('CHORDZ', 'Lars', 'jin', 'Lars has no T3 bank - Jin proxy (Mishima style)'),
    'vainabel':  ('VAIN ABEL ELIAS', 'Bass Armstrong', 'bryan', 'Bass (DOA4) - Bryan proxy frame data, real DOA4 move names'),
    'lili':      ('LILI', 'Lili', 'xiaoyu', 'Lili has no T3 bank - Xiaoyu proxy (graceful striker)'),
    'baek':      ('BAEK', 'Baek', 'bryan', 'Baek has no T3 bank - Bryan proxy (TKD kicks)'),
}

DMG_TARGET = {'1': 12, '2': 14, '3': 15, '4': 20}

def find_t3cmd(moves, byn, notation, src_row, dst_row):
    for b in moves[src_row].get('branches', []):
        if b.get('entry') and parse_command(b.get('command', '')) == notation:
            return b['command']
    return notation

def build_fighter(fid, disp, base, t3name, proxy_note, src, variant):
    moves = src['moves']
    byn = src['by_notation']
    out_moves = {}
    used_rows = set()
    strings = []
    specials = []

    # --- basic attacks 1/2/3/4 ---
    for btn in ['1', '2', '3', '4']:
        cands = byn.get(btn, [])
        dst_rows = sorted(set(d for s, d in cands if is_strike(moves[d])))
        row = None
        if dst_rows:
            neutral, other = [], []
            for dst in dst_rows:
                srcs = [s for s, d in cands if d == dst]
                (neutral if min(srcs) <= 12 else other).append(dst)
            pool = neutral or other
            pool.sort(key=lambda r: (moves[r]['active_first'], abs(moves[r]['damage'] - DMG_TARGET[btn])))
            row = pool[variant % len(pool)]
        if row is None:
            strikes = [i for i, m in enumerate(moves) if is_strike(m) and i not in used_rows]
            strikes.sort(key=lambda r: (moves[r]['active_first'], abs(moves[r]['damage'] - DMG_TARGET[btn])))
            row = strikes[0] if strikes else None
        if row is None:
            continue
        src_row = next((s for s, d in cands if d == row), 0)
        t3cmd = find_t3cmd(moves, byn, btn, src_row, row)
        out_moves[btn] = move_entry(disp, t3name, btn, row, t3cmd, moves[row])
        used_rows.add(row)

        # --- strings: follow-up button branches from this strike (up to 3 hits) ---
        seq = [btn]
        cur = row
        for _ in range(2):
            nxt = None
            for b in moves[cur].get('branches', []):
                if not b.get('entry'):
                    continue
                n = parse_command(b.get('command', ''))
                if n in ('1', '2', '3', '4'):
                    dst = next((d for s, d in byn.get(n, []) if s == cur), None)
                    if dst is not None and is_strike(moves[dst]) and dst not in used_rows:
                        nxt = (n, dst, b['command'])
                        break
            if not nxt:
                break
            n, dst, t3c = nxt
            seq.append(n)
            key = ','.join(seq)
            out_moves[key] = move_entry(disp, t3name, key, dst, t3c, moves[dst], string_of=','.join(seq[:-1]))
            strings.append({'input': key, 'hits': list(seq),
                            't3_rows': [out_moves[','.join(seq[:i + 1])]['t3_row'] for i in range(len(seq))]})
            used_rows.add(dst)
            cur = dst

    # --- throws 1+3 / 2+4 ---
    for notation, t3c in [('1+3', 'LP+LK'), ('2+4', 'RP+RK')]:
        cands = byn.get(t3c, [])
        row = pick_throw(cands, moves, skip_rows=used_rows)
        if row is None:
            allthrows = [i for i, m in enumerate(moves) if is_throwmove(m) and i not in used_rows]
            row = allthrows[variant % len(allthrows)] if allthrows else None
        if row is None:
            continue
        src_row = next((s for s, d in cands if d == row), 0)
        t3cmd = find_t3cmd(moves, byn, t3c, src_row, row)
        out_moves[notation] = move_entry(disp, t3name, notation, row, t3cmd, moves[row], is_throw=True)
        used_rows.add(row)

    # --- directional attacks (up to 2) ---
    got_dir = 0
    for notation in ['f+1', 'd/f+2', 'd+4', 'b+1', 'd/b+3', 'u/f+4']:
        cands = byn.get(notation, [])
        row = pick(cands, moves, want='fast', skip_rows=used_rows)
        if row is None:
            continue
        src_row = next((s for s, d in cands if d == row), 0)
        t3cmd = find_t3cmd(moves, byn, notation, src_row, row)
        out_moves[notation] = move_entry(disp, t3name, notation, row, t3cmd, moves[row])
        used_rows.add(row)
        got_dir += 1
        if got_dir >= 2:
            break

    # --- specials: motion inputs (King's chain throws, lunging strikes, ...).
    # Motion commands in the T3 banks target throws (chain throws) and strikes.
    # Rank: throws first (character-defining), then strikes by damage.
    speccands = []
    for n, clist in byn.items():
        # motion notations contain ',' (f,n,f / qcf etc.) or dash forms f,F / b,B
        if ',' not in n and 'F' not in n and 'B' not in n:
            continue
        if ',any' in n:  # stance transitions, not attacks
            continue
        btn = n.rsplit('+', 1)[-1] if '+' in n else ''
        if btn not in ('1', '2', '3', '4'):
            continue
        for s, d in clist:
            if d in used_rows:
                continue
            m = moves[d]
            if is_throwmove(m):
                speccands.append((1000, n, s, d, True))
            elif is_strike(m):
                speccands.append((m['damage'], n, s, d, False))
    speccands.sort(key=lambda x: (-x[0], x[1]))
    seen = set()
    for score, n, s, d, is_thr in speccands:
        if n in seen:
            continue
        seen.add(n)
        t3cmd = find_t3cmd(moves, byn, n, s, d)
        out_moves[n] = move_entry(disp, t3name, n, d, t3cmd, moves[d], is_throw=is_thr)
        specials.append({'input': n, 't3_row': d, 'damage': out_moves[n]['damage'],
                         'throw': is_thr})
        used_rows.add(d)
        if len(specials) >= 3:
            break

    if not specials:
        # Bank has no motion-input attacks (e.g. Xiaoyu) — promote directional
        # attacks as the fighter's specials, honestly flagged.
        for n in list(out_moves.keys()):
            if '+' in n and ',' not in n and not any(c in n for c in ('1+3', '2+4')):
                btn = n.rsplit('+', 1)[-1]
                if btn in ('1', '2', '3', '4'):
                    specials.append({'input': n, 't3_row': out_moves[n]['t3_row'],
                                     'damage': out_moves[n]['damage'],
                                     'throw': False,
                                     'fallback': 'directional — no motion inputs in T3 bank'})
                    if len(specials) >= 2:
                        break

    return {
        'fighter': fid,
        'display': disp,
        'tekken_base': base,
        't3_source': t3name,
        'proxy': proxy_note is not None,
        'proxy_note': proxy_note,
        'variant': variant,
        'moves': out_moves,
        'strings': strings,
        'specials': specials,
        'frame_convention': 'T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP',
    }

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    srcs = {n: load_source(n) for n in SOURCES}
    per_src = defaultdict(int)
    order = sorted(ROSTER.items(), key=lambda kv: 0 if kv[1][3] is None else 1)
    for fid, (disp, base, t3name, proxy_note) in order:
        variant = per_src[t3name]
        per_src[t3name] += 1
        data = build_fighter(fid, disp, base, t3name, proxy_note, srcs[t3name], variant)
        with open(f'{OUTDIR}/{fid}.json', 'w') as f:
            json.dump(data, f, indent=1)
        nm = len(data['moves'])
        print(f'{fid:12s} <- {t3name:10s} v{variant} moves={nm:3d} strings={len(data["strings"])} specials={len(data["specials"])}', flush=True)
    print(f'\nWrote {len(order)} moveset files to {OUTDIR}')

if __name__ == '__main__':
    main()
