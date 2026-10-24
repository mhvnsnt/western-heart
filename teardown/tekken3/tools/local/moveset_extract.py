#!/usr/bin/env python3
"""Extract Tekken 3 movesets from motion banks: move lists, input mappings,
frame data.

For each bank (divmotNN.bin):
- move rows (section 1): frame count, damage, active window, state/attack
  words, stance, heading, step, air window, hold, flags, hit freeze,
  body-sphere, reaction records, sound/event/attack refs
- branch rows (section 0): input commands decoded to human-readable inputs
  (buttons, directions, double-taps, motion sequences from the USA EXE
  tables at 0x800954D0 / 0x800955CC)
- event lists (section 4): (frame, command) pairs

Output: moveset_<fighter>.json + moveset_<fighter>.csv per bank, plus
MOVESET-SUMMARY.md.

Move names are not in the banks (they live in the ARC move-list text);
moves are identified by move-index slot and row.
"""

from __future__ import annotations

import csv
import json
import struct
import sys
from pathlib import Path

LOCAL = Path(__file__).resolve().parent
RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(LOCAL))
sys.path.insert(0, str(RESEARCH))
import motion  # noqa: E402

EXE_PATH = Path("/home/hatch/workspace/game-reverse-engineering/tekken3/disc/files/TEKKEN3/SLUS_004.02")
EXE_BASE, EXE_HEADER = 0x80010000, 0x800
# USA motion-sequence pointer tables (verified: all 63 + 41 entries dereference).
SEQ_TABLE_A = 0x800954D0  # 63 entries, commands 0xC00E..0xC04C
SEQ_TABLE_B = 0x800955CC  # 41 entries, commands 0xC7FF..0xC827

BUTTONS = ("LP", "RP", "LK", "RK")


def _u16(exe: bytes, addr: int) -> int:
    return struct.unpack_from("<H", exe, addr - EXE_BASE + EXE_HEADER)[0]


def _u32(exe: bytes, addr: int) -> int:
    return struct.unpack_from("<I", exe, addr - EXE_BASE + EXE_HEADER)[0]


def _s16(exe: bytes, addr: int) -> int:
    v = _u16(exe, addr)
    return v - 0x10000 if v & 0x8000 else v


def read_sequence(exe: bytes, addr: int) -> tuple[int, list[int]]:
    window = _s16(exe, addr)
    steps, p = [], addr + 2
    while (s := _u16(exe, p)) != 0:
        steps.append(s)
        p += 2
    return window, steps


def load_seq_tables(exe: bytes) -> dict[int, tuple[int, list[int]]]:
    out = {}
    for base, count, first in ((SEQ_TABLE_A, 63, 0xC00E), (SEQ_TABLE_B, 41, 0xC7FF)):
        for i in range(count):
            ptr = _u32(exe, base + 4 * i)
            out[first + i] = read_sequence(exe, ptr)
    return out


def step_text(step: int) -> str:
    direction, spec = step & 0xF, step >> 8
    text = str(direction)
    if spec & 0x1F == 0x10 or spec == 0:
        return text
    names = "+".join(b for i, b in enumerate(BUTTONS) if spec & (1 << i))
    return f"{text}{'(any ' if spec & 0x10 else '+'}{names}{')' if spec & 0x10 else ''}"


def command_text(cmd: int, seqs: dict[int, tuple[int, list[int]]]) -> str:
    if cmd == 0xC000:
        return "<end>"
    if cmd == 0xC00D:
        return "<no-input>"
    if cmd == 0xC001:
        return "f,f"
    if cmd == 0xC002:
        return "b,b"
    if cmd == 0xC00C:
        return "<common>"
    if cmd in seqs:
        window, steps = seqs[cmd]
        return f"[{' '.join(step_text(s) for s in steps)}]({window}f)"
    if cmd < 0xC000:
        parts = []
        btns = [b for i, b in enumerate(BUTTONS) if cmd & (1 << i)]
        dirs = [str(d) for d in range(1, 10) if d != 5 and (cmd & (1 << (d + 4)))]
        if dirs:
            parts.append("/".join(dirs))
        if cmd & 0x10:
            parts.append("any+" + "+".join(btns) if btns else "any-button")
        elif btns:
            parts.append("+".join(btns))
        elif not dirs:
            parts.append("<no-button>")
        return "+".join(parts)
    return f"<cmd {cmd:#06x}>"


