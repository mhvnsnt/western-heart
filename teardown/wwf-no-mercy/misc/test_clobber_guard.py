#!/usr/bin/env python3
"""Unit tests for clobber_guard.py — includes a synthetic reproduction of the
PR #579 stale-base clobber pattern (must flag) and legit cases (must not)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from clobber_guard import (  # noqa: E402
    _UnparseableDiff, _diff_line_sets, _diff_names, _parse_diff_output,
    _read_revision_files, check_files, is_binary_path, main,
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


class DiffBased(unittest.TestCase):
    """The diff-based check in main(): three revisions in a temp repo.

    base has f.txt (a, b). main adds NEW-LINE. head-stale is base again
    (the PR #579 pattern); head-keeping matches main.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="clobber-guard-diff-")
        self._old_cwd = os.getcwd()
        os.chdir(self.dir)
        self._git("init", "-q")
        self._git("config", "user.name", "test")
        self._git("config", "user.email", "test@example.com")
        self._write("f.txt", b"a\nb\n")
        self._write("gone.txt", b"will vanish\n")
        self._write("my b/file.txt", b"space bee\n")
        self._git("add", "-A")
        self._git("commit", "-qm", "base")
        self.base = self._git("rev-parse", "HEAD")
        self._write("f.txt", b"a\nb\nNEW-LINE\n")
        self._write("my b/file.txt", b"space bee\nBEE-LINE\n")
        self._git("add", "-A")
        self._git("commit", "-qm", "main")
        self.main = self._git("rev-parse", "HEAD")
        # head-stale: back to base content (reverts main's lines)
        self._git("checkout", "-q", self.base)
        self._git("checkout", "-qb", "stale")
        self.stale = self._git("rev-parse", "HEAD")
        # head-keeping: same content as main
        self._git("checkout", "-q", self.main)
        self._git("checkout", "-qb", "keeping")
        self.keeping = self._git("rev-parse", "HEAD")
        # head-deleting: main's content minus gone.txt AND f.txt
        self._write("f.txt", b"a\nb\nNEW-LINE\n")
        os.remove(os.path.join(self.dir, "gone.txt"))
        os.remove(os.path.join(self.dir, "f.txt"))
        self._git("add", "-A")
        self._git("commit", "-qm", "deleting")
        self.deleting = self._git("rev-parse", "HEAD")
        self.event = os.path.join(self.dir, "event.json")
        with open(self.event, "w") as fh:
            json.dump({"pull_request": {"body": "", "labels": []}}, fh)

    def tearDown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.dir, ignore_errors=True)
        for k in ("BASE_SHA", "HEAD_SHA", "MAIN_SHA", "GITHUB_EVENT_PATH"):
            os.environ.pop(k, None)

    def _git(self, *args):
        r = subprocess.run(["git", "-C", self.dir, *args],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _write(self, rel, data):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    def _run_main(self, base, head, main_sha):
        os.environ["BASE_SHA"] = base
        os.environ["HEAD_SHA"] = head
        os.environ["MAIN_SHA"] = main_sha
        os.environ["GITHUB_EVENT_PATH"] = self.event
        return main()

    def test_stale_head_flags(self):
        self.assertEqual(self._run_main(self.base, self.stale, self.main), 1)

    def test_keeping_head_passes(self):
        self.assertEqual(self._run_main(self.base, self.keeping, self.main), 0)

    def test_main_equals_base_passes_fast(self):
        self.assertEqual(self._run_main(self.base, self.stale, self.base), 0)

    def test_branch_deleted_file_does_not_flag(self):
        # f.txt is gone at head, but the deletion guard owns deletions;
        # the clobber guard must not flag its main-added line. gone.txt
        # was never touched by main, so it cannot flag either.
        self.assertEqual(
            self._run_main(self.base, self.deleting, self.main), 0)

    def test_diff_names_and_line_sets(self):
        names = _diff_names(self.base, self.main, cwd=self.dir)
        self.assertEqual(sorted(names), ["f.txt", "my b/file.txt"])
        added, deleted = _diff_line_sets(self.base, self.main, names,
                                         cwd=self.dir)
        self.assertEqual(added["f.txt"], {"NEW-LINE"})
        self.assertEqual(added["my b/file.txt"], {"BEE-LINE"})
        self.assertEqual(deleted["f.txt"], set())
        # main -> stale: NEW-LINE is deleted (the revert, incl. the
        # " b/" filename, which the header parser must not mangle).
        _, deleted2 = _diff_line_sets(self.main, self.stale, names,
                                      collect_added=False, cwd=self.dir)
        self.assertEqual(deleted2["f.txt"], {"NEW-LINE"})
        self.assertEqual(deleted2["my b/file.txt"], {"BEE-LINE"})

    def test_parse_diff_output_crlf_and_blanks(self):
        lines = [
            b"diff --git a/f.txt b/f.txt\n",
            b"index 1111111..2222222 100644\n",
            b"--- a/f.txt\n",
            b"+++ b/f.txt\n",
            b"@@ -1,1 +1,3 @@\n",
            b" a\n",
            b"+CRLF-LINE\r\n",
            b"+\n",
            b"+   \n",
            b"-gone\r\n",
        ]
        added, deleted = _parse_diff_output(lines, {"f.txt"})
        self.assertEqual(added["f.txt"], {"CRLF-LINE"})
        self.assertEqual(deleted["f.txt"], {"gone"})

    def test_parse_diff_output_bad_header_raises(self):
        lines = [b"diff --git a/f.txt b/other.txt\n"]
        with self.assertRaises(_UnparseableDiff):
            _parse_diff_output(lines, {"f.txt"})


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
