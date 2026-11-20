#!/usr/bin/env python3
"""Reconcile PR #988 restored moves against the embedded T8 quarantine records.

WHY THIS EXISTS
---------------
PR #988 (`fix/anim-true-mapping-20261023`) promoted the moves that had been
quarantined under each moveset JSON's embedded `t8_quarantine_20261024`
section back into the live `moves` dict, and added the new `anim_t3`
(true-map) animation mapping to each restored move. The restore dropped
fields that only the quarantine record still carried, and on one Pantera
move it resurrected the pre-fix T8 throw reading that a documented fix
had already corrected to a T7 strike.

RECONCILE RULE (quarantine-newer data wins; #988's anim_t3 is the one
exception; a documented fix is never overwritten)
--------------------------------------------------
For every restored move (a live `moves` entry whose key -- or `input` --
matches a quarantine entry) in every `game/assets/movesets/*.json`:

1. MISSING-IN-LIVE fields are restored from the quarantine entry, EXCEPT
   `t3_row` / `t3_source` when the live move already has `anim_t3`: the
   flat fields are the pre-#988 animation record and `anim_t3` supersedes
   them -- restoring them would outrank the true-map in fighter.js clip
   selection (`own` t3_row is tried before `anim`) and silently revert
   #988's mapping. Those are logged SUPERSEDED, not restored.
2. DIFFERING fields take the quarantine value, EXCEPT `damage` on a move
   listed in the file's documented damage fix
   (`string_fix_20261024.damage_fixed_keys`): that damage is the
   documented T7-MOD string-step value, so the live value is KEPT and the
   diff is logged, not applied.
3. LIVE-ONLY fields are kept, EXCEPT `throw_break` (and any throw field)
   on a move listed in the file's documented strike fix
   (`string_fix_20261024.throw_flag_fixed_to_T7_strike`): a documented
   T7 strike must not carry throw fields. Those are DELETED.
4. `anim_t3` is never touched: it is #988's new mapping and the only
   #988 addition merged in.

The script is idempotent: after a run, a second run reports 0 actionable
differences (kept-documented-fix and superseded-by-anim_t3 diffs are
reported every run as informational, and do not count as actionable).

USAGE
-----
    python3 tools/reconcile-988-quarantine.py [--root REPO] [--check]

    --check   dry run: report only, write nothing, exit 1 if any
              actionable difference exists (0 otherwise).
    default   apply in place and print the report.

SAFETY
------
* A file is only rewritten if it round-trips byte-identically through
  `json.dumps(indent=2) + "\\n"` before editing -- a file whose on-disk
  formatting differs is skipped with a warning instead of reformatted.
* Only moveset JSONs under `game/assets/movesets/` are read or written.
  Nothing else in the repo is touched.
* After applying, the script re-scans its own output in memory and
  asserts 0 remaining actionable differences.
"""

import argparse
import copy
import json
import sys
from pathlib import Path

MOVESET_GLOB = "game/assets/movesets/*.json"

# Flat pre-#988 animation fields, superseded by the structured anim_t3 map.
SUPERSEDED_ANIM_FIELDS = ("t3_row", "t3_source")

# Fields that must never survive on a documented T7 strike.
THROW_FIELDS = ("throw", "isGrab", "throw_break", "unblockable")


def find_fix_lists(doc):
    """Collect documented-fix move lists from a moveset file.

    Returns (damage_fixed_keys, throw_fixed_to_strike_keys): move keys
    whose live `damage` / throw reading a documented fix owns.
    """
    damage_fixed, throw_fixed = set(), set()
    for value in doc.values():
        if not isinstance(value, dict):
            continue
        for field, val in value.items():
            if not isinstance(val, list):
                continue
            if field == "damage_fixed_keys":
                damage_fixed.update(str(x) for x in val)
            elif field == "throw_flag_fixed_to_T7_strike":
                throw_fixed.update(str(x) for x in val)
    return damage_fixed, throw_fixed


