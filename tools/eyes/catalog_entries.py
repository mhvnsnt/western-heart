#!/usr/bin/env python3
"""Fitted eyes -> creation-suite parts-catalog entries (EYES phase, 2026-11-02).

One entry per eye TYPE in game/js/fitted-eyes.js EYE_TYPES (kept in step by test/fitted-eyes.test.mjs). Structure
follows the WWE 2K Create-A-Superstar Face > Eyes window ("Eyes (color, shape)",
customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md), filed on the Tekken 7 EYES slot
(teardown/tekken7-steam-ui/T7-UI-LAYOUT.md). Geometry = customization/parts/eyes/eyeball.glb placed left + right at
customization/parts/eyes/eye-sockets.json (tools/eyes/build_eye_sockets.mjs). Lens types use the eye-library iris
textures already in the repo. Player-facing names are generic (names law).

  python3 tools/eyes/catalog_entries.py --apply   # upsert into customization/creation-suite-ui/data/parts-catalog.json
customization/build_suite_catalog.py calls fitted_entries() too, so a full rebuild keeps them.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'customization' / 'creation-suite-ui' / 'data' / 'parts-catalog.json'
COUNT_KEY = 'customization/parts/eyes (fitted eyes, 2026-11-02)'
GLB = 'customization/parts/eyes/eyeball.glb'
SOCKETS = 'customization/parts/eyes/eye-sockets.json'
# id -> (player name, lens texture or None) — mirrors game/js/fitted-eyes.js EYE_TYPES
TYPES = [
    ('wh-eye-natural', 'Natural Eyes', None),
    ('wh-eye-lens-gold', 'Gold Iris', 'customization/eye-library/eye-classic-original.png'),
    ('wh-eye-lens-ice', 'Ice Blue Iris', 'customization/eye-library/eye-blue-snow-leopard.png'),
    ('wh-eye-lens-amber', 'Amber Striated Iris', 'customization/eye-library/eye-yellow-tiger.png'),
]


def fitted_entries(root=ROOT):
    out = []
    for pid, name, lens in TYPES:
        out.append({
            'id': pid, 'name': name, 'part_class': 'mesh_part', 'suite_slot': 'eye', 't7_slot': 'EYES',
            'equip_slot': 'EYES', 'wwe_category': 'Eyes', 'library': 'wh-fitted-eyes',
            'source': 'tools/eyes/catalog_entries.py', 'glb': GLB, 'asset': lens or GLB, 'socket': 'head',
            'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1, 'modeled_in_place_for': None,
            'geometry_pending': False, 'kind': 'eyes', 'eye_kind': 'fitted_eye',
            'placement': {'socket': 'head', 'mode': 'fitted-eyes', 'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1},
            'fitted_eyes': {'sockets': SOCKETS, 'space': 'head-bone-local', 'sides': ['left', 'right'], 'lens': lens},
            'editable': ['iris', 'sclera', 'pupil'], 'license': 'own (procedural eyeball, wh make_eye_parts.py)',
        })
    return out


def apply():
    cat = json.loads(CATALOG.read_text())
    new = fitted_entries()
    ids = {e['id'] for e in new}
    parts = [p for p in cat['parts'] if p.get('id') not in ids]
    parts.extend(new)
    cat['parts'] = parts
    cat['total'] = len(parts)
    cat.setdefault('counts', {})[COUNT_KEY] = len(new)
    CATALOG.write_text(json.dumps(cat, indent=1) + '\n')
    print(f'{len(new)} fitted eye entries upserted; catalog total {len(parts)}')


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
    else:
        print(json.dumps(fitted_entries(), indent=1))
