#!/usr/bin/env python3
"""Unit tests for the gltfpack pipeline (Lane 5, 2026-10-24).
Run: python3 -m unittest discover -s tools/gltfpack -p 'test_gltfpack_pipeline.py' -v
No gltfpack binary needed: validation / flag / budget logic only.
"""
import importlib.util
import json
import os
import struct
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BATCH = _load("batch-optimize.py")
BUDGETS = _load("check-budgets.py")


def _glb(doc, bin_len=64):
    j = json.dumps(doc).encode()
    j += b" " * ((4 - len(j) % 4) % 4)
    total = 12 + 8 + len(j) + 8 + bin_len
    return (b"glTF" + struct.pack("<II", 2, total)
            + struct.pack("<II", len(j), 0x4E4F534A) + j
            + struct.pack("<II", bin_len, 0x004E4942) + b"\0" * bin_len)


class TestValidate(unittest.TestCase):
    def _write(self, data):
        fd, path = tempfile.mkstemp(suffix=".glb")
        os.write(fd, data)
        os.close(fd)
        self.addCleanup(os.unlink, path)
        return path

    def test_good_skinned_and_unskinned(self):
        ok, err, info = BATCH.validate_glb(self._write(_glb(
            {"buffers": [{"byteLength": 64}], "skins": [{"joints": [0]}]})))
        self.assertTrue(ok, err)
        self.assertTrue(info["skinned"])
        ok, _err, info = BATCH.validate_glb(self._write(_glb(
            {"buffers": [{"byteLength": 64}]})))
        self.assertTrue(ok)
        self.assertFalse(info["skinned"])

    def test_bad_magic_and_overrun_buffer_view(self):
        ok, _e, _i = BATCH.validate_glb(self._write(b"NOPE" + b"\0" * 40))
        self.assertFalse(ok)
        ok, err, _i = BATCH.validate_glb(self._write(_glb(
            {"buffers": [{"byteLength": 64}],
             "bufferViews": [{"byteOffset": 60, "byteLength": 16}]})))
        self.assertFalse(ok)
        self.assertIn("overruns", err)

    def test_meshopt_view_uses_extension_extent_not_decoded_size(self):
        doc = {"buffers": [{"byteLength": 64}],
               "bufferViews": [{"byteOffset": 0, "byteLength": 1000,
                                "extensions": {"EXT_meshopt_compression":
                                               {"byteOffset": 0, "byteLength": 64}}}]}
        ok, err, _i = BATCH.validate_glb(self._write(_glb(doc, bin_len=64)))
        self.assertTrue(ok, err)

    def test_bin_chunk_mismatch(self):
        doc = {"buffers": [{"byteLength": 128}]}
        ok, err, _i = BATCH.validate_glb(self._write(_glb(doc, bin_len=64)))
        self.assertFalse(ok)
        self.assertIn("BIN chunk", err)


class TestFlags(unittest.TestCase):
    def test_skinned_gets_kn_unskinned_does_not(self):
        self.assertEqual(BATCH.flags_for(True), ["-cc", "-kn"])
        self.assertEqual(BATCH.flags_for(False), ["-cc"])

    def test_tc_off_by_default_and_si_needs_allow(self):
        self.assertNotIn("-tc", BATCH.flags_for(True))
        self.assertNotIn("-si", BATCH.flags_for(True))
        self.assertEqual(BATCH.flags_for(False, tc=True), ["-cc", "-tc"])


class TestBudgets(unittest.TestCase):
    def _entry(self, **kw):
        e = {"input": "game/assets/stages/x.glb", "status": "ok",
             "inBytes": 1000, "outBytes": 500}
        e.update(kw)
        return e

    def test_pass_and_growth_and_cap(self):
        self.assertEqual(BUDGETS.check({"assets": [self._entry()]}, BUDGETS.DEFAULT_CAPS), [])
        self.assertEqual(len(BUDGETS.check(
            {"assets": [self._entry(outBytes=1500)]}, BUDGETS.DEFAULT_CAPS)), 1)
        self.assertEqual(len(BUDGETS.check(
            {"assets": [self._entry(outBytes=6_000_000, inBytes=9_000_000)]},
            BUDGETS.DEFAULT_CAPS)), 1)

    def test_tc_needs_measurement_and_skinned_simplify_needs_approval(self):
        self.assertEqual(len(BUDGETS.check(
            {"assets": [self._entry(tc=True)]}, BUDGETS.DEFAULT_CAPS), ), 1)
        self.assertEqual(BUDGETS.check(
            {"assets": [self._entry(tc=True, tc_measured=True)]}, BUDGETS.DEFAULT_CAPS), [])
        self.assertEqual(len(BUDGETS.check(
            {"assets": [self._entry(simplified=True, skinned=True)]},
            BUDGETS.DEFAULT_CAPS), ), 1)
        self.assertEqual(BUDGETS.check(
            {"assets": [self._entry(simplified=True, skinned=True, simplify_approved=True)]},
            BUDGETS.DEFAULT_CAPS), [])

    def test_failed_assets_are_not_budget_breaches(self):
        self.assertEqual(BUDGETS.check(
            {"assets": [self._entry(status="invalid")]}, BUDGETS.DEFAULT_CAPS), [])


class TestRunnerDefaults(unittest.TestCase):
    def test_tc_is_opt_in_in_run_gltfpack_job(self):
        with open(os.path.join(HERE, "run_gltfpack_job.py")) as fh:
            src = fh.read()
        # The runner must never pass -tc unconditionally: it appears
        # only behind the params.tc gate.
        self.assertIn('if params.get("tc")', src)
        self.assertNotIn('"-cc", "-tc"', src)
        self.assertIn('params.get("kn", True)', src)


if __name__ == "__main__":
    unittest.main()
