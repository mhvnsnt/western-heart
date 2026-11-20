#!/usr/bin/env python3
"""Validate tools/anatomy/stack_layers.json consistency.

Checks (map-level only — it does NOT walk roster/ anatomy files; see
docs/research/ANATOMY-STACK-WIRING-2026-10-24.md section 6 for the
planned --check-roster extension):
  1. Every allow-listed dataset has id, name, license, attribution.
  2. Every block-listed dataset has id, name, license, reason.
  3. No dataset id appears on both lists.
  4. Every code entry has id, name, license (+ notice for allow-list).
  5. Every Somakine->WH layer mapping points at a real WH layer.
  6. WH layers include the five wh.anatomy-layers/2 layers.

Usage: python3 tools/anatomy/validate_stack_layers.py
Exit 0 = map consistent; exit 1 = violations printed.
"""
import json
import sys
from pathlib import Path

EXPECTED_WH_LAYERS = {"bone", "muscle", "organ", "fat", "skin"}


def fail(errors, msg):
    errors.append(msg)


def main():
    here = Path(__file__).resolve().parent
    data = json.loads((here / "stack_layers.json").read_text())
    errors = []

    allow_ids = set()
    for entry in data.get("datasets_allow", []):
        for key in ("id", "name", "license", "attribution"):
            if not entry.get(key):
                fail(errors, f"allow-list entry missing {key}: {entry}")
        if entry.get("id"):
            allow_ids.add(entry["id"])
    for entry in data.get("datasets_block", []):
        for key in ("id", "name", "license", "reason"):
            if not entry.get(key):
                fail(errors, f"block-list entry missing {key}: {entry}")
        if entry.get("id") in allow_ids:
            fail(errors, f"dataset on both lists: {entry['id']}")
    for entry in data.get("code_allow", []):
        for key in ("id", "name", "license", "notice"):
            if not entry.get(key):
                fail(errors, f"code allow-list entry missing {key}: {entry}")
    for entry in data.get("code_block_game_runtime", []):
        for key in ("id", "name", "license", "reason"):
            if not entry.get(key):
                fail(errors, f"code block-list entry missing {key}: {entry}")
    wh_layers = set(data.get("wh_layers", []))
    if wh_layers != EXPECTED_WH_LAYERS:
        fail(errors, f"wh_layers {sorted(wh_layers)} != expected {sorted(EXPECTED_WH_LAYERS)}")
    for mapping in data.get("somakine_to_wh_layer_map", []):
        if mapping.get("wh_layer") not in wh_layers:
            fail(errors, f"layer map points at unknown WH layer: {mapping}")
        if not mapping.get("somakine_layer") or not mapping.get("treatment"):
            fail(errors, f"layer map entry incomplete: {mapping}")

    if errors:
        print("FAIL: stack_layers.json has %d violation(s):" % len(errors))
        for error in errors:
            print(" - " + error)
        return 1
    print(
        "OK: stack_layers.json consistent "
        f"({len(allow_ids)} allow-listed datasets, "
        f"{len(data.get('datasets_block', []))} blocked, "
        f"{len(data.get('somakine_to_wh_layer_map', []))} layer mappings)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
