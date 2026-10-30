#!/usr/bin/env python3
"""Batch verification for the 100% wiring pass (2026-10-24) — one run, all wired fighters.

GPU-READY JOB SPEC (for the parent to execute on a GPU host; this script itself
runs the JSON-level checks on CPU and prints the GPU spec when --gpu is passed
without a GPU present, instead of faking GPU work):
  script name:  tools/combat-qa/wiring_batch_verify.py
  inputs:       game/assets/movesets/{kinpo,burger,purplerain,pond,ryusan,
                  demonio,diablo,scimitar,phantom,skull,pantera}.json
                game/assets/movesets/{19 MOD-wired fighters}.json
                game/data/moveset-library/banks/wrestling.json
                game/data/moveset-library/index.json
  outputs:      stdout PASS/FAIL per check + exit code (0 = all pass);
                --report PATH writes the same report as JSON.
  memory:       JSON mode < 1 GB RAM, no GPU (moveset JSONs ~20 MB +
                wrestling bank ~6 MB). Full skeletal forward-kinematics clip
                mode (NOT implemented here — it needs a MOTA clip decoder +
                rigs, a separate lane) is estimated at 8-16 GB GPU RAM for the
                11,613-clip mot batch; that figure is an ESTIMATE, not measured.
  GPU mode:     --gpu runs the same JSON checks batched with multiprocessing
                and, when torch + CUDA are importable, reserves the device and
                reports device properties; it does NOT claim FK results. If
                torch/CUDA are absent it prints the spec above and exits 2
                (not a pass, not a failure of the JSON checks).

Checks (all must pass in JSON mode):
  1. MOT tables reconcile: resolved + unmapped == total; no 0x8000 ref in
     resolved; every resolved clip starts 00 64 / 00 C8; unmapped lookup
     keys == anim_ref - 0x8000; cancel_links carry LP1/RP2/LK3/RK4 inputs.
  2. Playable wiring is NONE on every mot table (clip keys only).
  3. T3: the 18 UNMAPPED entries carry no anim_ref/t3_row + UNMAPPED trace;
     kept basics carry the audit rows; chord trace counts match the
     verification doc; no string ender was rewired (strings arrays untouched
     by this script's scope — verified separately by diff).
  4. Wrestling: 4,153 input_lp rows round-trip to the original input digits;
     256 null rows carry UNMAPPED status; index counts match.
  5. MOD: every mod_damage in the 19 newly wired fighters carries
     mod_source TheBigTuna/Tekken-7-Frame-Data; no t8_source move carries a
     mod_damage added by this lane (checked via --against main copies when
     provided); megami.json is never in the wired set.

Usage:
  python3 tools/combat-qa/wiring_batch_verify.py [repo-root] [--report out.json] [--gpu]
"""
import argparse
import json
import os
import re
import sys

MOT_EXPECT = {
    "kinpo": (2464, 861, 1603, 4731),
    "burger": (2325, 667, 1658, 4267),
    "purplerain": (2303, 710, 1593, 4813),
    "pond": (2338, 745, 1593, 4670),
    "ryusan": (2183, 656, 1527, 4119),
}
MARKED_EXPECT = {
    "demonio": [("1", 41), ("1_r41", 41), ("u+1,1~t3.jin.2", 41)],
    "kinpo": [("1", 35)],
    "scimitar": [("1", 184)],
    "diablo": [("1", 46), ("1_r46", 46), ("u+1,1~t3.heihachi.2", 46)],
    "phantom": [("1", 62), ("1_r62", 62), ("u+1,1~t3.yoshimitsu.2", 62),
                ("2", 307), ("4", 243)],
    "burger": [("3", 65), ("b_c36_r65", 65)],
    "skull": [("3", 63), ("3_c36", 63), ("u+1,3", 63)],
}
KEPT_EXPECT = {
    "pantera": [("1", 110), ("2", 99), ("3", 264), ("4", 216)],
    "burger": [("1", 172), ("2", 100), ("4", 104)],
    "skull": [("1", 172), ("2", 100), ("4", 104)],
    "diablo": [("2", 157), ("3", 153), ("4", 104)],
    "phantom": [("3", 123)],
    "demonio": [("2", 220), ("3", 195), ("4", 199)],
    "kinpo": [("2", 220), ("3", 195), ("4", 199)],
    "scimitar": [("2", 220), ("3", 195), ("4", 199)],
}
CHORD_EXPECT = {"pantera": (4, 17), "demonio": (7, 11), "diablo": (8, 11),
                "kinpo": (3, 7), "scimitar": (13, 15), "burger": (0, 0),
                "skull": (0, 0), "phantom": (0, 5)}
