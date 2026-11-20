#!/usr/bin/env python3
"""t3_condition_walk.py — Tekken 3 branch-condition-aware string walk.

Walks a fighter's own T3 bank branch graph (teardown/tekken3/movesets/
moveset_<bank>.json) through a WH input string (e.g. "1,2,1", "d+1+2,2,1",
"WS+2", "f,f+2"), deciding each branch with the decoded branch-condition
table (tools/anim/t3_condition_codes.json) instead of treating every
non-zero condition as a dead end.

The decode (see docs/movesets/T3-CONDITION-CODE-DECODE-2026-10-31.md):
condition 0 is unconditional; 36 and the pairs 37/38, 62/63, 64/65, 18/19,
40/41 are variant selectors (parallel rows of the same move); 48 gates the
crouch-state family (source profile: stance_slot 40/54/57, state_words
0x3129/0x2021/0x2829); 57-61 gate the 0x3884 state family; 39 is the throw
gate (its restriction variants are opponent-state); 25/24/55 are
distance-parameter gates; codes 2-23 with param 1536 and 72-75 are engine
dispatch families on 'any-button' transitions and are NOT walkable.

Modes:
  walk      --bank king --input "1,2,1" [--start standing|crouch]
  validate  --movesets-dir game/assets/movesets --banks-dir teardown/tekken3/movesets
            Replays every provenance_fix record of the Phase-1 files and
            reports how often the condition-aware walk reaches the proven
            row, against two baselines (all-nonzero-blocked, all-passable).
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict

EMPTY = 1073741823
BTN = {'1': 'LP', '2': 'RP', '3': 'LK', '4': 'RK'}
DIRNUM = {'n': 5, 'u': 8, 'd': 2, 'f': 6, 'b': 4,
          'u/f': 9, 'd/f': 3, 'u/b': 7, 'd/b': 1}
MOTIONS = {'qcf': [2, 3, 6], 'qcb': [2, 1, 4],
           'hcf': [4, 1, 2, 3, 6], 'hcb': [6, 3, 2, 1, 4],
           'f,f': 'hex:c001', 'b,b': 'hex:c002', 'd,f': [2, 6], 'd,b': [2, 4]}

# ---------------------------------------------------------------- conditions
class Table:
    """Walk rules from the decoded condition table (JSON)."""
    def __init__(self, path=None):
        self.rules = {}
        if path and os.path.exists(path):
            data = json.load(open(path))
            for code, entry in data.get('codes', {}).items():
                self.rules[int(code)] = entry.get('walk_rule', 'blocked_unknown')
        self.stats = Counter()

    def rule(self, code):
        return self.rules.get(code, 'blocked_unknown')

# state-family profiles, derived from the condition source census
CROUCH_FAMILY_STANCE = {40, 54, 57}
CROUCH_FAMILY_WORDS = {'0x00003129', '0x00002021', '0x00002829'}
F3884_STANCE = {153, 157, 158, 166, 167, 168}
F3884_WORDS = {'0x00003884', '0x00004284', '0x00004c02'}

def branch_passable(table, br, src_row, mode='decoded'):
    """Return (passable, tag). mode: decoded | all_blocked | all_pass."""
    cond = br.get('condition')
    if mode == 'all_pass':
        return True, 'baseline-pass'
    if mode == 'all_blocked':
        return (cond == 0), 'baseline'
    rule = table.rule(cond)
    if rule == 'pass':
        return True, 'pass'
    if rule == 'pass_variant':
        return True, 'variant'
    if rule == 'pass_state_family_crouch':
        ok = (src_row.get('stance_slot') in CROUCH_FAMILY_STANCE
              or src_row.get('state_word') in CROUCH_FAMILY_WORDS)
        return ok, 'state-family-crouch' if ok else 'blocked-crouch-family'
    if rule == 'pass_state_family_3884':
        ok = (src_row.get('stance_slot') in F3884_STANCE
              or src_row.get('state_word') in F3884_WORDS)
        return ok, 'state-family-3884' if ok else 'blocked-3884-family'
    if rule == 'pass_throw_gate':
        return True, 'throw-gate'
    if rule == 'pass_distance_flagged':
        return True, 'distance-gated'
    return False, rule  # blocked_dispatch / blocked_unknown

# ---------------------------------------------------------------- input parse
STEP_PREFIXES = ('WS', 'FC', 'BT', 'CD', 'SS')

def parse_step(step):
    """WH notation step -> (state_prefix, dirspec, buttons)
    dirspec: ('dirs', {numpad,...}) | ('seq', [numpad,...]) | ('hex', code) | None
    buttons: set of LP/RP/LK/RK (empty = direction-only step)"""
    s = step.strip()
    prefix = None
    for p in STEP_PREFIXES:
        if s.upper().startswith(p + '+') or s.upper().startswith(p + ' '):
            prefix = p
            s = s[len(p):].lstrip('+ ').strip()
            break
    if '+' in s:
        dpart, bpart = s.rsplit('+', 1)
        # buttons may be like "1+2" handled below; here bpart is last token
        tokens = s.split('+')
    else:
        tokens = [s]
    buttons = set()
    dirs = []
    motion = None
    for tok in tokens:
        t = tok.strip().lower()
        if t in MOTIONS and not isinstance(MOTIONS[t], str):
            motion = MOTIONS[t]
        elif t in ('f,f', 'b,b'):
            motion = MOTIONS[t]
        elif t in DIRNUM:
            dirs.append(DIRNUM[t])
        elif t and all(ch in '1234' for ch in t):
            for ch in t:
                buttons.add(BTN[ch])
        elif t in ('1+2', '2+1'):
            buttons.update({'LP', 'RP'})
        elif t == '':
            pass
        else:
            # unknown token (e.g. 'n' inside "f,n,d,d/f" handled by split on ',')
            pass
    if motion is not None:
        if isinstance(motion, str):
            return prefix, ('hex', motion.split(':')[1]), buttons
        return prefix, ('seq', motion), buttons
    if dirs:
        return prefix, ('dirs', set(dirs)), buttons
    return prefix, None, buttons

def parse_input(notation):
    """Full WH input string -> list of steps. Handles 'f,n,d,d/f+1' style:
    consecutive direction-only tokens merge into one motion step."""
    raw = [t.strip() for t in notation.split(',') if t.strip()]
    steps = []
    pending_dirs = []
    for tok in raw:
        pfx, dspec, btns = parse_step(tok)
        if dspec is not None and not btns and pfx is None:
            # direction-only token: accumulate
            if dspec[0] == 'dirs':
                pending_dirs.extend(sorted(dspec[1]))
            else:
                pending_dirs.append(dspec)
            continue
        if pending_dirs:
            seq = []
            for pd in pending_dirs:
                if isinstance(pd, tuple):
                    seq = pd  # a hex/seq spec overrides
                    break
                seq.append(pd)
            if isinstance(seq, list) and seq:
                dspec = ('seq', seq)
            pending_dirs = []
        steps.append((pfx, dspec, btns))
    if pending_dirs:
        seq = [pd for pd in pending_dirs if isinstance(pd, int)]
        if seq:
            steps.append((None, ('seq', seq), set()))
    return steps

# ---------------------------------------------------------------- branch match
def branch_buttons(cmd):
    return {t for t in re.split(r'[^A-Z]+', cmd or '') if t in ('LP', 'RP', 'LK', 'RK')}

def branch_dirs(cmd, hexs):
    """Return ('dirs', set) | ('seq', list) | ('hex', code) | ('any',) | ('common',) | None"""
    if cmd == '<common>':
        return ('common',)
    if cmd == 'any-button':
        return ('any',)
    m = re.match(r'^\[(.*)\]\(\d+f\)$', cmd or '')
    if m:
        inner = m.group(1)
        btns = branch_buttons(inner)
        seq = [int(x) for x in re.findall(r'\b[1-9]\b', inner.split('+')[0])]
        return ('seq', seq)
    try:
        h = int(hexs, 16)
    except Exception:
        h = 0
    if h in (0xC001, 0xC002):
        return ('hex', format(h, 'x'))
    if h >= 0xC000:
        return ('motion-other', h)
    head = (cmd or '').split('+')[0]
    dirs = set()
    for tok in head.split('/'):
        tok = tok.strip()
        if tok.isdigit():
            dirs.add(int(tok))
    if dirs:
        return ('dirs', dirs)
    return None

def step_matches_branch(step, br):
    pfx, dspec, btns = step
    bbtns = branch_buttons(br.get('command'))
    bdirs = branch_dirs(br.get('command'), br.get('command_hex'))
    if bdirs and bdirs[0] == 'common':
        return False  # common-table links are not input steps
    if bdirs and bdirs[0] == 'any':
        return bool(btns)  # any-button catch-all matches any button step
    if bbtns != btns:
        return False
    if dspec is None:
        return bdirs is None
    if dspec[0] == 'dirs':
        return bool(bdirs) and bdirs[0] == 'dirs' and bool(dspec[1] & bdirs[1])
    if dspec[0] == 'seq':
        return bool(bdirs) and bdirs[0] == 'seq' and list(dspec[1]) == list(bdirs[1])
    if dspec[0] == 'hex':
        return bool(bdirs) and bdirs[0] == 'hex' and dspec[1] == bdirs[1]
    return False

# ---------------------------------------------------------------- graph + walk
FREE_COMMANDS = ('<common>', '<end>')

def is_free_branch(br):
    if br.get('command') in FREE_COMMANDS:
        return True
    try:
        return int(br.get('command_hex'), 16) == 0xC00D  # no-input auto-transition
    except Exception:
        return False

def is_state_edge(br):
    """A branch with no specific buttons is a state transition, not an input
    step: '<common>'/'<end>'/no-input links, direction-only branches, and
    directional 'any-button' branches (e.g. '3+any-button' moves between
    crouch sub-states — kuma rows 12-16)."""
    if is_free_branch(br):
        return True
    return not branch_buttons(br.get('command'))

def free_closure(bank, rows, table, mode='decoded'):
    """Expand a row set over zero-input state edges whose condition the
    table allows. This models how control reaches the state rows a string
    actually starts from (hub -> crouch family -> sub-states)."""
    seen = set(rows)
    frontier = list(rows)
    while frontier:
        nxt = []
        for row in frontier:
            src = bank.rows.get(row)
            if src is None:
                continue
            for br in src.get('branches') or []:
                if not is_state_edge(br):
                    continue
                if br.get('command') == '<end>':
                    ok = True
                else:
                    ok, _ = branch_passable(table, br, src, mode)
                if not ok:
                    continue
                tgt = bank.resolve(br.get('target_slot'))
                if tgt is not None and tgt not in seen:
                    seen.add(tgt)
                    nxt.append(tgt)
        frontier = nxt
    return seen

def walk2(bank, steps, table, mode='decoded', starts=None):
    """String walk with state-edge closure around every input step."""
    if starts is None:
        starts = bank.standing_hubs()
    frontier = free_closure(bank, set(starts), table, mode)
    for step in steps:
        nxt = set()
        for row in frontier:
            src = bank.rows.get(row)
            if src is None:
                continue
            for br in src.get('branches') or []:
                if is_state_edge(br):
                    continue
                if not step_matches_branch(step, br):
                    continue
                ok, _ = branch_passable(table, br, src, mode)
                if not ok:
                    continue
                tgt = bank.resolve(br.get('target_slot'))
                if tgt is not None:
                    nxt.add(tgt)
        if not nxt:
            return set()
        frontier = free_closure(bank, nxt, table, mode)
    return frontier

def transition_support(bank, steps, expected, table, mode='decoded'):
    """Does the expected row have an inbound branch that (a) spells the
    record's final input step and (b) the condition table allows from the
    source row? This tests the condition table at the transition level,
    independent of start-anchor choices."""
    if not steps:
        return False
    last = steps[-1]
    slot_of = set()
    for i, r in enumerate(bank.mindex):
        if r == expected:
            slot_of.add(i)
    if not slot_of:
        return False
    for m in bank.data['moves']:
        for br in m.get('branches') or []:
            if br.get('target_slot') not in slot_of:
                continue
            if is_state_edge(br):
                continue
            if not step_matches_branch(last, br):
                continue
            ok, _ = branch_passable(table, br, m, mode)
            if ok:
                return True
    return False

class Bank:
    def __init__(self, path):
        d = json.load(open(path))
        self.name = d['bank']
        self.data = d
        self.rows = {m['row']: m for m in d['moves']}
        self.mindex = d['move_index']

    def resolve(self, slot):
        if slot is None or slot >= len(self.mindex):
            return None
        r = self.mindex[slot]
        if r == EMPTY or isinstance(r, str):
            return None
        return r

    def standing_hubs(self):
        return [m['row'] for m in self.data['moves']
                if m['stance_slot'] == 3 and m['state_word'] == '0x00000842'
                and len(m.get('branches') or []) >= 40]

    def crouch_hubs(self):
        return [m['row'] for m in self.data['moves']
                if m['state_word'] == '0x00022829' or m['stance_slot'] in (57, 58)]

# ---------------------------------------------------------------- validation
def load_banks(banks_dir):
    out = {}
    for name in os.listdir(banks_dir):
        if name.startswith('moveset_') and name.endswith('.json'):
            b = Bank(os.path.join(banks_dir, name))
            short = name[len('moveset_'):-len('.json')]
            out[short] = b
    return out

def validate(movesets_dir, banks_dir, table, modes=('decoded', 'all_blocked', 'all_pass')):
    banks = load_banks(banks_dir)
    results = {m: Counter() for m in modes}
    tsupport = {m: 0 for m in modes}
    set_sizes = []
    detail_miss = []
    files = sorted(f for f in os.listdir(movesets_dir) if f.endswith('.json'))
    total = 0
    for fn in files:
        d = json.load(open(os.path.join(movesets_dir, fn)))
        moves = d.get('moves') or {}
        if not isinstance(moves, dict):
            continue
        # anchors: this file's own pre-existing (non-fix) anim_t3 rows per bank
        anchors = defaultdict(set)
        for mv0 in moves.values():
            if isinstance(mv0, dict) and not mv0.get('provenance_fix'):
                a0 = mv0.get('anim_t3') or {}
                if a0.get('bank') and a0.get('row') is not None:
                    anchors[a0['bank']].add(a0['row'])
        for key, mv in moves.items():
            if not isinstance(mv, dict) or not mv.get('provenance_fix'):
                continue
            at3 = mv.get('anim_t3') or {}
            bank_name = at3.get('bank')
            expected = at3.get('row')
            if bank_name not in banks or expected is None:
                continue
            notation = mv.get('input')
            if not notation:
                continue
            total += 1
            bank = banks[bank_name]
            steps = parse_input(str(notation))
            starts = set(bank.standing_hubs()) | anchors.get(bank_name, set())
            first_prefix = steps[0][0] if steps else None
            if first_prefix in ('WS', 'FC'):
                starts |= set(bank.crouch_hubs())
            starts = sorted(starts)
            proof = (mv['provenance_fix'].get('method') or '').split()[-1]
            for mode in modes:
                if transition_support(bank, steps, expected, table, mode):
                    tsupport[mode] += 1
                reached = walk2(bank, steps, table, mode, starts)
                if mode == 'decoded':
                    set_sizes.append(len(reached))
                if expected in reached:
                    kind = 'UNIQUE-HIT' if len(reached) == 1 else 'HIT'
                elif reached:
                    kind = 'MISS'
                else:
                    kind = 'NO-WALK'
                results[mode][kind] += 1
                results[mode][f'byproof-{proof}-{kind}'] += 1
                if mode == 'decoded' and kind in ('MISS', 'NO-WALK') and len(detail_miss) < 40:
                    detail_miss.append({'file': fn, 'move': key, 'input': notation,
                                        'bank': bank_name, 'expected': expected,
                                        'proof': proof, 'kind': kind,
                                        'reached': sorted(reached)[:6]})
    mean_size = (sum(set_sizes) / len(set_sizes)) if set_sizes else 0
    return total, results, detail_miss, mean_size, tsupport

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--banks-dir', default='teardown/tekken3/movesets')
    ap.add_argument('--table', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    't3_condition_codes.json'))
    sub = ap.add_subparsers(dest='cmd', required=True)
    w = sub.add_parser('walk')
    w.add_argument('--bank', required=True)
    w.add_argument('--input', required=True)
    w.add_argument('--start', choices=('standing', 'crouch'), default='standing')
    v = sub.add_parser('validate')
    v.add_argument('--movesets-dir', default='game/assets/movesets')
    args = ap.parse_args()
    table = Table(args.table)
    if args.cmd == 'walk':
        banks = load_banks(args.banks_dir)
        bank = banks[args.bank]
        steps = parse_input(args.input)
        starts = bank.crouch_hubs() if args.start == 'crouch' else bank.standing_hubs()
        reached = walk2(bank, steps, table, 'decoded', starts)
        print(f"bank={bank.name} input={args.input!r} steps={len(steps)} starts={starts}")
        if not reached:
            print("no walk reaches a terminal row")
        else:
            print(f"terminal candidate rows ({len(reached)}): {sorted(reached)}")
    else:
        total, results, miss, mean_size, tsupport = validate(args.movesets_dir, args.banks_dir, table)
        print(f"provenance_fix records validated: {total}")
        print(f"decoded-mode mean terminal set size: {mean_size:.1f} rows")
        for mode in results:
            print(f"[{mode}] transition-support (final step condition-passable): "
                  f"{tsupport[mode]}/{total}")
        for mode, res in results.items():
            hits = res['UNIQUE-HIT'] + res['HIT']
            print(f"[{mode}] UNIQUE-HIT={res['UNIQUE-HIT']} HIT={res['HIT']} "
                  f"MISS={res['MISS']} NO-WALK={res['NO-WALK']}  reach-rate={hits}/{total}")
            for proof in ('A', 'B', 'C', 'S'):
                uh, h = res[f'byproof-{proof}-UNIQUE-HIT'], res[f'byproof-{proof}-HIT']
                m_, nw = res[f'byproof-{proof}-MISS'], res[f'byproof-{proof}-NO-WALK']
                if uh + h + m_ + nw:
                    print(f"    proof {proof}: hit={uh + h} miss={m_} no-walk={nw}")
        print("\nsample decoded-mode misses:")
        for m in miss[:15]:
            print(" ", m)

if __name__ == '__main__':
    main()
