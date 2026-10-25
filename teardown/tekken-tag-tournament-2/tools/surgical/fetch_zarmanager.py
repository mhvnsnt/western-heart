#!/usr/bin/env python3
"""Fetch the Xbox 360 container modules (GodPackage, StfsPackage).

Source: dfdx047/ZarManager on GitHub (formerly dfdevx2/zarmanager).
Only core/xbox/god.py and core/xbox/stfs.py are fetched (stdlib-only);
they are NOT vendored here because the upstream license is unverified
(see teardown docs PULL-LOG). Run this once per machine:

    python3 fetch_zarmanager.py [destdir]

Then add destdir to sys.path (or PYTHONPATH) so `from core.xbox.god import
GodPackage` resolves. The surgical scripts expect this layout.
"""
import base64
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

REPO_ID = "1337839359"  # dfdx047/ZarManager (numeric id survives renames)
CONNECTION = "custom.github_pat"
FILES = ["core/xbox/god.py", "core/xbox/stfs.py"]


def api_get(path):
    url = f"https://api.github.com/repositories/{REPO_ID}/contents/{path}?ref=main"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ttt2-surgical/1.0",
    })
    add_surrogate_to_request(req, CONNECTION, allowed_hosts=["api.github.com"])
    with urllib.request.urlopen(req, timeout=60) as r:
        import json
        return json.load(r)


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else "zarmanager"
    for f in FILES:
        d = api_get(f)
        content = base64.b64decode(d["content"]).decode("utf-8")
        out = os.path.join(dest, f)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as fh:
            fh.write(content)
        print(f"saved {out} ({len(content)} bytes)")
    for init in [os.path.join(dest, "core/__init__.py"),
                 os.path.join(dest, "core/xbox/__init__.py")]:
        open(init, "a").close()
    print("done. add %s to sys.path / PYTHONPATH" % os.path.abspath(dest))


if __name__ == "__main__":
    main()
