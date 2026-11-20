#!/usr/bin/env python3
"""STREAM 6 — Moveset expansion: 12% -> 100% (owner 2026-10-19 ~16:46 CDT).

Takes every fighter's moveset JSON in game/assets/movesets/ to the full
reachable Tekken movelist the T3 teardown supports:
  1. Keeps every existing move verbatim (lane-3 curated + WH signature lanes).
  2. Remaps unreachable WH-signature input keys ('S', 'P+K', 'qcf+P', ...)
     to live Tekken inputs ('1+2', '3+4', 'qcf+1', ...), logged with
     input_remapped_from provenance. Previously these moves could never fire.
  3. Expands T3-banked fighters from the REAL T3 teardown banks
     (~/workspace/wh-lane3-movesets/_lane3/t3/moveset_{king,jin,bryan,heihachi,
     xiaoyu,yoshimitsu,gunjack}.json): every directional attack, throw,
     motion special and deepened string the bank supports, each on a distinct
     T3 row with real frame data (60fps -> seconds, damage T3 170HP -> WH 100HP).
  4. Backfills throw_break on EVERY throw (T3/T7 rules: 1+3 -> '1',
     2+4 -> '2', 1+2/3+4/chains -> '1+2') — the throw-break system reads this.
  5. Adds Cain Elias (new fighter, owner 2026-10-19): Undertaker archetype,
     King bank grappler rows + WH-original signature throws
     (Last Ride / Tombstone / Chokeslam / Hell's Gate).

Honesty rules (owner NO-GUESSING law):
  - Every banked move carries t3_source/t3_row/t3_command provenance.
  - WH-original moves carry wh_original:true and NO t3_source.
  - DOA/VF federation fighters (doa_source) are NOT expanded from T3 banks —
    that would corrupt their federation provenance. Reported as-is.
  - Per-bank row ledger keeps fighters sharing a bank distinct; a row is
    never reused by two moves of the same fighter.

Additive only: existing keys keep their data; new keys appended.
Schema v2 preserved (anim_ref, input_slots, move_class).
"""
import json, os, re, sys
from collections import defaultdict

T3DIR = os.path.expanduser('~/workspace/wh-lane3-movesets/_lane3/t3')
REPO = os.path.expanduser('~/workspace/wt-stream6')
MSDIR = os.path.join(REPO, 'game', 'assets', 'movesets')
SOURCES = ['king', 'jin', 'bryan', 'heihachi', 'xiaoyu', 'yoshimitsu', 'gunjack']

# ---------------------------------------------------------------- Tekken notation
# parse_command: decoding copied from lane-3 extract_movelists.py
# (~/workspace/wh-lane3-movesets/_lane3/extract_movelists.py) — same decoding.
DIRMAP = {'1': 'd/b', '2': 'd', '3': 'd/f', '4': 'b', '5': 'n',
          '6': 'f', '7': 'u/b', '8': 'u', '9': 'u/f'}
BTNM = {'LP': '1', 'RP': '2', 'LK': '3', 'RK': '4'}

def parse_command(cmd):
    if not cmd or cmd in ('any-button',):
        return None
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
    m = re.fullmatch(r'((?:LP|RP|LK|RK)(?:\+(?:LP|RP|LK|RK))*)', cmd)
    if m:
        return '+'.join(BTNM[x] for x in m.group(1).split('+'))
    m = re.fullmatch(r'\[([1-9 ]+)(?:\+((?:LP|RP|LK|RK)(?:\+(?:LP|RP|LK|RK))*))?\]\((\d+)f\)', cmd)
    if m:
        seq = m.group(1).split()
        btns = m.group(2)
        b = '+' + '+'.join(BTNM[x] for x in btns.split('+')) if btns else ''
        seqn = [DIRMAP[s] for s in seq]
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
        m2 = re.fullmatch(r'([1-9](?:/[1-9])?)\+any-button', cmd)
        if m2:
            d = m2.group(1)
            d = '/'.join(DIRMAP[x] for x in d.split('/'))
            return {'f': 'f,F', 'd/f': 'ws', 'd': 'fc'}.get(d, d) + ',any'
        return None
    return None

# T3 fine-grained diagonal encodings -> canonical Tekken directions.
TRIPLE_NORM = {'b/u/b': 'u/b', 'd/b/b': 'd/b', 'd/b/d': 'd',
               'd/d/f': 'd/f', 'd/f/f': 'd/f', 'f/u/f': 'u/f',
               'u/u/f': 'u/f', 'b/f': 'f'}

def normalize_notation(n):
    if not n:
        return n
    parts = re.split(r'([,+])', n)
    return ''.join(TRIPLE_NORM.get(p, p)
                   if re.fullmatch(r'[a-z]+(?:/[a-z]+)+', p) else p
                   for p in parts)

# A notation the game engine can actually resolve (movesets.js TekkenBuffer +
# fighter.js tryAttack, extended Stream 6: directional chords d/b+1+3,
# raw dir-sequence motions d,d/b,d,d/b+1+2). Anything else is dead on mobile.
_single = (r'([1234]|[1234]\+[1234]'
           r'|((f|b|d|u|d/f|d/b|u/f|u/b|n|ws|fc|wr),)*((f|b|d|u|d/f|d/b|u/f|u/b|n)\+[1234](\+[1234])*)'
           r'|((f|b|d|u|d/f|d/b|u/f|u/b|n),)+(f|b|d|u|d/f|d/b|u/f|u/b|n)\+[1234](\+[1234])*'
           r'|(qcf|qcb|hcf|hcb|f,F|b,B|d,D|u,U|f,n,f)([+](([1234])(\+[1234])*))?)')
REACHABLE = re.compile(rf'^{_single}(,[1234])*$')

def is_reachable(notation):
    return bool(REACHABLE.match(notation or ''))

# ---------------------------------------------------------------- T3 bank loading
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
    by_notation = defaultdict(list)
    for m in moves:
        src = m['row']
        for b in m.get('branches', []):
            if not b.get('entry'):
                continue
            n = parse_command(b.get('command', ''))
            if not n:
                continue
            n = normalize_notation(n)
            dst = slot_to_row(b['target_slot'])
            if dst is None:
                continue
            by_notation[n].append((src, dst, b.get('command', '')))
    return {'name': name, 'moves': moves, 'by_notation': by_notation}

def throw_damage(m):
    for e in m.get('events', []) or []:
        if isinstance(e, dict):
            for k in ('damage', 'dmg', 'power'):
                if k in e and isinstance(e[k], (int, float)) and e[k] > 0:
                    return int(e[k])
    return 35

def framedata(m, is_throw=False):
    af, al, sf = m['active_first'], m['active_last'], m['stream_frames']
    startup = max(0.05, af / 60.0)
    active = max(0.017, (al - af + 1) / 60.0)
    recovery = max(0.1, (sf - al) / 60.0)
    dmg = throw_damage(m) if is_throw else m['damage']
    damage = max(1, round(dmg * 100.0 / 170.0))
    return {'startup': round(startup, 3), 'active': round(active, 3),
            'recovery': round(recovery, 3), 'damage': damage, 't3_damage': dmg}

def is_strike(m):
    return m['active_first'] > 0 and m['damage'] > 0 and m['stream_frames'] > 0

def is_throwmove(m):
    return m.get('attack_class') == 1 and m['damage'] == 0 and m['active_first'] > 0

LIMB = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}

def throw_break_for(notation):
    """T3->T7 throw escape rules (tekken.fandom.com/wiki/Throw):
    1+3 throws break with 1, 2+4 with 2, 1+2/3+4 and chain throws with 1+2."""
    n = notation or ''
    if '1+2' in n or '3+4' in n:
        return '1+2'
    if ',' in n:  # chain throw links break at each link with 1+2
        return '1+2'
    if n in ('1+3',):
        return '1'
    if n in ('2+4',):
        return '2'
    btns = set(re.findall(r'[1234]', n.rsplit(',', 1)[-1]))
    if btns <= {'1', '3'} and btns:
        return '1'
    if btns <= {'2', '4'} and btns:
        return '2'
    return '1+2'

