#!/usr/bin/env python3
"""Restore the per-fighter move data destroyed by commit 8ebdc527 ("Sweep repair: restore true
union tree for PR #338", merged to main in PR #338).

What the sweep did (measured, 2026-10-20): in 49 game/assets/movesets/*.json files it replaced the
`moves` table (dict of input -> full move record: startup/active/recovery, damage, t3_row, limb,
anim_ref, ...) with a bare list of the input strings, and resolved the forward-merge staging fields
(`strings__main`, `specials__main`) by keeping ONE side, so rich string/special records were lost
(e.g. pantera 370 rich moves -> 0; byou 29 rich strings -> 4).

Repair (no authored data; every record comes from git history):
  moves    = the sweep's parent 4cc6b41b `moves` dict (verified a key superset of the sweep list)
  strings  = union by input of 4cc6b41b `strings` and `strings__main`, rich dict records preferred
  specials = same for `specials` / `specials__main`
  `*__main` staging fields are folded into the union (their content is kept, the field is not).
All other fields are kept exactly as they are now.

Usage: python3 tools/moveset-restore/restore_sweep_338.py [--check]
"""
import json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRE = "4cc6b41b"


def git_json(ref, path):
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def key_of(e):
    return e.get("input") if isinstance(e, dict) else e


def union(*lists):
    out, idx = [], {}
    for lst in lists:
        for e in lst or []:
            k = json.dumps(key_of(e))
            if k not in idx:
                idx[k] = len(out); out.append(e)
            elif isinstance(e, dict) and not isinstance(out[idx[k]], dict):
                out[idx[k]] = e  # rich record wins over a bare input string
    return out


def main():
    check = "--check" in sys.argv
    n = 0
    for f in sorted((REPO / "game/assets/movesets").glob("*.json")):
        cur = json.loads(f.read_text())
        if not isinstance(cur, dict) or not isinstance(cur.get("moves"), list):
            continue
        if any(isinstance(x, dict) for x in cur["moves"]):
            continue
        rel = str(f.relative_to(REPO))
        pre = git_json(PRE, rel)
        if not pre or not isinstance(pre.get("moves"), dict):
            print(f"SKIP {f.name}: no rich pre-sweep moves"); continue
        missing = set(cur["moves"]) - set(pre["moves"])
        if missing:
            print(f"SKIP {f.name}: sweep list has keys absent before it: {sorted(missing)[:5]}"); continue
        new = dict(cur)
        new["moves"] = pre["moves"]
        for fld in ("strings", "specials"):
            new[fld] = union(pre.get(fld), pre.get(fld + "__main"), cur.get(fld))
        new["restored_from_sweep_338"] = {
            "date": "2026-10-20", "by": "tools/moveset-restore/restore_sweep_338.py",
            "source_commit": PRE, "destroyed_by": "8ebdc527",
            "moves": len(new["moves"]), "strings": len(new["strings"]), "specials": len(new["specials"])}
        n += 1
        if check:
            print(f"{f.name}: moves {len(cur['moves'])} names -> {len(new['moves'])} records; strings "
                  f"{len(cur.get('strings') or [])} -> {len(new['strings'])}; specials {len(cur.get('specials') or [])} -> {len(new['specials'])}")
        else:
            f.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
    print(f"{'would restore' if check else 'restored'} {n} files")


if __name__ == "__main__":
    main()
