#!/usr/bin/env python3
"""PR status board for the repo (NOT the game). Owner 2026-11-03:
"no I don't want that on the game home screen but in the repo yes".

Lists every open PR (draft/ready, author, branch, head sha, base, stacked-on PR,
each required check, mergeable state, last update) and writes a Markdown board.

  python3 .github/scripts/pr_status_board.py --out docs/PR-STATUS.md   # build the board
  python3 .github/scripts/pr_status_board.py --out FILE --publish       # CI: also push it

--publish never writes to main (main is branch-protected, bot pushes are refused).
It updates (1) docs/PR-STATUS.md on the dedicated branch `pr-status-board`, and
(2) the body of the pinned issue "PR Status Board". Each is written only when the
board content changed (the "Generated" timestamp line is ignored in the compare).
Stdlib only; auth comes from GITHUB_TOKEN (Actions) or the caller's gateway.
"""
import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
REPO = os.environ.get("GITHUB_REPOSITORY", "mhvnsnt/western-heart")
BOARD_BRANCH = os.environ.get("BOARD_BRANCH", "pr-status-board")
BOARD_PATH = "docs/PR-STATUS.md"
ISSUE_TITLE = "PR Status Board"
SELF_CHECK = "pr-status-board"          # our own job: never listed on the board
GEN_PREFIX = "_Generated "              # line ignored when comparing content
# Fallback when the protection API is unreadable (AGENTS.md "Main protection law").
DEFAULT_REQUIRED = ["clobber-guard", "deletion-guard", "guard", "instruction-gate"]

FAIL = {"FAILURE", "TIMED_OUT", "ERROR", "ACTION_REQUIRED", "STARTUP_FAILURE"}
OK = {"SUCCESS", "NEUTRAL", "SKIPPED"}
ICON = {"pass": "✅", "fail": "❌", "run": "⏳", "missing": "·", "cancelled": "⊘"}


def req(method, path, body=None):
    url = path if path.startswith("http") else f"{API}/{path.lstrip('/')}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        r.add_header("Authorization", f"Bearer {tok}")
    r.add_header("Accept", "application/vnd.github+json")
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"message": raw.decode(errors="replace")}


def graphql(query, variables):
    code, out = req("POST", "graphql", {"query": query, "variables": variables})
    if code != 200 or not out or out.get("errors"):
        raise SystemExit(f"GraphQL failed ({code}): {json.dumps(out)[:500]}")
    return out["data"]


PR_QUERY = """
query($owner:String!, $name:String!, $after:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(states:OPEN, first:50, after:$after, orderBy:{field:UPDATED_AT, direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title url isDraft mergeable mergeStateStatus updatedAt
        headRefName baseRefName headRefOid author { login }
        commits(last:1) { nodes { commit { statusCheckRollup { contexts(first:100) { nodes {
          __typename
          ... on CheckRun { name status conclusion }
          ... on StatusContext { context state }
        } } } } } }
      }
    }
  }
}"""


def fetch_prs():
    owner, name = REPO.split("/")
    prs, after = [], None
    while True:
        d = graphql(PR_QUERY, {"owner": owner, "name": name, "after": after})
        page = d["repository"]["pullRequests"]
        prs += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return prs
        after = page["pageInfo"]["endCursor"]


def fetch_required():
    """Required status-check names on main (readable via /branches/main)."""
    code, b = req("GET", f"repos/{REPO}/branches/main")
    ctx = (((b or {}).get("protection") or {}).get("required_status_checks") or {}).get("contexts")
    protected = bool((b or {}).get("protected")) if code == 200 else True
    return (ctx or list(DEFAULT_REQUIRED)), protected


def check_state(node):
    """Normalise one rollup context to pass / fail / run / cancelled."""
    if node.get("__typename") == "StatusContext":
        s = (node.get("state") or "").upper()
        return "pass" if s == "SUCCESS" else "run" if s in ("PENDING", "EXPECTED") else "fail"
    if (node.get("status") or "").upper() != "COMPLETED":
        return "run"
    c = (node.get("conclusion") or "").upper()
    if c in OK:
        return "pass"
    if c == "CANCELLED":
        return "cancelled"
    return "fail" if c in FAIL else "run"


def _worst(states):
    for s in ("fail", "run", "cancelled", "pass"):
        if s in states:
            return s
    return "missing"


