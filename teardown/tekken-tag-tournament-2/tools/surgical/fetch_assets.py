#!/usr/bin/env python3
"""Download TTT2 release assets via the GitHub data API (binary path).

Pattern: GET /repos/{owner}/{repo}/releases/assets/{id} with
Accept: application/octet-stream (no redirects) -> 302 Location (signed URL)
-> unauthenticated streamed GET with Range resume support.

Credential: dynamic_credentials surrogate, attached ONLY to api.github.com.
The signed redirect target never receives auth.
"""
import os
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request

CONNECTION = "custom.github_pat"
OWNER = "mhvnsnt"
REPO = "western-heart"

# (asset_id, name, size) for release tag ttt2-7z-v1
ASSETS = [
    (636969185, "ttt2-500m.part_01", 524288000),
    (636982972, "ttt2-500m.part_02", 524288000),
    (637007845, "ttt2-500m.part_03", 524288000),
    (637017468, "ttt2-500m.part_04", 524288000),
    (637026996, "ttt2-500m.part_05", 524288000),
    (637036616, "ttt2-500m.part_06", 524288000),
    (637048809, "ttt2-500m.part_07", 524288000),
    (637062804, "ttt2-500m.part_08", 524288000),
    (637074446, "ttt2-500m.part_09", 524288000),
    (637087292, "ttt2-500m.part_10", 524288000),
    (637100555, "ttt2-500m.part_11", 524288000),
    (637112656, "ttt2-500m.part_12", 524288000),
    (637122432, "ttt2-500m.part_13", 524288000),
    (637135390, "ttt2-500m.part_14", 524288000),
    (637316953, "ttt2-500m.part_15", 524288000),
    (637370706, "ttt2-500m.part_16", 524288000),
    (637406074, "ttt2-500m.part_17", 524288000),
    (637486005, "ttt2-500m.part_18", 524288000),
    (637507555, "ttt2-500m.part_19", 524288000),
    (637543882, "ttt2-500m.part_20", 524288000),
    (637575069, "ttt2-500m.part_21", 524288000),
    (637589680, "ttt2-500m.part_22", 524288000),
    (637641451, "ttt2-500m.part_23", 524288000),
    (637653786, "ttt2-500m.part_24", 524288000),
    (637676883, "ttt2-500m.part_25", 524288000),
    (637690659, "ttt2-500m.part_26", 256424393),
    (648795103, "ttt2-loose-files.tar", 165601280),
]

CHUNK = 8 * 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # raise HTTPError(302) instead of following


def resolve_download_url(asset_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/assets/{asset_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/octet-stream",
                                                "User-Agent": "ttt2-extract-worker/1.0"})
    add_surrogate_to_request(req, CONNECTION, allowed_hosts=["api.github.com"])
    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(req, timeout=60)
        raise RuntimeError("expected 302 for asset download")
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location")
            if not loc:
                raise RuntimeError("302 without Location")
            return loc
        raise


def download_one(asset_id, name, size, dest_dir, retries=6):
    import requests
    dest = os.path.join(dest_dir, name)
    have = os.path.getsize(dest) if os.path.exists(dest) else 0
    if have == size:
        print(f"[skip] {name} complete", flush=True)
        return True
    if have > size:
        print(f"[warn] {name} oversize ({have}>{size}), restarting", flush=True)
        os.remove(dest)
        have = 0
    for attempt in range(1, retries + 1):
        try:
            loc = resolve_download_url(asset_id)
            headers = {"User-Agent": "ttt2-extract-worker/1.0"}
            if have:
                headers["Range"] = f"bytes={have}-"
            t0 = time.time()
            # (connect timeout, per-read timeout): a stalled socket raises
            # and we resume with Range on the next attempt.
            with requests.get(loc, headers=headers, stream=True,
                              timeout=(15, 45)) as resp:
                if have and resp.status_code != 206:
                    print(f"[warn] {name}: server ignored Range "
                          f"(got {resp.status_code}), restarting", flush=True)
                    if os.path.exists(dest):
                        os.remove(dest)
                    have = 0
                    continue  # re-resolve not needed; retry loop re-ranges
                mode = "ab" if have else "wb"
                with open(dest, mode) as f:
                    for buf in resp.iter_content(chunk_size=CHUNK):
                        if not buf:
                            continue
                        f.write(buf)
                        have += len(buf)
            final = os.path.getsize(dest)
            if final == size:
                dt = time.time() - t0
                mb = size / 1e6
                print(f"[ok] {name} ({mb:.0f}MB, {dt:.0f}s, {mb / max(dt, 1):.1f}MB/s)",
                      flush=True)
                return True
            print(f"[warn] {name}: size {final} != {size}, retrying", flush=True)
        except Exception as e:
            print(f"[err] {name} attempt {attempt}: {type(e).__name__}: {e}", flush=True)
            time.sleep(5 * attempt)
    return False


def main():
    dest_dir = sys.argv[1] if len(sys.argv) > 1 else "parts"
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    os.makedirs(dest_dir, exist_ok=True)
    ok = True
    for asset_id, name, size in ASSETS:
        if only and name not in only:
            continue
        if not download_one(asset_id, name, size, dest_dir):
            ok = False
            print(f"[FAIL] {name}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