def extract_bank(bank_path: Path, exe: bytes, seqs, common: "motion.MotionBank | None" = None,
                 common_data: bytes | None = None) -> dict:
    data = bank_path.read_bytes()
    bank = motion.parse_bank(data)
    b = bank.bounds
    moves = []
    for row in range(bank.move_count):
        r = bank.move_row(row)
        anim_word, state, atk_lo = r[0], r[1], r[2] & 0xFFFF
        ai_hint = (r[2] >> 16) & 0xFF
        branches, stance = r[3], r[4] & 0xFFFF
        heading = r[4] >> 16
        if heading & 0x8000:
            heading -= 0x10000
        damage = r[5] & 0x3FFF
        atk_class = (r[5] >> 14) & 0x3
        step = r[5] >> 16
        if step & 0x8000:
            step -= 0x10000
        nframes = data[b[1] + row * 0x38 + 0x18]
        air_first, air_last = data[b[1] + row * 0x38 + 0x19], data[b[1] + row * 0x38 + 0x1A]
        hold = data[b[1] + row * 0x38 + 0x1B]
        sound_idx, event_idx = r[7], r[8]
        flags = r[9]
        atk_desc = r[10]
        hit_freeze = data[b[1] + row * 0x38 + 0x2C]
        act_first, act_last = data[b[1] + row * 0x38 + 0x2D], data[b[1] + row * 0x38 + 0x2E]
        body_sphere = r[12] & 0xFFFF
        reaction = r[12] >> 16
        close_reaction = r[13] & 0xFFFF
        # animation stream frame count + tag (resolve divmot99 common bank)
        stream_frames, tag, common_anim = None, None, False
        if anim_word < motion.COMMON_FLAG:
            off = bank.anim_offset(anim_word)
            tag = struct.unpack_from("<h", data, off - 2)[0]
            stream_frames = motion.parse_anim(data, off).frames
        elif common is not None and common_data is not None:
            off = common.anim_offset(anim_word - motion.COMMON_FLAG)
            tag = struct.unpack_from("<h", common_data, off - 2)[0]
            stream_frames = motion.parse_anim(common_data, off).frames
            common_anim = True
        # branch list (move+0x0C is a branch-row INDEX; relocated to branches+12*index)
        branch_list = []
        if branches != 0xFFFFFFFF:
            p = b[0] + 12 * branches
            while True:
                cmd = struct.unpack_from("<H", data, p)[0]
                if cmd == 0xC000:
                    tgt = struct.unpack_from("<H", data, p + 6)[0]
                    branch_list.append({"command": "<end>", "target_slot": tgt})
                    break
                restriction, cond = data[p + 2], data[p + 3]
                param = struct.unpack_from("<H", data, p + 4)[0]
                tgt = struct.unpack_from("<H", data, p + 6)[0]
                flags_b, first, last, entry = data[p + 8], data[p + 9], data[p + 10], data[p + 11]
                branch_list.append({
                    "command": command_text(cmd, seqs),
                    "command_hex": f"{cmd:#06x}",
                    "restriction": restriction, "condition": cond,
                    "condition_param": param, "target_slot": tgt,
                    "flags": flags_b, "first": first, "last": last, "entry": entry,
                })
                p += 12
                if len(branch_list) > 200:
                    branch_list.append({"error": "branch list too long, truncated"})
                    break
        # event list
        events = []
        if event_idx != 0xFFFFFFFF:
            p = b[4] + 4 * event_idx
            for _ in range(256):
                fr, cm = struct.unpack_from("<HH", data, p)
                p += 4
                if fr == 0xFFFF:
                    break
                events.append({"frame": fr, "command": f"{cm:#06x}"})
        moves.append({
            "row": row,
            "stream_frames": stream_frames if stream_frames is not None else nframes,
            "common_anim": common_anim,
            "anim_tag": tag,
            "damage": damage, "attack_class": atk_class,
            "active_first": act_first, "active_last": act_last,
            "state_word": f"{state:#010x}", "attack_word": f"{atk_lo:#06x}",
            "ai_hint": ai_hint, "stance_slot": stance, "heading_change": heading,
            "step_per_frame": step, "air_first": air_first, "air_last": air_last,
            "hold_frame": hold, "flags": f"{flags:#010x}",
            "hit_freeze": hit_freeze, "body_sphere": body_sphere,
            "reaction": reaction, "close_reaction": close_reaction,
            "sound_idx": None if sound_idx == 0xFFFFFFFF else sound_idx,
            "event_idx": None if event_idx == 0xFFFFFFFF else event_idx,
            "attack_desc": f"{atk_desc:#010x}",
            "branches": branch_list, "events": events,
        })
    # move-index slot -> row (first 64 slots annotated; full table stored)
    move_index = bank.move_index
    return {
        "bank": bank_path.name, "bank_type": bank.type_code,
        "move_count": bank.move_count, "moves": moves,
        "move_index": move_index,
    }


