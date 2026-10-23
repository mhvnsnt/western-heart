#!/usr/bin/env python3
"""Validate select-screen default models for all fighters.

For each fighter in roster-full.js, resolves the effective default model
(via attires.js selectedAttireModel logic), then validates the GLB:
  - file exists and has valid GLB header
  - contains at least one mesh with primitives
  - is skinned (has JOINTS_0/WEIGHTS_0) or explicitly static-ok
  - materials have usable color data (baseColorTexture -> valid image,
    baseColorFactor, or COLOR_0 vertex colors)
  - embedded images are non-zero size

Output: game/data/model-readiness.json
  { "<fighter-id>": { "status": "ready|broken|missing",
                      "model": "<model-key>", "glb": "<path>",
                      "issues": [...] } }

Status meanings:
  ready   — model loads, renders with textures
  broken  — file exists but has problems (untextured, unskinned when
            skinning expected, corrupt)
  missing — file not found or no MODEL_URLS key

Usage:
  python3 tools/model-validate/validate_select_models.py [--roster PATH]
  [--out PATH] [--repo-root PATH]

Requires: tools/rig-repair/_common.py on sys.path (for Glb parsing).
"""
import sys, os, json, re, struct

REPO = os.environ.get('WH_REPO', os.path.expanduser('~/workspace/select-card-fix'))
sys.path.insert(0, os.path.join(REPO, 'tools', 'rig-repair'))
from _common import Glb


def load_roster(repo):
    src = open(os.path.join(repo, 'game/js/roster-full.js')).read()
    return re.findall(r"\{\s*id:\s*'([^']+)'.*?model:\s*'([^']+)'", src, re.DOTALL)


def load_ladders(repo):
    src = open(os.path.join(repo, 'game/js/attires.js')).read()
    m = re.search(r'export const ATTIRE_VARIANTS = \{(.*?)\n\};', src, re.DOTALL)
    blocks = re.split(r"(?m)^\s*['\"]([^'\"]+)['\"]\s*:\s*\[", m.group(1))
    ladders = {}
    for i in range(1, len(blocks), 2):
        fm = re.search(r"\{\s*model:\s*['\"]([^'\"]+)['\"]", blocks[i+1])
        ladders[blocks[i]] = fm.group(1) if fm else None
    return ladders


def load_urls(repo):
    src = open(os.path.join(repo, 'game/js/assets.js')).read()
    m = re.search(r'export const MODEL_URLS = \{(.*?)\n\};', src, re.DOTALL)
    urls = {}
    for k, v in re.findall(r"['\"]?([\w\-\.]+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", m.group(1)):
        urls[k] = v
    return urls


def resolve_default(fid, model, ladders, fids):
    rides = model != fid and model in fids
    lst = ladders.get(fid) if rides else (ladders.get(model) or ladders.get(fid))
    return lst or model


def validate_glb(path):
    """Return (status, issues list)."""
    issues = []
    if not os.path.exists(path):
        return 'missing', ['file not found: ' + path]
    try:
        with open(path, 'rb') as f:
            magic = f.read(4)
        if magic != b'glTF':
            return 'broken', ['not a GLB file (bad magic)']
        g = Glb(path)
    except Exception as e:
        return 'broken', ['parse failed: %s' % e]

    j = g.g
    meshes = j.get('meshes', [])
    if not meshes:
        issues.append('no meshes')
    prims = sum(len(m.get('primitives', [])) for m in meshes)
    if prims == 0:
        issues.append('meshes have no primitives')

    # skinning check
    has_joints = any(
        'JOINTS_0' in (p.get('attributes') or {}) for m in meshes
        for p in m.get('primitives', []))
    has_weights = any(
        'WEIGHTS_0' in (p.get('attributes') or {}) for m in meshes
        for p in m.get('primitives', []))
    if not (has_joints and has_weights):
        issues.append('not skinned (no JOINTS_0/WEIGHTS_0)')

    # material / texture check
    materials = j.get('materials', [])
    images = j.get('images', [])
    textures = j.get('textures', [])
    if not materials and prims > 0:
        issues.append('no materials (will render untextured white)')
    else:
        for mi, mat in enumerate(materials):
            pbr = mat.get('pbrMetallicRoughness', {})
            bct = pbr.get('baseColorTexture', {})
            has_tex = bool(bct)
            has_factor = 'baseColorFactor' in pbr
            # check vertex colors on any primitive using this material
            has_vcolor = any(
                'COLOR_0' in (p.get('attributes') or {})
                for m in meshes for p in m.get('primitives', [])
                if p.get('material') == mi)
            if not (has_tex or has_factor or has_vcolor):
                issues.append('material %d has no color source' % mi)
            if has_tex:
                ti = bct.get('index')
                if ti is None or ti >= len(textures):
                    issues.append('material %d bad texture index' % mi)
                else:
                    ii = textures[ti].get('source')
                    if ii is None or ii >= len(images):
                        issues.append('material %d bad image index' % mi)
    # image payload check (embedded only; external URIs skipped)
    for ii, img in enumerate(images):
        bv = img.get('bufferView')
        if bv is not None:
            try:
                data = g.views[bv]
                if len(data) == 0:
                    issues.append('image %d zero-byte' % ii)
            except Exception:
                issues.append('image %d unreadable' % ii)

    if issues:
        return 'broken', issues
    return 'ready', []


def main():
    repo = REPO
    out = os.path.join(repo, 'game/data/model-readiness.json')
    entries = load_roster(repo)
    ladders = load_ladders(repo)
    urls = load_urls(repo)
    fids = set(e[0] for e in entries)

    # GLB paths in MODEL_URLS are relative to game/
    result = {}
    for fid, model in entries:
        eff = resolve_default(fid, model, ladders, fids)
        rel = urls.get(eff)
        if not rel:
            result[fid] = {'status': 'missing', 'model': eff,
                           'glb': None, 'issues': ['no MODEL_URLS key: ' + eff]}
            continue
        # '../roster/...' is relative to game/, 'assets/...' too
        full = os.path.normpath(os.path.join(repo, 'game', rel))
        status, issues = validate_glb(full)
        result[fid] = {'status': status, 'model': eff, 'glb': rel,
                       'issues': issues}

    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({'generated': 'validate_select_models.py',
               'fighters': result}, open(out, 'w'), indent=2)

    n_ready = sum(1 for v in result.values() if v['status'] == 'ready')
    n_broken = sum(1 for v in result.values() if v['status'] == 'broken')
    n_missing = sum(1 for v in result.values() if v['status'] == 'missing')
    print('ready=%d broken=%d missing=%d total=%d' % (
        n_ready, n_broken, n_missing, len(result)))
    for fid, v in sorted(result.items()):
        if v['status'] != 'ready':
            print('  %s: %s %s' % (fid, v['status'], v['issues'][:2]))
    sys.exit(1 if (n_broken or n_missing) else 0)


if __name__ == '__main__':
    main()
