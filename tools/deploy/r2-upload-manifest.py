#!/usr/bin/env python3
"""tools/deploy/r2-upload-manifest.py — build the Cloudflare R2 upload manifest.

Owner decision 2026-10-26 ("Split it: Pages shell + GLBs on R2"): the Pages
deploy ships the shell only (build_pages.py --shell-only); every other model
loads at runtime from R2. This script lists every model the R2 bucket must
hold, so the upload lane has a complete, verifiable checklist.

The manifest is built from LIVE GITHUB, never from local disk:
  * the file list is the same reference closure build_pages.py computes
    (compute_deploy_files, full mode) over the given ref;
  * sizes and blob SHAs come from the git objects / GitHub trees API;
  * `release_asset` is filled where a release asset matches the model by
    (name, size) — the Releases store is the store of record for many
    Tripo originals. Where no release asset matches, `source` is the
    pinned repo blob on main, which the upload lane fetches via git/raw —
    still GitHub, never local disk.

Does NOT upload anything and does NOT touch R2 (no bucket exists yet —
Cloudflare signup is owner-only; see tools/deploy/DEPLOY-SPLIT.md).

    python3 tools/deploy/r2-upload-manifest.py [--ref origin/main] [--out tools/deploy/r2-upload-manifest.json]
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pages  # noqa: E402  (shares compute_deploy_files + blob_sizes)


def gh_json(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def release_index():
    """(asset name, asset size) -> release tag, from every release.

    Best-effort: the releases list endpoint carries each release's assets
    inline. A model matches a release asset only on name AND size, so a
    same-named different build never masquerades as the deploy file.
    """
    index = {}
    rels = gh_json(f"repos/{build_pages.REPO}/releases?per_page=100")
    if not rels:
        print("warning: could not list releases; release_asset will be null throughout")
        return index
    for rel in rels:
        for a in rel.get("assets") or []:
            index.setdefault((a.get("name"), a.get("size")), rel.get("tag_name"))
    return index


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sha = build_pages.git("rev-parse", a.ref).strip()
    sizes, oids = build_pages.blob_sizes(sha)
    build_pages.prefetch_text(oids)
    files, _ = build_pages.compute_deploy_files(sha, sizes, oids)
    bundled = set(build_pages.shell_bundled_models(sha))
    # Drift check: the JS single source of truth vs the Python fallback.
    if set(build_pages.SHELL_BUNDLED_MODELS) != bundled:
        print("WARNING: asset-config.js bundled list != build_pages.py fallback list")
        print("  js:  ", sorted(bundled))
        print("  py:  ", sorted(build_pages.SHELL_BUNDLED_MODELS))
    models = [f for f in files if f.lower().endswith((".glb", ".gltf"))]
    rel_index = release_index()
    entries = []
    for f in models:
        base = os.path.basename(f)
        tag = rel_index.get((base, sizes[f]))
        entries.append({
            "repo_path": f,
            "r2_key": f,
            "bytes": sizes[f],
            "blob_sha": oids[f],
            "bundled_in_shell": f in bundled,
            "release_asset": {"tag": tag, "name": base} if tag else None,
            "source": (f"release {tag}/{base}" if tag
                       else f"repo {build_pages.REPO}@{sha[:9]}:{f} (blob {oids[f][:9]})"),
        })
    total = sum(e["bytes"] for e in entries)
    remote = sum(e["bytes"] for e in entries if not e["bundled_in_shell"])
    doc = {
        "format": "wh-r2-upload-manifest/1",
        "ref": a.ref,
        "commit": sha,
        "repo": build_pages.REPO,
        "models": len(entries),
        "bytes": total,
        "remote_bytes": remote,
        "r2_free_tier_bytes": 10 * 1024 ** 3,
        "fits_free_tier": total <= 10 * 1024 ** 3,
        "release_matched": sum(1 for e in entries if e["release_asset"]),
        "tool": "tools/deploy/r2-upload-manifest.py",
        "note": ("Upload every entry to the R2 bucket at its r2_key, from the "
                 "listed source (release asset where matched, else the pinned "
                 "repo blob — fetch via git/raw, never from local disk). "
                 "Bundled models ship on Pages too; they are listed so the "
                 "loader has one remote base for every model."),
        "entries": entries,
    }
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "r2-upload-manifest.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=1)
    print(f"ref {a.ref} = {sha}: {len(entries)} models, {total/1e6:.1f} MB "
          f"({remote/1e6:.1f} MB remote-only), {doc['release_matched']} release-matched")
    print(f"fits R2 free tier (10 GB): {doc['fits_free_tier']}")
    print("manifest:", out)


if __name__ == "__main__":
    main()
