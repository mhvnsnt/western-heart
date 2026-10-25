#!/usr/bin/env python3
"""Decode Tekken 3 hit reactions and throws -> game/assets/anim/t3/reactions.json (lane E, 2026-10-24).

Source priority (owner law 2026-10-23): T5/T6/T7/T8/TTT2 first. No reaction or throw data from any of them is
decoded in the repo (teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md: T7 fighter animation 0/51; T6 DATA401 still
encrypted; T5 TK5DATA2 motions only named, not extracted; TTT2 not extracted; T8 models/UI only), so this is the
logged T3 fallback (docs/anim/PROCEDURAL_AUDIT.md). Nothing here is authored: every number is read from the
owner's disc (USA EXE SLUS_004.02 and the divmot banks), with SHA-256.

What the game does (n0madic/Tekken3Remake docs/research/code/combat.md "Reactions", "Launches and juggles",
"Throws"; formats/divmot-banks.md; ports in tools/research/fight_sim.py and remake core/fighter/move_system.gd):
  * an attacking move row's +0x32 (u16) is the defender's reaction: < 0x1000 indexes g_reactionRecords
    (EXE 0x80010CE8, 633 records x 21 s16); 0x1nnn is entry nnn of g_throwVictimSlots (0x800174C4), the
    victim move of a throw; +0x34 indexes g_closeReactions (0x800177DC, s16 reaction, s16 distance).
  * HitSelectReaction picks guard -> airborne (g_airKinds 0x8001A630) -> down -> counter hit -> facing quadrant.
  * a throw is a branch row with transition 0x21; the thrower's throw move's +0x32 gives the victim slot.
  * slots resolve in the DEFENDER's move index first; a slot it lacks is filled from the opponent's bank
    (DivmotMergeSharedSlots), which is how throw-victim moves and attacker-specific staggers reach the victim.

Addresses: the research tree is Japan Rev.1. The USA EXE's 0x80010000-0x8002172C image range is byte-identical
in place (remake_import/layouts/usa.json segment [0, 71469, 0]; teardown/tekken3/tools/local/usa_tables.py "the
0x8001xxxx region did NOT shift"), and every table used here lies inside it. The decode is verified below.

Usage (T3REMAKE_RESEARCH = n0madic/Tekken3Remake tools/research, as for lab/tools/t3_motion_bake.py):
  python3 tools/anim/t3_reaction_tables.py            # write reactions.json (coverage read from the packs)
  python3 tools/anim/t3_reaction_tables.py --check    # decode + verify only, write nothing
Bake the clips with tools/anim/t3_reaction_bake.py, then re-run this to refresh the coverage numbers.
"""
import argparse
import hashlib
import json
import os
import struct
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T3 = REPO / "teardown/tekken3"
EXE_PATH = T3 / "disc/files/TEKKEN3/SLUS_004.02"
ANIM = T3 / "animations"
OUT = REPO / "game/assets/anim/t3/reactions.json"
RESEARCH = os.environ.get("T3REMAKE_RESEARCH", "/workspace/t3anim/t3r/tools/research")

EXE_BASE, EXE_HEADER = 0x80010000, 0x800
REACTIONS, REACTION_COUNT, REACTION_WORDS = 0x80010CE8, 633, 21
FORCED_REACTION = 0x8001DEC0          # record of a body thrown into a fighter (Tekken Force)
THROW_VICTIM_SLOTS, THROW_VICTIM_COUNT = 0x800174C4, 397 + 21   # remake_import/tables.py: entries + a record's reach
CLOSE_REACTIONS, CLOSE_REACTION_COUNT = 0x800177DC, 58
AIR_KINDS, AIR_KIND_COUNT = 0x8001A630, 6
PUSH_TABLES, PUSH_ENTRIES = 0x8001075C, 700 + 10
LAUNCH_PUSH = 0x80019D2C
MOVE_SLOTS, EMPTY, COMMON = 4023, 0x3FFFFFFF, 0x40000000
COMMON_BRANCHES, COMMON_BRANCH_COUNT = 0x80017C78, 672   # remake_import/tables.py
END, CALL, RETURN = 0xC000, 0xC00C, 0xC00D               # fight_sim.py branch_find
BREAK_INPUT = {0x3A: "1", 0x3B: "2", 0x3C: "1+2"}          # moves.md branch conditions 0x3A-0x3C
STAND_SLOT, CROUCH_SLOT, COLLAPSE_SLOT, MERGE_FALLBACK_SLOT = 3, 40, 0xD66, 0xDC5
RECORD_FIELDS = ["front", "front_crouch", "counter", "counter_crouch", "side1", "side1_crouch", "side3",
                 "side3_crouch", "back", "back_crouch", "guard", "guard_crouch", "down", "down_other",
                 "push_angle", "push_hit", "unused_angle", "push_counter", "push_angle_down", "push_down", "push_guard"]
