#!/usr/bin/env python3
"""Instruction gate: fails a PR whose body does not prove the owner's method was followed.

Usage in CI:  python3 .github/scripts/instruction_gate.py   (reads GITHUB_EVENT_PATH)
Library use:  check(body, changed_files, repo_root, labels, author) -> list of errors
"""
import json
import os
import re
import subprocess
import sys

SECTIONS = [
    ("instruction", "Owner instruction (verbatim quote)"),
    ("specified", "Method the owner specified"),
    ("used", "Method actually used"),
    ("deviations", "Deviations (none / list, each with owner approval link)"),
    ("proof", "Proof (paths to files, frames, test output)"),
    ("selfcheck", "Self-check: I verified the result against the literal instruction"),
]
PLACEHOLDER = re.compile(r"^>\s*Paste the owner's exact words\. Do not paraphrase\.$", re.I)
APPROVAL_REF = re.compile(r"(https?://\S+|#\d+)")
NONE_WORDS = {"none", "none.", "n/a", "no deviations", "no deviations."}


def _norm_heading(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def parse_sections(body):
    """Return {key: text} for the required sections (comments stripped)."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    wanted = {_norm_heading(title): key for key, title in SECTIONS}
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            h = _norm_heading(m.group(1))
            cur = next((k for t, k in wanted.items() if h == t or h.startswith(t)), None)
            if cur is not None:
                out.setdefault(cur, [])
            continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def _norm_method(s):
    s = re.sub(r"[`*_>\-]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip(" .")


def extract_paths(proof):
    paths = re.findall(r"`([^`\s]+)`", proof)
    if not paths:
        for line in proof.splitlines():
            line = re.sub(r"^\s*[-*+]\s+", "", line).strip()
            if line and " " not in line:
                paths.append(line)
    return [p.strip().lstrip("./") if p.startswith("./") else p.strip() for p in paths]


def _exists(repo_root, p):
    if os.path.exists(os.path.join(repo_root, p)):
        return True
    # sparse checkout in CI: ask git whether the path exists at HEAD
    r = subprocess.run(["git", "-C", repo_root, "cat-file", "-e", f"HEAD:{p}"],
                       capture_output=True)
    return r.returncode == 0


HEX_COMMIT = re.compile(r"^[0-9a-f]{7,40}$", re.I)
DIGEST = re.compile(r"^(sha256:)?([0-9a-f]{64}|[0-9a-f]{4,}(\u2026|\.\.\.)[0-9a-f]+)$", re.I)


def proof_kind(p):
    """How a Proof entry is verified: path (file in the diff/repo), commit (SHA in this repo),
    ref (tag, release or branch of this repo), url, or digest (a checksum: identifies bytes,
    never looked up). Workers cite archived originals by release tag and commit SHA."""
    if re.match(r"https?://", p):
        return "url"
    if DIGEST.match(p):
        return "digest"
    if HEX_COMMIT.match(p):
        return "commit"
    if "/" in p or "." in p.rsplit("/", 1)[-1]:
        return "path"
    return "ref"


def _is_commit(repo_root, sha):
    r = subprocess.run(["git", "-C", repo_root, "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True)
    return r.returncode == 0


def gh_resolver(repo):
    """Look a commit / tag / release / branch up on GitHub (the CI checkout is shallow)."""
    def resolve(kind, ref):
        if kind == "commit":
            urls = [f"repos/{repo}/commits/{ref}"]
        else:
            urls = [f"repos/{repo}/git/ref/tags/{ref}", f"repos/{repo}/releases/tags/{ref}",
                    f"repos/{repo}/branches/{ref}"]
        for u in urls:
            if subprocess.run(["gh", "api", u, "--silent"], capture_output=True).returncode == 0:
                return True
        return False
    return resolve


def check(body, changed_files, repo_root=".", labels=(), author="", resolve_ref=None):
    labels = {l.lower() for l in labels}
    if author.lower() in {"dependabot[bot]", "dependabot"}:
        return []
    if "docs-only" in labels:
        non_md = [f for f in changed_files if not f.lower().endswith(".md")]
        if not non_md:
            return []
        return ["'docs-only' label is set but the PR changes non-.md files: " + ", ".join(non_md[:10])]

    errors = []
    sec = parse_sections(body)
    for key, title in SECTIONS:
        text = sec.get(key)
        if text is None:
            errors.append(f"Missing required section: '## {title}'")
        elif not text or (key == "instruction" and PLACEHOLDER.match(text)):
            errors.append(f"Section is empty: '## {title}'")
    if errors:
        return errors

    dev = sec["deviations"]
    dev_is_none = _norm_method(dev) in {_norm_method(w) for w in NONE_WORDS}
    if _norm_method(sec["specified"]) != _norm_method(sec["used"]) and dev_is_none:
        errors.append("'Method actually used' differs from 'Method the owner specified' but Deviations says none. "
                      "Use the method he named, or list the deviation with his approval link.")
    if not dev_is_none:
        items = [l for l in dev.splitlines() if l.strip()]
        for item in items:
            if not APPROVAL_REF.search(item):
                errors.append(f"Deviation has no owner approval link/#ref: {item.strip()}")

    paths = extract_paths(sec["proof"])
    if not paths:
        errors.append("Proof lists no paths. Put each file/frame/test-output path in backticks.")
    changed = set(changed_files)
    resolved = 0
    for p in paths:
        kind = proof_kind(p)
        if kind == "digest":
            continue  # a checksum identifies bytes; it is not a reference to look up
        if kind == "url" or p in changed or _exists(repo_root, p):
            resolved += 1
            continue
        if kind in ("commit", "ref") and (_is_commit(repo_root, p) if kind == "commit" else False):
            resolved += 1
            continue
        if kind in ("commit", "ref") and resolve_ref is not None and resolve_ref(kind, p):
            resolved += 1
            continue
        if kind == "commit":
            errors.append(f"Proof commit not found in this repo: {p}")
        elif kind == "ref":
            errors.append(f"Proof ref is not a file, commit, tag, release or branch of this repo: {p}")
        else:
            errors.append(f"Proof path not in this PR's diff or the repo: {p}")
    if paths and not resolved and not errors:
        errors.append("Proof lists only checksums. Add the file, commit, tag/release or URL they belong to.")

    if not re.search(r"^\s*[-*]\s+\[[xX]\]", sec["selfcheck"], re.M):
        errors.append("Self-check box is not ticked ([x]).")
    return errors


def _gh_get_pr(repo, number):
    r = subprocess.run(["gh", "api", f"repos/{repo}/pulls/{number}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def live_pr(pr, repo, fetch=_gh_get_pr):
    """Use the PR's CURRENT body and labels, not the event snapshot.

    The event payload is frozen when the run is queued. Two quick body edits
    plus cancel-in-progress can leave the surviving run holding the older body,
    and "Re-run" replays that same stale payload, so a body that is already
    fixed keeps failing. Falls back to the payload if the API call fails.
    """
    try:
        cur = fetch(repo, pr["number"])
    except Exception:  # noqa: BLE001
        cur = None
    if not cur:
        return pr
    merged = dict(pr)
    merged["body"] = cur.get("body")
    if "labels" in cur:
        merged["labels"] = cur["labels"]
    return merged


def main():
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        ev = json.load(f)
    repo = ev["repository"]["full_name"]
    pr = live_pr(ev["pull_request"], repo)
    files = subprocess.run(["gh", "api", "--paginate", f"repos/{repo}/pulls/{pr['number']}/files",
                            "-q", ".[].filename"],
                           capture_output=True, text=True, check=True).stdout.split("\n")
    files = [f for f in files if f]
    errs = check(pr.get("body") or "", files, ".",
                 [l["name"] for l in pr.get("labels", [])], pr["user"]["login"], gh_resolver(repo))
    if errs:
        print("INSTRUCTION GATE FAILED (AGENTS.md law 15: Lock the method)")
        for e in errs:
            print(f"::error::{e}")
        sys.exit(1)
    print("Instruction gate passed.")


if __name__ == "__main__":
    main()
