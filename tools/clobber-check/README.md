# tools/clobber-check — pre-push clobber check

Run the repo's clobber-guard revert check on your **local files before you
push**, so a stale full-file copy never becomes a PR. This is the local half
of the anti-clobber immune system (the other halves: the `clobber-guard` CI
check in `.github/workflows/`, and the revert guard inside
`tools/git-merge/git_merge.py`).

## Why not a git pre-push hook?

Pushes from the crew's VMs go through the GitHub **Git Database API**
(SSH/HTTPS `git push` is blocked), so no git hook ever fires. This script
**is** the hook for the data-API flow: run it by hand — or call it from your
push wrapper — before every push.

## Usage

```bash
# 1. Note the SHA you synced from (your push helper prints it;
#    gh_push.py prints "base main = <sha>").
# 2. From the repo root, BEFORE pushing:
python3 tools/clobber-check/clobber_check.py --base <sync-sha> <file> [<file> ...]

# Exit 0 = clean, safe to push. Exit 1 = REFUSED (reason printed).
```

If it refuses: re-sync each flagged file from main, re-apply your edits
**surgically** on the fresh copies, and re-run the check. That is the law —
see `docs/owner-directives.md` ("ANTI-CLOBBER LAW").

## What it checks

For each file: lines that main added **after your sync point** (`--base`)
that your local copy **lacks** = the stale-base full-file overwrite pattern
(PR #579, 2026-10-22). Same algorithm as
`.github/scripts/clobber_guard.py` (`reverted_lines`), which this script
imports — one source of truth.

Deliberate reverts are allowed but must be explicit: name each file in a
`## Reverts` section of the PR body (paths in backticks), or put the
`owner-approved-revert` label on the PR. The CI check and the merge helper
honor the same escapes.

## Credential

On the crew VM it uses the `custom.github_pat` connector's secure credential
flow; anywhere else, set `GH_TOKEN`.

## Wiring it into your push wrapper

Call it with the file list and the base SHA **before** creating any blobs;
abort the push on non-zero exit. Example (bash):

```bash
python3 tools/clobber-check/clobber_check.py --base "$SYNC_SHA" "$@" \
  || { echo "clobber check failed; push aborted"; exit 1; }
# ... proceed to create blobs / branch / PR
```
