#!/usr/bin/env python3
"""Serve a git commit's tree over HTTP (no checkout), for boot-testing a
gh-pages build commit before pushing it.
    python3 tools/perf/serve_ref.py <commit> [port] [--prefix /western-heart/]
Big blobs are read from ~/.cache/wh-cook/src/<blob> when present
(cook step downloads), otherwise via git cat-file."""
import http.server, mimetypes, os, subprocess, sys, threading
commit = sys.argv[1]
port = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 8765
prefix = sys.argv[sys.argv.index("--prefix") + 1] if "--prefix" in sys.argv else "/western-heart/"
tree = {}
for line in subprocess.run(["git", "ls-tree", "-r", commit], capture_output=True, text=True, check=True).stdout.splitlines():
    meta, path = line.split("\t", 1)
    tree[path] = meta.split()[2]
SRC = os.path.expanduser("~/.cache/wh-cook/src")
lock = threading.Lock()
mimetypes.add_type("application/wasm", ".wasm"); mimetypes.add_type("model/gltf-binary", ".glb")
mimetypes.add_type("text/javascript", ".js"); mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("image/ktx2", ".ktx2")

def blob(obj):
    p = os.path.join(SRC, obj)
    if os.path.exists(p):
        return open(p, "rb").read()
    return subprocess.run(["git", "cat-file", "blob", obj], capture_output=True, check=True).stdout

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        from urllib.parse import unquote, urlsplit
        p = unquote(urlsplit(self.path).path)
        if not p.startswith(prefix):
            return self.send_error(404)
        rel = p[len(prefix):]
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        obj = tree.get(rel)
        if not obj:
            return self.send_error(404)
        data = blob(obj)
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(rel)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=600")  # same as GitHub Pages
        self.end_headers()
        self.wfile.write(data)

http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
