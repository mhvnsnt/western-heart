#!/usr/bin/env python3
"""Generate full-depth (100+ move) per-fighter moveset JSONs from the real
Tekken 3 decoded motion banks (teardown/tekken3/movesets/moveset_*.json).

Owner law (FULL MOVESET LAW 2026-10-19): every character gets the FULL moveset
of the character they were built on top of, Tekken-depth, no placeholders.

Method (all real data, no invention):
- Each bank row has `branches`: {command (decoded input), target_slot} edges.
- BFS over the branch graph from stance rows builds canonical Tekken notation
  paths: entry-row -> first-hit rows (strikes/throws), attack rows -> string
  continuations ('1,2', 'b+2,1' ...).
- Frame data per move comes from the DESTINATION attack row:
  startup = active_first/60, active = window/60, recovery = (stream - last)/60,
  damage = round(t3_damage * 100/170) (T3 170HP -> WH 100HP, same convention
  as the hand-curated files).
- attack_class == 1 rows are throws (King has 28 chain throws etc.).
- Condition/restriction nonzero edges are context variants; kept under a
  suffixed key, canonical notation stays in input_slots (matches the
  moveset-editor schema v2 + TekkenBuffer expectations).

Existing curated files are preserved as the base: every hand-picked move stays
byte-identical; the generator only ADDS bank-derived moves under keys that are
not already present (except per-fighter naming for the display name).

Outputs (additive):
- game/assets/movesets/<fighter>.json for every fighter whose t3_source is
  one of the 7 decoded banks
- game/assets/movesets/demonio-human.json, doc-frank-wowomomo.json,
  doc-frank-hood.json (roster ids with no file yet; bank = jin / gunjack)
- game/assets/{king,demonio,bryan,heihachi,xiaoyu,yoshimitsu,gunjack}_moves.json
  aggregates (make fighter.js loadRealMovesets() actually resolve)
"""
import json, os, sys, collections, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'banks')
OUT_MOVESETS = os.path.join(REPO, 'game', 'assets', 'movesets')
OUT_AGG = os.path.join(REPO, 'game', 'assets')

DIRNUM = {'1': 'd/b', '2': 'd', '3': 'd/f', '4': 'b', '5': 'n',
          '6': 'f', '7': 'u/b', '8': 'u', '9': 'u/f'}
BTN = {'LP': '1', 'RP': '2', 'LK': '3', 'RK': '4'}
LIMB = {'1': 'armL', '2': 'armR', '3': 'legL', '4': 'legR'}


def convert_command(cmd):
    """Decoded bank command -> list of Tekken notations (any-button expands to
    the 4 concrete buttons, mirroring real Tekken movelists). Empty list = skip."""
    if not cmd or cmd in ('<common>', '<end>'):
        return []
    c = cmd.strip()
    # motion form: [6 5 4 1 2 6+LP](30f)
    if c.startswith('['):
        inner = c[1:c.index(']')]
        toks = inner.split()
        dirs, btns = [], []
        for t in toks:
            parts = t.split('+')
            for p in parts:
                if p in DIRNUM:
                    dirs.append(DIRNUM[p])
                elif p in BTN:
                    btns.append(BTN[p])
        if not dirs and not btns:
            return []
        # neutral-mash commands (>=3 standalone neutral holds) are mash/taunt
        # inputs, not discrete moves
        if dirs.count('n') >= 3:
            return []
        return [(','.join(dirs) + ('+' + '+'.join(btns) if btns else ''))]
    if 'any-button' in c:
        if c == 'any-button':
            return []  # bare fallback: handled as pass-through in bank_edges
        out = []
        for t in c.split(','):
            sub = t.split('/')[0].split('+')
            dirs = [DIRNUM[p] for p in sub if p in DIRNUM]
            if 'any-button' in sub:
                out.extend('+'.join(dirs + [b]) for b in ('1', '2', '3', '4'))
            else:
                btns = [BTN[p] for p in sub if p in BTN]
                if not dirs and not btns:
                    return []
                out.append('+'.join(dirs + btns))
        return out
    if c in ('f,f', 'b,b'):
        return ['f,F' if c == 'f,f' else 'b,B']
    # combo form: 1+LP+LK, 3+RP+LK, LP+RP+LK+RK, 1/2+LP+RK, 1+LP+RP
    # '/' marks ALTERNATIVES in bank notation (6/9+LP = f or u/f + LP) -> first
    out = []
    for t in c.split(','):
        alts = t.split('/')
        pick = alts[0]
        sub = pick.split('+')
        dirs = [DIRNUM[p] for p in sub if p in DIRNUM]
        btns = [BTN[p] for p in sub if p in BTN]
        if not dirs and not btns:
            return []
        out.append('+'.join(dirs + btns))
    return [','.join(out)]