def fmt_time(s):
    """ISO 8601 from the API -> 'YYYY-MM-DD HH:MM UTC'. Unknown formats pass through."""
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        m = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{1,2}):(\d{2}) ([AP]M) \w+ \(UTC([+-]\d{2}):(\d{2})\)", s or "")
        if not m:
            return s or "?"
        h = int(m.group(2)) % 12 + (12 if m.group(4) == "PM" else 0)
        off = dt.timedelta(hours=int(m.group(5)), minutes=int(m.group(6)) * (1 if m.group(5)[0] == "+" else -1))
        t = dt.datetime.fromisoformat(f"{m.group(1)}T{h:02d}:{m.group(3)}:00").replace(tzinfo=dt.timezone(off))
        return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def classify(pr, required, heads):
    nodes = (((pr.get("commits") or {}).get("nodes") or [{}])[0].get("commit") or {})
    ctx = (((nodes.get("statusCheckRollup") or {}).get("contexts") or {}).get("nodes")) or []
    by_name = {}
    for n in ctx:
        name = n.get("name") or n.get("context") or "?"
        if name == SELF_CHECK:
            continue
        by_name.setdefault(name, []).append(check_state(n))
    states = {k: _worst(v) for k, v in by_name.items()}
    req_states = {r: states.get(r, "missing") for r in required}
    all_states = set(states.values()) | set(req_states.values())
    stacked_on = heads.get(pr["baseRefName"]) if pr["baseRefName"] != "main" else None
    mergeable = pr.get("mergeable") or "UNKNOWN"
    if mergeable == "CONFLICTING":
        status = "conflicted"
    elif "fail" in all_states:
        status = "failing"
    elif "run" in all_states:
        status = "running"
    elif pr["isDraft"]:
        status = "draft"
    elif pr["baseRefName"] != "main":
        status = "stacked"
    elif mergeable == "MERGEABLE" and all(v == "pass" for v in req_states.values()) and "cancelled" not in all_states:
        status = "ready"
    else:
        status = "blocked"
    return {
        "number": pr["number"], "title": pr["title"], "url": pr.get("url", ""),
        "draft": pr["isDraft"], "author": (pr.get("author") or {}).get("login", "ghost"),
        "head": pr["headRefName"], "sha": (pr.get("headRefOid") or "")[:7], "base": pr["baseRefName"],
        "stacked_on": stacked_on, "required": req_states, "mergeable": mergeable,
        "merge_state": pr.get("mergeStateStatus") or "UNKNOWN", "updated": fmt_time(pr.get("updatedAt")),
        "status": status,
        "other": {s: sum(1 for k, v in states.items() if k not in required and v == s) for s in ("pass", "fail", "run")},
    }


ORDER = ["ready", "running", "blocked", "stacked", "failing", "conflicted", "draft"]
LABEL = {"ready": "🟢 ready to merge", "running": "⏳ running", "blocked": "🟠 blocked",
         "stacked": "🔗 stacked", "failing": "🔴 failing", "conflicted": "⚔️ conflicted", "draft": "📝 draft"}


def merge_chains(rows):
    """Stacked PRs: the PR a branch is based on merges first (e.g. #1525 before #1526)."""
    by_num = {r["number"]: r for r in rows}
    kids = {}
    for r in rows:
        if r["stacked_on"]:
            kids.setdefault(r["stacked_on"], []).append(r["number"])
    chains = []
    for r in sorted(rows, key=lambda r: r["number"]):
        if r["stacked_on"] or r["number"] not in kids:
            continue
        stack, todo = [], [r["number"]]
        while todo:
            n = todo.pop(0)
            stack.append(n)
            todo += sorted(kids.get(n, []))
        chains.append(" → ".join(f"#{n}" for n in stack) + f" (root targets `{by_num[r['number']]['base']}`)")
    return chains


def esc(s):
    return s.replace("|", "\\|").replace("\n", " ")


def render(rows, required, now):
    rows = sorted(rows, key=lambda r: (ORDER.index(r["status"]), -r["number"]))
    cnt = {s: sum(1 for r in rows if r["status"] == s) for s in ORDER}
    drafts = sum(1 for r in rows if r["draft"])
    out = [
        "# PR Status Board",
        "",
        "<!-- Generated by .github/workflows/pr-status-board.yml (.github/scripts/pr_status_board.py). "
        "Do not edit by hand: the next run overwrites it. Lives in the repo, never in the game UI. -->",
        "",
        f"**{len(rows)} open PRs — 🟢 ready to merge: {cnt['ready']} · 🔴 failing: {cnt['failing']} · "
        f"⏳ running: {cnt['running']} · ⚔️ conflicted: {cnt['conflicted']}** "
        f"(also 🟠 blocked: {cnt['blocked']} · 🔗 stacked: {cnt['stacked']} · 📝 draft, green-or-idle: {cnt['draft']}; "
        f"{drafts} of {len(rows)} are drafts)",
        "",
        f"{GEN_PREFIX}{now} · required checks on `main`: {', '.join('`'+r+'`' for r in required)}_",
        "",
        "Legend: ✅ pass · ❌ fail · ⏳ queued/running · ⊘ cancelled · `·` not reported. "
        "Ready = not draft, targets `main`, GitHub says MERGEABLE, every check green. "
        "Status priority: conflicted > failing > running > draft > stacked > ready.",
        "",
    ]
    chains = merge_chains(rows)
    out += ["## Merge order (stacked PRs)", ""]
    out += [f"- {c}" for c in chains] if chains else ["- No stacked PRs open."]
    out += ["", "## Open PRs", ""]
    hdr = ["Status", "PR", "Draft?", "Author / lane branch", "Head", "Base"] + [f"`{r}`" for r in required] + \
          ["Other checks", "Mergeable", "Updated"]
    out.append("| " + " | ".join(hdr) + " |")
    out.append("|" + "---|" * len(hdr))
    for r in rows:
        base = f"`{esc(r['base'])}`" + (f" (on #{r['stacked_on']})" if r["stacked_on"] else "")
        o = r["other"]
        other = " ".join(f"{n}{ICON[s]}" for s, n in o.items() if n) or "—"
        cells = [LABEL[r["status"]], f"[#{r['number']}]({r['url']}) {esc(r['title'])[:90]}",
                 "draft" if r["draft"] else "ready", f"{esc(r['author'])} / `{esc(r['head'])}`",
                 f"`{r['sha']}`", base] + [ICON[r["required"][q]] for q in required] + \
                [other, f"{r['mergeable'].lower()} ({r['merge_state'].lower()})", r["updated"]]
        out.append("| " + " | ".join(cells) + " |")
    if not rows:
        out.append("| — | No open PRs | | | | |" + " |" * (len(required) + 3))
    return "\n".join(out) + "\n"