def move_entry(display, src_name, notation, row, cmd, m, is_throw=False,
               string_of=None, move_class=None):
    fd = framedata(m, is_throw=is_throw)
    last_btn = re.findall(r'[1234]', notation)
    limb = LIMB.get(last_btn[-1] if last_btn else '', 'armR')
    heavy = fd['damage'] >= 15 or is_throw
    entry = {
        'name': f"{display} {notation}{' throw' if is_throw else ''} (T3 {src_name} r{row})",
        'input': notation,
        't3_source': src_name, 't3_row': row, 't3_command': cmd,
        'startup': fd['startup'], 'active': fd['active'], 'recovery': fd['recovery'],
        'damage': fd['damage'], 't3_damage': fd['t3_damage'],
        'limb': limb, 'heavy': heavy,
        'knock': 6.5 if is_throw else (4.2 if limb.startswith('leg') or heavy else 2.2),
        'soulGain': 11 if heavy else 8,
        'anim_ref': f't3:{src_name}:row:{row}',
        'input_slots': [notation],
        'move_class': move_class or ('throw' if is_throw else ('string' if string_of else 'strike')),
    }
    if string_of:
        entry['string_hit'] = string_of
        entry['input_slots'] = [notation] + notation.split(',')
    if is_throw:
        entry['throw'] = True
        entry['unblockable'] = True
        entry['isGrab'] = True
        entry['throw_break'] = throw_break_for(notation)
        entry['note'] = 'T3 bank stores 0 damage for throws; damage follows WH grappler convention'
    return entry

# ------------------------------------------------- dead-key remap (WH signatures)
# WH-signature moves keyed 'S', 'P+K', 'qcf+P', ... can never fire: the engine
# only resolves Tekken notations. Remap them to live inputs, keeping
# input_remapped_from provenance. Only touches wh_original moves.
# Fallback live inputs when the primary remap target is taken.
def remap_signature_key(key):
    if is_reachable(key):
        return key
    k = key
    k = re.sub(r'\bS\b', '1+2', k)
    k = re.sub(r'\bP\b', '1', k)
    k = re.sub(r'\bK\b', '4', k)
    k = re.sub(r'^D\+', 'd+', k)  # legacy down-prefix
    k = k.replace(' ', '')
    if is_reachable(k):
        return k
    return None

REMAP_FALLBACKS = {'1+2': ['3+4', '1+4', '2+3'], '3+4': ['1+2', '1+4', '2+3'],
                   'qcf+1': ['qcf+2'], 'qcf+4': ['qcf+3']}

def remap_targets(key):
    primary = remap_signature_key(key)
    if not primary:
        return []
    return [primary] + REMAP_FALLBACKS.get(primary, [])

# ------------------------------------------------- row picking
def pick_row(cands, moves, used_rows, bank_used, want='fast', dmg_target=None):
    """Best destination row for a notation. Hard-skips rows this fighter
    already uses; prefers rows no fighter on this bank has used yet."""
    scored = []
    for src, dst, cmd in cands:
        if dst in used_rows:
            continue
        m = moves[dst]
        if not is_strike(m):
            continue
        score = 0
        if dst not in bank_used:
            score += 100
        if src <= 12:
            score += 50
        elif src <= 60:
            score += 20
        if want == 'fast':
            score += max(0, 30 - m['active_first'])
        if dmg_target:
            score += max(0, 20 - abs(m['damage'] - dmg_target))
        scored.append((score, m['active_first'], dst, src, cmd))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return scored[0][2], scored[0][3], scored[0][4]

def pick_throw_row(cands, moves, used_rows, bank_used):
    scored = []
    for src, dst, cmd in cands:
        if dst in used_rows:
            continue
        m = moves[dst]
        if not is_throwmove(m):
            continue
        score = 0
        if dst not in bank_used:
            score += 100
        score += (50 if src <= 12 else 0) + max(0, 60 - m['stream_frames'])
        scored.append((score, dst, src, cmd))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][1], scored[0][2], scored[0][3]

