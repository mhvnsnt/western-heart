import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from instruction_gate import check  # noqa: E402

GOOD = """## Owner instruction (verbatim quote)
> Cut the arm piece out with Smart Cut in the same project.

## Method the owner specified
Smart Cut in the existing project file

## Method actually used
Smart Cut in the existing project file

## Deviations (none / list, each with owner approval link)
none

## Proof (paths to files, frames, test output)
- `renders/arm_cut.png`

## Self-check: I verified the result against the literal instruction
- [x] I re-read the verbatim instruction and the result matches it.
"""

BAD = GOOD.replace("Smart Cut in the existing project file\n\n## Deviations",
                   "Rectangular crop of the frame\n\n## Deviations")


class Gate(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_passing_body(self):
        self.assertEqual(check(GOOD, ["renders/arm_cut.png"], self.d), [])

    def test_failing_body_substituted_method(self):
        errs = check(BAD, ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("differs" in e for e in errs), errs)

    def test_missing_section(self):
        body = GOOD.split("## Proof")[0]
        self.assertTrue(any("Missing required section" in e for e in check(body, [], self.d)))

    def test_empty_section(self):
        body = GOOD.replace("Smart Cut in the existing project file\n\n## Method actually",
                            "\n## Method actually")
        self.assertTrue(any("empty" in e for e in check(body, ["renders/arm_cut.png"], self.d)))

    def test_deviation_without_approval(self):
        body = BAD.replace("none\n", "- used a crop because it was faster\n")
        errs = check(body, ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("approval" in e for e in errs), errs)

    def test_deviation_with_approval_passes(self):
        body = BAD.replace("none\n", "- crop instead of Smart Cut, approved https://github.com/o/r/pull/1#issuecomment-1\n")
        self.assertEqual(check(body, ["renders/arm_cut.png"], self.d), [])

    def test_missing_proof_path(self):
        errs = check(GOOD, [], self.d)
        self.assertTrue(any("Proof path" in e for e in errs), errs)

    def test_proof_path_in_repo(self):
        os.makedirs(os.path.join(self.d, "renders"))
        open(os.path.join(self.d, "renders/arm_cut.png"), "w").close()
        self.assertEqual(check(GOOD, [], self.d), [])

    def test_unticked_selfcheck(self):
        errs = check(GOOD.replace("[x]", "[ ]"), ["renders/arm_cut.png"], self.d)
        self.assertTrue(any("Self-check" in e for e in errs), errs)

    def test_docs_only_exempt(self):
        self.assertEqual(check("", ["README.md", "docs/a.md"], self.d, ["docs-only"]), [])

    def test_docs_only_with_code_fails(self):
        self.assertTrue(check("", ["README.md", "main.py"], self.d, ["docs-only"]))

    def test_dependabot_exempt(self):
        self.assertEqual(check("", ["package.json"], self.d, [], "dependabot[bot]"), [])


    def test_commit_tag_and_digest_refs(self):
        # PR #720's Proof: release tags, commit SHAs and truncated sha256 digests (2026-10-23 backlog).
        body = GOOD.replace("- `renders/arm_cut.png`",
                            "- `renders/arm_cut.png`\n- original in release `bruno-a1-original`, commit `56c0d4e5`, "
                            "sha256 `5f1fb5a7\u2026e9906da41`")
        known = {("ref", "bruno-a1-original"), ("commit", "56c0d4e5")}
        ok = lambda kind, ref: (kind, ref) in known  # noqa: E731
        self.assertEqual(check(body, ["renders/arm_cut.png"], self.d, resolve_ref=ok), [])

    def test_unknown_ref_and_commit_fail(self):
        body = GOOD.replace("- `renders/arm_cut.png`", "- `renders/arm_cut.png`\n- `no-such-release` `deadbeef1`")
        errs = check(body, ["renders/arm_cut.png"], self.d, resolve_ref=lambda kind, ref: False)
        self.assertTrue(any("not a file, commit, tag" in e for e in errs), errs)
        self.assertTrue(any("Proof commit not found" in e for e in errs), errs)

    def test_digest_only_proof_fails(self):
        body = GOOD.replace("- `renders/arm_cut.png`", "- `5f1fb5a7\u2026e9906da41`")
        errs = check(body, [], self.d)
        self.assertTrue(any("only checksums" in e for e in errs), errs)

    def test_url_proof_passes(self):
        body = GOOD.replace("`renders/arm_cut.png`", "`https://github.com/o/r/releases/tag/x`")
        self.assertEqual(check(body, [], self.d), [])



class LiveBody(unittest.TestCase):
    """Repro: the event payload holds the old (bad) body; the PR now has the fixed one."""

    def test_stale_payload_uses_current_body(self):
        from instruction_gate import live_pr
        stale = {"number": 1, "body": BAD, "labels": [], "user": {"login": "x"}}
        self.assertTrue(check(stale["body"], ["renders/arm_cut.png"]))
        pr = live_pr(stale, "o/r", fetch=lambda repo, n: {"body": GOOD, "labels": []})
        self.assertEqual(check(pr["body"], ["renders/arm_cut.png"]), [])

    def test_fetch_failure_falls_back_to_payload(self):
        from instruction_gate import live_pr
        stale = {"number": 1, "body": BAD}
        self.assertEqual(live_pr(stale, "o/r", fetch=lambda r, n: None)["body"], BAD)

        def boom(r, n):
            raise OSError("no network")
        self.assertEqual(live_pr(stale, "o/r", fetch=boom)["body"], BAD)


if __name__ == "__main__":
    unittest.main()
