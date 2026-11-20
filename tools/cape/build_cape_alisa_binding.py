#!/usr/bin/env python3
"""Build game/data/cape-alisa-binding.json (owner t118u #4: Cape Jones replaces Alisa).

Additive mapping only: reads Alisa's reference frame data (docs/t7t8-reference/frame-data-t8-full/alisa.json)
and binds every Alisa move to fighter id `cyborgx` (display name CAPE JONES) with a T3 action slot to animate it.
Alisa's original files are never edited. Frame data source is T8 (allowed under owner law t121u). Slot is a mechanical rule (throw -> grab, else by damage).
No Alisa animation bank exists yet; anim_source stays PENDING until decoded from T5/T6/T7/T8/TTT2 (never T3).
"""
import json, re, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = 'docs/t7t8-reference/frame-data-t8-full/alisa.json'
src = json.load(open(os.path.join(ROOT, SRC)))

def dmg(m):
    nums = [int(x) for x in re.findall(r'\d+', m.get('damage') or '')]
    return sum(nums)

def slot(m):
    inp = (m.get('input') or '').replace(' ', '')
    if re.search(r'(1\+3|2\+4)', inp) and 'throw' in ((m.get('notes') or '') + (m.get('name') or '')).lower() or (m.get('target') or '').startswith('t'):
        return 'grab'
    d = dmg(m)
    return 'light' if d < 12 else 'medium' if d < 20 else 'heavy'

moves = []
for m in src['moves']:
    moves.append({'alisa_id': m['id'], 'name': m.get('name'), 'input': m.get('input'),
                  'damage': m.get('damage'), 'startup': m.get('startup'), 'target': m.get('target'),
                  'slot': slot(m), 'anim_source': 'PENDING-T5-T8-TTT2'})
out = {
    'format': 'wh-cape-alisa-binding/1',
    'owner': 't118u #4 (2026-10-23): Cape Jones replaces Alisa; takes her moveset + animations plus his own extras. Secret identity Cyborg X; called Cape Jones in story.',
    'fighter_id': 'cyborgx', 'display_name': 'CAPE JONES', 'secret_identity': 'CYBORG X', 'replaces': 'Alisa',
    'model': 'cape-jones', 'source_frame_data': SRC, 'source_license': src.get('license'),
    'anim_bank_status': 'MISSING: no Alisa animation bank in game. Owner law t121u: motions must come from T5/T6/T7/T8/TTT2 teardowns; Tekken 3 is NOT a source. The game currently falls back to the gunjack T3 bank for cyborgx; that fallback is logged here as a last resort only and must be replaced.',
    'source_law': 'owner t121u 2026-10-23: no Tekken 3 as a source; T5/T6/T7/T8/TTT2 only; T3 = logged last resort.',
    't3_last_resort_log': [{'what': 'cyborgx fight animation', 'current_bank': 'game/assets/anim/t3/gunjack (T3)', 'reason': 'no Alisa bank decoded from T5-T8/TTT2 yet', 'logged': '2026-10-23 CT'}],
    'extras': [], 'extras_note': 'Cape-only extra moves: none in canon yet; owner to supply (not invented).',
    'count': len(moves), 'moves': moves,
}
p = os.path.join(ROOT, 'game', 'data', 'cape-alisa-binding.json')
json.dump(out, open(p, 'w'), indent=1); open(p, 'a').write('\n')
from collections import Counter
print(p, len(moves), dict(Counter(x['slot'] for x in moves)))
