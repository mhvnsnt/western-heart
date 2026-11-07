import subprocess, json, base64, os, sys

REPO = "mhvnsnt/western-heart"
BRANCH = "smutbase6-fidelity-20261104"
W = "/home/hatch/workspace/_smutbase6-fidelity-20261104"

FILES = [("docs/handoffs/SMUTBASE6-FIDELITY-2026-11-04.md", f"{W}/GAP-REPORT-DRAFT.md")]
for f in sorted(os.listdir(f"{W}/renders")):
    FILES.append((f"docs/proof/2026-11-04/smutbase6-fidelity/{f}", f"{W}/renders/{f}"))
for f in ["inventory-pond-ryusan.json", "inventory-tobi-chatur.json", "inventory-megami-menajerii.json",
          "blend-inv-pond.json", "blend-inv-ryusan.json", "blend-inv-tobi.json", "blend-inv-chatur.json"]:
    FILES.append((f"docs/proof/2026-11-04/smutbase6-fidelity/{f}", f"{W}/{f}"))

def gh_api(path, payload=None, method=None):
    cmd = ["gh", "api", path]
    if method:
        cmd += ["-X", method]
    inp = None
    if payload is not None:
        inp = json.dumps(payload)
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=inp, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL", path, r.stderr[:400]); sys.exit(1)
    return json.loads(r.stdout) if r.stdout.strip() else {}

main = gh_api(f"repos/{REPO}/git/ref/heads/main")
base_sha = main["object"]["sha"]
base_commit = gh_api(f"repos/{REPO}/git/commits/{base_sha}")
base_tree = base_commit["tree"]["sha"]
print("base", base_sha, base_tree)

tree_items = []
for repo_path, local in FILES:
    data = open(local, "rb").read()
    blob = gh_api(f"repos/{REPO}/git/blobs", {"content": base64.b64encode(data).decode(), "encoding": "base64"})
    tree_items.append({"path": repo_path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print("blob", repo_path, len(data), blob["sha"][:10])

tree = gh_api(f"repos/{REPO}/git/trees", {"base_tree": base_tree, "tree": tree_items})
commit = gh_api(f"repos/{REPO}/git/commits", {
    "message": "SmutBase 6 fidelity gap report: source blends inventoried in Blender 5.2.3, shipped-vs-blend gaps + rebuild plan (owner order 2026-11-04)",
    "tree": tree["sha"], "parents": [base_sha]})
print("commit", commit["sha"])
ref = gh_api(f"repos/{REPO}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
print("ref ok")
pr = gh_api(f"repos/{REPO}/pulls", {
    "title": "SmutBase 6 fidelity gap report + Blender reference renders (2026-11-04)",
    "head": BRANCH, "base": "main",
    "body": "Owner order 2026-11-04: the six must match their source .blend files exactly, full rigs, all textures. This PR lands the phase-1 audit: every source located + hashed, the four in-repo blends inventoried in Blender 5.2.3 (bone counts, hidden flags, shape keys, packed images), EEVEE/Workbench reference renders as the fidelity targets, per-character shipped-vs-blend gap lists, and the ordered rebuild plan. Headlines: Pond 224 bones vs shipped 52, Ryusan 520 vs 73, Tobi 254 vs 73, Chatur 983/133 vs 52 AND four arms vs two; 71-129 shape keys per blend vs 0 morphs shipped; Tobi's flat Eyes/Hair closure refuted (maps are packed in the blend); Pond's hidden-mesh removal confirmed faithful (blend's own hide flags); Megami/Menajerii commission blends (596MB/985MB) are NOT in holdings - recovery action opened, full GLBs are the interim targets."})
print("PR", pr["number"], pr["html_url"])
