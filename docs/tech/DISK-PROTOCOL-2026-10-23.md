# Disk Cleanup Protocol — Standing Practice

**Created:** 2026-10-23
**User directive:** "make sure you're doing disc cleanup as we work and pushing whatever to the repo and getting it cleaned off disc. 100% to the repo by exact."

## The Rule

As work completes:
1. **PUSH** to repo (feature branch + PR, 6-section body, merge when green)
2. **VERIFY** byte-exact (compare SHA256 checksums: local file vs repo blob)
3. **DELETE** local copy only after verification confirms match

**Never delete before verifying. Never verify after deleting.**

## Never Touch

- `~/workspace/tools/` — toolchain installs (Ghidra, DepotDownloader, etc.)
- `~/workspace/bible/` (17GB) — active work
- `~/workspace/western-heart/` (16GB) — active work
- `~/workspace/ashlane/` (8.7GB) — active work
- `~/workspace/originalize/` (6.1GB) — active work
- `/tmp/cjx/` — user's Cape Jones scratch (THEY clear it, not us)
- Any active extraction work (ISO files not yet on release)

## Safe to Delete (After Verification)

- Stale working copies (`fix3/`, `fix2/`, etc.) — snapshots from completed fix sessions
- Byte-exact duplicates (verify with `md5sum` or `sha256sum` first)
- Build artifacts (`__pycache__/`, `.pyc`, temp files)
- `/tmp/` scratch (512MB tmpfs, fills fast — clean regularly)
- Browser download caches (after confirming sources are archived)

## Large Files (>100MB)

- **Do NOT** push via git directly (blob API 502s on ~110MB+ base64)
- Compress with meshopt first (PR #747 pattern: 54MB→21MB)
- Or upload to GitHub Releases (for ISOs, large archives)
- Raw game files → user's PRIVATE repo, never public western-heart

## Verification Commands

```bash
# Local checksum
sha256sum <file>

# Compare two local files
md5sum file1 file2  # identical output = identical files

# Verify repo blob matches local (via API)
# 1. Get blob SHA from branch
# 2. Download and compare checksums
```

## Cleanup Checklist (Per Session)

- [ ] `df -h` — check disk usage
- [ ] Identify large dirs with `du -sh ~/workspace/*/`
- [ ] For completed work: push → verify → delete
- [ ] Clean `/tmp/` scratch
- [ ] Update this doc if new patterns emerge

## History

- 2026-10-23: Initial cleanup freed ~32GB (fix3/ 172GB→0, fix2/lily duplicate 2.6GB). Disk 94%→64%.
- PR #904: 7 missing files from fix3 pushed (1 research doc + 6 proof renders).
