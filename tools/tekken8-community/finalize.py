"""Finalize T8 join outputs: burger wavu-only pass, class rollup, clip-maps v2."""
import json, os, sys, collections, re
sys.path.insert(0, '/home/hatch/workspace/agent-ops/t7-clip-lane/worker-b/tools')
from join_engine import wh_input_canon, canon_notation

OUT = '/tmp/t8src/landing/clip-maps'
os.makedirs(OUT, exist_ok=True)
SRC = '/tmp/t8src/join-out'
WB = '/home/hatch/workspace/agent-ops/t7-clip-lane/worker-b'
WC = '/home/hatch/workspace/agent-ops/t8-community-lane/worker-c'

CODES = {'pantera': 'PGN', 'phantom': 'CML', 'skull': 'CHT', 'kinpo': 'DER',
         'demonio': 'ANT', 'diablo': 'BEE', 'scimitar': 'HRS', 'burger': None}
BASES = {'pantera': 'King', 'phantom': 'Yoshimitsu', 'skull': 'Bryan', 'burger': 'Bob',
         'kinpo': 'Asuka', 'demonio': 'Jin', 'diablo': 'Heihachi', 'scimitar': 'Shaheen'}

def t7_class(reason):
    r = reason or ''
    if r.startswith('no MVL row'):
        return 'no_evidence'
    if r.startswith('MVL name match'):
        return 'notation_differs'
    if r.startswith('multiple motbin terminals'):
        return 'ambiguous_pool'
    if 'no attack-class' in r:
        return 'mvl_matched_graph_gap'
    if 'motbin graph candidate exists' in r:
        return 'graph_only_held'
    return 'other'

def norm_name(n):
    return re.sub(r'[^a-z0-9]+', '', (n or '').lower())

def burger_records():
    bob = json.load(open(f'{WC}/bob-t8-movelist.json'))
    moves = bob['moves'] if isinstance(bob, dict) else bob
    by_steps = {}
    for mv in moves:
        nota = mv['notation']
        for a, b in [('df', 'd/f'), ('db', 'd/b'), ('uf', 'u/f'), ('ub', 'u/b')]:
            nota = re.sub(r'(?<![a-zA-Z])' + a + r'(?=\+|,|$)', b, nota)
        _, steps = canon_notation(nota)
        if steps:
            by_steps.setdefault(tuple(steps), []).append(mv)
    mp = json.load(open(f'{WB}/burger-mapping.json'))
    targets = [m for m in mp['moves'] if m['status'] == 'unmapped']
    recs = []
    for t in targets:
        _, steps = wh_input_canon(t['wh_input'])
        rows = by_steps.get(tuple(steps), [])
        rec = {'t7_id': t['t7_id'], 'wh_key': t.get('wh_key'), 'input': t['wh_input'],
               'wh_name': t.get('wh_name'), 't7_reason': t['reason']}
        if rows:
            named = [r for r in rows if norm_name(r.get('name')) == norm_name(t.get('wh_name'))]
            pick = named[0] if named else rows[0]
            rec.update({'status': 'movelist_only', 'grade': 'medium',
                        't8_id': pick['t8_id'], 't8_move_name': pick.get('name'),
                        'startup': pick.get('startup'), 'damage': pick.get('damage'),
                        'source': 'wavu-tekkendocs-bob',
                        'evidence': ['wavu_name_notation_exact' if named else 'wavu_notation_match']})
        else:
            rec.update({'status': 'unmapped', 'reason': 'no_t8_evidence',
                        'source': 'wavu-tekkendocs-bob'})
        recs.append(rec)
    return recs

all_records = {}
for wh in ['pantera', 'phantom', 'skull', 'kinpo', 'demonio', 'diablo', 'scimitar']:
    d = json.load(open(f'{SRC}/{wh}-t8.json'))
    all_records[wh] = d['records']
all_records['burger'] = burger_records()

rollup = {}
class_tot = collections.Counter()
class_res = collections.defaultdict(collections.Counter)
for wh, recs in all_records.items():
    st = collections.Counter()
    for r in recs:
        cls = t7_class(r['t7_reason'])
        r['t7_class'] = cls
        class_tot[cls] += 1
        outcome = r['status'] if r['status'] != 'mapped' else 'mapped_' + r['grade']
        st[outcome] += 1
        class_res[cls][outcome] += 1
    rollup[wh] = {'targets': len(recs), 'stats': dict(st)}
print('class totals:', dict(class_tot))
for cls in ['no_evidence', 'notation_differs', 'ambiguous_pool', 'mvl_matched_graph_gap', 'graph_only_held', 'other']:
    print(cls, dict(class_res[cls]))
