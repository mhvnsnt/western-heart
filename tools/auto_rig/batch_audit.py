#!/usr/bin/env python3
"""tools/auto_rig/batch_audit.py — audit EVERY fighter / attire model the game loads, in one batch (owner 2026-11-01:
"you need to do a universal fix", "get all the character models fixed ... like Negativo and Pantera").

For each distinct model in game/js/assets.js MODEL_URLS (tools/auto_rig/list_models.mjs):
  1. header: skinned or static, joint count, naming pipeline, primitives, compression;
  2. skinned models are decoded (tools/anim/gltf_codec.mjs, run beside a node_modules link) and read in their
     skinned rest pose with ALL primitives merged (rig_inspect.load_skinned), then graded on the failure signatures
     the Negativo re-rig measured (tools/auto_rig/rig_inspect.py region_shares / seam_stats):
       cone face     face weighted off the Head group (old Negativo: Head 57.5%, shoulders 35%) or the chin off
                     Head + Neck (old Negativo: shoulders 80%)
       crushed arms  upper arms weighted to the shoulders / torso (old Negativo: 46%; refit: 6%)
       cracks        UV-seam copies of a vertex carrying different weights (rig_inspect seams)
       pose          A-pose (upper arm well below horizontal): the T-pose regions do not apply; route to the A-pose
                     path (Burger)
  3. a verdict per model and a ranked report: docs/rigs/RIG-AUDIT-<date>.json + .md

Grades come from measured rigs: Pantera (reference) face Head 96.1%; refit Negativo face 99.4%, upper-arm trunk 6%.
Hair hanging on the shoulders is Head-weighted by design (head_territory.py), so the arm test reads the TRUNK share
(shoulder + torso), never the Head share.

    node tools/auto_rig/list_models.mjs > /tmp/models.json
    python3 tools/auto_rig/batch_audit.py --models /tmp/models.json --jobs 3 --out docs/rigs/RIG-AUDIT-2026-11-01
Env: NODE_PATH = node_modules with @gltf-transform + meshoptimizer (tools/setup/setup_toolchain.sh).
"""
import argparse
import datetime
import json
import multiprocessing as mp
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

FACE_HEAD_MIN = 0.85     # face region on the Head group
FACE_TRUNK_MAX = 0.05    # face region on shoulders / torso
CHIN_HEADNECK_MIN = 0.70
ARM_TRUNK_MAX = 0.20     # upper arm on shoulders / torso
SEAM_BAD = 1000          # seam copies disagreeing by > 0.1 (Pantera, reference: 188)
APOSE_DEG = 25           # upper arm this far below horizontal = A-pose


def glb_header(path):
    with open(path, 'rb') as f:
        b = f.read(20)
        n = struct.unpack('<I', b[12:16])[0]
        return json.loads(f.read(n))


def pipeline(names):
    s = ' '.join(names)
    if 'mixamorig' in s: return 'mixamo'
    if 'DEF-' in s or 'Breast' in s or 'Pelvis' in s: return 'gamerig'
    if 'LeftArm' in s and 'Spine2' in s: return 'humanoid'
    if 'L_' in s or '_L' in s: return 'L_R_'
    return 'other'


def group(name):
    import rig_inspect as R
    g = R.bone_group(name)
    if g == 'other':
        n = name.split(':')[-1]
        if n.startswith(('DEF-spine', 'DEF-chest', 'DEF-breast', 'DEF-pelvis', 'DEF-hips')): return 'Torso'
        if n.startswith('DEF-head') or n.startswith(('DEF-jaw', 'DEF-eye', 'HeadTop')): return 'Head'
        if n.startswith('DEF-neck'): return 'Neck'
        if n.startswith(('DEF-upper_arm', 'DEF-forearm', 'DEF-hand', 'DEF-f_', 'DEF-thumb')): return 'Arm'
        if n.startswith(('DEF-thigh', 'DEF-shin', 'DEF-foot', 'DEF-toe')): return 'Leg'
        if n.startswith(('LeftArm', 'RightArm')): return 'Arm'
    return g


def grade(path, codec_dir):
    """One model -> dict (header facts, region group shares, seams, verdict)."""
    out = {'path': os.path.relpath(path, REPO), 'bytes': os.path.getsize(path)}
    try:
        js = glb_header(path)
    except Exception as e:  # noqa: BLE001
        return dict(out, verdict='UNREADABLE', error=str(e)[:200])
    skins = js.get('skins') or []
    out['extensions'] = js.get('extensionsUsed') or []
    out['primitives'] = sum(len(m.get('primitives', [])) for m in js.get('meshes', []))
    if not skins:
        return dict(out, skinned=False, verdict='STATIC (needs a rig)')
    names = [js['nodes'][i].get('name', '') for i in skins[0]['joints']]
    out.update(skinned=True, joints=len(names), pipeline=pipeline(names))
    work = tempfile.mkdtemp(prefix='audit_')
    try:
        plain = path
        if any(x in out['extensions'] for x in ('EXT_meshopt_compression', 'KHR_mesh_quantization', 'KHR_draco_mesh_compression')):
            plain = os.path.join(work, 'plain.glb')
            r = subprocess.run(['node', os.path.join(codec_dir, 'gltf_codec.mjs'), 'decode', path, plain],
                               capture_output=True, text=True, timeout=900)
            if r.returncode or not os.path.exists(plain):
                return dict(out, verdict='UNDECODABLE', error=(r.stderr or r.stdout)[-300:])
        import rig_inspect as R
        P, Jn, W, _, jn, jp = R.load_skinned(plain)
        out['verts'] = int(len(P))
        out['height_m'] = round(float(P[:, 1].max() - P[:, 1].min()), 3)
        need = ('Head', 'Neck', 'Spine2', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightArm', 'RightForeArm', 'Hips', 'Spine1')
        missing = [n for n in need if n not in jp]
        if missing:
            return dict(out, verdict='NONSTANDARD SKELETON (region audit needs %s)' % ', '.join(missing[:4]))
        v = jp['LeftForeArm'] - jp['LeftArm']
        out['upper_arm_deg_below_horizontal'] = round(float(np.degrees(np.arctan2(-v[1], np.hypot(v[0], v[2])))), 1)
        regions = {}
        for label, n, sh in R.region_shares(P, Jn, W, jn, jp):
            g = {}
            for b, w in sh.items():
                gg = group(b)
                g[gg] = g.get(gg, 0.0) + w
            regions[label] = {'n': n, 'groups': {k: round(x, 3) for k, x in sorted(g.items(), key=lambda kv: -kv[1])}}
        out['regions'] = regions
        out['seams'] = R.seam_stats(P, Jn, W, jn)
        issues = []
        if out['upper_arm_deg_below_horizontal'] > APOSE_DEG:
            issues.append('A-POSE')
        face = regions['face (front of head)']
        chin = regions['chin / jaw underside']
        if face['n'] >= 50:
            fg = face['groups']
            if fg.get('Head', 0) < FACE_HEAD_MIN or fg.get('Clav', 0) + fg.get('Torso', 0) > FACE_TRUNK_MAX:
                issues.append('CONE FACE')
        if chin['n'] >= 20 and chin['groups'].get('Head', 0) + chin['groups'].get('Neck', 0) < CHIN_HEADNECK_MIN:
            if 'CONE FACE' not in issues: issues.append('CONE FACE')
        for side in ('L upper arm', 'R upper arm'):
            a = regions[side]
            if a['n'] >= 50 and a['groups'].get('Clav', 0) + a['groups'].get('Torso', 0) > ARM_TRUNK_MAX:
                issues.append('CRUSHED ARMS'); break
        if out['seams']['copies_disagreeing_over_0.1'] > SEAM_BAD:
            issues.append('SEAM CRACKS')
        out['issues'] = issues
        out['verdict'] = 'OK' if not issues else ' + '.join(issues)
        return out
    except Exception as e:  # noqa: BLE001
        return dict(out, verdict='AUDIT ERROR', error=('%s: %s' % (type(e).__name__, e))[:300])
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _job(args):
    return grade(*args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--models', required=True, help='JSON from tools/auto_rig/list_models.mjs')
    ap.add_argument('--out', required=True, help='report path without extension (.json + .md written)')
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--only', default='', help='comma list of substrings of repo paths')
    a = ap.parse_args()
    rows = json.load(open(a.models))
    users = {}
    for key, _url, rel, size in rows:
        if size > 0: users.setdefault(rel, []).append(key)
    paths = [p for p in users if not a.only or any(s in p for s in a.only.split(','))]
    codec_dir = tempfile.mkdtemp(prefix='codec_')  # ES modules ignore NODE_PATH: run a copy beside a link
    shutil.copy(os.path.join(REPO, 'tools/anim/gltf_codec.mjs'), codec_dir)
    if os.environ.get('NODE_PATH'):
        os.symlink(os.environ['NODE_PATH'].split(os.pathsep)[0], os.path.join(codec_dir, 'node_modules'))
    results = []
    with mp.Pool(a.jobs) as pool:
        for r in pool.imap_unordered(_job, [(os.path.join(REPO, p), codec_dir) for p in paths]):
            r['used_by'] = users.get(r['path'], [])
            results.append(r)
            print('%-28s %-62s %s' % (r['used_by'][0][:28], r['path'][-62:], r['verdict']), flush=True)
    shutil.rmtree(codec_dir, ignore_errors=True)
    order = {'OK': 9}
    results.sort(key=lambda r: (order.get(r['verdict'], 0), r['path']))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'date': datetime.date.today().isoformat(), 'tool': 'tools/auto_rig/batch_audit.py',
               'thresholds': {'face_head_min': FACE_HEAD_MIN, 'face_trunk_max': FACE_TRUNK_MAX,
                              'chin_headneck_min': CHIN_HEADNECK_MIN, 'arm_trunk_max': ARM_TRUNK_MAX,
                              'seam_bad_copies_over_0.1': SEAM_BAD, 'apose_deg': APOSE_DEG},
               'models': results}, open(a.out + '.json', 'w'), indent=1)
    lines = ['# Rig audit %s (`tools/auto_rig/batch_audit.py`)' % datetime.date.today().isoformat(), '',
             'Every model in `game/js/assets.js` MODEL_URLS, graded on the Negativo failure signatures. JSON: `%s.json`.'
             % a.out, '', '| verdict | model | used by | face Head | chin Head+Neck | upper-arm trunk (L/R) | seam copies >0.1 | arm deg |',
             '|---|---|---|---|---|---|---|---|']
    for r in results:
        reg = r.get('regions') or {}
        f = reg.get('face (front of head)', {}).get('groups', {})
        c = reg.get('chin / jaw underside', {}).get('groups', {})
        tr = lambda k: (reg.get(k, {}).get('groups', {}).get('Clav', 0) + reg.get(k, {}).get('groups', {}).get('Torso', 0))
        lines.append('| %s | `%s` | %s | %s | %s | %s | %s | %s |' % (
            r['verdict'], r['path'], ', '.join(r['used_by'][:3]),
            ('%.0f%%' % (100 * f.get('Head', 0))) if f else '-', ('%.0f%%' % (100 * (c.get('Head', 0) + c.get('Neck', 0)))) if c else '-',
            ('%.0f%% / %.0f%%' % (100 * tr('L upper arm'), 100 * tr('R upper arm'))) if reg else '-',
            r.get('seams', {}).get('copies_disagreeing_over_0.1', '-'), r.get('upper_arm_deg_below_horizontal', '-')))
    tally = {}
    for r in results:
        tally[r['verdict']] = tally.get(r['verdict'], 0) + 1
    lines[2:2] = ['**%d models:** %s' % (len(results), ', '.join('%s %d' % kv for kv in sorted(tally.items(), key=lambda kv: -kv[1]))), '']
    open(a.out + '.md', 'w').write('\n'.join(lines) + '\n')
    print('wrote %s.json / .md: %s' % (a.out, tally))


if __name__ == '__main__':
    main()
