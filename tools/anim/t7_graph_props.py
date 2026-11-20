#!/usr/bin/env python3
"""t7_graph_props.py: import EVERY extra move property list of a T7 moveset (same motbin JSON the graph importer reads),
with source indices, into <dir>/graph.props.json (format wh-t7-graph-props/1). Separate from graph.json so the clip shards
(which carry graph.json's sha256) stay valid.

Layout (TekkenMovesetExtractor motbinExport.py, T7): move.extra_prop_idx -> rows {starting_frame, id, value} (struct 0xC),
each list ends at the all-zero row; move.start_prop_idx / end_prop_idx -> rows {requirements_idx, extraprop, value}.
Kept raw: starting_frame flag bits and property semantics are NOT interpreted here.

Exe evidence for the player-variable writers (TekkenGame-Win64-Shipping.exe property switch 0x1407198ac, id - 0x8001
jump table 0x14071fca8): 0x8414/0x8415/0x8416 set/add/sub [self+0x938]; 0x80ed/0x8112/0x8113 set/add/sub [self+0x964];
0x8106/0x8107/0x8108 set/add/sub self player flag [0x968 + idx*2]; 0x8109.. the same on the opponent.
usage: t7_graph_props.py --mothead <dir> --code kin --graph game/assets/anim/t7/king/graph.json --out .../graph.props.json
"""
import argparse, hashlib, json, os

VAR_WRITERS = {0x8414: ['set', 0x938], 0x8415: ['add', 0x938], 0x8416: ['sub', 0x938],
               0x80ed: ['set', 0x964], 0x8112: ['add', 0x964], 0x8113: ['sub', 0x964]}
FLAG_WRITERS = {0x8106: ['set', 'self'], 0x8107: ['add', 'self'], 0x8108: ['sub', 'self'],
                0x8109: ['set', 'opponent'], 0x810a: ['add', 'opponent']}
NONE = 0xFFFFFFFFFFFFFFFF


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--mothead', required=True); ap.add_argument('--code', required=True)
    ap.add_argument('--graph', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    jp = os.path.join(a.mothead, 'json', '%smot.json' % a.code)
    jb = open(jp, 'rb').read(); raw = json.loads(jb)['raw']
    EP, mv = raw['extra_move_properties'], raw['moves']
    SE = raw.get('move_end_props') if isinstance(raw.get('move_end_props'), list) else []
    SS = raw.get('move_start_props') if isinstance(raw.get('move_start_props'), list) else []

    def plist(rows, i, kind):
        out = []
        if i == NONE or i >= len(rows):
            return out
        while i < len(rows):
            r = rows[i]
            if kind == 'extra':
                if r['id'] == 0 and r['starting_frame'] == 0 and r['value'] == 0:
                    break
                out.append([i, r['starting_frame'], r['id'], r['value']])
            else:
                if r['extraprop'] == 0 and r['requirements_idx'] == 0 and r['value'] == 0:
                    break
                out.append([i, r['requirements_idx'], r['extraprop'], r['value']])
            i += 1
        return out
    moves = []
    for m in mv:
        moves.append({'extra': plist(EP, m['extra_prop_idx'], 'extra'), 'start': plist(SS, m['start_prop_idx'], 'se'),
                      'end': plist(SE, m['end_prop_idx'], 'se'),
                      # move word +0x56: on entry the exe turns the yaw by it (0x14074ffe7..0x14075003d)
                      'turn_0x56': m['u_0x56']})
    g = open(a.graph, 'rb').read()
    out = {'format': 'wh-t7-graph-props/1', 'source_json_sha256': sha(jb), 'graph_sha256': sha(g),
           'fields': {'extra': ['source_index', 'starting_frame_raw', 'id', 'value'],
                      'start/end': ['source_index', 'requirements_idx', 'extraprop', 'value']},
           'counts': {'extra_rows': len(EP), 'start_rows': len(SS), 'end_rows': len(SE),
                      'moves_with_extra': sum(1 for x in moves if x['extra'])},
           'var_writers': {hex(k): v for k, v in VAR_WRITERS.items()}, 'flag_writers': {hex(k): v for k, v in FLAG_WRITERS.items()},
           'moves': moves}
    open(a.out, 'w').write(json.dumps(out, separators=(',', ':')))
    print('GRAPH_PROPS', out['counts'], '->', a.out, os.path.getsize(a.out), 'B')


if __name__ == '__main__':
    main()
