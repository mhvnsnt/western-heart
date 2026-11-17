#!/usr/bin/env python3
"""Generated CC0 clothing + accessories -> MANIFEST.json + creation-suite parts-catalog entries.

Filed on the WWE 2K CAW Attire hierarchy (WWE_ATTIRE_TREE regions: Upper Body / Lower Body / Arms & Hands /
Legs & Feet / Headgear) with a CAW tab (Upper / Lower / Hands / Feet / Accessories) and on the Tekken 7 slot spine
(ATTIRE_TREE: 9 Upper Body, 10 Full Body, 11 Lower Body, H Hands, F Feet, 4 Hair Accessory, 12 Upper Accessory,
13 Lower Accessory). Player-facing names are generic (names law).

  python3 tools/mpfb2/clothing/catalog_entries.py --manifest   # (re)write customization/parts/clothing/generated/MANIFEST.json
  python3 tools/mpfb2/clothing/catalog_entries.py --apply      # upsert into customization/creation-suite-ui/data/parts-catalog.json
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN = 'customization/parts/clothing/generated'
CATALOG = ROOT / 'customization' / 'creation-suite-ui' / 'data' / 'parts-catalog.json'
COUNT_KEY = 'customization/parts/clothing/generated (CC0 clothing + accessories generated on the 9 bodies, 2026-11-03)'
TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
             'powerhouse-w', 'athletic-w', 'striker-w']
TAB = {'Upper Body': 'Upper', 'Lower Body': 'Lower', 'Arms & Hands': 'Hands', 'Legs & Feet': 'Feet', 'Headgear': 'Accessories'}
SUITE_SLOT = {'9': 'upper_body', '10': 'fullbody', '11': 'lower_body', 'H': 'gloves', 'F': 'shoes'}


def items():
    return json.loads((HERE / 'items.json').read_text())


def manifest():
    out = []
    for it in items():
        d = ROOT / GEN / it['id']
        tpls = [t for t in TEMPLATES if (d / f'{t}.glb').exists()]
        out.append({'id': it['id'], 'name': it['name'], 'family': 'accessories' if it.get('acc') else 'clothing',
                    'wwe_region': it['wwe'][0], 'wwe_type': it['wwe'][1], 't7_slot': it['t7'], 'equip_slot': it['equip'],
                    'layer_offset_m': it['offset'], 'default_color': it['color'], 'roughness': it.get('rough'),
                    'license': 'CC0-1.0', 'author': 'Western Heart (original geometry generated in Blender on each template body)',
                    'templates': tpls, 'files': {t: f"{it['id']}/{t}.glb" for t in tpls}})
    return {'library': 'wh-generated-clothing', 'created': '2026-11-03',
            'source': 'original CC0 garments generated on each template body in Blender 4.3.2 (tools/mpfb2/clothing/shell_fit.py)',
            'space': 'model-bind, skinned to the template skeleton (JOINTS_0 = template skin joints, extras.wh_joint_index)',
            'morphs': 'targets named like the template body sliders (b_*/f_*); apply the same slider values as the body',
            'hide': 'mesh.extras.wh_hide {skin|generic|nails: run-length [start,count,...]} = template body vertices under the garment; game/js/fitted-parts.js drops body triangles whose 3 vertices are hidden',
            'tool': 'tools/mpfb2/clothing/ (shell_fit.py -> build_glb.mjs, gltfpack -cc -kn -km -ke)', 'entries': out}


def fitted_entries():
    out = []
    for e in manifest()['entries']:
        d = f"{GEN}/{e['id']}"; glb = f"{d}/technician.glb"
        acc = e['family'] == 'accessories'
        socket = {'4': 'head', 'H': 'hand', 'F': 'foot'}.get(e['t7_slot'], 'body')
        out.append({
            'id': e['id'], 'name': e['name'], 'part_class': 'mesh_part',
            'suite_slot': 'accessory' if acc else SUITE_SLOT[e['t7_slot']], 't7_slot': e['t7_slot'], 'equip_slot': e['equip_slot'],
            'wwe_category': e['wwe_type'], 'wwe_region': e['wwe_region'], 'wwe_caw_tab': 'Accessories' if acc else TAB[e['wwe_region']],
            'library': 'wh-generated-clothing', 'source': f'{GEN}/MANIFEST.json', 'glb': glb, 'asset': glb, 'socket': socket,
            'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1, 'modeled_in_place_for': None, 'geometry_pending': False,
            'kind': 'clothing', 'placement': {'socket': socket, 'mode': 'fitted', 'offset': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': 1},
            'fitted': {'dir': d, 'templates': e['templates'], 'space': 'model-bind', 'skinned': True, 'hides_body': True,
                       'color': e['default_color'], 'roughness': e['roughness']},
            'editable': ['tint', 'visible'], 'license': 'CC0-1.0',
        })
    return out


def apply():
    cat = json.loads(CATALOG.read_text())
    new = fitted_entries(); ids = {e['id'] for e in new}
    parts = [p for p in cat['parts'] if p.get('id') not in ids] + new
    cat['parts'] = parts; cat['total'] = len(parts)
    cat.setdefault('counts', {})[COUNT_KEY] = len(new)
    CATALOG.write_text(json.dumps(cat, indent=1) + '\n')
    print(f'{len(new)} generated clothing entries upserted; catalog total {len(parts)}')


if __name__ == '__main__':
    if '--manifest' in sys.argv:
        (ROOT / GEN / 'MANIFEST.json').write_text(json.dumps(manifest(), indent=1) + '\n'); print('manifest written')
    if '--apply' in sys.argv:
        apply()
    if len(sys.argv) == 1:
        print(json.dumps(fitted_entries(), indent=1))
