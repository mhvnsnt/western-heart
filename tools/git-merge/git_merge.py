#!/usr/bin/env python3
"""Merge a GitHub PR as a real merge commit via the Git Database API.

Why this exists: on machines where SSH to github.com is blocked and the
merge REST endpoint is unusable with the available credential, this still
merges cleanly. It performs a genuine 3-way merge:

  1. Verifies the PR is open, not a draft, mergeable_state == 'clean'.
  2. Verifies CI check-runs on the head SHA: at least one ran, none failed.
  3. For every file the PR touches, 3-way merges base/main/branch with
     `git merge-file`. Any conflict ABORTS the whole merge.
  4. Builds the merged tree on top of main's CURRENT tree (main-only files
     are untouched), creates a merge commit with parents [main, branch],
     and fast-forward-updates the base ref. If the base moved underneath us,
     the ref update fails safely and nothing changes.
  5. Verifies the PR now reads merged.

Auth: uses the custom.github_pat connector credential through Muse's
dynamic credential surrogate (no keys in this file, in args, or in env).
Needs /opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py
on the machine running it.

Usage:
    git_merge.py <PR> [--yes] [--owner o] [--repo r] [--base main]
Without --yes it dry-runs: prints the plan and changes nothing.

Exit codes: 0 = merged (or dry-run OK), 1 = refused/aborted, 2 = usage error.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

_CANDIDATE_HELPERS = [
    "/opt/muse/skills/custom-connector-setup/bin",
    os.path.expanduser("~/workspace/custom-skills/custom-connector-setup/bin"),
]
for _p in _CANDIDATE_HELPERS:
    if os.path.isdir(_p):
        sys.path.insert(0, _p)
        break
try:
    from dynamic_credentials import add_surrogate_to_request
except ImportError:
    sys.exit("git_merge.py needs dynamic_credentials.py from the "
             "custom-connector-setup skill; not found.")

CONNECTION = "custom.github_pat"
ALLOWED_HOSTS = ["api.github.com"]
API = "https://api.github.com"
BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}


class MergeRefused(Exception):
    pass


def api(method, path, data=None):
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "DoggByte-git-merge-helper"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    add_surrogate_to_request(req, CONNECTION, allowed_hosts=ALLOWED_HOSTS)
    try:
        with urllib.request.build_opener().open(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", "replace")
        raise MergeRefused(f"API {method} {path} -> HTTP {e.code}: {payload[:300]}")


def get_pr(owner, repo, n):
    pr = api("GET", f"/repos/{owner}/{repo}/pulls/{n}")
    if pr.get("state") != "open":
        raise MergeRefused(f"PR #{n} is not open (state={pr.get('state')})")
    if pr.get("draft"):
        raise MergeRefused(f"PR #{n} is a draft; never merge drafts")
    ms = pr.get("mergeable_state")
    for _ in range(6):
        if ms not in (None, "unknown"):
            break
        time.sleep(5)
        pr = api("GET", f"/repos/{owner}/{repo}/pulls/{n}")
        ms = pr.get("mergeable_state")
    if ms != "clean":
        raise MergeRefused(f"PR #{n} mergeable_state={ms!r}, need 'clean'")
    return pr


def check_ci(owner, repo, pr):
    sha = pr["head"]["sha"]
    runs = api("GET", f"/repos/{owner}/{repo}/commits/{sha}/check-runs")
    check_runs = runs.get("check_runs", [])
    if not check_runs:
        raise MergeRefused(f"no CI check-runs found for head {sha[:8]}; refusing")
    # Superseded runs linger: judge only the latest run per check name.
    latest = {}
    for r in sorted(check_runs, key=lambda r: r.get("id", 0), reverse=True):
        latest.setdefault(r["name"], r)
    check_runs = list(latest.values())
    bad = [(r["name"], r.get("conclusion")) for r in check_runs
           if r.get("conclusion") in BAD_CONCLUSIONS]
    if bad:
        raise MergeRefused(f"failing CI checks: {bad}")
    pending = [r["name"] for r in check_runs if r.get("status") != "completed"]
    if pending:
        raise MergeRefused(f"CI still running: {pending}")
    return [(r["name"], r.get("conclusion")) for r in check_runs]


def blob_bytes(owner, repo, sha):
    b = api("GET", f"/repos/{owner}/{repo}/git/blobs/{sha}")
    return base64.b64decode(b["content"])


def tree_entries(owner, repo, tree_sha):
    t = api("GET", f"/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1")
    return {e["path"]: e for e in t.get("tree", []) if e["type"] == "blob"}


def three_way_merge(path, base_b, main_b, branch_b):
    """Return (merged bytes, description); raise MergeRefused on conflict."""
    if main_b == base_b:
        return branch_b, "branch-only change"
    if branch_b == base_b:
        return main_b, "main-only change (unexpected for PR file)"
    for b in (base_b, main_b, branch_b):
        if b is not None:
            try:
                b.decode("utf-8")
            except UnicodeDecodeError:
                raise MergeRefused(
                    f"{path}: binary file changed on both sides; refusing")
    if base_b is None:
        base_b, main_b, branch_b = b"", main_b or b"", branch_b or b""
    with tempfile.TemporaryDirectory() as td:
        fb, fm, fo = (f"{td}/base", f"{td}/main", f"{td}/other")
        open(fb, "wb").write(base_b)
        open(fm, "wb").write(main_b)
        open(fo, "wb").write(branch_b)
        r = subprocess.run(["git", "merge-file", "-p", fm, fb, fo],
                           capture_output=True, timeout=60)
        if r.returncode not in (0, 1):
            raise MergeRefused(f"{path}: git merge-file failed: "
                               f"{r.stderr.decode()[:200]}")
        if r.returncode == 1 or b"<<<<<<<" in r.stdout:
            raise MergeRefused(f"{path}: merge CONFLICT between base branch "
                               f"and PR branch; refusing to clobber either side")
        return r.stdout, "3-way merged (both sides changed)"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("pr", help="PR number to merge")
    ap.add_argument("--yes", action="store_true", help="execute the merge")
    ap.add_argument("--owner", default="mhvnsnt")
    ap.add_argument("--repo", default="western-heart")
    ap.add_argument("--base", default="main", help="base branch")
    a = ap.parse_args(argv)
    if not a.pr.isdigit():
        ap.print_usage()
        return 2
    n, owner, repo, base = a.pr, a.owner, a.repo, a.base

    pr = get_pr(owner, repo, n)
    ci = check_ci(owner, repo, pr)
    branch = pr["head"]["ref"]
    branch_sha = pr["head"]["sha"]
    title = pr["title"]

    cmp = api("GET", f"/repos/{owner}/{repo}/compare/{base}...{branch}")
    if cmp.get("status") not in ("ahead", "diverged"):
        raise MergeRefused(f"compare status={cmp.get('status')!r}; "
                           f"nothing to merge or branch behind")
    merge_base = cmp["merge_base_commit"]["sha"]
    files = cmp.get("files", [])
    if not files:
        raise MergeRefused("PR touches no files")

    base_ref = api("GET", f"/repos/{owner}/{repo}/git/refs/heads/{base}")
    base_sha = base_ref["object"]["sha"]
    base_commit = api("GET", f"/repos/{owner}/{repo}/git/commits/{base_sha}")
    base_tree = base_commit["tree"]["sha"]
    branch_entries = tree_entries(owner, repo,
        api("GET", f"/repos/{owner}/{repo}/git/commits/{branch_sha}")["tree"]["sha"])
    merge_base_entries = tree_entries(owner, repo,
        api("GET", f"/repos/{owner}/{repo}/git/commits/{merge_base}")["tree"]["sha"])
    base_branch_entries = tree_entries(owner, repo, base_tree)

    plan = []
    new_blobs = {}
    for f in files:
        path = f["filename"]
        status = f["status"]
        if status == "removed":
            plan.append((path, "deleted by PR"))
            new_blobs[path] = None
            continue
        b_blob = branch_entries.get(path, {}).get("sha")
        if not b_blob:
            raise MergeRefused(f"{path}: in PR diff but missing from branch tree")
        base_blob = merge_base_entries.get(path, {}).get("sha")
        main_blob = base_branch_entries.get(path, {}).get("sha")
        base_b = blob_bytes(owner, repo, base_blob) if base_blob else None
        main_b = blob_bytes(owner, repo, main_blob) if main_blob else None
        branch_b = blob_bytes(owner, repo, b_blob)
        merged, how = three_way_merge(path, base_b, main_b, branch_b)
        plan.append((path, how))
        if merged != branch_b or how != "branch-only change":
            nb = api("POST", f"/repos/{owner}/{repo}/git/blobs",
                     {"content": base64.b64encode(merged).decode(),
                      "encoding": "base64"})
            new_blobs[path] = nb["sha"]
        else:
            new_blobs[path] = b_blob

    print(f"PR #{n}: {title}")
    print(f"branch {branch} ({branch_sha[:8]}) -> {base} ({base_sha[:8]})")
    print(f"CI: {len(ci)} checks green: {[c[0] for c in ci]}")
    print("files:")
    for path, how in plan:
        print(f"  {how:38s} {path}")
    if not a.yes:
        print("dry run: no changes made (re-run with --yes to merge)")
        return 0

    fresh = api("GET",
                f"/repos/{owner}/{repo}/git/refs/heads/{base}")["object"]["sha"]
    if fresh != base_sha:
        raise MergeRefused(f"{base} moved during merge ({base_sha[:8]} -> "
                           f"{fresh[:8]}); aborting safely, re-run")

    tree = [{"path": p, "mode": "100644", "type": "blob", "sha": s}
            for p, s in new_blobs.items() if s is not None]
    tree += [{"path": p, "mode": "100644", "type": "blob", "sha": None}
             for p, s in new_blobs.items() if s is None]
    new_tree = api("POST", f"/repos/{owner}/{repo}/git/trees",
                   {"base_tree": base_tree, "tree": tree})["sha"]

    me = api("GET", "/user")
    ident = {"name": me["login"],
             "email": f"{me['id']}+{me['login']}@users.noreply.github.com"}
    msg = (f"Merge pull request #{n} from {owner}/{branch}\n\n{title}\n\n"
           f"Merged by DoggByte git_merge.py (3-way, no conflicts, CI green).")
    commit = api("POST", f"/repos/{owner}/{repo}/git/commits",
                 {"message": msg, "tree": new_tree,
                  "parents": [base_sha, branch_sha],
                  "author": ident, "committer": ident})
    try:
        api("PATCH", f"/repos/{owner}/{repo}/git/refs/heads/{base}",
            {"sha": commit["sha"], "force": False})
    except MergeRefused as e:
        raise MergeRefused(f"{base} ref update failed (safe, nothing pushed): {e}")

    pr2 = api("GET", f"/repos/{owner}/{repo}/pulls/{n}")
    if not pr2.get("merged"):
        raise MergeRefused("ref updated but PR does not show merged; "
                           "investigate before continuing")
    print(f"MERGED: {commit['sha'][:8]}  PR #{n} closed as merged.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except MergeRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
