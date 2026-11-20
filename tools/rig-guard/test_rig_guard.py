#!/usr/bin/env python3
"""Unit tests for tools/rig-guard/rig_guard.py.

Run: python3 -m unittest discover -s tools/rig-guard -p 'test_rig_guard.py' -v
"""
import unittest

from rig_guard import (
    check_removals,
    extract_model_keys,
    parse_model_removal_callout,
    removed_keys,
)

SAMPLE = """export const MODEL_URLS = {
  pantera: 'assets/models/pantera.glb',
  // comment with a { brace } and a MODEL_URLS mention
  'kinpo-attire1': '../roster/kinpo/attires/attire1/model-intake.glb',
  "quoted": "assets/models/q.glb",
};
"""


class ExtractTest(unittest.TestCase):
    def test_extracts_bare_quoted_and_double_quoted(self):
        self.assertEqual(
            extract_model_keys(SAMPLE), {"pantera", "kinpo-attire1", "quoted"})

    def test_comment_braces_do_not_corrupt_parse(self):
        self.assertNotIn("brace", extract_model_keys(SAMPLE))

    def test_missing_block_is_empty(self):
        self.assertEqual(extract_model_keys("const X = 1;"), set())


class RemovalTest(unittest.TestCase):
    def test_key_removed_fails(self):
        self.assertEqual(
            check_removals({"a", "b", "c"}, {"a", "b"}, "", []), {"c"})

    def test_key_added_passes(self):
        self.assertEqual(check_removals({"a"}, {"a", "b"}, "", []), set())

    def test_renamed_key_flags_old_name(self):
        self.assertEqual(removed_keys({"old"}, {"new"}), {"old"})

    def test_identical_sets_pass(self):
        self.assertEqual(check_removals({"a"}, {"a"}, "", []), set())


class EscapeTest(unittest.TestCase):
    BODY = "## Model removals\n\nRetiring `c` per owner directive.\n"

    def test_body_callout_passes(self):
        self.assertEqual(
            check_removals({"a", "b", "c"}, {"a", "b"}, self.BODY, []), set())

    def test_partial_callout_still_fails_on_rest(self):
        self.assertEqual(
            check_removals({"b", "c"}, {"a"}, self.BODY, []), {"b"})

    def test_label_passes(self):
        self.assertEqual(
            check_removals({"a", "c"}, {"a"}, "",
                           ["owner-approved-model-removal"]), set())

    def test_callout_parser_finds_backticked_keys(self):
        self.assertEqual(parse_model_removal_callout(self.BODY), {"c"})


if __name__ == "__main__":
    unittest.main()
