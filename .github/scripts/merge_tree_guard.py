#!/usr/bin/env python3
"""merge-tree-guard: fail when a merge commit pushed to main drops files that
main had but the merged PR never deleted.

Catches the PR #974 failure mode (2026-10-23): the PR head was clean (0
deletions, all PR-time CI green), but the merge commit was constructed from
the stale branch tree instead of a real 3-way merge, silently dropping 150
files main had gained since the fork point. No PR-time guard can catch that --
the damage is created after checks pass, at merge-commit construction.

For each merge commit M in before..after (first-parent):
    P1 = first parent (main side)
    Pi = other parents (branch sides)
    B_i = merge-base(P1, Pi)          (the PR's fork point)
    D1 = files deleted between P1 and M      (git diff --diff-filter=D P1 M)
    D2 = union over i of files deleted between B_i and Pi
         (the PR's own deletions)
    VIOLATION = D1 - D2
Fail when VIOLATION is non-empty: those are files the merge dropped that the
PR never deleted.

Degenerate case (explicit loud message): a merge commit whose tree is
byte-identical to the branch side's tree while main added files after the
fork point -- i.e. not a real 3-way merge at all.

Escape hatch: if the merged PR carries the "owner-approved-deletion" label,
the merge commit is skipped (labels looked up via the commits API, the same
way deletion-guard.yml does for push events).

Env: BEFORE_SHA, AFTER_SHA, REPO (owner/repo), GH_TOKEN (for label lookup).
Exit 0 = clean, 1 = violation found.
"""
import os
import subprocess
import sys

OWNER_LABEL = "owner-approved-deletion"


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo,
                          capture_output=True, text=True)


def is_merge_commit(repo, sha):
    return len(git(repo, "rev-list", "--parents", "-n", "1",
                   sha).stdout.split()) > 2


def parents(repo, sha):
    return git(repo, "rev-list", "--parents", "-n", "1",
               sha).stdout.split()[1:]


def merge_commits_in_range(repo, before, after):
    r = git(repo, "rev-list", "--first-parent", "--merges",
            f"{before}..{after}")
    if r.returncode != 0:
        print(f"::warning::rev-list failed: {r.stderr.strip()}")
        return []
    return [l for l in r.stdout.splitlines() if l.strip()]


def merge_base(repo, a, b):
    r = git(repo, "merge-base", a, b)
    return r.stdout.strip() if r.returncode == 0 else None


def deleted_files(repo, a, b):
    r = git(repo, "diff", "--no-renames", "--diff-filter=D",
            "--name-only", a, b)
    return set(filter(None, r.stdout.splitlines()))


def added_files(repo, a, b):
    r = git(repo, "diff", "--no-renames", "--diff-filter=A",
            "--name-only", a, b)
    return set(filter(None, r.stdout.splitlines()))


def tree_sha(repo, rev):
    return git(repo, "rev-parse", f"{rev}^{{tree}}").stdout.strip()


def files_in_tree(repo, rev):
    r = git(repo, "ls-tree", "-r", "--name-only", rev)
    return set(filter(None, r.stdout.splitlines()))


def pr_labels(repo_path, sha, repo_slug, token):
    """Label names on PRs associated with a commit (commits API)."""
    env = dict(os.environ, GH_TOKEN=token)
    r = subprocess.run(
        ["gh", "api", f"repos/{repo_slug}/commits/{sha}/pulls",
         "--jq", "[.[].labels[].name]"],
        cwd=repo_path, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"::warning::label lookup failed for {sha[:8]}: "
              f"{r.stderr.strip()[:200]}")
        return set()
    try:
        import json
        return set(json.loads(r.stdout or "[]"))
    except Exception:
        return set()


def check_merge_commit(repo, sha, label_lookup):
    """Return (violations, notes). violations = files the merge dropped that
    the PR never deleted. Empty list = clean (or skipped)."""
    ps = parents(repo, sha)
    if len(ps) < 2:
        return [], [f"{sha[:8]}: not a merge commit, skipped"]
    p1, branches = ps[0], ps[1:]

    labels = label_lookup(sha)
    if OWNER_LABEL in labels:
        return [], [f"{sha[:8]}: skipped ({OWNER_LABEL} label)"]

    d1 = deleted_files(repo, p1, sha)
    d2 = set()
    bases = {}
    for p2 in branches:
        b = merge_base(repo, p1, p2)
        if b is None:
            print(f"::warning::{sha[:8]}: no merge-base for parent "
                  f"{p2[:8]}; its deletions unverifiable")
            continue
        bases[p2] = b
        d2 |= deleted_files(repo, b, p2)

    violations = sorted(d1 - d2)

    # Degenerate fake merge: merge tree == branch tree while main added files
    # after the fork point that are missing from the merge. (Already covered
    # by the D1/D2 check; this just makes it loud.)
    notes = []
    tree_m = tree_sha(repo, sha)
    in_m = None
    for p2 in branches:
        if tree_m and tree_m == tree_sha(repo, p2):
            b = bases.get(p2)
            if b is None:
                continue
            main_added = added_files(repo, b, p1)
            if in_m is None:
                in_m = files_in_tree(repo, sha)
            dropped = sorted(main_added - in_m)
            if dropped:
                notes.append(
                    f"{sha[:8]}: FAKE MERGE -- merge tree is byte-identical "
                    f"to branch tree {p2[:8]}; not a real 3-way merge. "
                    f"{len(dropped)} file(s) main added after the fork are "
                    f"missing from the merge.")
    return violations, notes


def main():
    before = os.environ.get("BEFORE_SHA", "")
    after = os.environ.get("AFTER_SHA", "")
    repo_slug = os.environ.get("REPO", "")
    token = os.environ.get("GH_TOKEN", "")
    repo = os.getcwd()

    if not before or before == "0" * 40:
        print("No before SHA (new ref); skipping.")
        return 0
    if not after:
        print("No after SHA; skipping.")
        return 0

    merges = merge_commits_in_range(repo, before, after)
    print(f"Merge commits in {before[:8]}..{after[:8]}: {len(merges)}")
    if not merges:
        print("No merge commits; OK.")
        return 0

    def label_lookup(sha):
        if not (repo_slug and token):
            return set()
        return pr_labels(repo, sha, repo_slug, token)

    failed = False
    for m in merges:
        violations, notes = check_merge_commit(repo, m, label_lookup)
        for n in notes:
            print(n)
        if violations:
            failed = True
            print(f"::error::Merge {m} dropped {len(violations)} file(s) "
                  f"that main had but the merged PR never deleted:")
            for f in violations:
                print(f"  - {f}")
    if failed:
        print("::error::merge-tree-guard FAILED: fake/stale-tree merge "
              "detected. Revert the merge and re-land with a real 3-way "
              "merge that keeps both sides.")
        return 1
    print("merge-tree-guard OK: no dropped files in merged range.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
