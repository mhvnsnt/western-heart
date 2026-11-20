#!/usr/bin/env python3
"""Project dw-motion-bank.json into the Western Heart moveset-library v1
bank format (game/data/moveset-library/banks/dw.json).

Only MOTION clips become library moves (frames > 1, wireable kit assigned).
1-frame init_obj bodies / wave-echo archetypes are NOT moves — they belong
in the HM_TEARDOWN wave/boss data (see dw_teardown.py), not this bank.
The face STUB and unassigned-kit clips are excluded (never wired).

Derivation (from the measured gloss + first-frame data; nothing invented):
  type / subtype / position: keyword rules over the index gloss, plus the
    measured first-frame max-Y (airborne when Y > 2000 mm).
  frames.total: measured clip frames. startup / active / recovery: null —
    the keyframe timing split is NOT yet decoded (see DW-DECODE-LOG.md
    §keyframe). Listed in provenance.estimated.
  damage: null — damage numbers live in TK5DATA0/1 (not decoded).
    Listed in provenance.estimated.
  input: null — no input notation is stored in the gym files.
    Listed in provenance.estimated.
  name: canon kit + gloss (rename map). name_status flags PROVISIONAL
    glosses and Jay-call-blocked names.

Canon laws (Jay 2026-11-07 ~22:19, revised ~22:32; corrected ~22:43):
  "Devil" only in our own way/language, never the source game's way.
  "Jin" only ever means the soul JIN (the Blade Soul). Source kit names
  are provenance only, never canon names. Jay-call-blocked names are
  PROVISIONAL, never decided here.

Usage: python3 dw_bank_to_moveset.py <dw-motion-bank.json> <out.json>
"""
import json, re, sys
from pathlib import Path

def slug_of(source_file, group):
    # strip 'gym_<group>_' prefix and '.dat' suffix
    name = source_file
    if name.startswith('gym_'):
        name = name[4:]
    prefix = group + '_'
    if name.startswith(prefix):
        name = name[len(prefix):]
    if name.endswith('.dat'):
        name = name[:-4]
    # sanitise for an id slug
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug

def derive_type_position(gloss, max_y_mm):
    g = gloss.lower()
    # position first (airborne overrides)
    if max_y_mm is not None and max_y_mm > 2000:
        position = 'airborne'
    elif any(k in g for k in ('jump', 'fly', 'warp', 'meteorite', 'hijump')):
        position = 'airborne' if any(k in g for k in ('fly', 'warp', 'meteorite')) else 'jumping'
    elif any(k in g for k in ('knocked down', 'wdown', 'dead', 'breakfall', 'ukemi')):
        position = 'grounded'
    elif 'crouch' in g:
        position = 'crouching'
    elif 'run' in g:
        position = 'running'
    else:
        position = 'standing'
    # type / subtype
    if 'throw' in g or 'nage' in g:
        return 'throw', None, position
    if 'stance' in g or 'kamae' in g:
        return 'stance', None, position
    if any(k in g for k in ('jump', 'fly', 'warp', 'meteorite')):
        if 'beam' in g or 'fire' in g or 'shot' in g:
            return 'special', None, position
        return 'aerial', None, position
    if 'beam' in g or 'laser' in g or 'fire' in g or 'shot' in g or 'machinegun' in g \
       or 'hadou' in g or 'wave' in g or 'charge' in g or 'burn' in g or 'breath' in g:
        return 'special', None, position
    if 'kick' in g:
        return 'strike', 'kick', position
    if 'punch' in g:
        return 'strike', 'punch', position
    if any(k in g for k in ('dash', 'step', 'walk', 'turn', 'movement', 'fstep',
                            'idou', 's way', 'sway', 'landing', 'chaku', 'escape',
                            'nige', 'breakfall', 'ukemi', 'dead')):
        return 'transition', None, position
    if any(k in g for k in ('entrance', 'tojo', 'toujyou', 'appearance')):
        return 'taunt', None, position
    if 'guard' in g:
        return 'hold', None, position
    if 'hand' in g:
        return 'strike', 'punch', position
    return 'strike', None, position

