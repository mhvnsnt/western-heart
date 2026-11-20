#!/usr/bin/env python3
"""tools/moveset-merge/repair_slots.py: re-point the moveset slots that the old notation reading hijacked.

Before 2026-11-01, merge_sources.notation_of misread three kinds of input:
  * a real tilde input as a source tag: '3~4' -> '3';
  * the while-running state as plain: 'WR 4' -> '4' (notation.py DESCR);
  * an unparsed string as its first hit: '1,2,&amp;#58;4' -> '1', via input_slots[0].
The slot table then fired those moves on the plain button: Purple Rain's 1 played the 3-hit string
1,2,:4 and its 3 played 3~3, Phantom's 3 played 3~4, Negativo's 4 played WR 4.

This tool finds every slot the OLD reading put there whose move answers to a DIFFERENT input under the fixed
reading, then re-points it to the move merge_sources would slot there now. Priority is merge_one's, unchanged:
  1. signature > T8 base > T7 base > T3 base > curated/donor > proxy bank;
  2. then unconditional rows;
  3. then the exact key;
  4. then file order.
Only slots on a button input (the notation holds 1-4) are re-pointed. A slot that no move answers to (movement
inputs such as 'f,f,F') is reported and left alone. Only the changed slot lines are rewritten, so every other
byte of each moveset file stays as it is.

    python3 tools/moveset-merge/repair_slots.py              # report; exit 1 if a slot needs repair
    python3 tools/moveset-merge/repair_slots.py --write      # rewrite those slot lines in place
    python3 tools/moveset-merge/repair_slots.py --only purplerain,phantom
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import merge_sources as MS  # noqa: E402
import notation as N  # noqa: E402

BUTTON = re.compile(r"[1-4]")
# The pre-2026-11-01 reading, kept ONLY to find the slots it assigned. Slots other tools alias on purpose
# ('BT.2' -> 'BT.1', Pantera's '3+4,1' -> 'JGS.1') answer to another input under BOTH readings and are left alone.
LEGACY_VARIANT = re.compile(r"(?:_[cr]\d+)+(?:_\d+)?$|__\w+$|_t[378]$|~[\w.]+$")


def legacy_canon(raw):
    """notation.canon as it was: one unescape (a twice-escaped '&#58;' stayed unparsed), a token opening with
    ':' / '~' unparsed, and 'WR 4' read as plain '4'."""
    s = html.unescape(str(raw)).strip()
    if "&#" in s or re.search(r",\s*[:~]|^[:~]", s):
        return None
    if not re.match(r"wr\s*\+", s, re.I):
        s = re.sub(r"^wr\s+", "", s, flags=re.I)
    return N.canon(s)[0]


def legacy_notation_of(key, m):
    for cand in (m.get("input"), key, (m.get("input_slots") or [None])[0], m.get("t7_command")):
        if cand:
            nt = legacy_canon(LEGACY_VARIANT.sub("", str(cand)))
            if nt:
                return nt
    return None


def answers_to(k, m, specials):
    """The input move k answers to under the fixed reading (merge_one's rule: notation, else the key itself
    when the old buffer could fire it)."""
    nt = MS.notation_of(k, m)
    if not nt and MS.reachable_old(k, specials):
        nt = k
    return nt


def plan(fid, cur, over):
    """[(notation, old_key, new_key or None)] for this fighter's hijacked button slots."""
    slots, moves = cur.get("slots"), cur.get("moves")
    if not isinstance(slots, dict) or not isinstance(moves, dict):
        return []
    B = MS.bases_for(fid, cur, over)
    specials = {sp.get("input") for sp in cur.get("specials") or [] if isinstance(sp, dict)}
    owner = {}
    for idx, (k, m) in enumerate(moves.items()):
        if not isinstance(m, dict):
            continue
        nt = answers_to(k, m, specials)
        if not nt:
            continue
        t = MS.tier(m, B)
        if t == 5 and B.get("exclude_proxy"):
            continue
        rank = (t, 1 if (m.get("t3_condition") or m.get("t3_restriction")) else 0, 0 if k == nt else 1, idx)
        if nt not in owner or rank < owner[nt][0]:
            owner[nt] = (rank, k)
    out = []
    for nt, k in slots.items():
        m = moves.get(k)
        if not isinstance(m, dict) or not BUTTON.search(nt):
            continue
        if answers_to(k, m, specials) == nt or legacy_notation_of(k, m) != nt:
            continue  # right input, or a deliberate alias the old reading did not make
        out.append((nt, k, owner[nt][1] if nt in owner else None))
    return out


def rewrite(text, fixes):
    """Rewrite only the '"<notation>": "<key>"' lines inside the top-level "slots" object."""
    lines = text.split("\n")
    start = next(i for i, ln in enumerate(lines) if re.match(r'^(\s*)"slots": \{\s*$', ln))
    indent = re.match(r"^(\s*)", lines[start]).group(1)
    done = set()
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if re.match(r"^" + indent + r"\}", ln):
            break
        body = ln.strip()
        comma = body.endswith(",")
        try:
            (nt, k), = json.loads("{" + body.rstrip(",") + "}").items()
        except ValueError:
            continue
        if nt in fixes and fixes[nt][0] == k:
            ea = "\\u" in ln
            lead = ln[:len(ln) - len(ln.lstrip())]
            lines[i] = lead + json.dumps(nt, ensure_ascii=ea) + ": " + json.dumps(fixes[nt][1], ensure_ascii=ea) + ("," if comma else "")
            done.add(nt)
    missing = set(fixes) - done
    if missing:
        raise SystemExit(f"slot lines not found for {sorted(missing)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    over = json.loads((HERE / "bases.json").read_text())["override"]
    only = set(filter(None, a.only.split(",")))
    need, left = 0, []
    for p in sorted(MS.MS_DIR.glob("*.json")):
        if only and p.stem not in only:
            continue
        text = p.read_text()
        try:
            cur = json.loads(text)
        except ValueError:
            continue
        if not isinstance(cur, dict):
            continue
        rows = plan(p.stem, cur, over)
        fixes = {nt: (old, new) for nt, old, new in rows if new}
        for nt, old, new in rows:
            if new:
                print(f"{p.stem:20s} {nt!r:14s} {old!r} -> {new!r}")
            else:
                left.append(f"{p.stem}: {nt!r} -> {old!r} (no move answers to {nt!r}; left as is)")
        need += len(fixes)
        if a.write and fixes:
            after = rewrite(text, fixes)
            check = json.loads(after)
            assert {k: v for k, v in check.items() if k != "slots"} == {k: v for k, v in cur.items() if k != "slots"}
            p.write_text(after)
    for x in left:
        print("left:", x)
    print(f"{need} slot(s) {'re-pointed' if a.write else 'need repair'}; {len(left)} left as is")
    return 0 if (a.write or need == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
