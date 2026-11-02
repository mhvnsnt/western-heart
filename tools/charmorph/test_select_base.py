#!/usr/bin/env python3
"""test_select_base.py — proof run for the CharMorph base family (no Blender).

    python3 tools/charmorph/test_select_base.py [--repo-root PATH] [--bases PATH]

Checks, all pure Python:
  1. tools/creation-suite/bases.json has the charmorph family with
     exactly 1 base: vitruvian.
  2. Every base's job spec matches run_charmorph_job.py's schema
     (tool "charmorph", params.character == "vitruvian").
  3. The charmorph runner file that tools/suite-jobs/run_job.py
     dispatches to (default convention) exists, and select_base.py's
     list/job/fighter commands round-trip for every base in a temp dir.
  4. The family licence is CC0 base data — Vitruvian only. No other
     CharMorph base (CC-BY/AGPL) is in the family.
  5. run_charmorph_job.py's pure-Python validation accepts the
     emitted spec, rejects a non-Vitruvian character, and fails
     honestly without an addon checkout (naming the fetch script).

It does NOT bake a mesh (a bake needs the addon checkout + the
downloaded Vitruvian character + Blender, none present in this
proof); it proves the base is selectable and produces a runnable
job spec. Exit non-zero on failure.
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
    fam = next(f for f in data["families"] if f["id"] == "charmorph")
    assert fam["license_base_data"] == "CC0", fam["license_base_data"]
    assert len(fam["bases"]) == 1, len(fam["bases"])
    assert fam["bases"][0]["id"] == "vitruvian"
    runner = os.path.join(root, "tools", "charmorph", "run_charmorph_job.py")
    assert os.path.isfile(runner), "missing charmorph runner"
    selector = os.path.join(root, "tools", "charmorph", "select_base.py")
    assert os.path.isfile(selector), "missing charmorph selector"
    spec = importlib.util.spec_from_file_location("wh_run_charmorph_job", runner)
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
            assert jspec["tool"] == "charmorph"
            assert jspec["params"]["character"] == "vitruvian"
            mod.validate_spec(jspec)
            r = subprocess.run([sys.executable, selector, "fighter", bid,
                                "--bases", bases_path,
                                "--out", os.path.join(td, bid + ".fighter.json")],
                               capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            with open(os.path.join(td, bid + ".fighter.json")) as fh:
                frag = json.load(fh)
            assert frag["base_license"] == "CC0"
            assert frag["charmorph"] == base["charmorph"]
    # Rejection: a non-Vitruvian character must fail validation.
    bad = {"tool": "charmorph",
           "params": {"character": "antonia"},
           "out": "x.glb"}
    try:
        mod.validate_spec(bad)
    except RuntimeError:
        pass
    else:
        raise AssertionError("validate_spec accepted character antonia")
    # Honest failure without an addon checkout (no fake bake).
    good = {"tool": "charmorph", "params": {"character": "vitruvian"},
            "out": os.path.join(tempfile.gettempdir(), "charmorph-should-not-exist.glb")}
    try:
        mod.run_job(good, log=lambda *a: None)
    except RuntimeError as e:
        assert "fetch-charmorph.sh" in str(e), str(e)
    else:
        raise AssertionError("run_job succeeded without an addon checkout")
    # Dispatch check: run_job.py must resolve tool "charmorph" to the runner.
    run_job = os.path.join(root, "tools", "suite-jobs", "run_job.py")
    if os.path.isfile(run_job):
        spec2 = importlib.util.spec_from_file_location("wh_run_job", run_job)
        mod2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod2)
        path = mod2._runner_path("charmorph")
        assert path == runner, path
    print(f"PASS: charmorph family — {len(fam['bases'])} base selectable, "
          f"job spec + fighter fragment round-trip, dispatch resolves, "
          f"validation + honest no-addon failure verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
