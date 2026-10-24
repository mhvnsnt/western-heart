#!/usr/bin/env python3
"""Build Zui's Steve Fox T7 set + Lei drunken-fist stance system into zui.json.

Owner orders 2026-10-21 ~01:20 CDT:
  "Wire zui models to Steve and his moves add in drunken gist moves and stance
   switch from boxing to drunken fist and Steve's other stances and such"
  "Add drunken fist to him from lei moves and stance switching added on top of
   Steve fix stance switching and boxing etc."

Sources (Tekken / teardown data only):
  * Steve Fox full T7 set: docs/t7t8-reference/frame-data-t7/steve.json
    (t7chicken / TekkenBot-extracted, SOURCE.json in same dir).
  * Lei Wulong drunken fist: the DRU group already imported into
    game/assets/movesets/rave.json from the same T7 frame-data library
    (t7_move_id lei_*), copied verbatim + stance fields added.
  * Existing zui.json entries are NEVER dropped: on a canonical-input
    collision with a Jin T3 proxy entry, the Steve entry takes the canonical
    key (owner order: Zui's moves ARE Steve's) and the proxy entry is kept
    under the repo rekey convention "<input>_r<t3_row>" with its payload
    byte-identical. Collisions between two imported entries keep the first
    canonical and rekey later ones "<input>_r<source row number>".

Conversion conventions mirror the repo's existing T7 imports (rave.json):
  damage  = sum of the first (non-bracket) number of each hit in damage_raw
  startup = speed frames / 60 (3dp)
  limb    = last button in the input (1 armL, 2 armR, 3 legL, 4 legR)
  fields  = t7_source / t7_move_id / t7_command / t7_hit_level /
            t7_damage_raw / t7_startup_frames / t7_on_block / t7_on_hit /
            t7_on_ch / anim_ref "t7:steve:<slug>" / note with frame data.
active / recovery / soulGain / knock / heavy are WH tuning values derived
from the frame data (documented in the moves' notes and the build report);
 frame data itself is never altered.
"""
import json, re, sys, copy
from pathlib import Path

T7_SOURCE = ("t7chicken (dayhaysoos/t7chickenplus-graphql \u2014 "
             "TekkenBot-extracted T7 frame data)")

STANCE_PREFIX = {
    "DCK": "DCK", "EXT": "DCK", "FLK": "FLK", "PAB": "PKB", "PKB": "PKB",
    "SWY": "SWY", "ALB": "ALB", "LWV": "LWV", "RWV": "RWV",
}

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")
    return re.sub(r"_+", "_", s)

def clean_input(notation):
    """Normalize a t7chicken notation to a WH moveset key.

    'DRU 2, 2 (or SS 2, 2)' -> 'DRU 2,2'; 'f+3 (or f+4)' -> 'f+3';
    'Approach enemy... 1+3' -> '1+3'; 'WR f, f, F (Full Screen)' -> 'WR f,f,F'.
    """
    n = str(notation).strip()
    if "..." in n:  # contextual prefix: 'Approach enemy... 1+3'
        n = n.split("...", 1)[1].strip()
    n = n.split(" (or ")[0].strip()
    if " or " in n:  # '1+3 or 2+4' -> first alternative
        n = n.split(" or ")[0].strip()
    n = re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()  # trailing '(Full Screen)'
    n = re.sub(r",\s+", ",", n)
    n = re.sub(r"\s+,", ",", n)
    n = re.sub(r"\s+", " ", n)
    return n

def parse_damage(raw):
    raw = str(raw or "").strip()
    if raw in ("", "-", "none", "None"):
        return 0
    total = 0
    for part in raw.split(","):
        m = re.match(r"\s*(\d+)", part)
        if m:
            total += int(m.group(1))
    return total

def last_button(inp):
    for ch in reversed(inp):
        if ch in "1234":
            return {"1": "armL", "2": "armR", "3": "legL", "4": "legR"}[ch]
    return "armR"

def stance_of(inp):
    m = re.match(r"^([A-Z]{2,4})\s", inp)
    if not m:
        return None
    if m.group(1) == "EXT":  # EXT DCK = Extended Ducking
        return "DCK"
    return STANCE_PREFIX.get(m.group(1))