def is_motion_notation(n):
    return any(d in n for d in ('d/b', 'd/f', 'u/b', 'u/f')) and len(n.split(',')) >= 2


# ---- EXE common branch table (CALL 0xC00C = '<common>') ---------------------
# A '<common>' branch is NOT a move slot: BranchFind (fight_sim.branch_find,
# 0x8002E078) jumps to COMMON_ROWS + 12*target_slot in the USA EXE and walks those
# 12-byte rows (u16 cmd, u8 restriction, u8 condition, s16 slot @+6, u8 flags,
# u8 first/last window) until RETURN 0xC00D, then resumes the bank's own list.
# Their slots index the fighter's OWN move_index (e.g. common block 0 holds the
# 1+3 / 2+4 throws and throw escapes). Before 2026-10-21 the generator treated
# target_slot as a move slot of the bank, which misrouted every common edge.
COMMON_ROWS = 0x80017C78
EXE_PATH = os.path.join(REPO, 'teardown', 'tekken3', 'disc', 'files', 'TEKKEN3', 'SLUS_004.02')
_COMMON_CACHE = {}


def common_rows(idx):
    """[(command_text, restriction, condition, slot)] of EXE common block `idx`."""
    if idx in _COMMON_CACHE:
        return _COMMON_CACHE[idx]
    import struct, types
    sys.modules.setdefault('motion', types.ModuleType('motion'))  # command_text needs no motion parser
    sys.path.insert(0, os.path.join(REPO, 'teardown', 'tekken3', 'tools', 'local'))
    import moveset_extract as ME
    if not hasattr(common_rows, 'exe'):
        common_rows.exe = open(EXE_PATH, 'rb').read()
        common_rows.seqs = ME.load_seq_tables(common_rows.exe)
    exe, out = common_rows.exe, []
    a = COMMON_ROWS + 12 * idx
    for _ in range(256):
        cmd = ME._u16(exe, a)
        if cmd in (0xC000, 0xC00D):
            break
        o = a - ME.EXE_BASE + ME.EXE_HEADER
        out.append((ME.command_text(cmd, common_rows.seqs), exe[o + 2], exe[o + 3],
                    struct.unpack_from('<h', exe, o + 6)[0]))
        a += 12
    _COMMON_CACHE[idx] = out
    return out


def load_bank(bank):
    path = os.path.join(BANK_DIR, f'moveset_{bank}.json')
    with open(path) as f:
        return json.load(f)