def reconcile_file(path, apply):
    """Reconcile one moveset JSON. Returns (actions, notes, changed)."""
    raw = path.read_bytes()
    doc = json.loads(raw)
    quarantines = {k: v for k, v in doc.items()
                   if "quarantine" in k.lower() and isinstance(v, dict)}
    if not quarantines:
        return [], [], False
    # Safety: only rewrite a file whose bytes round-trip through
    # json.dumps(indent=2) + newline -- never reformat a live file.
    if (json.dumps(doc, indent=2) + "\n").encode() != raw:
        return [], [f"{path}: SKIP -- on-disk formatting does not round-trip "
                    "through json.dumps(indent=2); refusing to reformat"], False
    moves = doc.get("moves")
    if not isinstance(moves, dict):
        return [], [f"{path}: SKIP -- no `moves` dict"], False
    damage_fixed, throw_fixed = find_fix_lists(doc)

    # Index live moves by key and by input (quarantine keys are not always
    # the live key; the `input` field is the stable join).
    by_input = {}
    for key, mv in moves.items():
        if isinstance(mv, dict) and mv.get("input"):
            by_input.setdefault(mv["input"], key)

    actions, notes = [], []
    for qsection, entries in quarantines.items():
        for qkey, qv in entries.items():
            if not isinstance(qv, dict):
                notes.append(f"{path} {qkey}: SKIP -- quarantine entry not an object")
                continue
            live_key = qkey if qkey in moves else by_input.get(qv.get("input") or qkey)
            if live_key is None or not isinstance(moves.get(live_key), dict):
                notes.append(f"{path} {qkey}: UNMATCHED -- no live move for quarantine entry")
                continue
            live = moves[live_key]
            is_strike_fix = live_key in throw_fixed
            # 1+2. Quarantine fields: restore missing, correct differing.
            for field in qv:
                if field == "anim_t3":
                    continue  # #988's mapping; never touched either way.
                if field not in live:
                    if field in SUPERSEDED_ANIM_FIELDS and "anim_t3" in live:
                        agree = (live["anim_t3"].get("row") == qv.get("t3_row")
                                 and live["anim_t3"].get("bank") == qv.get("t3_source"))
                        notes.append(f"{path} {live_key}: SUPERSEDED {field}={qv[field]!r} "
                                     f"-- live anim_t3 {live['anim_t3']} wins "
                                     f"({'same row' if agree else 'DIFFERENT row: true-map wins'})")
                        continue
                    live[field] = copy.deepcopy(qv[field])
                    actions.append(f"{path} {live_key}: RESTORED {field}={qv[field]!r}")
                elif live[field] != qv[field]:
                    if field == "damage" and live_key in damage_fixed:
                        notes.append(f"{path} {live_key}: KEPT-DOCUMENTED-FIX damage "
                                     f"live={live[field]!r} quar={qv[field]!r} "
                                     "-- in damage_fixed_keys, live value stands")
                        continue
                    old = live[field]
                    live[field] = copy.deepcopy(qv[field])
                    actions.append(f"{path} {live_key}: CORRECTED {field} "
                                   f"{old!r} -> {qv[field]!r}")
            # 3. Live-only fields: keep, except throw fields on a
            # documented strike.
            for field in list(live):
                if field in qv or field == "anim_t3":
                    continue
                if is_strike_fix and field in THROW_FIELDS:
                    old = live.pop(field)
                    actions.append(f"{path} {live_key}: DELETED-CONTRADICTING "
                                   f"{field}={old!r} -- documented T7 strike")
                else:
                    notes.append(f"{path} {live_key}: KEPT-LIVE-ONLY {field}={live[field]!r}")
            # Invariant: a documented strike must not read as a throw.
            if is_strike_fix and (live.get("throw") or live.get("isGrab")
                                  or live.get("move_class") == "throw"):
                notes.append(f"{path} {live_key}: VIOLATION -- still reads as throw "
                             "after reconcile; needs a human look")

    changed = bool(actions)
    if changed and apply:
        path.write_bytes((json.dumps(doc, indent=2) + "\n").encode())
    return actions, notes, changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None,
                    help="repo root (default: parent of tools/ holding this script)")
    ap.add_argument("--check", action="store_true",
                    help="dry run: report only, write nothing")
    args = ap.parse_args()
    root = Path(args.root) if args.root else Path(__file__).resolve().parents[1]
    files = sorted(root.glob(MOVESET_GLOB))
    if not files:
        print(f"no moveset JSONs found under {root / MOVESET_GLOB}")
        return 2

    all_actions, all_notes = [], []
    changed_files = []
    for path in files:
        actions, notes, changed = reconcile_file(path, apply=not args.check)
        # Report paths relative to the repo root, not absolute.
        rel = str(path.relative_to(root))
        all_actions.extend(a.replace(str(path), rel) for a in actions)
        all_notes.extend(n.replace(str(path), rel) for n in notes)
        if changed:
            changed_files.append(rel)
    print(f"files scanned: {len(files)}  files changed: {len(changed_files)}")
    for f in changed_files:
        print(f"  changed: {f}")
    print(f"actions applied: {len(all_actions)}")
    for a in all_actions:
        print(f"  {a}")
    print(f"informational notes: {len(all_notes)}")
    for n in all_notes:
        print(f"  {n}")
    if args.check:
        print(f"actionable differences found: {len(all_actions)}")
        return 1 if all_actions else 0
    # Idempotency self-check: re-scan the rewritten files in memory;
    # no actionable difference may remain after an apply run.
    remaining = 0
    for path in files:
        actions, _, _ = reconcile_file(path, apply=False)
        remaining += len(actions)
    print(f"idempotency re-scan actionable differences remaining: {remaining}")
    if remaining:
        print("ERROR: reconcile did not converge -- investigate before committing",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