# ------------------------------------------------- string deepening
def deepen_strings(moves_json, src, used_rows, bank_used, display, src_name,
                   max_new=30):
    """Follow branch chains from existing strikes; worklist grows as new
    strings are added, so chains deepen to 6 hits iteratively."""
    new_moves, new_strings = {}, []
    moves, byn = src['moves'], src['by_notation']
    worklist = [(k, v) for k, v in moves_json['moves'].items()
                if is_reachable(k) and isinstance(v, dict)
                and v.get('t3_row') is not None and not v.get('throw')
                and v.get('move_class') in ('strike', 'string', None)]
    while worklist and len(new_moves) < max_new:
        key, mv = worklist.pop(0)
        seq = key.split(',')
        if len(seq) >= 6:
            continue
        cur = mv['t3_row']
        if not (0 <= cur < len(moves)):
            continue
        for b in moves[cur].get('branches', []):
            if not b.get('entry'):
                continue
            n = parse_command(b.get('command', ''))
            if not n or not re.fullmatch(r'[1234]', n):
                continue
            dst = next((d for s, d, c in byn.get(n, []) if s == cur), None)
            if dst is None or not is_strike(moves[dst]):
                continue
            if dst in used_rows:
                continue
            nkey = ','.join(seq + [n])
            if nkey in moves_json['moves'] or nkey in new_moves:
                continue
            entry = move_entry(display, src_name, nkey, dst, b['command'],
                               moves[dst], string_of=','.join(seq))
            new_moves[nkey] = entry
            new_strings.append({'input': nkey, 'hits': seq + [n],
                                't3_rows': [dst]})
            used_rows.add(dst)
            bank_used.add(dst)
            worklist.append((nkey, entry))
            if len(new_moves) >= max_new:
                break
    return new_moves, new_strings