def bank_edges(bank):
    """Shortest-path search (Dijkstra on notation-label count) over the branch
    graph. Every attack row reached gets its canonical Tekken input path:
    stance rows -> first hits; attack rows -> string continuations / cancels.
    Returns (by_row, found) with found: row -> (labels, raw_cmd, cond, restr)."""
    import heapq
    d = load_bank(bank)
    moves = d['moves']
    mi = d['move_index']
    slot2row = {}
    for s, x in enumerate(mi):
        if isinstance(x, int) and x < 100000:
            slot2row[s] = x
    by_row = {m['row']: m for m in moves}

    def is_attack(m):
        return m['attack_word'] != '0x0000' or m['damage'] > 0

    edges = collections.defaultdict(list)
    for m in moves:
        branches = []
        for b in m.get('branches', []):
            if b.get('command') == '<common>':
                # expand the EXE common block in place (see common_rows)
                for ctext, crest, ccond, cslot in common_rows(b.get('target_slot') or 0):
                    branches.append({'command': ctext, 'target_slot': cslot, 'condition': ccond,
                                     'restriction': crest, '_common': b.get('target_slot')})
            else:
                branches.append(b)
        for b in branches:
            cmd = b.get('command')
            dst = slot2row.get(b.get('target_slot'))
            if dst is None or dst not in by_row:
                continue
            if cmd in (None, '<end>', '<no-input>') or (cmd or '').startswith('<'):
                continue  # no-input continuation markers carry no notation
            if cmd == 'any-button' and not is_attack(by_row[dst]):
                # bare any-button fallback into a stance row: pass-through
                edges[m['row']].append((None, dst, 0, 0, cmd))
            elif cmd == 'any-button' and is_attack(by_row[dst]):
                # bare any-button into an attack row: 4 concrete buttons
                for n in ('1', '2', '3', '4'):
                    edges[m['row']].append((n, dst, b.get('condition', 0) or 0,
                                           b.get('restriction', 0) or 0, cmd))
            elif 'any-button' in cmd and not is_attack(by_row[dst]):
                # dir+any-button into a stance hub (crouch/WS/rise transitions):
                # pass-through; the hub's own branches carry the real inputs
                edges[m['row']].append((None, dst, b.get('condition', 0) or 0,
                                       b.get('restriction', 0) or 0, cmd))
            else:
                for n in convert_command(cmd):
                    edges[m['row']].append((n, dst, b.get('condition', 0) or 0,
                                           b.get('restriction', 0) or 0, cmd))
    # conditioned incoming edges per row (context variants of the same move)
    cond_incoming = collections.defaultdict(set)
    for m in moves:
        for b in m.get('branches', []):
            dst = slot2row.get(b.get('target_slot'))
            c = b.get('condition') or 0
            if dst in by_row and c:
                cond_incoming[dst].add(c)
    # Dijkstra: cost = (label_count, edge_count). Seed from every row that
    # carries input branches (stance hubs AND hub rows the bank flags as
    # attacks, e.g. Bryan rows 22-24 which split one jab into f/b variants).
    found = {}
    pq = []
    counter = [0]
    # Seed ONLY from stance hubs (non-attack rows). Seeding attack rows too
    # (the 2026-10-19 version) made every string continuation reachable as a
    # one-button move from the previous hit, so no multi-input string
    # ('1,2', '1,2,1') ever formed and continuation rows were filed under
    # bare buttons (fixed 2026-10-20). Hub rows the bank flags as attacks
    # (e.g. Bryan 22-24) are still reached from the stance and expanded.
    for m in moves:
        if is_attack(m):
            continue
        if any(b.get('command') not in (None, '<end>') for b in m.get('branches', [])):
            counter[0] += 1
            pq.append((0, 0, counter[0], m['row'], [], [m['row']], None, 0, 0))
    heapq.heapify(pq)
    best_cost = {}
    MAXSEG = 10
    while pq:
        lc, ec, _, src, path, rowpath, raw, cond, restr = heapq.heappop(pq)
        if best_cost.get(src) is not None and best_cost[src] <= (lc, ec):
            continue
        best_cost[src] = (lc, ec)
        if is_attack(by_row[src]) and src not in found and path:
            found[src] = (list(path), raw, cond, restr, list(rowpath))
        for n, dst, c2, r2, raw2 in edges.get(src, []):
            conds = cond or c2
            rests = restr or r2
            raws = raw2 if n is not None else raw
            label = list(path)
            rp = list(rowpath)
            if n is not None:
                if label and label[-1] == n and ',' in n:
                    continue  # avoid immediate duplicate-motion loops
                label.append(n)
                rp.append(dst)
            if len(label) > MAXSEG or lc + (1 if n else 0) > MAXSEG:
                continue
            # condition-variant edges only fill rows not otherwise reached
            if c2 and dst in found:
                continue
            counter[0] += 1
            heapq.heappush(pq, (lc + (1 if n else 0), ec + 1, counter[0], dst, label, rp, raws, conds, rests))
    return by_row, found, cond_incoming


def frame_data(row, bank):
    af, al = row['active_first'] or 0, row['active_last'] or 0
    sf = row['stream_frames'] or 1
    is_throw = row['attack_class'] == 1
    if is_throw and af == 0:
        startup = 0.2
    elif af > 0:
        startup = round(af / 60.0, 3)
    else:
        startup = 0.167
    active = round(max(al - af + 1, 1) / 60.0, 3)
    recovery = round(max(sf - max(al, af), 0) / 60.0, 3)
    t3d = row['damage'] or 0
    if is_throw and t3d == 0:
        dmg = 21  # WH grappler convention (same as vainabel.json note)
        dmg_note = 't3 row damage 0; WH grappler convention 21'
    else:
        dmg = round(t3d * 100 / 170)
        dmg_note = None
    return startup, active, recovery, dmg, dmg_note, is_throw


