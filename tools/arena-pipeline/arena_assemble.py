#!/usr/bin/env python3
"""WH Arena Pipeline — venue manifest assembler.

Follows the Def Jam VENUE.XML pattern (teardown research 2026-10-23): a venue
is a MANIFEST — model file + display name + IDs + references to crowd,
ambient, sound, and lighting config blocks. Atmosphere is data-driven
composition, not baked geometry.

Also follows the WMXIX pattern: an arena slot = package manifest where
geometry, textures, lighting, staging, crowd, and overlays are separate
concerns loaded by an arena loader.

This tool takes a stage manifest JSON and:
  1. Validates all referenced files exist
  2. Validates the geometry (GLB present, has meshes)
  3. Emits a game-ready package manifest the arena loader consumes
  4. Runs the canon-lock check on any lighting/color overrides

Manifest format (example: manifests/tree-of-life.json):
{
  "id": "tree-of-life",
  "name": "TREE OF LIFE",
  "tier": "CANON LANDS",
  "geometry": "game/assets/stages/tree-of-life.glb",   // optional: procedural builder instead
  "builder": "treelife",                                // procedural fallback
  "groups": {                                           // named mesh groups (No Mercy pattern)
    "preserve": ["Soul_Fruit", "Trunk", "Dunes"]        // groups the game targets
  },
  "fighting_surface": {"y": 0, "detect": "ring_mat"},   // y=0 normalization
  "crowd": {"type": "soul_motes", "count": 260},        // procedural, not geometry
  "ambient": "desert_dawn",
  "sounds": "TreeOfLifeSFX",
  "lighting_rig": "lighting/tree-of-life.json",        // separate .light file (WMXIX pattern)
  "canon": {"source": "CANON.md §8 L1351", "locked": true}
}

Usage:
    python3 arena_assemble.py manifests/tree-of-life.json --out game/assets/stages/
    python3 arena_assemble.py --validate-all manifests/
"""
import json
import os
import sys

REQUIRED_MANIFEST_FIELDS = ['id', 'name', 'tier']
GEOMETRY_FIELDS = ['geometry', 'builder']  # at least one required


def load_manifest(path):
    with open(path) as f:
        return json.load(f)


def validate_manifest(manifest, base_dir):
    """Returns list of errors. Empty = valid."""
    errors = []
    mid = manifest.get('id', '?')
    for f in REQUIRED_MANIFEST_FIELDS:
        if f not in manifest:
            errors.append(f'{mid}: manifest missing `{f}`')
    if not any(manifest.get(g) for g in GEOMETRY_FIELDS):
        errors.append(f'{mid}: need `geometry` (GLB path) or `builder` (procedural)')
    # geometry file exists
    geo = manifest.get('geometry')
    if geo:
        gpath = os.path.join(base_dir, geo)
        if not os.path.exists(gpath):
            errors.append(f'{mid}: geometry file not found: {geo}')
        elif os.path.getsize(gpath) == 0:
            errors.append(f'{mid}: geometry file is empty: {geo}')
    # lighting rig exists
    lr = manifest.get('lighting_rig')
    if lr:
        lrpath = os.path.join(base_dir, lr)
        if not os.path.exists(lrpath):
            errors.append(f'{mid}: lighting rig not found: {lr}')
    # canon lock for CANON LANDS
    if manifest.get('tier') == 'CANON LANDS':
        canon = manifest.get('canon', {})
        if not canon.get('source'):
            errors.append(f'{mid}: CANON LANDS manifest needs canon.source (CANON.md reference)')
        if canon.get('locked') is not True:
            errors.append(f'{mid}: CANON LANDS manifest needs canon.locked=true')
    # fighting surface
    fs = manifest.get('fighting_surface', {})
    if fs and 'y' in fs:
        try:
            float(fs['y'])
        except (ValueError, TypeError):
            errors.append(f'{mid}: fighting_surface.y must be numeric')
    return errors


def assemble(manifest_path, out_dir):
    manifest = load_manifest(manifest_path)
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    # base_dir for relative paths: repo root (two up from manifests/)
    repo_root = os.path.abspath(os.path.join(base_dir, '..', '..'))
    errors = validate_manifest(manifest, repo_root)
    if errors:
        print(f'⛔ {manifest_path}: {len(errors)} errors:')
        for e in errors:
            print(f'  ✗ {e}')
        return 1
    mid = manifest['id']
    # Emit game-ready package manifest
    package = {
        'id': mid,
        'name': manifest['name'],
        'tier': manifest['tier'],
        'geometry': manifest.get('geometry'),
        'builder': manifest.get('builder'),
        'groups': manifest.get('groups', {}),
        'fighting_surface_y': manifest.get('fighting_surface', {}).get('y', 0),
        'crowd': manifest.get('crowd'),
        'ambient': manifest.get('ambient'),
        'sounds': manifest.get('sounds'),
        'lighting_rig': manifest.get('lighting_rig'),
        'canon_locked': manifest.get('canon', {}).get('locked', False),
        'pipeline_version': 'wh.arena-manifest/1',
    }
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{mid}.package.json')
    with open(out_path, 'w') as f:
        json.dump(package, f, indent=2)
    print(f'✓ {mid}: package manifest → {out_path}')
    return 0


def validate_all(manifests_dir):
    repo_root = os.path.abspath(os.path.join(manifests_dir, '..', '..'))
    total_errors = 0
    count = 0
    for fn in sorted(os.listdir(manifests_dir)):
        if not fn.endswith('.json'):
            continue
        count += 1
        path = os.path.join(manifests_dir, fn)
        try:
            manifest = load_manifest(path)
        except json.JSONDecodeError as e:
            print(f'⛔ {fn}: invalid JSON: {e}')
            total_errors += 1
            continue
        errors = validate_manifest(manifest, repo_root)
        if errors:
            total_errors += len(errors)
            for e in errors:
                print(f'  ✗ {e}')
        else:
            print(f'✓ {manifest.get("id", fn)}: manifest valid')
    print(f'\n{count} manifests, {total_errors} errors')
    return 1 if total_errors else 0


def main():
    args = sys.argv[1:]
    if '--validate-all' in args:
        i = args.index('--validate-all')
        return validate_all(args[i + 1])
    if len(args) >= 1 and args[0].endswith('.json'):
        out_dir = 'game/assets/stages'
        if '--out' in args:
            out_dir = args[args.index('--out') + 1]
        return assemble(args[0], out_dir)
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
