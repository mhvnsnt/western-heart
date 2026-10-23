#!/usr/bin/env python3
"""Rig guard: fail a PR that removes ANY model key from MODEL_URLS.

The loss this prevents: a wired model silently becomes unreachable when its
MODEL_URLS key is deleted (the zui/zen gaps of 2026-10-21 were only found by
manual audit — GLBs on disk with no key, unloadable in fights). Deleting a
key IS deleting a wired model, skinned or not: ANY key removal fails, not
just skinned ones.

Algorithm (pure functions, unit-tested in test_rig_guard.py):
    removed    = keys(MODEL_URLS at BASE) - keys(MODEL_URLS at HEAD)
    violating  = removed - called_out
Additions never flag. BASE is the PR fork point (merge-base), so keys main
added after the fork cannot false-positive on a stale base.

Explicit escape — silence is refusal:
  * the PR carries the label "owner-approved-model-removal", or
  * the PR body has a "## Model removals" section naming every removed key
    in backticks (per the >20-line callout rule: removals are intentional
    and called out in the PR body).

Usage in CI:
    BASE_SHA=<fork point> HEAD_SHA=<pr head> \
        python3 tools/rig-guard/rig_guard.py          # reads GITHUB_EVENT_PATH
Library use:
    check_removals(base_keys, head_keys, body, labels) -> set of violating keys
Local use (pre-push, same as tools/clobber-check):
    BASE_SHA=<sync-sha> HEAD_SHA=$(git rev-parse HEAD) \
        python3 tools/rig-guard/rig_guard.py
"""
import json
import os
import re
import subprocess
import sys

MODEL_FILE = "game/js/assets.js"
REMOVE_LABEL = "owner-approved-model-removal"


def extract_model_keys(js_text):
    """All top-level keys of the MODEL_URLS literal. Empty set if absent.

    Char-scanner (not regex): tracks strings and // /* */ comments so a
    brace inside a comment or a '//' inside a path can never corrupt the
    parse. A depth-1 string/identifier followed by ':' is a key.
    """
    m = re.search(r"MODEL_URLS\s*=\s*\{", js_text or "")
    if not m:
        return set()
    block, keys = js_text[m.start():], set()
    i, n, depth = block.find("{"), len(block), 0
    while i < n:
        ch = block[i]
        if ch in "'\"`":  # string: skip, but a depth-1 one before ':' is a key
            q, j, buf = ch, i + 1, []
            while j < n:
                c = block[j]
                if c == "\\":
                    buf.append(block[j + 1] if j + 1 < n else "")
                    j += 2
                    continue
                if c == q:
                    break
                buf.append(c)
                j += 1
            k = j + 1
            while k < n and block[k] in " \t\n\r":
                k += 1
            if depth == 1 and k < n and block[k] == ":":
                keys.add("".join(buf))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and block[i + 1] == "/":
            nl = block.find("\n", i)
            i = n if nl < 0 else nl + 1
            continue
        if ch == "/" and i + 1 < n and block[i + 1] == "*":
            end = block.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        elif depth == 1 and (ch.isalpha() or ch in "_$"):
            j = i
            while j < n and (block[j].isalnum() or block[j] in "_$"):
                j += 1
            k = j
            while k < n and block[k] in " \t\n\r":
                k += 1
            if k < n and block[k] == ":":
                keys.add(block[i:j])
            i = j
            continue
        i += 1
    return keys


def removed_keys(base_keys, head_keys):
    """Keys wired at BASE but gone at HEAD. Additions never flag."""
    return set(base_keys) - set(head_keys)


def parse_model_removal_callout(body):
    """Keys (in backticks) named under a '## Model removals' PR-body section."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    keys, armed = set(), False
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            armed = re.sub(r"[^a-z0-9]+", " ", m.group(1).lower()).strip().startswith(
                "model removal")
            continue
        if armed:
            keys.update(re.findall(r"`([^`\s]+)`", line))
    return keys


def check_removals(base_keys, head_keys, body="", labels=()):
    """Removed keys not covered by the escape path. Empty set = pass."""
    if REMOVE_LABEL in {str(lb).lower() for lb in (labels or [])}:
        return set()
    return removed_keys(base_keys, head_keys) - parse_model_removal_callout(body)


def _git_show(rev, path):
    p = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def main():
    base = os.environ.get("BASE_SHA", "")
    head = os.environ.get("HEAD_SHA", "")
    path = os.environ.get("MODEL_FILE", MODEL_FILE)
    if not base or not head:
        print("rig_guard: BASE_SHA and HEAD_SHA env required", file=sys.stderr)
        return 2
    base_text = _git_show(base, path)
    head_text = _git_show(head, path)
    if head_text is None:
        print(f"rig_guard: {path} missing at HEAD {head[:8]} — nothing to guard")
        return 0
    if base_text is None:
        print(f"rig_guard: {path} new at HEAD — no baseline, pass")
        return 0
    body, labels = "", []
    ev = os.environ.get("GITHUB_EVENT_PATH", "")
    if ev:
        try:
            with open(ev) as fh:
                pr = json.load(fh).get("pull_request", {})
            body = pr.get("body") or ""
            labels = [lb.get("name", "") for lb in pr.get("labels", [])]
        except (OSError, ValueError) as exc:
            print(f"rig_guard: warning: event unreadable ({exc}); escape path degraded")
    base_keys = extract_model_keys(base_text)
    head_keys = extract_model_keys(head_text)
    bad = check_removals(base_keys, head_keys, body, labels)
    if bad:
        print("rig_guard FAIL: MODEL_URLS key(s) removed with no documented opt-out:")
        for key in sorted(bad):
            print(f"  - {key}")
        print(f'Escape: name each key in backticks under a "## Model removals" '
              f'PR-body section, or add the "{REMOVE_LABEL}" label.')
        return 1
    print(f"rig_guard PASS: no MODEL_URLS removals ({len(head_keys)} keys wired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
