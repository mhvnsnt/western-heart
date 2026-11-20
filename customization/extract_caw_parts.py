#!/usr/bin/env python3
"""Extract ALL WMXIX CAW (edit_data/) files from ISO into customization/parts/wmxix/.

Organizes by category:
  wmxix/base/       - Man/, Woman/ base bodies (the default CAW bodies)
  wmxix/faces/      - Face/, Face_op/ face parts
  wmxix/hair/       - Hair/ styles
  wmxix/upper_body/ - Upper_Body/ attire
  wmxix/lower_body/ - Lower_Body/ attire
  wmxix/shoes/      - Shoes/
  wmxix/gloves/     - Gloves/
  wmxix/gears/      - Gears/ equipment
  wmxix/accessories/ - Wrist/, Knee/, Elbow/ + 64gara/
  wmxix/colors/     - COL/ palettes
  wmxix/common/     - common/ shared
  wmxix/textures/   - .tex, .tga, .tpl, .tm2, .psd texture files

Streams from ISO via ISOReader. Writes PARTS-INDEX entries to JSONL for later merge.
Usage: python3 extract_caw_parts.py
"""
import struct, sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)  # western-heart/
TOOLS = os.path.expanduser('~/workspace/game-reverse-engineering/wwe-wrestlemania-xix/tools')
WMXIX_TEARDOWN = os.path.join(REPO, 'teardown', 'wmxix')
sys.path.insert(0, TOOLS)
sys.path.insert(0, WMXIX_TEARDOWN)
import importlib.util
_spec = importlib.util.spec_from_file_location("extract_yanm", os.path.join(WMXIX_TEARDOWN, "extract_yanm.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ISOReader = _mod.ISOReader

OUT = os.path.join(REPO, 'customization', 'parts', 'wmxix')

# Map edit_data sub-dirs to our categories
# For Man/ and Woman/, the SECOND level determines the category
SUBCAT_MAP = {
    'Face': 'faces',
    'Hair': 'hair',
    'Upper_Body': 'upper_body',
    'Lower_Body': 'lower_body',
    'Shoes': 'shoes',
    'Gloves': 'gloves',
    'Gears': 'gears',
    'Wrist': 'accessories',
    'Knee': 'accessories',
    'Elbow': 'accessories',
    '64gara': 'accessories',
    'Face_op': 'faces',
}
GENDER_DIRS = {'Man', 'Woman'}

TEX_EXTS = {'.tex', '.tga', '.tpl', '.tm2', '.psd', '.tpg'}

def main():
    rdr = ISOReader()
    paths = sorted(p for p in rdr.files if p.startswith('edit_data/'))
    print(f'{len(paths)} edit_data files to extract')

    index_entries = []
    counts = {}
    for p in paths:
        # p = edit_data/MODEL/Man/Elbow/me0_000/l0.ymg or edit_data/COL/000_0.ycg
        rel = p[len('edit_data/'):]
        parts = rel.split('/')
        # Skip MODEL/ prefix if present
        if parts[0] == 'MODEL':
            parts = parts[1:]
        topdir = parts[0] if parts else 'unknown'

        # Texture files go to textures/
        ext = os.path.splitext(p)[1].lower()
        gender_prefix = None
        if ext in TEX_EXTS:
            cat = 'textures'
        elif topdir in GENDER_DIRS and len(parts) > 1:
            # Man/Elbow/..., Woman/Hair/... -> use subcategory
            subcat = parts[1]
            cat = SUBCAT_MAP.get(subcat, 'base')
            gender_prefix = topdir.lower()
        elif topdir == 'COL':
            cat = 'colors'
        elif topdir == 'common':
            cat = 'common'
        else:
            cat = SUBCAT_MAP.get(topdir, 'misc')

        # Build output path preserving sub-structure
        if gender_prefix:
            outpath = os.path.join(OUT, cat, gender_prefix, *parts[1:])
        else:
            outpath = os.path.join(OUT, cat, *parts)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)

        data = rdr.read(p)
        with open(outpath, 'wb') as f:
            f.write(data)

        counts[cat] = counts.get(cat, 0) + 1
        index_entries.append({
            'part_id': p,
            'name': os.path.basename(p),
            'source_game': 'wmxix',
            'slot': cat,
            'file_path': os.path.relpath(outpath, REPO),
            'size': len(data),
        })

    rdr.f.close()

    # Write JSONL index
    idx_path = os.path.join(OUT, 'PARTS-INDEX.jsonl')
    with open(idx_path, 'w') as f:
        for e in index_entries:
            f.write(json.dumps(e) + '\n')

    print(f'\nExtracted {len(index_entries)} files:')
    for cat, n in sorted(counts.items()):
        print(f'  {cat}: {n}')
    print(f'Index: {idx_path}')

if __name__ == '__main__':
    main()
