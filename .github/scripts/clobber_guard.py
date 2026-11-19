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

Performance note (2026-11-19, PRs #1755/#1758/#1759): the guard used to
fetch every changed file's blob at all three revisions before deciding
anything. On a binary-heavy PR (5,780 files, mostly .npy) that is ~17k
lazy blob fetches, which blew the 25-minute job timeout. PR #1756 skipped
known-binary extensions before fetching; PR #1758 batched the reads
through one `git cat-file --batch` per revision. That saved subprocess
spawns but NOT the fetches: in the CI checkout (`filter: blob:none`) each
missing blob still negotiates separately, and the batch reads left the
#1759 guard running past 8 minutes on a 7k-file text diff. main() now
works from `git diff` output instead: `git diff` bulk-fetches every blob
it needs in one or two promisor negotiations (verified: the 12,409-file
PR #1759 diff in a fresh partial clone took 2 fetches), and the check
only needs the files main actually changed — additions(base→main) ∩
deletions(main→head). When main hasn't moved past the fork point the
guard passes without reading anything. The blob-based check_files() /
_read_revision_files() remain as the library API and as the fallback for
a diff header no filename parser can match.

Diff-path note: the diff-based check counts line occurrences where the
set-based check does not — a line main added twice that the branch keeps
once now flags. In practice main rarely adds the same line twice to one
file, and the Reverts callout covers the exception.
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


def _diff_names(rev_a, rev_b, diff_filter=None, cwd=None):
    """File paths changed between two revisions (tree-only, no blobs)."""
    args = ["git", "diff", "--no-renames", "--name-only", "-z"]
    if diff_filter:
        args.append(f"--diff-filter={diff_filter}")
    args += [rev_a, rev_b]
    r = subprocess.run(args, capture_output=True, check=True, cwd=cwd)
    return [p for p in r.stdout.decode().split("\x00") if p]


class _UnparseableDiff(Exception):
    """A diff header could not be matched to a file; fall back to blobs."""


def _parse_diff_header(line, known):
    """Path for a `diff --git a/X b/Y` header line (bytes, no trailing LF).

    With --no-renames the a/ and b/ sides name the same path, so the
    header is `diff --git a/P b/P` and P is recovered by length: the part
    after `diff --git a/` is P + " b/" + P. Raises _UnparseableDiff when
    the header does not fit that shape or names a path outside `known`.
    """
    prefix = b"diff --git a/"
    if not line.startswith(prefix):
        raise _UnparseableDiff(repr(line[:80]))
    rest = line[len(prefix):]
    if len(rest) % 2 == 0:  # 2*len(P)+3 is always odd
        raise _UnparseableDiff(repr(line[:80]))
    plen = (len(rest) - 3) // 2
    path = rest[:plen]
    if rest[plen:] != b" b/" + path:
        raise _UnparseableDiff(repr(line[:80]))
    text = path.decode("utf-8", "replace")
    if text not in known:
        raise _UnparseableDiff(repr(line[:80]))
    return text


def _parse_diff_output(lines, known, collect_added=True,
                       collect_deleted=True):
    """Parse `git diff -U0` output (bytes lines) into per-file line sets.

    Returns ({path: added lines}, {path: deleted lines}). Blank lines are
    ignored, matching text_lines(). A trailing CR is stripped, so CRLF
    files compare equal to their LF form (splitlines() does the same).
    Raises _UnparseableDiff on a header that cannot be matched.
    """
    added, deleted = {}, {}
    current = None
    for raw in lines:
        line = raw.rstrip(b"\n")
        if line.startswith(b"diff --git "):
            current = _parse_diff_header(line, known)
            added.setdefault(current, set())
            deleted.setdefault(current, set())
        elif current is None:
            continue
        elif line.startswith(b"+++ ") or line.startswith(b"--- "):
            continue  # file header lines, not content
        elif line.startswith(b"+") and collect_added:
            text = line[1:].rstrip(b"\r").decode("utf-8", "replace")
            if text.strip():
                added[current].add(text)
        elif line.startswith(b"-") and collect_deleted:
            text = line[1:].rstrip(b"\r").decode("utf-8", "replace")
            if text.strip():
                deleted[current].add(text)
    return added, deleted


def _diff_line_sets(rev_a, rev_b, paths, collect_added=True,
                    collect_deleted=True, chunk=2000, cwd=None):
    """Per-file added/deleted line sets between two revisions, via git diff.

    `git diff` bulk-fetches every blob it needs in one or two promisor
    negotiations (verified: the 12,409-file PR #1759 diff in a fresh
    partial clone took 2 fetches), where per-file reads negotiate per
    blob. Paths are chunked to stay under argv limits.
    """
    known = set(paths)
    added, deleted = {}, {}
    for i in range(0, len(paths), chunk):
        batch = paths[i:i + chunk]
        proc = subprocess.Popen(
            ["git", "-c", "core.quotePath=false", "diff", "--no-renames",
             "-U0", rev_a, rev_b, "--"] + batch,
            stdout=subprocess.PIPE, cwd=cwd)
        a, d = _parse_diff_output(proc.stdout, known, collect_added,
                                  collect_deleted)
        proc.wait()
        if proc.returncode not in (0, 1):  # 1 = differences found
            raise subprocess.CalledProcessError(proc.returncode, "git diff")
        for p, s in a.items():
            added.setdefault(p, set()).update(s)
        for p, s in d.items():
            deleted.setdefault(p, set()).update(s)
    return added, deleted


def main():
    base_sha = os.environ["BASE_SHA"]
    head_sha = os.environ["HEAD_SHA"]
    main_sha = os.environ["MAIN_SHA"]
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        ev = json.load(f)
    pr = ev["pull_request"]
    body = pr.get("body") or ""
    labels = [l["name"] for l in pr.get("labels", [])]
    if any(l.lower() == REVERT_LABEL for l in labels):
        print("Clobber guard passed: owner-approved-revert label present.")
        return 0

    # Files main changed after the fork point (tree-only: no blob fetch).
    # When main hasn't moved, there are no main-added lines to revert.
    # Only files the BRANCH also changed can be reverts: a file the branch
    # never touched keeps main's version at merge, so flagging it would
    # fail every PR open while main advances. (The pre-diff guard had the
    # same restriction — it only read files in the branch's diff.)
    main_changed = {p for p in _diff_names(base_sha, main_sha)
                    if not is_binary_path(p)}
    branch_changed = set(_diff_names(base_sha, head_sha))
    changed = sorted(main_changed & branch_changed)
    if not changed:
        print("Clobber guard passed: no main-side lines reverted.")
        return 0
    # Files absent at head (deleted by the branch, or added on main after
    # the fork so the branch never had them): the merge keeps main's
    # version, so they cannot be reverts — the same skip check_files()
    # applies to head=None / main=None.
    deleted_at_head = set(_diff_names(main_sha, head_sha, diff_filter="D"))
    callout = parse_revert_callout(body)
    paths = [p for p in changed
             if p not in deleted_at_head and p not in callout]
    if not paths:
        print("Clobber guard passed: no main-side lines reverted.")
        return 0

    try:
        added, _ = _diff_line_sets(base_sha, main_sha, paths,
                                   collect_deleted=False)
        _, deleted = _diff_line_sets(main_sha, head_sha, paths,
                                     collect_added=False)
        bad = {p: added[p] & deleted.get(p, set()) for p in paths
               if added.get(p) and added[p] & deleted.get(p, set())}
    except _UnparseableDiff as exc:
        # A diff header could not be matched to a file (pathological
        # filename): fall back to the exact blob-based check.
        print(f"::warning::diff header unparseable ({exc}); "
              "falling back to blob reads")
        base_files = _read_revision_files(base_sha, paths)
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