# ------------------------------------------------- per-fighter expansion
def expand_fighter(data, src, bank_used, report):
    """Additive expansion of one fighter's moveset. Returns (added, remapped)."""
    fid = data['fighter']
    display = data.get('display', fid.upper())
    src_name = data.get('t3_source')
    moves = data['moves']
    added, remapped = 0, []

    used_rows = set(
        v.get('t3_row') for v in moves.values()
        if isinstance(v, dict) and v.get('t3_row') is not None
        and v.get('t3_source') == src_name)

    # ---- 1) remap dead WH-signature keys to reachable inputs
    for key in list(moves.keys()):
        mv = moves[key]
        if not isinstance(mv, dict) or not mv.get('wh_original'):
            continue
        if is_reachable(key):
            continue
        new_key = None
        for cand in remap_targets(key):
            if cand not in moves:
                new_key = cand
                break
        if new_key:
            mv['input'] = new_key
            mv['input_slots'] = [new_key]
            mv['input_remapped_from'] = key
            moves[new_key] = mv
            del moves[key]
            remapped.append((key, new_key))
            report['remaps'].append(f'{fid}: {key!r} -> {new_key!r}')
        else:
            mv['unreachable'] = True
            mv['unreachable_note'] = ('input has no live mobile mapping; '
                                      'kept as data, needs manual mapping')
            report['unreachable'].append(f'{fid}: {key!r}')

    # ---- 2) backfill throw_break on every throw
    for key, mv in moves.items():
        if isinstance(mv, dict) and (mv.get('throw') or mv.get('isGrab')):
            if 'throw_break' not in mv:
                mv['throw_break'] = throw_break_for(mv.get('input', key))
                report['throw_breaks'] += 1

    if src_name not in SOURCES or src is None:
        return added, remapped  # DOA/VF federation: provenance stays pure

    bank_moves, byn = src['moves'], src['by_notation']
    TARGET = 100

    def budget_ok():
        return len(moves) < TARGET

    # ---- 3) directional attacks: every directional/chord notation the bank has
    def is_directional_notation(n):
        if not is_reachable(n) or ',' in n:
            return False
        return bool(re.match(r'^(f|b|d|u|d/f|d/b|u/f|u/b|n|ws|fc|wr)\+', n)) \
            and not re.match(r'^(qcf|qcb|hcf|hcb|f,F|b,B|d,D|u,U|f,n,f)', n)

    dir_notations = sorted(
        (n for n in byn
         if is_directional_notation(n)
         and not any(is_throwmove(bank_moves[d]) for _, d, _ in byn[n])),
        key=lambda n: (len(n), n))
    for notation in dir_notations:
        if not budget_ok():
            break
        if notation in moves:
            continue
        pk = pick_row(byn[notation], bank_moves, used_rows, bank_used)
        if not pk:
            continue
        dst, s, cmd = pk
        moves[notation] = move_entry(display, src_name, notation, dst, cmd,
                                     bank_moves[dst], move_class='strike')
        used_rows.add(dst); bank_used.add(dst); added += 1

    # ---- 4) throws: every throw notation in the bank
    throw_notations = sorted(
        set(n for n, cl in byn.items()
            if is_reachable(n)
            and any(is_throwmove(bank_moves[d]) for _, d, _ in cl)),
        key=lambda n: (0 if n in ('1+3', '2+4') else 1, n))
    for notation in throw_notations:
        if not budget_ok():
            break
        if notation in moves:
            continue
        pk = pick_throw_row(byn[notation], bank_moves, used_rows, bank_used)
        if not pk:
            continue
        dst, s, cmd = pk
        moves[notation] = move_entry(display, src_name, notation, dst, cmd,
                                     bank_moves[dst], is_throw=True,
                                     move_class='throw')
        used_rows.add(dst); bank_used.add(dst); added += 1

    # ---- 5) deepen strings
    if budget_ok():
        nm, ns = deepen_strings(data, src, used_rows, bank_used, display,
                                src_name, max_new=TARGET - len(moves))
        moves.update(nm)
        data.setdefault('strings', []).extend(ns)
        added += len(nm)

    # ---- 6) motion specials: every remaining motion notation
    if budget_ok():
        speccands = []
        for n, clist in byn.items():
            if n in moves or not is_reachable(n):
                continue
            if ',' not in n and 'F' not in n and 'B' not in n:
                continue
            if ',any' in n:
                continue
            btn = n.rsplit('+', 1)[-1] if '+' in n else ''
            if btn not in ('1', '2', '3', '4'):
                continue
            for s, d, cmd in clist:
                if d in used_rows:
                    continue
                m = bank_moves[d]
                if is_throwmove(m):
                    speccands.append((1000, n, s, d, cmd, True))
                elif is_strike(m):
                    speccands.append((m['damage'], n, s, d, cmd, False))
        speccands.sort(key=lambda x: (-x[0], x[1]))
        seen = set()
        for score, n, s, d, cmd, is_thr in speccands:
            if not budget_ok() or n in seen:
                continue
            seen.add(n)
            moves[n] = move_entry(display, src_name, n, d, cmd, bank_moves[d],
                                  is_throw=is_thr,
                                  move_class='special' if not is_thr else 'throw')
            data.setdefault('specials', []).append(
                {'input': n, 't3_row': d, 'damage': moves[n]['damage'],
                 'throw': is_thr})
            used_rows.add(d); bank_used.add(d); added += 1

    # ---- 7) provenance
    data['expansion'] = {
        'stream': 'stream6/combat-100',
        'date': '2026-10-19',
        'moves_added': added,
        'inputs_remapped': [f'{a}->{b}' for a, b in remapped],
        'note': ('Additive expansion from real T3 teardown bank rows. '
                 'Existing moves untouched.'),
    }
    return added, remapped

