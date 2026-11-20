# autosave.sh scratch-repo test (2026-10-23 16:07 CDT)
1. Dirty tree on main + a deleted file → moved to `claude/autosave-20261023-160733`, committed `wip(autosave)`, plain push OK; the deletion was NOT committed.
2. Staged GitHub token → gitleaks `leaks found: 1` → commit aborted, nothing pushed.
3. 105 MB non-LFS file → skipped, rest committed + pushed (0.9 s total).
4. PostToolUse within 10 min → debounced, no commit.
