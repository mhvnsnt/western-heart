#!/usr/bin/env python3
"""
video_to_bvh.py — MediaPipe pose estimation → BVH motion capture.

Usage:
    video_to_bvh.py input.mp4 output.bvh [--max-frames N] [--every-nth N]

Pipeline: video frames → MediaPipe PoseLandmarker (33 landmarks) →
mapped to BVH hierarchy → .bvh file importable by Blender/game engines.

Mapping: MediaPipe's 33 landmarks → simplified humanoid BVH skeleton.
The full 53-joint Tekken skeleton mapping is documented in
docs/research/MOCAP-PIPELINE-2026-10-23.md (gaps noted).
"""
import os
import sys
import argparse
import math
import numpy as np

# Ensure bundled syslibs are findable
_SYSLIBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'syslibs', 'usr', 'lib', 'x86_64-linux-gnu')
if os.path.isdir(_SYSLIBS):
    os.environ['LD_LIBRARY_PATH'] = _SYSLIBS + ':' + os.environ.get('LD_LIBRARY_PATH', '')

# ---------------------------------------------------------------------------
# MediaPipe → BVH joint mapping
# MediaPipe PoseLandmarker outputs 33 landmarks. We build a BVH hierarchy
# from the most stable subset.
# ---------------------------------------------------------------------------
# (mp_index, bvh_name, parent_bvh_name)
JOINT_MAP = [
    (0,  'Hips',        None),        # nose → use as head proxy for root calc
    (11, 'Spine',       'Hips'),      # left shoulder
    (12, 'Spine',       'Hips'),      # right shoulder (averaged)
    (0,  'Head',        'Spine'),     # nose
    (11, 'Shoulder.L',  'Spine'),
    (13, 'Elbow.L',     'Shoulder.L'),
    (15, 'Wrist.L',     'Elbow.L'),
    (12, 'Shoulder.R',  'Spine'),
    (14, 'Elbow.R',     'Shoulder.R'),
    (16, 'Wrist.R',     'Elbow.R'),
    (23, 'Hip.L',       'Hips'),
    (25, 'Knee.L',      'Hip.L'),
    (27, 'Ankle.L',     'Knee.L'),
    (24, 'Hip.R',       'Hips'),
    (26, 'Knee.R',      'Hip.R'),
    (28, 'Ankle.R',     'Knee.R'),
]

# Deduplicated hierarchy for BVH (in order)
BVH_HIERARCHY = [
    ('Hips',       None),
    ('Spine',      'Hips'),
    ('Head',       'Spine'),
    ('Shoulder.L', 'Spine'),
    ('Elbow.L',    'Shoulder.L'),
    ('Wrist.L',    'Elbow.L'),
    ('Shoulder.R', 'Spine'),
    ('Elbow.R',    'Shoulder.R'),
    ('Wrist.R',    'Elbow.R'),
    ('Hip.L',      'Hips'),
    ('Knee.L',     'Hip.L'),
    ('Ankle.L',    'Knee.L'),
    ('Hip.R',      'Hips'),
    ('Knee.R',     'Hip.R'),
    ('Ankle.R',    'Knee.R'),
]

# MediaPipe landmark index per BVH joint (averaged where listed as tuple)
BVH_MP_INDEX = {
    'Hips':       (23, 24),
    'Spine':      (11, 12),
    'Head':       (0,),
    'Shoulder.L': (11,),
    'Elbow.L':    (13,),
    'Wrist.L':    (15,),
    'Shoulder.R': (12,),
    'Elbow.R':    (14,),
    'Wrist.R':    (16,),
    'Hip.L':      (23,),
    'Knee.L':     (25,),
    'Ankle.L':    (27,),
    'Hip.R':      (24,),
    'Knee.R':     (26,),
    'Ankle.R':    (28,),
}