def strip_gen(text):
    return "\n".join(l for l in (text or "").splitlines() if not l.startswith(GEN_PREFIX)).strip()


def publish_branch(board):
    code, b = req("GET", f"repos/{REPO}/branches/{BOARD_BRANCH}")
    if code == 404:
        _, main = req("GET", f"repos/{REPO}/branches/main")
        c, r = req("POST", f"repos/{REPO}/git/refs",
                   {"ref": f"refs/heads/{BOARD_BRANCH}", "sha": main["commit"]["sha"]})
        print(f"create branch {BOARD_BRANCH}: {c}")
        if c >= 300:
            return f"branch create failed ({c}): {r}"
    code, f = req("GET", f"repos/{REPO}/contents/{BOARD_PATH}?ref={BOARD_BRANCH}")
    sha, old = None, ""
    if code == 200:
        sha, old = f["sha"], base64.b64decode(f["content"]).decode()
    if strip_gen(old) == strip_gen(board):
        return "branch: unchanged, no commit"
    body = {"message": "chore(pr-status-board): refresh docs/PR-STATUS.md [skip ci]",
            "content": base64.b64encode(board.encode()).decode(), "branch": BOARD_BRANCH}
    if sha:
        body["sha"] = sha
    c, r = req("PUT", f"repos/{REPO}/contents/{BOARD_PATH}", body)
    return f"branch: committed ({c})" if c < 300 else f"branch: commit failed ({c}): {r}"


def find_issue():
    """Pinned issue first (no index lag), then title search."""
    owner, name = REPO.split("/")
    q = "query($o:String!,$n:String!){repository(owner:$o,name:$n){pinnedIssues(first:3){nodes{issue{number title body state}}}}}"
    c, d = req("POST", "graphql", {"query": q, "variables": {"o": owner, "n": name}})
    for n in (((d or {}).get("data") or {}).get("repository") or {}).get("pinnedIssues", {}).get("nodes", []):
        i = n["issue"]
        if i["title"] == ISSUE_TITLE and i["state"] == "OPEN":
            return i
    c, s = req("GET", f"search/issues?q=repo:{REPO}+is:issue+is:open+in:title+%22PR+Status+Board%22")
    return next((i for i in (s or {}).get("items", []) if i.get("title") == ISSUE_TITLE), None)


def publish_issue(board):
    issue = find_issue()
    if issue is None:
        c, issue = req("POST", f"repos/{REPO}/issues", {"title": ISSUE_TITLE, "body": board})
        if c >= 300:
            return f"issue: create failed ({c}): {issue}"
        pc, pr = req("POST", "graphql", {"query": "mutation($id:ID!){pinIssue(input:{issueId:$id}){issue{number}}}",
                                         "variables": {"id": issue["node_id"]}})
        return f"issue: created #{issue['number']} (pin: {pc}{' '+str(pr.get('errors')) if pr and pr.get('errors') else ''})"
    if strip_gen(issue.get("body")) == strip_gen(board):
        return f"issue #{issue['number']}: unchanged"
    c, r = req("PATCH", f"repos/{REPO}/issues/{issue['number']}", {"body": board[:65000]})
    return f"issue #{issue['number']}: updated ({c})" if c < 300 else f"issue: update failed ({c}): {r}"


def build():
    required, protected = fetch_required()
    prs = fetch_prs()
    heads = {p["headRefName"]: p["number"] for p in prs}
    rows = [classify(p, required, heads) for p in prs]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return render(rows, required, now), protected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=BOARD_PATH)
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    board, protected = build()
    with open(a.out, "w") as f:
        f.write(board)
    print(board.splitlines()[4])
    if a.publish:
        # main is protected (required checks, admins included) so a bot push to it is refused:
        # publish to the dedicated branch + the pinned issue instead, never to main.
        print(f"main protected: {protected}")
        msgs = [publish_branch(board), publish_issue(board)]
        print("\n".join(msgs))
        if any("failed" in m for m in msgs):
            sys.exit(1)


if __name__ == "__main__":
    main()