TRANSITIONS = {"throw": 0x21, "thrown": 0x22, "guard": 0x23, "air": 0x24, "down": 0x25, "counter": 0x26,
               "side1": 0x27, "side3": 0x28, "front": 0x2A, "back": 0x2B, "launch": 0x1E}
# combat.md "Launches and juggles": the documented g_airKinds rows (ground offset, air move slot).
DOC_AIR_KINDS = [[440, 0xD56], [550, 0xD61], [204, 0xD62], [436, 0xD63], [436, 0xD64], [1357, 0xD57]]

# Every runtime bank folder (game/assets/anim/t3/<dir>) -> its divmot motion bank.
BANK_DIRS = {
    "anna": "divmot17_anna", "armorking": "divmot03_king", "bosconovitch": "divmot18_bosconovitch",
    "bryan": "divmot12_bryan", "eddy": "divmot08_eddy", "forestlaw_on_law": "divmot20_forestlaw",
    "gon": "divmot19_gon", "gunjack": "divmot16_gunjack", "heihachi": "divmot13_heihachi",
    "heihachi_on_jin": "divmot13_heihachi", "hwoarang": "divmot06_hwoarang", "jin": "divmot09_jin",
    "julia": "divmot10_julia", "king_on_pantera_leoman": "divmot03_king", "kuma": "divmot11_kuma",
    "law": "divmot01_law", "lei": "divmot02_lei", "nina": "divmot05_nina", "ogre": "divmot14_ogre",
    "paul": "divmot00_paul", "xiaoyu": "divmot07_xiaoyu", "yoshimitsu": "divmot04_yoshimitsu",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- EXE tables

class Exe:
    def __init__(self, path=EXE_PATH):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        load = struct.unpack_from("<I", self.data, 0x18)[0]
        if self.data[:8] != b"PS-X EXE" or load != EXE_BASE:
            sys.exit(f"{path}: not the T3 PS-X EXE loading at {EXE_BASE:#x}")

    def s16(self, addr, n):
        return list(struct.unpack_from(f"<{n}h", self.data, addr - EXE_BASE + EXE_HEADER))


def exe_tables(exe):
    return {
        "records": [exe.s16(REACTIONS + 2 * REACTION_WORDS * i, REACTION_WORDS) for i in range(REACTION_COUNT)],
        "forced_record": exe.s16(FORCED_REACTION, REACTION_WORDS),
        "throw_victim_slots": exe.s16(THROW_VICTIM_SLOTS, THROW_VICTIM_COUNT),
        "close_reactions": [exe.s16(CLOSE_REACTIONS + 4 * i, 2) for i in range(CLOSE_REACTION_COUNT)],
        "air_kinds": [exe.s16(AIR_KINDS + 4 * i, 2) for i in range(AIR_KIND_COUNT)],
        "push_tables": exe.s16(PUSH_TABLES, PUSH_ENTRIES),
        "launch_push": exe.s16(LAUNCH_PUSH, 8),
    }


# ---------------------------------------------------------------- motion banks (divmot-banks.md)

class Bank:
    def __init__(self, path):
        self.path = Path(path)
        d = self.data = self.path.read_bytes()
        if d[0] != 0:
            raise ValueError(f"{path}: not a divmot bank")
        self.type = d[1]
        self.n = struct.unpack_from("<H", d, 2)[0]
        self.b = list(struct.unpack_from("<15I", d, 4))
        if self.b[0] != 0x40 or self.b[14] != len(d):
            raise ValueError(f"{path}: section directory does not cover the file")
        has_index = self.b[3] - self.b[2] >= 4 * MOVE_SLOTS
        self.move_index = list(struct.unpack_from(f"<{MOVE_SLOTS}I", d, self.b[2])) if has_index else []

    def row(self, i):
        d, o = self.data, self.b[1] + 56 * i
        w = struct.unpack_from("<IIHBBIHhHhBBBBIIIIBBBBHHHH", d, o)
        return {"anim": w[0], "state": w[1], "attack": w[2], "branches": w[5], "stance": w[6], "end_turn": w[7],
                "damage": w[8] & 0x3FFF, "attack_class": w[8] >> 14, "air": [w[11], w[12]], "hold": w[13],
                "sound": w[14], "events": w[15], "flags": w[16], "attack_desc": w[17], "hit_freeze": w[18],
                "active": [w[19], w[20]], "spheres": w[22], "reaction": w[23], "close": w[24]}

    common_rows = []   # EXE 0x80017C78 rows (load_banks); command 0xC00C calls one, 0xC00D returns

    def branch_list(self, i):
        """The move's branch rows in BranchFind order, with CALL (0xC00C) expanded into the EXE common rows
        up to their RETURN (0xC00D), as fight_sim.branch_find walks them."""
        out, k = [], self.row(i)["branches"]
        while True:
            cmd, res, cond, par, tgt, fl, f0, f1, ent = struct.unpack_from("<HBBHHBBBB", self.data, self.b[0] + 12 * k)
            if cmd == CALL:
                c = tgt
                while self.common_rows[c]["cmd"] != RETURN:
                    out.append(dict(self.common_rows[c], common_row=c))
                    c += 1
            else:
                out.append({"cmd": cmd, "res": res, "cond": cond, "param": par, "target": tgt, "flags": fl,
                            "first": f0, "last": f1, "entry": ent})
            if cmd == 0xC000:
                return out
            k += 1

    def events(self, i):
        idx = self.row(i)["events"]
        if idx == 0xFFFFFFFF:
            return []
        out, o = [], self.b[4] + 4 * idx
        while True:
            frame, cmd = struct.unpack_from("<HH", self.data, o)
            if frame == 0:
                return out
            out.append((frame, cmd))
            o += 4

    def frames(self, anim_word, common):
        bank = common if anim_word >= COMMON else self
        return bank.data[bank.b[6] + (anim_word % COMMON)]   # stream's first byte = frame count (written at load)


def exe_branch_rows(exe):
    out = []
    for i in range(COMMON_BRANCH_COUNT):
        cmd, res, cond, par, tgt, fl, f0, f1, ent = struct.unpack_from(
            "<HBBHHBBBB", exe.data, COMMON_BRANCHES - EXE_BASE + EXE_HEADER + 12 * i)
        out.append({"cmd": cmd, "res": res, "cond": cond, "param": par, "target": tgt, "flags": fl,
                    "first": f0, "last": f1, "entry": ent})
    return out


def load_banks(exe=None):
    Bank.common_rows = exe_branch_rows(exe or Exe())
    common = Bank(ANIM / "divmot99_common.bin")
    banks = {stem: Bank(ANIM / f"{stem}.bin") for stem in sorted(set(BANK_DIRS.values()))}
    return banks, common


def resolve(bank, common, slot):
    """(bank object, row, 'own'|'common') of a slot this bank defines, else None (MoveLookup)."""
    if slot < 0 or slot >= MOVE_SLOTS:
        return None
    v = bank.move_index[slot]
    if v == EMPTY:
        return None
    return (common, v - COMMON, "common") if v >= COMMON else (bank, v, "own")


def restriction_ok(res, bank_type):
    """Branch restriction byte +0x02 (divmot-banks.md): False only when it can never match this bank."""
    if 1 <= res <= 0x17:
        return bank_type == res - 1
    if 0x18 <= res <= 0x2E:
        return bank_type != res - 0x18
    return True   # 0 = none; opponent-bank and character-id restrictions depend on the match


def restriction_text(res):
    if res == 0:
        return None
    if res <= 0x17:
        return f"own bank {res - 1}"
    if res <= 0x2E:
        return f"own bank != {res - 0x18}"
    if res <= 0x45:
        return f"opponent bank {res - 0x2F}"
    if res <= 0x5C:
        return f"own character {res - 0x46}"
    return f"own character != {res - 0x5D}"


def cond_kind(cond):
    if cond == 0:
        return "always"
    if 2 <= cond <= 0x17:
        return "situation"        # SituationClassify front/side/back x standing/crouching/down + distance
    if cond >= 0x45:
        return "reversal"         # BranchFindReversal (parry / reversal throws)
    if cond in BREAK_INPUT:
        return "break"            # throw escape: tap LP / RP / both (LatchButtonTaps), a 0x21 counter-pair
    return "condition"


def command_texter(exe):
    sys.modules.setdefault("motion", types.ModuleType("motion"))   # command text needs no motion parser
    sys.path.insert(0, str(T3 / "tools/local"))
    import moveset_extract as ME   # noqa: E402
    seqs = ME.load_seq_tables(exe.data)
    return lambda cmd: ME.command_text(cmd, seqs)


# ---------------------------------------------------------------- per-bank decode

def reaction_kind(value, tables):
    if value == 0:
        return None
    if value & 0xF000:
        return {"throw_victim_index": value & 0xFFF, "victim_slot": tables["throw_victim_slots"][value & 0xFFF] & 0xFFFF}
    return {"record": value}


def bank_moves(bank, common):
    """(row bank, row, label) of every move the bank can run: all own rows, plus the divmot99 rows its move
    index names (a bank's moveset is both)."""
    out = [(bank, i, i) for i in range(bank.n)]
    seen = set()
    for v in bank.move_index:
        if v != EMPTY and v >= COMMON and v - COMMON not in seen:
            seen.add(v - COMMON)
    out += [(common, r, f"common:{r}") for r in sorted(seen)]
    return out


def row_label(hit):
    return hit[1] if hit[2] == "own" else f"common:{hit[1]}"


def bank_rows(bank, tables):
    """row -> [reaction +0x32, close +0x34, attack class] for every row with a reaction or close entry."""
    out = {}
    for i in range(bank.n):
        r = bank.row(i)
        if r["reaction"] or r["close"]:
            out[str(i)] = [r["reaction"], r["close"], r["attack_class"]]
    return out


def first_slot_of(bank):
    slot_of = {}
    for s, v in enumerate(bank.move_index):
        if v != EMPTY:
            slot_of.setdefault(v, s)
    return slot_of


def throw_branch(b, cmd_text, slot_of, label, src_row, rb):
    key = (src_row + COMMON) if rb is not None and rb.type == 99 else src_row
    return {"from_row": label, "from_slot": slot_of.get(key), "command": cmd_text(b["cmd"]), "cond": b["cond"],
            "cond_kind": cond_kind(b["cond"]), "param": b["param"], "restriction": restriction_text(b["res"]),
            "window": [b["first"], b["last"]], "entry": b["entry"], "throw_slot": b["target"]}


def bank_throws(bank, common, tables, cmd_text):
    """Every transition-0x21 branch of the bank's moves -> the throw moves (thrower clip), their victim slots,
    damage frame and breaks; plus each throw attempt's 0x21 rows in BranchFind order."""
    slot_of = first_slot_of(bank)
    throws, attempts = {}, {}
    for rb, row, label in bank_moves(bank, common):
        rows = [b for b in rb.branch_list(row) if b["flags"] & 0x3F == 0x21 and restriction_ok(b["res"], bank.type)]
        if not rows:
            continue
        src = rb.row(row)
        entries = [throw_branch(b, cmd_text, slot_of, label, row, rb) for b in rows]
        for e in entries:
            throws.setdefault(e["throw_slot"], {"slot": e["throw_slot"], "via": []})["via"].append(
                {k: v for k, v in e.items() if k != "throw_slot"})
        if any(e["cond_kind"] == "situation" for e in entries):
            attempts[label] = {"slot": entries[0]["from_slot"], "attack": f"{src['attack']:#x}",
                               "attack_class": src["attack_class"], "branches": entries}
    out = []
    for slot in sorted(throws):
        t = throws[slot]
        hit = resolve(bank, common, slot)
        if hit is None:
            t.update(defined=False, note="throw slot empty in this bank: DivmotMergeSharedSlots fills it from the "
                                         "opponent's bank, so the thrower plays the opponent's row for this slot "
                                         "(and that row's victim move)")
            out.append(t)
            continue
        rb, row, src = hit
        r = rb.row(row)
        ev = rb.events(row)
        dmg = r["damage"] + sum(c & 0xFF for _, c in ev if c >> 8 == 0x0B)
        v = r["reaction"]
        victim = (tables["throw_victim_slots"][v & 0xFFF] & 0xFFFF) if v & 0xF000 else (
            tables["records"][v][0] & 0xFFFF if v else None)
        t.update(defined=True, row=row_label(hit), src=src, frames=rb.frames(r["anim"], common),
                 state=f"{r['state']:#x}", attack=f"{r['attack']:#x}", damage=dmg,
                 damage_frames=[f for f, c in ev if c >> 8 == 0x0B], victim_value=v, victim_slot=victim,
                 next=rb.branch_list(row)[-1]["target"])
        if not v:
            t["victim_note"] = ("+0x32 is 0: ThrowVictimStart reads record 0, whose first word is slot 0 (the "
                                "round-start stance, the bank's t3_stance clip); no victim move of its own")
        vh = resolve(bank, common, victim) if victim is not None else None
        t["victim_in_thrower_bank"] = bool(vh)
        if vh:
            vr = vh[0].row(vh[1])
            t["victim_frames"] = vh[0].frames(vr["anim"], common)
            t["victim_events"] = [[f, f"{c:#06x}"] for f, c in vh[0].events(vh[1])]
            t["breaks"] = [{"input": BREAK_INPUT[b["cond"]], "window": [b["first"], b["last"]],
                            "escape_slot": b["target"]}
                           for b in vh[0].branch_list(vh[1])
                           if b["flags"] & 0x3F == 0x21 and b["cond"] in BREAK_INPUT]
        out.append(t)
    return out, attempts


def standard_throw_inputs(bank, common, cmd_text):
    """Stance commands (standing slot 3, crouching slot 40) that start a throw attempt: a move whose branch
    list holds transition-0x21 rows (the standard throws are attack 0x412, class 1, zero damage)."""
    out, seen = [], set()
    for stance in (STAND_SLOT, CROUCH_SLOT):
        hit = resolve(bank, common, stance)
        if not hit:
            continue
        rb, row, _ = hit
        for b in rb.branch_list(row):
            if b["cmd"] == END or not restriction_ok(b["res"], bank.type):
                continue
            tgt = resolve(bank, common, b["target"])
            if not tgt or not any(x["flags"] & 0x3F == 0x21 for x in tgt[0].branch_list(tgt[1])):
                continue
            key = (stance, b["cmd"], b["cond"], b["param"], b["target"])
            if key in seen:
                continue
            seen.add(key)
            r = tgt[0].row(tgt[1])
            out.append({"stance_slot": stance, "command": cmd_text(b["cmd"]), "cond": b["cond"],
                        "param": b["param"], "attempt_slot": b["target"],
                        "attempt_row": tgt[1] if tgt[2] == "own" else f"common:{tgt[1]}",
                        "attempt_attack": f"{r['attack']:#x}", "window": [b["first"], b["last"]]})
    return out


# ---------------------------------------------------------------- what each bank's reactions pack must hold

def global_sets(banks, common, tables):
    """Union over every bank of the reaction slots their rows can make a defender play."""
    recs, victims, escapes = set(), set(), set()
    moves = {(id(rb), row): (rb, row) for bank in banks.values() for rb, row, _ in bank_moves(bank, common)}
    for rb, row in moves.values():
        for b in rb.branch_list(row):
            if b["flags"] & 0x3F == 0x21 and b["cond"] in BREAK_INPUT:
                escapes.add(b["target"])
        if True:
            r = rb.row(row)
            vals = [r["reaction"]]
            if r["close"]:
                vals.append(tables["close_reactions"][r["close"]][0] & 0xFFFF)
            for v in vals:
                if v & 0xF000:
                    victims.add(tables["throw_victim_slots"][v & 0xFFF] & 0xFFFF)
                elif v:
                    recs.add(v)
    hit = {}
    for rec in sorted(recs) + ["forced"]:
        words = tables["forced_record"] if rec == "forced" else tables["records"][rec]
        for k in range(14):
            if words[k]:
                hit.setdefault(words[k] & 0xFFFF, set()).add("guard" if k in (10, 11) else "hit")
    air = {s & 0xFFFF: {"air"} for _, s in tables["air_kinds"]}
    air.setdefault(COLLAPSE_SLOT, set()).add("collapse")
    return recs, hit, air, victims, escapes


def wanted_slots(bank, common, tables, gsets, throws):
    """slot -> roles for every slot this bank's reactions pack must hold: the bank defines it (own or common
    row) and some bank's attack, throw, air kind, KO or continuation can start it on a fighter using this bank."""
    _, hit, air, victims, escapes = gsets
    want = {}
    for src in (hit, air):
        for s, roles in src.items():
            if resolve(bank, common, s):
                want.setdefault(s, set()).update(roles)
    for s in victims:
        if resolve(bank, common, s):
            want.setdefault(s, set()).add("victim")
    for s in escapes:
        if resolve(bank, common, s):
            want.setdefault(s, set()).add("escape")
    for t in throws:
        if t.get("defined"):
            want.setdefault(t["slot"], set()).add("throw")
    # continuation closure: default continuation (<end> row target) until a stance slot
    frontier = list(want)
    while frontier:
        s = frontier.pop()
        rb, row, _ = resolve(bank, common, s)
        for b in rb.branch_list(row):
            if b["cmd"] != END:
                continue
            t = b["target"]
            if t in (STAND_SLOT, CROUCH_SLOT) or t in want or not resolve(bank, common, t):
                continue
            want[t] = {"chain"}
            frontier.append(t)
    return want


def slot_meta(bank, common, slot):
    rb, row, src = resolve(bank, common, slot)
    r = rb.row(row)
    br = rb.branch_list(row)
    launch = [b["entry"] for b in br if b["flags"] & 0x3F == 0x1E]
    meta = {"row": row if src == "own" else f"common:{row}", "src": src, "frames": rb.frames(r["anim"], common),
            "state": f"{r['state']:#x}", "next": br[-1]["target"]}
    if r["air"] != [0, 0]:
        meta["air"] = r["air"]
    if r["hold"]:
        meta["hold"] = r["hold"]
    if launch:
        meta["launch_entry"] = launch[0]
    return meta


# ---------------------------------------------------------------- verification

def verify(exe, tables, banks, common):
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    check("g_airKinds 0x8001A630 equals combat.md's air-kind table", tables["air_kinds"] == DOC_AIR_KINDS,
          f"{tables['air_kinds']}")
    nz = sum(1 for r in tables["records"] if r[16])
    check("168 of 633 records have a non-zero +0x20 angle (combat.md)", nz == 168, f"{nz}")
    mp = max(max(r[15], r[17], r[19], r[20]) for r in tables["records"])
    check("highest push-table index the records use is 700 (remake_import PUSH_ENTRIES = 700 + 10)", mp == 700, f"{mp}")
    check("record 0 is all zero", not any(tables["records"][0]), "")
    max_tv = max_close = 0
    for b in banks.values():
        for i in range(b.n):
            r = b.row(i)
            if r["reaction"] & 0xF000:
                max_tv = max(max_tv, r["reaction"] & 0xFFF)
            max_close = max(max_close, r["close"])
    check("throw-victim indexes stay inside the 397 entries (remake_import THROW_VICTIM_COUNT)", max_tv < 397, f"max {max_tv}")
    check("close-reaction indexes stay inside the 58 entries", max_close < CLOSE_REACTION_COUNT, f"max {max_close}")
    # The research port's own address arithmetic (fight_sim._reaction_from) on a RAM image of this EXE.
    try:
        sys.path.insert(0, RESEARCH)
        import fight_sim   # noqa: E402
        ram = fight_sim.Ram(bytearray(fight_sim.RAM_SIZE))
        img = exe.data[EXE_HEADER:]
        ram.data[EXE_BASE & 0x1FFFFFFF:(EXE_BASE & 0x1FFFFFFF) + len(img)] = img
        bad = n = 0
        for b in banks.values():
            for i in range(b.n):
                v = b.row(i)["reaction"]
                if not v:
                    continue
                addr = fight_sim._reaction_from(ram, v)
                words = [ram.s16(addr + 2 * k) for k in range(REACTION_WORDS)]
                mine = tables["records"][v] if not v & 0xF000 else tables["throw_victim_slots"][(v & 0xFFF):(v & 0xFFF) + 21]
                n += 1
                bad += words != list(mine)
        check("fight_sim._reaction_from (research port) reads the same record / victim entry for every bank row",
              bad == 0 and n > 0, f"{n} rows, {bad} mismatches")
    except Exception as e:   # noqa: BLE001
        check("fight_sim._reaction_from cross-check", False, f"research tree not importable: {e}")
    # Independent extractor: teardown/tekken3/tools/local/moveset_extract.py output.
    bad = n = 0
    for stem, b in banks.items():
        p = T3 / "movesets" / f"moveset_{stem.split('_', 1)[1]}.json"
        if not p.exists():
            continue
        for m in json.loads(p.read_text())["moves"]:
            r = b.row(m["row"])
            n += 1
            bad += (m["reaction"], m["close_reaction"], m["attack_class"]) != (r["reaction"], r["close"], r["attack_class"])
    check("+0x32 / +0x34 / attack class equal teardown/tekken3/movesets/moveset_*.json (moveset_extract.py)",
          bad == 0 and n > 0, f"{n} rows, {bad} mismatches")
    # Every slot a bank's own attacks' records name is defined in that bank (own or common row): an attacker
    # always brings the rows its reactions need, so DivmotMergeSharedSlots never leaves a reaction empty.
    undefined = 0
    for b in banks.values():
        for rb, row, _ in bank_moves(b, common):
            r = rb.row(row)
            for v in (r["reaction"], tables["close_reactions"][r["close"]][0] & 0xFFFF if r["close"] else 0):
                if v and not v & 0xF000:
                    undefined += sum(1 for k in range(14) if tables["records"][v][k]
                                     and not resolve(b, common, tables["records"][v][k] & 0xFFFF))
    check("every reaction slot named by the records of a bank's moves (own + divmot99 rows) is defined by that bank",
          undefined == 0, f"{undefined} undefined")
    return checks


# ---------------------------------------------------------------- coverage from the baked packs

def coverage(dirs_info):
    cov = {}
    for d, info in dirs_info.items():
        p = REPO / "game/assets/anim/t3" / d / "reactions.pack.json"
        want = info["slots"]
        if not p.exists():
            cov[d] = {"pack": None, "wanted": len(want), "baked": 0, "missing": len(want), "throws": 0,
                      "throws_with_thrower_clip": 0}
            continue
        pk = json.loads(p.read_text())
        rows, miss = pk.get("rows", {}), pk.get("missing", {})
        roles = {}
        for key, m in want.items():
            for role in m["roles"]:
                c = roles.setdefault(role, [0, 0])
                c[0 if key in rows else 1] += 1
        thr = [t for t in info["throws"] if t.get("defined")]
        cov[d] = {"pack": str(p.relative_to(REPO)), "pack_sha256": sha(p), "wanted": len(want),
                  "baked": sum(1 for k in want if k in rows), "missing": sum(1 for k in want if k in miss),
                  "unaccounted": sorted(k for k in want if k not in rows and k not in miss),
                  "by_role_baked_missing": roles,
                  "throws": len(thr),
                  "throws_with_thrower_clip": sum(1 for t in thr if f"{t['slot']:#x}" in rows),
                  "throws_with_victim_clip_here": sum(1 for t in thr if t.get("victim_slot") is not None
                                                      and f"{t['victim_slot']:#x}" in rows)}
    return cov


def build(check_only=False):
    exe = Exe()
    tables = exe_tables(exe)
    banks, common = load_banks(exe)
    checks = verify(exe, tables, banks, common)
    for c in checks:
        print(("PASS " if c["pass"] else "FAIL ") + c["check"] + (f" [{c['detail']}]" if c["detail"] else ""))
    if not all(c["pass"] for c in checks):
        sys.exit("verification failed: reactions.json not written")
    if check_only:
        return None
    cmd_text = command_texter(exe)
    gsets = global_sets(banks, common, tables)
    dirs_info, by_stem = {}, {}
    for d, stem in BANK_DIRS.items():
        b = banks[stem]
        if stem not in by_stem:
            throws, attempts = bank_throws(b, common, tables, cmd_text)
            want = wanted_slots(b, common, tables, gsets, throws)
            slots = {f"{s:#x}": dict(slot_meta(b, common, s), roles=sorted(r)) for s, r in sorted(want.items())}
            by_stem[stem] = {"divmot": str(b.path.relative_to(REPO)), "divmot_sha256": sha(b.path), "bank_type": b.type,
                             "rows": bank_rows(b, tables), "throws": throws, "throw_attempts": attempts,
                             "throw_inputs": standard_throw_inputs(b, common, cmd_text), "slots": slots}
        dirs_info[d] = by_stem[stem]
    doc = {
        "format": "wh-t3-reactions/1",
        "tool": "tools/anim/t3_reaction_tables.py (+ tools/anim/t3_reaction_bake.py for the clips)",
        "contract": "docs/anim/T3-REACTIONS.md",
        "source_priority": "T3 fallback logged in docs/anim/PROCEDURAL_AUDIT.md: no T5/T6/T7/T8/TTT2 reaction or throw "
                           "data is decoded in the repo (teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md, T7 0/51).",
        "hand_keyed": False,
        "exe": str(EXE_PATH.relative_to(REPO)), "exe_sha256": sha(EXE_PATH),
        "common_bank": str(common.path.relative_to(REPO)), "common_bank_sha256": sha(common.path),
        "addresses": {"g_reactionRecords": f"{REACTIONS:#x}", "g_throwVictimSlots": f"{THROW_VICTIM_SLOTS:#x}",
                      "g_closeReactions": f"{CLOSE_REACTIONS:#x}", "g_airKinds": f"{AIR_KINDS:#x}",
                      "g_pushTables": f"{PUSH_TABLES:#x}", "launch_push": f"{LAUNCH_PUSH:#x}",
                      "forced_record": f"{FORCED_REACTION:#x}",
                      "note": "Japan Rev.1 addresses; identical in the USA EXE (0x8001xxxx image range unshifted)"},
        "verification": checks,
        "record_fields": RECORD_FIELDS,
        "transitions": TRANSITIONS,
        "stance_slots": {"standing": STAND_SLOT, "crouching": CROUCH_SLOT},
        "collapse_slot": COLLAPSE_SLOT,
        "merge_fallback_slot": {"slot": MERGE_FALLBACK_SLOT, "note": "DivmotMergeSharedSlots fills a slot empty in "
                                "both banks from this slot; it is empty in every bank, and no reaction a bank's "
                                "own records name is empty (verification), so it never applies here"},
        **tables,
        "common_rows": bank_rows(common, tables),
        "banks": {},
        "coverage": {},
    }
    for d, info in dirs_info.items():
        doc["banks"][d] = info
    doc["coverage"] = coverage(dirs_info)
    OUT.write_text(json.dumps(doc, separators=(",", ":")))
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size / 1e6:.2f} MB)")
    for d, c in doc["coverage"].items():
        print(f"  {d}: {c['baked']}/{c['wanted']} baked, {c['missing']} missing, throws {c['throws']} "
              f"(thrower clip {c['throws_with_thrower_clip']})")
    return doc


def bank_plan(d):
    """Slots (int) -> roles for one bank folder; used by tools/anim/t3_reaction_bake.py."""
    exe = Exe()
    tables = exe_tables(exe)
    banks, common = load_banks(exe)
    b = banks[BANK_DIRS[d]]
    throws, _ = bank_throws(b, common, tables, lambda c: f"{c:#06x}")
    want = wanted_slots(b, common, tables, global_sets(banks, common, tables), throws)
    return b, common, want


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="decode and verify only; write nothing")
    build(ap.parse_args().check)
