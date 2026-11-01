#!/usr/bin/env python3
"""tools/auto_rig/batch_refit.py — the universal rig fix in batches (owner 2026-11-01: "you need to do a universal fix",
"get everyone that's easier done faster ... in batches instead of one at a time").

Reads the rig audit (tools/auto_rig/batch_audit.py) and re-rigs every flagged model (CONE FACE, CRUSHED ARMS, and
STATIC models with no rig at all, which cannot animate in a fight) with the Negativo pipeline
(tools/auto_rig/refit_rig.py: landmark skeleton fit, bone heat, head territory, seam-safe smoothing, gates), in
parallel jobs, each model's facing and height measured from the model itself:
  * facing  : toes ahead of the ankles in the file's own bind space (+X / -X / +Z / -Z), as refit_skeleton does;
  * height  : the model's skinned rest height, kept (the game renders a GLB at its own size: AGENTS.md rig law 5).
A refit SHIPS only if (1) refit_rig's rig_report.json says PASS, (2) the output re-grades with batch_audit.grade()
without CONE FACE / CRUSHED ARMS, and (3) it fits jsDelivr (<= 19.5 MB, tools/deploy/fit_cdn_budget.py) because the
Pages site is full. The old file is never touched (keep-both): the refit lands next to it as <stem>-refit.glb.
Results: <report-root>/batch.json, one row per model; tools/auto_rig/apply_refits.py then points MODEL_URLS at the
shipped ones.

    python3 tools/auto_rig/batch_refit.py --audit docs/rigs/RIG-AUDIT-2026-11-01.json \\
        --report-root docs/proof/2026-11-01/refit-batch --jobs 2 [--only phantom,diablo] [--limit 10] [--dry-run]
Env: WH_BLENDER (Blender 4.0.2), NODE_PATH (node_modules with @gltf-transform + meshoptimizer).
A-pose models (Burger) and nonstandard skeletons are listed as skipped: they need the A-pose path.
"""
import argparse
import json
import multiprocessing as mp
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

FIX = ('CONE FACE', 'CRUSHED ARMS')
CDN_BUDGET = 19.5e6


def codec_dir():
    d = tempfile.mkdtemp(prefix='codec_')
    shutil.copy(os.path.join(REPO, 'tools/anim/gltf_codec.mjs'), d)
    if os.environ.get('NODE_PATH'):
        os.symlink(os.environ['NODE_PATH'].split(os.pathsep)[0], os.path.join(d, 'node_modules'))
    return d


