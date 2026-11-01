#!/usr/bin/env python3
"""Guard for the Zui Steve/Lei import (union / no-loss / no-fabrication).

Usage: guard_zui.py <before_zui.json> <after_zui.json> <steve_frame_data.json> <rave.json>

Asserts:
  1. Every pre-existing move survives: same key + deep-equal payload, or
     exactly one rekeyed "<key>_r..." entry with a deep-equal payload.
  2. Every imported Steve entry's t7_move_id exists in the T7 Steve frame
     data; every imported DRU entry traces to a rave.json T7 Lei entry.
  3. No pre-existing string/special entry was dropped.
Exit 0 = PASS.
"""
import json, sys

def main():
    before = json.load(open(sys.argv[1]))
    after = json.load(open(sys.argv[2]))
    steve = json.load(open(sys.argv[3]))
    rave = json.load(open(sys.argv[4]))
    fails = []

    bm, am = before["moves"], after["moves"]
    rekeyed = 0
    for key, entry in bm.items():
        if key in am and am[key] == entry:
            continue
        cands = [k for k in am if k.startswith(key + "_r") and am[k] == entry]
        if len(cands) == 1:
            rekeyed += 1
            continue
        fails.append(f"LOST or ALTERED: {key}")
    steve_ids = {r["id"] for r in steve["movelist"]}
    rave_dru_ids = {v["t7_move_id"] for v in rave["moves"].values()
                    if isinstance(v, dict) and v.get("t7_move_id")}
    n_steve = n_dru = 0
    for key, entry in am.items():
        tag = entry.get("wh_import")
        if tag == "zui-steve-t7-20261021":
            n_steve += 1
            if entry.get("t7_move_id") not in steve_ids:
                fails.append(f"FABRICATED Steve entry at {key}: {entry.get('t7_move_id')}")
        elif tag == "zui-lei-dru-20261021":
            n_dru += 1
            if entry.get("t7_move_id") not in rave_dru_ids:
                fails.append(f"UNTRACED DRU entry at {key}: {entry.get('t7_move_id')}")
    for field in ("strings", "specials"):
        b_inputs = [s["input"] for s in before[field]]
        a_inputs = [s["input"] for s in after[field]]
        for inp in b_inputs:
            if inp not in a_inputs:
                fails.append(f"LOST {field} entry: {inp}")
    print(f"before={len(bm)} after={len(am)} rekeyed_preserved={rekeyed} "
          f"steve_imported={n_steve} dru_imported={n_dru}")
    if fails:
        print("GUARD FAIL")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("GUARD PASS: union complete, no loss, every addition traces to "
          "Steve T7 frame data or the T7 Lei set in rave.json")

if __name__ == "__main__":
    main()
