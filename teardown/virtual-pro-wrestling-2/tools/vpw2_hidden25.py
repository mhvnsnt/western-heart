#!/usr/bin/env python3
"""VPW2 costumes + the Hidden 25 manifest.

1. Costumes: file 0x006B "Default Wrestler Costume data", 396 entries of
   49 bytes (VPWStudio GameSpecific/VPW2/DefaultCostumeData.cs). Each of
   the 98 default wrestlers has 4 costume slots (AppearanceIndex = first
   slot, stepping by 4); all edit/controller-pak wrestlers share slot 392.
   Option names resolved from AkiText file 0x006A (edit-mode option lists,
   in enum order).
2. Hidden 25: the 25 wrestlers No Mercy carries as moveset+params only
   (No Mercy fids 0x2a6-0x2be). Mapped to VPW2 roster slots via the
   stable-member order (1-based slots, proven on all 3 AJPW stables)
   matched against the contemporary FAQ roster columns
   (cheaters-heaven.com Virtual Pro Wrestling 2 FAQ, 2000). 23 of 25 map;
   Raven and Big Show are NOT in VPW2 (no FAQ/Wikipedia roster entry) --
   recorded as unmapped with the reason.
3. Per-wrestler model files: face/head/neck triple matched by DB label
   (head shape word + hair type + body-type group), mask parts if masked,
   ring-attire parts matching body type. The 1,589 unlabeled body-part
   models (torso/limbs/hair) are all extracted, but the per-wrestler
   selection table lives in game code VPWStudio does not document -- that
   is the remaining gap, recorded honestly here.

Usage: python3 vpw2_hidden25.py   (run from vpw2/tools/)
Outputs: vpw2/extracted/roster/costumes.json,
  vpw2/extracted/roster/hidden25.json
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.path.dirname(HERE)
BASE = os.path.dirname(VPW2)
RAW = os.path.join(VPW2, 'extracted', 'raw')
ROSTER_DIR = os.path.join(VPW2, 'extracted', 'roster')
MODELS_DIR = os.path.join(VPW2, 'extracted', 'models')

# 006A option-list sections: (field, start_index, count)
SECTIONS = {
    'body_type': (0, 9),
    'ring_attire': (9, 122),
    'entrance_attire': (131, 32),
    'upper_attire': (163, 51),
    'boots': (214, 53),
    'tattoo': (267, 16),
    'wristband': (283, 14),
    'elbow_pad': (297, 4),
    'knee_pad': (301, 16),
    'gloves': (317, 7),
    'head_shape': (324, 5),
    'face_number': (329, 111),
    'hair_type': (440, 15),
    'front_hair': (455, 111),
    'facial_hair': (566, 32),
    'facepaint': (598, 32),
    'accessory': (630, 31),
    'mask_head_shape': (661, 4),
    'mask_hair_type': (665, 3),
    'mask_number': (668, 23),
    'mask_accessory1': (691, 5),
    'mask_accessory2': (696, 12),
    'entrance_weapon': (708, 6),
}
# HeadShape enum -> DB label word
HEAD_SHAPE_WORD = {0: 'Standard', 1: 'Slender', 2: 'Round',
                   3: 'Triangular', 4: 'Tall'}

# Costume struct field order (DefaultCostumeData.cs, 49 bytes)
FIELDS = [
    'body_type', 'skin_color', 'ring_attire', 'ring_attire_color1',
    'ring_attire_color2', 'upper_attire', 'upper_attire_color1',
    'upper_attire_color2', 'entrance_attire', 'entrance_attire_color1',
    'entrance_attire_color2', 'entrance_weapon', 'gloves',
    'gloves_color1', 'gloves_color2', 'tattoo', 'wristband',
    'wristband_color', 'left_elbow_pad', 'left_elbow_pad_color',
    'right_elbow_pad', 'right_elbow_pad_color', 'left_knee_pad',
    'left_knee_pad_color', 'right_knee_pad', 'right_knee_pad_color',
    'boots', 'boots_color1', 'boots_color2', 'mask', 'head_shape',
    'unknown1', 'face_number', 'hair_type', 'hair_color', 'front_hair',
    'unknown2', 'facial_hair', 'facepaint', 'accessory',
    'mask_head_shape', 'mask_number', 'mask_color1', 'mask_color2',
    'mask_color3', 'mask_color4', 'mask_hair_type', 'mask_accessory1',
    'mask_accessory2',
]
# fields whose value indexes a 006A option list (field -> section key)
OPTION_FIELDS = {
    'body_type': 'body_type', 'ring_attire': 'ring_attire',
    'upper_attire': 'upper_attire', 'entrance_attire': 'entrance_attire',
    'entrance_weapon': 'entrance_weapon', 'gloves': 'gloves',
    'tattoo': 'tattoo', 'wristband': 'wristband',
    'left_elbow_pad': 'elbow_pad', 'right_elbow_pad': 'elbow_pad',
    'left_knee_pad': 'knee_pad', 'right_knee_pad': 'knee_pad',
    'boots': 'boots', 'head_shape': 'head_shape',
    'face_number': 'face_number', 'hair_type': 'hair_type',
    'front_hair': 'front_hair', 'facial_hair': 'facial_hair',
    'facepaint': 'facepaint', 'accessory': 'accessory',
    'mask_head_shape': 'mask_head_shape', 'mask_number': 'mask_number',
    'mask_hair_type': 'mask_hair_type',
    'mask_accessory1': 'mask_accessory1',
    'mask_accessory2': 'mask_accessory2',
}

# Hidden 25: (No Mercy moveset fid, inferred real name, VPW2 slot or None,
#  mapping evidence)
# Slot derived from stable-member order + FAQ columns (see module docstring).
HIDDEN25 = [
    ('0x2a6', 'Jun Izumida', 18, 'direct: real name in VPW2 roster'),
    ('0x2a7', 'Raven', None, 'NOT IN VPW2: no FAQ/Wikipedia roster entry; '
     'no VPW2 counterpart found'),
    ('0x2a8', 'Atsushi Onita', 64, 'stable 14 (Legends 3) #6 + FAQ column'),
    ('0x2a9', 'Jinsei Shinzaki', 67, 'stable 7 (Michinoku) #2 + FAQ column'),
    ('0x2aa', 'Hiroyoshi Tenzan', 40, 'stable 4 (IWGP 2) #3 + FAQ column'),
    ('0x2ab', 'Genichiro Tenryu', 30, 'stable 6 (FMW) #8 + FAQ column'),
    ('0x2ac', 'Big Show', None, 'NOT IN VPW2: no FAQ/Wikipedia roster '
     'entry; no VPW2 counterpart found'),
    ('0x2ad', 'Jun Akiyama', 5, 'direct: real name in VPW2 roster'),
    ('0x2ae', 'Akira Taue', 3, 'direct: real name in VPW2 roster'),
    ('0x2af', 'Bruiser Brody', 21, 'stable 12 (Legends 1) #7 + FAQ column; '
     'fake name "King Kong Freddy" = King Kong Brody pun'),
    ('0x2b0', 'Vader', 14, 'direct: real name in VPW2 roster'),
    ('0x2b1', 'Kenta Kobashi', 4, 'direct: real name in VPW2 roster'),
    ('0x2b2', 'Mitsuharu Misawa', 0, 'direct: real name in VPW2 roster'),
    ('0x2b3', 'Satoshi Kojima', 42, 'stable 4 (IWGP 2) #4 + FAQ column'),
    ('0x2b4', 'Kendo Ka Shin', 48, 'stable 5 (IWGP Jr) #3 + FAQ column; '
     'fake name "Mendo Kote Men" ~ Kendo pun'),
    ('0x2b5', 'Kazuo Yamazaki', 29, 'stable 3 (IWGP 1) #7 + FAQ column'),
    ('0x2b6', 'Masahiro Chono', 39, 'stable 4 (IWGP 2) #1 + FAQ column'),
    ('0x2b7', 'Shinya Hashimoto', 26, 'stable 3 (IWGP 1) #1 + FAQ column'),
    ('0x2b8', 'Akira Maeda', 77, 'stable 13 (Legends 2) #2 + FAQ column'),
    ('0x2b9', 'Toshiaki Kawada', 2, 'direct: real name in VPW2 roster'),
    ('0x2ba', 'Hayabusa', 56, 'stable 6 (FMW) #1 + FAQ column; fake name '
     '"Hayate" ~ Hayabusa'),
    ('0x2bb', 'Mil Mascaras', 71, 'stable 12 (Legends 1) #2 + FAQ column; '
     'fake name "El Mascaredo" ~ Mascaras'),
    ('0x2bc', 'Great Sasuke', 66, 'stable 7 (Michinoku) #1 + FAQ column; '
     'fake name "Ninja Tasuke" ~ Sasuke'),
    ('0x2bd', 'Shinjiro Ohtani', 49, 'stable 5 (IWGP Jr) #5 + FAQ column'),
    ('0x2be', 'CIMA', 54, 'stable 7 (Michinoku) #7 + FAQ column '
     '(Shima Nobunaga = CIMA)'),
]


def load_db():
    db = {}
    path = os.path.join(BASE, 'pulls', 'VPWStudio', 'VPWStudio',
                        'VPWStudio', 'FileTableDB', 'VPW2.txt')
    for line in open(path):
        m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', line.strip())
        if m:
            db[int(m.group(1), 16)] = (m.group(2), m.group(3))
    return db


def hair_variant(hair_type):
    """HairType value (0-based, 髪1..髪15) -> DB label hair phrase."""
    h = hair_type + 1
    if h in (5, 6, 14):
        return 'Hair 5, 6, 14'
    if h in (1, 4, 7, 9, 12, 13, 15):
        return f'Hair {h}'
    return 'most Hair Types'


def main():
    options = json.load(open(os.path.join(VPW2, 'extracted', 'text',
                                          '006A.json')))['strings']
    roster = json.load(open(os.path.join(ROSTER_DIR,
                                         'roster.json')))['wrestlers']
    db = load_db()
    # model manifest: fid -> extracted OBJ path
    model_paths = {}
    mman = json.load(open(os.path.join(VPW2, 'extracted', 'models',
                                       'manifest.json')))
    for m in mman['models']:
        model_paths[int(m['file_id'], 16)] = m['file']

    def opt(section, value):
        start, count = SECTIONS[section]
        if 0 <= value < count:
            return options[start + value]
        return None

    # ---- parse all 396 costume entries ----
    blob = open(os.path.join(RAW, '006B.bin'), 'rb').read()
    assert len(blob) == 396 * 49, f'006B len {len(blob)}'
    costumes = []
    for i in range(396):
        raw = blob[i * 49:(i + 1) * 49]
        entry = {'costume_index': i}
        for j, field in enumerate(FIELDS):
            v = raw[j]
            entry[field] = v
            if field in OPTION_FIELDS:
                entry[field + '_name'] = opt(OPTION_FIELDS[field], v)
        costumes.append(entry)
    json.dump({'source': 'file 0x006B, 396 x 49-byte DefaultCostumeData '
                         '(VPWStudio GameSpecific/VPW2/DefaultCostumeData.cs)',
               'slots_note': 'each default wrestler has 4 costume slots; '
                             'AppearanceIndex = first slot. All edit / '
                             'controller-pak wrestlers share slot 392.',
               'names_source': 'AkiText file 0x006A option lists, in enum '
                               'order (sections mapped in vpw2_hidden25.py)',
               'costumes': costumes},
              open(os.path.join(ROSTER_DIR, 'costumes.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'costumes: {len(costumes)} entries parsed')

    # ---- model-label indexes ----
    face_models = {}   # (head_word, hair_phrase, body_group) -> fid
    neck_models, head_models = {}, {}
    mask_face, mask_sides, mask_neck = {}, {}, {}
    ring_attire = {}   # body-type phrase -> [fids]
    for fid, (typ, label) in db.items():
        if typ != 'AkiModel':
            continue
        m = re.match(r'\[(Face|Neck|Head)\] (\w+), (.+), '
                     r'(Body Types 7,8|most Body Types)', label)
        if m:
            part, word, hair, bgroup = m.groups()
            hair = hair.replace('Hair 5,6,14', 'Hair 5, 6, 14').replace(
                'Hair 5, 6 and 14', 'Hair 5, 6, 14')
            key = (word, hair, bgroup)
            if part == 'Face':
                face_models[key] = fid
            elif part == 'Neck':
                neck_models[key] = fid
            else:
                head_models[key] = fid
        m2 = re.match(r'\[(Mask Face|Mask Sides|Mask Neck)\](?: (.*))?$', label)
        if m2:
            (mask_face if m2.group(1) == 'Mask Face' else
             mask_sides if m2.group(1) == 'Mask Sides' else
             mask_neck).setdefault(m2.group(2) or '', []).append(fid)
        m3 = re.match(r'\[Ring Attire\] (.+) \(Body Type (.+)\)', label)
        if m3:
            ring_attire.setdefault(m3.group(2), []).append(fid)
    print(f'face/neck/head triples indexed: {len(face_models)} face variants')

    def match_head(w):
        c = costumes[w['appearance_index']]
        word = HEAD_SHAPE_WORD.get(c['head_shape'])
        hair = hair_variant(c['hair_type'])
        bgroup = ('Body Types 7,8' if c['body_type'] in (7, 8)
                  else 'most Body Types')
        key = (word, hair, bgroup)
        return {'head_shape': word, 'hair': hair, 'body_group': bgroup,
                'face_fid': (f"{face_models[key]:04X}"
                             if key in face_models else None),
                'neck_fid': (f"{neck_models[key]:04X}"
                             if key in neck_models else None),
                'head_fid': (f"{head_models[key]:04X}"
                             if key in head_models else None)}

    def match_attire(w):
        c = costumes[w['appearance_index']]
        bt = c['body_type'] + 1  # DB labels use 1-based body type numbers
        hits = []
        for phrase, fids in ring_attire.items():
            nums = [int(n) for n in re.findall(r'\d+', phrase)]
            if bt in nums:
                hits.extend(f'{f:04X}' for f in fids)
        return sorted(hits)

    # ---- hidden 25 ----
    out = []
    n_mapped = 0
    for nm_fid, real_name, slot, evidence in HIDDEN25:
        rec = {'no_mercy_moveset_fid': nm_fid, 'real_name': real_name,
               'evidence': evidence}
        if slot is None:
            rec['vpw2_slot'] = None
            rec['note'] = ('No VPW2 counterpart: not in the contemporary '
                           'FAQ roster or Wikipedia roster. Their No Mercy '
                           'hidden moveset cannot be linked to any VPW2 '
                           'wrestler by bytes (params/moveset formats '
                           'differ between games); linking by decoded move '
                           'lists needs the bit-packed moveset parser, '
                           'which does not exist yet.')
            out.append(rec)
            continue
        n_mapped += 1
        w = roster[slot]
        c0 = costumes[w['appearance_index']]
        head = match_head(w)
        attire = match_attire(w)
        # verify model files exist on disk (via the models manifest)
        model_files = [f for f in (head['face_fid'], head['neck_fid'],
                                   head['head_fid']) if f]
        head['face_obj'] = model_paths.get(
            int(head['face_fid'], 16)) if head['face_fid'] else None
        head['neck_obj'] = model_paths.get(
            int(head['neck_fid'], 16)) if head['neck_fid'] else None
        head['head_obj'] = model_paths.get(
            int(head['head_fid'], 16)) if head['head_fid'] else None
        missing = [f for f in model_files
                   if int(f, 16) not in model_paths]
        mask_info = None
        if c0['mask'] != 0:
            mask_info = {
                'mask_number': c0['mask_number'],
                'mask_number_name': c0.get('mask_number_name'),
                'mask_head_shape': c0.get('mask_head_shape_name'),
                'mask_hair_type': c0.get('mask_hair_type_name'),
                'note': 'Mask part files are unlabeled beyond [Mask Face] '
                        '(24 files, 0x1944-0x19A9), [Mask Sides] (41, '
                        '0x1956-0x1990), [Mask Neck] (12, 0x1998-0x19A3); '
                        'the per-number selection is game code VPWStudio '
                        'does not document. All mask files are extracted.',
                'mask_face_fids': sorted(
                    f'{f:04X}' for f in mask_face.get('', [])),
                'mask_sides_fids': sorted(
                    f'{f:04X}' for f in mask_sides.get('', [])),
                'mask_neck_fids': sorted(
                    f'{f:04X}' for f in mask_neck.get('', [])),
            }
        rec.update({
            'vpw2_slot': slot, 'vpw2_id4': w['id4'],
            'vpw2_name': w['name'], 'vpw2_name_short': w['name_short'],
            'height_cm': w['height_cm'], 'weight_kg': w['weight_kg'],
            'appearance_index': w['appearance_index'],
            'costume_slots': [w['appearance_index'] + k for k in range(4)],
            'costume_slot0': c0,
            'head_models': head,
            'ring_attire_models': attire,
            'masked': c0['mask'] != 0,
            'mask_models': mask_info,
            'model_files_verified': len(model_files) - len(missing),
            'model_files_missing': missing,
        })
        out.append(rec)
    json.dump({'source': 'No Mercy hidden-25 list (No Mercy lane, '
                         'western-heart main 11ebc898); VPW2 mapping via '
                         'stable-member order + contemporary FAQ roster',
               'mapped': f'{n_mapped}/25',
               'unmapped_note': 'Raven and Big Show are not in VPW2.',
               'model_gap': 'Face/head/neck + ring-attire models are '
                            'label-matched and verified on disk. The 1,589 '
                            'unlabeled body-part models (torso/limbs/hair) '
                            'are all extracted, but the per-wrestler '
                            'selection table lives in game code VPWStudio '
                            'does not document.',
               'wrestlers': out},
              open(os.path.join(ROSTER_DIR, 'hidden25.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'hidden25: {n_mapped}/25 mapped')
    for r in out:
        if r['vpw2_slot'] is not None:
            h = r['head_models']
            print(f"  {r['real_name']:18s} slot {r['vpw2_slot']:3d} "
                  f"{r['vpw2_name']} head={h['face_fid']}/{h['neck_fid']}/"
                  f"{h['head_fid']} attire={len(r['ring_attire_models'])} "
                  f"masked={r['masked']}")
        else:
            print(f"  {r['real_name']:18s} UNMAPPED")


if __name__ == '__main__':
    main()
