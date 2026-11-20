import subprocess, json, base64, os, sys

REPO = "mhvnsnt/western-heart"
BRANCH = "smutbase6-recovery-20261105"
W = "/home/hatch/workspace/_smutbase6-fidelity-20261104"
PROOF = "docs/proof/2026-11-04/smutbase6-fidelity"

# Build updated handoff: FRESH main content (re-fetched now, never a stale copy) + recovery section
import urllib.request
_r = subprocess.run(["gh", "api", "repos/mhvnsnt/western-heart/contents/docs/handoffs/SMUTBASE6-FIDELITY-2026-11-04.md",
                     "-H", "Accept: application/vnd.github.raw"], capture_output=True)
assert _r.returncode == 0, _r.stderr[:300]
handoff = _r.stdout
print("fresh handoff bytes:", len(handoff))
assert b"MEGAMI + MENAJERII SOURCE RECOVERY" not in handoff, "recovery section already on main"
section = open(f"{W}/RECOVERY-SECTION.md", "rb").read()
if not handoff.endswith(b"\n"):
    handoff += b"\n"
updated = handoff + section

FILES = [
    ("docs/handoffs/SMUTBASE6-FIDELITY-2026-11-04.md", None, updated),
    (f"{PROOF}/parvati-src-front-20261104.png", f"{W}/renders/parvati-src-front-20261104.png", None),
    (f"{PROOF}/parvati-src-q34-20261104.png", f"{W}/renders/parvati-src-q34-20261104.png", None),
    (f"{PROOF}/parvati-src-face-20261104.png", f"{W}/renders/parvati-src-face-20261104.png", None),
    (f"{PROOF}/vixen-src-front-20261104.png", f"{W}/renders/vixen-src-front-20261104.png", None),
    (f"{PROOF}/vixen-src-face-20261104.png", f"{W}/renders/vixen-src-face-20261104.png", None),
    (f"{PROOF}/inventory-parvati-recovered.json", f"{W}/recovered-sources/inventory-parvati.json", None),
    (f"{PROOF}/inventory-vixen-recovered.json", f"{W}/recovered-sources/inventory-vixen.json", None),
]

