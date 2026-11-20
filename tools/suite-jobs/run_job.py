#!/usr/bin/env python3
"""run_job.py — one-shot creation-suite job runner (no server needed).

Usage:
    python3 tools/suite-jobs/run_job.py --spec jobs/<name>.json [--status-dir jobs]

Reads the job spec, dispatches on spec["tool"], runs it, writes
<spec>.status.json with {state: done|error, out, log, timings}.
Exit 0 on done, 1 on error.
"""
import argparse
import datetime
import importlib.util
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))


def _runner_path(tool):
    """Map tool name -> runner script path. Convention: tools/<tool>/run_<tool>_job.py,
    with a few explicit overrides."""
    overrides = {
        "mb-lab": "tools/mb-lab/run_mblab_job.py",
        "gnm": "tools/gnm/run_gnm_job.py",
        "mpfb2-live": "tools/mpfb2/run_mpfb2_job.py",
        "gamerig": "tools/auto_rig/backends/gamerig_backend.py",
    }
    if tool in overrides:
        return os.path.join(REPO, overrides[tool])
    cand = os.path.join(REPO, "tools", tool, f"run_{tool}_job.py")
    return cand if os.path.isfile(cand) else None


def load_runner(tool):
    path = _runner_path(tool)
    if not path or not os.path.isfile(path):
        return None, f"no runner for tool {tool!r} (looked for {path})"
    name = f"wh_job_{tool.replace('-', '_')}"
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except Exception as e:  # noqa: BLE001
        return None, f"runner import failed for {tool!r}: {e}"


def run_spec(spec_path, status_dir=None):
    t0 = time.time()
    log = []

    def say(msg):
        line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
        log.append(line)
        print(line, flush=True)

    with open(spec_path) as fh:
        spec = json.load(fh)
    tool = spec.get("tool")
    job_id = spec.get("id") or os.path.splitext(os.path.basename(spec_path))[0]
    say(f"job {job_id}: tool={tool}")

    status = {
        "id": job_id, "tool": tool, "state": "running",
        "spec": os.path.abspath(spec_path), "out": spec.get("out"),
        "started": datetime.datetime.now().isoformat(timespec="seconds"),
        "log": log,
    }

    mod, err = load_runner(tool)
    if err:
        status.update(state="error", error=err)
        say(f"ERROR: {err}")
    else:
        try:
            say(f"dispatching to {mod.__name__}")
            out = None
            if hasattr(mod, "run_job"):
                out = mod.run_job(spec, say)
            elif hasattr(mod, "main"):
                # argparse-style runner: emulate CLI
                sys.argv = [mod.__file__, "--spec", os.path.abspath(spec_path)]
                if spec.get("out"):
                    sys.argv += ["--out", spec["out"]]
                out = mod.main()
            else:
                raise RuntimeError("runner has neither run_job(spec, log) nor main()")
            status.update(state="done", out=out or spec.get("out"))
            say(f"done -> {status['out']}")
        except Exception:  # noqa: BLE001
            status.update(state="error", error=traceback.format_exc(limit=8))
            say("ERROR:\n" + traceback.format_exc(limit=8))

    status["elapsed_s"] = round(time.time() - t0, 1)
    status["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    sdir = status_dir or os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(sdir, exist_ok=True)
    spath = os.path.join(sdir, job_id + ".status.json")
    with open(spath, "w") as fh:
        json.dump(status, fh, indent=1)
    say(f"status -> {spath}")
    return status


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="job spec JSON path")
    ap.add_argument("--status-dir", default=None)
    a = ap.parse_args(argv)
    st = run_spec(a.spec, a.status_dir)
    return 0 if st["state"] == "done" else 1


if __name__ == "__main__":
    sys.exit(main())
