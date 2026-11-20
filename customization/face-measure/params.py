#!/usr/bin/env python3
"""Face-measure engine step 2: parametric face measurement (face-params/v1).

Input: track.py JSON (one subject, many frames).
Method (the upgrades over a single-frame ratio read):
  - neutral-expression gate from blendshapes, pose gate from the facial
    transformation matrix (yaw/pitch),
  - pitch correction of every vertical measurement (v1 threw verticals away),
  - multi-frame similarity (Procrustes) averaging in 3D landmark space,
  - all measurements expressed in inter-ocular (iris-centre) units + raw.
Output: params JSON conforming to face-params/v1 (see schema doc).
Usage: params.py TRACK.json OUT.json [--single IMAGE_KEY]
"""
import sys, json, math
import numpy as np

ANCHORS = [33, 263, 133, 362, 1, 10, 152]

def pose_angles(m):
    R = np.array(m)[:3, :3]
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, -R[1, 2]))))
    yaw = math.degrees(math.atan2(R[0, 2], R[2, 2]))
    return pitch, yaw

def gate(face):
    bs = face.get("blendshapes", {})
    smile = (bs.get("mouthSmileLeft", 0) + bs.get("mouthSmileRight", 0)) / 2
    if smile > 0.32: return False, "smile"
    if bs.get("jawOpen", 0) > 0.10: return False, "jawOpen"
    if bs.get("eyeBlinkLeft", 0) > 0.35 or bs.get("eyeBlinkRight", 0) > 0.35: return False, "blink"
    if "matrix" in face:
        p, y = pose_angles(face["matrix"])
        if abs(y) > 12: return False, "yaw"
        if p < -22 or p > 18: return False, "pitch"
    return True, "ok"

def to_px(face, w, h):
    lm = np.array(face["landmarks"], dtype=float)
    lm[:, 0] *= w; lm[:, 1] *= h; lm[:, 2] *= w
    return lm

def similarity_align(src, ref, idx):
    """Return src similarity-aligned (scale+rot+trans, 3D, no reflection) to ref on idx."""
    s, r = src[idx], ref[idx]
    sc, rc = s.mean(0), r.mean(0)
    S, R = s - sc, r - rc
    H = S.T @ R
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    Rot = Vt.T @ D @ U.T
    scale = (R * (S @ Rot.T)).sum() / (S * S).sum()
    return (src - sc) @ Rot.T * scale + rc

def measure(shape, pitch_deg):
    """shape: (478,3) aligned landmark set in px. Returns param dict (IOD units)."""
    pc = 1.0 / max(0.55, math.cos(math.radians(abs(pitch_deg))))  # pitch correction
    def d(a, b, vertical=False):
        va, vb = shape[a], shape[b]
        if vertical:
            dist = abs(va[1] - vb[1]) * pc
            return dist
        return float(np.linalg.norm(va[:2] - vb[:2]))
    def dz(a, ref):
        return float(shape[a][2] - ref)
    iod = d(468, 473)
    eye_plane_z = (shape[468][2] + shape[473][2]) / 2
    P = {}
    g = lambda v: round(v / iod, 4)
    P["global.face_width_cheek"] = g(d(234, 454))
    P["global.face_width_temple"] = g(d(127, 356))
    P["global.face_height"] = g(d(10, 152, vertical=True))
    P["global.forehead_height"] = g(d(10, 168, vertical=True))
    P["global.nose_length"] = g(d(168, 2, vertical=True))
    P["global.lower_face_height"] = g(d(2, 152, vertical=True))
    P["brows.brow_outer_span"] = g(d(70, 300))
    P["brows.brow_eye_gap"] = g((d(70, 159, vertical=True) + d(300, 386, vertical=True)) / 2)
    P["eyes.eye_width_r"] = g(d(33, 133))
    P["eyes.eye_width_l"] = g(d(362, 263))
    P["eyes.eye_gap_inner"] = g(d(133, 362))
    P["eyes.eye_fissure"] = g((d(159, 145, vertical=True) + d(386, 374, vertical=True)) / 2)
    P["nose.alar_width"] = g(d(49, 279))
    P["nose.tip_projection"] = g(dz(1, eye_plane_z))
    P["lips.mouth_width"] = g(d(61, 291))
    P["lips.upper_thickness"] = g(d(0, 13, vertical=True))
    P["lips.lower_thickness"] = g(d(14, 17, vertical=True))
    P["lips.philtrum"] = g(d(2, 0, vertical=True))
    P["jaw.jaw_width"] = g(d(172, 397))
    P["jaw.chin_width"] = g(d(148, 377))
    P["jaw.chin_height"] = g(d(17, 152, vertical=True))
    P["cheeks.cheek_prominence"] = g((dz(234, eye_plane_z) + dz(454, eye_plane_z)) / 2)
    P["cheeks.cheek_level"] = round(float((shape[93][1] - shape[168][1]) / max(1e-6, (shape[152][1] - shape[168][1]) * pc)), 4)
    return P, round(iod, 2)

def main():
    track = json.load(open(sys.argv[1]))
    out_path = sys.argv[2]
    single = None
    if "--single" in sys.argv:
        single = sys.argv[sys.argv.index("--single") + 1]
    faces = []
    used, skipped = [], {}
    for name, entry in track.items():
        if single and name != single: continue
        if not entry.get("faces"): continue
        f = entry["faces"][0]
        ok, why = gate(f) if not single else (True, "single")
        if not ok:
            skipped[name] = why; continue
        pitch = pose_angles(f["matrix"])[0] if "matrix" in f else 0.0
        faces.append((name, to_px(f, entry["w"], entry["h"]), pitch))
        used.append(name)
    if not faces:
        print("NO gated faces"); sys.exit(1)
    # two-round Procrustes mean
    ref = faces[0][1]
    for _ in range(2):
        aligned = [similarity_align(lm, ref, ANCHORS) for _, lm, _ in faces]
        ref = np.mean(aligned, axis=0)
    mean_pitch = float(np.mean([p for _, _, p in faces]))
    params, iod = measure(ref, mean_pitch)
    out = {
        "schema": "face-params/v1",
        "frames_used": used,
        "frames_skipped": skipped,
        "mean_pitch_deg": round(mean_pitch, 2),
        "iod_px": iod,
        "params": params,
        "mean_shape": [[round(float(v), 2) for v in p] for p in ref],
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print("frames used:", len(used), "skipped:", skipped)
    print(json.dumps(params, indent=1))
    print("wrote", out_path)

if __name__ == "__main__":
    main()
