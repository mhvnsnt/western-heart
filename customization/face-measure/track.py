#!/usr/bin/env python3
"""Face-measure engine step 1: track images with MediaPipe Face Landmarker.
Apache-2.0 tool. Outputs per-image JSON: landmarks (478x3, image-normalized),
blendshapes, 4x4 facial transformation matrix, image size.
Usage: track.py OUT.json IMG [IMG ...]
"""
import sys, json, os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL = os.environ.get(
    "FACE_LANDMARKER_TASK",
    "/home/hatch/workspace/video-study-build/models/face_landmarker.task",
)

def main():
    out_path, imgs = sys.argv[1], sys.argv[2:]
    opts = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL),
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=4,
        min_face_detection_confidence=0.3,
        min_face_presence_confidence=0.3,
    )
    lm = vision.FaceLandmarker.create_from_options(opts)
    results = {}
    for p in imgs:
        try:
            img = mp.Image.create_from_file(p)
        except Exception as e:
            results[os.path.basename(p)] = {"image": p, "faces": [], "error": str(e)[:120]}
            print(p, "LOAD FAILED:", str(e)[:80], flush=True)
            continue
        r = lm.detect(img)
        entry = {"image": p, "w": img.width, "h": img.height, "faces": []}
        for i, face in enumerate(r.face_landmarks or []):
            f = {
                "landmarks": [[round(v.x, 5), round(v.y, 5), round(v.z, 5)] for v in face],
            }
            if r.face_blendshapes and i < len(r.face_blendshapes):
                f["blendshapes"] = {
                    c.category_name: round(c.score, 4) for c in r.face_blendshapes[i]
                }
            if r.facial_transformation_matrixes and i < len(r.facial_transformation_matrixes):
                m = r.facial_transformation_matrixes[i]
                f["matrix"] = [[round(float(m[row][col]), 5) for col in range(4)] for row in range(4)]
            entry["faces"].append(f)
        results[os.path.basename(p)] = entry
        print(p, "faces:", len(entry["faces"]), flush=True)
    with open(out_path, "w") as fh:
        json.dump(results, fh)
    print("wrote", out_path)

if __name__ == "__main__":
    main()
