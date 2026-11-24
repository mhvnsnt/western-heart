#!/usr/bin/env python3
"""Batch-convert the five AKI N64 maps with the FIXED v1.3 converter.

Calls vpw2_to_bannon_v13.py's own functions UNMODIFIED (imported as a
module): convert_pair() for P1/P2 moves (fitted grapple offset +
shared pair lift) and fk_clip()+author_clip() for singles. One
StanceRef per game, built on that game's stance clip (its first anim)
with the Mixamo REST (rest_mixamo.json) — the same mode the main lane
used for the proven VPW2 German pair.

Why not --batch? The converter's --batch mode ignores --rest (it
builds a Bannon-REST stance) and applies NO pair lift; --pair-convert
is the only mode that delivers both, and it is what the main lane ran.
This driver is a loop over --pair-convert-equivalent calls, with one
shared StanceRef per game for speed. No converter code is copied or
changed: every number comes out of the v1.3 module.

Checkpointed/resume-safe: moves whose outputs already exist are
skipped; progress + per-pair fit quality land in
clips/<game>/convert-progress.json.

Usage: convert_batch.py [game ...] [--force] [--limit N] [--only FILE]
  --only FILE: JSON list of move ids to convert (for the proof set)
Outputs: clips/<game>/<move_id>__P1.json (+ __P2.json)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, '/home/hatch/workspace/preview-clips/export')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vpw2_to_bannon_v13 as v13

WORK = os.path.dirname(os.path.abspath(__file__))
REST = '/home/hatch/workspace/preview-clips/export/rest_mixamo.json'
STANCES = {'nomercy': '2DD9', 'wm2k': '1609', 'revenge': '0E39',
           'vpw64': '1347', 'worldtour': '0B55'}


def sanitize(mid):
    return mid.replace(':', '_').replace('/', '_')


def convert_game(game, force=False, limit=None, only=None):
    bank = os.path.join(WORK, 'banks', game)
    mmap = json.load(open(os.path.join(WORK, 'maps', f'{game}-map.json')))
    outdir = os.path.join(WORK, 'clips', game)
    os.makedirs(outdir, exist_ok=True)
    prog_path = os.path.join(outdir, 'convert-progress.json')
    prog = json.load(open(prog_path)) if os.path.exists(prog_path) else {
        'game': game, 'done': {}, 'failed': {}, 'fit_flags': []}
    v13.STANCE_FID = STANCES[game]
    rest = v13.load_rest(REST)
    stance = v13.StanceRef(bank, rest=rest)
    print(f'{game}: stance {STANCES[game]} {stance.nframes}f, OM-y mean '
          f'{stance.om_y:.1f}, scale_y {stance.scale_y:.5f}', flush=True)
    ids = sorted(mmap.keys())
    if only is not None:
        only_set = set(only)
        ids = [i for i in ids if i in only_set]
    if limit:
        ids = ids[:limit]
    # drop stale fit flags for moves in scope (rebuilt on conversion)
    prog['fit_flags'] = [f for f in prog.get('fit_flags', [])
                         if f['move_id'] not in set(ids)]
    done = skipped = failed = 0
    for mid in ids:
        e = mmap[mid]
        name = sanitize(mid)
        p1_path = os.path.join(outdir, f'{name}__P1.json')
        p2_path = os.path.join(outdir, f'{name}__P2.json')
        want_p2 = bool(e.get('p2_fid'))
        exists = os.path.exists(p1_path) and (not want_p2 or
                                              os.path.exists(p2_path))
        if exists and not force:
            skipped += 1
            continue
        try:
            # bank files are 4-digit zero-padded (anim_0ECC.npy); map
            # fids from move_library slugs can be 3-digit ('ECC').
            p1 = e['p1_fid'].zfill(4)
            p2 = e['p2_fid'].zfill(4) if e.get('p2_fid') else None
            if want_p2:
                d, info, lifts = v13.convert_pair(
                    bank, p1, p2, outdir, name,
                    stance, stance, verbose=False)
                belly = info['hand_to_belly_m']['mean']
                prog['done'][mid] = {
                    'p1': e['p1_fid'], 'p2': e['p2_fid'],
                    'offset_m': round(d, 4), 'hand_to_belly_mean_m':
                        round(belly, 4),
                    'pair_lift_max_m': round(max(lifts), 4)}
                # The hand-to-belly fit is only meaningful for
                # waistlock-style grapples (suplex family): for
                # punches/submissions/dives the hands never grip the
                # waist, so a big number is expected, not a defect.
                # Bar: 0.30 m (the G7 waist-centre bar) for waistlock
                # moves only. Calibrated: the proven VPW2 German pair
                # scores 0.187 m on this metric with the Mixamo REST
                # (WM2K German: 0.187 m, NM German: 0.223 m) — so the
                # raw 0.15 m G7 bar is NOT the bar for this REST.
                nm = (e.get('name') or '').lower()
                waistlock = any(w in nm for w in
                                ('suplex', 'driver', 'back body',
                                 'backdrop', 'belly to back',
                                 'fallaway', 'german'))
                # Fragments (break-up / release / repeat / reversal /
                # counter variants) have no lock-up window — the fit
                # metric is meaningless for them.
                fragment = any(w in nm for w in
                               ('break up', 'release', 'repeat',
                                'reversal', 'counter'))
                if waistlock and not fragment and belly > 0.30:
                    prog['fit_flags'].append(
                        {'move_id': mid, 'p1': e['p1_fid'],
                         'p2': e['p2_fid'], 'hand_to_belly_mean_m':
                             round(belly, 4),
                         'note': 'waistlock-family fit > 0.30 m; '
                                 'lock-up contact may read loose'})
            else:
                clip = v13.load_clip(bank, p1)
                frames, roots, n_reps = v13.fk_clip(clip, stance)
                cj = v13.author_clip(frames, roots, e['p1_fid'],
                                     n_reps=n_reps)
                json.dump(cj, open(p1_path, 'w'))
                prog['done'][mid] = {'p1': e['p1_fid'], 'p2': None}
            done += 1
            prog['failed'].pop(mid, None)
        except Exception as ex:
            import traceback
            traceback.print_exc()
            prog['failed'][mid] = {'p1': e.get('p1_fid'),
                                   'p2': e.get('p2_fid'),
                                   'error': f'{type(ex).__name__}: {ex}'}
            failed += 1
        if (done + failed) % 50 == 0:
            json.dump(prog, open(prog_path, 'w'), indent=1)
            print(f'{game}: {done} done, {skipped} skipped, {failed} '
                  f'failed', flush=True)
    json.dump(prog, open(prog_path, 'w'), indent=1)
    print(f'{game}: CONVERT DONE {done} converted, {skipped} skipped, '
          f'{failed} failed, {len(ids)} in scope', flush=True)
    return prog


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('games', nargs='*')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--only', default=None,
                    help='JSON list of move ids to convert')
    args = ap.parse_args()
    only = json.load(open(args.only)) if args.only else None
    games = args.games or ['nomercy', 'wm2k', 'revenge', 'vpw64',
                           'worldtour']
    for g in games:
        convert_game(g, force=args.force, limit=args.limit, only=only)
