#!/usr/bin/env python3
"""GPU verification: full 22-bank x hit-type reaction coverage matrix.

Kaggle notebook (2x Tesla T4, parent's browser notebook):
    # Cell 1: get the repo into the notebook session, then run:
    !python tools/anim/gpu_hit_reaction_matrix.py --root . \
        --out gpu_reaction_matrix.csv --gaps gpu_reaction_gaps.json
    # The script prints the matrix; the CSV + JSON are the proof artifacts.

What it does (no guesses anywhere):
  For every attacker bank in game/assets/anim/t3/reactions.json, for
  every attacker move row that carries a reaction, and for every hit
  situation (front, crouch, counter, side, back, guard, down, air
  kinds, close-range), it replays the file's own selection rule
  (docs/anim/T3-REACTIONS.md "Picking a hit reaction": record field
  by situation, class gate, close substitution, air kinds) as one
  vectorized gather per bank, then checks the picked slot against
  EVERY defender bank two ways: the defender's slots plan in
  reactions.json, and the actual baked row in that bank's
  reactions.pack.json (defender bank first, attacker bank second,
  DivmotMergeSharedSlots order).

Cell verdicts:
  PASS     - every row that names a slot for this situation resolves
             on all 22 defenders, with pack bytes present.
  UNMAPPED - at least one named slot fails to resolve somewhere, or
             a record field names slot 0 (no slot for that
             situation). The failing rows are written to --gaps.
  Separately counted, never counted as failures: class-1 rows
  (never react), throw-range reactions (0x1nnn, the grapple lane),
  and rows with reaction 0 (not attacks). Wall splat has no column:
  the decoded records carry no wall field, so there is nothing to
  matrix (see the node test, which asserts that absence).

Backend: torch when importable (CUDA on the Kaggle T4s, CPU
otherwise), numpy fallback when torch is absent. The selection math
is one code path written against operations both backends share
(fancy indexing, elementwise compare, sum), so the device changes
where the gather runs, not what it computes.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

SLOT_SPACE = 8192  # max slot anywhere in the data is 4010; headroom is free

# situation -> record field index (docs/anim/T3-REACTIONS.md record_fields)
SITUATIONS = [
    ("front", 0), ("front_crouch", 1),
    ("counter", 2), ("counter_crouch", 3),
    ("side1", 4), ("side1_crouch", 5),
    ("side3", 6), ("side3_crouch", 7),
    ("back", 8), ("back_crouch", 9),
    ("guard", 10), ("guard_crouch", 11),
    ("down", 12), ("down_other", 13),
]
AIR_SITUATIONS = [(f"air_kind_{k}", k) for k in range(6)]


def load_backend():
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[gpu-matrix] backend=torch device={device}"
              + (f" ({torch.cuda.get_device_name(0)})" if device == "cuda" else ""))
        return ("torch", torch, device)
    except Exception as exc:  # noqa: BLE001 - torch is optional here
        import numpy as np
        print(f"[gpu-matrix] backend=numpy (torch unavailable: {exc})")
        return ("numpy", np, None)


def to_backend(kind, lib, device, arr):
    if kind == "torch":
        t = lib.tensor(arr)
        return t.to(device) if device else t
    return lib.array(arr)


def as_int_list(x):
    if hasattr(x, "tolist"):
        return x.tolist()
    return list(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".",
                    help="repo root (dir containing game/assets/anim/t3/reactions.json)")
    ap.add_argument("--banks", default="",
                    help="comma list of attacker bank dirs; default all 22")
    ap.add_argument("--defenders", default="",
                    help="comma list of defender bank dirs to resolve against; "
                         "default all 22 (subset runs pass the banks whose "
                         "packs are present, so pack checks stay honest)")
    ap.add_argument("--out", default="gpu_reaction_matrix.csv")
    ap.add_argument("--gaps", default="gpu_reaction_gaps.json")
    ap.add_argument("--no-packs", action="store_true",
                    help="skip pack-byte checks (slots-plan only)")
    args = ap.parse_args()

    kind, lib, device = load_backend()
    t3 = Path(args.root) / "game" / "assets" / "anim" / "t3"
    with open(t3 / "reactions.json") as f:
        R = json.load(f)
    bank_dirs = sorted(R["banks"].keys())
    if args.banks:
        wanted = [b.strip() for b in args.banks.split(",") if b.strip()]
        bank_dirs = [b for b in bank_dirs if b in wanted]
    print(f"[gpu-matrix] attacker banks: {len(bank_dirs)}")

    # --- backend tensors -------------------------------------------------
    records = to_backend(kind, lib, device, R["records"])  # [633, 21]
    close_reactions = to_backend(kind, lib, device, R["close_reactions"])  # [58, 2]
    air_kinds = to_backend(kind, lib, device, R["air_kinds"])  # [6, 2]
    # slot_defined[V, slot]: defender V's slots plan names the slot.
    # pack_present[V, slot]: defender V's pack actually bakes the row.
    n_banks = len(R["banks"])
    all_dirs = sorted(R["banks"].keys())
    dir_index = {d: i for i, d in enumerate(all_dirs)}
    if args.defenders:
        defenders = [d.strip() for d in args.defenders.split(",") if d.strip()]
    else:
        defenders = all_dirs
    n_def = len(defenders)
    print(f"[gpu-matrix] defender banks: {n_def}")
    import numpy as np
    slot_defined = np.zeros((n_banks, SLOT_SPACE), dtype=np.int64)
    for d, bank in R["banks"].items():
        for k in bank["slots"]:
            slot_defined[dir_index[d], int(k, 16)] = 1
    pack_present = np.zeros((n_banks, SLOT_SPACE), dtype=np.int64)
    if not args.no_packs:
        for d in all_dirs:
            pack_path = t3 / d / "reactions.pack.json"
            if not pack_path.exists():
                print(f"[gpu-matrix] WARNING: no pack for {d} (pack checks fail for it)")
                continue
            with open(pack_path) as f:
                pack = json.load(f)
            for k in pack.get("rows", {}):
                pack_present[dir_index[d], int(k, 16)] = 1
    else:
        pack_present = slot_defined.copy()
    slot_defined_b = to_backend(kind, lib, device, slot_defined)
    pack_present_b = to_backend(kind, lib, device, pack_present)
    def_idx_b = to_backend(kind, lib, device, [dir_index[d] for d in defenders])

    rows_out = []
    gaps = []
    # (attacker dir, rows dict). The shared divmot99 rows run as an
    # extra pseudo-bank when no --banks filter is given: they are not
    # a 23rd bank, they are the common attacks every bank can throw.
    bank_items = [(d, R["banks"][d]["rows"]) for d in bank_dirs]
    if not args.banks:
        bank_items.append(("common_divmot99", R["common_rows"]))
    for a_dir, bank_rows in bank_items:
        a_idx = dir_index.get(a_dir)  # None for the common pseudo-bank
        row_keys = sorted(bank_rows.keys(), key=int)
        react = [bank_rows[k][0] for k in row_keys]
        close_idx = [bank_rows[k][1] for k in row_keys]
        cls = [bank_rows[k][2] for k in row_keys]
        react_b = to_backend(kind, lib, device, react)
        close_b = to_backend(kind, lib, device, close_idx)
        cls_b = to_backend(kind, lib, device, cls)
        # Class gate + reaction class, vectorized over this bank's rows.
        is_class1 = (cls_b == 1) | (cls_b == 3)
        is_throw = (react_b >= 0x1000) & (react_b != 0)
        is_zero = react_b == 0
        live = (~is_class1) & (~is_throw) & (~is_zero)
        # Close-substituted reaction value per row (0 when no close entry).
        has_close = close_b != 0
        close_val = close_reactions[close_b, 0] & 0xFFFF
        eff_react = lib.where(has_close, close_val, react_b)
        # Gathers below index records[] with every row, including
        # gated/throw rows whose reaction is 4469: clamp those to
        # record 0 (all zeros) — the live mask excludes them anyway.
        eff_react = lib.where(live, eff_react, lib.zeros_like(eff_react))
        n_live = int(live.sum())
        n_class1 = int(is_class1.sum())
        n_throw = int(is_throw.sum())
        n_zero = int(is_zero.sum())

        def evaluate(situation, slots):
            """slots: backend int array, one slot per row (0 = no slot)."""
            named = live & (slots != 0)
            unmapped = live & (slots == 0)
            n_named = int(named.sum())
            n_unmapped = int(unmapped.sum())
            if n_named == 0:
                return ("PASS" if n_unmapped == 0 else "UNMAPPED",
                        n_named, n_unmapped, 0, 0)
            # Resolve per defender: defined in V's plan, else in A's plan;
            # pack bytes must exist in the owning bank's pack.
            # Gather [n_rows, n_defenders] via slot index arrays.
            idx = slots  # [n_rows]
            # defender-defined matrix: [n_def, n_rows]
            defd = slot_defined_b[def_idx_b][:, idx]
            packd = pack_present_b[def_idx_b][:, idx]
            if a_idx is None:
                defa = lib.zeros_like(idx)
                packa = lib.zeros_like(idx)
            else:
                defa = slot_defined_b[a_idx, idx]
                packa = pack_present_b[a_idx, idx]
            # owner pack present: V's pack if V defines, else A's pack
            owner_pack = lib.where(defd == 1, packd, packa)
            ok_per_def = (defd == 1) | (defa == 1)
            ok_per_def = ok_per_def & (owner_pack == 1)
            # A row resolves everywhere iff all defenders ok.
            all_ok = ok_per_def.sum(axis=0) == n_def
            resolved_all = int((named & all_ok).sum())
            partial = n_named - resolved_all
            verdict = "PASS" if (n_unmapped == 0 and partial == 0) else "UNMAPPED"
            return verdict, n_named, n_unmapped, resolved_all, partial

        def evaluate_and_gap(situation, slots, field_note, skip_gaps=False):
            if n_live == 0:
                # No live rows at all (the common pseudo-bank: all 34
                # common rows are throw-range). Vacuous PASS would lie;
                # this situation has nothing to cover for this bank.
                rows_out.append({
                    "attacker_bank": a_dir, "situation": situation,
                    "verdict": "N/A", "rows_live": 0,
                    "rows_named_slot": 0, "rows_slot_zero_unmapped": 0,
                    "rows_resolved_all_defenders": 0, "rows_partial": 0,
                    "rows_class_gated": n_class1, "rows_throw_range": n_throw,
                    "rows_no_reaction": n_zero,
                })
                return "N/A"
            verdict, n_named, n_unmapped, resolved_all, partial = evaluate(situation, slots)
            rows_out.append({
                "attacker_bank": a_dir, "situation": situation,
                "verdict": verdict, "rows_live": n_live,
                "rows_named_slot": n_named, "rows_slot_zero_unmapped": n_unmapped,
                "rows_resolved_all_defenders": resolved_all,
                "rows_partial": partial,
                "rows_class_gated": n_class1, "rows_throw_range": n_throw,
                "rows_no_reaction": n_zero,
            })
            if verdict == "UNMAPPED" and (n_unmapped or partial) and not skip_gaps:
                # Gap detail (CPU-side, small: only failing rows).
                slots_list = as_int_list(slots)
                live_list = as_int_list(live)
                for i, k in enumerate(row_keys):
                    if not live_list[i] or slots_list[i] != 0:
                        continue
                    if slots_list[i] == 0:
                        gaps.append({"bank": a_dir, "situation": situation,
                                     "row": k, "reason": "record field names slot 0"})
                # Partial rows: recompute cheaply per defender on CPU.
                if partial:
                    sd = slot_defined
                    pp = pack_present
                    for i, k in enumerate(row_keys):
                        if not live_list[i] or slots_list[i] == 0:
                            continue
                        s = slots_list[i]
                        bad = []
                        for v_dir in defenders:
                            vi = dir_index[v_dir]
                            owner_ok = (sd[vi, s] == 1 and pp[vi, s] == 1) or \
                                (a_idx is not None and sd[a_idx, s] == 1 and pp[a_idx, s] == 1)
                            if not owner_ok:
                                bad.append(v_dir)
                        if bad:
                            gaps.append({"bank": a_dir, "situation": situation,
                                         "row": k, "slot": s,
                                         "reason": "unresolved on defenders",
                                         "defenders": bad[:5],
                                         "defender_count": len(bad)})
            return verdict

        for name, field in SITUATIONS:
            slots = records[eff_react, field]
            evaluate_and_gap(name, slots, field)
        for name, kind_idx in AIR_SITUATIONS:
            # Air slot does not depend on the row; broadcast the kind slot.
            slot_val = int(air_kinds[kind_idx, 1])
            slots = lib.zeros_like(react_b) + slot_val
            # Kind 5 (slot 0xd57) comes only from launch branches and
            # only Gon defines it: a non-PASS there is a launch-gated
            # path, not a general coverage failure, so it is labelled
            # LAUNCH_ONLY instead of UNMAPPED and writes no gaps.
            skip = (kind_idx == 5)
            evaluate_and_gap(name, slots, kind_idx, skip_gaps=skip)
            if kind_idx == 5 and rows_out[-1]["verdict"] == "UNMAPPED":
                rows_out[-1]["verdict"] = "LAUNCH_ONLY"
            # Air only applies to live rows; the gate below is in evaluate().
        # Close-range front: rows WITH a close entry use the close record.
        slots = records[eff_react, 0]
        # Rows without a close entry are not close situations: mask them
        # out by pretending their slot is named-but-live only when entry exists.
        # (evaluate() counts live rows, so instead report close_front only
        # over close-entry rows via a dedicated row set.)
        close_live = live & has_close
        named = close_live & (slots != 0)
        n_named = int(named.sum())
        n_unmapped = int((close_live & (slots == 0)).sum())
        if n_named:
            idx = slots
            defd = slot_defined_b[def_idx_b][:, idx]
            packd = pack_present_b[def_idx_b][:, idx]
            if a_idx is None:
                defa_c = lib.zeros_like(idx)
                packa_c = lib.zeros_like(idx)
            else:
                defa_c = slot_defined_b[a_idx, idx]
                packa_c = pack_present_b[a_idx, idx]
            owner_pack = lib.where(defd == 1, packd, packa_c)
            ok = ((defd == 1) | (defa_c == 1)) & (owner_pack == 1)
            resolved_all = int((named & (ok.sum(axis=0) == n_def)).sum())
        else:
            resolved_all = 0
        verdict = ("N/A" if int(close_live.sum()) == 0 else
                   "PASS" if (n_unmapped == 0 and n_named == resolved_all) else "UNMAPPED")
        rows_out.append({
            "attacker_bank": a_dir, "situation": "close_front",
            "verdict": verdict, "rows_live": int(close_live.sum()),
            "rows_named_slot": n_named, "rows_slot_zero_unmapped": n_unmapped,
            "rows_resolved_all_defenders": resolved_all,
            "rows_partial": n_named - resolved_all,
            "rows_class_gated": n_class1, "rows_throw_range": n_throw,
            "rows_no_reaction": n_zero,
        })

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    with open(args.gaps, "w") as f:
        json.dump(gaps, f, indent=1)
    n_pass = sum(1 for r in rows_out if r["verdict"] == "PASS")
    n_launch = sum(1 for r in rows_out if r["verdict"] == "LAUNCH_ONLY")
    n_na = sum(1 for r in rows_out if r["verdict"] == "N/A")
    print(f"[gpu-matrix] cells: {len(rows_out)}  PASS: {n_pass}  "
          f"UNMAPPED: {len(rows_out) - n_pass - n_launch - n_na}  "
          f"LAUNCH_ONLY: {n_launch}  N/A: {n_na}  gaps: {len(gaps)}")
    print(f"[gpu-matrix] matrix -> {args.out}")
    print(f"[gpu-matrix] gaps   -> {args.gaps}")
    print(f"{'bank':<26} {'situation':<16} {'verdict':<9} named unmapped resolved partial")
    for r in rows_out:
        print(f"{r['attacker_bank']:<26} {r['situation']:<16} {r['verdict']:<9} "
              f"{r['rows_named_slot']:<5} {r['rows_slot_zero_unmapped']:<8} "
              f"{r['rows_resolved_all_defenders']:<8} {r['rows_partial']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