def convert_steve_row(row):
    raw_notation = str(row.get("notation", "")).strip()
    inp = clean_input(raw_notation)
    dmg = parse_damage(row.get("damage"))
    speed = str(row.get("speed", "-")).strip()
    startup_frames = speed if re.fullmatch(r"\d+", speed) else None
    startup = round(int(speed) / 60, 3) if startup_frames else 0.25
    name = (row.get("move_name") or "").strip() or inp
    hit_level = str(row.get("hit_level", "-"))
    heavy = dmg >= 18
    if dmg == 0:
        move_class = "special"
        active, recovery, knock, soul = 0.3, 0.3, 0.0, 6
    else:
        move_class = ("throw" if "throw" in hit_level.lower()
                      else "string" if "," in inp else "strike")
        active = 0.05
        recovery = 0.7 if heavy else 0.55
        on_hit = str(row.get("on_hit", "-"))
        knock = 5.0 if on_hit in ("KND", "LAUNCH", "STUN") and heavy else \
            4.2 if on_hit in ("KND", "LAUNCH", "STUN") else 2.2
        soul = max(3, min(15, round(dmg * 0.5)))
    mv = {
        "name": name,
        "input": inp,
        "input_slots": [inp],
        "move_class": move_class,
        "anim_ref": "t7:steve:" + slug(name if row.get("move_name") else inp),
        "damage": dmg,
        "startup": startup,
        "active": active,
        "recovery": recovery,
        "limb": last_button(inp),
        "heavy": heavy,
        "knock": knock,
        "soulGain": soul,
        "t7_source": T7_SOURCE,
        "t7_move_id": row.get("id"),
        "t7_command": raw_notation,
        "t7_hit_level": hit_level,
        "t7_damage_raw": str(row.get("damage", "-")),
        "t7_startup_frames": startup_frames if startup_frames else "-",
        "t7_on_block": str(row.get("on_block", "-")),
        "t7_on_hit": str(row.get("on_hit", "-")),
        "t7_on_ch": str(row.get("on_ch", "-")),
        "note": (f"T7 [{hit_level}] on block {row.get('on_block', '-')} / "
                 f"on hit {row.get('on_hit', '-')} / CH {row.get('on_ch', '-')}"),
        "wh_import": "zui-steve-t7-20261021",
    }
    st = stance_of(inp)
    if st:
        mv["stance"] = st
        mv["stance_gate"] = True
    return mv

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    zui_path = root / "game/assets/movesets/zui.json"
    zui = json.loads(zui_path.read_text())
    steve = json.loads((root / "docs/t7t8-reference/frame-data-t7/steve.json").read_text())
    rave = json.loads((root / "game/assets/movesets/rave.json").read_text())

    log = {"steve_added": 0, "steve_skipped": [], "dru_added": 0,
           "jin_rekeyed": [], "import_rekeyed": [], "collisions_kept_first": []}
    moves = zui["moves"]

    def put(mv, rekey_suffix_hint):
        """Insert mv under its canonical input; resolve collisions."""
        inp = mv["input"]
        if inp not in moves:
            moves[inp] = mv
            return inp
        existing = moves[inp]
        # Existing Jin T3 proxy yields the canonical key to a Steve entry
        # (owner order). The proxy payload is preserved verbatim, rekeyed.
        if (mv.get("wh_import") == "zui-steve-t7-20261021"
                and existing.get("t3_source") == "jin"
                and existing.get("t7_move_id") is None):
            row = existing.get("t3_row", "jin")
            new_key = f"{inp}_r{row}"
            while new_key in moves:
                new_key += "x"
            moves[new_key] = existing
            del moves[inp]
            moves[inp] = mv
            log["jin_rekeyed"].append({"from": inp, "to": new_key,
                                        "t3_row": row})
            return inp
        # Import-vs-import (or DRU vs anything): first wins canonical.
        key = f"{inp}_r{rekey_suffix_hint}"
        while key in moves:
            key += "x"
        moves[key] = mv
        log["import_rekeyed"].append({"input": inp, "key": key,
                                       "t7_move_id": mv.get("t7_move_id")})
        return key

    # ---- 1) Steve Fox full T7 set ----
    stance_moves = {}
    steve_keys = {}
    for row in steve["movelist"]:
        raw = str(row.get("notation", ""))
        if clean_input(raw) in ("WALL BOUND", ""):
            log["steve_skipped"].append({"id": row.get("id"), "notation": raw,
                                         "why": "mechanic row, no move input"})
            continue
        mv = convert_steve_row(row)
        # Peekaboo (steve_198) shares f+3+4 with Lei's Drunken Master Walk in
        # the source data. Zui's f+3+4 = Drunken Master Walk (owner order +
        # Zui's canon title); Peekaboo's entry is preserved rekeyed and the
        # stance stays reachable via its ,F transition strings.
        if row.get("id") == "steve_198":
            moves["f+3+4_r198"] = mv
            log["import_rekeyed"].append({"input": "f+3+4",
                                           "key": "f+3+4_r198",
                                           "t7_move_id": "steve_198",
                                           "why": "shares f+3+4 with Drunken Master Walk"})
            key = "f+3+4_r198"
        else:
            key = put(mv, str(row.get("id", "")).replace("steve_", ""))
        steve_keys[row.get("id")] = key
        log["steve_added"] += 1
        st = mv.get("stance")
        if st:
            stance_moves.setdefault(st, []).append(mv["input"])

    # ---- 2) Lei drunken fist (verbatim from rave.json T7 Lei import) ----
    DRU_EXTRA_IDS = {"lei_290", "lei_298", "lei_307", "lei_309", "lei_426"}
    dru_inputs = []
    for key0, entry in rave["moves"].items():
        if not isinstance(entry, dict) or not entry.get("t7_move_id"):
            continue
        inp = str(entry.get("input", ""))
        if not (inp.startswith("DRU") or entry["t7_move_id"] in DRU_EXTRA_IDS):
            continue
        mv = copy.deepcopy(entry)
        mv["stance"] = "DRU"
        mv["stance_gate"] = True
        mv["wh_import"] = "zui-lei-dru-20261021"
        mv["zui_note"] = ("Drunken Fist for Zui, imported verbatim from the "
                          "T7 Lei Wulong set (rave.json); frame data unchanged.")
        k = put(mv, str(entry["t7_move_id"]).replace("lei_", ""))
        dru_inputs.append(mv["input"])
        log["dru_added"] += 1

    # ---- 3) specials (additive, deduped by input) ----
    # strings[] is a curated editor list in this repo (rave.json does not
    # mirror its comma moves there either); the buffer resolves string
    # continuations from the moves dict itself, so strings[] stays untouched.
    have_specials = {s["input"] for s in zui["specials"]}
    for mv in list(moves.values()):
        if not mv.get("wh_import"):
            continue
        inp = mv["input"]
        if " (" in inp or inp.startswith("WR ") or re.search(r",[BF]$", inp):
            continue  # not a buffer-parseable notation
        is_motion = any(t in inp for t in ("qcf", "qcb", "hcf", "hcb", "f,f", "b,b"))
        is_stance_entry = inp in ("f+3+4", "b+3+4")
        if (is_motion or is_stance_entry) and inp not in have_specials:
            zui["specials"].append({
                "input": inp, "t7_move_id": mv.get("t7_move_id"),
                "damage": mv["damage"], "throw": mv["move_class"] == "throw",
                **({"stance": mv["stance"]} if mv.get("stance") else {}),
                **({"stance_entry": True} if is_stance_entry else {}),
            })
            have_specials.add(inp)

    # ---- 4) stance system block ----
    def grp(prefix_list):
        out = []
        for mv in moves.values():
            if mv.get("stance") in prefix_list and mv["input"] not in out:
                out.append(mv["input"])
        return out
    zui["stances"] = {
        "system": ("Stance data v1 (owner order 2026-10-21). Stances are "
                   "moveset-data groups: entry moves resolve through the "
                   "input buffer (specials / directionals); gated moves "
                   "carry stance + stance_gate and resolve by their exact "
                   "Tekken notation (getMove / tryAttack / editor preview). "
                   "The fighter state machine has no stance flag yet \u2014 "
                   "the gate is data-level, recorded honestly in "
                   "docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md."),
        "default": "BOX",
        "list": {
            "BOX": {"name": "Boxing \u2014 Steve Fox base stance",
                    "entry": None, "exit": None,
                    "note": "All non-stance-gated Steve T7 moves."},
            "DCK": {"name": "Ducking", "source": "Steve Fox T7",
                    "entry": "f+3", "entry_ids": ["steve_113"],
                    "note": "EXT DCK (Extended Ducking) rows included.",
                    "moves": grp(["DCK"])},
            "LWV": {"name": "Left Weave", "source": "Steve Fox T7",
                    "entry": "3 (from Ducking)", "entry_ids": ["steve_135"],
                    "moves": grp(["LWV"])},
            "RWV": {"name": "Right Weave", "source": "Steve Fox T7",
                    "entry": "4 (from Ducking)", "entry_ids": ["steve_136"],
                    "moves": grp(["RWV"])},
            "FLK": {"name": "Flicker Stance", "source": "Steve Fox T7",
                    "entry": "b+3+4", "entry_ids": ["steve_164"],
                    "note": "Also entered from the many ',B' transition strings in the set.",
                    "moves": grp(["FLK"])},
            "PKB": {"name": "Peekaboo", "source": "Steve Fox T7 (PAB rows)",
                    "entry": "f+3+4",
                    "entry_note": ("f+3+4 is shared with Drunken Master Walk "
                                   "in the source data; on Zui it fires "
                                   "Drunken Master Walk. Peekaboo's own "
                                   "entry row is preserved as f+3+4_r198 "
                                   "(steve_198) and its ',F' transition "
                                   "strings enter Peekaboo in play."),
                    "moves": grp(["PKB"])},
            "SWY": {"name": "Swaying", "source": "Steve Fox T7",
                    "entry": "b+3", "entry_ids": ["steve_195"],
                    "moves": grp(["SWY"])},
            "ALB": {"name": "Albatross (spin)", "source": "Steve Fox T7",
                    "entry": "3+4", "entry_ids": ["steve_251"],
                    "moves": grp(["ALB"])},
            "DRU": {"name": "Drunken Fist \u2014 Drunken Master",
                    "source": "Lei Wulong T7 (via rave.json T7 import)",
                    "entry": "f+3+4", "entry_ids": ["lei_290"],
                    "exit": "DRU b",
                    "note": ("Zui's signature stance (canon title: Drunken "
                             "Master; Attire 1: Drunken Monk). Entered from "
                             "boxing with f+3+4 (Drunken Master Walk); "
                             "DRU f / DRU b / DRU f,b are its in-stance "
                             "movement; DRU 1+2 (Tiger Sip) sustains it."),
                    "moves": sorted(set(dru_inputs))},
        },
    }

    # ---- 5) provenance / bookkeeping ----
    zui["t7_base"] = "steve"
    zui["t7_dataset"] = ("t7chicken (dayhaysoos/t7chickenplus-graphql \u2014 "
                         "TekkenBot-extracted T7 frame data)")
    zui["t7_import_note"] = (
        "Full T7 Steve Fox movelist imported 2026-10-21 (owner order: wire "
        "Zui to Steve and his moves) from docs/t7t8-reference/frame-data-t7/"
        "steve.json. Pre-existing Jin T3 proxy entries preserved verbatim; "
        "where a Steve move takes a contested canonical input, the proxy "
        "entry is rekeyed '<input>_r<t3_row>'. Lei drunken-fist group "
        "imported verbatim from rave.json's T7 Lei set.")
    zui["stance_expansion_20261021"] = {
        "date": "2026-10-21",
        "owner_order": "Wire Zui to Steve + Lei drunken fist + stance switching",
        **log,
        "total_moves": len(moves),
    }
    zui_path.write_text(json.dumps(zui, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({**log, "total_moves": len(moves)}, indent=1))

if __name__ == "__main__":
    main()
