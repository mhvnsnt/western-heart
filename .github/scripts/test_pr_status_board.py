"""Offline tests for pr_status_board.py (no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import pr_status_board as b  # noqa: E402

REQ = ["clobber-guard", "guard"]


def pr(n, base="main", head=None, draft=False, mergeable="MERGEABLE", checks=()):
    ctx = [{"__typename": "CheckRun", "name": nm, "status": st, "conclusion": c} for nm, st, c in checks]
    return {"number": n, "title": f"PR {n}", "url": "", "isDraft": draft, "mergeable": mergeable,
            "mergeStateStatus": "CLEAN", "updatedAt": "2026-11-03T22:00:00Z", "headRefName": head or f"b{n}",
            "baseRefName": base, "headRefOid": "abcdef1234", "author": {"login": "x"},
            "commits": {"nodes": [{"commit": {"statusCheckRollup": {"contexts": {"nodes": ctx}}}}]}}


GREEN = [("clobber-guard", "COMPLETED", "SUCCESS"), ("guard", "COMPLETED", "SUCCESS")]


class T(unittest.TestCase):
    def rows(self, prs):
        heads = {p["headRefName"]: p["number"] for p in prs}
        return [b.classify(p, REQ, heads) for p in prs]

    def test_statuses(self):
        rows = self.rows([
            pr(1, checks=GREEN),
            pr(2, checks=GREEN + [("x", "COMPLETED", "FAILURE")]),
            pr(3, checks=[("guard", "IN_PROGRESS", None)]),
            pr(4, mergeable="CONFLICTING", checks=GREEN),
            pr(5, draft=True, checks=GREEN),
        ])
        self.assertEqual([r["status"] for r in rows], ["ready", "failing", "running", "conflicted", "draft"])
        self.assertEqual(rows[2]["required"]["clobber-guard"], "missing")

    def test_own_check_ignored(self):
        (r,) = self.rows([pr(1, checks=GREEN + [("pr-status-board", "IN_PROGRESS", None)])])
        self.assertEqual(r["status"], "ready")

    def test_stacked_merge_order_and_sort(self):
        rows = self.rows([pr(1525, head="hair", checks=GREEN), pr(1526, base="hair", checks=GREEN)])
        self.assertEqual(rows[1]["stacked_on"], 1525)
        self.assertEqual(rows[1]["status"], "stacked")
        md = b.render(rows, REQ, "now")
        self.assertIn("#1525 → #1526", md)
        self.assertLess(md.index("[#1525]"), md.index("[#1526]"))  # ready-to-merge first
        self.assertIn("ready to merge: 1", md)

    def test_compare_ignores_timestamp(self):
        rows = self.rows([pr(1, checks=GREEN)])
        self.assertEqual(b.strip_gen(b.render(rows, REQ, "t1")), b.strip_gen(b.render(rows, REQ, "t2")))

    def test_time(self):
        self.assertEqual(b.fmt_time("2026-11-03T22:00:00Z"), "2026-11-03 22:00 UTC")


if __name__ == "__main__":
    unittest.main()
