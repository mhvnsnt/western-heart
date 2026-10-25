#!/usr/bin/env python3
"""WH Arena Pipeline — stage definition validator.

Validates stage definitions in game/js/stages.js against the pipeline contract:
  1. Required fields present (id, name, dims, spawns, lighting, floor, builder)
  2. Dimensions sane (width/depth/wallDistance within fighting-game bounds)
  3. Spawns within wall distance
  4. Lighting block complete (sky, fog, hemi, sun, rim, fill)
  5. Canon-lock fields present for CANON LANDS tier (swatch, universe, element)

Usage:
    python3 arena_validate.py [path/to/stages.js]

Exit 0 = all stages valid. Exit 1 = validation errors (listed).
"""
import re
import sys

REQUIRED_FIELDS = ['id', 'name', 'dims', 'spawns', 'lighting', 'floor', 'builder']
REQUIRED_DIMS = ['width', 'depth', 'wallDistance']
REQUIRED_LIGHTING = ['sky', 'fog', 'hemi', 'sun', 'rim', 'fill']

# Sanity bounds from teardown research (Tekken standard: 16.8m wide arena)
MAX_WIDTH = 40.0
MAX_DEPTH = 20.0
MAX_WALL = 20.0


def parse_stages(src):
    """Extract stage blocks from stages.js source. Returns list of (id, block_text)."""
    # Find the STAGES array
    m = re.search(r'export const STAGES = \[(.*?)\n\];', src, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    # Split on top-level { ... } blocks (naive brace matching)
    stages = []
    depth = 0
    start = None
    for i, ch in enumerate(body):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                block = body[start:i + 1]
                id_m = re.search(r"id:\s*'([^']+)'", block)
                sid = id_m.group(1) if id_m else f'unknown@{start}'
                stages.append((sid, block))
                start = None
    return stages


def validate_stage(sid, block):
    errors = []
    for field in REQUIRED_FIELDS:
        if not re.search(rf'\b{field}\s*:', block):
            errors.append(f'{sid}: missing required field `{field}`')
    # dims
    dm = re.search(r'dims:\s*\{([^}]+)\}', block)
    if dm:
        dims_text = dm.group(1)
        dims = dict(re.findall(r'(\w+):\s*([\d.]+)', dims_text))
        for d in REQUIRED_DIMS:
            if d not in dims:
                errors.append(f'{sid}: dims missing `{d}`')
        try:
            w = float(dims.get('width', 0))
            dp = float(dims.get('depth', 0))
            wd = float(dims.get('wallDistance', 0))
            if w > MAX_WIDTH:
                errors.append(f'{sid}: width {w} exceeds max {MAX_WIDTH}')
            if dp > MAX_DEPTH:
                errors.append(f'{sid}: depth {dp} exceeds max {MAX_DEPTH}')
            if wd > MAX_WALL:
                errors.append(f'{sid}: wallDistance {wd} exceeds max {MAX_WALL}')
            if wd > w / 2 + 0.01:
                errors.append(f'{sid}: wallDistance {wd} > width/2 {w/2} (fighters spawn outside walls)')
        except ValueError:
            errors.append(f'{sid}: dims contain non-numeric values')
    # spawns within walls
    sm = re.search(r'spawns:\s*\{([^}]+)\}', block)
    if sm and dm:
        try:
            spawns = dict(re.findall(r'(\w+):\s*(-?[\d.]+)', sm.group(1)))
            wd = float(dims.get('wallDistance', 99))
            for k, v in spawns.items():
                if abs(float(v)) > wd:
                    errors.append(f'{sid}: spawn {k}={v} outside wallDistance {wd}')
        except ValueError:
            pass
    # lighting
    lm = re.search(r'lighting:\s*\{', block)
    if lm:
        for lf in REQUIRED_LIGHTING:
            # look for the key inside the lighting block (approximate: after lighting:)
            li = block.find('lighting:')
            if not re.search(rf'\b{lf}\s*:', block[li:li + 3000]):
                errors.append(f'{sid}: lighting missing `{lf}`')
    # canon lands need swatch + universe + element
    if "'CANON LANDS'" in block or '"CANON LANDS"' in block:
        for cf in ['swatch', 'universe', 'element']:
            if not re.search(rf'\b{cf}\s*:', block):
                errors.append(f'{sid}: CANON LANDS tier missing `{cf}` (canon grounding required)')
    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'game/js/stages.js'
    try:
        src = open(path).read()
    except FileNotFoundError:
        print(f'ERROR: {path} not found')
        return 1
    stages = parse_stages(src)
    if not stages:
        print('ERROR: no stages parsed from STAGES array')
        return 1
    print(f'Validating {len(stages)} stages in {path}...')
    all_errors = []
    for sid, block in stages:
        all_errors.extend(validate_stage(sid, block))
    if all_errors:
        print(f'\n{len(all_errors)} VALIDATION ERRORS:')
        for e in all_errors:
            print(f'  ✗ {e}')
        return 1
    print(f'✓ All {len(stages)} stages valid.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
