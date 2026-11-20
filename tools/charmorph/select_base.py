#!/usr/bin/env python3
"""select_base.py — select a CharMorph base family base for the creation suite.

The CharMorph family has exactly ONE wired base: Vitruvian (CC0).
Other CharMorph bases exist upstream (Antonia CC-BY, Reom CC-BY,
MB-Lab base AGPL) and are deliberately NOT in this family, so the
family's CC0 label can never be misread as covering them. This script
mirrors tools/mb-lab/select_base.py:

    python3 tools/charmorph/select_base.py list
    python3 tools/charmorph/select_base.py show vitruvian
    python3 tools/charmorph/select_base.py job vitruvian --out jobs/charmorph-vitruvian.json
    python3 tools/charmorph/select_base.py fighter vitruvian --out fighter-vitruvian.json

`job` writes a suite job spec that tools/suite-jobs/run_job.py can run
(tool "charmorph", dispatched by its default convention to
tools/charmorph/run_charmorph_job.py). Running the job needs the
CharMorph vendor checkout (bash tools/charmorph/fetch-charmorph.sh)
AND the downloaded Vitruvian character; this script itself needs
neither — selection and spec generation are pure Python and are what
the proof run exercises.

No base here ships a baked mesh yet — base_mesh is the job's output
path, not an existing file (see tools/charmorph/CHARMORPH-PROOF-20261102.md).
Gender is "unspecified": no gendered Vitruvian variant is claimed.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
BASES_PATH = os.path.join(REPO, "tools", "creation-suite", "bases.json")
FAMILY_ID = "charmorph"


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
        assert b["job"]["tool"] == "charmorph", b["id"]
        assert b["job"]["params"]["character"] == b["charmorph"]["character"], b["id"]
        assert b["charmorph"]["character"] == "vitruvian", b["id"]
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
        print(f"{fam['name']} — {fam['license_base_data']} base data "
              f"(Vitruvian only; see licence note)")
        for b in fam["bases"]:
            print(f"  {b['id']:24s} {b['gender']:12s} {b['name']}  "
                  f"({b['charmorph']['character']}, rig: {b['charmorph']['rig']})")
        return 0
    if not a.base:
        print("need a base id; run `list`", file=sys.stderr)
        return 2
    base = next((b for b in fam["bases"] if b["id"] == a.base), None)
    if base is None:
        print(f"unknown CharMorph base {a.base!r}; run `list`", file=sys.stderr)
        return 2
    if a.cmd == "show":
        print(json.dumps(base, indent=1))
        return 0
    if a.cmd == "job":
        spec = dict(base["job"])
        spec["id"] = f"charmorph-{base['id']}"
        out = a.out or f"jobs/charmorph-{base['id']}.json"
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as fh:
            json.dump(spec, fh, indent=1)
        print(f"job spec -> {out}")
        print("run: python3 tools/suite-jobs/run_job.py --spec " + out)
        return 0
    # fighter
    frag = {
        "base_family": "charmorph",
        "base_id": base["id"],
        "base_license": fam["license_base_data"],
        "charmorph": base["charmorph"],
    }
    out = a.out or f"fighter-{base['id']}.json"
    with open(out, "w") as fh:
        json.dump(frag, fh, indent=1)
    print(f"fighter fragment -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
