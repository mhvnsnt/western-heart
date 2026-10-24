#!/usr/bin/env python3
"""Write customization/parts/{defjam,wmxix}/CATALOG.json from the converted data.

game/js/customization-consumer.js has always listed these two paths, but they
were never generated, so the live site 404'd on them and the fight-side merge
silently skipped Def Jam and WMXIX. This derives both from files already in
the repo (no new content):
  defjam <- customization/parts-converted/defjam/CATALOG.json (2,624 converted parts)
  wmxix  <- customization/parts-converted/CATALOG.json entries with source_game=wmxix
Entries keep their honest status (Def Jam GLBs are POINTS-only previews).
"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return json.load(open(os.path.join(R, p)))
def write(p, meta, parts):
    os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
    with open(os.path.join(R, p), 'w') as f:
        json.dump({'_meta': dict(meta, count=len(parts), generator='customization/build_source_catalogs.py',
                                 consumer='packages/creation-suite/src/catalogs.js'), 'parts': parts}, f, indent=1)
dj = []
for e in load('customization/parts-converted/defjam/CATALOG.json')['parts']:
    e = dict(e); e['file'] = e.get('glb') or e.get('file'); e.setdefault('part_class', 'mesh_part')
    e['conversion'] = {'status': e.get('status', 'converted'), 'topology': e.get('topology_status')}
    dj.append(e)
write('customization/parts/defjam/CATALOG.json', {'catalog': 'Def Jam parts (converted, POINTS previews)'}, dj)
wm = [e for e in load('customization/parts-converted/CATALOG.json')['parts'] if e.get('source_game') == 'wmxix']
write('customization/parts/wmxix/CATALOG.json', {'catalog': 'WWE WrestleMania XIX edit_data parts'}, wm)
print(len(dj), len(wm))