def facing_and_height(path, cdir):
    """(+X|-X|+Z|-Z, height m) from the toes in the file's own bind space and the skinned rest height."""
    import anim_check as ac
    import rig_inspect as R
    work = tempfile.mkdtemp(prefix='face_')
    try:
        plain = os.path.join(work, 'p.glb')
        r = subprocess.run(['node', os.path.join(cdir, 'gltf_codec.mjs'), 'decode', path, plain], capture_output=True, text=True)
        if r.returncode: raise RuntimeError('decode: ' + r.stderr[-200:])
        m = ac.AnimModel(plain)
        bind = m.bind_world()
        idx = {m.nodes[int(j)].get('name', '').split(':')[-1]: int(j) for j in m.joint_nodes}
        p = lambda n: np.asarray(bind[idx[n]])[:3, 3]
        fwd = (p('LeftToeBase') - p('LeftFoot')) + (p('RightToeBase') - p('RightFoot'))
        ax = max([('+X', fwd[0]), ('-X', -fwd[0]), ('+Z', fwd[2]), ('-Z', -fwd[2])], key=lambda t: t[1])[0]
        P = R.load_skinned(plain)[0]
        return ax, round(float(P[:, 1].max() - P[:, 1].min()), 3)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def static_facing_height_pose(path, cdir):
    """Static mesh (no skeleton): (facing, height m, 'T'|'A', confidence). The arms span ACROSS the facing: at
    shoulder height the wider horizontal axis is the arm axis (Gashadokuro's kaiju model faces +X with its arms along
    Z; a feet-only test read its floor tail as heels). The sign along the facing axis comes from the feet: toes
    reach further past the ankles than heels do, using only floor points near each ankle (a tail or cape on the
    floor is ignored). Confidence < 1.3 means ambiguous: batch_refit reports it for a fit-plot review instead of
    guessing; a wrong facing cannot ship anyway (the refit's gates and the re-audit reject it)."""
    import refit_skeleton as RS
    work = tempfile.mkdtemp(prefix='face_')
    try:
        plain = os.path.join(work, 'p.glb')
        r = subprocess.run(['node', os.path.join(cdir, 'gltf_codec.mjs'), 'decode', path, plain], capture_output=True, text=True)
        if r.returncode: raise RuntimeError('decode: ' + r.stderr[-200:])
        V = np.asarray(RS.load_mesh(plain)[0], dtype=np.float64)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    y0, H = V[:, 1].min(), V[:, 1].max() - V[:, 1].min()
    band = V[(V[:, 1] > y0 + 0.65 * H) & (V[:, 1] < y0 + 0.92 * H)]
    ext = [band[:, 0].max() - band[:, 0].min(), band[:, 2].max() - band[:, 2].min()] if len(band) else [0.0, 0.0]
    arm_ax = 0 if ext[0] >= ext[1] else 2               # arms along X -> facing along Z, and vice versa
    f_ax = 2 if arm_ax == 0 else 0
    pose = 'T' if max(ext) > 0.80 * H else 'A'
    ankle = V[(V[:, 1] > y0 + 0.06 * H) & (V[:, 1] < y0 + 0.10 * H)]
    floor = V[V[:, 1] < y0 + 0.03 * H]
    sign, conf = +1, 0.0
    if len(ankle) > 20 and len(floor) > 20:
        c = ankle[:, [0, 2]].mean(0)
        near = floor[np.hypot(floor[:, 0] - c[0], floor[:, 2] - c[1]) < 0.18 * H]  # the feet, not a tail
        if len(near) > 20:
            a = ankle[:, f_ax].mean()
            ahead, behind = near[:, f_ax].max() - a, a - near[:, f_ax].min()
            if min(ahead, behind) > 0:
                sign, conf = (1, ahead / behind) if ahead >= behind else (-1, behind / ahead)
    facing = ('+' if sign > 0 else '-') + ('Z' if f_ax == 2 else 'X')
    return facing, round(float(H), 3), pose, round(float(conf), 2)


def refit_one(row, report_root, cdir, dry):
    src = os.path.join(REPO, row['path'])
    stem, ext = os.path.splitext(src)
    out = stem + '-refit' + ext
    key = row['used_by'][0]
    rep = os.path.join(REPO, report_root, re.sub(r'[^\w.-]+', '_', key))
    res = {'key': key, 'used_by': row['used_by'], 'src': row['path'], 'out': os.path.relpath(out, REPO), 'audit': row['verdict']}
    t0 = time.time()
    try:
        if row.get('skinned'):
            facing, height = facing_and_height(src, cdir)
        else:
            facing, height, pose, conf = static_facing_height_pose(src, cdir)
            res.update(static_pose=pose, facing_confidence=conf)
            if conf < 1.3:
                return dict(res, facing=facing, height_m=height, status='REVIEW (static facing ambiguous: check the fit plot)')
        res.update(facing=facing, height_m=height)
        if dry: return dict(res, status='DRY RUN')
        env = dict(os.environ)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'refit_rig.py'), '--in', src, '--out', out, '--report-dir', rep,
                            '--facing=' + facing, '--height=' + str(height)], capture_output=True, text=True, env=env)  # '=': '-Z' is a value
        res['seconds'] = round(time.time() - t0)
        if r.returncode or not os.path.exists(out):
            return dict(res, status='REFIT FAILED', error=(r.stderr or r.stdout)[-400:])
        rr = json.load(open(os.path.join(rep, 'rig_report.json')))
        res['rig_report'] = rr.get('verdict')
        if rr.get('verdict') != 'PASS':
            os.remove(out)
            return dict(res, status='GATE FAILED (rig_report)')
        import batch_audit as BA
        g = BA.grade(out, cdir)
        res['regrade'] = g.get('verdict')
        if any(f in g.get('verdict', '') for f in FIX):
            os.remove(out)
            return dict(res, status='GATE FAILED (re-audit: %s)' % g.get('verdict'))
        if os.path.getsize(out) > CDN_BUDGET:
            fit = subprocess.run([sys.executable, os.path.join(REPO, 'tools/deploy/fit_cdn_budget.py'), out, out, '--budget', str(CDN_BUDGET)],
                                 capture_output=True, text=True, env=env)
            if fit.returncode or os.path.getsize(out) > CDN_BUDGET:
                return dict(res, status='TOO BIG FOR CDN (%d B)' % os.path.getsize(out), error=fit.stderr[-300:])
        res['bytes'] = os.path.getsize(out)
        return dict(res, status='SHIP')
    except Exception as e:  # noqa: BLE001
        return dict(res, status='ERROR', error=('%s: %s' % (type(e).__name__, e))[:300])


