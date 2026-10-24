#!/usr/bin/env python3
"""Clobber guard: fail a PR that reverts lines main added after the PR's base.

The PR #579 failure mode (2026-10-22): a PR branched from a stale base
(Oct 17) overwrote whole files with stale full-file copies, deleting
427 lines of game/js/assets.js, 113 of game/js/main.js, 32 of game/js/game.js,
25 of index.html and 316 of WORKLOG.md that main had added since the fork
point. Torch broke live.

Algorithm (pure function `reverted_lines`, shared by the CI check, the local
pre-push tool in tools/clobber-check/, and the git_merge.py merge helper):
    main_added = lines(MAIN) - lines(BASE)  # main-side lines added since the fork
    reverted   = main_added - lines(HEAD)   # ...that the branch version lacks

Only non-blank lines count. Because comparison is on line TEXT (set
difference), a line the branch moved elsewhere in the file still exists in
HEAD and never flags: moves and legit refactors do not trip the guard.
A branch edit that touches a pre-fork line is not flagged either (the line
was never main-added). Binary files are skipped.

Explicit escapes (silence is refusal):
  * the PR carries the label "owner-approved-revert", or
  * the PR body has a "## Reverts" section naming every offending file path
    in backticks (per the >20-line callout rule: deletions must be intentional
    and called out in the PR body).

Usage in CI:
    BASE_SHA=<fork point> HEAD_SHA=<pr head> MAIN_SHA=<main tip> \
        python3 .github/scripts/clobber_guard.py      # reads GITHUB_EVENT_PATH
Library use:
    check_files(base, main, head, body, labels) -> {path: {offending lines}}
"""
import json
import os
import re
import subprocess
import sys

REVERT_LABEL = "owner-approved-revert"


def text_lines(data):
    """Line texts of a file, or None for binary. Blank lines are ignored."""
    if data is None:
        return set()
    if b"\x00" in data:
        return None  # binary: not line-diffable, skip
    return {ln for ln in data.decode("utf-8", "replace").splitlines()
            if ln.strip()}


def reverted_lines(base_b, main_b, head_b):
    """Main-side lines added after BASE that are absent from HEAD.

    Returns the set of offending line texts (empty = clean).
    """
    base = text_lines(base_b)
    main = text_lines(main_b)
    head = text_lines(head_b)
    if main is None or head is None or base is None:
        return set()
    main_added = main - base
    return main_added - head


def _norm_heading(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def parse_revert_callout(body):
    """File paths (in backticks) named under a '## Reverts' PR-body section."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    paths, cur = set(), None
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            cur = _norm_heading(m.group(1)).startswith("revert")
            continue
        if cur:
            paths.update(re.findall(r"`([^`\s]+)`", line))
    return {p.strip().lstrip("./") for p in paths}


def check_files(base_files, main_files, head_files, body="", labels=()):
    """Return {path: {offending lines}} for files the branch reverts.

    base_files / main_files / head_files map path -> bytes (or None if the
    file does not exist at that revision). Files deleted by the branch are
    skipped here (the deletion guards own those); files deleted on main are
    skipped too.
    """
    if any(l.lower() == REVERT_LABEL for l in labels):
        return {}
    callout = parse_revert_callout(body)
    bad = {}
    for path, head_b in head_files.items():
        if head_b is None:
            continue  # deleted by branch: deletion-guard territory
        if main_files.get(path) is None:
            continue  # deleted on main: not our failure mode
        if path in callout:
            continue  # explicitly called out in the PR body
        off = reverted_lines(base_files.get(path), main_files.get(path), head_b)
        if off:
            bad[path] = off
    return bad


def _git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main():
    base_sha = os.environ["BASE_SHA"]
    head_sha = os.environ["HEAD_SHA"]
    main_sha = os.environ["MAIN_SHA"]
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        ev = json.load(f)
    pr = ev["pull_request"]
    body = pr.get("body") or ""
    labels = [l["name"] for l in pr.get("labels", [])]

    diff = subprocess.run(
        ["git", "diff", "--no-renames", "--name-only", "-z",
         base_sha, head_sha],
        capture_output=True, check=True, text=True).stdout
    paths = [p for p in diff.split("\x00") if p]

    base_files = {p: _git_show(base_sha, p) for p in paths}
    main_files = {p: _git_show(main_sha, p) for p in paths}
    head_files = {p: _git_show(head_sha, p) for p in paths}

    bad = check_files(base_files, main_files, head_files, body, labels)
    if not bad:
        print("Clobber guard passed: no main-side lines reverted.")
        return 0
    print("CLOBBER GUARD FAILED: this PR deletes lines main added after "
          "the PR's base commit (stale-base full-file overwrite pattern).")
    print("Re-sync the flagged files from main and re-apply your edits "
          "surgically, or call out each deletion in a '## Reverts' PR-body "
          "section / add the 'owner-approved-revert' label.")
    for path, lines in sorted(bad.items()):
        print(f"::error file={path}::reverts {len(lines)} main-side line(s); "
              f"e.g. {sorted(lines)[0][:120]!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
