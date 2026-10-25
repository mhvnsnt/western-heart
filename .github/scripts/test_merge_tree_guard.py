#!/usr/bin/env python3
"""Unit tests for merge_tree_guard.py — builds real temp git repos and
reproduces the PR #974 fake stale-tree merge (must flag) plus legit merges
(must pass)."""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from merge_tree_guard import (  # noqa: E402
    check_merge_commit,
    is_merge_commit,
    merge_commits_in_range,
)


def sh(repo, *args, check=True):
    r = subprocess.run(["git", *args], cwd=repo,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r


def write(repo, name, content="x\n"):
    p = os.path.join(repo, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(content)


class TempRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        sh(self.repo, "init", "-q")
        sh(self.repo, "config", "user.email", "t@t.t")
        sh(self.repo, "config", "user.name", "t")
        sh(self.repo, "config", "commit.gpgsign", "false")
        # base commit on main
        write(self.repo, "base.txt")
        sh(self.repo, "add", "base.txt")
        sh(self.repo, "commit", "-qm", "base")
        self.base = sh(self.repo, "rev-parse", "HEAD").stdout.strip()
        # feature branch adds its own file
        sh(self.repo, "checkout", "-qb", "feat")
        write(self.repo, "feat.txt")
        sh(self.repo, "add", "feat.txt")
        sh(self.repo, "commit", "-qm", "feat work")
        self.feat = sh(self.repo, "rev-parse", "HEAD").stdout.strip()
        # main gains a file after the fork point
        sh(self.repo, "checkout", "-q", "master")
        write(self.repo, "main-added.txt")
        sh(self.repo, "add", "main-added.txt")
        sh(self.repo, "commit", "-qm", "main work after fork")
        self.main_tip = sh(self.repo, "rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.tmp.cleanup()

    def fake_stale_tree_merge(self):
        """Reproduce #974: merge commit whose tree == stale branch tree."""
        tree = sh(self.repo, "rev-parse", f"{self.feat}^{{tree}}").stdout.strip()
        m = sh(self.repo, "commit-tree", tree, "-p", self.main_tip,
               "-p", self.feat, "-m", "fake merge").stdout.strip()
        sh(self.repo, "update-ref", "refs/heads/master", m)
        return m

    def real_merge(self):
        sh(self.repo, "merge", "--no-ff", "-m", "real merge", "feat", "-q")
        return sh(self.repo, "rev-parse", "HEAD").stdout.strip()

    def no_labels(self, sha):
        return set()


class FakeMerge(TempRepo):
    def test_fake_stale_tree_merge_flags(self):
        m = self.fake_stale_tree_merge()
        self.assertTrue(is_merge_commit(self.repo, m))
        violations, notes = check_merge_commit(self.repo, m, self.no_labels)
        # main-added.txt was dropped by the merge; the PR never deleted it.
        self.assertEqual(violations, ["main-added.txt"])
        # feat.txt is in both trees -- not a violation.
        self.assertNotIn("feat.txt", violations)
        # degenerate case gets the loud banner
        self.assertTrue(any("FAKE MERGE" in n for n in notes),
                        f"expected FAKE MERGE note, got {notes}")

    def test_merge_range_lists_it(self):
        m = self.fake_stale_tree_merge()
        found = merge_commits_in_range(self.repo, self.base, m)
        self.assertEqual(found, [m])

    def test_owner_label_escapes(self):
        m = self.fake_stale_tree_merge()
        violations, notes = check_merge_commit(
            self.repo, m, lambda sha: {"owner-approved-deletion"})
        self.assertEqual(violations, [])
        self.assertTrue(any("owner-approved-deletion" in n for n in notes))


class CleanMerge(TempRepo):
    def test_real_merge_passes(self):
        m = self.real_merge()
        violations, notes = check_merge_commit(self.repo, m, self.no_labels)
        self.assertEqual(violations, [])
        self.assertFalse(any("FAKE MERGE" in n for n in notes))

    def test_pr_own_deletion_not_flagged(self):
        # Branch deletes base.txt itself; the merge dropping it is legit.
        sh(self.repo, "checkout", "-q", "feat")
        sh(self.repo, "rm", "-q", "base.txt")
        sh(self.repo, "commit", "-qm", "branch deletes base.txt")
        sh(self.repo, "checkout", "-q", "master")
        m = self.real_merge()
        violations, _ = check_merge_commit(self.repo, m, self.no_labels)
        self.assertEqual(violations, [])

    def test_non_merge_commit_skipped(self):
        violations, notes = check_merge_commit(
            self.repo, self.main_tip, self.no_labels)
        self.assertEqual(violations, [])
        self.assertTrue(any("not a merge" in n for n in notes))

    def test_unrelated_history_skipped(self):
        # Branch with no common history: deletions unverifiable -> skip,
        # never false-flag.
        sh(self.repo, "checkout", "-q", "--orphan", "alien")
        sh(self.repo, "rm", "-q", "-rf", ".")
        write(self.repo, "alien.txt")
        sh(self.repo, "add", "alien.txt")
        sh(self.repo, "commit", "-qm", "alien root")
        alien = sh(self.repo, "rev-parse", "HEAD").stdout.strip()
        sh(self.repo, "checkout", "-q", "master")
        tree = sh(self.repo, "rev-parse", f"{alien}^{{tree}}").stdout.strip()
        m = sh(self.repo, "commit-tree", tree, "-p", self.main_tip,
               "-p", alien, "-m", "alien merge").stdout.strip()
        violations, notes = check_merge_commit(self.repo, m, self.no_labels)
        self.assertEqual(violations, [])
        self.assertTrue(any("unverifiable" in n for n in notes))


if __name__ == "__main__":
    unittest.main()
