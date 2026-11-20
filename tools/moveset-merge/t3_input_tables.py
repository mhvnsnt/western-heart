#!/usr/bin/env python3
"""Decoded Tekken 3 input timing -> game/assets/movesets/t3_input_tables.json (read by game/js/movesets.js).

Owner 2026-10-21: "Ur changes were probably hand tooled when they should have come from the teardown
files and code." The input buffer's timing therefore comes from the game itself:
  * motion windows: the USA EXE sequence tables (SEQ_TABLE_A 0x800954D0, 63 entries, commands
    0xC00E..; SEQ_TABLE_B 0x800955CC, 41 entries, 0xC7FF..), each = s16 window in frames + u16 steps
    (low nibble = numpad direction, high byte = buttons) — decoded by
    teardown/tekken3/tools/local/moveset_extract.py load_seq_tables (unchanged)
  * dash / backdash (commands 0xC001 / 0xC002): FUN_8002CB08 / FUN_8002CBF0 — direction, neutral,
    direction within a 0x13 (19) frame budget (n0madic/Tekken3Remake fight_sim.double_tap)
  * history: 60 one-frame entries (fight_sim HIST_LEN), the game runs at 60 fps
Usage: python3 tools/moveset-merge/t3_input_tables.py
"""
import hashlib, json, sys, types
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.modules.setdefault("motion", types.ModuleType("motion"))  # command decoding needs no motion parser
sys.path.insert(0, str(REPO / "teardown/tekken3/tools/local"))
import moveset_extract as ME  # noqa: E402

EXE = REPO / "teardown/tekken3/disc/files/TEKKEN3/SLUS_004.02"
NP = {1: "d/b", 2: "d", 3: "d/f", 4: "b", 5: "n", 6: "f", 7: "u/b", 8: "u", 9: "u/f"}


def dash_frames():
    """Length of the row the standing stance (slot 3) branches to on f,f / b,b (0xC001 / 0xC002),
    per decoded bank; the dash state lasts this long, so a button during it is a dash move."""
    import statistics
    out = {"f,f": [], "b,b": []}
    for p in sorted((REPO / "teardown/tekken3/movesets").glob("moveset_*.json")):
        d = json.loads(p.read_text())
        mi, rows = d["move_index"], {m["row"]: m for m in d["moves"]}
        if not isinstance(mi[3], int) or mi[3] not in rows:
            continue
        for b in rows[mi[3]]["branches"]:
            ts = b.get("target_slot")
            if b.get("command") in out and ts is not None and ts < len(mi) and isinstance(mi[ts], int) and mi[ts] in rows:
                out[b["command"]].append(rows[mi[ts]]["stream_frames"])
    return {k: int(statistics.median(v)) for k, v in out.items() if v}


def main():
    exe = EXE.read_bytes()
    seqs = ME.load_seq_tables(exe)
    out = []
    for cmd, (window, steps) in sorted(seqs.items()):
        dirs = [NP.get(s & 0xF, "?") for s in steps]
        # sequences that only differ by buttons (n,n,n... chain-throw button runs) carry no motion
        if all(d == "n" for d in dirs):
            continue
        out.append({"cmd": hex(cmd), "window": window, "dirs": dirs, "buttons": [s >> 8 for s in steps]})
    doc = {
        "format": "wh-t3-input/1",
        "tool": "tools/moveset-merge/t3_input_tables.py",
        "exe": str(EXE.relative_to(REPO)), "exe_sha256": hashlib.sha256(exe).hexdigest(),
        "history_frames": 60, "fps": 60, "double_tap_budget": 0x13,
        "dash_frames": dash_frames(),
        "sources": {"sequences": "SEQ_TABLE_A 0x800954D0 + SEQ_TABLE_B 0x800955CC (USA)",
                    "double_tap": "FUN_8002CB08 / FUN_8002CBF0 (fight_sim.double_tap)",
                    "dash_frames": "median stream_frames of the row slot 3 branches to on f,f / b,b, all decoded banks"},
        "open_item": "while-standing (WS.) window: the crouch-release row length is not decoded yet; "
                     "the engine keeps 0.35 s and says so (trace slot 40 -> stand-up row via fight_sim.branch_find).",
        "sequences": out,
    }
    dst = REPO / "game/assets/movesets/t3_input_tables.json"
    dst.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"{len(out)} motion sequences -> {dst.relative_to(REPO)}")


if __name__ == "__main__":
    main()
