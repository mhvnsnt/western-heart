"""
ScriptClient: HTTP client for the SCRIPT inference service.

Implements the REST contract specified in
docs/research/SCRIPT-INTEGRATION-2026-10-23.md Sec 4.2:

  POST /v1/generate {prompt, style_hints, seed, duration_s, fps, model,
                     constraints} -> 202 {job_id, status}
  GET  /v1/jobs/{id}              -> {status, artifacts?, metrics?}
  GET  /v1/jobs/{id}/trajectory   -> .npz {states, actions, fps, ...}

StubScriptServer implements the same contract in-process with synthetic
trajectories so the plumbing is testable with no GPU and no weights.

Std-lib only (urllib).
"""

from __future__ import annotations

import io
import json
import threading
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional

import numpy as np

from script_contract import (
    ScriptTrajectory,
    make_synthetic_trajectory,
)
from prompt_builder import JobSpec


class ScriptServiceError(RuntimeError):
    pass


class ScriptClient:
    """Client for a SCRIPT inference service (real or stub)."""

    def __init__(self, base_url: str, timeout_s: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        url = self.base_url + path
        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(
            url, data=body, method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                if resp.status == 204:
                    return {}
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise ScriptServiceError(f"{method} {path}: HTTP {e.code} {e.reason}")
        except urllib.error.URLError as e:
            raise ScriptServiceError(f"{method} {path}: {e.reason}")

    def generate(self, job: JobSpec) -> str:
        payload = {
            "prompt": job.prompt,
            "style_hints": job.style_hints,
            "seed": job.seed,
            "duration_s": job.duration_s,
            "fps": 30,
            "model": job.model,
            "constraints": job.constraints,
            "archetype": job.archetype,
        }
        resp = self._request("POST", "/v1/generate", payload)
        if "job_id" not in resp:
            raise ScriptServiceError(f"bad generate response: {resp}")
        return resp["job_id"]

    def job_status(self, job_id: str) -> dict:
        return self._request("GET", f"/v1/jobs/{job_id}")

    def wait_for_job(self, job_id: str, poll_s: float = 0.2,
                     timeout_s: float = 60.0) -> dict:
        deadline = time.time() + timeout_s
        while True:
            status = self.job_status(job_id)
            if status.get("status") in ("done", "failed"):
                return status
            if time.time() > deadline:
                raise ScriptServiceError(f"job {job_id} timed out")
            time.sleep(poll_s)

    def fetch_trajectory(self, job_id: str) -> ScriptTrajectory:
        url = self.base_url + f"/v1/jobs/{job_id}/trajectory"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read()
        except urllib.error.URLError as e:
            raise ScriptServiceError(f"fetch trajectory: {e.reason}")
        buf = io.BytesIO(raw)
        data = np.load(buf, allow_pickle=False)
        metrics_raw = data["metrics_json"] if "metrics_json" in data else None
        metrics = json.loads(str(metrics_raw)) if metrics_raw is not None else {}
        traj = ScriptTrajectory(
            states=np.asarray(data["states"]),
            actions=np.asarray(data["actions"]),
            fps=int(data["fps"]),
            prompt=str(data["prompt"]),
            seed=int(data["seed"]),
            model=str(data["model"]),
            metrics={k: float(v) for k, v in metrics.items()},
        )
        return traj.validate()

    def generate_trajectory(self, job: JobSpec, timeout_s: float = 60.0) -> ScriptTrajectory:
        job_id = self.generate(job)
        status = self.wait_for_job(job_id, timeout_s=timeout_s)
        if status.get("status") != "done":
            raise ScriptServiceError(f"job {job_id} failed: {status}")
        return self.fetch_trajectory(job_id)


# ---------------------------------------------------------------------------
# In-process stub server (tests / offline plumbing only)
# ---------------------------------------------------------------------------

class _StubHandler(BaseHTTPRequestHandler):
    server_version = "StubScriptServer/0.1"

    def _send_json(self, code: int, obj: dict):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # quiet
        pass

    def do_POST(self):
        if self.path == "/v1/generate":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            job_id = self.server.create_job(payload)  # type: ignore[attr-defined]
            self._send_json(202, {"job_id": job_id, "status": "queued"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_GET(self):
        parts = self.path.strip("/").split("/")
        # /v1/jobs/{id}  or  /v1/jobs/{id}/trajectory
        if len(parts) >= 3 and parts[0] == "v1" and parts[1] == "jobs":
            job_id = parts[2]
            if len(parts) == 4 and parts[3] == "trajectory":
                blob = self.server.get_trajectory_blob(job_id)  # type: ignore[attr-defined]
                if blob is None:
                    self._send_json(404, {"error": "no trajectory"})
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(blob)))
                self.end_headers()
                self.wfile.write(blob)
                return
            status = self.server.get_status(job_id)  # type: ignore[attr-defined]
            if status is None:
                self._send_json(404, {"error": "no such job"})
                return
            self._send_json(200, status)
        else:
            self._send_json(404, {"error": "not found"})


class StubScriptServer:
    """Same REST contract as the real service; synthetic trajectories."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self._httpd = HTTPServer((host, port), _StubHandler)
        self._httpd.create_job = self.create_job  # type: ignore[attr-defined]
        self._httpd.get_status = self.get_status  # type: ignore[attr-defined]
        self._httpd.get_trajectory_blob = self.get_trajectory_blob  # type: ignore[attr-defined]
        self._jobs: Dict[str, dict] = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self._httpd.server_address
        return f"http://{host}:{port}"

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self._httpd.shutdown()
        self._thread.join(timeout=5)

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()

    def create_job(self, payload: dict) -> str:
        with self._lock:
            self._counter += 1
            job_id = f"stub-job-{self._counter}"
            seed = int(payload.get("seed", 0))
            duration_s = float(payload.get("duration_s", 2.0))
            horizon = max(4, int(round(duration_s * 30)))
            traj = make_synthetic_trajectory(
                horizon=horizon, seed=seed,
                prompt=str(payload.get("prompt", "")),
            )
            buf = io.BytesIO()
            np.savez(
                buf,
                states=traj.states, actions=traj.actions,
                fps=np.int64(traj.fps),
                prompt=np.array(traj.prompt),
                seed=np.int64(traj.seed),
                model=np.array(payload.get("model", "script-base")),
                # dicts don't survive npz; store metrics as a JSON string
                metrics_json=np.array(json.dumps({"synthetic": 1.0})),
            )
            self._jobs[job_id] = {
                "status": "done",
                "artifacts": {"trajectory_npz": f"/v1/jobs/{job_id}/trajectory"},
                "metrics": {"synthetic": 1.0},
                "_blob": buf.getvalue(),
            }
            return job_id

    def get_status(self, job_id: str) -> Optional[dict]:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        return {k: v for k, v in job.items() if not k.startswith("_")}

    def get_trajectory_blob(self, job_id: str) -> Optional[bytes]:
        job = self._jobs.get(job_id)
        return None if job is None else job["_blob"]
