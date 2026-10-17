#!/usr/bin/env python3
"""Build master PARTS-INDEX.json from all extracted CAW parts.

Combines:
  - wmxix/PARTS-INDEX.jsonl (2,690 files from ISO extraction)
  - no-mercy/ parts (from manifest.json + faces + skins)

Writes customization/parts/PARTS-INDEX.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(HERE, 'parts')

def main():
    entries = []

    # WMXIX from JSONL
    jsonl_path = os.path.join(PARTS, 'wmxix', 'PARTS-INDEX.jsonl')
    with open(jsonl_path) as f:
        for line in f:
            e = json.loads(line)
            entries.append(e)
    print(f'WMXIX: {len(entries)} entries')

    # No Mercy from manifest.json
    nm_base = os.path.join(PARTS, 'no-mercy')
    manifest = json.load(open(os.path.join(nm_base, 'manifest.json')))
    nm_count = 0
    for mod in manifest['models']:
        fpath = mod['file']
        # Only include CAW-relevant dirs (not arena/backstage/stage/lobby/unlabeled)
        topdir = fpath.split('/')[0]
        if topdir in ('body_parts', 'face', 'attire_parts', 'weapon'):
            slot_map = {
                'body_parts': 'bodies',
                'face': 'faces',
                'attire_parts': 'attire',
                'weapon': 'accessories',
            }
            entries.append({
                'part_id': f"no-mercy:{mod['file_id']}:{fpath}",
                'name': os.path.basename(fpath),
                'source_game': 'no-mercy',
                'slot': slot_map[topdir],
                'file_path': f'customization/parts/no-mercy/{fpath}',
                'label': mod.get('label', ''),
                'nverts': mod.get('nverts', 0),
                'nfaces': mod.get('nfaces', 0),
            })
            nm_count += 1
    print(f'No Mercy models: {nm_count} entries')

    # No Mercy faces (PNG)
    faces_dir = os.path.join(nm_base, 'faces')
    face_count = 0
    for fn in sorted(os.listdir(faces_dir)):
        if fn.endswith('.png'):
            entries.append({
                'part_id': f'no-mercy:face-tex:{fn}',
                'name': fn,
                'source_game': 'no-mercy',
                'slot': 'faces',
                'file_path': f'customization/parts/no-mercy/faces/{fn}',
            })
            face_count += 1
    print(f'No Mercy face textures: {face_count} entries')

    # No Mercy skins (PNG)
    skins_dir = os.path.join(nm_base, 'skins')
    skin_count = 0
    for fn in sorted(os.listdir(skins_dir)):
        if fn.endswith('.png'):
            entries.append({
                'part_id': f'no-mercy:skin-tex:{fn}',
                'name': fn,
                'source_game': 'no-mercy',
                'slot': 'skins',
                'file_path': f'customization/parts/no-mercy/skins/{fn}',
            })
            skin_count += 1
    print(f'No Mercy skin textures: {skin_count} entries')

    # DOA from parts/doa/manifest.json (empty until the DOA6 model pull lands;
    # see parts/doa/GAP.md). Entries are pre-shaped to the index schema.
    doa_manifest_path = os.path.join(PARTS, 'doa', 'manifest.json')
    doa_count = 0
    if os.path.exists(doa_manifest_path):
        doa_manifest = json.load(open(doa_manifest_path))
        for e in doa_manifest.get('parts', []):
            entries.append(e)
            doa_count += 1
    print(f'DOA parts: {doa_count} entries')

    # Write master index
    out_path = os.path.join(PARTS, 'PARTS-INDEX.json')
    with open(out_path, 'w') as f:
        json.dump({
            'total_parts': len(entries),
            'sources': ['wmxix', 'no-mercy', 'doa'],
            'parts': entries,
        }, f, indent=1)
    print(f'\nTotal: {len(entries)} parts -> {out_path}')

    # Summary by slot
    from collections import Counter
    slots = Counter(e['slot'] for e in entries)
    print('\nBy slot:')
    for slot, n in sorted(slots.items()):
        print(f'  {slot}: {n}')

if __name__ == '__main__':
    main()
