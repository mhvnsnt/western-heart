#!/usr/bin/env python3
"""W7: decode RSP breakpoint hits into wrestler->motion assignments.

Input: hits.jsonl from w7_rsp.py (0x800364F0 move_exec hits with descriptors).
Decodes each descriptor through the wprm tables (WMXIX-WPRM-DECODE.json):
  - type 2 (Table A): packed key; group = top two decimal digits,
    index = low three digits (decimal digits in 6-bit fields).
  - type 1 (Table B): name lookup.
Motion names are 4-char motion IDs (e.g. '0101') -> move.mpc clips via
WMXIX-MPC-INDEX.json -> calibrated durations via
mpc-clips-manifest-calibrated.json.
Wrestler identity comes from the Defwres codes found by the RSP client's
GPR scan (wrestler object +0x514).

Usage:
  python3 w7_decode.py hits.jsonl [--wprm ...] [--mpc ...] [--cal ...]
    [--out assignment.json]
"""
import argparse
import json
import struct
import sys


def load_wprm(path):
    w = json.load(open(path))
    tA, tB = {}, {}
    for g in w["tables"]["A_packed_lookup_FUN_8007609c"]["groups"]:
        recs = {}
        for r in g["records"]:
            n = r["name"]
            if len(n) == 4 and all(32 <= ord(c) < 127 for c in n):
                recs[r["idx"]] = n
        tA[g["key"]] = recs
    for g in w["tables"]["B_name_lookup_FUN_80075fb8"]["groups"]:
        recs = {}
        for r in g["records"]:
            n = r["name"]
            if len(n) == 4 and all(32 <= ord(c) < 127 for c in n):
                recs[r["idx"]] = n
        tB[g["key"]] = recs
    return tA, tB


def unpack_key(key):
    """Packed key: decimal digits in 6-bit fields. Returns (group, index).
    Per the Ghidra doc: group = top two digits, index = low three digits.
    The packed form stores each decimal digit in a 6-bit field; unpack by
    reading 5 fields of 6 bits (30 bits) from the top."""
    digits = []
    for i in range(5):
        digits.append((key >> (24 - 6 * i)) & 0x3F)
    # digits are 0-9 decimal; group = first two, index = last three
    if any(d > 9 for d in digits):
        return None, None
    group = digits[0] * 10 + digits[1]
    index = digits[2] * 100 + digits[3] * 10 + digits[4]
    return group, index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hits")
    ap.add_argument("--wprm", default="w6-docs/WMXIX-WPRM-DECODE.json")
    ap.add_argument("--mpc", default="w6-docs/WMXIX-MPC-INDEX.json")
    ap.add_argument("--cal", default="mpc-clips-manifest-calibrated.json")
    ap.add_argument("--out", default="assignment.json")
    args = ap.parse_args()

    tA, tB = load_wprm(args.wprm)
    try:
        mpc = json.load(open(args.mpc))
    except Exception:
        mpc = {}
    try:
        cal = json.load(open(args.cal))["clips"]
    except Exception:
        cal = {}

    hits = [json.loads(l) for l in open(args.hits) if l.strip()]
    print("hits: %d" % len(hits))
    decoded = []
    for h in hits:
        d = h.get("descriptor")
        if not d:
            continue
        key, typ, variant = d["key"], d["type"], d["variant"]
        rec = {"t": h.get("t"), "key": key, "key_hex": "0x%x" % key,
               "type": typ, "variant": variant,
               "wrestler": h.get("wrestler")}
        if typ == 2:
            group, index = unpack_key(key)
            rec["table"] = "A"
            rec["group"] = group
            rec["index"] = index
            motion = tA.get(group, {}).get(index) if group is not None else None
            rec["motion"] = motion
        elif typ == 1:
            rec["table"] = "B"
            # Table B is name-keyed: the key is 4 ASCII chars
            try:
                name = struct.pack(">I", key).decode("ascii")
            except Exception:
                name = None
            rec["name_key"] = name
            motion = None
            for gk, recs in tB.items():
                for idx, nm in recs.items():
                    if nm == name:
                        motion = nm
                        rec["group"] = gk
                        rec["index"] = idx
                        break
                if motion:
                    break
            rec["motion"] = motion
        else:
            rec["table"] = "?"
            rec["motion"] = None
        # clip lookup
        m = rec.get("motion")
        if m:
            clip = cal.get(m + "_00A") or cal.get(m)
            if clip:
                rec["clip"] = {"id": m, "duration_seconds": clip.get("duration_seconds"),
                               "tick_total": clip.get("tick_total")}
        decoded.append(rec)

    # assignment table: wrestler codes -> set of motions
    assign = {}
    unknown = []
    for r in decoded:
        w = r.get("wrestler") or []
        codes = tuple(sorted(set(c for entry in w for c in entry.get("codes", [])))) if w else ()
        key = codes if codes else ("UNKNOWN",)
        assign.setdefault(key, set()).add((r.get("motion"), r.get("table"),
                                           r.get("group"), r.get("index"),
                                           r.get("variant")))
        if not codes:
            unknown.append(r)
    out = {"decoded_hits": decoded,
           "assignment": {"/".join(k): sorted([list(x) for x in v]) for k, v in assign.items()},
           "stats": {"hits_total": len(hits), "decoded": len(decoded),
                     "with_motion": sum(1 for r in decoded if r.get("motion")),
                     "with_wrestler": sum(1 for r in decoded if r.get("wrestler")),
                     "unknown_wrestler": len(unknown)}}
    json.dump(out, open(args.out, "w"), indent=1)
    print("decoded %d/%d hits; with motion: %d; with wrestler: %d" % (
        len(decoded), len(hits), out["stats"]["with_motion"], out["stats"]["with_wrestler"]))
    print("wrestler keys:", list(out["assignment"].keys()))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
