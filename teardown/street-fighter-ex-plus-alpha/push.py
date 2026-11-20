import subprocess, json, os, base64, sys

REPO = "mhvnsnt/western-heart"
SRC = "/home/hatch/workspace/sf-teardown-push"
PREFIX = "teardown/street-fighter-ex-plus-alpha"
BASE = "853b12b7569f927820fcf93ed3cef4662c49bd6a"
BRANCH = "feature/sf-ex-plus-alpha-teardown"

def api(*args, input_data=None):
    cmd = ["gh", "api"] + list(args)
    r = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("gh api failed: " + " ".join(args) + "\n" + r.stderr[:500])
    return json.loads(r.stdout) if r.stdout.strip() else {}

tree = []
for root, _, files in os.walk(SRC):
    for fn in sorted(files):
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, SRC)
        with open(p, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        b = api("repos/%s/git/blobs" % REPO, "--input", "-",
                input_data=json.dumps({"content": content, "encoding": "base64"}))
        tree.append({"path": "%s/%s" % (PREFIX, rel), "mode": "100644",
                     "type": "blob", "sha": b["sha"]})
        print("blob:", rel, b["sha"][:8], flush=True)

print("total blobs:", len(tree), flush=True)
t = api("repos/%s/git/trees" % REPO, "--input", "-",
        input_data=json.dumps({"base_tree": BASE, "tree": tree}))
print("tree:", t["sha"], flush=True)
c = api("repos/%s/git/commits" % REPO, "--input", "-",
        input_data=json.dumps({
            "message": ("SF EX Plus Alpha teardown: moveset data, roster, TEARDOWN.md\n\n"
                        "- 26-slot character system documented (P00-P19 PAC model packs + OVL/OVL2 move-data overlays)\n"
                        "- Character name table + 165 move names extracted verbatim from SLUS_005.48\n"
                        "- Raw move-data overlays (52 files) committed for frame-data research\n"
                        "- Per owner SF directive: movesets research-only, Tekken play style stays"),
            "tree": t["sha"], "parents": [BASE]}))
print("commit:", c["sha"], flush=True)
r = api("repos/%s/git/refs" % REPO, "--input", "-",
        input_data=json.dumps({"ref": "refs/heads/%s" % BRANCH, "sha": c["sha"]}))
print("branch:", r["ref"], flush=True)
