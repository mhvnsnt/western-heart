#!/usr/bin/env python3
"""check-budgets.py — CI budget check for a batch-optimize manifest.

Reads the manifest JSON written by batch-optimize.py and FAILS
(exit 1) on any breach, so an oversized or regressed optimization
cannot land silently:

  - output larger than input (an "optimization" that grew the asset)
  - output over the per-kind cap (defaults below; --budgets JSON
    overrides: {"fighter": N, "stage": N, "default": N} in bytes)
  - a -tc asset with no measurement note (manifest entries carry
    "tc": true; the batch run must record "tc_measured": true for
    that asset — set it in the manifest before running this check,
    with the measured before/after numbers beside it)
  - a simplified SKINNED asset without approval (manifest entries
    carry "simplified": true and "skinned": true; approval is the
    "simplify_approved": true field)

Kind is guessed from the input path: roster/ or game/assets/models/
-> fighter; game/assets/stages/ -> stage; anything else -> default.
Usage: python3 tools/gltfpack/check-budgets.py manifest.json [--budgets budgets.json]
"""
import argparse
import json
import sys

DEFAULT_CAPS = {"fighter": 40_000_000, "stage": 5_000_000, "default": 10_000_000}


def kind_of(path):
    if path.startswith("game/assets/stages/"):
        return "stage"
    if path.startswith("roster/") or path.startswith("game/assets/models/"):
        return "fighter"
    return "default"


def check(manifest, caps):
    errors = []
    for e in manifest.get("assets", []):
        if e.get("status") not in ("ok", "planned"):
            continue  # invalid/failed assets are the batch runner's failure, not a budget breach
        inp, out = e.get("input", "?"), e.get("output", "?")
        in_b, out_b = e.get("inBytes"), e.get("outBytes")
        if in_b is not None and out_b is not None and out_b > in_b:
            errors.append(f"{inp}: output {out_b} > input {in_b} (grew)")
        if out_b is not None and out_b > caps[kind_of(inp)]:
            errors.append(f"{inp}: output {out_b} over {kind_of(inp)} cap {caps[kind_of(inp)]}")
        if e.get("tc") and not e.get("tc_measured"):
            errors.append(f"{inp}: -tc used without tc_measured=true (measure per asset first)")
        if e.get("simplified") and e.get("skinned") and not e.get("simplify_approved"):
            errors.append(f"{inp}: simplified skinned fighter without simplify_approved=true")
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--budgets", default="")
    a = ap.parse_args(argv)
    with open(a.manifest) as fh:
        manifest = json.load(fh)
    caps = dict(DEFAULT_CAPS)
    if a.budgets:
        with open(a.budgets) as fh:
            caps.update(json.load(fh))
    errors = check(manifest, caps)
    if errors:
        print("BUDGET CHECK FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    n = len([e for e in manifest.get("assets", []) if e.get("status") in ("ok", "planned")])
    print(f"budget check passed ({n} assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
