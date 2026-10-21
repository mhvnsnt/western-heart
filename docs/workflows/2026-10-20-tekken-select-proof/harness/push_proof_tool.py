#!/usr/bin/env python3
"""Push the select-screen proof set to mhvnsnt/western-heart via the
git data API — no local checkout/staging. Each blob's returned sha is
checked against the locally computed git blob id (byte-proof).
Usage: push_proof.py [png|harness|all]  (passes append to the branch)
"""
import base64, hashlib, json, os, subprocess, sys, tempfile

REPO = "mhvnsnt/western-heart"
BRANCH = "docs/select-proof-assets-20261020"
DEST = "docs/workflows/2026-10-20-tekken-select-proof"
YF = "/home/hatch/workspace/your_files"
HARNESS = "/home/hatch/workspace/_wh-work/select-harness"

PNGS = [
    "live-select-final-phone-demonio-attire1.png",
    "live-select-final-phone-demonio.png",
    "live-select-final-phone-initial.png",
    "select-new-phone-demonio-idle-a.png",
    "select-new-phone-demonio-idle-b.png",
    "select-new-phone-initial.png",
    "select-probe-cdp.png",
    "select-v2-phone-demonio-stance-a.png",
    "select-v2-phone-demonio-stance-b.png",
    "select-v2-phone-fight-canvas.png",
    "select-v2-phone-fight-dom-a.png",
    "select-v2-phone-fight-dom-b.png",
    "select-v3-desktop-initial.png",
    "select-v3-desktop-pantera-stance-a.png",
    "select-v3-desktop-pantera-stance-b.png",
    "select-v3-phone-demonio-attire1.png",
    "select-v3-phone-demonio-motion-a.png",
    "select-v3-phone-demonio-motion-b.png",
    "select-v3-phone-demonio-stance-a.png",
    "select-v3-phone-demonio-stance-b.png",
    "select-v3-phone-pantera-gate.png",
    "select-v3-phone-stage-select.png",
    "select-v3-phone-versus-p2-rin.png",
]


def gh_api(method, endpoint, payload=None):
    import time
    last = None
    for attempt in range(4):
        cmd = ["gh", "api", f"repos/{REPO}/{endpoint}", "-X", method]
        tmp = None
        if payload is not None:
            fd, tmp = tempfile.mkstemp(suffix=".json")
            with os.fdopen(fd, "w") as f:
                json.dump(payload, f)
            cmd += ["--input", tmp]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if tmp:
            os.unlink(tmp)
        if r.returncode == 0:
            return json.loads(r.stdout)
        last = r.stderr[:300]
        print(f"retry {attempt + 1} {method} {endpoint}: {last[:100]}", flush=True)
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"gh api {method} {endpoint}: {last}")


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


which = sys.argv[1] if len(sys.argv) > 1 else "all"
files = []
if which in ("all", "png", "png1", "png2"):
    subset = PNGS if which in ("all", "png") else (PNGS[:12] if which == "png1" else PNGS[12:])
    for name in subset:
        files.append((os.path.join(YF, name), f"{DEST}/{name}"))
if which in ("all", "harness"):
    for name in sorted(os.listdir(HARNESS)):
        if name == "push_proof.py":
            continue
        files.append((os.path.join(HARNESS, name), f"{DEST}/harness/{name}"))

branch_exists = True
try:
    ref = gh_api("GET", f"git/ref/heads/{BRANCH}")
    base_sha = ref["object"]["sha"]
except RuntimeError:
    branch_exists = False
    ref = gh_api("GET", "git/ref/heads/main")
    base_sha = ref["object"]["sha"]
print("base:", base_sha, "branch_exists:", branch_exists, flush=True)
base_tree = gh_api("GET", f"git/commits/{base_sha}")["tree"]["sha"]

tree_entries = []
total = 0
for local, repo_path in files:
    data = open(local, "rb").read()
    total += len(data)
    blob = gh_api("POST", "git/blobs",
                  {"content": base64.b64encode(data).decode(), "encoding": "base64"})
    ok = blob["sha"] == git_blob_id(data)
    print(f"blob {repo_path} {len(data)}B sha-ok={ok}", flush=True)
    if not ok:
        sys.exit(f"BLOB MISMATCH {repo_path}")
    tree_entries.append({"path": repo_path, "mode": "100644", "type": "blob", "sha": blob["sha"]})

tree = gh_api("POST", "git/trees", {"base_tree": base_tree, "tree": tree_entries})
new_commit = gh_api("POST", "git/commits", {
    "message": f"Select-screen proof assets ({which}): verification screenshots + capture harness for the PR #384 build record",
    "tree": tree["sha"], "parents": [base_sha]})
if branch_exists:
    gh_api("PATCH", f"git/refs/heads/{BRANCH}", {"sha": new_commit["sha"], "force": True})
else:
    gh_api("POST", "git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": new_commit["sha"]})
print("COMMIT:", new_commit["sha"], f"({len(tree_entries)} files, {total}B)", flush=True)

listing = gh_api("GET", f"git/trees/{tree['sha']}?recursive=1")
paths = {e["path"] for e in listing["tree"]}
missing = [rp for _, rp in files if rp not in paths]
print("TREE VERIFY missing:", missing if missing else "NONE — all present", flush=True)
