#!/usr/bin/env python3
"""Face-weight guard: fail a PR that adds/modifies a rigged GLB whose face-region
vertices carry >5% skin weight on spine/pelvis/hips/root (or other non-head)
bones.

The loss this prevents: the "face cone" bug (2026-10-23) — jaw/chin/face verts
weighted to Spine/Pelvis/Hips instead of Head, so the face stretches toward the
spine whenever the body moves. Universal fix landed in the same PR that added
this guard; this guard makes sure it can never come back.

Algorithm (pure function `check_face_weights`, unit-tested in
test_face_weight_guard.py):
  face region = verts in the top 15% of model height (Y-up)
  bad bones   = joint names matching spine/pelvis/hip/root/waist/torso/chest/
                thigh/knee/foot/leg/clavicle/shoulder/arm/forearm/hand/...
  violating   = any face vert with total bad-bone weight > 0.05

CI usage (see .github/workflows/game-checks.yml, face-weight-guard job):
    python3 tools/rig-guard/face_weight_guard.py   # scans PR-changed .glb files
Local usage:
    python3 tools/rig-guard/face_weight_guard.py path/to/model.glb [...]
"""
import json
import os
import struct
import subprocess
import sys

BAD_PATTERNS = ('spine', 'pelvis', 'hip', 'root', 'waist', 'torso', 'chest',
                'thigh', 'knee', 'foot', 'leg', 'clavicle', 'shoulder',
                'arm', 'forearm', 'hand', 'elbow', 'wrist', 'finger', 'thumb')
HEAD_PATTERNS = ('head', 'neck')
THRESHOLD = 0.05
FACE_FRAC = 0.15


def classify_joint(name):
    ln = (name or '').lower()
    for p in HEAD_PATTERNS:
        if p in ln:
            return 'head'
    for p in BAD_PATTERNS:
        if p in ln:
            return 'bad'
    return 'other'


def read_glb_chunks(path):
    with open(path, 'rb') as f:
        data = f.read()
    magic, _, _ = struct.unpack('<III', data[:12])
    if magic != 0x46546C67:
        raise ValueError(f'{path}: not a GLB')
    off, js, bindata = 12, None, b''
    while off < len(data):
        clen, ctype = struct.unpack('<II', data[off:off + 8])
        cdata = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(cdata.decode('utf-8').rstrip(' \x00'))
        elif ctype == 0x004E4942:
            bindata = cdata
        off += 8 + clen
    return js, bindata


def decode_buffer_view(js, bv_idx, bin_buf):
    """Return raw bytes of a bufferView, handling EXT_meshopt_compression."""
    bv = js['bufferViews'][bv_idx]
    ext = (bv.get('extensions') or {}).get('EXT_meshopt_compression')
    if ext is not None:
        import meshopt
        coff = ext.get('byteOffset') or 0
        comp = bytes(bin_buf[coff:coff + ext['byteLength']])
        arr = meshopt.decode_gltf_buffer(comp, ext['count'], ext['byteStride'],
                                         ext['mode'], ext.get('filter', 'NONE'))
        return arr.tobytes()
    off = bv.get('byteOffset') or 0
    return bytes(bin_buf[off:off + bv['byteLength']])


def read_accessor(js, bin_buf, acc_idx, normalize=False):
    import numpy as np
    acc = js['accessors'][acc_idx]
    data = decode_buffer_view(js, acc['bufferView'], bin_buf)
    bv = js['bufferViews'][acc['bufferView']]
    fmt = {5121: 'B', 5123: 'H', 5126: 'f'}[acc['componentType']]
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4,
             'MAT4': 16}[acc['type']]
    esz = {'B': 1, 'H': 2, 'f': 4}[fmt]
    stride = bv.get('byteStride') or ncomp * esz
    aoff = acc.get('byteOffset') or 0
    dt = np.dtype('<' + ('u1' if fmt == 'B' else 'u2' if fmt == 'H' else 'f4'))
    arr = np.zeros((acc['count'], ncomp))
    raw = np.frombuffer(data, dtype=np.uint8)
    for i in range(acc['count']):
        s = aoff + i * stride
        arr[i] = np.frombuffer(raw[s:s + ncomp * esz].tobytes(), dtype=dt)
    if normalize:
        if fmt == 'B':
            arr /= 255.0
        elif fmt == 'H':
            arr /= 65535.0
    return arr


