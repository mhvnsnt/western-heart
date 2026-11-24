#!/usr/bin/env python3
"""Contract-check assembled preview clips (PREVIEW_CLIPS.md):
52 bones per performer, quaternion norms ~1, finite + bounded Hips
`p` tracks (relative offsets — negative values are correct, see
assemble_preview.py: p = p_glb - BIND_HIPS - FEET).

Usage: verify_previews.py <dir> [dir ...]
"""
import glob
import json
import math
import os
import sys


def check_file(f):
    bad = []
    try:
        d = json.load(open(f))
    except Exception as e:
        return [(f, 'unparseable JSON', type(e).__name__, str(e)[:80])]
    if 'performers' not in d or not d['performers']:
        return [(f, 'no performers')]
    for perf in d['performers']:
        nb = len(perf['tracks'])
        if nb != 52:
            bad.append((f, perf['role'], 'bones', nb))
        for t, keys in perf['tracks'].items():
            for k in keys:
                q = k['q']
                n = math.sqrt(sum(x * x for x in q))
                if not (0.99 <= n <= 1.01):
                    bad.append((f, perf['role'], 'quat norm', t,
                                round(n, 4)))
                if 'p' in k:
                    # Bound is 15 m: running moves (Bronco Buster,
                    # Bulldog) legitimately travel 5-7 m of root
                    # motion; the bound only catches explosions/NaN.
                    if (not all(math.isfinite(v) for v in k['p'])
                            or max(abs(v) for v in k['p']) > 15):
                        bad.append((f, perf['role'], 'hips p extreme',
                                    k['p']))
    return bad


if __name__ == '__main__':
    total = 0
    all_bad = []
    for d in sys.argv[1:]:
        files = sorted(glob.glob(os.path.join(d, '*.json')))
        total += len(files)
        for f in files:
            all_bad.extend(check_file(f))
        print(f'{d}: {len(files)} files checked')
    print(f'TOTAL: {total} files, {len(all_bad)} violations')
    for b in all_bad[:30]:
        print('  ', b)
    sys.exit(1 if all_bad else 0)
