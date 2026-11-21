"""Matched-camera likeness gate (plan section 6.1 method).
Usage: gate.py <subject.png> --ref identity|f003 --out <prefix>
Tracks subject with MediaPipe, similarity-aligns to the reference on the
anchor set, reports mean + per-region error (% of reference face width),
and writes <prefix>_deltas.json: per-warp-landmark delta in SUBJECT image
space (units of subject face width) for the Blender warp step.
Run with the EGL env (see run_mp.sh).
"""
import argparse, json, math, os
import numpy as np

BASE = '/home/hatch/workspace/_pilot2-v2-20261108'
ap = argparse.ArgumentParser()
ap.add_argument('subject')
ap.add_argument('--ref', default='identity')
ap.add_argument('--out', required=True)
args = ap.parse_args()

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
MODEL = '/home/hatch/workspace/video-study-build/models/face_landmarker.task'
opts = mp_vision.FaceLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=MODEL),
    running_mode=mp_vision.RunningMode.IMAGE, num_faces=1,
    output_face_blendshapes=True, output_facial_transformation_matrixes=True)
lm = mp_vision.FaceLandmarker.create_from_options(opts)
img = mp.Image.create_from_file(args.subject)
res = lm.detect(img)
assert res.face_landmarks, 'NO FACE in subject'
S = np.array([[p.x, p.y] for p in res.face_landmarks[0]])
bs = {c.category_name: round(c.score, 3) for c in res.face_blendshapes[0]} if res.face_blendshapes else {}

if args.ref == 'identity':
    ref = json.load(open(f'{BASE}/angel_identity.json'))
    A = np.array(ref['landmarks2d'])
    ANCH = [33, 263, 133, 362, 1]
    ref_fw = ref['face_w']
else:
    track = json.load(open(f'{BASE}/angel_track.json'))
    A = np.array(track['482_f003.png']['landmarks'])[:, :2]
    ANCH = [263, 362, 1, 2, 152]
    ref_fw = float(np.linalg.norm(A[234] - A[1]) + np.linalg.norm(A[263] - A[1])) / 1.0

OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
LIPS = [61,146,91,181,84,17,314,405,321,375,291,409,270,269,267,0,37,39,40,185,57,165,167,164,393,391,308,415,310,311,312,95,88,178,87,14,317,402,318,324]
LEYE = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]
REYE = [263,249,390,373,374,380,381,382,362,398,384,385,386,387,388,466]
LBROW = [70,63,105,66,107,55,65,52,53,46]
RBROW = [300,293,334,296,336,285,295,282,283,276]
NOSE = [1,2,4,5,6,94,98,168,195,197,240,274,278,344,440]
REGIONS = {'oval_jaw': OVAL, 'lips': LIPS, 'eye_L': LEYE, 'eye_R': REYE,
           'brow_L': LBROW, 'brow_R': RBROW, 'nose': NOSE}
WARP = sorted(set(OVAL + LIPS + LEYE + REYE + LBROW + RBROW + NOSE + [51, 281, 5, 195, 94, 234, 454]))

def sim_fit(src, dst):
    cs, cd = src.mean(0), dst.mean(0)
    X, Y = src - cs, dst - cd
    U, Sv, Vt = np.linalg.svd(X.T @ Y)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:
        Vt[-1] *= -1; R = Vt.T @ U.T
    s = Sv.sum() / (X ** 2).sum()
    t = cd - s * R @ cs
    return s, R, t

s, R, t = sim_fit(S[ANCH], A[ANCH])
S_al = (s * (R @ S.T).T) + t
err = np.linalg.norm(S_al - A, axis=1) / ref_fw * 100
subj_fw = float(np.linalg.norm(S[234] - S[454])) if args.ref == 'identity' else float(np.linalg.norm(S[234] - S[1]))
metrics = {'subject': args.subject, 'ref': args.ref, 'mean_err_pct': round(float(err.mean()), 2),
           'max_err_pct': round(float(err.max()), 2), 'blendshapes': bs,
           'regions': {k: round(float(err[idx].mean()), 2) for k, idx in REGIONS.items()}}
# deltas in subject image space: T^{-1}(A) - S, normalized by subject face width
A_in_subj = ((A - t) @ R) / s  # inverse similarity applied to reference points
deltas = {}
for i in WARP:
    d = (A_in_subj[i] - S[i]) / subj_fw
    deltas[str(i)] = [round(float(d[0]), 5), round(float(d[1]), 5)]
json.dump(metrics, open(f'{args.out}_metrics.json', 'w'), indent=1)
json.dump({'landmarks': S.tolist(), 'deltas': deltas, 'subj_face_w': subj_fw,
           'ref': args.ref}, open(f'{args.out}_deltas.json', 'w'))
print(json.dumps(metrics, indent=1))
