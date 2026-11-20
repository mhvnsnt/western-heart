#!/usr/bin/env python3
"""select_base.py — select an MPFB2 base family base for the creation suite.

The MPFB2 family is 6 macro-parameter bases (see
tools/creation-suite/bases.json, family "mpfb2"). This script makes them
selectable as a family, in the same pattern as
tools/mb-lab/select_base.py:

    python3 tools/mpfb2/select_base.py list
    python3 tools/mpfb2/select_base.py show mpfb2-powerhouse
    python3 tools/mpfb2/select_base.py job mpfb2-powerhouse --out jobs/mpfb2-powerhouse.json
    python3 tools/mpfb2/select_base.py fighter mpfb2-powerhouse --out fighter-mpfb2-powerhouse.json

`job` writes a suite job spec that tools/suite-jobs/run_job.py can run
(tool "mpfb2-live", dispatched by its override to
tools/mpfb2/run_mpfb2_job.py). The job spec follows run_mpfb2_job.py's
actual schema — params carry `macro` (MPFB2 macro attributes, 0..1)
and `rig` directly. Running the job needs the MPFB2 vendor checkout
(bash tools/mpfb2/fetch-mpfb2.sh) and Blender 4.2+; this script itself
needs neither — selection and spec generation are pure Python and are
what the proof run exercises.

Macro values follow MPFB2's own documentation
(docs/entities/objectproperties.md in makehumancommunity/mpfb2):
gender 0.0 = fully female, 1.0 = fully male; age, muscle, weight,
height, proportions, cupsize, firmness all default 0.5. No base here
ships a baked mesh yet — base_mesh is the job's output path, not an
existing file (see tools/mpfb2/MPFB2-PROOF-20261102.md).

Licence: MPFB2 addon code GPL-3.0, core assets CC0 (see
tools/mpfb2/README.md). The CC0 label here is for the BASE DATA only;
it is not a blanket label for the addon code, and it must never be
applied to MB-Lab (AGPL) bases.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BASES_PATH = os.path.join(REPO, "tools", "creation-suite", "bases.json")
FAMILY_ID = "mpfb2"

MACRO_KEYS = {
    "gender", "age", "muscle", "weight", "height",
    "proportions", "cupsize", "firmness",
}


def load_family(bases_path=BASES_PATH):
    with open(bases_path) as fh:
        data = json.load(fh)
    for fam in data["families"]:
        if fam["id"] == FAMILY_ID:
            return fam
    raise RuntimeError(f"family {FAMILY_ID!r} not in {bases_path}")


def validate(fam):
    assert fam["license_base_data"] == "CC0", fam["license_base_data"]
    ids = [b["id"] for b in fam["bases"]]
    assert len(ids) == len(set(ids)), "duplicate base ids"
    for b in fam["bases"]:
        assert b["base_mesh"].endswith(".glb"), b["id"]
        assert b["job"]["tool"] == "mpfb2-live", b["id"]
        assert b["job"]["params"]["macro"] == b["mpfb2"]["macro"], b["id"]
        assert set(b["mpfb2"]["macro"]) <= MACRO_KEYS, b["id"]
        for k, v in b["mpfb2"]["macro"].items():
            assert 0.0 <= float(v) <= 1.0, (b["id"], k, v)
        gender = b["mpfb2"]["macro"]["gender"]
        if b["gender"] == "female":
            assert float(gender) == 0.0, b["id"]
        elif b["gender"] == "male":
            assert float(gender) == 1.0, b["id"]
        else:
            raise AssertionError(f"unexpected gender {b['gender']!r} for {b['id']}")
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
              f"{fam['license_code']} code")
        for b in fam["bases"]:
            print(f"  {b['id']:24s} {b['gender']:6s} {b['name']}  "
                  f"({b['mpfb2']['macro']})")
        return 0
    if not a.base:
        print("need a base id; run `list`", file=sys.stderr)
        return 2
    base = next((b for b in fam["bases"] if b["id"] == a.base), None)
    if base is None:
        print(f"unknown MPFB2 base {a.base!r}; run `list`", file=sys.stderr)
        return 2
    if a.cmd == "show":
        print(json.dumps(base, indent=1))
        return 0
    if a.cmd == "job":
        spec = dict(base["job"])
        spec["id"] = f"mpfb2-live-{base['id']}"
        out = a.out or f"jobs/mpfb2-live-{base['id']}.json"
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as fh:
            json.dump(spec, fh, indent=1)
        print(f"job spec -> {out}")
        print("run: python3 tools/suite-jobs/run_job.py --spec " + out)
        return 0
    # fighter
    frag = {
        "base_family": "mpfb2",
        "base_id": base["id"],
        "base_license": fam["license_base_data"],
        "mpfb2": base["mpfb2"],
    }
    out = a.out or f"fighter-{base['id']}.json"
    with open(out, "w") as fh:
        json.dump(frag, fh, indent=1)
    print(f"fighter fragment -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
