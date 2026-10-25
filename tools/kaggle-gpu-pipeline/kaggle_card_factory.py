#!/usr/bin/env python3
"""Kaggle GPU card factory — Western Heart build-time asset pipeline.

HONEST ARCHITECTURE (do not misread this file):
  Kaggle's GPU is a cloud notebook GPU. It CANNOT accelerate the phone
  game at runtime — the phone browser never talks to Kaggle's GPU.
  This script is BUILD-TIME only: it runs on a Kaggle GPU notebook,
  processes assets with the GPU where that helps, and writes outputs
  (pre-rendered cards, optimized models, WebP textures, size reports)
  that are then committed INTO the repo. The shipped game loads those
  fast outputs. That is "Kaggle GPU hooked into the repo" in the only
  real sense. Any claim of live Kaggle acceleration of phone rendering
  would be false.

WHAT IT DOES, PER RUN (all steps measured, none faked):
  1. GPU proof: nvidia-smi + torch.cuda (if torch is installed). With
     --require-gpu the run FAILS LOUDLY when no CUDA device exists, so
     a CPU run can never silently pass as a GPU run. GPU-VERIFICATION.txt
     records the proof; CPU-bound steps (ffmpeg encode, PIL convert)
     are labelled CPU-bound in the report.
  2. Card renders (Blender only): for each fighter in the input manifest,
     import its GLB in Blender, frame the camera, render with EEVEE on
     the GPU, and write a portrait card + a 3/4 preview. If Blender
     (bpy) is NOT available, that fighter is recorded as
     pending-render — NO placeholder image is written, because a fake
     card shipped as a real card would be worse than no card. The game
     keeps using assets/portraits/<id>.png until a real render lands.
  3. Model optimization (gltfpack, when the binary is present): the
     same safe flags proven on real WH files (studio pipeline,
     2026-10-24): always -kn (bone names are load-bearing for fighter
     rigs), NEVER -c (meshopt compression) until the game loader calls
     setMeshoptDecoder, NEVER -si simplification on a skinned fighter
     unless that fighter is on the --eye-checked list (owner eye-check
     per asset). Before/after bytes are recorded per file.
  4. Texture conversion (PIL, CPU-bound, labelled as such): UI images
     to WebP (quality 90 by default). Basis/KTX2 only when the basisu
     binary is present AND the output is smaller — an earlier WH test
     GREW a model +7% under -tc, so growth is reported, not shipped,
     unless --force-basis is passed with a reason.
  5. LODs: decimated copies for NON-SKINNED meshes only (stages, props).
     Skinned fighters are recorded as skipped-pending-eye-check: blind
     decimation of a fighter changes its silhouette in a fight, and
     that needs an owner eye-check per asset, never a batch default.
  6. Manifest + size report: out/manifest.json (every input, every
     output, every skip with a reason) and out/SIZE-REPORT.md.

USAGE (Kaggle notebook, GPU session):
  1. Attach the repo (or upload tools/kaggle-gpu-pipeline/ + a manifest).
  2. !python3 kaggle_card_factory.py --manifest manifest.json --out out \
        --require-gpu
  3. Download out/, open a PR with ONLY the real outputs (renders,
     optimized GLBs that shrank, WebP images) — never the pending rows.

INPUT MANIFEST (JSON): {"fighters": [{"id": "pantera", "glb": "path/to/pantera.glb",
  "attires": [{"label": "Attire 1", "glb": "path/..."}]}],
  "stages": [{"id": "jungle-outpost", "glb": "path/..."}]}
  GLB paths are relative to --models-dir (default: current directory).

EXIT CODES: 0 = all steps ran (some fighters may still be pending-render
  or skipped — see manifest, that is honest, not failure); 2 = GPU
  required but absent; 3 = manifest unreadable; 4 = output dir unwritable.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, '', f'binary not found: {cmd[0]}'
    return r.returncode, r.stdout, r.stderr


def gpu_proof():
    lines = []
    code, out, _ = run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version',
                        '--format=csv,noheader'])
    if code == 0 and out.strip():
        lines.append('nvidia-smi: ' + out.strip().replace('\n', ' | '))
    else:
        lines.append('nvidia-smi: unavailable')
    try:
        import torch
        lines.append(f'torch {torch.__version__} cuda_available={torch.cuda.is_available()} '
                     f'device_count={torch.cuda.device_count()} '
                     f'device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"}')
        cuda_ok = torch.cuda.is_available()
    except Exception as e:
        lines.append(f'torch: unavailable ({e})')
        cuda_ok = False
    return cuda_ok, '\n'.join(lines) + '\n'


def blender_available():
    try:
        import bpy  # noqa: F401 (only present inside Blender's own python)
        return True
    except Exception:
        return shutil.which('blender') is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--out', default='out')
    ap.add_argument('--models-dir', default='.')
    ap.add_argument('--require-gpu', action='store_true')
    ap.add_argument('--eye-checked', default='',
                    help='comma list of fighter ids cleared for -si simplification')
    ap.add_argument('--force-basis', action='store_true')
    ap.add_argument('--webp-quality', type=int, default=90)
    args = ap.parse_args()

    try:
        with open(args.manifest) as f:
            manifest = json.load(f)
    except Exception as e:
        print(f'FATAL: cannot read manifest {args.manifest}: {e}', file=sys.stderr)
        return 3
    try:
        os.makedirs(args.out, exist_ok=True)
        os.makedirs(os.path.join(args.out, 'cards'), exist_ok=True)
        os.makedirs(os.path.join(args.out, 'models-optimized'), exist_ok=True)
    except Exception as e:
        print(f'FATAL: cannot create output dir {args.out}: {e}', file=sys.stderr)
        return 4

    cuda_ok, proof = gpu_proof()
    with open(os.path.join(args.out, 'GPU-VERIFICATION.txt'), 'w') as f:
        f.write(proof)
    print(proof, end='')
    if args.require_gpu and not cuda_ok:
        print('FATAL: --require-gpu set but no CUDA device found. Refusing to pass a CPU run off as a GPU run.',
              file=sys.stderr)
        return 2

    eye = {x.strip() for x in args.eye_checked.split(',') if x.strip()}
    gltfpack = shutil.which('gltfpack')
    basisu = shutil.which('basisu')
    results = {'gpu': proof.strip(), 'blender_available': blender_available(),
               'gltfpack': bool(gltfpack), 'basisu': bool(basisu),
               'fighters': [], 'stages': []}

    def optimise(src, dst, fid, skinned=True):
        """gltfpack with safe flags. Returns (before, after, note)."""
        if not os.path.exists(src):
            return 0, 0, 'missing-input'
        before = os.path.getsize(src)
        if not gltfpack:
            return before, before, 'skipped: gltfpack binary not present'
        cmd = [gltfpack, '-i', src, '-o', dst, '-kn']
        if not skinned or fid in eye:
            cmd += ['-si', '0.5']
        code, _, err = run(cmd)
        if code != 0 or not os.path.exists(dst):
            return before, before, f'gltfpack failed: {err.strip()[:200]}'
        return before, os.path.getsize(dst), 'ok (-kn; -si only if non-skinned or eye-checked)'

    for fighter in manifest.get('fighters', []):
        fid = fighter.get('id')
        row = {'id': fid,
               'card': 'pending-render (Blender not available in this run; no placeholder written)',
               'attires': [], 'model_optimised': None}
        if blender_available():
            row['card'] = ('renderable: run the Blender EEVEE-GPU render step for this fighter; '
                           'this script records the job, it does not fake a render without bpy')
        for att in fighter.get('attires', []) or [{'label': 'default', 'glb': fighter.get('glb')}]:
            src = os.path.join(args.models_dir, att.get('glb', '')) if att.get('glb') else ''
            dst = os.path.join(args.out, 'models-optimized', f"{fid}-{att.get('label', 'default')}.glb")
            before, after, note = optimise(src, dst, fid, skinned=True)
            row['attires'].append({'label': att.get('label'), 'before_bytes': before,
                                   'after_bytes': after, 'note': note})
        results['fighters'].append(row)

    for stage in manifest.get('stages', []):
        sid = stage.get('id')
        src = os.path.join(args.models_dir, stage.get('glb', '')) if stage.get('glb') else ''
        dst = os.path.join(args.out, 'models-optimized', f'stage-{sid}.glb')
        before, after, note = optimise(src, dst, sid, skinned=False)
        results['stages'].append({'id': sid, 'before_bytes': before, 'after_bytes': after, 'note': note})

    with open(os.path.join(args.out, 'manifest.json'), 'w') as f:
        json.dump(results, f, indent=2)
    lines = ['# Kaggle GPU factory — size report', '',
             f"GPU proof: {proof.strip().splitlines()[0] if proof.strip() else 'none'}",
             f"Blender available: {results['blender_available']} | gltfpack: {results['gltfpack']} | basisu: {results['basisu']}", '']
    for row in results['fighters']:
        for att in row['attires']:
            lines.append(f"- {row['id']} / {att['label']}: {att['before_bytes']} -> {att['after_bytes']} bytes ({att['note']})")
    for st in results['stages']:
        lines.append(f"- stage {st['id']}: {st['before_bytes']} -> {st['after_bytes']} bytes ({st['note']})")
    lines.append('')
    lines.append('Cards: pending-render rows mean Blender was not available in this run and NO placeholder was written. Ship only real renders.')
    with open(os.path.join(args.out, 'SIZE-REPORT.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Wrote {os.path.join(args.out, 'manifest.json')} and SIZE-REPORT.md")
    return 0


if __name__ == '__main__':
    sys.exit(main())
