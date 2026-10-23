#!/usr/bin/env python3
"""Pre-push clobber check: run the clobber-guard revert check on your LOCAL
files BEFORE pushing, so a stale full-file copy never becomes a PR.

Why this exists instead of a git pre-push hook: pushes from this VM go
through the GitHub Git Database API (SSH/HTTPS git push is blocked), so no
git hook ever fires. This script IS the hook for the data-API flow — run it
by hand (or wrap it in your push helper) before every push.

What it does: for each file you are about to push, it fetches that file's
bytes at BASE (the main SHA you synced from) and at MAIN (current main tip,
fetched live) through the GitHub API, and runs the same `reverted_lines`
algorithm as .github/scripts/clobber_guard.py: lines main added after your
sync point that your local copy lacks = stale-clobber = REFUSED.

Usage:
    # 1. Note the SHA you synced from (your push helper prints it, e.g.
    #    gh_push.py prints "base main = <sha>").
    # 2. From the repo root, before pushing:
    python3 tools/clobber-check/clobber_check.py --base <sync-sha> <file> [<file> ...]
    #    Exit 0 = clean, safe to push. Exit 1 = REFUSED (reason printed).
    # 3. If refused: re-sync the flagged files from main, re-apply your edits
    #    SURGICALLY on the fresh copies, and re-run this check.

    # Current main tip is used as MAIN by default; override with --main <sha>.

Credential: on this VM it uses the custom.github_pat connector's secure
credential flow (same as github_api.py); anywhere else, set GH_TOKEN.

Installation: nothing to install. Run it from the repo root before every
data-API push. To make it unavoidable, call it from your push wrapper
script before it creates any blobs.
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))
from clobber_guard import reverted_lines  # noqa: E402

API = "https://api.github.com"
OWNER = "mhvnsnt"
REPO = "western-heart"


class CheckRefused(Exception):
    pass


def _auth_headers():
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "DoggByte-clobber-check"}
    # VM path: surrogate credential injected for api.github.com only.
    try:
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import add_surrogate_to_request
        return headers, ("surrogate", add_surrogate_to_request)
    except Exception:
        pass
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        return headers, ("token", None)
    raise CheckRefused("no credential: on this VM the custom.github_pat "
                       "connector must be available; elsewhere set GH_TOKEN")


def _authed_get(url, headers, auth):
    req = urllib.request.Request(url, headers=headers, method="GET")
    if auth[0] == "surrogate":
        auth[1](req, "custom.github_pat", allowed_hosts=["api.github.com"])
    try:
        with urllib.request.build_opener().open(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise CheckRefused(f"API GET {url.split('api.github.com/')[-1][:60]} "
                           f"-> HTTP {e.code}")


def api_get_blob_bytes(ref_sha, path, headers, auth):
    d = _authed_get(
        f"{API}/repos/{OWNER}/{REPO}/contents/{path}?ref={ref_sha}",
        headers, auth)
    if d is None:
        return None
    if not isinstance(d, dict) or d.get("type") != "file":
        raise CheckRefused(f"{path}: not a file at {ref_sha[:8]}")
    content = d.get("content") or ""
    if d.get("encoding") == "base64":
        return base64.b64decode(content)
    return content.encode()


def main(argv):
    ap = argparse.ArgumentParser(
        description="Pre-push clobber check (see header for the why/how).")
    ap.add_argument("--base", required=True,
                    help="main SHA you synced your local copies from")
    ap.add_argument("--main", default=None,
                    help="main SHA to check against (default: current tip)")
    ap.add_argument("files", nargs="+", help="repo-relative paths to push")
    a = ap.parse_args(argv)

    headers, auth = _auth_headers()
    if a.main:
        main_sha = a.main
    else:
        ref = _authed_get(f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/main",
                          headers, auth)
        main_sha = ref["object"]["sha"]
    print(f"base (your sync point) = {a.base[:8]}")
    print(f"main (live tip)         = {main_sha[:8]}")
    if a.base == main_sha:
        print("base == main tip: nothing main-side could have been added; "
              "still checking local edits are intentional.")

    bad = {}
    for path in a.files:
        local = os.path.join(REPO_ROOT, path)
        if not os.path.isfile(local):
            raise CheckRefused(f"local file not found: {path}")
        with open(local, "rb") as fh:
            local_b = fh.read()
        base_b = api_get_blob_bytes(a.base, path, headers, auth)
        if base_b is None:
            print(f"  NEW-FILE (no base copy): {path}")
            continue
        main_b = api_get_blob_bytes(main_sha, path, headers, auth)
        if main_b is None:
            print(f"  note: {path} was deleted on main after your base; "
                  f"pushing it re-adds the file (deletion guards will judge)")
            continue
        off = reverted_lines(base_b, main_b, local_b)
        if off:
            bad[path] = off
        else:
            print(f"  clean: {path}")

    if not bad:
        print("PRE-PUSH CHECK PASSED: no stale-clobber in these files.")
        return 0
    print("PRE-PUSH CHECK REFUSED: your local cop(ies) lack lines main added "
          "after your sync point (stale-base full-file overwrite pattern).")
    print("Fix: re-sync each flagged file from main and re-apply your edits "
          "surgically, then re-run this check.")
    for path, off in sorted(bad.items()):
        print(f"  {path}: {len(off)} main-side line(s) missing, e.g. "
              f"{sorted(off)[0][:120]!r}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except CheckRefused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(1)