BODY = """## Owner instruction (verbatim quote)

"the six must look EXACTLY like their source .blend files opened in Blender \u2014 perfect \u2014 with the FULL rigs that come with their own files, all textures and everything else from the source files" (owner, 2026-11-04)

Megami = Parvati (Jun Kazama), Menajerii = Vixen (Roger Jr.). Their commission blends were missing from all holdings (gap report #1567); this PR closes the source-recovery track so their rebuilds (steps 5 and 6 of the plan) can run from the real files.

## Method the owner specified

Phase-1 handoff (#1567) recovery actions: locate or re-download the two commission .rar originals (hashes recorded), store everything per the storing laws so the files never exist in only one place, and unblock the Megami/Menajerii rebuilds \u2014 without starting those rebuilds out of order.

## Method actually used

Exactly the specified method. A browser lane identified the original SmutBase listings (MilkGuy_3D "Parvati Holcomb" + "Vixen") and re-downloaded both archives after the disk/GitHub/TeraBox searches came back exhausted/negative. This lane then: (1) verified both rars against the full original sha256 values preserved in the lane checkpoint \u2014 **both match exactly**; (2) extracted and inventoried both blends in Blender 5.2.3 (the decisive contents test for the one open hash question, below); (3) rendered identity proofs and eye-checked them against the known GLB sources; (4) stored everything on release `megami-menajerii-smutbase-20261023`: both rars whole, and both blends as \u2264300 MB parts with a reassembly manifest (whole-file uploads above ~412 MB would not finalize from this VM \u2014 assets stuck in "starter" state with no retrievable content despite both gh and curl reporting success; a 419,430,400-byte part failed repeatedly while everything \u2264412,236,235 B succeeded, so the blends went up as 314,572,800-byte-capped parts via direct API POST). Every stored asset's size + sha256 digest was verified against the local file via the Releases API, and the store was pull-back proven: all six parts re-downloaded, reassembled, both whole-file sha256 values reproduced exactly, and `ParvatiCommission.rar` re-downloaded and hash-matched.

What lands in this PR: the handoff doc gains a "MEGAMI + MENAJERII SOURCE RECOVERY \u2014 FOUND" section (hashes, sizes, measured inventories, store locations, status change), plus the identity renders and full inventory JSONs as proof. The binaries themselves live on the release, not in git.

Measured inventory (Blender 5.2.3): Parvati(Commission).blend \u2014 595,860,144 B, file version Blender 4.2, 66 scene objects, armature `Parvati` 469 bones, GZM controller objects present, 474 shape keys on the body mesh, 123/124 images packed. Vixen (Commission).blend \u2014 984,617,116 B, 67 scene objects, armature `Vixen` 450 bones, GZM rig, 2,509 shape keys across 24 meshes, 124/125 images packed.

## Deviations (none / list, each with owner approval link)

None against the owner's order. Two record-keeping findings, documented in the handoff section itself (#1567):

1. The SmutBase mirror page states a "source" SHA-256 for ParvatiCommission.rar (`2601d935e1f8\u2026`) that shares only the 8-char prefix with the real archive. The downloaded archive's hash matches the ORIGINAL intake record in full (`2601d9356f5e\u2026c68ff7`), and its contents match the intake description \u2014 the mirror page value is the artifact. No action needed; recorded so nobody re-chases it. (#1567)
2. The old intake record's "Blender 4.02, 90 / 88 objects" labels: the files read as Blender 4.2 with 66 / 67 scene objects. Counting/label deltas in the old record; every hard identifier matches. (#1567)

## Proof (paths to files, frames, test output)

- `docs/proof/2026-11-04/smutbase6-fidelity/parvati-src-front-20261104.png`
- `docs/proof/2026-11-04/smutbase6-fidelity/parvati-src-q34-20261104.png`
- `docs/proof/2026-11-04/smutbase6-fidelity/parvati-src-face-20261104.png`
- `docs/proof/2026-11-04/smutbase6-fidelity/vixen-src-front-20261104.png`
- `docs/proof/2026-11-04/smutbase6-fidelity/vixen-src-face-20261104.png`
- `docs/proof/2026-11-04/smutbase6-fidelity/inventory-parvati-recovered.json`
- `docs/proof/2026-11-04/smutbase6-fidelity/inventory-vixen-recovered.json`

Renders are from the recovered blends themselves, eye-checked: Parvati is the same character/face/steampunk outfit as `parvati-full.glb` piece for piece (goggles, chest plate, belt + hanging cloth, thigh pouch); Vixen is the same suit/face/proportions as the intact sibling `model.glb` (high collar, spiked neck emblem, pelvis emblem, knee guards). Release store verified via API: both rars whole + six blend parts, every asset's size + sha256 digest matches the local file; pull-back re-downloaded all six parts, reassembled both blends, and reproduced both whole-file sha256 values exactly (`cfc9864a\u2026` / `085d914c\u2026`), plus the Parvati rar re-download hash-matched (`2601d935\u2026c68ff7`).

## Self-check: I verified the result against the literal instruction

- [x] I verified the result against the literal instruction

Recovery was the blocker on "the FULL rigs that come with their own files" for these two: Parvati's 469-bone GZM rig + 474 shape keys + 123 packed images and Vixen's 450-bone GZM rig + 2,509 shape keys + 124 packed images are now in hand and stored on the release (asset digests verified, one pull-back hash-verified). The rebuilds themselves are NOT in this PR \u2014 they keep their place in the owner's order (Chatur \u2192 Ryusan \u2192 Megami \u2192 Menajerii). Nothing was deleted anywhere; the browser-download originals remain untouched.
"""

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
        print("FAIL", path, r.stderr[:500]); sys.exit(1)
    return json.loads(r.stdout) if r.stdout.strip() else {}

main = gh_api(f"repos/{REPO}/git/ref/heads/main")
base_sha = main["object"]["sha"]
base_commit = gh_api(f"repos/{REPO}/git/commits/{base_sha}")
base_tree = base_commit["tree"]["sha"]
print("base", base_sha, base_tree)

tree_items = []
for repo_path, local, inline in FILES:
    data = inline if inline is not None else open(local, "rb").read()
    blob = gh_api(f"repos/{REPO}/git/blobs", {"content": base64.b64encode(data).decode(), "encoding": "base64"})
    tree_items.append({"path": repo_path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print("blob", repo_path, len(data), blob["sha"][:10])

tree = gh_api(f"repos/{REPO}/git/trees", {"base_tree": base_tree, "tree": tree_items})
commit = gh_api(f"repos/{REPO}/git/commits", {
    "message": "SmutBase fidelity: Megami + Menajerii commission sources RECOVERED (byte-identical rars, blends inventoried, stored on release)",
    "tree": tree["sha"], "parents": [base_sha]})
print("commit", commit["sha"])
ref = gh_api(f"repos/{REPO}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
print("ref ok")
pr = gh_api(f"repos/{REPO}/pulls", {
    "title": "SmutBase fidelity: Megami + Menajerii source recovery \u2014 FOUND (byte-identical archives, stored)",
    "head": BRANCH, "base": "main", "body": BODY})
print("PR", pr["number"], pr["html_url"])
