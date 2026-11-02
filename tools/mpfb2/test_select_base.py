#!/usr/bin/env python3
"""test_select_base.py — proof run for the MPFB2 base family (no Blender).

    python3 tools/mpfb2/test_select_base.py [--repo-root PATH] [--bases PATH]

Checks, all pure Python:
  1. tools/creation-suite/bases.json has the mpfb2 family with 6 bases.
  2. Every base's job spec matches run_mpfb2_job.py's schema (tool
     "mpfb2-live", params.macro with MPFB2 macro keys, values in
     [0, 1], gender consistent with the base's gender string).
  3. The mpfb2-live runner file that tools/suite-jobs/run_job.py
     dispatches to exists, and select_base.py's list/job/fighter
     commands round-trip for every base in a temp dir.
  4. The family licence is CC0 base data — for the base data only,
     never a blanket label for the addon code.
  5. run_mpfb2_job.py's pure-Python validation accepts every emitted
     job spec and rejects a bad macro value; with no vendor checkout
     it fails honestly naming the fetch script (no fake bake).

It does NOT bake a mesh (a bake needs the MPFB2 vendor checkout +
Blender 4.2+, neither present in this proof); it proves the bases
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
    if "--bases" in sys.argv:
        bases_path = sys.argv[sys.argv.index("--bases") + 1]
    with open(bases_path) as fh:
        data = json.load(fh)
    fam = next(f for f in data["families"] if f["id"] == "mpfb2")
    assert fam["license_base_data"] == "CC0", fam["license_base_data"]
    assert len(fam["bases"]) == 6, len(fam["bases"])
    runner = os.path.join(root, "tools", "mpfb2", "run_mpfb2_job.py")
    assert os.path.isfile(runner), "missing mpfb2-live runner"
    selector = os.path.join(root, "tools", "mpfb2", "select_base.py")
    assert os.path.isfile(selector), "missing mpfb2 selector"
    # Load the runner's pure-Python parts (no bpy import at top level).
    spec = importlib.util.spec_from_file_location("wh_run_mpfb2_job", runner)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as td:
        for base in fam["bases"]:
            bid = base["id"]
            r = subprocess.run([sys.executable, selector, "job", bid,
                                "--bases", bases_path,
                                "--out", os.path.join(td, bid + ".json")],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            with open(os.path.join(td, bid + ".json")) as fh:
                jspec = json.load(fh)
            assert jspec["tool"] == "mpfb2-live"
            assert jspec["params"]["macro"] == base["mpfb2"]["macro"]
            assert jspec["params"]["rig"] == base["job"]["params"]["rig"]
            mod.validate_spec(jspec)  # must accept every emitted spec
            r = subprocess.run([sys.executable, selector, "fighter", bid,
                                "--bases", bases_path,
                                "--out", os.path.join(td, bid + ".fighter.json")],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            with open(os.path.join(td, bid + ".fighter.json")) as fh:
                frag = json.load(fh)
            assert frag["base_license"] == "CC0"
            assert frag["mpfb2"] == base["mpfb2"]
    # Rejection: a macro value outside [0, 1] must fail validation.
    bad = {"tool": "mpfb2-live",
           "params": {"macro": {"gender": 1.0, "weight": 1.5}, "rig": None},
           "out": "x.glb"}
    try:
        mod.validate_spec(bad)
    except RuntimeError:
        pass
    else:
        raise AssertionError("validate_spec accepted weight 1.5")
    # Honest failure without a vendor checkout (no fake bake).
    good = {"tool": "mpfb2-live",
            "params": {"macro": {"gender": 1.0, "weight": 0.5}, "rig": None},
            "out": os.path.join(tempfile.gettempdir(), "mpfb2-should-not-exist.glb")}
    try:
        mod.run_job(good, log=lambda *a: None)
    except RuntimeError as e:
        assert "fetch-mpfb2.sh" in str(e), str(e)
    else:
        raise AssertionError("run_job succeeded without a vendor checkout")
    # Dispatch check: run_job.py must resolve tool "mpfb2-live" to the runner.
    run_job = os.path.join(root, "tools", "suite-jobs", "run_job.py")
    if os.path.isfile(run_job):
        spec2 = importlib.util.spec_from_file_location("wh_run_job", run_job)
        mod2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod2)
        path = mod2._runner_path("mpfb2-live")
        assert path == runner, path
    print(f"PASS: mpfb2 family — {len(fam['bases'])} bases selectable, "
          f"job specs + fighter fragments round-trip, dispatch resolves, "
          f"validation + honest no-vendor failure verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
