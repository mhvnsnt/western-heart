#!/usr/bin/env python3
"""WH Arena Pipeline — canon color/lighting lock.

USER LAW (2026-10-23): DO NOT change arena colors or lighting unless the user
explicitly says so OR it's canon-consistent. Upgrade graphics QUALITY
(god rays, lighting fidelity, effects, geometry) but PRESERVE colors and
canon look. "Colour is law" (CANON.md §8 L1381–1385).

This tool snapshots the canon-locked fields (lighting colors, sky gradients,
fog colors, floor tints, swatches) for every CANON LANDS stage and compares
against the baseline. Any change FAILS unless --approve is passed with a
user-approval reference.

Usage:
    # Create/update the baseline (only when user approves a look change):
    python3 canon_lock.py --snapshot game/js/stages.js

    # Check current stages.js against the baseline (CI):
    python3 canon_lock.py --check game/js/stages.js

    # Check with user approval reference (e.g. user said to change Tree of Life):
    python3 canon_lock.py --check game/js/stages.js --approve "user 2026-10-23: <quote>"

Exit 0 = locked fields unchanged (or approved). Exit 1 = unauthorized changes.
"""
import json
import os
import re
import sys

BASELINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'canon_baseline.json')

# Fields that are canon-locked: colors and lighting INTENT.
# Geometry, props, effects quality, and non-color params are NOT locked.
LOCKED_PATTERNS = [
    r'sky\s*:\s*\[(.*?)\]',
    r'fog\s*:\s*\[(.*?)\]',
    r'hemi\s*:\s*\[(.*?)\]',
    r'sun\s*:\s*\[(.*?)\]',
    r'rim\s*:\s*\[(.*?)\]',
    r'fill\s*:\s*\[(.*?)\]',
    r"swatch\s*:\s*\[(.*?)\]",
    r'tint\s*:\s*([\'"]#[0-9a-fA-F]{6}[\'"])',
    r'platformTint\s*:\s*([\'"]#[0-9a-fA-F]{6}[\'"])',
]


def extract_stage_blocks(src):
    m = re.search(r'export const STAGES = \[(.*?)\n\];', src, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
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
                tier_m = re.search(r"tier:\s*'([^']+)'", block)
                tier = tier_m.group(1) if tier_m else ''
                stages.append((sid, tier, block))
                start = None
    return stages


def locked_fingerprint(block):
    """Extract all canon-locked color/lighting values from a stage block."""
    vals = []
    for pat in LOCKED_PATTERNS:
        for m in re.finditer(pat, block, re.DOTALL):
            # Normalize: strip whitespace, lowercase hex
            v = re.sub(r'\s+', '', m.group(0)).lower()
            vals.append(v)
    return sorted(vals)


def snapshot(src_path):
    src = open(src_path).read()
    baseline = {}
    for sid, tier, block in extract_stage_blocks(src):
        if tier == 'CANON LANDS':
            baseline[sid] = locked_fingerprint(block)
    with open(BASELINE_FILE, 'w') as f:
        json.dump(baseline, f, indent=2)
    print(f'Snapshot written: {BASELINE_FILE} ({len(baseline)} canon stages)')


def check(src_path, approve=None):
    if not os.path.exists(BASELINE_FILE):
        print(f'ERROR: no baseline at {BASELINE_FILE}. Run --snapshot first.')
        return 1
    baseline = json.load(open(BASELINE_FILE))
    src = open(src_path).read()
    current = {}
    for sid, tier, block in extract_stage_blocks(src):
        if tier == 'CANON LANDS':
            current[sid] = locked_fingerprint(block)
    violations = []
    for sid, base_fp in baseline.items():
        if sid not in current:
            violations.append(f'{sid}: stage REMOVED from STAGES (canon stage deleted!)')
            continue
        cur_fp = current[sid]
        if cur_fp != base_fp:
            base_set, cur_set = set(base_fp), set(cur_fp)
            added = sorted(cur_set - base_set)
            removed = sorted(base_set - cur_set)
            detail = []
            if removed:
                detail.append(f'removed: {removed[:3]}')
            if added:
                detail.append(f'added: {added[:3]}')
            violations.append(f'{sid}: canon-locked colors/lighting changed ({", ".join(detail)})')
    for sid in current:
        if sid not in baseline:
            print(f'NOTE: {sid} is a new CANON LANDS stage (no baseline — will be snapshotted on next --snapshot)')
    if violations:
        print(f'\n⛔ CANON LOCK: {len(violations)} unauthorized color/lighting change(s):')
        for v in violations:
            print(f'  ✗ {v}')
        if approve:
            print(f'\n  Approval reference provided: {approve}')
            print('  → Override ACCEPTED (logged). Ensure the user actually said this.')
            return 0
        print('\n  To change a canon arena look, the user must explicitly approve.')
        print('  Then re-run with --approve "<user quote>" or update the baseline via --snapshot.')
        return 1
    print(f'✓ Canon lock clean: {len(current)} canon stages, colors/lighting unchanged.')
    return 0


def main():
    args = sys.argv[1:]
    if '--snapshot' in args:
        i = args.index('--snapshot')
        snapshot(args[i + 1] if i + 1 < len(args) else 'game/js/stages.js')
        return 0
    if '--check' in args:
        i = args.index('--check')
        src = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith('--') else 'game/js/stages.js'
        approve = None
        if '--approve' in args:
            j = args.index('--approve')
            approve = args[j + 1] if j + 1 < len(args) else ''
        return check(src, approve)
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
