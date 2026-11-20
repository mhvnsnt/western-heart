import json, re, ghpush as g

BR = 'cust/creation-suite-20261018'
reg = json.loads(g.fcontent(BR, 'customization/PARTS-REGISTRY.json'))
idx = json.loads(g.fcontent(BR, 'customization/parts/PARTS-INDEX.json'))

BONES = {
 'head': ['Head','mixamorig:Head','head','J_Head','Bip01 Head'],
 'face': ['Head','mixamorig:Head','head','J_Head'],
 'eyes': ['Head'],
 'torso': ['Spine','Spine1','mixamorig:Spine','spine','J_Spine1','Hips','mixamorig:Hips'],
 'legs': ['Hips','mixamorig:Hips','hips','J_Hips','Bip01 Pelvis'],
 'hands': ['LeftHand','RightHand','mixamorig:LeftHand','mixamorig:RightHand'],
 'feet': ['LeftFoot','RightFoot','mixamorig:LeftFoot','mixamorig:RightFoot'],
}

SLOTMAP = {
 'hair':        dict(suite_slot='hair',      slotId='2',  socket='head',  menu='head',  tab='Head (hair)'),
 'accessories': dict(suite_slot='accessory', slotId='12', socket='torso', menu='attire',tab='Gear'),
 'gloves':      dict(suite_slot='gloves',    slotId='H',  socket='hands', menu='attire',tab='Hands'),
 'shoes':       dict(suite_slot='shoes',     slotId='F',  socket='feet',  menu='attire',tab='Feet'),
 'gears':       dict(suite_slot='gear',      slotId='14', socket='torso', menu='attire',tab='Gear'),
 'upper_body':  dict(suite_slot='upper_body',slotId='9',  socket='torso', menu='attire',tab='Upper'),
 'lower_body':  dict(suite_slot='lower_body',slotId='11', socket='legs',  menu='attire',tab='Lower'),
 'masks':       dict(suite_slot='mask',      slotId='3',  socket='face',  menu='attire',tab='Face (masks)'),
 'eyes':        dict(suite_slot='eye',       slotId='6',  socket='eyes',  menu='head',  tab='Eyes'),
 'decals':      dict(suite_slot='decal_logo',slotId='8',  socket='torso', menu='paint', tab='Paint & Tattoos'),
 'attire':      dict(suite_slot='attire',    slotId='10', socket='torso', menu='attire',tab='Full Body'),
}

def friendly(part_id):
    m = re.match(r'edit_data/MODEL/(?:Man|Woman)/([^/]+)/([a-z0-9]+)_(\d+)', part_id, re.I)
    if m:
        name = m.group(1).replace('_',' ').title()
        return f'{name} Set {m.group(3)}'
    m = re.match(r'^no-mercy:0x([0-9a-f]+):([^:]+)/', part_id, re.I)
    if m: return f'{m.group(2).replace("_"," ").title()} 0x{m.group(1).upper()}'
    m = re.match(r'^no-mercy:skin-tex:(.+)\.png', part_id, re.I)
    if m: return f'Skin Texture {m.group(1)}'
    return part_id.split('/')[-1]

CONV = {
 'wmxix': '.ymg GameCube binary — decode to GLB before in-engine use (see customization/parts/wmxix tooling).',
 'no-mercy': 'No Mercy binary — convert to GLB before in-engine use (see no-mercy tooling).',
}

def sid(part_id):
    s = re.sub(r'[^a-z0-9]+', '-', part_id.lower()).strip('-')
    return s[:120]

entries = []
for p in idx['parts']:
    slot = p.get('slot')
    if slot not in SLOTMAP: continue
    m = SLOTMAP[slot]
    entries.append({
      'id': sid(p['part_id']),
      'name': friendly(p['part_id']),
      'type': 'mesh_part' if slot != 'eyes' else 'texture_part',
      'library': p['source_game'],
      'source_game': p['source_game'],
      'file': p['file_path'],
      'size': p.get('size'),
      'conversion': CONV.get(p['source_game'], 'convert to GLB before in-engine use'),
      'geometryPending': True,
      'suite_slot': m['suite_slot'],
      'slotId': m['slotId'],
      'socket': m['socket'],
      'bone_aliases': BONES[m['socket']],
      'menu': m['menu'], 'tab': m['tab'],
      'offset': [0,0,0], 'rotation': [0,0,0], 'scale': 1.0,
      'editable': ['tint','roughness','metalness','offset','rotation','scale','visible'],
      'character_mappings': {},
    })

