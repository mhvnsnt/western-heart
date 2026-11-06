#!/usr/bin/env python3
"""Fitted hair / facial hair / eyebrows / eyelashes -> creation-suite parts-catalog entries.

Reads customization/parts/hair/mpfb2/MANIFEST.json and builds non-pending catalog entries, structured on the
WWE 2K Create-A-Superstar Face tab (Hairstyle / Facial Hair / Eyebrows / Eyes>Eyelashes, see
customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md) and filed on the Tekken 7 slot spine (HAIR '2', FACE_HAIR '7',
FACE '6'; teardown/tekken7-steam-ui/T7-UI-LAYOUT.md).

  python3 tools/mpfb2/hair/catalog_entries.py --apply   # upsert into customization/creation-suite-ui/data/parts-catalog.json
customization/build_suite_catalog.py calls fitted_entries() too, so a full catalog rebuild keeps them.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'customization' / 'parts' / 'hair' / 'mpfb2' / 'MANIFEST.json'
CATALOG = ROOT / 'customization' / 'creation-suite-ui' / 'data' / 'parts-catalog.json'
COUNT_KEY = 'customization/parts/hair/mpfb2 (fitted CC0 hair, 2026-11-02)'
SLOT = {  # fitted slot -> (suite_slot, t7_slot, equip_slot, WWE 2K CAW category, kind)
    'hair': ('hair', '2', '2', 'Hairstyle', 'hair'),
    'facial_hair': ('facial_hair', '7', '7', 'Facial Hair', 'facial_hair'),
    'eyebrows': ('eyebrows', '6', '6', 'Eyebrows', 'eyebrows'),
    'eyelashes': ('eyelashes', '6', '6L', 'Eyelashes', 'eyelashes'),
}


def fitted_entries(root=ROOT):
    man = json.loads((Path(root) / 'customization' / 'parts' / 'hair' / 'mpfb2' / 'MANIFEST.json').read_text())
    out = []
    for e in man['entries']:
        suite_slot, t7, equip, wwe, kind = SLOT[e['slot']]
        d = f"customization/parts/hair/mpfb2/{e['id']}"
        glb = f"{d}/technician.glb"  # default-template fit; the suite / game pick the fit for the active template
        out.append({
            'id': e['id'], 'name': e['name'], 'part_class': 'mesh_part', 'suite_slot': suite_slot, 't7_slot': t7,
            'equip_slot': equip, 'wwe_category': wwe, 'library': 'wh-fitted-hair',
            'source': 'customization/parts/hair/mpfb2/MANIFEST.json', 'glb': glb, 'asset': glb, 'socket': 'head',
            'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1, 'modeled_in_place_for': None,
            'geometry_pending': False, 'kind': kind,
            'placement': {'socket': 'head', 'mode': 'fitted', 'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1},
            'fitted': {'dir': d, 'templates': e['templates'], 'space': 'head-bone-local', 'texture': f"{d}/texture.png"},
            'editable': ['tint', 'visible'], 'license': 'CC0-1.0',
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
    print(f'{len(new)} fitted entries upserted; catalog total {len(parts)}')


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply()
    else:
        print(json.dumps(fitted_entries(), indent=1))
