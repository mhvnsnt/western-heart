#!/usr/bin/env python3
"""Seekable virtual file over the 26 TTT2 release parts via HTTP Range.

Presents the concatenated parts as one contiguous byte stream so py7zr can
parse the 7z end-header and extract selected members without downloading
all 13.36GB. Signed-URL refresh + retries built in.

Usage:
    vf = PartVirtualFile(ASSETS)   # (asset_id, name, size) list
    with py7zr.SevenZipFile(vf, mode='r') as z: ...
"""
import io
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

import requests  # noqa: E402

CONNECTION = "custom.github_pat"
OWNER = "mhvnsnt"
REPO = "western-heart"
UA = "ttt2-extract-worker/1.0"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def resolve_download_url(asset_id):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/assets/{asset_id}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/octet-stream", "User-Agent": UA})
    add_surrogate_to_request(req, CONNECTION, allowed_hosts=["api.github.com"])
    try:
        urllib.request.build_opener(NoRedirect()).open(req, timeout=60)
        raise RuntimeError("expected 302")
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location")
            if loc:
                return loc
        raise


class PartVirtualFile(io.RawIOBase):
    """Read-only seekable binary stream over concatenated HTTP parts."""

    def __init__(self, assets, verbose=False):
        # assets: [(asset_id, name, size)]
        self.assets = assets
        self.sizes = [s for _, _, s in assets]
        self.starts = []
        off = 0
        for s in self.sizes:
            self.starts.append(off)
            off += s
        self.total = off
        self.pos = 0
        self._urls = {}   # idx -> signed url
        self.verbose = verbose
        self.bytes_fetched = 0

    # -- io interface --
    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, pos, whence=0):
        if whence == 0:
            self.pos = pos
        elif whence == 1:
            self.pos += pos
        elif whence == 2:
            self.pos = self.total + pos
        else:
            raise ValueError(whence)
        self.pos = max(0, min(self.pos, self.total))
        return self.pos

    # -- http --
    def _url(self, idx):
        if idx not in self._urls:
            if self.verbose:
                print(f"[vfile] resolving part {idx + 1}", flush=True)
            self._urls[idx] = resolve_download_url(self.assets[idx][0])
        return self._urls[idx]

    def _fetch(self, idx, lo, hi, retries=5):
        """Fetch [lo, hi) within part idx (absolute part-relative offsets)."""
        for attempt in range(retries):
            try:
                url = self._url(idx)
                headers = {"User-Agent": UA, "Range": f"bytes={lo}-{hi - 1}"}
                with requests.get(url, headers=headers, stream=True,
                                  timeout=(15, 45)) as r:
                    if r.status_code == 403:  # signed url expired
                        self._urls.pop(idx, None)
                        continue
                    r.raise_for_status()
                    data = r.content
                if len(data) != hi - lo:
                    raise IOError(f"short range read: {len(data)} != {hi - lo}")
                self.bytes_fetched += len(data)
                return data
            except Exception as e:
                if attempt == retries - 1:
                    raise
                if self.verbose:
                    print(f"[vfile] retry {attempt + 1} part{idx + 1}: {e}",
                          flush=True)
                self._urls.pop(idx, None)  # force re-resolve next try
                time.sleep(3 * (attempt + 1))
        raise IOError("unreachable")

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.total - self.pos
        n = min(n, self.total - self.pos)
        if n <= 0:
            return b""
        out = bytearray()
        while n > 0:
            idx = self._part_index(self.pos)
            part_start = self.starts[idx]
            lo = self.pos - part_start
            hi = min(lo + n, self.sizes[idx])
            # cap single fetch at 8MB to keep requests bounded
            hi = min(hi, lo + 8 * 1024 * 1024)
            out += self._fetch(idx, lo, hi)
            got = hi - lo
            self.pos += got
            n -= got
        return bytes(out)

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)

    def _part_index(self, pos):
        # binary search
        lo, hi = 0, len(self.starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo
