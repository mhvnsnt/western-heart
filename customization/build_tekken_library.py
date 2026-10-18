#!/usr/bin/env python3
"""build_tekken_library.py — Lane H (creation suite).

Reads Lane F's per-fighter movelists (game/assets/movesets/*.json — READ ONLY,
never written) + the wrestling move database, and writes a DERIVED index for the
Create Fighter moveset editor:

    customization/create-fighter/data/TEKKEN-LIBRARY.json

Each entry: move_id, move_name, input (Tekken notation), damage, limb,
source, source_fighter, t3_command, preview_clip (T3 clip id for live preview),
anim_ref, properties, federation (True for wrestling-sourced moves mapped to
Tekken inputs — the federation rule: Tekken inputs are the language).

Re-run when Lane F's data grows:
    python3 customization/build_tekken_library.py
"""
import json, re, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))          # customization/
REPO = os.path.dirname(HERE)                               # repo root (worktree)
MOVESET_DIR = os.path.join(REPO, 'game', 'assets', 'movesets')
WRESTLE_DB = os.path.join(HERE, 'create-fighter', 'data', 'MOVE-DATABASE.json')
OUT = os.path.join(HERE, 'create-fighter', 'data', 'TEKKEN-LIBRARY.json')

T3_BASE = '../../game/assets/anim/t3/king_on_pantera_leoman/'  # relative to create-fighter page

def preview_clip_for(inp):
    """Honest heuristic: map a Tekken input to the closest real T3 clip we hold.
    A move with a real anim_ref always wins over this mapping (see DESIGN-v0.3)."""
    s = (inp or '').strip().lower()
    if s in ('1+3', '2+4'):
        return 't3_grab'
    if ',' in s:
        return 't3_heavy'                      # strings
    if re.search(r'qcf|qcb|hcf|hcb|\bdp\b|f,f|b,b|d,d|n,d', s):
        return 't3_heavy'                      # motion inputs = specials
    m = re.search(r'([1234])(\+[1234])*$', s)  # trailing limb number(s)
    if m:
        limbs = m.group(0).replace('+', '')
        if set(limbs) <= set('12'):
            return 't3_light'
        if set(limbs) <= set('34'):
            return 't3_medium'
        return 't3_heavy'
    return 't3_stance'

def safe_id(*parts):
    return 'T3-' + re.sub(r'[^A-Za-z0-9]+', '-', '-'.join(parts)).strip('-').upper()

def main():
    moves = []
    files = sorted(glob.glob(os.path.join(MOVESET_DIR, '*.json')))
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        fid = d.get('fighter', os.path.basename(f)[:-5])
        display = d.get('display', fid)
        for inp, m in (d.get('moves') or {}).items():
            moves.append({
                'move_id': safe_id(fid, inp),
                'move_name': m.get('name', f'{display} {inp}'),
                'input': m.get('input', inp),
                'damage': m.get('damage'),
                'limb': m.get('limb'),
                'startup': m.get('startup'),
                'source': 'tekken3',
                'source_fighter': fid,
                'source_display': display,
                't3_command': m.get('t3_command'),
                't3_row': m.get('t3_row'),
                'preview_clip': preview_clip_for(m.get('input', inp)),
                'anim_ref': None,
                'properties': ['throw'] if inp in ('1+3', '2+4') else [],
                'federation': False,
            })

    # Wrestling federation moves -> Tekken inputs (federation rule)
    throw_i = 0
    limb_i = 0
    limbs = ['1', '2', '3', '4']
    if os.path.exists(WRESTLE_DB):
        with open(WRESTLE_DB) as fh:
            wdb = json.load(fh)
        for m in wdb.get('sample_moves', []):
            slots = ' '.join(m.get('slot_eligibility') or []).lower()
            if 'finisher' in slots:
                tek = 'finisher'
            elif 'taunt' in slots:
                tek = 'taunt'
            elif 'grapple' in slots or 'throw' in slots or 'submission' in slots:
                tek = ['1+3', '2+4'][throw_i % 2]; throw_i += 1
            else:
                tek = limbs[limb_i % 4]; limb_i += 1
            moves.append({
                'move_id': m.get('move_id'),
                'move_name': m.get('move_name'),
                'input': tek,
                'damage': m.get('power'),
                'limb': None,
                'startup': None,
                'source': m.get('source'),
                'source_fighter': None,
                'source_display': m.get('source'),
                't3_command': None,
                't3_row': None,
                'preview_clip': preview_clip_for(tek) if tek not in ('finisher', 'taunt') else 't3_win_rp',
                'anim_ref': m.get('anim_ref'),
                'properties': m.get('properties') or [],
                'federation': True,
                'federation_note': 'wrestling-sourced move mapped to Tekken input (federation rule)',
                'wrestling_slots': m.get('slot_eligibility'),
            })

    out = {
        '_meta': {
            'built_by': 'customization/build_tekken_library.py (Lane H)',
            'sources': [
                'game/assets/movesets/*.json (Lane F, read-only)',
                'customization/create-fighter/data/MOVE-DATABASE.json (wrestling)',
            ],
            'preview_clip_rule': 'T3 clip mapped by Tekken input (see DESIGN-v0.3 §3); a real anim_ref always wins',
            'federation_rule': 'wrestling moves carry federation:true and a Tekken input; no wrestling control schemes',
        },
        'total_moves': len(moves),
        'tekken_moves': sum(1 for m in moves if not m['federation']),
        'federation_moves': sum(1 for m in moves if m['federation']),
        'moves': moves,
    }
    with open(OUT, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f'wrote {OUT}: {len(moves)} moves '
          f'({out["tekken_moves"]} tekken + {out["federation_moves"]} federation)')

if __name__ == '__main__':
    main()
