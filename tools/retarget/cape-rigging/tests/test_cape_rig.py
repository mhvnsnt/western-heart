"""Tests for tools/retarget/cape-rigging/cape_rig.py — synthetic rig only.

No Cape Jones .blend, mesh, BVH or GLB is used: the test rig is built
in code (a T-pose capsule cloud + a joint dict in CJ space), so the
tests run in CI with stdlib only. Tolerances are in metres.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cape_rig  # noqa: E402


def capsule_cloud(a, b, radius, n_len=14, n_ring=10):
    """Points on a capsule segment a-b (plus end caps), CJ space."""
    axis = cape_rig.vnorm(cape_rig.vsub(b, a))
    ref = [0, 0, 1] if abs(axis[2]) < 0.9 else [1, 0, 0]
    u = cape_rig.vnorm(cape_rig.vcross(axis, ref))
    w = cape_rig.vcross(axis, u)
    pts = []
    for i in range(n_len + 1):
        t = i / n_len
        centre = cape_rig.vadd(a, cape_rig.vscale(cape_rig.vsub(b, a), t))
        r = radius
        # Taper at the very ends so slices stay clustered.
        if i in (0, n_len):
            r = radius * 0.8
        for k in range(n_ring):
            ang = 2 * math.pi * k / n_ring
            off = cape_rig.vadd(cape_rig.vscale(u, math.cos(ang) * r),
                                cape_rig.vscale(w, math.sin(ang) * r))
            pts.append(cape_rig.vadd(centre, off))
    return pts


def synthetic_tpose():
    """CJ-space T-pose cloud, height ~0.925 m, L=+X, feet at z=0.

    Segment radii follow joint_detect's assumptions: thigh thick,
    knee thin, calf medium, ankle thin; arms horizontal at shoulder
    height with a thinner elbow/wrist region.
    """
    pts = []
    # Legs: hip (0.50) -> knee (0.27) -> ankle (0.07), per side.
    for s in (1, -1):
        x = 0.09 * s
        pts += capsule_cloud([x, 0, 0.50], [x, 0, 0.28], 0.055)
        pts += capsule_cloud([x, 0, 0.28], [x, 0, 0.26], 0.032)  # knee pinch
        pts += capsule_cloud([x, 0, 0.26], [x, 0, 0.08], 0.045)
        pts += capsule_cloud([x, 0, 0.08], [x, 0, 0.06], 0.030)  # ankle pinch
        pts += capsule_cloud([x, -0.02, 0.03], [x, -0.10, 0.03], 0.030)  # foot
    # Torso column + head sphere.
    pts += capsule_cloud([0, 0, 0.50], [0, 0, 0.80], 0.11)
    for i in range(12):
        for k in range(10):
            th = math.pi * i / 11
            ph = 2 * math.pi * k / 10
            pts.append([0.07 * math.sin(th) * math.cos(ph),
                        -0.01 + 0.07 * math.sin(th) * math.sin(ph),
                        0.86 + 0.07 * math.cos(th)])
    # Arms: shoulder x=0.14 -> elbow 0.32 -> wrist 0.48, at z=0.74.
    for s in (1, -1):
        pts += capsule_cloud([0.14 * s, 0, 0.74], [0.32 * s, 0, 0.74], 0.045)
        pts += capsule_cloud([0.32 * s, 0, 0.74], [0.34 * s, 0, 0.74], 0.028)
        pts += capsule_cloud([0.34 * s, 0, 0.74], [0.47 * s, 0, 0.74], 0.038)
        pts += capsule_cloud([0.47 * s, 0, 0.74], [0.49 * s, 0, 0.74], 0.030)
    return pts


JOINTS = {
    "hip_z": 0.535, "waist_z": 0.60, "chest_z": 0.68, "neck_z": 0.80,
    "chin_z": 0.83, "head_top": [0, -0.01, 0.925], "face_y": -0.08,
    "shoulder_L": [0.16, 0, 0.74], "elbow_L": [0.33, 0, 0.74],
    "wrist_L": [0.48, 0, 0.74], "fingertip_L": [0.56, 0, 0.74],
    "hip_L": [0.09, 0, 0.535], "knee_L": [0.09, 0, 0.27],
    "ankle_L": [0.09, 0, 0.07], "toe_L": [0.09, -0.10, 0.03],
    "heel_L": [0.09, 0.02, 0.03],
    "shoulder_R": [-0.16, 0, 0.74], "elbow_R": [-0.33, 0, 0.74],
    "wrist_R": [-0.48, 0, 0.74], "fingertip_R": [-0.56, 0, 0.74],
    "hip_R": [-0.09, 0, 0.535], "knee_R": [-0.09, 0, 0.27],
    "ankle_R": [-0.09, 0, 0.07], "toe_R": [-0.09, -0.10, 0.03],
    "heel_R": [-0.09, 0.02, 0.03],
    "finger_dir_L": [1, 0, 0], "palm_L": [0.50, 0, 0.74], "finger_len_L": 0.05,
    "thumb_L": [0.50, -0.03, 0.72],
    "finger_dir_R": [-1, 0, 0], "palm_R": [-0.50, 0, 0.74], "finger_len_R": 0.05,
    "thumb_R": [-0.50, -0.03, 0.72],
}


class TestFit(unittest.TestCase):
    def test_guides_cover_torso_and_limbs(self):
        guides = cape_rig.fit_guides(JOINTS)
        for g in ("master_torso_str", "spine_ctrl_2_str", "head_str",
                  "shoulder_str_L", "elbow_str_L", "knee_str_R", "ankle_str_L"):
            self.assertIn(g, guides)
        # Finger guides: 4 fingers x 5 + thumb x 4, per side.
        fing = [g for g in guides if g.startswith("fing_")]
        self.assertEqual(len(fing), 48)

    def test_no_cj_scale_by_default(self):
        guides = cape_rig.fit_guides(JOINTS)
        head, tail = guides["shoulder_str_L"]
        self.assertAlmostEqual(head[0], 0.16, places=6)
        self.assertAlmostEqual(tail[0], 0.33, places=6)

    def test_cj_scale_is_opt_in(self):
        guides = cape_rig.fit_guides(JOINTS, rest_scale=0.544)
        head, _ = guides["shoulder_str_L"]
        self.assertAlmostEqual(head[0], 0.16 * 0.544, places=6)

    def test_warp_records_nearest_guide(self):
        guides = cape_rig.fit_guides(JOINTS)
        warped = cape_rig.warp_bones(guides, {"spine_1_def": ([0, 0, 0.60], [0, 0, 0.68])})
        self.assertIn(warped["spine_1_def"]["nearest_guide"], guides)
        self.assertLess(warped["spine_1_def"]["nearest_guide_dist"], 0.05)

    def test_wh_space_conversion(self):
        # CJ up +Z, facing -Y -> WH up +Y, facing +Z.
        self.assertEqual(cape_rig.to_wh_space([0.1, -0.2, 0.9]), [0.1, 0.9, 0.2])


class TestDetect(unittest.TestCase):
    def test_detect_recovers_test_rig_joints(self):
        joints = cape_rig.detect_joints(synthetic_tpose())
        for key in ("hip_L", "knee_L", "ankle_L", "hip_R", "knee_R"):
            self.assertIn(key, joints, key)
        self.assertAlmostEqual(joints["knee_L"][2], 0.27, delta=0.04)
        self.assertAlmostEqual(joints["ankle_L"][2], 0.07, delta=0.04)
        self.assertAlmostEqual(joints["hip_L"][0], 0.09, delta=0.03)
        self.assertGreater(joints["chest_z"], joints["waist_z"])
        self.assertGreater(joints["waist_z"], joints["hip_z"])


class TestCage(unittest.TestCase):
    def test_weights_sum_to_one_and_locked_is_rigid(self):
        segs = {
            "head": ([0, 0, 0.80], [0, 0, 0.925]),
            "chest": ([0, 0, 0.60], [0, 0, 0.68]),
            "thigh_L": ([0.09, 0, 0.535], [0.09, 0, 0.27]),
            "shin_L": ([0.09, 0, 0.27], [0.09, 0, 0.07]),
        }
        cage = cape_rig.build_cage(segs, ring=8)
        self.assertEqual(len(cage), 4 * 3 * 8)
        weights = cape_rig.compute_weights(cage, segs)
        worst, n, bad = cape_rig.verify_weights(weights)
        self.assertEqual(bad, 0)
        self.assertLess(worst, 1e-6)
        # A vert on the head segment must be locked to head = 1.0.
        head_vert = cage[0]
        self.assertEqual(weights["head"][0], 1.0)

    def test_cage_fit_moves_bbox_centre(self):
        cage = [[-1, -1, -1], [1, 1, 1]]
        fitted = cape_rig.fit_cage_to_bbox(
            cage, ([-1, -1, -1], [1, 1, 1]), ([0, 0, 0], [0.4, 1.8, 0.4]))
        self.assertAlmostEqual(fitted[0][0], 0.0, places=6)
        self.assertAlmostEqual(fitted[1][1], 1.8, places=6)


if __name__ == "__main__":
    unittest.main()