def main():
    bank_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    bank = json.loads(bank_path.read_text())
    moves = []
    skipped = []
    for c in bank['clips']:
        if 'bones' not in c:
            skipped.append((c['source_file'], 'MISSING — no file data in TK5DATA2 (name only in load lists)'))
            continue
        if not c.get('wireable'):
            skipped.append((c['source_file'], 'not wireable'))
            continue
        if c.get('frames', 0) <= 1:
            skipped.append((c['source_file'], '1-frame pose (body/init, not a move)'))
            continue
        if c['group'] == 'init_obj':
            skipped.append((c['source_file'], '1-frame body/init (HM_TEARDOWN, not a move)'))
            continue
        slug = slug_of(c['source_file'], c['group'])
        kit = c['canon_kit_id']
        mid = f"dw:{kit}:{slug}"
        max_y = None
        ys = [ff['floats'][1] for ff in c.get('first_frame', [])
              if ff.get('channel') == 'position_mm']
        if ys:
            max_y = max(ys)
        mtype, subtype, position = derive_type_position(c.get('gloss', ''), max_y)
        name = f"{c['canon_kit']} — {c.get('gloss', '')}" if c.get('gloss') else c['canon_kit']
        # name_status: PROVISIONAL gloss unless the gloss confidence is high
        conf = c.get('gloss_confidence', '')
        if 'PROVISIONAL' in c['canon_kit']:
            name_status = 'PROVISIONAL — Jay-call-blocked name; canon kit name provisional'
        elif conf == 'high':
            name_status = 'DW decoded — canon kit name; gloss high-confidence'
        else:
            name_status = 'DW decoded — canon kit name; gloss PROVISIONAL'
        estimated = ['frames.startup', 'frames.active', 'frames.recovery',
                     'damage', 'input']
        moves.append({
            'id': mid,
            'name': name,
            'name_status': name_status,
            'source': 'tekken5_devil_within',
            'source_character': c['canon_kit'],
            'source_game_label': 'Tekken 5 (source data; canon names per HeartMind rename map)',
            'anim_ref': mid,
            'type': mtype,
            'subtype': subtype,
            'position': position,
            'orientation': 'forward',
            'input': None,
            'input_slots': [],
            'frames': {'startup': None, 'active': None, 'recovery': None,
                       'total': c['frames']},
            'damage': None,
            'damage_raw': None,
            'properties': [c.get('subtype', 'standard')],
            'hit_level': None,
            'limb': None,
            'active': None,
            'wh': {'heavy': False, 'knock': None, 'soulGain': None},
            'provenance': {
                'note': (f"Decoded from Tekken 5 disc, TK5DATA2.BIN (romD). "
                         f"Source file {c['source_file']}; {c['frames']} frames @60fps "
                         f"({c.get('duration_s')}s), {c['bones']} bones, subtype "
                         f"{c.get('subtype')}. First-frame channels decoded "
                         f"(position/scale/rotation-packed); per-frame keyframe "
                         f"packing not yet reversed (DW-DECODE-LOG.md §keyframe)."),
                'estimated': estimated,
            },
        })
    out = {
        'bank': 'dw',
        'game': 'tekken5_devil_within',
        'schema': 'moveset-library/v1',
        'built': '2026-11-08',
        'builder': 'devil-within-decode: dw_bank_to_moveset.py (from dw-motion-bank.json)',
        'honesty': ('estimated fields are flagged per-entry in provenance.estimated; '
                    'nothing is invented as canon. Frames/damage/input are null '
                    'until the keyframe packing + TK5DATA0/1 numbers decode.'),
        'canon_law': ('"Devil" only in our own way/language, never the source game\'s way. '
                      '"Jin" only ever means the soul JIN (the Blade Soul).'),
        'count': len(moves),
        'moves': moves,
    }
    out_path.write_text(json.dumps(out, indent=1))
    print(f"moves={len(moves)} skipped={len(skipped)} -> {out_path}")
    for s in skipped:
        print(f"  skip {s[0]}: {s[1]}")

if __name__ == '__main__':
    main()