def _job(a):
    return refit_one(*a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', required=True)
    ap.add_argument('--report-root', required=True)
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--only', default='')
    ap.add_argument('--exclude', default='', help='comma list of keys / path substrings to leave out')
    ap.add_argument('--max-prims', type=int, default=0,
                    help='only models with at most this many primitives (multi-part support in head_territory / seam_safe_smooth pending)')
    ap.add_argument('--kind', choices=('all', 'rigged', 'static'), default='all',
                    help='rigged = re-rig skinned models (the proven Negativo path); static = rig the unrigged ones')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    rows = json.load(open(a.audit))['models']
    want, skipped = [], []
    for r in rows:
        v = r.get('verdict', '')
        if not (any(f in v for f in FIX) or v.startswith('STATIC')): continue
        if 'A-POSE' in v: skipped.append((r['path'], 'A-pose: needs the A-pose path')); continue
        if a.only and not any(s in ' '.join(r['used_by']) + r['path'] for s in a.only.split(',')): continue
        if a.exclude and any(s in ' '.join(r['used_by']) + r['path'] for s in a.exclude.split(',')): continue
        if (a.kind == 'rigged' and not r.get('skinned')) or (a.kind == 'static' and r.get('skinned')): continue
        if a.max_prims and r.get('primitives', 1) > a.max_prims: continue
        want.append(r)
    # a fighter's default model first (what a player sees first; a static default cannot animate at all), then attires
    want.sort(key=lambda r: (0 if any(re.fullmatch(r'[a-z0-9_-]+', k) and 'attire' not in k for k in r['used_by']) else 1,
                             0 if not r.get('skinned') else 1, r['path']))
    if a.limit: want = want[:a.limit]
    cdir = codec_dir()
    os.makedirs(os.path.join(REPO, a.report_root), exist_ok=True)
    out_path = os.path.join(REPO, a.report_root, 'batch.json')
    done = json.load(open(out_path))['results'] if os.path.exists(out_path) else []
    seen = {d['src'] for d in done if d.get('status') == 'SHIP'}
    todo = [r for r in want if r['path'] not in seen]
    print('%d flagged (A-pose skipped: %d); %d already shipped; running %d with %d jobs' % (len(want), len(skipped), len(seen), len(todo), a.jobs), flush=True)
    with mp.Pool(a.jobs) as pool:
        for res in pool.imap_unordered(_job, [(r, a.report_root, cdir, a.dry_run) for r in todo]):
            done = [d for d in done if d['src'] != res['src']] + [res]
            json.dump({'audit': a.audit, 'skipped': skipped, 'results': done}, open(out_path, 'w'), indent=1)
            print('%-28s %-22s %s' % (res['key'][:28], res['status'][:22], res.get('error', '')[:80]), flush=True)
    shutil.rmtree(cdir, ignore_errors=True)


if __name__ == '__main__':
    main()
