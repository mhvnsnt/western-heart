#!/usr/bin/env python3
"""Tests for tools/customization/import_tweak_patch.py.

Run: python3 tools/customization/tests/test_import_tweak_patch.py
Covers: valid patch applies; every malformed shape is REJECTED with a clear
error and writes nothing.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "customization"))
from import_tweak_patch import validate, apply_patch, PatchError  # noqa: E402


def good_patch(**kw):
    p = {
        "format": "wh-tweak-patch", "version": 1,
        "kit_id": "julia-parts-fix-1", "fighter": "nightwolf",
        "attire": "default", "exported_at": "2026-10-22T06:35:00Z",
        "exported_by": "suite", "suite_build": "test",
        "notes": "head was backwards",
        "changes": [
            {"kind": "part_transform", "group": "head",
             "rotation_deg": [0, 180, 0], "flip": [False, False, False],
             "offset": [0, 0, 0], "scale": 1.0, "note": "face forward"},
        ],
    }
    p.update(kw)
    return p


class FakeRepo:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="tweakrepo")
        os.makedirs(os.path.join(self.root, "game", "js"))
        os.makedirs(os.path.join(self.root, "customization", "tweak-kits"))
        with open(os.path.join(self.root, "game", "js", "roster-full.js"), "w") as f:
            f.write("{ id: 'nightwolf', name: 'NIGHTWOLF' },\n")
        kit = {"format": "wh-tweak-kit", "version": 1, "id": "julia-parts-fix-1",
               "fighter": "nightwolf", "attire": "default", "status": "staged",
               "notes": "", "flagged_parts": ["head"], "part_map": {},
               "adjustments": {}, "history": []}
        with open(os.path.join(self.root, "customization", "tweak-kits",
                               "julia-parts-fix-1.json"), "w") as f:
            json.dump(kit, f)

    def teardown(self):
        shutil.rmtree(self.root, ignore_errors=True)


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()

    def tearDown(self):
        self.repo.teardown()

    def ok(self, patch):
        return validate(patch, self.repo.root)

    def bad(self, patch, snippet):
        with self.assertRaises(PatchError) as cm:
            validate(patch, self.repo.root)
        self.assertIn(snippet, str(cm.exception))

    def test_valid(self):
        n = self.ok(good_patch())
        self.assertEqual(n["fighter"], "nightwolf")
        self.assertEqual(len(n["changes"]), 1)

    def test_bad_format(self):
        self.bad(good_patch(format="nope"), "'format'")

    def test_bad_version(self):
        self.bad(good_patch(version=99), "unsupported 'version'")

    def test_unknown_fighter(self):
        self.bad(good_patch(fighter="nope"), "unknown 'fighter'")

    def test_unknown_kit(self):
        self.bad(good_patch(kit_id="nope"), "unknown 'kit_id'")

    def test_kit_fighter_mismatch(self):
        p = good_patch()
        kp = os.path.join(self.repo.root, "customization", "tweak-kits",
                          "julia-parts-fix-1.json")
        kit = json.load(open(kp))
        kit["fighter"] = "pantera"
        json.dump(kit, open(kp, "w"))
        self.bad(p, "does not match kit")

    def test_empty_changes(self):
        self.bad(good_patch(changes=[]), "'changes' must be a non-empty array")

    def test_bad_group(self):
        p = good_patch()
        p["changes"][0]["group"] = "wings"
        self.bad(p, "bad 'group'")

    def test_duplicate_group(self):
        p = good_patch()
        p["changes"].append(dict(p["changes"][0]))
        self.bad(p, "duplicate group")

    def test_rotation_out_of_range(self):
        p = good_patch()
        p["changes"][0]["rotation_deg"] = [0, 720, 0]
        self.bad(p, "within [-360, 360]")

    def test_rotation_nan(self):
        p = good_patch()
        p["changes"][0]["rotation_deg"] = [0, float("nan"), 0]
        self.bad(p, "'rotation_deg' must be 3 finite numbers")

    def test_flip_not_bool(self):
        p = good_patch()
        p["changes"][0]["flip"] = [0, 0, 0]
        self.bad(p, "'flip' must be 3 booleans")

    def test_offset_out_of_range(self):
        p = good_patch()
        p["changes"][0]["offset"] = [99, 0, 0]
        self.bad(p, "within [-5, 5]")

    def test_bad_scale(self):
        p = good_patch()
        p["changes"][0]["scale"] = 0
        self.bad(p, "'scale'")

    def test_bad_kind(self):
        p = good_patch()
        p["changes"][0]["kind"] = "move_part"
        self.bad(p, "bad 'kind'")

    def test_not_an_object(self):
        self.bad([1, 2], "must be a JSON object")


class TestApply(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()

    def tearDown(self):
        self.repo.teardown()

    def test_apply_merges_and_records(self):
        norm = validate(good_patch(), self.repo.root)
        written = apply_patch(norm, self.repo.root)
        self.assertEqual(len(written), 1)
        kit_p, applied_p = written[0]
        kit = json.load(open(kit_p))
        self.assertEqual(kit["version"], 2)
        self.assertEqual(kit["adjustments"]["head"]["rotation_deg"], [0, 180, 0])
        self.assertTrue(os.path.isfile(applied_p))
        rec = json.load(open(applied_p))
        self.assertEqual(rec["validation"], "pass")
        self.assertEqual(len(kit["history"]), 1)

    def test_apply_second_patch_wins(self):
        n1 = validate(good_patch(), self.repo.root)
        apply_patch(n1, self.repo.root)
        p2 = good_patch()
        p2["changes"][0]["rotation_deg"] = [0, 90, 0]
        n2 = validate(p2, self.repo.root)
        (kit_p, _), = apply_patch(n2, self.repo.root)
        kit = json.load(open(kit_p))
        self.assertEqual(kit["adjustments"]["head"]["rotation_deg"], [0, 90, 0])
        self.assertEqual(kit["version"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)


def feel_patch(**kw):
    p = {
        "format": "wh-tweak-patch", "version": 1,
        "kit_id": None, "fighter": "nightwolf",
        "attire": "default", "exported_at": "2026-10-22T07:00:00Z",
        "exported_by": "suite", "suite_build": "test",
        "notes": "more oomph",
        "changes": [
            {"kind": "hitfeel_tune", "hitstop": 1.2, "shake": 0.8,
             "knockback": 1.1, "launch": 1.0, "note": "heavier"},
        ],
    }
    p.update(kw)
    return p


class TestHitFeel(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()

    def tearDown(self):
        self.repo.teardown()

    def ok(self, patch):
        return validate(patch, self.repo.root)

    def bad(self, patch, snippet):
        with self.assertRaises(PatchError) as cm:
            validate(patch, self.repo.root)
        self.assertIn(snippet, str(cm.exception))

    def test_valid_feel(self):
        n = self.ok(feel_patch())
        self.assertEqual(n["changes"][0]["kind"], "hitfeel_tune")
        self.assertEqual(n["changes"][0]["hitstop"], 1.2)

    def test_feel_out_of_range(self):
        p = feel_patch()
        p["changes"][0]["shake"] = 9
        self.bad(p, "in [0, 4]")

    def test_feel_all_ones_rejected(self):
        p = feel_patch()
        p["changes"][0].update(
            {"hitstop": 1.0, "shake": 1.0, "knockback": 1.0, "launch": 1.0})
        self.bad(p, "changes nothing")

    def test_feel_apply_writes_file(self):
        n = self.ok(feel_patch())
        written = apply_patch(n, self.repo.root)
        self.assertEqual(len(written), 1)
        fp, applied_p = written[0]
        self.assertTrue(fp.endswith("customization/hit-feel/nightwolf.json"))
        doc = json.load(open(fp))
        self.assertEqual(doc["multipliers"]["hitstop"], 1.2)
        self.assertEqual(doc["multipliers"]["launch"], 1.0)
        self.assertTrue(os.path.isfile(applied_p))

    def test_mixed_patch_applies_both(self):
        p = feel_patch()
        p["changes"].append(good_patch()["changes"][0])
        n = self.ok(p)
        written = apply_patch(n, self.repo.root)
        self.assertEqual(len(written), 2)


def screen_patch(**kw):
    p = {
        "format": "wh-tweak-patch", "version": 1,
        "kit_id": None, "fighter": "ui",
        "attire": "stage-select", "exported_at": "2026-10-22T07:30:00Z",
        "exported_by": "suite", "suite_build": "test",
        "notes": "remixed title",
        "changes": [
            {"kind": "ui_screen_define",
             "screen": {
                 "format": "wh-ui-screen", "version": 1,
                 "id": "stage-select", "name": "Stage Select",
                 "source": "workshop", "canvas": {"w": 1280, "h": 720},
                 "elements": [
                     {"id": "title", "type": "label", "x": 48, "y": 28,
                      "w": 700, "h": 56, "text": "PICK YOUR BATTLEFIELD",
                      "style": {"fontSize": 40, "color": "#f2b01e"}},
                 ],
                 "flow": {}, "wiring": {}},
             "note": "renamed title"},
        ],
    }
    p.update(kw)
    return p


class TestUIScreen(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()

    def tearDown(self):
        self.repo.teardown()

    def ok(self, patch):
        return validate(patch, self.repo.root)

    def bad(self, patch, snippet):
        with self.assertRaises(PatchError) as cm:
            validate(patch, self.repo.root)
        self.assertIn(snippet, str(cm.exception))

    def test_valid_screen(self):
        n = self.ok(screen_patch())
        self.assertEqual(n["changes"][0]["kind"], "ui_screen_define")

    def test_bad_screen_format(self):
        p = screen_patch()
        p["changes"][0]["screen"]["format"] = "nope"
        self.bad(p, "bad screen format")

    def test_bad_element_type(self):
        p = screen_patch()
        p["changes"][0]["screen"]["elements"][0]["type"] = "hologram"
        self.bad(p, "bad type")

    def test_duplicate_element_id(self):
        p = screen_patch()
        p["changes"][0]["screen"]["elements"].append(
            dict(p["changes"][0]["screen"]["elements"][0]))
        self.bad(p, "duplicate id")

    def test_screen_apply_writes_file(self):
        n = self.ok(screen_patch())
        written = apply_patch(n, self.repo.root)
        self.assertEqual(len(written), 1)
        sp, applied_p = written[0]
        self.assertTrue(sp.endswith("customization/ui-screens/stage-select.json"))
        doc = json.load(open(sp))
        self.assertEqual(doc["elements"][0]["text"], "PICK YOUR BATTLEFIELD")
        self.assertTrue(os.path.isfile(applied_p))