def extract_poses(video_path, model_path, max_frames=0, every_nth=1):
    """Run MediaPipe PoseLandmarker over video frames. Returns list of (33,3) arrays."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions

    try:
        import cv2
    except ImportError:
        print("ERROR: opencv required for video input. Install opencv-python.", file=sys.stderr)
        sys.exit(1)

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
    )
    landmarker = PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    idx = 0
    while True:
        ret, frame_bgr = cap.read()
        if not ret:
            break
        if idx % every_nth != 0:
            idx += 1
            continue
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        ts_ms = int(idx / fps * 1000)
        result = landmarker.detect_for_video(mp_img, ts_ms)
        if result.pose_world_landmarks:
            lm = result.pose_world_landmarks[0]
            arr = np.array([[p.x, p.y, p.z] for p in lm], dtype=np.float64)
        else:
            arr = np.full((33, 3), np.nan)
        frames.append(arr)
        idx += 1
        if max_frames and len(frames) >= max_frames:
            break
    cap.release()
    landmarker.close()
    return frames, fps / every_nth


def interpolate_nans(frames):
    """Linear-interpolate NaN gaps (frames where no pose was detected)."""
    if not frames:
        return frames
    stacked = np.stack(frames)  # (F, 33, 3)
    F = stacked.shape[0]
    for j in range(33):
        for c in range(3):
            col = stacked[:, j, c]
            mask = np.isnan(col)
            if mask.all():
                col[:] = 0.0
            elif mask.any():
                x = np.arange(F)
                col[mask] = np.interp(x[mask], x[~mask], col[~mask])
    return [stacked[i] for i in range(F)]


def write_bvh(frames, fps, out_path):
    """Write BVH with Hips root (6ch) + 14 joints (3ch rotations as zero)."""
    n_joints = len(BVH_HIERARCHY)
    # Offsets: computed from first valid frame, in meters scaled to cm
    ref = frames[0]
    offsets = {}
    for name, parent in BVH_HIERARCHY:
        idxs = BVH_MP_INDEX[name]
        pos = np.mean([ref[i] for i in idxs], axis=0) * 100.0  # m → cm
        if parent is None:
            offsets[name] = pos
        else:
            pidxs = BVH_MP_INDEX[parent]
            ppos = np.mean([ref[i] for i in pidxs], axis=0) * 100.0
            offsets[name] = pos - ppos

    # Build hierarchy text (children map)
    children = {}
    for name, parent in BVH_HIERARCHY:
        children.setdefault(parent, []).append(name)

    lines = []
    lines.append("HIERARCHY")

    def emit(name, depth):
        ind = "  " * depth
        pname = children.get(name, [])
        is_root = depth == 0
        is_leaf = not pname
        tag = "ROOT" if is_root else ("End Site" if False else "JOINT")
        if is_leaf:
            lines.append(f"{ind}JOINT {name}")
        else:
            lines.append(f"{ind}{tag} {name}")
        lines.append(f"{ind}{{")
        o = offsets[name]
        lines.append(f"{ind}  OFFSET {o[0]:.4f} {o[1]:.4f} {o[2]:.4f}")
        if is_root:
            lines.append(f"{ind}  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")
        elif not is_leaf:
            lines.append(f"{ind}  CHANNELS 3 Zrotation Xrotation Yrotation")
        if is_leaf:
            lines.append(f"{ind}  End Site")
            lines.append(f"{ind}  {{")
            lines.append(f"{ind}    OFFSET 0.0 0.0 0.0")
            lines.append(f"{ind}  }}")
        else:
            for c in pname:
                emit(c, depth + 1)
        lines.append(f"{ind}}}")

    emit('Hips', 0)

    # Motion
    lines.append("MOTION")
    lines.append(f"Frames: {len(frames)}")
    lines.append(f"Frame Time: {1.0/fps:.6f}")
    for fr in frames:
        vals = []
        for name, parent in BVH_HIERARCHY:
            idxs = BVH_MP_INDEX[name]
            pos = np.mean([fr[i] for i in idxs], axis=0) * 100.0
            if name == 'Hips':
                # MediaPipe Y is up in world landmarks? world landmarks: y up, x right, z toward viewer
                vals += [f"{pos[0]:.4f}", f"{pos[1]:.4f}", f"{pos[2]:.4f}", "0.0000", "0.0000", "0.0000"]
            else:
                vals += ["0.0000", "0.0000", "0.0000"]
        lines.append(" ".join(vals))

    with open(out_path, 'w') as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {out_path}: {len(frames)} frames @ {fps:.1f}fps, {n_joints} joints")


def main():
    ap = argparse.ArgumentParser(description="Video → BVH via MediaPipe")
    ap.add_argument("input", help="Input video file")
    ap.add_argument("output", help="Output .bvh file")
    ap.add_argument("--max-frames", type=int, default=0)
    ap.add_argument("--every-nth", type=int, default=1)
    ap.add_argument("--model", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "models", "pose_landmarker.task"))
    args = ap.parse_args()

    print(f"Extracting poses from {args.input} ...")
    frames, fps = extract_poses(args.input, args.model, args.max_frames, args.every_nth)
    print(f"Got {len(frames)} frames, interpolating gaps ...")
    frames = interpolate_nans(frames)
    write_bvh(frames, fps, args.output)


if __name__ == "__main__":
    main()
