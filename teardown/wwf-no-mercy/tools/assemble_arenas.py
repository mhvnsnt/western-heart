#!/usr/bin/env python3
"""Assemble WWF No Mercy per-arena combined OBJs from extracted AkiModel pieces.

Source: western-heart/teardown/wwf-no-mercy/models/ (per-piece OBJs from
extract_all_models.py; vertices are in stored AkiModel coordinates, already
offset/scale-applied).

Findings that shape this assembly:
- Arena pieces come in two flavors: (a) world-placed big structures (crowd
  bowl, stage sets, trons, ramps, barricades, announce table), (b) small
  local-template parts the game instances in code (ring posts, turnbuckles,
  apron skirts, cage pieces) -- no placement data exists in ROM for those,
  so they are concatenated in stored coordinates.
- No rope geometry exists in the ROM file table (verified by label scan);
  AKI games generate ropes procedurally at runtime.
- No separate arena display-list/layout section exists; arena data is purely
  AkiModel files + textures, per the FileTableDB type census.

Output: <outdir>/arena_<name>.obj (10 PPV arenas), ring_normal.obj,
ring_cage.obj, backstage_<area>.obj (5 areas), lobby.obj, plus
assembly_manifest.json and ARENAS.md.

Each output OBJ: `g <file_id>_<sanitized label>` per piece, v/vt/f
preserved, vertex colors merged into a sidecar .vc.

Usage: assemble_arenas.py <models_dir> <outdir>
"""
import json, os, re, sys

ARENA_NAMES = ["RAW", "Smackdown", "Royal Rumble", "WrestleMania",
               "King of the Ring", "Summerslam", "Survivor Series",
               "Backlash", "Armageddon", "No Mercy"]
BACKSTAGE_AREAS = ["Bar/Lounge", "Boiler Room", "Hallway", "Locker Room",
                   "Parking Lot"]

def sanitize(label):
    s = re.sub(r'[^A-Za-z0-9]+', '_', label).strip('_')
    return s[:80] or 'piece'

def load_manifest(models_dir):
    with open(os.path.join(models_dir, 'manifest.json')) as f:
        return json.load(f)['models']

def piece_file(models_dir, entry):
    rel = entry['file']
    p = os.path.join(models_dir, rel)
    if os.path.exists(p):
        return p
    # fall back: search by basename in any category dir
    base = os.path.basename(rel)
    for cat in os.listdir(models_dir):
        q = os.path.join(models_dir, cat, base)
        if os.path.exists(q):
            return q
    return None

def arena_prefix(label):
    m = re.match(r'\[(Arena|Stage)\] ([A-Z][\w &\'.,\-]*?) - ', label)
    if m:
        return m.group(2)
    return None

def classify(entry):
    """Return ('arena', name) / ('ring_normal') / ('ring_cage') /
    ('backstage', area) / ('lobby') / ('shared') / (None)."""
    label = entry['label']
    cat = entry['file'].split('/')[0]
    if cat == 'lobby':
        return ('lobby',)
    if cat == 'backstage':
        m = re.match(r'\[Backstage\] ([\w /&\'.\-]+?) - ', label)
        area = m.group(1) if m else 'unlabeled'
        return ('backstage', area)
    if cat in ('arena', 'stage'):
        name = arena_prefix(label)
        if name:
            return ('arena', name)
        low = label.lower()
        if 'cage match' in low or 'cage piece' in low:
            return ('ring_cage',)
        if ('normal match' in low or 'ring step' in low):
            return ('ring_normal',)
        return ('shared',)
    return (None,)

def write_combined(path, entries, models_dir):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    nv_total = 0
    vc_lines = []
    used = []
    with open(path, 'w') as f:
        f.write('# WWF No Mercy arena assembly by assemble_arenas.py\n')
        f.write('# pieces in stored AkiModel coordinates; see ARENAS.md\n')
        for e in entries:
            p = piece_file(models_dir, e)
            if p is None:
                continue
            gname = f"{e['file_id']}_{sanitize(e['label'])}"
            f.write(f'g {gname}\n')
            voff = nv_total
            nverts = 0
            with open(p) as pf:
                for line in pf:
                    if line.startswith('v '):
                        f.write(line)
                        nverts += 1
                    elif line.startswith('vt '):
                        f.write(line)
                    elif line.startswith('f '):
                        parts = line.split()
                        out = []
                        for pt in parts[1:]:
                            vti = pt.split('/')
                            out.append(f"{int(vti[0]) + voff}/{int(vti[1]) + voff if len(vti) > 1 and vti[1] else ''}".rstrip('/'))
                        f.write('f ' + ' '.join(out) + '\n')
            vc_path = p[:-4] + '.vc'
            if os.path.exists(vc_path):
                vc_lines.extend(open(vc_path).read().splitlines())
            else:
                vc_lines.extend(['255 255 255'] * nverts)
            nv_total += nverts
            used.append(e)
    with open(path[:-4] + '.vc', 'w') as f:
        f.write('\n'.join(vc_lines) + '\n')
    return used

def main():
    models_dir, outdir = sys.argv[1], sys.argv[2]
    entries = load_manifest(models_dir)
    groups = {}
    for e in entries:
        key = classify(e)
        if key[0] is None:
            continue
        groups.setdefault(key, []).append(e)
    for v in groups.values():
        v.sort(key=lambda e: e['file_id'])

    manifest = {"outputs": []}
    os.makedirs(outdir, exist_ok=True)

    def emit(fname, keys):
        sel = []
        for k in keys:
            sel.extend(groups.get(k, []))
        seen = set()
        sel = [e for e in sel if not (e['file_id'] in seen or seen.add(e['file_id']))]
        path = os.path.join(outdir, fname)
        used = write_combined(path, sel, models_dir)
        manifest["outputs"].append({
            "file": fname, "pieces": len(used),
            "verts": sum(e['nverts'] for e in used),
            "faces": sum(e['nfaces'] for e in used),
            "piece_ids": [e['file_id'] for e in used],
        })
        print(f"{fname}: {len(used)} pieces, "
              f"{sum(e['nverts'] for e in used)} verts, "
              f"{sum(e['nfaces'] for e in used)} faces")

    shared = [('shared',)]
    # 10 PPV arenas
    for name in ARENA_NAMES:
        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        emit(f'arena_{slug}.obj',
             [('arena', name), ('ring_normal',)] + shared)
    # cage ring variant
    emit('ring_cage.obj', [('ring_cage',)] + shared)
    # backstage areas
    for area in BACKSTAGE_AREAS:
        slug = re.sub(r'[^a-z0-9]+', '_', area.lower()).strip('_')
        emit(f'backstage_{slug}.obj', [('backstage', area)])
    emit('lobby.obj', [('lobby',)])

    with open(os.path.join(outdir, 'assembly_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    print('wrote assembly_manifest.json')

if __name__ == '__main__':
    main()
