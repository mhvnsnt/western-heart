# MediaPipe Mocap Pipeline — 2026-10-23

**User directive (verbatim):** *"OpenPose / MediaPipe — Mocap from video footage. This is HUGE: convert martial arts/combat footage into .bvh motion capture data."*

## 1. Status: WORKING on CPU

The pipeline is installed and verified at `~/workspace/tools/mocap/`:
- `venv/` — Python 3.12 venv with mediapipe 1.1.1, opencv, numpy
- `models/pose_landmarker.task` — 30MB pose model (heavy variant, float16)
- `syslibs/` — bundled libGL/libGLESv2 (extracted from Ubuntu debs, no sudo needed)
- `video_to_bvh.py` — video → BVH converter (tested, valid output)

**Verified:** PoseLandmarker loads and runs on CPU via XNNPACK delegate. BVH writer produces valid output (HIERARCHY + MOTION, 15 joints, correct frame timing).

## 2. Pipeline

```
video.mp4 → MediaPipe PoseLandmarker (33 landmarks/frame, world coords)
         → NaN interpolation (missed detections)
         → video_to_bvh.py → .bvh (Blender / game-engine importable)
```

Usage:
```bash
cd ~/workspace/tools/mocap
./venv/bin/python video_to_bvh.py input.mp4 output.bvh --every-nth 2
```

## 3. MediaPipe → Tekken Skeleton Mapping

MediaPipe outputs 33 landmarks. Our Tekken skeleton has 53 joints. Mapping:

| BVH Joint    | MP Landmark(s) | Tekken Equivalent       | Notes                    |
|--------------|----------------|-------------------------|--------------------------|
| Hips         | 23+24 (avg)    | Hips                    | Root, 6-channel          |
| Spine        | 11+12 (avg)    | Spine1                  |                          |
| Head         | 0              | Head                    | Nose proxy               |
| Shoulder.L/R | 11 / 12        | Shoulder_L/R            |                          |
| Elbow.L/R    | 13 / 14        | Elbow_L/R               |                          |
| Wrist.L/R    | 15 / 16        | Wrist_L/R               | No finger data           |
| Hip.L/R      | 23 / 24        | Hip_L/R                 |                          |
| Knee.L/R     | 25 / 26        | Knee_L/R                |                          |
| Ankle.L/R    | 27 / 28        | Ankle_L/R               | No toe data              |

**Gaps (not captured by MediaPipe Pose):**
- Fingers/hands (use MediaPipe Hands as separate pass if needed)
- Toes/feet detail
- Facial expression (use FaceMesh separately)
- Twist/roll rotation (positions only — rotations are zeroed in current BVH; a follow-up should compute joint orientations from bone vectors)

## 4. Limitations & Next Steps

1. **Rotations:** Current BVH has zeroed rotations (positions drive the root only). For game-ready animations, compute per-joint quaternion rotations from parent→child bone vectors.
2. **Occlusion:** Martial arts footage with fast motion will drop frames — the interpolator handles gaps but quality degrades.
3. **Single person:** PoseLandmarker detects multiple people; the script takes the first. For sparring footage, track IDs across frames.
4. **Scale:** World landmarks are metric but noisy — consider a calibration step using a known-height reference.

## 5. License

MediaPipe: Apache 2.0. Clean for commercial use.
