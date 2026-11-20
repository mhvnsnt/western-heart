#!/usr/bin/env python3
"""Build the HeartMind teardown data file (game/data/heartmind-dw-teardown.json)
from the decoded Devil Within data.

This is the data for the HM_TEARDOWN seam in game/js/heartmind.js:
  HM_TEARDOWN = { ready, enemyAi, waveTables, doorSystems }.
The three core fields are NOT yet filled — they live in TK5DATA0/1
(not decoded) or need the stage assignment resolved. They are null here
with the reason recorded, NOT guessed. The measured DW data that IS
available (wave-echo archetypes, boss kits, stage inventories, sound
donors, the moveset bank) is carried in `dw_data` so the wave/boss
builders can consume it now.

Wave composition (per stage): the romD load lists record WHICH enemy
archetypes load together, but the per-stage assignment of load lists is
UNMEASURED, and spawn counts / spawn order are NOT in the load lists.
So waveTables stays null. The archetype sets are recorded in dw_data.

Canon laws (Jay 2026-11-07 ~22:19, revised ~22:32; corrected ~22:43):
  "Devil" only in our own way/language, never the source game's way.
  "Jin" only ever means the soul JIN (the Blade Soul).

Usage: python3 dw_teardown.py <dw-motion-bank.json> <moj-stage-inventory.json>
         <romd_blocks.json> <out.json>
"""
import json, sys
from pathlib import Path
from collections import Counter

def main():
    bank_p, moj_p, blocks_p, out_p = (Path(a) for a in sys.argv[1:5])
    bank = json.loads(bank_p.read_text())
    moj = json.loads(moj_p.read_text())
    blocks = json.loads(blocks_p.read_text())

    clips = {c['source_file']: c for c in bank['clips'] if 'bones' in c}

    # wave-echo archetypes (mon_ + tk_ families, 12 archetypes, all 1-frame, 78 bones)
    archetypes = []
    for name, c in sorted(clips.items()):
        if c['group'] == 'init_obj' and c['canon_kit_id'] == 'wave_echo':
            archetypes.append({
                'source_file': name, 'canon': c['canon_kit'],
                'bones': c['bones'], 'frames': c['frames'],
            })

    # boss kits: move counts + total frames/duration per kit
    boss_kits = {}
    for c in bank['clips']:
        if 'bones' not in c or not c.get('wireable'):
            continue
        kit = c['canon_kit_id']
        if kit in ('warden', 'drowned_ogre', 'unmasked', 'surge', 'surge_bloom'):
            boss_kits.setdefault(kit, {'canon_kit': c['canon_kit'], 'clips': 0,
                                       'frames': 0, 'duration_s': 0.0})
            boss_kits[kit]['clips'] += 1
            boss_kits[kit]['frames'] += c.get('frames', 0)
            boss_kits[kit]['duration_s'] = round(boss_kits[kit]['duration_s'] + c.get('duration_s', 0), 3)

    # boss bodies (init_obj boss1/2/3/5)
    boss_bodies = []
    for name, c in sorted(clips.items()):
        if c['group'] == 'init_obj' and c['canon_kit_id'].endswith('_body'):
            boss_bodies.append({'source_file': name, 'canon': c['canon_kit'],
                                'bones': c['bones']})

    # stages (from the moj inventory)
    stages = []
    for s in moj['stages']:
        stages.append({'source_file': s['source_file'], 'canon_stage': s['canon_stage'],
                       'size_bytes': s.get('size_bytes'),
                       'nudp_count': s.get('nudp_count'), 'tim2_count': s.get('tim2_count'),
                       'mif_count': s.get('mif_count'),
                       'nudp_tiling_ok': s.get('nudp_tiling_ok')})

    # load-list archetype sets (evidence for future waveTables)
    # count how many load lists reference each archetype family
    fam = Counter()
    for b in blocks:
        names = set(b.get('names', []))
        for n in names:
            if n.startswith('gym_init_obj_mon_'):
                fam['mon'] += 1
            elif n.startswith('gym_init_obj_tk_'):
                fam['tk'] += 1
            elif n.startswith('gym_init_obj_boss'):
                fam['boss'] += 1

    out = {
        'format': 'western-heart heartmind-dw-teardown v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'canon_law': ('"Devil" only in our own way/language, never the source game\'s way. '
                      '"Jin" only ever means the soul JIN (the Blade Soul).'),
        # --- the HM_TEARDOWN seam fields (heartmind.js) ---
        'ready': False,
        'enemyAi': None,
        'waveTables': None,
        'doorSystems': None,
        'not_ready_reason': (
            'enemyAi (per-enemy AI patterns) and doorSystems (platforming/door '
            'progression) live in TK5DATA0/1 (not decoded — disk quota blocks the '
            'full fetch; stream-scan found no readable DW strings in TK5DATA1). '
            'waveTables (per-stage wave composition) needs the load-list-to-stage '
            'assignment resolved; spawn counts/order are not in the load lists. '
            'Nothing is guessed. See DW-DECODE-LOG.md.'),
        # --- measured DW data, available now ---
        'dw_data': {
            'moveset_bank': 'game/data/moveset-library/banks/dw.json (165 moves, v1 schema)',
            'motion_bank': 'teardown/tekken5/dw-motion-bank.json (220 clips, 214 extracted)',
            'wave_echo_archetypes': archetypes,
            'wave_echo_archetype_count': len(archetypes),
            'boss_kits': boss_kits,
            'boss_bodies': boss_bodies,
            'stages': stages,
            'stage_note': ('THE FURNACE (stage 4) has no DW donor: no boss4 init, '
                           'no moj_stg03. The SOUL SPHERE is an orb that spawns '
                           'monsters; the missing body is the design.'),
            'load_list_evidence': {
                'blocks_with_mon_archetypes': fam['mon'],
                'blocks_with_tk_archetypes': fam['tk'],
                'blocks_with_boss': fam['boss'],
                'note': ('Counts of romD name-list blocks referencing each family. '
                         'The lists record which files load together, not spawn '
                         'counts or order.'),
            },
            'missing_files': bank['missing_files'],
            'decode_status': bank['decode_status'],
        },
    }
    out_p.write_text(json.dumps(out, indent=1))
    print(f"archetypes={len(archetypes)} boss_kits={list(boss_kits)} "
          f"boss_bodies={len(boss_bodies)} stages={len(stages)} -> {out_p}")

if __name__ == '__main__':
    main()