def limb_of(notation):
    for b in ('1', '2', '3', '4'):
        if b in notation.split('+')[-1].split(',')[-1].replace('b/', '').replace('f/', '').replace('u/', '').replace('d/', ''):
            pass
    # simplest: first button digit anywhere in the notation
    for ch in notation:
        if ch in LIMB:
            return LIMB[ch]
    return 'armL'


def build_moves(bank, display, path_rows):
    """path_rows = (by_row, found, cond_incoming). found: row -> path data."""
    by_row, found, cond_incoming = path_rows
    moves = {}
    for row, (labels, raw_cmd, cond, restr, rowpath) in sorted(found.items()):
        m = by_row[row]
        canon = ','.join(labels)
        if not canon:
            continue
        # damage-0, non-throw rows are hub/transition rows flagged with an
        # attack word (e.g. Bryan rows 22-24); not real moves
        if (m['damage'] or 0) == 0 and m['attack_class'] != 1:
            continue
        startup, active, recovery, dmg, dmg_note, is_throw = frame_data(m, bank)
        key = canon
        suffix = 0
        tag = ''
        if cond not in (0, None):
            tag = f'_c{cond}'
        elif restr not in (0, None):
            tag = f'_r{restr}'
        while key in moves:
            suffix += 1
            key = canon + (tag or '') + f'_r{row}' + (f'_{suffix}' if suffix > 1 else '')
        if suffix == 0 and tag:
            key = canon + tag
        mv = {
            'name': f'{display} {key} (T3 {bank} r{row})',
            'input': key,
            't3_source': bank,
            't3_row': row,
            't3_command': raw_cmd,
            'startup': startup, 'active': active, 'recovery': recovery,
            'damage': dmg,
            'limb': 'both' if is_throw else limb_of(canon),
            'heavy': (not is_throw) and (m['damage'] or 0) >= 20,
            'knock': 6.5 if is_throw else 2.2,
            'soulGain': 11 if is_throw else 8,
            'anim_ref': f't3:{bank}:row:{row}',
            'input_slots': [canon],
            'move_class': 'throw' if is_throw else ('special' if is_motion_notation(canon) else 'strike'),
        }
        if cond not in (0, None):
            mv['t3_condition'] = cond
        if restr not in (0, None):
            mv['t3_restriction'] = restr
        if dmg_note:
            mv['damage_note'] = dmg_note
        moves[key] = mv
        # context variants: the bank gates some rows on conditions (back-turned,
        # counter-hit, wall, etc.) — each is a real contextual variant
        for cv in sorted(cond_incoming.get(row, ())):
            if cv == cond:
                continue
            vkey = f'{canon}_c{cv}'
            if vkey in moves:
                continue
            vmv = dict(mv)
            vmv['name'] = f'{display} {vkey} (T3 {bank} r{row})'
            vmv['input'] = vkey
            vmv['t3_condition'] = cv
            vmv['move_class'] = 'special'
            moves[vkey] = vmv
    # strings: every multi-segment canonical path is a real string chain
    strings = []
    seen_str = set()
    for row, (labels, raw_cmd, cond, restr, rowpath) in sorted(found.items()):
        if len(labels) < 2:
            continue
        canon = ','.join(labels)
        if canon in moves and canon not in seen_str:
            seen_str.add(canon)
            strings.append({'input': canon, 'hits': labels,
                            't3_rows': rowpath[1:]})
    return moves, strings


def gen_for_bank(bank, display):
    return build_moves(bank, display, bank_edges(bank))[0]


