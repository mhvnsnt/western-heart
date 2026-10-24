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
  attack_word = decoded T3 attack word (0x412 high, 0x217 mid, 0x10F low, 0x31F s.mid, 0x607 unblockable,
                0x800 throw-class flag), the same word fighter.js reads from the movesets' hit_words.

Usage: python3 tools/anim/t3_hit_frames.py [--check]   (--check: exit 1 if any file is stale or missing)
"""
import argparse, glob, hashlib, json, sys
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    by_bin = {}
    for f in sorted(TABLES.glob("moveset_*.json")):
        t = json.loads(f.read_text())
        by_bin[t.get("bank")] = (f, t)
    stale = 0
    for d in sorted(p for p in BANKS.iterdir() if p.is_dir()):
        src = bank_source(d)
        if src not in by_bin:
            print(f"{d.name}: no decoded move table for {src} (MISSING)")
            continue
        f, t = by_bin[src]
        rows = {}
        for m in t["moves"]:
            word = int(m["attack_word"], 16)
            # Throw rows (decoded, combat.md): reaction (move +0x32) 0x1xxx = an entry of g_throwVictimSlots,
            # the victim move of a throw (a throw ATTEMPT row); attack word 0x800 with no posture bits =
            # "throw attempt (connects only through the throw system)" (throw execution rows).
            throw = int((m.get("reaction", 0) & 0xF000) == 0x1000 or ((word & 0x800) and not (word & 7)))
            if m.get("active_first", 0) > 0 or throw:
                rows[str(m["row"])] = [m["active_first"], m["active_last"], m["stream_frames"], word, throw]
        out = {"format": "wh-hitframes/1", "bank": f"teardown/tekken3/animations/{src}",
               "source": str(f.relative_to(REPO)), "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
               "tool": "tools/anim/t3_hit_frames.py", "fps": 60,
               "fields": ["active_first", "active_last", "stream_frames", "attack_word", "throw"], "rows": rows}
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
