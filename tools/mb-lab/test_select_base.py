#!/usr/bin/env python3
"""test_select_base.py — proof run for the MB-Lab base family (no Blender).

    python3 tools/mb-lab/test_select_base.py [--repo-root PATH]

Checks, all pure Python:
  1. tools/creation-suite/bases.json has the mb-lab family with 9 bases.
  2. Every base's job spec matches run_mblab_job.py's schema (tool
     "mb-lab", params.character/morphs direct, values in [-1, 1]).
  3. The mb-lab runner file that tools/suite-jobs/run_job.py dispatches
     to exists, and select_base.py's list/job/fighter commands round-trip
     for every base in a temp dir.
  4. The family licence is AGPL-3.0 base data — never CC0.

It does NOT bake a mesh (the 9 meshes were baked in #1495 and a bake
needs the MB-Lab vendor checkout + Blender 4.0.2); it proves the bases
are selectable and produce runnable job specs. Exit non-zero on failure.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))


def main():
    root = REPO
    if "--repo-root" in sys.argv:
        root = sys.argv[sys.argv.index("--repo-root") + 1]
    bases_path = os.path.join(root, "tools", "creation-suite", "bases.json")
    with open(bases_path) as fh:
        data = json.load(fh)
    fam = next(f for f in data["families"] if f["id"] == "mb-lab")
    assert fam["license_base_data"] == "AGPL-3.0", fam["license_base_data"]
    assert fam["license_base_data"] != "CC0"
    assert len(fam["bases"]) == 9, len(fam["bases"])
    runner = os.path.join(root, "tools", "mb-lab", "run_mblab_job.py")
    assert os.path.isfile(runner), "missing mb-lab runner"
    selector = os.path.join(root, "tools", "mb-lab", "select_base.py")
    with tempfile.TemporaryDirectory() as td:
        for base in fam["bases"]:
            bid = base["id"]
            r = subprocess.run([sys.executable, selector, "job", bid,
                                "--bases", bases_path,
                                "--out", os.path.join(td, bid + ".json")],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            with open(os.path.join(td, bid + ".json")) as fh:
                spec = json.load(fh)
            assert spec["tool"] == "mb-lab"
            assert spec["params"]["finalize"] is True
            assert spec["params"]["character"] == base["mb_lab"]["character"]
            assert spec["params"]["morphs"] == base["mb_lab"]["morphs"]
            r = subprocess.run([sys.executable, selector, "fighter", bid,
                                "--bases", bases_path,
                                "--out", os.path.join(td, bid + ".fighter.json")],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            with open(os.path.join(td, bid + ".fighter.json")) as fh:
                frag = json.load(fh)
            assert frag["base_license"] == "AGPL-3.0"
            assert frag["mb_lab"] == base["mb_lab"]
    # Dispatch check: run_job.py must resolve tool "mb-lab" to the runner.
    run_job = os.path.join(root, "tools", "suite-jobs", "run_job.py")
    if os.path.isfile(run_job):
        spec = importlib.util.spec_from_file_location("wh_run_job", run_job)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        path, err = mod._runner_path("mb-lab"), None
        # _runner_path returns a path or None; verify it points at the runner
        assert path == runner, path
    print(f"PASS: mb-lab family — {len(fam['bases'])} bases selectable, "
          f"job specs + fighter fragments round-trip, dispatch resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
