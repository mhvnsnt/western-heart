#!/usr/bin/env python3
"""t7_graph_import.py: import a Tekken 7 character's COMPLETE move graph (every move, every cancel incl. group
cancels, input sequences, requirements, aliases, hit data, animation refs) from its motbin into one runtime graph
the game interprets directly (game/js/t7graph.js). Source-driven and whole-bank: nothing is hand-picked, every source
identifier is retained (move index + name, cancel/group index, requirement index, sequence index, extradata index).

Decoding (each verified, see docs/proof/2026-11-10/t7-full-graph/README.md):
  - cancel command: low 32 bits direction mask (bits 1..9 = d/b d d/f b n f u/b u u/f, 0 = any), high 32 bits buttons
    (bits 0..3 = 1..4, bit 4 = RA) | 0x40000000 press flag; 0x8000 = AUTO (end/transition), 0x8001..0x800C engine
    specials (0x800B = group-cancel ref, 0x800C = group end), 0x800D..0x8FFF = input sequence (cmd - 0x800D)
    — same layout as TKMovesets2 Editor_t7_Commands.cpp getCommandString (Kiloutre, a1b1917a);
  - group cancels: 40-byte <QQQIIIHH rows (cmd, req, extradata, start, end, starting_frame, move, option);
  - input sequences: {input_window_frames, input_amount, input_idx} -> inputs {direction, button}, chronological;
  - requirements: {condition, param} rows ending at condition 881;
  - move ids >= 0x8000 are aliases: motbin header u16[148] at 0x28 (TekkenMovesetExtractor motbinExport.py T7 layout);
  - anim bank: anim_id & 0xC000 -> 0x4000 <code>rotsm.arc, 0x8000 common.arc, 0 <code>mot.bin.
Kept raw on purpose (meaning not decoded, never guessed): cancel_extradata values, cancel option, unknown
requirement conditions.

usage: python3 tools/anim/t7_graph_import.py --mothead <GRE>/teardown/tekken7-steam/tkdata/mothead --code kin \
         --out game/assets/anim/t7/king/graph.json [--coverage docs/proof/.../coverage.json]
Deterministic: same inputs -> byte-identical output (the source sha256s are recorded in the file)."""
import argparse, hashlib, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from t7_move_resolve import Motbin  # noqa: E402  (clip(): bank/clip/format of an anim_id)

AUTO, GROUP_REF, GROUP_END, SEQ0, SEQ_MAX = 0x8000, 0x800B, 0x800C, 0x800D, 0x8FFF
REQ_END = 881
PRESS = 0x40000000


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--mothead', required=True); ap.add_argument('--code', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--coverage')
    a = ap.parse_args()
    mb = Motbin(a.mothead, a.code)
    G = mb.G; raw = mb.js['raw']
    jpath = G + 'json/' + mb._json_name(); bpath = G + 'bin/%smot.bin' % a.code
    binb = open(bpath, 'rb').read()
    aliases = list(struct.unpack_from('<148H', binb, 0x28))
    mv, C, CE, R, HC = raw['moves'], raw['cancels'], raw['cancel_extradata'], raw['requirements'], raw['hit_conditions']
    seqs, inputs = raw['input_sequences'], raw['inputs']

    # requirements: index -> [[cond, param], ...] up to (excluding) the 881 terminator
    req_cache = {}
    def reqs(i):
        if i not in req_cache:
            out, j = [], i
            while j < len(R) and R[j]['condition'] != REQ_END:
                out.append([R[j]['condition'], R[j]['param']]); j += 1
            req_cache[i] = out
        return req_cache[i]

    def cancel_row(d, b, req, xd, ds, de, sf, mid, opt, grp):
        # [cmd, dir_mask, buttons(0..4 bits), press(0/1), seq(-1|idx), req_idx, start, end, starting_frame, to, option,
        #  extradata_value(raw), group_row(-1|idx)]
        seq = d - SEQ0 if SEQ0 <= d <= SEQ_MAX else -1
        return [d, d if d < AUTO else 0, b & 0x1F, 1 if b & PRESS else 0, seq, req, ds, de, sf, mid, opt,
                CE[xd]['value'] if 0 <= xd < len(CE) else None, grp]

    moves = []
    for i, m in enumerate(mv):
        rows, j = [], m['cancel_idx']
        while j < len(C):
            c = C[j]; d = c['direction']
            if d == GROUP_REF:
                k = c['move_id']
                while k < len(mb.groups):
                    cmd, greq, gxd, gds, gde, gsf, gmid, gopt = mb.groups[k]
                    gd = cmd & 0xFFFFFFFF
                    if gd == GROUP_END: break
                    rows.append(cancel_row(gd, cmd >> 32, greq, gxd, gds, gde, gsf, gmid, gopt, k)); k += 1
            else:
                rows.append(cancel_row(d, c['button'], c['requirements_idx'], c['extradata_idx'], c['detection_start'],
                                       c['detection_end'], c['starting_frame'], c['move_id'], c['cancel_option'], -1))
            if d == AUTO: break
            j += 1
        mm = mb.moves[i]; clip = mb.clip(mm)
        hc = HC[m['hit_condition_idx']] if 0 <= m['hit_condition_idx'] < len(HC) else None
        moves.append({'id': i, 'name': m['name'], 'anim': m['anim_name'], 'anim_id': m['anim_id'],
                      'bank': clip.get('bank'), 'clip': clip.get('clip'), 'fmt': clip.get('fmt'),
                      'len': m['anim_len'], 'first_active': m['first_active_frame'], 'last_active': m['last_active_frame'],
                      'hitlevel': m['hitlevel'], 'damage': hc['damage'] if hc else 0, 'transition': m['transition'],
                      'airborne': [m['airborne_start'], m['airborne_end']], 'cancels': rows})
    used_reqs = sorted({r[5] for m in moves for r in m['cancels']})
    graph = {'format': 'wh-t7-graph/1', 'code': a.code,
             'source': {'json': os.path.basename(jpath), 'json_sha256': sha(jpath), 'bin_sha256': sha(bpath),
                        'decoder_refs': ['TKMovesets2 a1b1917a Editor_t7_Commands.cpp (command layout)',
                                         'TekkenMovesetExtractor motbinExport.py (alias table 0x28 u16[148])']},
             'cancel_fields': ['cmd', 'dir', 'buttons', 'press', 'seq', 'req', 'start', 'end', 'starting_frame', 'to',
                               'option', 'extradata', 'group_row'],
             'aliases': aliases, 'stance': aliases[1],
             'requirements': {str(i): reqs(i) for i in used_reqs},
             'sequences': [{'window': s['input_window_frames'], 'inputs': [[e['direction'], e['button'] & 0x1F,
                            1 if e['button'] & PRESS else 0] for e in inputs[s['input_idx']:s['input_idx'] + s['input_amount']]]}
                           for s in seqs],
             'moves': moves}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w') as f: json.dump(graph, f, separators=(',', ':'), sort_keys=True)
    ncan = sum(len(m['cancels']) for m in moves)
    print('graph', a.out, 'moves', len(moves), 'cancel rows (groups inlined)', ncan, 'requirements', len(used_reqs),
          'sequences', len(seqs), 'bytes', os.path.getsize(a.out))
    if a.coverage: coverage(graph, a.coverage)


