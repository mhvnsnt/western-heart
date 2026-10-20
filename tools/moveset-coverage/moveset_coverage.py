#!/usr/bin/env python3
"""tools/moveset-coverage/moveset_coverage.py — FULL MOVESET LAW coverage report.

The law (owner 2026-10-19): every Tripo-model fighter gets the FULL moveset
of their base character, 100+ moves, from real teardown data. This tool makes
that measurable: it scans the game's per-fighter moveset JSONs and reports,
per fighter file:

  - moves / strings / specials counts
  - the DATA BANK the moves came from (t3_bank / t3_source for Tekken 3 banks,
    doa_source for DOA5LR data, wh:* for WH-originals) and whether the file
    was bulk-generated from a full bank (generated_full_moveset provenance)
  - BANK MATCH: does the bank belong to the fighter's named base character?
    (jin bank for a Jin-based fighter = match; jin bank for a Katarina-based
    fighter = an assigned style bank, NOT the base character's own moveset)
  - the file's own proxy flag (proxy=true means the file itself declares the
    moveset borrowed)
  - anim coverage: % of moves carrying an anim_ref (a move without one cannot
    be played back by the engine)
  - law status:
        FULL-REAL    >= law-min moves, real teardown data, bank == base
        FULL-BANKED  >= law-min moves from a real teardown bank that is NOT
                     the named base's own bank (assigned style bank)
        REAL-THIN    real data but < law-min moves (partial extraction)
        PROXY        the file itself declares proxy=true

Usage:
    python3 moveset_coverage.py [--dir game/assets/movesets]
        [--md docs/MOVESET-COVERAGE.md] [--json-out R.json]
        [--law-min 100] [--quiet]
Exit 0 always (it's a report, not a gate) unless the dir is missing (2).
The markdown table it writes is the canonical coverage snapshot; regenerate
after any moveset extraction lands.
"""

import argparse
import glob
import json
import os
import re
import sys


def bank_label(d):
    """Human label of where the moves came from."""
    if d.get("t3_bank"):
        return d["t3_bank"]
    if d.get("t3_source"):
        return f"t3:{d['t3_source']}"
    for fld in ("doa_source", "vf_source", "sf_source", "kof_source"):
        if d.get(fld):
            return str(d[fld])[:48]
    return "—"


def bank_key(d):
    """Short key of the bank's owner character, for base matching."""
    if d.get("t3_source"):
        return d["t3_source"]
    if d.get("doa_source"):
        return "doa"
    return None


def bank_matches_base(d):
    """Does the bank belong to the named base character? Heuristic on names:
    'jin' in 'Jin Kazama' -> yes; 'jin' in 'Katarina' -> no. Returns None when
    there is no comparable bank (DOA/VF-sourced files carry their own data)."""
    key = bank_key(d)
    base = (d.get("tekken_base") or "").lower()
    if key is None or not base:
        return None
    key_n = re.sub(r"[^a-z0-9]", "", key.lower())
    base_n = re.sub(r"[^a-z0-9]", "", base)
    if key_n and key_n in base_n:
        return True
    # multi-word banks: 'armor king' vs base containing 'armorking'
    if key_n in ("armorking",) and "armorking" in base_n:
        return True
    return False


def analyze_file(path):
    with open(path) as f:
        d = json.load(f)
    moves = d.get("moves") or {}
    if isinstance(moves, list):
        moves = {str(i): m for i, m in enumerate(moves)}
    strings = d.get("strings") or []
    specials = d.get("specials") or []
    n_moves = len(moves)
    with_anim = sum(1 for m in moves.values()
                    if isinstance(m, dict) and m.get("anim_ref"))
    gen = d.get("generated_full_moveset") or {}
    return {
        "fighter": d.get("fighter") or os.path.basename(path)[:-5],
        "display": d.get("display") or "",
        "base": d.get("tekken_base") or "?",
        "moves": n_moves,
        "strings": len(strings),
        "specials": len(specials),
        "total": n_moves + len(strings) + len(specials),
        "anim_ref_pct": round(100.0 * with_anim / n_moves, 1) if n_moves else 0.0,
        "proxy": bool(d.get("proxy")),
        "bank": bank_label(d),
        "bank_match": bank_matches_base(d),
        "bank_rows": d.get("t3_bank_rows"),
        "generated": bool(gen),
    }