# Universal CC0 hair
HAIR = [
 ('cc0-hair-quaternius-buns','Quaternius Buns (CC0)','Hair_Buns.gltf'),
 ('cc0-hair-quaternius-buzzed','Quaternius Buzzed (CC0)','Hair_Buzzed.gltf'),
 ('cc0-hair-quaternius-buzzed-female','Quaternius Buzzed Female (CC0)','Hair_BuzzedFemale.gltf'),
 ('cc0-hair-quaternius-long','Quaternius Long (CC0)','Hair_Long.gltf'),
 ('cc0-hair-quaternius-simple-parted','Quaternius Simple Parted (CC0)','Hair_SimpleParted.gltf'),
 ('cc0-hair-quaternius-beard','Quaternius Beard (CC0)','Hair_Beard.gltf'),
 ('cc0-hair-quaternius-brows-regular','Quaternius Eyebrows Regular (CC0)','Eyebrows_Regular.gltf'),
 ('cc0-hair-quaternius-brows-female','Quaternius Eyebrows Female (CC0)','Eyebrows_Female.gltf'),
 ('cc0-hair-dread-ponytail','Toon Dread Ponytail (CC0, tiko479)','dread-ponytail.glb'),
]
for pid, name, fn in HAIR:
    entries.append({
      'id': pid, 'name': name, 'type': 'mesh_part', 'library': 'cc0-hair',
      'source': 'Quaternius CC0-1.0 / opengameart CC0 (see customization/parts/hair/MANIFEST.json)',
      'glb': 'customization/parts/hair/cc0/' + fn,
      'geometryPending': False,
      'suite_slot': 'hair', 'slotId': '2', 'socket': 'head',
      'bone_aliases': BONES['head'], 'menu': 'head', 'tab': 'Head (hair)',
      'offset': [0,0,0], 'rotation': [0,0,0], 'scale': 1.0,
      'editable': ['tint','roughness','metalness','offset','rotation','scale','visible'],
      'character_mappings': {'*': 'universal — socket attach at head with zero offsets; fit=headHeight auto-scale'},
      'notes': 'Suite-resized 512px textures for quaternius (full-res originals on disk at ~/workspace/customization-pulls/quaternius/hair/).' if 'quaternius' in pid else 'Static mesh — rig to head bone on attach.',
    })

existing_ids = {p.get('id') for p in reg['parts']}
new = [e for e in entries if e['id'] not in existing_ids]
reg['parts'].extend(new)

# suite_slots additions
reg['suite_slots'].update({
 'hair': {'attire_slot':'head','menu':'head','tab':'Head (hair)','note':'mesh hair on the Head socket; CC0 universal set wired'},
 'accessory': {'attire_slot':'torso','menu':'attire','tab':'Gear','note':'accessory mesh on torso/arm sockets'},
 'gloves': {'attire_slot':'hands','menu':'attire','tab':'Hands','note':'glove mesh on hand sockets'},
 'shoes': {'attire_slot':'feet','menu':'attire','tab':'Feet','note':'shoe mesh on foot sockets'},
 'gear': {'attire_slot':'torso','menu':'attire','tab':'Gear','note':'gear mesh (belts/chains/pads) on torso'},
 'upper_body': {'attire_slot':'torso','menu':'attire','tab':'Upper','note':'upper-body garment mesh'},
 'lower_body': {'attire_slot':'legs','menu':'attire','tab':'Lower','note':'lower-body garment mesh'},
 'attire': {'attire_slot':'torso','menu':'attire','tab':'Full Body','note':'full-body attire mesh'},
})
reg['libraries'].update({
 'wmxix': {'kind':'hair | gloves | shoes | upper_body | lower_body | accessories | gears | masks','manifest':'customization/parts/PARTS-INDEX.json','note':'WrestleMania XIX teardown parts (ymg binaries; geometryPending until decoded to GLB).','part_class':'mesh_part','path':'customization/parts/wmxix/'},
 'no-mercy': {'kind':'upper_body | lower_body | accessories | gears','manifest':'customization/parts/PARTS-INDEX.json','note':'WWF No Mercy teardown parts (binaries; geometryPending until converted to GLB).','part_class':'mesh_part','path':'customization/parts/no-mercy/'},
 'cc0-hair': {'kind':'hair','manifest':'customization/parts/hair/MANIFEST.json','note':'Universal CC0 hairstyles — Quaternius 8-piece set + toon dread ponytail. Real GLB/glTF, ready to attach.','part_class':'mesh_part','path':'customization/parts/hair/cc0/'},
})
reg['version'] = 2
reg['source'] = reg.get('source','') + ' | 2026-10-18: wired 3372 teardown wearable parts (geometryPending) + 9 universal CC0 hair pieces.'

import collections
print('new registry entries:', len(new), '| total parts now:', len(reg['parts']))
print('by suite_slot:', dict(collections.Counter(e['suite_slot'] for e in new)))
json.dump(reg, open('/home/hatch/workspace/csuite-lane/PARTS-REGISTRY.json','w'), indent=1)
print('wrote PARTS-REGISTRY.json', len(json.dumps(reg))//1024, 'KB')
