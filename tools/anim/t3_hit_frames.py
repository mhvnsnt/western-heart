#!/usr/bin/env python3
"""Write each Tekken 3 bank's DECODED hit frames next to its clips: game/assets/anim/t3/<bankdir>/hit_frames.json.

Lane D, 2026-10-24. Every T3 move row carries its active window in the decoded move table
(teardown/tekken3/movesets/moveset_<char>.json, `active_first`/`active_last` = move bytes +0x2D/+0x2E:
"First and last active frame; attack segments exist only inside it. +0x2D = 0 means not an attack",
n0madic/Tekken3Remake docs/research/code/moves.md). The animation stream runs one pose per move frame
at 60 fps (moveFrame = 1 on the move's first frame), so a clip's hit lands at stream frame active_first.
game/js/t3anims.js loads this file and fighter.js warps each attack clip so that frame lands on the
WH move's startup (the first active frame of its hitbox). Nothing is measured or authored here: the
values are copied from the decoded table, with the table's SHA-256.

Output (format wh-hitframes/1):
  rows { "<row>": [active_first, active_last, stream_frames, attack_word, throw] }
       every row with active_first > 0, plus every throw row (throw = 1: reaction 0x1xxx, a throw attempt that
       selects its victim move from g_throwVictimSlots; or attack word 0x800 without posture bits, a throw-system
       row) -- n0madic/Tekken3Remake docs/research/code/combat.md "Throws" + reaction table
  button = mask of the buttons that start the row (1 LP, 2 RP, 4 LK, 8 RK): the decoded branch commands that
       target it (command_hex & 0xF), else the t3_command the WH movesets record for that row; 0 = unknown.
       fighter.js matches a move with no row of its own by this (1/2 = left/right punch, 3/4 = left/right kick).
  attack_word = decoded T3 attack word (0x412 high, 0x217 mid, 0x10F low, 0x31F s.mid, 0x607 unblockable,
                0x800 throw-class flag), the same word fighter.js reads from the movesets' hit_words.

Usage: python3 tools/anim/t3_hit_frames.py [--check]   (--check: exit 1 if any file is stale or missing)
"""
import argparse, collections, glob, hashlib, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BANKS = REPO / "game/assets/anim/t3"
TABLES = REPO / "teardown/tekken3/movesets"


def bank_source(d):
    """The divmot file a bank folder was decoded from (rows.pack.json, else its light clip)."""
    for f in ("rows.pack.json", "t3_light.json", "t3_neutral.json"):
        p = d / f
        if p.exists():
            src = json.loads(p.read_text()).get("bank")
            if src:
                return Path(src).name
    return None


BTN = {"LP": 1, "RP": 2, "LK": 4, "RK": 8}  # T3 command button bits (command_hex & 0xF: 0x000f = LP+RP+LK+RK)
# moveset t3_source -> decoded table name (teardown/tekken3/movesets/moveset_<name>.json)
SRC_TABLE = {"demonio": "jin", "deviljin": "jin", "armorking": "king", "armor-king": "king", "panda": "kuma"}


def branch_buttons(t):
    """row -> button mask of the decoded branch commands that start it (most common non-zero mask).
    A branch targets a move-index slot; move_index[slot] is the row (ints below COMMON_FLAG)."""
    mi, by = t.get("move_index") or [], collections.defaultdict(collections.Counter)
    for m in t["moves"]:
        for b in m["branches"]:
            s, h = b.get("target_slot"), b.get("command_hex")
            if h is None or not isinstance(s, int) or s >= len(mi) or not isinstance(mi[s], int) or mi[s] >= 0x40000000:
                continue
            if int(h, 16) & 0xF:
                by[mi[s]][int(h, 16) & 0xF] += 1
    return {r: c.most_common(1)[0][0] for r, c in by.items()}


def moveset_buttons():
    """table name -> row -> button mask from the WH movesets' T3 provenance (t3_command of moves whose t3_row
    is that row), for rows the decoded branch lists do not reach (stance/common-bank branches)."""
    out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for f in sorted((REPO / "game/assets/movesets").glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        mv = d.get("moves") if isinstance(d, dict) else None
        for m in (mv.values() if isinstance(mv, dict) else []):
            if not isinstance(m, dict) or not isinstance(m.get("t3_row"), int):
                continue
            src = m.get("t3_source") or d.get("t3_source")
            mask = 0
            for tok in re.findall(r"LP|RP|LK|RK", str(m.get("t3_command") or "")):
                mask |= BTN[tok]
            if src and mask:
                out[SRC_TABLE.get(src, src)][m["t3_row"]][mask] += 1
    return {k: {r: c.most_common(1)[0][0] for r, c in v.items()} for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    by_bin = {}
    for f in sorted(TABLES.glob("moveset_*.json")):
        t = json.loads(f.read_text())
        by_bin[t.get("bank")] = (f, t)
    stale = 0
    ms_btn = moveset_buttons()
    for d in sorted(p for p in BANKS.iterdir() if p.is_dir()):
        src = bank_source(d)
        if src not in by_bin:
            print(f"{d.name}: no decoded move table for {src} (MISSING)")
            continue
        f, t = by_bin[src]
        rows = {}
        dec_btn = branch_buttons(t)
        mbtn = ms_btn.get(f.stem[len("moveset_"):], {})
        for m in t["moves"]:
            word = int(m["attack_word"], 16)
            # Throw rows (decoded, combat.md): reaction (move +0x32) 0x1xxx = an entry of g_throwVictimSlots,
            # the victim move of a throw (a throw ATTEMPT row); attack word 0x800 with no posture bits =
            # "throw attempt (connects only through the throw system)" (throw execution rows).
            throw = int((m.get("reaction", 0) & 0xF000) == 0x1000 or ((word & 0x800) and not (word & 7)))
            if m.get("active_first", 0) > 0 or throw:
                # button: decoded branch command mask, else the movesets' t3_command for this row, else 0.
                btn = dec_btn.get(m["row"]) or mbtn.get(m["row"]) or 0
                rows[str(m["row"])] = [m["active_first"], m["active_last"], m["stream_frames"], word, throw, btn]
        out = {"format": "wh-hitframes/1", "bank": f"teardown/tekken3/animations/{src}",
               "source": str(f.relative_to(REPO)), "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
               "tool": "tools/anim/t3_hit_frames.py", "fps": 60,
               "fields": ["active_first", "active_last", "stream_frames", "attack_word", "throw", "button"], "rows": rows}
        dst = d / "hit_frames.json"
        txt = json.dumps(out, separators=(",", ":"))
        if a.check:
            if not dst.exists() or dst.read_text() != txt:
                print(f"{d.name}: hit_frames.json stale or missing")
                stale += 1
            continue
        dst.write_text(txt)
        print(f"{d.name}: {len(rows)} attack rows from {f.name} -> {dst.relative_to(REPO)} ({len(txt)} bytes)")
    sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main()
