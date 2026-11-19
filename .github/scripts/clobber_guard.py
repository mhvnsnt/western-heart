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

Performance note (2026-11-19, PR #1755): the guard used to fetch every
changed file's blob at all three revisions before deciding anything. On a
binary-heavy PR (5,780 files, mostly .npy) that is ~17k lazy blob fetches,
which blew the 25-minute job timeout. Known-binary extensions are now
skipped before fetching (they could never flag: text_lines() skips binary
content anyway), and main's blobs are reused when main == base. The remaining
reads go through one `git cat-file --batch` process per revision
(_read_revision_files): one `git show` per file means one subprocess and one
lazy-fetch negotiation per file, while a single batch process reads all blobs
locally — so a 14k-file text diff (the No Mercy model re-extraction, PR
#1759) costs three subprocesses instead of ~28k. (`git archive` was
considered and rejected: in a partial clone it triggers a promisor fetch
that hangs in this environment, and it needs an ls-tree pre-pass because it
fails on missing paths; cat-file reports missing files itself.)
"""
import json
import os
import re
import subprocess
import sys

REVERT_LABEL = "owner-approved-revert"

# Extensions that are always binary in this repo. Files with these
# extensions are skipped BEFORE any blob fetch (see the performance note
# above). A binary file with a text extension is still caught by
# text_lines() after fetching; a text file with one of these extensions
# would be wrongly skipped, so keep this list to formats that are never
# plain text. (.obj is Wavefront text here; .gltf/.mtl/.json are text —
# not listed.)
BINARY_EXTS = frozenset({
    ".npy", ".npz", ".bin", ".dat", ".z64", ".n64", ".v64",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tga",
    ".dds", ".exr", ".hdr", ".psd",
    ".glb", ".fbx", ".blend",
    ".mp3", ".wav", ".ogg", ".flac", ".m4a",
    ".mp4", ".mov", ".webm", ".avi",
    ".zip", ".gz", ".bz2", ".xz", ".7z", ".tar", ".rar",
    ".pyc", ".pyo", ".onnx", ".pt", ".pth", ".safetensors",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".pdf", ".exe", ".dll", ".so", ".dylib", ".a", ".o",
})


def is_binary_path(path):
    """True when the path's extension marks it as always-binary."""
    return os.path.splitext(path)[1].lower() in BINARY_EXTS


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


def _read_revision_files(rev, paths, cwd=None):
    """Read many files at one revision through one `git cat-file --batch`.

    One `git show` per file means one subprocess (and one lazy-fetch
    negotiation in a partial clone) per file — ~17k fetches timed the
    job out on PR #1755. A single batch process reads all blobs locally.
    Returns {path: bytes}; files absent at the revision map to None.
    Paths containing a newline can't travel the line-based batch
    protocol, so they fall back to _git_show (vanishingly rare).
    """
    out = {}
    batch_paths = [p for p in paths if "\n" not in p]
    for p in paths:
        if "\n" in p:
            out[p] = _git_show(rev, p)
    if not batch_paths:
        return out
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
    for p in batch_paths:
        proc.stdin.write(f"{rev}:{p}\n".encode())
        proc.stdin.flush()
        header = proc.stdout.readline().decode().rstrip("\n")
        parts = header.split(" ")
        if len(parts) >= 3 and parts[1] == "blob":
            size = int(parts[2])
            out[p] = proc.stdout.read(size)
            proc.stdout.read(1)  # trailing LF after each object's contents
        elif len(parts) >= 3:
            # A tree/commit sits at that path: consume its contents and
            # discard, so the stream stays in sync for the next file.
            size = int(parts[2])
            proc.stdout.read(size)
            proc.stdout.read(1)
            out[p] = None
        else:
            out[p] = None  # "<object> missing": no contents follow
    proc.stdin.close()
    proc.wait()
    return out


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
    # Skip known-binary paths before fetching any blob: they can never
    # carry reverted lines (text_lines() skips them), and fetching them
    # is what times the job out on binary-heavy PRs (see BINARY_EXTS).
    n_skipped = sum(1 for p in paths if is_binary_path(p))
    if n_skipped:
        print(f"Skipping {n_skipped} known-binary file(s) before fetch.")
    paths = [p for p in paths if not is_binary_path(p)]

    base_files = _read_revision_files(base_sha, paths)
    # When main hasn't moved past the fork point, main == base: reuse
    # the blobs instead of fetching them a second time.
    if main_sha == base_sha:
        main_files = dict(base_files)
    else:
        main_files = _read_revision_files(main_sha, paths)
    head_files = _read_revision_files(head_sha, paths)

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