def status(row, law_min):
    if row["proxy"]:
        return "PROXY"
    if row["moves"] >= law_min:
        return "FULL-REAL" if row["bank_match"] else "FULL-BANKED"
    return "REAL-THIN"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="game/assets/movesets")
    ap.add_argument("--md", default=None, help="write markdown report here")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--law-min", type=int, default=100)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.dir, "*.json")))
    if not files:
        sys.stderr.write(f"no moveset JSONs under {a.dir}\n")
        sys.exit(2)
    rows = []
    for f in files:
        r = analyze_file(f)
        r["status"] = status(r, a.law_min)
        rows.append(r)
    order = {"FULL-REAL": 0, "FULL-BANKED": 1, "REAL-THIN": 2, "PROXY": 3}
    rows.sort(key=lambda r: (order[r["status"]], -r["moves"]))

    summary = {
        "fighter_files": len(rows),
        "total_moves": sum(r["total"] for r in rows),
        "moves_only": sum(r["moves"] for r in rows),
        "full_real": sum(1 for r in rows if r["status"] == "FULL-REAL"),
        "full_banked": sum(1 for r in rows if r["status"] == "FULL-BANKED"),
        "real_thin": sum(1 for r in rows if r["status"] == "REAL-THIN"),
        "proxy": sum(1 for r in rows if r["status"] == "PROXY"),
        "law_min": a.law_min,
    }
    report = {"summary": summary, "fighters": rows}
    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump(report, f, indent=2)

    lines = []
    lines.append("# MOVESET COVERAGE — FULL MOVESET LAW")
    lines.append("")
    lines.append("Generated by `tools/moveset-coverage/moveset_coverage.py` "
                 f"from `{a.dir}/`. Regenerate after any moveset extraction lands. "
                 "One row per moveset FILE (attire/variant files counted separately).")
    lines.append("")
    lines.append(f"- Fighter files: **{summary['fighter_files']}**")
    lines.append(f"- Moves (base `moves` only): **{summary['moves_only']}** "
                 f"(+{summary['total_moves'] - summary['moves_only']} strings/specials "
                 f"= {summary['total_moves']} total)")
    lines.append(f"- FULL-REAL (>= {a.law_min} moves, base character's own bank): "
                 f"**{summary['full_real']}**")
    lines.append(f"- FULL-BANKED (>= {a.law_min} moves, real teardown bank assigned "
                 f"as style, not the base's own): **{summary['full_banked']}**")
    lines.append(f"- REAL-THIN (real data, < {a.law_min} moves): "
                 f"**{summary['real_thin']}**")
    lines.append(f"- PROXY (file declares proxy=true): **{summary['proxy']}**")
    lines.append("")
    lines.append("| Fighter | Base | Moves | Strings | Specials | Anim % | Bank | Bank=Base | Status |")
    lines.append("|---|---|---:|---:|---:|---:|---|:---:|---|")
    for r in rows:
        bm = {True: "yes", False: "no", None: "—"}[r["bank_match"]]
        lines.append(f"| {r['fighter']} | {r['base']} | {r['moves']} | "
                     f"{r['strings']} | {r['specials']} | {r['anim_ref_pct']} | "
                     f"{r['bank'][:44]} | {bm} | {r['status']} |")
    lines.append("")
    lines.append("Status key: FULL-REAL = FULL MOVESET LAW met with the base "
                 "character's own decoded data · FULL-BANKED = full-depth real "
                 "teardown bank assigned as the fighter's style bank (e.g. a T7-era "
                 "base with no T3 bank of its own) · REAL-THIN = real data, partial "
                 "extraction · PROXY = the file itself declares the moveset borrowed.")
    md = "\n".join(lines) + "\n"
    if a.md:
        with open(a.md, "w") as f:
            f.write(md)
    if not a.quiet:
        print(md)
    print(json.dumps(summary), file=sys.stderr)


if __name__ == "__main__":
    main()
