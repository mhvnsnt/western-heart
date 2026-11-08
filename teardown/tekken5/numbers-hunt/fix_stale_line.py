#!/usr/bin/env python3
"""Fix the stale keyframe-status line in teardown/tekken5/dw-motion-bank.json
via the GitHub git-data API, entirely in memory (workspace quota is full
and /tmp is 100% full of other lanes' work — no local file writes).

Steps: main HEAD -> base tree -> fetch raw file -> verify stale line ->
replace ONLY line 5 -> JSON-parse check -> blob -> tree -> commit ->
compare-check (exactly 1 modified file) -> ref -> PR (do NOT merge).
"""
import base64
import json
import subprocess
import sys
import urllib.request

REPO = "mhvnsnt/western-heart"
PATH = "teardown/tekken5/dw-motion-bank.json"
BRANCH = "fix/dw-motion-bank-stale-line"
CRACK_SHA = "1beffd18f654c1f749b64fe25d2a213d860120c6"

OLD_FRAGMENT = "NOT yet reversed"
NEW_LINE = (' "decode_status": "Structural decode complete (header, record table, '
            'bone table, data section, first-frame float32 values for type-3/11 '
            'bones). Keyframe packing REVERSED (commit 1beffd18): per-joint curves '
            'for all 214 clips, 9,002 keyframes, in dw-motion-curves.json; rotation '
            'R = Rz\\u00b7Ry\\u00b7Rx, LOCAL \\u2014 see DW-DECODE-LOG.md '
            '\\u00a78/\\u00a722.",')

BODY = """## Owner instruction (verbatim quote)

One stale line: dw-motion-bank.json says keyframe packing is "NOT yet reversed" — superseded by the crack; fix the status line to the truth.

## Method the owner specified

Fix the status line in teardown/tekken5/dw-motion-bank.json to the truth: replace the superseded 'NOT yet reversed' wording with the cracked keyframe status (commit 1beffd18, dw-motion-curves.json), changing only that one line and nothing else.

## Method actually used

Fix the status line in teardown/tekken5/dw-motion-bank.json to the truth: replace the superseded 'NOT yet reversed' wording with the cracked keyframe status (commit 1beffd18, dw-motion-curves.json), changing only that one line and nothing else.

## Deviations (none / list, each with owner approval link)

None

## Proof (paths to files, frames, test output)

- `teardown/tekken5/dw-motion-bank.json`
- `teardown/tekken5/dw-motion-curves.json`
- `teardown/tekken5/DW-DECODE-LOG.md`
- `1beffd18f654c1f749b64fe25d2a213d860120c6`

## Self-check: I verified the result against the literal instruction

- [x] I verified the result against the literal instruction: only the decode_status line changed, from the superseded NOT yet reversed wording to the cracked keyframe status, and the file still parses as JSON.
"""


def gh(*args, input_bytes=None):
    r = subprocess.run(["gh", "api"] + list(args),
                       input=input_bytes, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"gh api {' '.join(args)} failed:\n{r.stderr.decode()}")
    return json.loads(r.stdout.decode() or "{}")


def main():
    # 0. Branch must not already exist.
    r = subprocess.run(["gh", "api", f"repos/{REPO}/branches/{BRANCH}"],
                       capture_output=True)
    if r.returncode == 0:
        raise SystemExit(f"ABORT: branch {BRANCH} already exists")
    # 1. Main HEAD + base tree.
    head = gh(f"repos/{REPO}/branches/main")["commit"]["sha"]
    base_tree = gh(f"repos/{REPO}/git/commits/{head}")["tree"]["sha"]
    print(f"main HEAD {head} tree {base_tree}")
    # 2. Fetch current file from main (in memory), verify stale line.
    req = urllib.request.Request(
        f"https://raw.githubusercontent.com/{REPO}/main/{PATH}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        text = resp.read().decode("utf-8")
    lines = text.split("\n")
    assert OLD_FRAGMENT in lines[4], f"line 5 not stale: {lines[4][:120]!r}"
    print(f"stale line confirmed: {lines[4][:100]}...")
    lines[4] = NEW_LINE
    new_text = "\n".join(lines)
    json.loads(new_text)  # must still parse
    print("edited file parses as JSON OK")
    # 3. Blob.
    blob = gh("-X", "POST", f"repos/{REPO}/git/blobs", "--input", "-",
              input_bytes=json.dumps(
                  {"content": base64.b64encode(new_text.encode()).decode(),
                   "encoding": "base64"}).encode())
    print(f"blob sha={blob['sha']}")
    # 4. Tree on top of the base tree (one modified entry).
    tree = gh("-X", "POST", f"repos/{REPO}/git/trees", "--input", "-",
              input_bytes=json.dumps(
                  {"base_tree": base_tree,
                   "tree": [{"path": PATH, "mode": "100644",
                             "type": "blob", "sha": blob["sha"]}]}).encode())
    print(f"tree sha={tree['sha']}")
    # 5. Commit.
    commit = gh("-X", "POST", f"repos/{REPO}/git/commits", "--input", "-",
                input_bytes=json.dumps(
                    {"message": "dw-decode: fix stale keyframe status line in "
                                "dw-motion-bank.json\n\nKeyframe packing was "
                                "reversed in 1beffd18 (214 clips, 9,002 "
                                "keyframes, dw-motion-curves.json); the "
                                "decode_status line still said NOT yet "
                                "reversed. One line changed, nothing else.",
                     "tree": tree["sha"], "parents": [head]}).encode())
    print(f"commit sha={commit['sha']}")
    cmp = gh(f"repos/{REPO}/compare/{head}...{commit['sha']}")
    changed = [(f["filename"], f["status"]) for f in cmp.get("files", [])]
    assert changed == [(PATH, "modified")], f"CHANGED MISMATCH: {changed}"
    assert cmp.get("status") == "ahead", f"compare status: {cmp.get('status')}"
    print(f"compare check OK: 1 modified file, status={cmp['status']}")
    # 6. Branch ref.
    ref = gh("-X", "POST", f"repos/{REPO}/git/refs", "--input", "-",
             input_bytes=json.dumps(
                 {"ref": f"refs/heads/{BRANCH}",
                  "sha": commit["sha"]}).encode())
    print(f"ref {ref['ref']} -> {ref['object']['sha']}")
    # 7. PR (do NOT merge; no docs-only label — this is a .json change).
    r = subprocess.run(
        ["gh", "pr", "create", "--repo", REPO, "--head", BRANCH,
         "--base", "main",
         "--title", "Fix stale 'NOT yet reversed' keyframe line in dw-motion-bank.json",
         "--body", BODY],
        capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"gh pr create failed (branch {BRANCH} exists, "
                         f"commit {commit['sha']}):\n{r.stderr.decode()}")
    print(f"PR: {r.stdout.decode().strip()}")
    print(f"HEAD={head} COMMIT={commit['sha']}")


if __name__ == "__main__":
    main()
