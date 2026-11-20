#!/usr/bin/env python3
"""Streaming range reader over a GitHub Release whose payload is one file
split into ordered part assets (e.g. pakchunk0-WindowsNoEditor.pak.part-00..42).

The virtual file is the concatenation of the parts. Reads are served with
HTTP Range requests against the release-asset download URLs, so a caller can
read a 20 GB pak's footer/index/a single entry without staging the file.

Backends:
  - GitHubReleaseParts: parts are release assets on github.com.
  - LocalParts: parts are local files (used by the self-test and for any
    locally mirrored part set). Same read interface.

Auth: env GITHUB_TOKEN or GH_TOKEN, else `gh auth token`.

CLI:
  release_range.py info      --repo R --release TAG --parts-list transfer-list.txt
  release_range.py read      ... --offset O --len N --out FILE
  release_range.py sha256    ... --part I            (stream one whole part)
  release_range.py sha256    ... --offset O --len N  (stream a range)

parts-list format (one per line): tag|name|sha256|size   (extra fields ignored)
or a JSON manifest: {"assets":[{"name":..., "size":...}, ...]} / plain list.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

API = "https://api.github.com"


def get_token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip():
        return out.stdout.strip()
    raise SystemExit("no GitHub token: set GITHUB_TOKEN or run `gh auth login`")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHubReleaseParts:
    """Range reads over release assets identified by (repo, tag)."""

    def __init__(self, repo, tag, token=None):
        self.repo = repo
        self.tag = tag
        self.token = token or get_token()
        self.assets = {}          # name -> asset id
        self._url_cache = {}      # name -> (signed_url, fetched_epoch)
        self._opener_redir = urllib.request.build_opener()
        self._opener_noredir = urllib.request.build_opener(_NoRedirect)
        self._resolve_release()

    def _api(self, url):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "wh-release-range/1.0",
        })
        with self._opener_redir.open(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def _resolve_release(self):
        page = 1
        rel = self._api(f"{API}/repos/{self.repo}/releases/tags/{self.tag}")
        self.release_id = rel["id"]
        while True:
            assets = self._api(
                f"{API}/repos/{self.repo}/releases/{self.release_id}/assets"
                f"?per_page=100&page={page}")
            if not assets:
                break
            for a in assets:
                self.assets[a["name"]] = a["id"]
            if len(assets) < 100:
                break
            page += 1

    def _signed_url(self, name):
        url, ts = self._url_cache.get(name, (None, 0))
        if url and time.time() - ts < 240:  # signed URLs live ~minutes; stay safe
            return url
        aid = self.assets[name]
        req = urllib.request.Request(
            f"{API}/repos/{self.repo}/releases/assets/{aid}", headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/octet-stream",
                "User-Agent": "wh-release-range/1.0",
            })
        try:
            self._opener_noredir.open(req, timeout=60)
            raise RuntimeError("expected redirect from asset endpoint")
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                url = e.headers["Location"]
            else:
                raise
        self._url_cache[name] = (url, time.time())
        return url

    def read_part_range(self, name, start, end_inclusive):
        """Read bytes [start, end] of one part asset, with retries."""
        want = end_inclusive - start + 1
        last_err = None
        for attempt in range(5):
            try:
                url = self._signed_url(name)
                req = urllib.request.Request(url, headers={
                    "Range": f"bytes={start}-{end_inclusive}",
                    "User-Agent": "wh-release-range/1.0",
                })
                with self._opener_redir.open(req, timeout=300) as r:
                    data = r.read()
                if len(data) != want:
                    raise IOError(f"short read on {name}: got {len(data)} want {want}")
                return data
            except Exception as e:  # signed URL may have expired; force re-resolve
                last_err = e
                self._url_cache.pop(name, None)
                time.sleep(2 * (attempt + 1))
        raise IOError(f"read_part_range failed for {name} [{start}-{end_inclusive}]: {last_err}")


class LocalParts:
    def __init__(self, paths):
        self.paths = paths  # name -> local path
        self.assets = {n: n for n in paths}

    def read_part_range(self, name, start, end_inclusive):
        with open(self.paths[name], "rb") as f:
            f.seek(start)
            return f.read(end_inclusive - start + 1)


class ReleaseFile:
    """A virtual read-only file = ordered concatenation of named parts."""

    def __init__(self, backend, parts):
        """parts: list of (name, size) in order."""
        self.backend = backend
        self.parts = parts
        self._bounds = []
        off = 0
        for name, size in parts:
            self._bounds.append((off, off + size, name))
            off += size
        self.size = off

    def read(self, offset, length):
        if offset < 0 or length < 0 or offset + length > self.size:
            raise ValueError(f"read out of range: off={offset} len={length} size={self.size}")
        out = bytearray()
        pos = offset
        end = offset + length
        for pstart, pend, name in self._bounds:
            if pend <= pos:
                continue
            if pstart >= end:
                break
            lo = max(pos, pstart) - pstart
            hi = min(end, pend) - pstart - 1
            out += self.backend.read_part_range(name, lo, hi)
            pos += hi - lo + 1
        if len(out) != length:
            raise IOError(f"virtual read short: got {len(out)} want {length}")
        return bytes(out)

    def stream_sha256(self, offset, length, chunk=1 << 20):
        h = hashlib.sha256()
        done = 0
        while done < length:
            n = min(chunk, length - done)
            h.update(self.read(offset + done, n))
            done += n
        return h.hexdigest()


def load_parts_list(path):
    """Return list of (name, size) from a transfer-list or JSON manifest."""
    with open(path) as f:
        text = f.read()
    parts = []
    if text.lstrip().startswith(("{", "[")):
        data = json.loads(text)
        assets = data.get("assets", data) if isinstance(data, dict) else data
        for a in assets:
            parts.append((a["name"], int(a["size"])))
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            fields = line.split("|")
            # tag|name|sha256|size
            parts.append((fields[1], int(fields[3])))
    parts.sort(key=lambda p: p[0])
    return parts


def selftest():
    """Synthetic 3-part local file: cross-boundary reads + sha of a range."""
    import tempfile
    payload = bytes((i * 7 + 3) % 251 for i in range(1000))
    chunks = [payload[:300], payload[300:750], payload[750:]]
    with tempfile.TemporaryDirectory() as td:
        paths = {}
        parts = []
        for i, c in enumerate(chunks):
            p = os.path.join(td, f"f.part-{i:02d}")
            with open(p, "wb") as f:
                f.write(c)
            paths[f"f.part-{i:02d}"] = p
            parts.append((f"f.part-{i:02d}", len(c)))
        rf = ReleaseFile(LocalParts(paths), parts)
        assert rf.size == 1000
        assert rf.read(0, 1000) == payload
        assert rf.read(299, 3) == payload[299:302]      # spans part 0/1
        assert rf.read(749, 2) == payload[749:751]      # spans part 1/2
        assert rf.read(999, 1) == payload[999:]
        assert rf.stream_sha256(100, 500) == hashlib.sha256(payload[100:600]).hexdigest()
    print("selftest OK")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("info", "read", "sha256"):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument("--release", required=True)
        p.add_argument("--parts-list", required=True)
    sub.choices["read"].add_argument("--offset", type=int, required=True)
    sub.choices["read"].add_argument("--len", type=int, required=True)
    sub.choices["read"].add_argument("--out", required=True)
    sub.choices["sha256"].add_argument("--part", type=int)
    sub.choices["sha256"].add_argument("--offset", type=int)
    sub.choices["sha256"].add_argument("--len", type=int)
    a = ap.parse_args(argv)

    parts = load_parts_list(a.parts_list)
    backend = GitHubReleaseParts(a.repo, a.release)
    missing = [n for n, _ in parts if n not in backend.assets]
    if missing:
        print(f"WARNING missing on release: {missing}", file=sys.stderr)
    rf = ReleaseFile(backend, [(n, s) for n, s in parts if n in backend.assets])

    if a.cmd == "info":
        print(json.dumps({"size": rf.size, "parts": len(rf.parts),
                          "present": [n for n, _ in rf.parts]}, indent=1))
    elif a.cmd == "read":
        data = rf.read(a.offset, a.len)
        with open(a.out, "wb") as f:
            f.write(data)
        print(f"wrote {len(data)} bytes to {a.out}")
    elif a.cmd == "sha256":
        if a.part is not None:
            name, size = parts[a.part]
            off = sum(s for _, s in parts[:a.part])
            print(f"{rf.stream_sha256(off, size)}  {name}")
        else:
            print(rf.stream_sha256(a.offset, a.len))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
