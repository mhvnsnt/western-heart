#!/usr/bin/env python3
"""tools/auto_rig/refit_rig.py — one command: landmark skeleton re-fit + bone heat + head territory + seam-safe
smoothing + every gate, for a T-pose model (static, or rigged with a misfit skeleton).

Built for Negativo (owner 2026-10-31: "cone face", "head and neck weighted toward his pelvis", "arms crushed like a
steamroller"), whose skeleton had been fitted to his full height including ~0.12 m of hair, so the chest bones sat
in his face, the arms 0.18 m above his arms and the hip joints in his belly. Every step below is a repo tool:

  1. tools/anim/gltf_codec.mjs decode           meshopt -> plain glTF (skipped when already plain)
  2. tools/auto_rig/refit_skeleton.py           template joints fitted inside the mesh + static bind copy
  3. tools/auto_rig/refit_landmarks.py          arms / hips / knees / spine / neck / head from the mesh's landmarks
  4. tools/auto_rig/backends/heat_rebind.py     Blender bone heat (voxel proxy), scaled to --height, CMU 135_04
                                                boxing window baked as the deformation gate clip
  5. tools/auto_rig/head_territory.py           head + hair rigid on Head (geodesic fade at the shoulders), neck blend
  5b. tools/auto_rig/secondary_chains.py        long hair below the neck -> hair_jiggle chains (production hair physics)
  6. tools/auto_rig/backends/seam_safe_smooth.py welded Laplacian + continuous top-4 until strict p99.9 <= --gate
  7. gates: validate.py, anim_check.py (official), rig_inspect.py seams / stretch / shares (+ PNGs with matplotlib)
  8. tools/anim/gltf_codec.mjs encode           -> --out

    python3 tools/auto_rig/refit_rig.py --in roster/X/attires/attire1/source/x-a1.glb \\
        --out roster/X/attires/attire1/source/x-a1-rigged.glb --report-dir docs/proof/<date>/refit-X \\
        --facing +X --height 2.0 [--keep-work] [--no-legs]

--height: the game renders a fighter at its GLB's own size (bodyScale defaults to 1) - match the model being
replaced. Env: WH_BLENDER (Blender 4.0.2), NODE_PATH (node_modules with @gltf-transform + meshoptimizer; see
tools/setup/setup_toolchain.sh). The verdict is <report-dir>/rig_report.json; nothing ships unless it says PASS
and the in-game close-up agrees (tools/anim/t7_closeup_probe.mjs with NO_REMOTE=1).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CODEC = os.path.join(REPO, 'tools', 'anim', 'gltf_codec.mjs')
DONOR = os.path.join(REPO, 'assets', 'free-pull-1', 'cmu-mocap', 'fighting', '135_04.bvh')


def run(cmd, log, env=None, ok=(0,)):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    with open(log, 'a') as f:
        f.write('$ ' + ' '.join(cmd) + '\n' + r.stdout[-20000:] + r.stderr[-20000:] + '\n')
    if r.returncode not in ok:
        sys.exit('step failed (%d): %s\n%s' % (r.returncode, ' '.join(cmd[:6]), r.stderr[-3000:]))
    return r


def last_json(text):
    i = text.find('{')
    try:
        return json.loads(text[i:]) if i >= 0 else {}
    except json.JSONDecodeError:
        j = text.rfind('\n{')
        return json.loads(text[j + 1:]) if j >= 0 else {'raw': text[-2000:]}


def is_meshopt(path):
    import struct
    b = open(path, 'rb').read(20 + 4)
    n = struct.unpack_from('<I', b, 12)[0]
    with open(path, 'rb') as f:
        f.seek(20)
        js = json.loads(f.read(n))
    return 'EXT_meshopt_compression' in (js.get('extensionsUsed') or [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report-dir', required=True)
    ap.add_argument('--facing', default='+Z', help='mesh facing for refit_skeleton (+Z/-Z/+X/-X)')
    ap.add_argument('--height', type=float, required=True, help='output height in metres (match the replaced model)')
    ap.add_argument('--template', default=None, help='template skeleton GLB (refit_skeleton default: pantera.glb)')
    ap.add_argument('--gate', type=float, default=2.5)
    ap.add_argument('--rounds', type=int, default=24)
    ap.add_argument('--no-legs', action='store_true')
    ap.add_argument('--keep-work', action='store_true')
    a = ap.parse_args()
    blender = os.environ.get('WH_BLENDER') or os.path.expanduser('~/workspace/tools/blender/blender-4.0.2-linux-x64/blender')
    os.makedirs(a.report_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix='wh-refit-')
    if not a.keep_work:
        import atexit
        atexit.register(shutil.rmtree, work, True)
    log = os.path.join(a.report_dir, 'steps.log')
    open(log, 'w').close()
    codec = CODEC
    if os.environ.get('NODE_PATH') and not os.path.isdir(os.path.join(os.path.dirname(CODEC), 'node_modules')):
        cdir = os.path.join(work, 'codec')  # ES modules ignore NODE_PATH: run a copy beside a node_modules link
        os.makedirs(cdir)
        os.symlink(os.environ['NODE_PATH'].split(os.pathsep)[0], os.path.join(cdir, 'node_modules'))
        codec = shutil.copy(CODEC, os.path.join(cdir, 'gltf_codec.mjs'))
    py = [sys.executable]
    bl = ['xvfb-run', '-a', 'env', '-u', 'PYTHONPATH', 'XDG_RUNTIME_DIR=/tmp', blender, '-b', '--factory-startup',
          '--python-exit-code', '1', '--python']
    W = lambda n: os.path.join(work, n)  # noqa: E731
    R = lambda n: os.path.join(a.report_dir, n)  # noqa: E731

    # 1-3
    dec = W('decoded.glb')
    if is_meshopt(a.inp):
        run(['node', codec, 'decode', a.inp, dec], log)
    else:
        shutil.copy(a.inp, dec)
    cmd = py + [os.path.join(HERE, 'refit_skeleton.py'), '--mesh', dec, '--out', W('fit.json'), '--facing=' + a.facing,
                '--static-out', W('static.glb')]
    if a.template:
        cmd += ['--template', a.template]
    run(cmd, log)
    cmd = py + [os.path.join(HERE, 'refit_landmarks.py'), '--fit', W('fit.json'), '--out', R('fit_landmarks.json')]
    if a.no_legs:
        cmd.append('--no-legs')
    run(cmd, log)
    shutil.copy(W('fit.json'), R('fit_template.json'))
    # 4
    run(bl + [os.path.join(HERE, 'backends', 'heat_rebind.py'), '--', '--in', W('static.glb'), '--fit',
              R('fit_landmarks.json'), '--out', W('rig.glb'), '--metrics-out', R('heat_rebind_metrics.json'),
              '--height', str(a.height), '--donor', DONOR], log)
    # 5-6
    run(py + [os.path.join(HERE, 'head_territory.py'), '--in', W('rig.glb'), '--out', W('rig_t.glb'),
              '--report', R('head_territory.json')], log)
    # long hair hanging below the neck gets its own hair_jiggle chains (game springbones simulates them) instead of
    # riding the spine / thighs (Phantom: p99.9 7.3 from waist-length hair on his legs); no long hair: unchanged copy
    run(py + [os.path.join(HERE, 'secondary_chains.py'), '--in', W('rig_t.glb'), '--out', W('rig_h.glb'),
              '--report', R('secondary_chains.json')], log, ok=(0, 1))
    if not os.path.exists(W('rig_h.glb')):  # fail-safe: an error here never blocks the refit
        shutil.copy(W('rig_t.glb'), W('rig_h.glb'))
    sm = run(py + [os.path.join(HERE, 'backends', 'seam_safe_smooth.py'), '--in', W('rig_h.glb'), '--out', W('rig_s.glb'),
                   '--gate', str(a.gate), '--rounds', str(a.rounds), '--report', R('seam_safe_smooth.json')], log, ok=(0, 1))
    final = W('rig_s.glb')
    # 7
    val = last_json(run(py + [os.path.join(HERE, 'validate.py'), '--in', final], log, ok=(0, 1)).stdout)
    run(py + [os.path.join(HERE, 'anim_check.py'), '--in', final, '--json-out', R('anim_check.json'),
              '--max-frames', '18', '--quiet'], log, ok=(0, 1))
    ins = os.path.join(HERE, 'rig_inspect.py')
    seams = last_json(run(py + [ins, 'seams', '--glb', final], log).stdout)
    stretch = last_json(run(py + [ins, 'stretch', '--glb', final], log).stdout)
    json.dump(seams, open(R('seams.json'), 'w'), indent=1)
    json.dump(stretch, open(R('stretch.json'), 'w'), indent=1)
    open(R('weight_shares.txt'), 'w').write(run(py + [ins, 'shares', '--glb', final], log).stdout)
    pngs = []
    try:
        import matplotlib  # noqa: F401
        run(py + [ins, 'fit', '--fit', W('fit.json'), '--fit2', R('fit_landmarks.json'), '--out', R('fit_template_vs_landmarks.png')], log)
        run(py + [ins, 'sections', '--fit', R('fit_landmarks.json'), '--out', R('sections.png')], log)
        run(py + [ins, 'weights', '--glb', final, '--out', R('weights.png')], log)
        pngs = ['fit_template_vs_landmarks.png', 'sections.png', 'weights.png']
    except ImportError:
        pass
    # 8
    run(['node', codec, 'encode', final, a.out], log)
    ac = json.load(open(R('anim_check.json')))
    an = list(ac.get('animations', {}).values())
    smooth = json.load(open(R('seam_safe_smooth.json')))
    spikes = [s for x in an for s in x.get('tearing', {}).get('spikes', [])]
    spike_joints = sorted({' + '.join(s['joints']) for s in spikes})
    official = max((x.get('edge_stretch_p999') or 0) for x in an) if an else None
    verdict = {
        'validate_pass': bool(val.get('pass')),
        'strict_stretch_p999': smooth['rounds'][-1]['p999'], 'strict_gate': a.gate,
        'strict_stretch_pass': bool(smooth.get('pass')),
        'official_anim_check_p999': official, 'official_stretch_pass': official is not None and official <= 2.5,
        'seams_pass': bool(seams.get('pass')),
        'tearing_spikes': len(spikes), 'tearing_spike_joints': spike_joints,
        'max_edge_elongation_mm': stretch.get('elongation_mm', {}).get('max'),
    }
    verdict['PASS'] = all(verdict[k] for k in ('validate_pass', 'strict_stretch_pass', 'official_stretch_pass', 'seams_pass'))
    rep = {'tool': 'tools/auto_rig/refit_rig.py', 'input': a.inp, 'output': a.out, 'height_m': a.height,
           'facing_in': a.facing, 'verdict': verdict, 'validate': val, 'pngs': pngs,
           'note': ('tearing spikes are listed with the joints of the moving vertices; the CMU boxing window swings '
                    'the feet with the root pinned (every rig in docs/proof shows 30-80 foot spikes). A spike on a '
                    'vertex that rides one limb rigidly is motion, not a tear; read the stretch report in mm.')}
    json.dump(rep, open(R('rig_report.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    sys.exit(0 if verdict['PASS'] else 1)


if __name__ == '__main__':
    main()
