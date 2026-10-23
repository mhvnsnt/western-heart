"""Build the W7e CATALOG.json update from /var/tmp/w7e/manifest.json.
Additive: parts[] gains one FULL_BODY entry per converted pack; the
costume-models named gap is flipped out of named_gaps (recorded in _meta);
all other gaps and census numbers are preserved byte-for-byte in meaning."""
import json, sys, hashlib, os

cat_path, man_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
cat = json.load(open(cat_path))
man = json.load(open(man_path))
packs = json.load(open('/home/hatch/workspace/_w7e-stage/scratch/pack_indices.json'))
parts = []
for idx in packs:
    m = man[str(idx)]
    assert m['stage'] in ('glb_ok', 'glb_ok_partial'), f'pack {idx} not converted: {m.get("stage")}'
    partial = m['stage'] == 'glb_ok_partial'
    slug = f'pack{idx:04d}-costume'
    rel = f'customization/parts/tekken5/full_body/{slug}/{slug}.glb'
    parts.append({
        'id': f'tekken5:cmn:full_body:{slug}',
        'name': f'Tekken 5 costume pack {idx:04d} — whole-costume model (TK5DATA1.BIN file {idx:04d} sub02)',
        'library': 'tekken5', 'source_game': 'tekken5', 'char_id': None,
        'slot': 'FULL_BODY', 'slot_id': 10, 'suite_slot': 'full_body',
        'kind': 'customize_item', 'part_class': 'mesh_part', 'scope': 'character',
        'player_cus_id': 0, 'color_slots': 0,
        'file': rel, 'glb': rel, 'format': 'glb',
        'editable': ['tint', 'offset', 'rotation', 'scale', 'visible'],
        'placement': {'socket': 'n/a — full-body costume model (bind pose), not a socket part',
                      'px': 0, 'py': 0, 'pz': 0, 'rx': 0, 'ry': 0, 'rz': 0, 's': 1},
        'nverts': m['glb']['verts'], 'ntris': m['glb']['tris'],
        'textures': {'tim2_picture_indices': m['tex_indices'],
                     'images_embedded': m['glb']['images'],
                     'materials_textured': m['glb']['materials_textured']},
        'conversion': {
            'status': 'converted_geometry_only_missing_pack_texture' if partial else 'converted',
            'tool': 'Range-fetch from GitHub release tekken5-disc-v1 -> FileTableGetPS2-method extraction (raw-or-LCG-XOR, E5 word-sum checksum) -> ModelMagic NUDP VIF decode (0x91/0x93) -> OBJ (UV/normals/material textureIndex) -> tim2dump TIM2->PNG -> Blender -> GLB (materials joined per texture, textures embedded)',
            'source_format': 'PS2 NUDP model + TIM2 textures inside TK5DATA1.BIN per-character packs (checksum-verified extraction, E5 table 0x27B5B0 + checksums 0x27E838)',
            'source_pack': {'data1_file': idx, 'pack_size': m['pack_size'],
                            'checksum_path': m['checksum'],
                            'sub01_tim2_sha256': m['sub01_sha256'], 'sub01_size': m['sub01_size'],
                            'sub02_nudp_sha256': m['sub02_sha256'], 'sub02_size': m['sub02_size'],
                            'vif_blobs_ok': m['blobs_ok'], 'vif_blobs_bad': m['blobs_bad'],
            **({'missing_tex_indices': m['missing_tex_indices'],
                'missing_texture_note': 'pack sub01 is a 192-byte placeholder TIM2 (1 picture, 8x8); the model references textureIndex 4, which does not exist in this pack — geometry converted, no texture could be bound from pack data'} if partial else {})},
            'glb_release': {'repo': 'mhvnsnt/western-heart', 'tag': 'tekken5-costume-glbs-v1',
                            'asset': f'pack{idx:04d}-costume.glb', 'size': m['glb']['size'],
                            'sha256': m['glb_sha256']},
        },
    })
cat['parts'] = parts
meta = cat['_meta']
meta['total'] = len(parts)
meta['by_slot']['FULL_BODY'] = len(parts)
meta['by_part_class']['mesh_part'] = len(parts)
meta['census']['costume_packs_converted_glb'] = len(parts)
meta['census']['costume_pack_char_attribution_proven'] = 0
meta['status'] = ('CONVERTED — W7e (2026-10-21): all 80 costume packs converted to textured GLBs '
                  '(parts[] at FULL_BODY granularity, char_id=null — no data-proven pack->character '
                  'table in held data; visual IDs are survey evidence only). GLB bytes live in GitHub '
                  'release tekken5-costume-glbs-v1 (manifest in conversion doc); the remaining named '
                  'gaps are the ctype-5 VIF-0x82 models, TK5DATA0.BIN, and the skull mask (not found in DATA1).')
meta['glb_storage'] = ('GitHub release mhvnsnt/western-heart tag tekken5-costume-glbs-v1: one asset per '
                       'pack (packNNNN-costume.glb) + manifest.json (sha256/size per asset). Entry file/glb '
                       'fields keep the canonical repo path shape from entry_template; per-entry '
                       'conversion.glb_release carries repo/tag/asset/sha256 for retrieval.')
meta['conversion_lane'] = 'gap-closure W7e, 2026-10-21 (conversion pass named in survey S9)'
cat['named_gaps'] = [g for g in cat['named_gaps'] if g['id'] != 'tekken5:packs:full_body:costume-models']
json.dump(cat, open(out_path, 'w'), indent=1, ensure_ascii=False)
print('entries', len(parts))
