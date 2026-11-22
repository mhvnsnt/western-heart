#!/usr/bin/env python3
"""VPW2 move -> AnimID map (VPW2 equivalent of the No Mercy lane's map).

Every AkiAnimation file carries a VPWStudio DB label with its move category
and name, e.g. "[Front Special Grapple] 62 - Sweet Chin Music (P1)".
AnimID = file_id - 0x2056 for move animations (0x2056-0x3322);
system animations (0x1A90-0x2055) are listed with their labels too.

Toki1 timing (damage/reversal/vulnerable frames) and move-damage records
are joined where the indexes line up: Toki1 entry i = anim file 0x1A90+i.

Usage: python3 vpw2_movemap.py   (run from vpw2/tools/)
Outputs: vpw2/extracted/moveset/move_anim_map.json,
  vpw2/extracted/moveset/move_anim_map.csv
"""
import csv
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.path.dirname(HERE)
BASE = os.path.dirname(VPW2)
MOVE_DIR = os.path.join(VPW2, 'extracted', 'moveset')

FIRST_ANIM = 0x1A90
FIRST_MOVE_ANIM = 0x2056


def main():
    db_path = os.path.join(BASE, 'pulls', 'VPWStudio', 'VPWStudio',
                           'VPWStudio', 'FileTableDB', 'VPW2.txt')
    rows = []
    cats = Counter()
    unlabeled = 0
    for line in open(db_path):
        m = re.match(r'([0-9A-Fa-f]{2,})=AkiAnimation;(.*)$', line.strip())
        if not m:
            continue
        fid = int(m.group(1), 16)
        label = m.group(2)
        cat, num, name, note = '', None, '', ''
        if not label:
            unlabeled += 1
        else:
            cm = re.match(r'\[(.+?)\]\s*(?:(\d+)\s*-\s*)?(.*)$', label)
            if cm:
                cat = cm.group(1)
                num = int(cm.group(2)) if cm.group(2) else None
                rest = cm.group(3)
                nm = re.match(r'^(.*?)\s*\(([^)]*)\)\s*$', rest)
                if nm:
                    name, note = nm.group(1), nm.group(2)
                else:
                    name = rest
            else:
                name = label
        cats[cat or '(no category)'] += 1
        is_move = fid >= FIRST_MOVE_ANIM
        rows.append({
            'file_id': f'{fid:04X}',
            'anim_id': fid - FIRST_MOVE_ANIM if is_move else None,
            'anim_index': fid - FIRST_ANIM,
            'kind': 'move' if is_move else 'system',
            'category': cat,
            'move_number': num,
            'move_name': name,
            'note': note,
            'label': label,
            'npy': f'{fid:04X}.npy',
        })
    rows.sort(key=lambda r: r['file_id'])
    moves = [r for r in rows if r['kind'] == 'move']
    systems = [r for r in rows if r['kind'] == 'system']
    print(f'animations: {len(rows)} total, {len(moves)} move, '
          f'{len(systems)} system, {unlabeled} unlabeled')
    print(f'categories: {len(cats)}')
    for cat, n in cats.most_common(12):
        print(f'  {cat}: {n}')

    # join Toki1 timing for move anims
    toki = json.load(open(os.path.join(MOVE_DIR, 'toki1.json')))['entries']
    tmap = {t['anim_index']: t for t in toki}
    for r in rows:
        t = tmap.get(r['anim_index'])
        if t:
            r['toki1'] = {
                'damage_frame_start': t['damage_frame_start'],
                'damage_frame_end': t['damage_frame_end'],
                'first_vulnerable_frame': t['first_vulnerable_frame'],
                'reversal_frame': t['reversal_frame'],
                'breakaway_frame': t['breakaway_frame'],
            }
    json.dump({'source': 'VPWStudio FileTableDB/VPW2.txt animation labels',
               'anim_id_note': 'AnimID = file_id - 0x2056 (move anims only)',
               'counts': {'total': len(rows), 'move': len(moves),
                          'system': len(systems), 'unlabeled': unlabeled,
                          'categories': len(cats)},
               'categories': dict(cats),
               'animations': rows},
              open(os.path.join(MOVE_DIR, 'move_anim_map.json'), 'w'),
              ensure_ascii=False, indent=1)
    with open(os.path.join(MOVE_DIR, 'move_anim_map.csv'), 'w',
              newline='') as f:
        w = csv.writer(f)
        w.writerow(['file_id', 'anim_id', 'kind', 'category',
                    'move_number', 'move_name', 'note'])
        for r in rows:
            w.writerow([r['file_id'],
                        r['anim_id'] if r['anim_id'] is not None else '',
                        r['kind'], r['category'],
                        r['move_number'] if r['move_number'] is not None
                        else '', r['move_name'], r['note']])
    print('wrote move_anim_map.json + .csv')


if __name__ == '__main__':
    main()