def check_face_weights(path, threshold=THRESHOLD, face_frac=FACE_FRAC):
    """Return list of violating verts; empty list = pass. Raises on unreadable."""
    import numpy as np
    js, bindata = read_glb_chunks(path)
    bin_buf = bytearray(bindata)
    skins = js.get('skins') or []
    if not skins:
        return []  # unskinned: nothing to check
    joint_names = [js['nodes'][j].get('name') or f'joint_{j}'
                   for j in skins[0]['joints']]
    bad_joints = {i for i, n in enumerate(joint_names)
                  if classify_joint(n) == 'bad'}
    if not bad_joints:
        return []
    bad = []
    for mesh in js.get('meshes', []):
        for prim in mesh['primitives']:
            attrs = prim['attributes']
            if 'JOINTS_0' not in attrs or 'WEIGHTS_0' not in attrs:
                continue
            pos = read_accessor(js, bin_buf, attrs['POSITION'])
            joints = read_accessor(js, bin_buf, attrs['JOINTS_0']).astype(int)
            weights = read_accessor(js, bin_buf, attrs['WEIGHTS_0'],
                                    normalize=True)
            ymin, ymax = pos[:, 1].min(), pos[:, 1].max()
            if ymax == ymin:
                continue
            fidx = np.where(pos[:, 1] >= ymax - face_frac * (ymax - ymin))[0]
            for vi in fidx:
                bw = 0.0
                detail = []
                for k in range(4):
                    ji, w = int(joints[vi, k]), float(weights[vi, k])
                    if w > 0 and ji in bad_joints:
                        bw += w
                        detail.append((joint_names[ji], round(w, 3)))
                if bw > threshold:
                    bad.append({'vert': int(vi), 'bad_weight': round(bw, 3),
                                'bones': detail})
                    if len(bad) >= 50:  # cap detail; we only need fail/pass
                        return bad
    return bad


def pr_changed_glbs():
    """GLB files added or modified in this PR (empty list if not in CI)."""
    base = os.environ.get('BASE_SHA', '')
    head = os.environ.get('HEAD_SHA', '')
    if not base or not head:
        return []
    p = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=AM',
                        f'{base}...{head}'], capture_output=True, text=True)
    return [l.strip() for l in p.stdout.splitlines()
            if l.strip().lower().endswith('.glb')]


def main():
    targets = sys.argv[1:] or pr_changed_glbs()
    if not targets:
        print('face_weight_guard: no GLB targets (not a PR run?) — pass')
        return 0
    try:
        import numpy  # noqa
    except ImportError:
        print('face_weight_guard: numpy missing; pip install numpy', file=sys.stderr)
        return 2
    try:
        import meshopt  # noqa
    except ImportError:
        print('face_weight_guard: meshopt missing; pip install meshopt',
              file=sys.stderr)
        return 2
    failures = {}
    for path in targets:
        if not os.path.exists(path):
            print(f'  skip (missing): {path}')
            continue
        try:
            bad = check_face_weights(path)
        except Exception as exc:
            print(f'  ERROR scanning {path}: {exc}', file=sys.stderr)
            return 2
        if bad:
            failures[path] = bad
            print(f'  FAIL {path}: {len(bad)}+ face verts >{THRESHOLD} on '
                  f'{sorted({b for v in bad for b, _ in v["bones"]})}')
        else:
            print(f'  pass {path}')
    if failures:
        print(f'\nface_weight_guard FAIL: {len(failures)} GLB(s) with face verts '
              f'weighted to spine/pelvis/root bones.')
        print('Fix: reassign those weights to the Head/Neck bone (see '
              'tools/rig-guard/README.md).')
        return 1
    print(f'face_weight_guard PASS: {len(targets)} GLB(s) clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
