#!/usr/bin/env python3
"""Kaggle API helper for WH -- DOCUMENTATION / CHECK-ONLY BY DEFAULT.

AUTH (verified from Kaggle docs, 2026-10-24):
  - The Kaggle API is NOT unauthenticated. It requires a Kaggle account
    and an API token: Kaggle web -> profile -> Account Settings -> API
    section -> "Create New API Token" downloads kaggle.json. Place it at
    ~/.kaggle/kaggle.json with mode 600 (chmod 600 ~/.kaggle/kaggle.json).
    The official CLI is `pip install kaggle`, then e.g.
    `kaggle datasets list -s "motion capture"`.
  - This script NEVER prints, logs, or transmits the contents of
    kaggle.json. It only checks that the file EXISTS and what its
    permission bits are (via os.stat, reading no bytes of the file).
  - DEFAULT MODE IS CHECK-ONLY: it reports file presence/mode, whether
    the `kaggle` CLI is installed, and the exact commands to run by
    hand. It does NOT sign in, call the Kaggle API, or download anything
    unless you explicitly pass --list, in which case it shells out to
    the official `kaggle` CLI (which reads kaggle.json itself) -- and
    even then it passes no credential on the command line.
  - On this VM on 2026-10-24: ~/.kaggle/kaggle.json EXISTS with mode 600
    and the `kaggle` CLI was NOT installed (no `kaggle` binary found).
    The live --list path was therefore NOT run here; it is provided for
    a machine where the owner has installed the CLI.

WH-relevant public-dataset search terms (run by hand once authenticated):
  motion capture, human pose estimation, fighting game, 3d human mesh,
  animation retargeting, dance motion.

Usage:
  python3 kaggle.py                 # check-only (safe default)
  python3 kaggle.py --list "motion capture"   # explicit live call via official CLI
"""
import argparse, os, shutil, stat, subprocess, sys

KAGGLE_JSON = os.path.expanduser("~/.kaggle/kaggle.json")
SEARCH_TERMS = ["motion capture", "human pose estimation", "fighting game",
                "3d human mesh", "animation"]


def check():
    exists = os.path.exists(KAGGLE_JSON)
    print(f"kaggle.json present: {exists}  (path: {KAGGLE_JSON})")
    if exists:
        mode = stat.S_IMODE(os.stat(KAGGLE_JSON).st_mode)
        print(f"kaggle.json mode: {oct(mode)}"
              f"  {'OK (600)' if mode == 0o600 else 'WARNING: should be 600 -- run: chmod 600 ~/.kaggle/kaggle.json'}")
        print("Contents are NOT read, printed, or transmitted by this script.")
    else:
        print("To create it: Kaggle -> profile -> Account Settings -> API -> "
              "'Create New API Token' -> save as ~/.kaggle/kaggle.json, chmod 600.")
    cli = shutil.which("kaggle")
    print(f"kaggle CLI installed: {bool(cli)}" + (f" ({cli})" if cli else
          " -- install with: pip install kaggle"))
    print("\nWH-relevant searches to run once authenticated:")
    for term in SEARCH_TERMS:
        print(f"  kaggle datasets list -s \"{term}\"")
    print("\nNOTE: check-only mode made no Kaggle API call and no sign-in.")
    return 0 if (exists and cli) else 0  # check mode always 'succeeds' as a report


def live_list(term):
    if not os.path.exists(KAGGLE_JSON):
        print("STOP: ~/.kaggle/kaggle.json not found; refusing live call.", file=sys.stderr)
        return 2
    if not shutil.which("kaggle"):
        print("STOP: `kaggle` CLI not installed; run: pip install kaggle", file=sys.stderr)
        return 2
    print(f"Running official CLI (it reads kaggle.json itself; no credential passed here):")
    print(f"  kaggle datasets list -s {term!r}")
    r = subprocess.run(["kaggle", "datasets", "list", "-s", term])
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", metavar="TERM", help="explicit live call via official kaggle CLI")
    a = ap.parse_args()
    if a.list:
        return live_list(a.list)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
