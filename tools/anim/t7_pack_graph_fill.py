#!/usr/bin/env python3
"""t7_pack_graph_fill.py: fill a fighter's T7 moves pack from the fighter's own IMPORTED motbin graph (pull-in-first).

Inputs, all already in the repo, nothing hand-typed per move:
  <dir>/graph.json           King's motbin graph (tools/anim/t7_graph_import.py): every move's damage, first active
                             frame and the clip it plays (bank + clip index)
  <dir>/graph.commands.json  the graph's cancel rows evaluated by the game's own interpreter (game/js/t7graph.js
                             via tools/anim/t7_graph_commands.mjs): from the neutral stance, which input reaches
                             which move, and from each move which follow-up input reaches which move
  <dir>/graph-clips/         every clip the graph reaches, baked on the SAME skeleton as moves.pack.json
  game/assets/movesets/<fighter>.json  the rows the game actually plays (only inputs the fighter has get filled)

What it writes into moves.pack.json (in place, deterministic, idempotent):
  1. every pack move gets `damage` + `first_active` from graph.json for its motbin move (the T7 source value; the
     game uses it as the hit damage for fighters in fighter.js T7_EXACT_DAMAGE);
  2. SINGLE INPUTS: a moveset row input with no pack move, whose stance press row (status evaluable, damage > 0)
     reaches a motbin move -> a pack move '<input>~t7.cmd' playing that move's own clip (copied from graph-clips
     when the pack does not hold it yet);
  3. STRING STEPS (2 steps): a moveset string 'A,B' with no pack string, where A is a stance press row to move X
     and X's own evaluable follow-up row '*+B' / 'B' reaches move Y -> '<A,B>~t7.cmd' playing Y's clip.
Rows whose source would be ambiguous (two different target moves for one input) and every CHORD input (e.g. 1+4,
d/b+1+2: precedence between a chord row and its single-button rows is not proven by the evaluable list) are
reported and never filled.

usage: python3 tools/anim/t7_pack_graph_fill.py game/assets/anim/t7/king game/assets/movesets/pantera.json [--dry]
"""
import json, os, re, sys

def norm_input(s):
    s = re.sub(r'\s+', '', str(s or '').lower())
    if not s or ',' in s: return None
    return re.sub(r'(^|[^a-z/])([du])([fb])(?=\+|$)', r'\1\2/\3', s)

def norm_string(s):
    steps = re.sub(r'\s+', '', str(s or '').lower()).split(',')
    if len(steps) < 2: return None
    out = [norm_input(x) if re.match(r'^([du]/?[fb]|[dubf])?\+?[1-4](\+[1-4])*$', x) else None for x in steps]
    return ','.join(out) if all(out) else None

