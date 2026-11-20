#!/usr/bin/env python3
"""Stage 1 of the WH mocap pipeline: video -> body keypoints (wh-keypoints/1 JSON).

[WIRED] Runs on CPU (MediaPipe BlazePose). No GPU needed.

Extracts per-frame 2D/3D pose landmarks from reference footage (martial arts,
wrestling, fight choreography) and writes them in the canonical wh-keypoints/1
schema consumed by tools/mocap/keypoints_to_bvh.py.

Backends:
  - mediapipe (default, CPU): Google MediaPipe Pose, 33 landmarks. Lightweight,
    runs in real time on CPU. Depth (z) is relative, not metric.
  - dwpose [NEEDS GPU]: the same DWPose (yolox_l + dw-ll_ucoco_384 ONNX) that
    MimicMotion and UniAnimate use for pose guidance. See README.md for the
    GPU-machine setup; it writes the same wh-keypoints/1 schema so the
    downstream stages are backend-agnostic.

Output schema (wh-keypoints/1):
  {
    "format": "wh-keypoints/1", "backend": "mediapipe",
    "fps": 30.0, "width": 640, "height": 480,
    "joints": ["nose", "left_shoulder", ...],
    "frames": [
      {"t": 0.0, "detected": true,
       "pos": {"nose": [x, y, z], ...},        # x,y normalized 0..1 (y DOWN),
       "conf": {"nose": 0.99, ...}},           # z: MediaPipe relative depth
      {"t": 0.033, "detected": false, "pos": {}, "conf": {}},
      ...
    ]
  }

Tips for good captures: single performer, full body in frame, camera
roughly at chest height, subject facing the camera for strikes (the
converter maps camera-facing to +Z; see keypoints_to_bvh.py --z-sign).
Side views work for locomotion but depth is weakest there.
"""
import argparse
import json
import sys

# MediaPipe landmark index -> canonical joint name
MP_JOINTS = {
    0: 'nose',
    2: 'left_eye', 5: 'right_eye',
    7: 'left_ear', 8: 'right_ear',
    11: 'left_shoulder', 12: 'right_shoulder',
    13: 'left_elbow', 14: 'right_elbow',
    15: 'left_wrist', 16: 'right_wrist',
    17: 'left_pinky', 18: 'right_pinky',
    19: 'left_index', 20: 'right_index',
    21: 'left_thumb', 22: 'right_thumb',
    23: 'left_hip', 24: 'right_hip',
    25: 'left_knee', 26: 'right_knee',
    27: 'left_ankle', 28: 'right_ankle',
    29: 'left_heel', 30: 'right_heel',
    31: 'left_foot_index', 32: 'right_foot_index',
}
JOINT_ORDER = [MP_JOINTS[i] for i in sorted(MP_JOINTS)]


def extract(video_path, out_path, stride=1, max_frames=0,
            min_detection_confidence=0.5, min_tracking_confidence=0.5):
    import cv2
    import mediapipe as mp

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f'cannot open video: {video_path}')
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = src_fps / stride

    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
    frames = []
    idx = 0
    kept = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % stride == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose.process(rgb)
                t = (idx / src_fps)
                if res.pose_landmarks:
                    pos, conf = {}, {}
                    for li, name in MP_JOINTS.items():
                        lm = res.pose_landmarks.landmark[li]
                        pos[name] = [lm.x, lm.y, lm.z]
                        conf[name] = float(lm.visibility)
                    frames.append({'t': round(t, 4), 'detected': True,
                                   'pos': pos, 'conf': conf})
                else:
                    frames.append({'t': round(t, 4), 'detected': False,
                                   'pos': {}, 'conf': {}})
                kept += 1
                if max_frames and kept >= max_frames:
                    break
            idx += 1
    finally:
        pose.close()
        cap.release()

    data = {
        'format': 'wh-keypoints/1',
        'backend': 'mediapipe',
        'fps': round(fps, 3),
        'width': width,
        'height': height,
        'source_video': video_path,
        'joints': JOINT_ORDER,
        'frames': frames,
    }
    with open(out_path, 'w') as f:
        json.dump(data, f)
    detected = sum(1 for fr in frames if fr['detected'])
    print(f'wrote {out_path}: {len(frames)} frames @ {fps:.2f} fps, '
          f'{detected} with detection')
    if detected == 0:
        print('WARNING: no person detected in any frame. Check the footage '
              '(single performer, full body visible).', file=sys.stderr)
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description='video -> wh-keypoints/1 JSON [WIRED, CPU]')
    ap.add_argument('video', help='input video (mp4/mov/webm)')
    ap.add_argument('output', help='output .json path')
    ap.add_argument('--stride', type=int, default=1,
                    help='process every Nth frame (fps_out = fps_in / N)')
    ap.add_argument('--max-frames', type=int, default=0,
                    help='cap output frames (0 = no cap)')
    ap.add_argument('--min-detection-confidence', type=float, default=0.5)
    ap.add_argument('--min-tracking-confidence', type=float, default=0.5)
    a = ap.parse_args(argv)
    extract(a.video, a.output, stride=a.stride, max_frames=a.max_frames,
            min_detection_confidence=a.min_detection_confidence,
            min_tracking_confidence=a.min_tracking_confidence)


if __name__ == '__main__':
    main()