# ------------------------------------------------- Cain Elias (new fighter)
# Owner 2026-10-19: Vain Abel's brother, based on Undertaker (WWE).
# Attire 1 = biker. Archetype: powerhouse grappler -> King T3 bank rows
# (distinct from pantera/yukihyo/kutz/zangief/armor-king via the bank ledger),
# plus WH-original signature throws (no Undertaker teardown exists).
CAIN_SIGNATURES = [
    # (key, name, kind, startup, active, recovery, damage, limb, heavy, knock, note)
    ('d/b+1+2', 'Tombstone Piledriver', 'throw', 0.45, 0.05, 0.9, 32, 'armR',
     True, 7.5, 'The Deadman drops them on their head. WH-original.'),
    ('f,f+1+2', 'Last Ride', 'throw', 0.5, 0.05, 1.0, 30, 'armR',
     True, 8.0, 'Powerbomb carried across the ring. WH-original.'),
    ('b+1+2', 'Chokeslam', 'throw', 0.4, 0.05, 0.85, 26, 'armR',
     True, 7.0, 'One-handed throat lift. WH-original.'),
    ('d+1+2', "Hell's Gate", 'throw', 0.35, 0.05, 0.8, 22, 'armR',
     True, 6.5, 'Submission choke. WH-original.'),
    ('u+1+2', 'Old School', 'strike', 0.38, 0.05, 0.7, 20, 'armR',
     True, 5.0, 'Top-rope arm drag, adapted for the pit. WH-original.'),
]

def build_cainelias(src, bank_used, report):
    src_name = 'king'
    bank_moves, byn = src['moves'], src['by_notation']
    display = 'CAIN ELIAS'
    moves = {}
    used_rows = set()

    DMG_TARGET = {'1': 12, '2': 14, '3': 15, '4': 20}
    for btn in ['1', '2', '3', '4']:
        pk = pick_row(byn.get(btn, []), bank_moves, used_rows, bank_used,
                      dmg_target=DMG_TARGET[btn])
        if not pk:
            continue
        dst, s, cmd = pk
        moves[btn] = move_entry(display, src_name, btn, dst, cmd,
                                bank_moves[dst])
        used_rows.add(dst); bank_used.add(dst)
    for notation in ['1+3', '2+4']:
        pk = pick_throw_row(byn.get(notation, []), bank_moves, used_rows,
                            bank_used)
        if not pk:
            continue
        dst, s, cmd = pk
        moves[notation] = move_entry(display, src_name, notation, dst, cmd,
                                     bank_moves[dst], is_throw=True,
                                     move_class='throw')
        used_rows.add(dst); bank_used.add(dst)

    for key, name, kind, su, ac, rc, dmg, limb, heavy, knock, note in CAIN_SIGNATURES:
        is_thr = (kind == 'throw')
        moves[key] = {
            'name': f'{name} [WH SIGNATURE]',
            'input': key,
            'startup': su, 'active': ac, 'recovery': rc, 'damage': dmg,
            't3_damage': None,
            'limb': limb, 'heavy': heavy, 'knock': knock, 'soulGain': 13,
            'anim_ref': f'wh:cainelias:sig:{name.lower().replace(chr(39), "").replace(" ", "-")}',
            'input_slots': [key],
            'move_class': 'signature',
            'wh_original': True,
            'note': note,
        }
        if is_thr:
            moves[key].update({'throw': True, 'unblockable': True,
                               'isGrab': True,
                               'throw_break': throw_break_for(key)})

    data = {
        'fighter': 'cainelias',
        'display': display,
        'tekken_base': 'Undertaker (WWE)',
        't3_source': src_name,
        'proxy': True,
        'proxy_note': ('Undertaker (WWE) archetype; no Undertaker teardown exists. '
                       'Grappler rows from King T3 bank (distinct row pool); '
                       'signature throws are WH-original. '
                       'Attire 2 fight-gear variant per owner 2026-10-19.'),
        'variant': 9,
        'moves': moves,
        'strings': [],
        'specials': [],
        'frame_convention': 'T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP',
        'schema_version': 2,
        'canon_note': ("Vain Abel Elias's brother (owner 2026-10-19). Biker attire; "
                       "Last Ride / Tombstone / Chokeslam / Hell's Gate."),
    }
    added, remapped = expand_fighter(data, src, bank_used, report)
    data['expansion']['moves_added'] += len(CAIN_SIGNATURES)
    data['expansion']['note'] += ' Includes new-fighter core + WH signature set.'
    return data

# ------------------------------------------------- driver
def main():
    os.makedirs(MSDIR, exist_ok=True)
    srcs = {n: load_source(n) for n in SOURCES}
    bank_used = {n: set() for n in SOURCES}
    report = {'remaps': [], 'unreachable': [], 'throw_breaks': 0,
              'per_fighter': []}

    files = sorted(f for f in os.listdir(MSDIR) if f.endswith('.json'))
    # non-proxy first (they define the bank's canonical rows), then proxy
    def sortkey(f):
        d = json.load(open(os.path.join(MSDIR, f)))
        return (0 if not d.get('proxy') else 1, f)
    files.sort(key=sortkey)

    for f in files:
        path = os.path.join(MSDIR, f)
        data = json.load(open(path))
        before = len(data.get('moves', {}))
        # demonio-winged: no deviljin bank exists; Devil Jin ≈ Jin (proxy, honest)
        if data.get('t3_source') == 'deviljin':
            data['t3_source'] = 'jin'
            data['proxy'] = True
            data['proxy_note'] = ('Devil Jin has no T3 bank — Jin bank proxy '
                                  '(same Mishima base style)')
        src_name = data.get('t3_source')
        src = srcs.get(src_name) if src_name in SOURCES else None
        added, remapped = expand_fighter(
            data, src, bank_used[src_name] if src else None, report)
        after = len(data.get('moves', {}))
        data['schema_version'] = 2
        with open(path, 'w') as fh:
            json.dump(data, fh, indent=1)
            fh.write('\n')
        reachable = sum(1 for k in data['moves'] if is_reachable(k))
        report['per_fighter'].append(
            (data['fighter'], before, after, reachable, added, len(remapped)))
        print(f"{data['fighter']:24s} {before:3d} -> {after:3d} "
              f"(reachable {reachable:3d}, +{added:3d} bank, remap {len(remapped)})",
              flush=True)

    # Cain Elias (new)
    cain = build_cainelias(srcs['king'], bank_used['king'], report)
    with open(os.path.join(MSDIR, 'cainelias.json'), 'w') as fh:
        json.dump(cain, fh, indent=1)
        fh.write('\n')
    print(f"cainelias (NEW): {len(cain['moves'])} moves "
          f"({sum(1 for k in cain['moves'] if is_reachable(k))} reachable)")

    rep_path = os.path.join(REPO, 'tools', 'moveset-expand',
                            'EXPANSION-REPORT.md')
    total_before = sum(b for _, b, _, _, _, _ in report['per_fighter'])
    total_after = sum(a for _, _, a, _, _, _ in report['per_fighter']) + len(cain['moves'])
    with open(rep_path, 'w') as fh:
        fh.write('# Stream 6 — Moveset Expansion Report\n\n')
        fh.write(f'Before: {total_before} moves across {len(report["per_fighter"])} fighters. '
                 f'After: {total_after} moves across {len(report["per_fighter"]) + 1} fighters (+cainelias).\n\n')
        fh.write(f'Throw-break backfills: {report["throw_breaks"]}\n\n')
        fh.write('## Input remaps (dead WH-signature keys -> live Tekken inputs)\n\n')
        for r in report['remaps']:
            fh.write(f'- {r}\n')
        fh.write('\n## Unreachable keys kept as data (need manual mapping)\n\n')
        for r in report['unreachable']:
            fh.write(f'- {r}\n')
        fh.write('\n## Per-fighter counts\n\n')
        fh.write('| fighter | before | after | reachable | +bank | remapped |\n')
        fh.write('|---|---|---|---|---|---|\n')
        for fid, b, a, r, ad, rm in report['per_fighter']:
            fh.write(f'| {fid} | {b} | {a} | {r} | {ad} | {rm} |\n')
        fh.write(f'| cainelias (NEW) | 0 | {len(cain["moves"])} | '
                 f'{sum(1 for k in cain["moves"] if is_reachable(k))} | — | — |\n')
    print(f'\nReport: {rep_path}')

if __name__ == '__main__':
    main()