def merge_into_file(path, bank, display, agg=False):
    """Merge generated moves into existing file (preserving curated data),
    or create a new file. Returns (move_count, added_count)."""
    rows = bank_edges(bank)  # (by_row, found, cond_incoming)
    gen, gen_strings = build_moves(bank, display, rows)
    by_row, found, cond_incoming = rows
    if os.path.exists(path):
        with open(path) as f:
            cur = json.load(f)
        base_moves = cur.get('moves', {})
        added = 0
        for k, v in gen.items():
            if k not in base_moves:
                base_moves[k] = v
                added += 1
        cur['moves'] = base_moves
        # merge generated strings (real branch-graph chains) over curated ones
        have_str = {s.get('input') for s in cur.get('strings', [])}
        cur['strings'] = cur.get('strings', []) + [s for s in gen_strings
                                                   if s['input'] not in have_str]
        cur['proxy'] = False
        cur['proxy_note'] = None
        cur['t3_bank'] = f'moveset_{bank}.json'
        cur['t3_bank_rows'] = len(by_row)
        cur['t3_bank_attack_rows'] = len(found)
        cur['generated_full_moveset'] = {
            'by': 'tools/gen-movesets-t3.py',
            'date': datetime.date.today().isoformat(),
            'note': ('Full T3 bank depth merged over curated base; curated moves '
                     'preserved verbatim. ' + BANK_NOTES.get(bank, '')),
        }
    else:
        cur = {
            'fighter': os.path.basename(path)[:-5],
            'display': display,
            'tekken_base': display.title(),
            't3_source': bank,
            'proxy': False,
            'proxy_note': None,
            'variant': 0,
            'moves': gen,
            'strings': gen_strings,
            'specials': [],
            'frame_convention': 'T3 60fps -> seconds; damage scaled T3 170HP -> WH 100HP',
            'schema_version': 2,
            'generated_full_moveset': {
                'by': 'tools/gen-movesets-t3.py',
                'date': datetime.date.today().isoformat(),
                'note': 'Full T3 bank depth, real decoded motion-bank rows.',
            },
        }
        added = len(gen)
    with open(path, 'w') as f:
        json.dump(cur, f, indent=2)
        f.write('\n')
    return len(cur['moves']), added


BANKS = ['king', 'jin', 'bryan', 'heihachi', 'xiaoyu', 'yoshimitsu', 'gunjack']
# Honest per-bank caveats (surfaced in generated files' provenance)
BANK_NOTES = {
    'king': 'Largest T3 bank (652 rows, 218 attacks).',
    'jin': '413 rows, 242 attacks.',
    'bryan': ('Smallest T3 bank (365 rows, 188 attacks); 79 attack rows have no '
              'per-character input in the extracted data (common-bank / reaction '
              'rows). Unique playable inputs top out at ~90-97 per fighter.'),
    'heihachi': '383 rows, 215 attacks.',
    'xiaoyu': '594 rows, 243 attacks.',
    'yoshimitsu': '449 rows, 247 attacks.',
    'gunjack': '391 rows, 249 attacks.',
}
# aggregate filename -> bank
AGGREGATES = {'king': 'king', 'demonio': 'jin', 'bryan': 'bryan',
              'heihachi': 'heihachi', 'xiaoyu': 'xiaoyu',
              'yoshimitsu': 'yoshimitsu', 'gunjack': 'gunjack'}
NEW_FIGHTERS = {'demonio-human': ('jin', 'DEMONIO'),
                'doc-frank-wowomomo': ('gunjack', 'DOC FRANK'),
                'doc-frank-hood': ('gunjack', 'DOC FRANK')}


def main():
    os.makedirs(OUT_MOVESETS, exist_ok=True)
    # per-fighter files with t3_source in the 7 banks
    total_added = 0
    nfiles = 0
    for fn in sorted(os.listdir(OUT_MOVESETS)):
        if not fn.endswith('.json'):
            continue
        path = os.path.join(OUT_MOVESETS, fn)
        with open(path) as f:
            cur = json.load(f)
        bank = cur.get('t3_source')
        if bank not in BANKS:
            continue
        display = cur.get('display') or cur.get('fighter', fn[:-5]).upper()
        n, added = merge_into_file(path, bank, display)
        total_added += added
        nfiles += 1
        print(f'{fn[:-5]}: {n} moves (+{added}) bank={bank}')
    # new roster fighters with no file yet
    for fid, (bank, display) in NEW_FIGHTERS.items():
        path = os.path.join(OUT_MOVESETS, fid + '.json')
        n, added = merge_into_file(path, bank, display)
        total_added += added
        nfiles += 1
        print(f'{fid}: {n} moves (new) bank={bank}')
    # aggregates for loadRealMovesets()
    for name, bank in AGGREGATES.items():
        path = os.path.join(OUT_AGG, f'{name}_moves.json')
        n, added = merge_into_file(path, bank, name.upper())
        print(f'aggregate {name}_moves.json: {n} moves')
    print(f'files touched: {nfiles + len(AGGREGATES)}, total moves added: {total_added}')


if __name__ == '__main__':
    main()
