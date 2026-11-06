#!/usr/bin/env python3
"""wire_catalog.py — wire tattoos + scars into the suite parts catalog as BODY-REGION DECAL layers.

Idempotent. Edits customization/creation-suite-ui/data/parts-catalog.json in place (same format:
json.dumps(indent=1) + newline), touching only:
  - the 99 No Mercy tattoo entries (source teardown/wwf-no-mercy/textures/rom/tattoo): placement
    null -> a body-region decal placement (default region chest; the player picks any of the 12
    regions in the TATTOOS layer editor), decal_kind 'tattoo'. suite_slot stays decal_logo
    (test/parts-tattoos.test.mjs).
  - + the procedural CC0 scar set (customization/decal-library/scars/scars.json, make_scars.py)
    as suite_slot 'scar' texture parts.
  - + 1 REFERENCE-ONLY row for the single scar-named Tekken 7 face-paint item (item 90016,
    teardown/tekken7/facepaint-reference.json): no texture file is in the repo, so it is
    geometry_pending (hidden unless COMING SOON is on) and never claims an asset. Generic name
    (names law).
  - header counts / total / notes.
"""
import json, os

CAT = 'customization/creation-suite-ui/data/parts-catalog.json'
SCARS = 'customization/decal-library/scars/scars.json'
TATTOO_SRC = 'teardown/wwf-no-mercy/textures/rom/tattoo'
SCAR_SRC = 'customization/decal-library/scars'
REF_SRC = 'teardown/tekken7/facepaint-reference.json'
EDITABLE = ['region', 'position', 'size', 'rotation', 'opacity', 'color', 'mirror', 'layer_order']
NOTE = (' Tattoos + scars as body-region decal LAYERS wired 2026-11-02 (creation suite TATTOOS + SCARS phase): '
        'the 99 tattoos carry a body_region_decal placement (default region chest, 12 regions selectable, '
        'per-template defaults in customization/templates/decal-placements.json), +11 Western Heart CC0 scars '
        '(suite_slot scar, customization/decal-library/scars/), +1 reference-only scar row for the one scar-named '
        'Tekken 7 face-paint item (texture not in repo, geometry_pending).')


def main():
    c = json.load(open(CAT))
    parts = c['parts']
    n_tat = 0
    for p in parts:
        if p.get('source') == TATTOO_SRC:
            p['placement'] = {'kind': 'body_region_decal', 'region': 'chest'}
            p['decal_kind'] = 'tattoo'
            p['editable'] = EDITABLE
            n_tat += 1
    parts[:] = [p for p in parts if p.get('source') not in (SCAR_SRC, REF_SRC)]
    m = json.load(open(SCARS))
    for s in m['scars']:
        parts.append({
            'id': 'wh-scar-' + s['id'], 'name': s['name'], 'part_class': 'texture_part', 'suite_slot': 'scar',
            't7_slot': '8', 'library': 'western-heart', 'source': SCAR_SRC, 'glb': None,
            'asset': f"{SCAR_SRC}/{s['file']}", 'socket': None, 'offset': [0, 0, 0], 'rotation': [0, 0, 0],
            'scale': 1, 'modeled_in_place_for': None, 'geometry_pending': False, 'kind': 'scar', 'decal_kind': 'scar',
            'placement': {'kind': 'body_region_decal', 'region': s['region'], 'u': s['u'], 'v': s['v']},
            'editable': EDITABLE, 'license': 'CC0-1.0',
        })
    parts.append({
        'id': 'wh-scar-ref-t7-90016', 'name': 'Brow Scar (reference)', 'part_class': 'texture_part',
        'suite_slot': 'scar', 't7_slot': '8', 'library': 'western-heart', 'source': REF_SRC, 'glb': None,
        'asset': None, 'socket': None, 'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1,
        'modeled_in_place_for': None, 'geometry_pending': True, 'reference_only': True, 'kind': 'scar',
        'decal_kind': 'scar', 'placement': {'kind': 'body_region_decal', 'region': 'face', 'u': 0.08, 'v': 0.35},
        'editable': EDITABLE,
        'reference': {'item_no': 90016, 'slot_code': 8, 'note': 'only scar-named Tekken 7 face-paint item; '
                      'CharacterItemTex file not in western-heart -> reference only, no texture claimed'},
    })
    c['counts'][SCAR_SRC] = len(m['scars'])
    c['counts'][REF_SRC] = 1
    c['total'] = len(parts)
    if NOTE.strip() not in c['notes']:
        c['notes'] = c['notes'] + NOTE
    with open(CAT, 'w') as f:
        f.write(json.dumps(c, indent=1) + '\n')
    print(f'tattoos placed: {n_tat}; scars: {len(m["scars"])} + 1 reference; total {c["total"]}')


if __name__ == '__main__':
    main()
