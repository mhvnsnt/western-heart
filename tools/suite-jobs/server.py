#!/usr/bin/env python3
"""server.py — creation-suite job server (stdlib only).

    python3 tools/suite-jobs/server.py [--port 8766] [--jobs-dir jobs]

POST /jobs        body = job spec JSON            -> {"id": ...} (202)
GET  /jobs                                       -> [{"id","tool","state"}, ...]
GET  /jobs/<id>                                  -> full status JSON
GET  /tools                                      -> installed/runnable tool registry

Jobs run in background threads via run_job.run_spec; the suite's Jobs panel
polls GET /jobs/<id> for live status. CORS is wide open for the local suite
pages (file:// and localhost origins).
"""
import argparse
import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import run_job

JOBS = {}
LOCK = threading.Lock()


def tool_registry():
    reg = []
    for tool in ["mb-lab", "gnm", "mpfb2-live", "gamerig", "mesh-edit"]:
        mod, err = run_job.load_runner(tool)
        reg.append({"tool": tool, "runnable": err is None,
                    "detail": err or f"{mod.__name__} loaded"})
    # blender availability (both pinned + live-path)
    import shutil
    reg.append({"tool": "blender-4.0.2",
                "runnable": os.path.isfile(os.path.expanduser(
                    "~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")),
                "detail": "pipeline standard"})
    reg.append({"tool": "blender-4.2+",
                "runnable": os.path.isfile("tools/mpfb2/vendor/blender42/blender"),
                "detail": "MPFB2 live path (fetch with --with-blender)"})
    return reg


def worker(job_id, spec):
    try:
        st = run_job.run_spec(spec["_spec_path"])
    except Exception as e:  # noqa: BLE001
        st = {"id": job_id, "state": "error", "error": str(e)}
    with LOCK:
        JOBS[job_id].update(st)
        JOBS[job_id]["state"] = st.get("state", "error")


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self._send(204, {})

    def do_GET(self):  # noqa: N802
        if self.path == "/tools":
            return self._send(200, tool_registry())
        if self.path == "/jobs":
            with LOCK:
                items = [{"id": j, "tool": JOBS[j].get("tool"),
                          "state": JOBS[j].get("state")} for j in JOBS]
            return self._send(200, items)
        if self.path.startswith("/jobs/"):
            jid = self.path.split("/jobs/")[1].split("/")[0]
            with LOCK:
                st = JOBS.get(jid)
            if not st:
                return self._send(404, {"error": "unknown job"})
            return self._send(200, st)
        return self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/jobs":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            spec = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:  # noqa: BLE001
            return self._send(400, {"error": f"bad JSON: {e}"})
        if "tool" not in spec:
            return self._send(400, {"error": "spec needs a 'tool' field"})
        jid = spec.get("id") or f"{spec['tool']}-{uuid.uuid4().hex[:8]}"
        spec["id"] = jid
        jobs_dir = self.server.jobs_dir
        os.makedirs(jobs_dir, exist_ok=True)
        spath = os.path.join(jobs_dir, jid + ".json")
        with open(spath, "w") as fh:
            json.dump(spec, fh, indent=1)
        spec["_spec_path"] = os.path.abspath(spath)
        with LOCK:
            JOBS[jid] = {"id": jid, "tool": spec["tool"], "state": "queued",
                         "queued_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "log": [f"queued {jid}"]}
        threading.Thread(target=worker, args=(jid, spec), daemon=True).start()
        return self._send(202, {"id": jid, "state": "queued"})

    def log_message(self, *a):  # keep stdout for job logs
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--jobs-dir", default="jobs")
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    srv.jobs_dir = a.jobs_dir
    print(f"suite job server on http://127.0.0.1:{a.port} (jobs dir: {a.jobs_dir})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