CSV_FIELDS = ["row", "stream_frames", "damage", "attack_class", "active_first",
              "active_last", "stance_slot", "heading_change", "step_per_frame",
              "air_first", "air_last", "hold_frame", "hit_freeze", "state_word",
              "attack_word", "flags", "n_branches", "n_events", "inputs"]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, default=Path("movesets"))
    args = ap.parse_args()
    t3 = Path("/home/hatch/workspace/game-reverse-engineering/tekken3")
    exe = EXE_PATH.read_bytes()
    seqs = load_seq_tables(exe)
    print(f"loaded {len(seqs)} motion sequences from USA EXE")
    outdir = t3 / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    common_data = (t3 / "animations" / "divmot99_common.bin").read_bytes()
    common = motion.parse_bank(common_data)
    print(f"common bank: {common.move_count} moves")
    banks = {
        "king": "divmot03_king.bin", "yoshimitsu": "divmot04_yoshimitsu.bin",
        "xiaoyu": "divmot07_xiaoyu.bin", "jin": "divmot09_jin.bin",
        "bryan": "divmot12_bryan.bin", "heihachi": "divmot13_heihachi.bin",
        "gunjack": "divmot16_gunjack.bin",
    }
    summary = []
    for fighter, fname in banks.items():
        ms = extract_bank(t3 / "animations" / fname, exe, seqs, common, common_data)
        # JSON (drop full move_index list into a compact form)
        js = dict(ms)
        js["move_index"] = [r if r < 0x40000000 else f"common:{r - 0x40000000}"
                            for r in ms["move_index"]]
        (outdir / f"moveset_{fighter}.json").write_text(json.dumps(js, indent=1))
        # CSV (frame-data sheet)
        with open(outdir / f"moveset_{fighter}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            for m in ms["moves"]:
                inputs = "; ".join(
                    f"{br['command']}->{br['target_slot']}[{br['first']}-{br['last']}]"
                    for br in m["branches"] if br.get("command") not in ("<end>", None))
                w.writerow({k: m.get(k) for k in CSV_FIELDS
                            if k not in ("n_branches", "n_events", "inputs")} | {
                    "n_branches": len([b for b in m["branches"] if b.get("command") not in ("<end>", None)]),
                    "n_events": len(m["events"]), "inputs": inputs})
        n_attacks = sum(1 for m in ms["moves"] if m["active_first"] or m["active_last"])
        summary.append((fighter, ms["bank_type"], ms["move_count"], n_attacks))
        print(f"{fighter}: {ms['move_count']} moves, {n_attacks} attacks")
    with open(outdir / "MOVESET-SUMMARY.md", "w") as f:
        f.write("# Tekken 3 Moveset Extraction (USA SLUS_004.02)\n\n")
        f.write("Extracted from the 7 motion banks with the verified USA table "
                "addresses. Move names are not stored in the banks (they live in "
                "the ARC move-list text); moves are identified by move-index slot "
                "and row.\n\n")
        f.write("| Fighter | Bank type | Move rows | Attacks (active window) |\n")
        f.write("|---|---|---|---|\n")
        for fighter, bt, mc, na in summary:
            f.write(f"| {fighter} | {bt} | {mc} | {na} |\n")
        f.write("\n## Input encoding\n\nBranch `command` words decode per "
                "n0madic moves.md: bits 0-3 = LP/RP/LK/RK, bit 4 = any, bits 5-13 "
                "= numpad directions; 0xC001 = f,f; 0xC002 = b,b; 0xC00D = no "
                "input; 0xC00E-0xC04C / 0xC7FF-0xC827 = motion sequences from "
                "USA EXE tables 0x800954D0 (63) / 0x800955CC (41).\n")
        f.write("\n## Frame data columns (CSV)\n\n`stream_frames` = total frames; "
                "`active_first`/`active_last` = hit active window; `damage` = "
                "base damage; `hit_freeze` = defender freeze frames; "
                "`step_per_frame` = forward movement/frame; `stance_slot` = "
                "stance after move; `inputs` = branch commands -> target slots "
                "with frame windows.\n")
    print("wrote", outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
