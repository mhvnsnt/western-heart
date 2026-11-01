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
    """Static mesh (no skeleton): (facing, height m, 'T'|'A'). Facing: the toes reach further past the ankles than the
    heels do; ambiguous feet (a robe on the floor) fall back to +Z, and a wrong guess cannot ship (the refit's gates
    and the re-audit reject it). Pose: arm span across the facing at shoulder height ~ body height = T-pose."""
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
    floor, ankle = V[V[:, 1] < y0 + 0.03 * H], V[(V[:, 1] > y0 + 0.06 * H) & (V[:, 1] < y0 + 0.10 * H)]
    best, ratio = '+Z', 0.0
    if len(floor) > 20 and len(ankle) > 20:
        for name, u in (('+X', [1, 0]), ('-X', [-1, 0]), ('+Z', [0, 1]), ('-Z', [0, -1])):
            f, a = floor[:, [0, 2]] @ np.array(u, float), ankle[:, [0, 2]] @ np.array(u, float)
            ahead, behind = f.max() - a.mean(), a.mean() - f.min()
            if behind > 0 and ahead / behind > ratio: best, ratio = name, ahead / behind
    facing = best if ratio >= 1.3 else '+Z'
    side = 0 if facing in ('+Z', '-Z') else 2  # arms run across the facing
    band = V[(V[:, 1] > y0 + 0.70 * H) & (V[:, 1] < y0 + 0.90 * H)]
    span = (band[:, side].max() - band[:, side].min()) if len(band) else 0.0
    return facing, round(float(H), 3), ('T' if span > 0.80 * H else 'A')


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
            facing, height, pose = static_facing_height_pose(src, cdir)
            res['static_pose'] = pose
            if pose != 'T':
                return dict(res, facing=facing, height_m=height, status='SKIPPED (static A-pose: A-pose path)')
        res.update(facing=facing, height_m=height)
        if dry: return dict(res, status='DRY RUN')
        env = dict(os.environ)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'refit_rig.py'), '--in', src, '--out', out, '--report-dir', rep,
                            '--facing', facing, '--height', str(height)], capture_output=True, text=True, env=env)
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
