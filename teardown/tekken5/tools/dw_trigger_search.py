#!/usr/bin/env python3
"""dw_trigger_search.py — find a grounded power-up clip for the Soul Surge Bloom
trigger role (replaces dwup00, which reads as a launch: hips to 2.375 m).

Measurement, not guessing: for every wireable 35-bone clip in
teardown/tekken5/dw-motion-curves.json, read the hips height (bone 1
position_mm Y, root-relative) at every keyframe and report:
  - hips_min / hips_max / hips_start / hips_end (mm)
  - rise = hips_max - hips_start (how high it leaps from its start)
  - travel = max horizontal displacement of bone 0 (mm)
A grounded power-up: small rise (no leap), starts low (crouch/gather) and
ends higher (rise), little horizontal travel.
Usage: python3 dw_trigger_search.py [--top N]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, 'repo')
CURVES = os.path.join(REPO, 'teardown', 'tekken5', 'dw-motion-curves.json')
BANK = os.path.join(REPO, 'teardown', 'tekken5', 'dw-motion-bank.json')


def hips_series(clip):
    """Hips height (mm) per keyframe: bone 1 position_mm Y."""
    for cv in clip['curves']:
        if cv['bone'] == 1 and cv['channel'] == 'position_mm':
            return [k[1] for k in cv['keys']]
    return None


def root_travel(clip):
    """Max horizontal displacement of bone 0 (mm) over the clip."""
    for cv in clip['curves']:
        if cv['bone'] == 0 and cv['channel'] == 'position_mm':
            pts = [(k[0], k[2]) for k in cv['keys']]
            x0, z0 = pts[0]
            return max(math.hypot(x - x0, z - z0) for x, z in pts)
    return None


def main():
    top_n = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 15
    with open(CURVES) as f:
        curves = json.load(f)
    with open(BANK) as f:
        bank = json.load(f)
    gloss = {c['source_file']: c for c in bank['clips']}

    rows = []
    for clip in curves['clips']:
        if clip.get('status') != 'decoded' or clip.get('bones') != 35:
            continue
        hips = hips_series(clip)
        if not hips:
            continue
        b = gloss.get(clip['source_file'], {})
        if not b.get('wireable'):
            continue
        hmin, hmax = min(hips), max(hips)
        hstart, hend = hips[0], hips[-1]
        rise = hmax - hstart
        travel = root_travel(clip) or 0.0
        # Grounded power-up shape: starts low, ends higher, small rise.
        crouch = hstart - hmin  # how far below its own min the start sits
        end_rise = hend - hstart
        rows.append({
            'file': clip['source_file'], 'group': clip.get('group'),
            'kit': clip.get('canon_kit_id'), 'frames': clip.get('frames'),
            'gloss': b.get('gloss', ''),
            'hmin': round(hmin), 'hmax': round(hmax), 'hstart': round(hstart),
            'hend': round(hend), 'rise': round(rise), 'travel': round(travel),
            'end_rise': round(end_rise),
        })
    # Rank: grounded first (small rise), then a rising end shape, then low travel.
    rows.sort(key=lambda r: (r['rise'], -r['end_rise'], r['travel']))
    print(f"{len(rows)} wireable 35-bone clips measured (hips = bone 1 Y, mm)")
    print(f"{'file':34} {'kit':12} {'fr':>4} {'hmin':>5} {'hmax':>5} {'rise':>5} {'end+':>5} {'trav':>5}  gloss")
    for r in rows[:top_n]:
        print(f"{r['file'][:34]:34} {str(r['kit'])[:12]:12} {r['frames']:>4} {r['hmin']:>5} "
              f"{r['hmax']:>5} {r['rise']:>5} {r['end_rise']:>5} {r['travel']:>5}  {r['gloss'][:60]}")
    # Reference: the current trigger, for comparison.
    cur = [r for r in rows if r['file'] == 'gym_dwup00.dat']
    print('\nCURRENT TRIGGER for comparison:')
    for r in cur:
        print(f"  {r['file']}: hmin {r['hmin']} hmax {r['hmax']} rise {r['rise']} end_rise {r['end_rise']} travel {r['travel']} — {r['gloss']}")
    # Candidates whose gloss suggests a power-up / charge / rise.
    keys = ('power', 'charge', 'up', 'rise', 'surge', 'bloom', 'aura', 'stance',
            'guard', 'kamae', 'transform', 'burst', 'gather')
    print('\nGLOSS-MATCHED candidates (power/charge/up/rise/surge/bloom/aura/stance/guard/kamae/transform/burst/gather), by rise:')
    cand = [r for r in rows if any(k in r['gloss'].lower() for k in keys)]
    for r in cand[:20]:
        print(f"  {r['file']:34} kit={str(r['kit'])[:12]:12} fr={r['frames']:>4} hmin={r['hmin']:>5} "
              f"hmax={r['hmax']:>5} rise={r['rise']:>5} end+={r['end_rise']:>5} trav={r['travel']:>5} — {r['gloss'][:60]}")
    if not cand:
        print('  (none)')


if __name__ == '__main__':
    main()
