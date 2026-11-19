#!/usr/bin/env python3
"""Unit tests for clobber_guard.py — includes a synthetic reproduction of the
PR #579 stale-base clobber pattern (must flag) and legit cases (must not)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from clobber_guard import (  # noqa: E402
    _read_revision_files, check_files, is_binary_path,
    parse_revert_callout, reverted_lines,
)


def lines(*ls):
    return ("\n".join(ls) + "\n").encode()


# --- synthetic #579: base (Oct 17) -> main adds lines -> branch overwrites
# --- with a stale full-file copy that lacks main's lines.
BASE_579 = lines(
    "const A = 1;",
    "const B = 2;",
    "// owner comment: torch urls below",
    "const C = 3;",
)
MAIN_579 = lines(
    "const A = 1;",
    "const B = 2;",
    "// owner comment: torch urls below",
    "'torch-tripo-a1': 'roster/torch/attires/attire1/model.glb',",
    "'torch-tripo-a2': 'roster/torch/attires/attire2/model.glb',",
    "'doc-frank-a1': 'roster/docfrank/attires/attire1/model.glb',",
    "const C = 3;",
)
# Stale branch: forked at BASE, added its own line, then committed the whole
# stale file — main's three MODEL_URLS lines are gone.
BRANCH_579 = lines(
    "const A = 1;",
    "const B = 2;",
    "// owner comment: torch urls below",
    "const D = 4;  // branch's own addition",
    "const C = 3;",
)


class RevertedLines(unittest.TestCase):
    def test_579_pattern_flags(self):
        off = reverted_lines(BASE_579, MAIN_579, BRANCH_579)
        self.assertEqual(len(off), 3)
        self.assertIn("'torch-tripo-a1': 'roster/torch/attires/attire1/model.glb',", off)

    def test_clean_pr_no_flag(self):
        head = lines(
            "const A = 1;", "const B = 2;",
            "// owner comment: torch urls below",
            "'torch-tripo-a1': 'roster/torch/attires/attire1/model.glb',",
            "'torch-tripo-a2': 'roster/torch/attires/attire2/model.glb',",
            "'doc-frank-a1': 'roster/docfrank/attires/attire1/model.glb',",
            "const C = 3;",
            "const D = 4;  // branch's own addition",
        )
        self.assertEqual(reverted_lines(BASE_579, MAIN_579, head), set())

    def test_moved_line_no_flag(self):
        # Legit refactor: branch moves a main-added line elsewhere in the file.
        head = lines(
            "'torch-tripo-a1': 'roster/torch/attires/attire1/model.glb',",
            "const A = 1;", "const B = 2;",
            "// owner comment: torch urls below",
            "'torch-tripo-a2': 'roster/torch/attires/attire2/model.glb',",
            "'doc-frank-a1': 'roster/docfrank/attires/attire1/model.glb',",
            "const C = 3;",
        )
        self.assertEqual(reverted_lines(BASE_579, MAIN_579, head), set())

    def test_branch_only_change_no_flag(self):
        # Branch edits a line that predates the fork: main didn't add it.
        head = lines(
            "const A = 1;", "const B = 22;",  # edited by branch
            "// owner comment: torch urls below",
            "'torch-tripo-a1': 'roster/torch/attires/attire1/model.glb',",
            "'torch-tripo-a2': 'roster/torch/attires/attire2/model.glb',",
            "'doc-frank-a1': 'roster/docfrank/attires/attire1/model.glb',",
            "const C = 3;",
        )
        self.assertEqual(reverted_lines(BASE_579, MAIN_579, head), set())

    def test_new_file_no_flag(self):
        self.assertEqual(reverted_lines(None, None, lines("hello")), set())

    def test_binary_skipped(self):
        self.assertEqual(reverted_lines(b"a\x00b", b"a\x00b\x00c", b"a\x00b"), set())

    def test_blank_lines_ignored(self):
        base = lines("a")
        main = lines("a", "")
        head = lines("a")
        self.assertEqual(reverted_lines(base, main, head), set())


class IsBinaryPath(unittest.TestCase):
    def test_binary_extensions(self):
        for p in ["clips/anim_37FA.npy", "img/sprite.PNG", "model.glb",
                  "audio/track.mp3", "data.bin", "rom.z64", "a/b/c.jpg",
                  "font.woff2", "archive.zip", "weights.safetensors"]:
            self.assertTrue(is_binary_path(p), p)

    def test_text_extensions_not_skipped(self):
        # .obj is Wavefront text in this repo; .gltf/.mtl/.json are text.
        for p in ["game/js/main.js", "index.html", "README.md",
                  "data.json", "model.obj", "model.gltf", "model.mtl",
                  "script.py", "notes.txt", "style.css", "noext"]:
            self.assertFalse(is_binary_path(p), p)


class ReadRevisionFiles(unittest.TestCase):
    """_read_revision_files against a real temp git repo (two commits)."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="clobber-guard-test-")
        self._git("init", "-q")
        self._git("config", "user.name", "test")
        self._git("config", "user.email", "test@example.com")
        self._write("a.txt", b"one\ntwo\n")
        self._write("sub/b.txt", b"bee\n")
        self._write("gone.txt", b"will vanish\n")
        self._git("add", "-A")
        self._git("commit", "-qm", "base")
        self.rev1 = self._git("rev-parse", "HEAD")
        self._write("a.txt", b"one\ntwo\nthree\n")
        os.remove(os.path.join(self.dir, "gone.txt"))
        self._write("c.txt", b"new\n")
        self._git("add", "-A")
        self._git("commit", "-qm", "head")
        self.rev2 = self._git("rev-parse", "HEAD")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _git(self, *args):
        r = subprocess.run(["git", "-C", self.dir, *args],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _write(self, rel, data):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def test_reads_both_revisions(self):
        paths = ["a.txt", "sub/b.txt", "gone.txt", "c.txt", "missing.txt"]
        base = _read_revision_files(self.rev1, paths, cwd=self.dir)
        self.assertEqual(base["a.txt"], b"one\ntwo\n")
        self.assertEqual(base["sub/b.txt"], b"bee\n")
        self.assertEqual(base["gone.txt"], b"will vanish\n")
        self.assertIsNone(base["c.txt"])
        self.assertIsNone(base["missing.txt"])
        head = _read_revision_files(self.rev2, paths, cwd=self.dir)
        self.assertEqual(head["a.txt"], b"one\ntwo\nthree\n")
        self.assertEqual(head["sub/b.txt"], b"bee\n")
        self.assertIsNone(head["gone.txt"])
        self.assertEqual(head["c.txt"], b"new\n")
        self.assertIsNone(head["missing.txt"])

    def test_many_files_one_batch(self):
        # 50 files through the single batch process, all read correctly.
        for i in range(50):
            self._write(f"many/f{i:02d}.txt", f"file {i}\n".encode())
        self._git("add", "-A")
        self._git("commit", "-qm", "many")
        rev = self._git("rev-parse", "HEAD")
        paths = [f"many/f{i:02d}.txt" for i in range(50)]
        got = _read_revision_files(rev, paths, cwd=self.dir)
        self.assertEqual(len(got), 50)
        for i in range(50):
            self.assertEqual(got[f"many/f{i:02d}.txt"],
                             f"file {i}\n".encode())

    def test_empty_paths(self):
        self.assertEqual(_read_revision_files(self.rev1, [], cwd=self.dir),
                         {})


class Callout(unittest.TestCase):
    BODY = ("## Reverts\n"
            "Intentional: dropping main's temp debug lines.\n"
            "- `game/js/assets.js`\n"
            "- `index.html`\n")

    def test_paths_parsed(self):
        self.assertEqual(parse_revert_callout(self.BODY),
                         {"game/js/assets.js", "index.html"})

    def test_no_section_empty(self):
        self.assertEqual(parse_revert_callout("## Proof\n- `x`\n"), set())


class CheckFiles(unittest.TestCase):
    def test_flags_without_escape(self):
        bad = check_files({"f.js": BASE_579}, {"f.js": MAIN_579},
                          {"f.js": BRANCH_579})
        self.assertEqual(set(bad), {"f.js"})
        self.assertEqual(len(bad["f.js"]), 3)

    def test_label_exempts(self):
        bad = check_files({"f.js": BASE_579}, {"f.js": MAIN_579},
                          {"f.js": BRANCH_579},
                          labels=["owner-approved-revert"])
        self.assertEqual(bad, {})

    def test_body_callout_exempts_named_file_only(self):
        body = "## Reverts\n- `f.js`\n"
        bad = check_files({"f.js": BASE_579, "g.js": BASE_579},
                          {"f.js": MAIN_579, "g.js": MAIN_579},
                          {"f.js": BRANCH_579, "g.js": BRANCH_579},
                          body=body)
        self.assertEqual(set(bad), {"g.js"})

    def test_deleted_by_branch_skipped(self):
        bad = check_files({"f.js": BASE_579}, {"f.js": MAIN_579},
                          {"f.js": None})
        self.assertEqual(bad, {})


if __name__ == "__main__":
    unittest.main()
