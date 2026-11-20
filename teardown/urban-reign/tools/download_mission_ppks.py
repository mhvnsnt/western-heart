#!/usr/bin/env python3
"""UR stages/missions decode, follow-on lane — download the 97 missing mission PPKs.
Source: Jay's own repo mhvnsnt/western-heart, teardown/urban-reign/missions/ppks/,
via raw.githubusercontent.com with the gh auth token. No ISO, no piracy/ROM sites.
Verifies each file by byte size AND git blob SHA (the listing's `sha` is the
git blob hash: sha1("blob <size>\\0" + content)).
"""
import json, hashlib, os, subprocess, sys, time
from pathlib import Path

LIST = Path("/tmp/mission-ppks-list.json")
OUT = Path.home() / "workspace/urban-reign-redux/decoded/inputs/mission_ppks"
OUT.mkdir(parents=True, exist_ok=True)
TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
BASE = "https://raw.githubusercontent.com/mhvnsnt/western-heart/main/teardown/urban-reign/missions/ppks/"
HAVE = {"mission001.ppk", "mission002.ppk", "mission100.ppk"}  # already in inputs/, Lane 4

rows = [json.loads(l) for l in open(LIST)]
missing = [r for r in rows if r["name"] not in HAVE]
manifest_path = OUT / "download-manifest.json"
manifest = {}
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())

def git_blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob %d\x00" % len(data))
    h.update(data)
    return h.hexdigest()

done, failed = 0, []
for i, r in enumerate(missing, 1):
    name, size, sha = r["name"], r["size"], r["sha"]
    dest = OUT / name
    if dest.exists() and dest.stat().st_size == size:
        data = dest.read_bytes()
        if git_blob_sha(data) == sha:
            manifest[name] = {"size": size, "git_sha": sha, "sha256": hashlib.sha256(data).hexdigest(), "status": "verified"}
            done += 1
            continue
    ok = False
    for attempt in (1, 2, 3):
        cp = subprocess.run(["curl", "-sL", "--fail", "-H", f"Authorization: Bearer {TOKEN}",
                             "-o", str(dest), BASE + name],
                            capture_output=True, text=True)
        if cp.returncode == 0 and dest.exists() and dest.stat().st_size == size:
            data = dest.read_bytes()
            if git_blob_sha(data) == sha:
                manifest[name] = {"size": size, "git_sha": sha, "sha256": hashlib.sha256(data).hexdigest(), "status": "verified"}
                ok = True
                break
        time.sleep(2 * attempt)
    if ok:
        done += 1
    else:
        failed.append(name)
        manifest[name] = {"size": size, "git_sha": sha, "status": "FAILED"}
    manifest_path.write_text(json.dumps(manifest, indent=2))
    if i % 10 == 0 or i == len(missing):
        print(f"{i}/{len(missing)} done={done} failed={len(failed)}", flush=True)

print(f"DONE downloaded/verified={done} failed={failed}")
manifest_path.write_text(json.dumps(manifest, indent=2))
sys.exit(0 if not failed else 1)
