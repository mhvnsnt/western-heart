#!/usr/bin/env python3
"""King T7 locomotion / sequence table dump (2026-11-10, Pantera pass 4). Read-only decode of the private motbin
JSON (the reverse-engineering repo, tkdata mothead json <code>mot.json) — no timings invented, nothing written there.
Usage: python3 tools/anim/t7_table_dump.py <mothead_dir> <code> out.json
Decodes (verified this pass):
  - input sequence cancel commands: index = cmd - 0x800D into raw.input_sequences (stride 16:
    input_window_frames, input_amount, unk_0x4, input_idx) -> raw.inputs[input_idx : +input_amount]
    ({direction, button}; listed chronologically, the LAST element carries press flag 0x40000000);
  - group cancels: own cancel cmd 0x800B -> group_cancels from move_id, 40-byte <QQQIIIHH rows
    (cmd, req, ext, detection_start, detection_end, starting_frame, move_id, option), ended by 0x800C;
  - requirements: raw.requirements[req_idx ...] rows {condition, param} until condition 881 (terminator).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t7_move_resolve as R

DN = {2: 'd/b', 4: 'd', 8: 'd/f', 16: 'b', 32: 'n', 64: 'f', 128: 'u/b', 256: 'u', 512: 'u/f'}
SPECIAL = {0x8000: 'END', 0x8001: 'f,f(0x8001)', 0x8002: 'b,b(0x8002)', 0x8003: '0x8003', 0x8004: '0x8004'}
MOVES = ['Kg_sDASHF', 'sDASH_00B', 'sDASH_00BLp', 'Kg_st2cr00B', 'Kg_st2cr00_', 'st2cr_00_Rv', 'sRUN__00F']

def main(mh, code, out):
    mb = R.Motbin(mh, code); raw = mb.js['raw']; by = {m['id']: m for m in mb.moves}; nm = {m['name']: m['id'] for m in mb.moves}
    seqs, inps, rq = raw['input_sequences'], raw['inputs'], raw['requirements']
    dd = lambda d: '|'.join(v for k, v in DN.items() if d & k) or ('any' if d == 0 else hex(d))
    def el(e):
        b = '+'.join(str(i + 1) for i in range(4) if e['button'] & (1 << i)); return dd(e['direction']) + ('+' + b if b else '')
    def seq(i):
        s = seqs[i]; return {'index': i, 'cmd': hex(0x800D + i), 'window': s['input_window_frames'],
                             'inputs': [el(e) for e in inps[s['input_idx']:s['input_idx'] + s['input_amount']]]}
    def reqs(i):
        o = []
        while i < len(rq):
            o.append([rq[i]['condition'], rq[i]['param']])
            if rq[i]['condition'] == 881: break
            i += 1
        return o
    def cmd(d):
        if 0x800D <= d < 0x800D + len(seqs): return 'seq:' + ','.join(seq(d - 0x800D)['inputs'])
        return SPECIAL.get(d, dd(d) if d < 0x8000 else hex(d))
    def links(m):
        o = []
        for c in m['cancels']:
            d = c['direction_raw']
            if d == 0x800B:
                j = c['move_id']
                while j < len(mb.groups):
                    g = mb.groups[j]; gd = g[0] & 0xffffffff
                    if gd == 0x800C: break
                    o.append({'src': 'group', 'cmd': cmd(gd), 'buttons': hex(g[0] >> 32), 'to': by.get(g[6], {}).get('name', g[6]),
                              'req': g[1], 'req_rows': reqs(g[1]), 'window': [g[3], g[4]], 'starting_frame': g[5]}); j += 1
            else:
                o.append({'src': 'own', 'cmd': cmd(d), 'buttons': hex(c['button_raw']), 'to': by.get(c['move_id'], {}).get('name', c['move_id']),
                          'req': c['requirements_idx'], 'req_rows': reqs(c['requirements_idx']), 'window': c['window'], 'starting_frame': c['starting_frame']})
                if d == 0x8000: break
        return o
    res = {'format': 'wh-t7-table-dump/1', 'code': code,
           'moves': {n: {'anim': by[nm[n]]['anim'], 'anim_id': hex(by[nm[n]]['anim_id']), 'links': links(by[nm[n]])} for n in MOVES if n in nm},
           'input_sequences': [seq(i) for i in range(len(seqs))]}
    json.dump(res, open(out, 'w'), indent=1)
    print(out, len(res['input_sequences']), 'sequences;', ', '.join(f"{k}:{len(v['links'])}" for k, v in res['moves'].items()))

if __name__ == '__main__':
    main(*sys.argv[1:4])
