"""Offline tests for pr_status_board.py (no network)."""
import base64
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

    def run_publish(self, fake_req):
        """publish_branch with b.req/b._sleep stubbed; returns (message, calls)."""
        calls = []

        def spy(method, path, body=None):
            # Snapshot the body: publish_branch mutates it in place on retry.
            calls.append((method, path, dict(body) if isinstance(body, dict) else body))
            return fake_req(method, path, body)

        old_req, old_sleep = b.req, b._sleep
        b.req, b._sleep = spy, lambda s: None
        try:
            return b.publish_branch("new board"), calls
        finally:
            b.req, b._sleep = old_req, old_sleep

    def branch_ok(self, method, path, body=None):
        if method == "GET" and path.startswith("repos/" + b.REPO + "/branches/"):
            return 200, {"name": b.BOARD_BRANCH}
        return None

    def test_publish_branch_get_failure_issues_no_put(self):
        """A failed contents GET must never issue a sha-less PUT (422 when the file exists)."""
        def fake(method, path, body=None):
            if (r := self.branch_ok(method, path, body)) is not None:
                return r
            if method == "GET" and "/contents/" in path:
                return 503, {"message": "Service Unavailable"}
            return 404, {"message": "Not Found"}

        msg, calls = self.run_publish(fake)
        self.assertEqual(msg, "branch: read failed (503): {'message': 'Service Unavailable'}")
        self.assertFalse([c for c in calls if c[0] == "PUT"], "no PUT may follow a failed read")
        self.assertEqual(sum(1 for c in calls if c[0] == "GET" and "/contents/" in c[1]), 4)  # 1 + 3 retries

    def test_publish_branch_retries_transient_get_then_puts_with_sha(self):
        gets = {"n": 0}

        def fake(method, path, body=None):
            if (r := self.branch_ok(method, path, body)) is not None:
                return r
            if method == "GET" and "/contents/" in path:
                gets["n"] += 1
                if gets["n"] < 3:
                    return 503, {"message": "Service Unavailable"}
                return 200, {"sha": "331168c6", "content": base64.b64encode(b"old board").decode()}
            if method == "PUT":
                return 200, {}
            return 404, {"message": "Not Found"}

        msg, calls = self.run_publish(fake)
        self.assertEqual(msg, "branch: committed (200)")
        puts = [c for c in calls if c[0] == "PUT"]
        self.assertEqual(len(puts), 1)
        self.assertEqual(puts[0][2]["sha"], "331168c6")

    def test_publish_branch_missing_file_creates_without_sha(self):
        def fake(method, path, body=None):
            if (r := self.branch_ok(method, path, body)) is not None:
                return r
            if method == "GET" and "/contents/" in path:
                return 404, {"message": "Not Found"}
            if method == "PUT":
                return 201, {}
            return 404, {"message": "Not Found"}

        msg, calls = self.run_publish(fake)
        self.assertEqual(msg, "branch: committed (201)")
        puts = [c for c in calls if c[0] == "PUT"]
        self.assertEqual(len(puts), 1)
        self.assertNotIn("sha", puts[0][2])

    def test_publish_branch_put_conflict_retries_with_fresh_sha(self):
        gets, puts = {"n": 0}, {"n": 0}

        def fake(method, path, body=None):
            if (r := self.branch_ok(method, path, body)) is not None:
                return r
            if method == "GET" and "/contents/" in path:
                gets["n"] += 1
                sha = "oldsha" if gets["n"] == 1 else "newsha"
                return 200, {"sha": sha, "content": base64.b64encode(b"old board").decode()}
            if method == "PUT":
                puts["n"] += 1
                return (409, {"message": "Conflict"}) if puts["n"] == 1 else (200, {})
            return 404, {"message": "Not Found"}

        msg, calls = self.run_publish(fake)
        self.assertEqual(msg, "branch: committed (200)")
        put_bodies = [c[2] for c in calls if c[0] == "PUT"]
        self.assertEqual([p["sha"] for p in put_bodies], ["oldsha", "newsha"])


if __name__ == "__main__":
    unittest.main()
