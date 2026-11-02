#!/usr/bin/env python3
"""select_base.py — select an MB-Lab base family base for the creation suite.

The MB-Lab family is the 9 template bases already baked in the repo
(customization/templates/body-templates.json, meshes in
customization/templates/meshes/<id>.glb). This script makes them
selectable as a family, instead of only as loose template rows:

    python3 tools/mb-lab/select_base.py list
    python3 tools/mb-lab/select_base.py show powerhouse
    python3 tools/mb-lab/select_base.py job powerhouse --out jobs/mb-lab-powerhouse.json
    python3 tools/mb-lab/select_base.py fighter powerhouse --out fighter-powerhouse.json

`job` writes a suite job spec that tools/suite-jobs/run_job.py can run
(tool "mb-lab", dispatched to tools/mb-lab/run_mblab_job.py). The job
spec follows run_mblab_job.py's actual schema — params carry
`character` and `morphs` directly (not nested under a second
`params` key). Running the job needs the MB-Lab vendor checkout
(bash tools/mb-lab/fetch-mb-lab.sh) and Blender 4.0.2; this script
itself needs neither — selection and spec generation are pure Python
and are what the proof run below exercises.

Licence: MB-Lab code GPL-3.0, base DATA AGPL-3.0. Bases selected
here are AGPL-3.0 (see tools/creation-suite/bases.json). They are
NOT CC0 — do not relabel them.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BASES_PATH = os.path.join(REPO, "tools", "creation-suite", "bases.json")
FAMILY_ID = "mb-lab"


def load_family(bases_path=BASES_PATH):
    with open(bases_path) as fh:
        data = json.load(fh)
    for fam in data["families"]:
        if fam["id"] == FAMILY_ID:
            return fam
    raise RuntimeError(f"family {FAMILY_ID!r} not in {bases_path}")


def validate(fam):
    ids = [b["id"] for b in fam["bases"]]
    assert len(ids) == len(set(ids)), "duplicate base ids"
    for b in fam["bases"]:
        assert b["base_mesh"].endswith(".glb"), b["id"]
        assert b["job"]["tool"] == "mb-lab", b["id"]
        assert b["job"]["params"]["character"] == b["mb_lab"]["character"], b["id"]
        assert b["job"]["params"]["morphs"] == b["mb_lab"]["morphs"], b["id"]
        for v in b["mb_lab"]["morphs"].values():
            assert -1.0 <= float(v) <= 1.0, (b["id"], v)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "show", "job", "fighter"])
    ap.add_argument("base", nargs="?", help="base id (show/job/fighter)")
    ap.add_argument("--bases", default=BASES_PATH)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    fam = load_family(a.bases)
    validate(fam)
    if a.cmd == "list":
        print(f"{fam['name']} — {fam['license_base_data']} base data, "
              f"{fam['license_code']} code (NOT CC0)")
        for b in fam["bases"]:
            print(f"  {b['id']:20s} {b['gender']:6s} {b['name']}  "
                  f"({b['mb_lab']['character']}, {b['mb_lab']['morphs']})")
        return 0
    if not a.base:
        print("need a base id; run `list`", file=sys.stderr)
        return 2
    base = next((b for b in fam["bases"] if b["id"] == a.base), None)
    if base is None:
        print(f"unknown MB-Lab base {a.base!r}; run `list`", file=sys.stderr)
        return 2
    if a.cmd == "show":
        print(json.dumps(base, indent=1))
        return 0
    if a.cmd == "job":
        spec = dict(base["job"])
        spec["id"] = f"mb-lab-{base['id']}"
        out = a.out or f"jobs/mb-lab-{base['id']}.json"
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as fh:
            json.dump(spec, fh, indent=1)
        print(f"job spec -> {out}")
        print("run: python3 tools/suite-jobs/run_job.py --spec " + out)
        return 0
    # fighter
    frag = {
        "base_family": "mb-lab",
        "base_id": base["id"],
        "base_license": fam["license_base_data"],
        "mb_lab": base["mb_lab"],
    }
    out = a.out or f"fighter-{base['id']}.json"
    with open(out, "w") as fh:
        json.dump(frag, fh, indent=1)
    print(f"fighter fragment -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
