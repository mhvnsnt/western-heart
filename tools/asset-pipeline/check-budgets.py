#!/usr/bin/env python3
"""Western Heart GLB budget check (CI step, no dependencies, no network).

Walks game/, roster/ and customization/ for *.glb files and reports each
file's size plus the total. Exit codes:
  0 — every file within budget (or no GLBs found).
  2 — a file exceeds 100 MB, GitHub's hard push limit: such a file cannot
      land via a normal push at all, so this is a real failure, not a
      taste threshold.
Files over 25 MB only WARN: that is a mobile-load smell (the whole
verified pipeline story is small — a hand stance GLB optimizes
158,884 -> 72,812 bytes, a jungle outpost 1,669,744 -> 680,460 bytes
with tools/asset-pipeline/wh-asset-pipeline.sh), but large roster
models are the owner's call, so CI reports them instead of blocking.

Usage: python3 tools/asset-pipeline/check-budgets.py [repo-root]
"""
import os
import sys

WARN_MB = 25
FAIL_MB = 100
SCAN_DIRS = ("game", "roster", "customization")


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    found = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in (".git", "node_modules")]
            for name in filenames:
                if name.lower().endswith(".glb"):
                    path = os.path.join(dirpath, name)
                    try:
                        found.append((path, os.path.getsize(path)))
                    except OSError as e:
                        print(f"UNREADABLE {path}: {e}")
    found.sort()
    total = sum(size for _, size in found)
    print(f"[asset-budget] {len(found)} GLB files, {total / 1048576:.1f} MB total")
    bad = False
    for path, size in found:
        mb = size / 1048576
        flag = ""
        if mb > FAIL_MB:
            flag = "  <-- OVER 100 MB (GitHub push limit)"
            bad = True
        elif mb > WARN_MB:
            flag = "  <-- over 25 MB (mobile-load warning)"
        print(f"  {mb:8.2f} MB  {path}{flag}")
    if bad:
        print("[asset-budget] FAIL: a GLB exceeds GitHub's 100 MB push limit")
        return 2
    print("[asset-budget] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
