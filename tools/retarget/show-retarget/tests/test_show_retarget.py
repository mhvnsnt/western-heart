"""Tests for tools/retarget/show-retarget/wh_show_retarget.py.

Synthetic poses only: no CMU BVH, no Cape Jones GLB, no real clip
bytes. Quats are (w, x, y, z). Tolerances are in quat components /
direction cosine, as noted per test.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import wh_show_retarget as wr  # noqa: E402

IDENT = (1.0, 0.0, 0.0, 0.0)

def qz(deg):
    a = math.radians(deg) / 2
    return (math.cos(a), 0.0, 0.0, math.sin(a))

PARENTS = {"Hips": None, "Spine": "Hips", "Chest": "Spine", "Neck": "Chest",
           "Head": "Neck", "LeftShoulder": "Chest", "LeftArm": "LeftShoulder",
           "LeftForeArm": "LeftArm", "LeftHand": "LeftForeArm",
           "LeftUpLeg": "Hips", "LeftLeg": "LeftUpLeg", "LeftFoot": "LeftLeg"}


class TestRetarget(unittest.TestCase):
    def test_rest_stays_rest(self):
        pose = {"Hips": IDENT, "LeftArm": IDENT, "Head": IDENT}
        out = wr.retarget_pose(pose, {}, {}, {"Hips": "Hips", "LeftArm": "LeftArm", "Head": "Head"})
        for v in out.values():
            self.assertAlmostEqual(v[0], 1.0, places=6)

    def test_rotation_transfers_with_target_rest(self):
        # Source rest identity, source pose 30 deg about Z; target
        # rest is itself 10 deg about Z, so target pose = 30 * 10 = 40 deg.
        out = wr.retarget_pose({"LeftArm": qz(30)}, {"LeftArm": IDENT},
                               {"LeftArm": qz(10)}, {"LeftArm": "LeftArm"})
        expect = qz(40)
        for a, b in zip(out["LeftArm"], expect):
            self.assertAlmostEqual(a, b, places=5)

    def test_unmapped_source_dropped_and_target_held(self):
        report = wr.retarget_report(["Hips", "CapeBone", "Head"],
                                    ["Hips", "Head", "LeftHand"],
                                    {"Hips": "Hips", "Head": "Head"})
        self.assertEqual(report["dropped_source"], ["CapeBone"])
        self.assertEqual(report["held_at_rest_target"], ["LeftHand"])

    def test_spine_collapse_averages(self):
        out = wr.retarget_pose({"Spine": qz(20), "Spine1": qz(20)}, {}, {},
                               {"Spine": "Chest", "Spine1": "Chest"})
        for a, b in zip(out["Chest"], qz(20)):
            self.assertAlmostEqual(a, b, places=5)

    def test_clip_in_place_zeroes_root(self):
        frames = wr.retarget_clip(
            [{"pose": {"Hips": IDENT}, "root_translation": [0.1, 1.0, 0.2]}],
            {}, {}, {"Hips": "Hips"}, in_place=True)
        self.assertEqual(frames[0]["root_translation"], [0.0, 0.0, 0.0])

    def test_clip_root_scales_by_hip_ratio(self):
        frames = wr.retarget_clip(
            [{"pose": {"Hips": IDENT}, "root_translation": [0.1, 1.0, 0.2]}],
            {}, {}, {"Hips": "Hips"}, in_place=False, hip_height_ratio=0.5)
        self.assertEqual(frames[0]["root_translation"], [0.05, 0.5, 0.1])


class TestStance(unittest.TestCase):
    def test_arm_direction_matches_desired(self):
        # Rest arm along +X (shoulder->elbow); desired direction is -Y
        # (arm hanging down). Shortest-arc solve must land on -Y.
        rest_pos = {"LeftArm": [0.2, 1.5, 0.0], "LeftForeArm": [0.5, 1.5, 0.0],
                    "LeftHand": [0.8, 1.5, 0.0]}
        world = wr.bake_stance_ik(
            {"LeftArm": IDENT}, {"LeftArm": [0.0, -1.0, 0.0]},
            {"LeftArm": IDENT}, rest_pos, PARENTS,
            {"LeftArm": "LeftForeArm"})
        got = wr.q_rotate(world["LeftArm"], [1.0, 0.0, 0.0])
        for a, b in zip(got, [0.0, -1.0, 0.0]):
            self.assertAlmostEqual(a, b, places=6)

    def test_non_arm_orientation_kept(self):
        world = wr.bake_stance_ik(
            {"Chest": qz(15)}, {}, {"Chest": IDENT},
            {"Chest": [0, 1.2, 0], "Neck": [0, 1.5, 0]}, PARENTS, {})
        self.assertAlmostEqual(world["Chest"][0], qz(15)[0], places=6)


class TestQA(unittest.TestCase):
    def _weights(self, head_bone):
        # 10 verts: 2 head verts (top of Y range), 8 body verts.
        pos = [[0, 0.2, 0]] * 8 + [[0, 1.8, 0], [0, 1.9, 0]]
        w = [{"LeftLeg": 1.0}] * 8 + [{head_bone: 1.0}, {head_bone: 1.0}]
        return w, pos

    def test_good_weights_pass(self):
        w, pos = self._weights("Head")
        report = wr.qa_weights(w, pos, height_axis=1)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["max_weight_sum_error"], 0.0)

    def test_head_dominated_by_spine_fails(self):
        w, pos = self._weights("Spine")
        report = wr.qa_weights(w, pos, height_axis=1)
        self.assertEqual(report["verdict"], "FAIL-FACE-STRETCH-RISK")
        self.assertEqual(report["suspect_fraction"], 1.0)

    def test_svg_contains_bones_and_views(self):
        svg = wr.qa_render_svg(
            {"Hips": [0, 1.0, 0], "Head": [0, 1.7, 0], "LeftHand": [0.5, 1.4, 0]},
            [("Hips", "Head"), ("Hips", "LeftHand")])
        self.assertIn("<svg", svg)
        self.assertIn("front", svg)
        self.assertIn("Head", svg)


if __name__ == "__main__":
    unittest.main()