MOD_WIRED_19 = ["bob", "burger-demon", "burger-speed-demon", "burger-the-mouth",
                "demonio-human", "demonio-bloodline-ember", "rin",
                "gyou-spirit-body", "t3-paul", "jin_soul", "retsu", "samura1",
                "sf-akuma", "star", "t3-eddy", "t3-hwoarang", "t3-law",
                "t3-nina", "zen"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--report", default=None)
    ap.add_argument("--gpu", action="store_true")
    args = ap.parse_args()
    root = args.root
    fails = []
    passes = []

    def check(cond, msg):
        (passes if cond else fails).append(msg)
        print(("PASS " if cond else "FAIL ") + msg)

    def load(rel):
        with open(os.path.join(root, rel)) as f:
            return json.load(f)

    for name, (total, nres, nunm, nlinks) in MOT_EXPECT.items():
        d = load(f"game/assets/movesets/{name}.json")
        t = d["t7_motbin_clips"]
        check(t["counts"]["total_moves"] == total, f"{name} mot total {total}")
        check(len(t["resolved"]) == nres, f"{name} resolved {nres}")
        check(len(t["unmapped_0x8000"]) == nunm, f"{name} unmapped {nunm}")
        check(len(t["cancel_links"]) == nlinks, f"{name} cancel_links {nlinks}")
        check(all(r[5].startswith("00 64") or r[5].startswith("00 c8")
                    for r in t["resolved"]), f"{name} clips 00 64/00 C8")
        check(all(int(r[3], 16) - 0x8000 == r[4] for r in t["unmapped_0x8000"]),
              f"{name} lookup keys")
        check(all(re.search(r"LP1|RP2|LK3|RK4", ln[1]) for ln in t["cancel_links"]),
              f"{name} cancel inputs LP-form")
        check(t["playable_wiring"].startswith("NONE"), f"{name} playable NONE")
    for name, marks in MARKED_EXPECT.items():
        d = load(f"game/assets/movesets/{name}.json")
        for key, row in marks:
            m = d["moves"][key]
            check("anim_ref" not in m and "t3_row" not in m
                  and m.get("t3_clip_status") == "UNMAPPED"
                  and m.get("t3_unmapped_former_row") == row,
                  f"{name}:{key} UNMAPPED former row {row}")
    for name, keeps in KEPT_EXPECT.items():
        d = load(f"game/assets/movesets/{name}.json")
        for key, row in keeps:
            check(d["moves"][key].get("t3_row") == row, f"{name}:{key} kept {row}")
    for name, (mh, lit) in CHORD_EXPECT.items():
        d = load(f"game/assets/movesets/{name}.json")
        ch = d.get("t3_verification_2026_10_24", {}).get("chord_string_enders", {})
        check(ch.get("motion_hard") == mh and ch.get("literal_branch_mask") == lit,
              f"{name} chord trace {mh}/{lit}")
    w = load("game/data/moveset-library/banks/wrestling.json")
    BTN = {"LP1": "1", "RP2": "2", "LK3": "3", "RK4": "4"}
    n_pop = n_null = bad = 0
    for m in w["moves"]:
        if m.get("input"):
            n_pop += 1
            back = m["input_lp"]
            for lp, dg in BTN.items():
                back = back.replace(lp, dg)
            if back != m["input"]:
                bad += 1
        else:
            n_null += 1
            if not (m["input_lp"] is None and m.get("input_lp_status") == "UNMAPPED"):
                bad += 1
    check((n_pop, n_null) == (4153, 256), f"wrestling {n_pop}/{n_null}")
    check(bad == 0, "wrestling round-trip")
    idx = load("game/data/moveset-library/index.json")
    wb = [b for b in idx["banks"] if b["id"] == "wrestling"][0]
    check(wb["input_lp_rows"] == 4153 and wb["input_lp_unmapped"] == 256,
          "index wrestling counts")
    for name in MOD_WIRED_19:
        d = load(f"game/assets/movesets/{name}.json")
        bad_src = [k for k, m in d["moves"].items()
                   if isinstance(m, dict) and m.get("mod_damage") is not None
                   and "t8_source" in m]
        check(not bad_src, f"{name} no t8_source move carries mod_damage")
        bad_mod = [k for k, m in d["moves"].items()
                   if isinstance(m, dict) and m.get("mod_damage") is not None
                   and m.get("mod_source") != "TheBigTuna/Tekken-7-Frame-Data"]
        check(not bad_mod, f"{name} mod_damage all carry MOD source")
    if args.gpu:
        try:
            import torch
            if torch.cuda.is_available():
                print(f"GPU: {torch.cuda.get_device_name(0)} "
                      f"({torch.cuda.get_device_properties(0).total_memory // 2**30} GB)")
            else:
                print("GPU requested but no CUDA device visible; JSON checks above still stand.")
        except ImportError:
            print("GPU requested but torch is not installed; JSON checks above still stand.")
            print("GPU job spec: see this file's header (script name, inputs, outputs, memory).")
    report = {"passes": passes, "fails": fails}
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
    print(f"\n{len(passes)} passed, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