def main():
    d, msf = sys.argv[1], sys.argv[2]; dry = '--dry' in sys.argv
    graph = json.load(open(f'{d}/graph.json')); cmds = json.load(open(f'{d}/graph.commands.json'))
    pack_path = f'{d}/moves.pack.json'; pack = json.load(open(pack_path))
    gidx = json.load(open(f'{d}/graph-clips/index.json'))
    if gidx.get('graph_sha256') != cmds.get('graph_sha256'): sys.exit('graph-clips and graph.commands were made from different graphs')
    moves = {m['name']: m for m in graph['moves']}
    ms = json.load(open(msf))
    rows = [r for v in ms.values() if isinstance(v, dict) for r in v.values() if isinstance(r, dict) and r.get('input')]
    ms_inputs = {norm_input(r['input']) for r in rows} - {None}
    ms_strings = {norm_string(r['input']) for r in rows} - {None}
    report = {'damage_set': 0, 'single_added': [], 'string_added': [], 'ambiguous': [], 'clips_copied': []}
    # 1. T7 damage + first active on every pack move
    for k, m in pack['moves'].items():
        g = moves.get(m.get('motbin_move'))
        if g and g.get('damage', 0) not in (None, 16384):
            if m.get('damage') != g['damage'] or m.get('first_active') != g.get('first_active'): report['damage_set'] += 1
            m['damage'] = g['damage']; m['first_active'] = g.get('first_active')
    have_in = {norm_input(m['input']) for m in pack['moves'].values()} - {None}
    have_str = {norm_string(m['input']) for m in pack['moves'].values()} - {None}
    shards = {}
    def clip_for(move):
        key = f"{move['bank']}_{move['clip']}"
        for m in pack['moves'].values():  # the pack already plays this motbin move: reuse its verified clip
            if m.get('motbin_move') == move['name'] and m.get('clip') in pack['clips']: return m['clip']
        for ck, c in pack['clips'].items():  # pack already holds the same source clip (any key spelling)
            ts = c.get('t7_source') or {}
            if ck == key or (isinstance(ts, dict) and ts.get('clip') == move['clip'] and str(ts.get('file', '')).startswith(('kin' + move['bank'], move['bank']))):
                return ck
        ent = gidx['clips'].get(key)
        if not ent: return None
        sh = ent['shard']
        if sh not in shards: shards[sh] = json.load(open(f"{d}/graph-clips/{gidx['shards'][sh]['file']}"))
        data = shards[sh]['clips'].get(key)
        if not data: return None
        pack['clips'][key] = data; report['clips_copied'].append(key); return key
    def add(key, inp, mv, why):
        ck = clip_for(mv)
        if not ck: report['ambiguous'].append([inp, mv['name'], 'clip not in graph-clips']); return
        pack['moves'][key] = {'clip': ck, 'input': inp, 't7_command': inp, 'motbin_move': mv['name'], 'motbin_id': mv['id'],
                              'active_frames': [mv['first_active'], mv.get('last_active') or mv['first_active']],
                              'damage': mv['damage'], 'first_active': mv['first_active'],
                              'verified': why, 'filled_by': 'tools/anim/t7_pack_graph_fill.py'}
    # 2. single inputs from the stance
    stance = {}
    for r in cmds['stance_press_commands_evaluable']:
        ni = norm_input(r['notation'].replace('*+', ''))
        if ni: stance.setdefault(ni, set()).add(r['to'])
    for ni in sorted(ms_inputs - have_in):
        tos = {t for t in stance.get(ni, ()) if moves.get(t, {}).get('damage', 0) not in (0, 16384)}
        if len(tos) > 1: report['ambiguous'].append([ni, sorted(tos), 'several stance rows']); continue
        if not tos: continue
        t = tos.pop()
        if ni.count('+') > 1 or re.search(r'[1-4]\+[1-4]', ni):  # chords: stance-row precedence between a chord and
            # its single-button rows is not proven by this list, so chords are reported, never filled
            report['ambiguous'].append([ni, t, 'chord: stance-row precedence unverified, not filled']); continue
        add(f'{ni}~t7.cmd', ni, moves[t], f'graph.commands.json: {ni} pressed from {cmds["stance"]} reaches {t} (evaluable row); damage {moves[t]["damage"]}, first active {moves[t]["first_active"]} from graph.json')
        report['single_added'].append([ni, t])
    # 3. two-step strings
    follow = {}
    for r in cmds['all']:
        if r.get('status') != 'evaluable' or r.get('kind') == 'state': continue
        b = norm_input(r['notation'].replace('*+', ''))
        if b: follow.setdefault((r['from'], b), set()).add(r['to'])
    for ns in sorted(ms_strings - have_str):
        st = ns.split(',')
        if len(st) != 2: continue
        if any(re.search(r'[1-4]\+[1-4]', x) for x in st):
            report['ambiguous'].append([ns, None, 'chord step: stance-row precedence unverified, not filled']); continue
        xs = stance.get(st[0], set())
        ys = {y for x in xs for y in follow.get((x, st[1]), ()) if moves.get(y, {}).get('damage', 0) not in (0, 16384)}
        if len(ys) > 1: report['ambiguous'].append([ns, sorted(ys), 'several follow-up rows']); continue
        if not ys: continue
        y = ys.pop()
        add(f'{ns}~t7.cmd', ns, moves[y], f'graph.commands.json: {st[0]} from {cmds["stance"]} -> {sorted(xs)}, then its evaluable follow-up {st[1]} -> {y}; damage {moves[y]["damage"]}, first active {moves[y]["first_active"]} from graph.json')
        report['string_added'].append([ns, y])
    pack.setdefault('source', {})['graph_fill'] = {'tool': 'tools/anim/t7_pack_graph_fill.py', 'graph_sha256': cmds['graph_sha256']}
    print(json.dumps(report, indent=1))
    if not dry:
        with open(pack_path, 'w') as f: json.dump(pack, f, separators=(',', ':'), sort_keys=False)

if __name__ == '__main__':
    main()