def resolve(graph, mid):
    return graph['aliases'][mid - 0x8000] if mid >= 0x8000 and mid - 0x8000 < len(graph['aliases']) else mid


def coverage(graph, out):
    """Reachability from the stance over the whole graph, edges split by requirement class, plus clip formats."""
    conds = {}
    for k, rows in graph['requirements'].items():
        conds[k] = sorted({c for c, _ in rows})
    seen, order, q = set(), [], [graph['stance']] + [resolve(graph, 0x8000 + i) for i in range(len(graph['aliases']))]
    gated_only = set()
    free_seen = set(); fq = [graph['stance']]
    while fq:  # requirement-free reachability (every requirement on the path is 'always')
        m = fq.pop()
        if m in free_seen or m >= len(graph['moves']): continue
        free_seen.add(m)
        for r in graph['moves'][m]['cancels']:
            if not graph['requirements'].get(str(r[5])) or all(c == 0 for c, _ in graph['requirements'][str(r[5])]):
                fq.append(resolve(graph, r[9]))
        fq.append(resolve(graph, graph['moves'][m]['transition']))
    while q:
        m = q.pop()
        if m in seen or m >= len(graph['moves']): continue
        seen.add(m); order.append(m)
        for r in graph['moves'][m]['cancels']: q.append(resolve(graph, r[9]))
        q.append(resolve(graph, graph['moves'][m]['transition']))
    fmts = {}
    for m in seen: fmts[graph['moves'][m]['fmt']] = fmts.get(graph['moves'][m]['fmt'], 0) + 1
    anims = sorted({(graph['moves'][m]['bank'], graph['moves'][m]['clip']) for m in seen}, key=str)
    allc = {}
    for rows in graph['requirements'].values():
        for c, _ in rows: allc[c] = allc.get(c, 0) + 1
    rep = {'moves_total': len(graph['moves']), 'reachable_any_requirement': len(seen),
           'reachable_requirement_free': len(free_seen), 'unreachable': len(graph['moves']) - len(seen),
           'reachable_clip_formats': fmts, 'reachable_unique_clips': len(anims),
           'requirement_conditions_used': dict(sorted(allc.items())),
           'reachable_moves': sorted(seen),
           'reachable_clips': [[b, c, f] for (b, c), f in sorted({(graph['moves'][m]['bank'], graph['moves'][m]['clip']):
                               graph['moves'][m]['fmt'] for m in seen}.items(), key=str)]}
    json.dump(rep, open(out, 'w'), indent=1, sort_keys=True)
    print('coverage', json.dumps({k: v for k, v in rep.items() if k not in ('requirement_conditions_used', 'reachable_moves', 'reachable_clips')}))


if __name__ == '__main__':
    main()
