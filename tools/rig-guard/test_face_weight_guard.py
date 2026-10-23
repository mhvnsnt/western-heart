#!/usr/bin/env python3
"""Unit tests for face_weight_guard.check_face_weights (pure logic + I/O)."""
import io
import json
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from face_weight_guard import check_face_weights, classify_joint

import numpy as np


def make_glb(path, joint_names, vert_data):
    """Build a minimal GLB with one skinned mesh.

    vert_data: list of (y, [(joint_idx, weight), ...]) tuples.
    """
    n = len(vert_data)
    pos = np.zeros((n, 3), dtype='<f4')
    joints = np.zeros((n, 4), dtype='<u2')
    weights = np.zeros((n, 4), dtype='<f4')
    for i, (y, jw) in enumerate(vert_data):
        pos[i] = (0.0, y, 0.0)
        for k, (ji, w) in enumerate(jw[:4]):
            joints[i, k] = ji
            weights[i, k] = w
    blob = pos.tobytes() + joints.tobytes() + weights.tobytes()
    js = {
        'asset': {'version': '2.0'},
        'nodes': [{'name': nm, 'children': []} for nm in joint_names],
        'skins': [{
            'joints': list(range(len(joint_names))),
            'inverseBindMatrices': 3,
        }],
        'meshes': [{
            'primitives': [{
                'attributes': {'POSITION': 0, 'JOINTS_0': 1, 'WEIGHTS_0': 2},
            }],
        }],
        'accessors': [
            {'bufferView': 0, 'componentType': 5126, 'type': 'VEC3',
             'count': n},
            {'bufferView': 1, 'componentType': 5123, 'type': 'VEC4',
             'count': n},
            {'bufferView': 2, 'componentType': 5126, 'type': 'VEC4',
             'count': n},
            {'bufferView': 3, 'componentType': 5126, 'type': 'MAT4',
             'count': len(joint_names)},
        ],
        'bufferViews': [
            {'buffer': 0, 'byteOffset': 0, 'byteLength': pos.nbytes},
            {'buffer': 0, 'byteOffset': pos.nbytes,
             'byteLength': joints.nbytes},
            {'buffer': 0, 'byteOffset': pos.nbytes + joints.nbytes,
             'byteLength': weights.nbytes},
            {'buffer': 0, 'byteOffset': pos.nbytes + joints.nbytes + weights.nbytes,
             'byteLength': len(joint_names) * 64},
        ],
        'buffers': [{'byteLength': len(blob) + len(joint_names) * 64}],
    }
    blob += np.eye(4, dtype='<f4').tobytes() * 0 + b''.join(
        np.eye(4, dtype='<f4').tobytes() for _ in joint_names)
    js_bytes = json.dumps(js).encode()
    js_p = js_bytes + b' ' * ((4 - len(js_bytes) % 4) % 4)
    bin_p = blob + b'\x00' * ((4 - len(blob) % 4) % 4)
    total = 12 + 8 + len(js_p) + 8 + len(bin_p)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js_p), 0x4E4F534A) + js_p)
        f.write(struct.pack('<II', len(bin_p), 0x004E4942) + bin_p)


class TestClassify(unittest.TestCase):
    def test_head(self):
        self.assertEqual(classify_joint('Head'), 'head')
        self.assertEqual(classify_joint('Neck'), 'head')

    def test_bad(self):
        for n in ['Spine', 'Spine1', 'Pelvis', 'Hips', 'Root', 'LeftArm',
                  'RightHand', 'LeftUpLeg']:
            self.assertEqual(classify_joint(n), 'bad', n)

    def test_other(self):
        self.assertEqual(classify_joint('Chest'), 'bad')  # chest is bad
        self.assertEqual(classify_joint('Prop'), 'other')


class TestCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def glb(self, name, joints, verts):
        p = os.path.join(self.tmp, name)
        make_glb(p, joints, verts)
        return p

    def test_clean_passes(self):
        # face verts (y=1.9, top 15% of 0..2) all on Head
        p = self.glb('clean.glb', ['Hips', 'Spine', 'Head'],
                     [(1.9, [(2, 1.0)]), (1.95, [(2, 0.97), (1, 0.03)]),
                      (0.5, [(0, 1.0)])])
        self.assertEqual(check_face_weights(p), [])

    def test_spine_face_fails(self):
        p = self.glb('bad.glb', ['Hips', 'Spine', 'Head'],
                     [(1.9, [(1, 0.3), (2, 0.7)]),   # 30% spine -> fail
                      (0.5, [(1, 1.0)])])             # body spine: fine
        bad = check_face_weights(p)
        self.assertEqual(len(bad), 1)
        self.assertEqual(bad[0]['bones'][0][0], 'Spine')

    def test_below_threshold_passes(self):
        p = self.glb('edge.glb', ['Hips', 'Spine', 'Head'],
                     [(1.9, [(1, 0.04), (2, 0.96)])])  # 4% < 5% -> pass
        self.assertEqual(check_face_weights(p), [])

    def test_unskinned_passes(self):
        p = os.path.join(self.tmp, 'noskin.glb')
        # minimal GLB with no skins
        js = {'asset': {'version': '2.0'}, 'meshes': [],
              'accessors': [], 'bufferViews': [],
              'buffers': [{'byteLength': 0}]}
        js_b = json.dumps(js).encode()
        js_p = js_b + b' ' * ((4 - len(js_b) % 4) % 4)
        total = 12 + 8 + len(js_p) + 8
        with open(p, 'wb') as f:
            f.write(struct.pack('<III', 0x46546C67, 2, total))
            f.write(struct.pack('<II', len(js_p), 0x4E4F534A) + js_p)
            f.write(struct.pack('<II', 0, 0x004E4942))
        self.assertEqual(check_face_weights(p), [])


if __name__ == '__main__':
    unittest.main()