pool_resolved = sum(class_res[c].get('mapped_high', 0) + class_res[c].get('mapped_medium', 0) + class_res[c].get('movelist_only', 0) for c in ['no_evidence', 'notation_differs'])
pool_total = sum(class_tot[c] for c in ['no_evidence', 'notation_differs'])
print(f'POOL(81): resolved {pool_resolved}/{pool_total}')
tot_res = sum(v.get('mapped_high', 0) + v.get('mapped_medium', 0) + v.get('movelist_only', 0) for v in class_res.values())
print(f'ALL(300): resolved {tot_res}/300')

EXPORT_SRC = {
    'pantera': 'kaiutzi21/Tekken8Movesets t8_KING_v2/t8_KING.json (CC BY-NC 4.0)',
    'phantom': 'kaiutzi21/Tekken8Movesets t8_YOSHIMITSURUGI/t8_YOSHIMITSU.json (CC BY-NC 4.0)',
    'skull': 'kaiutzi21/Tekken8Movesets t8_BYRON/t8_BRYAN.json (CC BY-NC 4.0)',
    'kinpo': 'tekkenmods 6006 Screw Combos pack, t8_asukaEDIT/t8_ASUKA.json (JoydurnYup)',
    'demonio': 'kaiutzi21/Tekken8Movesets t8_JINBOSLICE/t8_JIN.json (CC BY-NC 4.0)',
    'diablo': 'kaiutzi21/Tekken8Movesets t8_HEIHACHI/t8_HEIHACHI.json (CC BY-NC 4.0)',
    'scimitar': 'kaiutzi21/Tekken8Movesets t8_SHAHEENIBRATATINI/t8_SHAHEEN.json (CC BY-NC 4.0)',
    'burger': 'no community export exists (Bob = T8 Season 3 DLC 2026-08); wavu movelist only',
}
for wh, recs in all_records.items():
    moves = []
    st = collections.Counter()
    for r in recs:
        st[r['status'] if r['status'] != 'mapped' else 'mapped_' + r['grade']] += 1
        mv = {'wh_key': r.get('wh_key'), 'wh_name': r.get('wh_name'), 'wh_input': r['input'],
              't7_id': r.get('t7_id'), 'status': r['status'],
              'confidence': r.get('grade'), 'reason': r.get('reason'),
              't7_class': r['t7_class'], 'evidence': r.get('evidence', []),
              'source': r.get('source')}
        if r['status'] == 'mapped':
            mv.update({'t8_move_index': r['t8_move_index'], 't8_move_name': r['t8_move_name'],
                       't8_anim_name': r.get('t8_anim_name'), 'startup': r.get('startup'),
                       'damage': r.get('damage'),
                       'clip': {'status': 'anim_name_resolved_no_bytes',
                                'note': 'T8 animation bytes live in the character anmbin/mota banks; only TKData packages carry anmbin (King package stored in GRE release t8-community-pieces-v1).'}})
            if r.get('wavu_conflict'):
                mv['wavu_conflict'] = True
            if r.get('alternates'):
                mv['alternates'] = [{'move': a['move'], 'name': a['name']} for a in r['alternates']]
        elif r['status'] == 'movelist_only':
            mv.update({'t8_id': r.get('t8_id'), 't8_move_name': r.get('t8_move_name'),
                       'startup': r.get('startup'), 'damage': r.get('damage'),
                       'clip': {'status': 'no_t8_export', 'note': 'movelist-level resolution only; no moveset export circulates for this character'}})
        else:
            mv['clip'] = {'status': 'unresolved'}
        moves.append(mv)
    doc = {'schema': 'wh-t8-clip-map/1', 'fighter': wh, 'base': BASES[wh],
           'base_code_tkdata': CODES[wh],
           'sources': {'export': EXPORT_SRC[wh],
                       'movelist': 'wavu.wiki via pbruvoll/tekkendocs json_movelist (unlicensed community frame data)',
                       'name_keys': 'AliK3112/tekken-8-movesets-scripts name_keys.json (45,716 entries)',
                       't7_record': f'game/assets/anim/t7/clip-maps/{wh}-clip-map.json'},
           'stats': dict(st), 'moves': moves}
    json.dump(doc, open(f'{OUT}/{wh}-clip-map.json', 'w'), indent=1)
    print('wrote', wh, dict(st))

json.dump({'rollup': rollup, 'class_totals': dict(class_tot),
           'class_resolution': {k: dict(v) for k, v in class_res.items()},
           'pool81': {'total': pool_total, 'resolved': pool_resolved}},
          open('/tmp/t8src/landing/rollup.json', 'w'), indent=1)
print('rollup written')
