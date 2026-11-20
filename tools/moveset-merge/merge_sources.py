#!/usr/bin/env python3
"""Add every external move source to every fighter — additions only, nothing lost.

Owner 2026-10-20/21: "We need move string, combos, different moves and move inputs, everything
Tekken and the teardown files have, but Tekken as the base" / "If ur just using stuff from t3 not
the other then u will be limiting us" / "why would you decrease fighter moves?"

main already holds the union of all 548 historical versions (PR #407, tools/moveset-merge/
build_merge.py + guard.py). This tool adds what history never had:
  T8  docs/t7t8-reference/frame-data-t8-full/<body>.json   (all 41 T8 characters, wavu, CC0)
      + docs/t7t8-reference/frame-data/<body>.json          (Oct 14 baseline, deduped by id)
  T7  docs/t7t8-reference/frame-data-t7/<label>.json        (47 T7 characters, t7chicken)
  T3  teardown/tekken3/movesets/moveset_<bank>.json         (20 decoded banks, via the fixed
      tools/gen-movesets-t3.py: strings + EXE common-table throws)
  donors  other WH moveset files (attire variants share the main kit; Koreshi <- Vega,
          KRONOS <- Zangief) — see bases.json
for the characters each fighter is built on (bases.json overrides, else BASE_TABLE on the file's
tekken_base).

Rules (checked by the built-in guard; any failure = nothing is written):
  * every existing move key stays, payload byte-for-byte; strings/specials only appended
  * a new move is added only if no existing move has the same source record (t8_id, t7 id,
    T3 bank+row+input); key = its notation when free, else '<notation>~<src>' (e.g. 'd/f+1~t7.lei')
  * every new move carries merge_source pointing at a record in a vendored dataset
  * `slots` (top level) maps each notation to the move key that input fires by default.
    Priority: WH signature > T8 base > T7 base > T3 base > other curated/donor > proxy bank.
    exclude_proxy fighters (Doc Frank, owner) never slot a proxy-bank move. Every input that
    fired a move before still fires one (proven per fighter) unless the owner's exclusion is the
    reason — those are listed in the report.
  * numbers: frames/60 -> seconds; damage scaled to WH 100 HP (T8 /180, T7 /170, raw kept in
    damage_raw); T7 rows have no recovery column: the same notation's T8 recovery is used,
    else 30f flagged recovery_estimated
  * animation: anim_t3 = {bank,row,match} — the same base character's decoded T3 row for the same
    notation ('same-notation'), else the nearest T3 row of that base by limb/class/startup
    ('nearest', flagged approximate). fighter.js plays it once that bank's rows are baked.

Usage:
  python3 tools/moveset-merge/merge_sources.py --dry-run            # report only
  python3 tools/moveset-merge/merge_sources.py --write [--only id,id]
Report: docs/movesets/SOURCE-MERGE-2026-10-21.json (+ .md written by hand from it)
"""
import argparse, collections, datetime, importlib.util, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import notation as N  # noqa: E402

MS_DIR = REPO / "game/assets/movesets"
T8_FULL = REPO / "docs/t7t8-reference/frame-data-t8-full"
T8_BASE = REPO / "docs/t7t8-reference/frame-data"
T7_DIR = REPO / "docs/t7t8-reference/frame-data-t7"
TODAY = datetime.date.today().isoformat()

# tekken_base text -> sources. Ordered: the first matching row wins (specific before generic).
BASE_TABLE = [
    (r"^armou?r king\b", {"t8": ["armor_king"], "t7": ["armorking"]}),
    (r"^devil jin\b", {"t8": ["devil_jin"], "t7": ["deviljin"], "t3": ["jin"]}),
    (r"^gun ?jack\b|^jack-?8\b", {"t8": ["jack-8"], "t7": ["jack-7"], "t3": ["gunjack"]}),
    (r"^forest law\b", {"t3": ["forestlaw"]}),
    (r"^marshall law\b|^law\b", {"t8": ["law"], "t7": ["law"], "t3": ["law"]}),
    (r"^bosconovitch\b", {"t3": ["bosconovitch"]}),
    (r"^jin\b", {"t8": ["jin"], "t7": ["jin"], "t3": ["jin"]}),
    (r"^heihachi\b", {"t8": ["heihachi"], "t7": ["heihachi"], "t3": ["heihachi"]}),
    (r"^king\b", {"t8": ["king"], "t7": ["king"], "t3": ["king"]}),
    (r"^lei\b", {"t7": ["lei"], "t3": ["lei"]}),
    (r"^paul\b", {"t8": ["paul"], "t7": ["paul"], "t3": ["paul"]}),
    (r"^eddy\b", {"t8": ["eddy"], "t7": ["eddy"], "t3": ["eddy"]}),
    (r"^nina\b", {"t8": ["nina"], "t7": ["nina"], "t3": ["nina"]}),
    (r"^julia\b", {"t7": ["julia"], "t3": ["julia"]}),
    (r"^anna\b", {"t8": ["anna"], "t7": ["anna"], "t3": ["anna"]}),
    (r"^hwoarang\b", {"t8": ["hwoarang"], "t7": ["hwoarang"], "t3": ["hwoarang"]}),
    (r"^xiaoyu\b", {"t8": ["xiaoyu"], "t7": ["xiaoyu"], "t3": ["xiaoyu"]}),
    (r"^yoshimitsu\b", {"t8": ["yoshimitsu"], "t7": ["yoshimitsu"], "t3": ["yoshimitsu"]}),
    (r"^bryan\b", {"t8": ["bryan"], "t7": ["bryan"], "t3": ["bryan"]}),
    (r"^kuma\b", {"t8": ["kuma"], "t7": ["kuma"], "t3": ["kuma"]}),
    (r"^ogre\b", {"t3": ["ogre"]}),
    (r"^gon\b", {"t3": ["gon"]}),
    (r"^lars\b", {"t8": ["lars"], "t7": ["lars"]}),
    (r"^alisa\b", {"t8": ["alisa"], "t7": ["alisa"]}),
    (r"^asuka\b", {"t8": ["asuka"], "t7": ["asuka"]}),
    (r"^lee\b", {"t8": ["lee"], "t7": ["lee"]}),
    (r"^steve\b", {"t8": ["steve"], "t7": ["steve"]}),
    (r"^shaheen\b", {"t8": ["shaheen"], "t7": ["shaheen"]}),
    (r"^josie\b", {"t7": ["josie"]}),
    (r"^katarina\b", {"t7": ["katarina"]}),
    (r"^miguel\b", {"t7": ["miguel"]}),
    (r"^dragunov\b", {"t8": ["dragunov"], "t7": ["dragunov"]}),
    (r"^negan\b", {"t7": ["negan"]}),
    (r"^akuma\b", {"t7": ["akuma"]}),
    (r"^zafina\b", {"t8": ["zafina"], "t7": ["zafina"]}),
    (r"^lili\b", {"t8": ["lili"], "t7": ["lili"]}),
    (r"^bob\b", {"t8": ["bob"], "t7": ["bob"]}),
    (r"^(?:craig )?marduk\b", {"t7": ["marduk"]}),
    (r"^kazuya\b", {"t8": ["kazuya"], "t7": ["kazuya"]}),
    (r"^feng\b", {"t8": ["feng"], "t7": ["feng"]}),
    (r"^leo\b", {"t8": ["leo"], "t7": ["leo"]}),
    (r"^claudio\b", {"t8": ["claudio"], "t7": ["claudio"]}),
    (r"^raven\b", {"t8": ["raven"], "t7": ["masterraven"]}),
    (r"^panda\b", {"t8": ["panda"], "t7": ["panda"]}),
    (r"^geese\b", {"t7": ["geese"]}),
]
T3_BANKS = {p.stem[len("moveset_"):] for p in (REPO / "teardown/tekken3/movesets").glob("moveset_*.json")}
T8_SCALE, T7_SCALE = 100 / 180, 100 / 170


def norm_name(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


# ---------------------------------------------------------------- loaders
_gen = None


def gen():
    global _gen
    if _gen is None:
        spec = importlib.util.spec_from_file_location("genms", REPO / "tools/gen-movesets-t3.py")
        G = importlib.util.module_from_spec(spec)
        saved = sys.argv
        sys.argv = [saved[0], str(REPO / "teardown/tekken3/movesets")]
        spec.loader.exec_module(G)
        sys.argv = saved
        _gen = G
    return _gen


_cache = {}


def t8_rows(name):
    if ("t8", name) in _cache:
        return _cache[("t8", name)]
    rows, body = {}, None
    for d in (T8_FULL, T8_BASE):
        p = d / f"{name}.json"
        if p.exists():
            j = json.loads(p.read_text())
            if "moves" not in j:
                continue
            body = body or j["body"]
            for r in j["moves"]:
                rows.setdefault(r["id"], r)
    out = (body, list(rows.values()))
    _cache[("t8", name)] = out
    return out


def t7_rows(label):
    if ("t7", label) in _cache:
        return _cache[("t7", label)]
    p = T7_DIR / f"{label}.json"
    d = json.loads(p.read_text()) if p.exists() else []
    out = d["movelist"] if isinstance(d, dict) else d
    _cache[("t7", label)] = out
    return out


def t3_moves(bank):
    if ("t3", bank) in _cache:
        return _cache[("t3", bank)]
    G = gen()
    rows = G.bank_edges(bank)
    moves, strings = G.build_moves(bank, bank.upper(), rows)
    _cache[("t3", bank)] = moves
    return moves


# ---------------------------------------------------------------- conversion helpers
def first_int(s):
    m = re.search(r"-?\d+", str(s or ""))
    return int(m.group()) if m else None


def damage_of(s):
    """'7 [8]' -> 7 ; '10,12' -> 22 ; '4,20' -> 24 (bracketed values = alternate/rage, dropped)"""
    s = re.sub(r"\[[^\]]*\]", "", str(s or ""))
    vals = [int(x) for x in re.findall(r"\d+", s)]
    return sum(vals), vals


def wiki_text(s, n=220):
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", str(s or ""))
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*\n\s*\*?\s*", "; ", s).strip("; *")
    return s[:n]


def knock_of(text, is_throw, heavy):
    t = str(text or "")
    if is_throw:
        return 6.5, None
    if re.search(r"\d+a\b|launch|float", t, re.I):
        return 6.0, "launch"
    if re.search(r"\bknd\b|knockdown|\d+d\b", t, re.I):
        return 5.0, "knockdown"
    return (4.2 if heavy else 2.2), None


def move_class_of(notation, is_throw):
    if is_throw:
        return "throw"
    if not notation:
        return "special"
    body = notation.split(".")[-1]
    if N.is_motion(notation) or notation.startswith(("R.", "H.")):
        return "special"
    if "," in body or "~" in body or ":" in body:
        return "string"
    if "." in notation:
        return "special"
    return "strike"


def soul(dmg):
    return int(max(2, min(13, round(dmg * 0.6) + 2)))


def conv_t8(row, body, display):
    raw = row["id"][len(body) + 1:]
    nt, note = N.canon(raw)
    start = first_int(row.get("startup"))
    recv = first_int(row.get("recv"))
    tot = first_int(row.get("tot"))
    dmg_raw, hits = damage_of(row.get("damage"))
    tgt = str(row.get("target") or "")
    is_throw = "t" in tgt.lower() or "throw" in raw.lower()
    dmg = round(dmg_raw * T8_SCALE)
    heavy = dmg_raw >= 18
    notes = wiki_text(row.get("notes"))
    knock, kind = knock_of(f"{row.get('hit')} {row.get('ch')} {notes}", is_throw, heavy)
    active = max(1, tot - (start - 1) - recv) if (tot and start and recv is not None) else 2
    mv = {
        "name": row.get("name") or f"{display} {nt or raw}",
        "input": nt or raw,
        "startup": round((start or 12) / 60, 3), "active": round(active / 60, 3),
        "recovery": round((recv if recv is not None else 30) / 60, 3),
        "damage": dmg, "damage_raw": dmg_raw,
        "limb": "both" if is_throw else N.limb(nt), "heavy": heavy or knock >= 5, "knock": knock,
        "soulGain": soul(dmg), "hit_level": tgt,
        "on_block": row.get("block"), "on_hit": row.get("hit"), "on_ch": row.get("ch"), "crush": row.get("crush"),
        "anim_ref": f"t8:{norm_name(body)}:{row['id'].lower()}",
        "input_slots": [nt] if nt else [],
        "move_class": move_class_of(nt, is_throw),
        "t8_source": norm_name(body), "t8_id": row["id"], "t8_damage": row.get("damage"), "t8_input": raw,
        "merge_source": f"t8:{row['id']}",
    }
    if len(hits) > 1:
        mv["multi_hit"] = {"hits": hits, "total": dmg_raw}
    if kind:
        mv[kind] = True
    if notes:
        mv["note"] = notes
    if note:
        mv["input_note"] = note
    if row.get("alias"):
        mv["t8_alias"] = row["alias"]
    if is_throw:
        mv.update(throw=True, isGrab=True, unblockable=True)
        br = re.search(r"break[^0-9]*([12](?:\+2)?)", notes, re.I)
        if br:
            mv["throw_break"] = br.group(1)
    return nt, mv


def conv_t7(row, label, display, t8_recv):
    raw = row.get("notation")
    nt, note = N.canon(raw)
    start = first_int(row.get("speed"))
    act = first_int(row.get("active_frames")) or 1
    dmg_raw, hits = damage_of(row.get("damage"))
    hl = str(row.get("hit_level") or "")
    is_throw = "throw" in hl.lower() or "throw" in str(row.get("notes") or "").lower()[:40]
    dmg = round(dmg_raw * T7_SCALE)
    heavy = dmg_raw >= 18
    notes = "" if row.get("notes") in (None, "-") else str(row.get("notes"))[:220]
    knock, kind = knock_of(f"{row.get('on_hit')} {row.get('on_ch')} {row.get('in_air')} {notes}", is_throw, heavy)
    recv = t8_recv.get(nt)
    mv = {
        "name": row.get("move_name") or f"{display} {nt or raw}",
        "input": nt or raw,
        "startup": round((start or 12) / 60, 3), "active": round(act / 60, 3),
        "recovery": round((recv if recv is not None else 30) / 60, 3),
        "damage": dmg, "damage_raw": dmg_raw,
        "limb": "both" if is_throw else N.limb(nt), "heavy": heavy or knock >= 5, "knock": knock,
        "soulGain": soul(dmg), "hit_level": hl,
        "on_block": row.get("on_block"), "on_hit": row.get("on_hit"), "on_ch": row.get("on_ch"),
        "crush": None if row.get("crush") in (None, "-") else row.get("crush"),
        "anim_ref": f"t7:{label}:{row.get('id')}",
        "input_slots": [nt] if nt else [],
        "move_class": move_class_of(nt, is_throw),
        "t7_source": "t7chicken (dayhaysoos/t7chickenplus-graphql — TekkenBot-extracted T7 frame data)",
        "t7_move_id": row.get("id"), "t7_command": raw, "t7_hit_level": hl, "t7_damage_raw": row.get("damage"),
        "t7_startup_frames": row.get("speed"), "t7_on_block": row.get("on_block"), "t7_on_hit": row.get("on_hit"),
        "t7_on_ch": row.get("on_ch"),
        "merge_source": f"t7:{row.get('id')}",
    }
    if recv is None:
        mv["recovery_estimated"] = "T7 data has no recovery column and T8 has no same-notation move: 30f"
    else:
        mv["recovery_from"] = "same-notation T8 recv"
    if len(hits) > 1:
        mv["multi_hit"] = {"hits": hits, "total": dmg_raw}
    if kind:
        mv[kind] = True
    if notes:
        mv["note"] = notes
    if note:
        mv["input_note"] = note
    if is_throw:
        mv.update(throw=True, isGrab=True, unblockable=True)
    return nt, mv


# ---------------------------------------------------------------- per-move facts on existing entries
# '~<src>.<id>' tags a source variant ('d/f+1~t7.lei', '4~t7.jin.2', '3~donor.byou'); a bare '~4' / '~D' is the
# INPUT ('3~4', '4~3', 'f+3~1', 'SCR 3,3,4~D'). Stripping every '~...' (before 2026-11-01) read '3~4' as '3' and
# slotted it on plain 3 (Phantom, Rave, Diablo, Demonio, Purple Rain '3~3'; tools/moveset-merge/tests/test_notation_slots.py).
VARIANT_SUFFIX = re.compile(r"(?:_[cr]\d+)+(?:_\d+)?$|__\w+$|_t[378]$|~(?:t\d|donor)\.[\w.]+$")


def notation_of(key, m):
    """The input a move answers to. `input` first (input_slots[0] is the FIRST HIT of a string in
    schema-v2 files, and t8_input is only the last segment), variant suffixes stripped
    ('1+3_c36', 'f+3__main', '1_t8', 'd/f+1~t7.lei'), then the key, then the LAST input_slots entry (the
    whole input: input_slots[0] slotted unparsed strings such as '1,2,&amp;#58;4' on their first hit '1')."""
    for cand in (m.get("input"), key, (m.get("input_slots") or [None])[-1], m.get("t7_command")):
        if not cand:
            continue
        nt, _ = N.canon(VARIANT_SUFFIX.sub("", str(cand)))
        if nt:
            return nt
    return None


def _hashable(v):
    # batch8 2026-10-23: older moveset files (chatur) store t3_row as a list
    # (multi-row moves); coerce so the identity tuple stays hashable.
    return tuple(v) if isinstance(v, list) else v


def identity(m):
    if m.get("t8_id"):
        return ("t8", _hashable(m["t8_id"]))
    if m.get("t7_move_id"):
        return ("t7", _hashable(m["t7_move_id"]))
    if m.get("t3_source") and m.get("t3_row") is not None:
        return ("t3", m["t3_source"], _hashable(m["t3_row"]), tuple(m.get("input_slots") or [m.get("input")]),
                _hashable(m.get("t3_condition")), _hashable(m.get("t3_restriction")))
    return None


def is_signature(m):
    return bool(m.get("wh_original")) or m.get("move_class") == "signature" or str(m.get("anim_ref", "")).startswith("wh:") \
        or m.get("t3_source") == "original"


def tier(m, B):
    if is_signature(m):
        return 0
    if m.get("t8_source") and norm_name(m["t8_source"]) in {norm_name(x) for x in B.get("t8", [])}:
        return 1
    if m.get("t7_move_id") and norm_name(str(m["t7_move_id"]).rsplit("_", 1)[0]) in {norm_name(x) for x in B.get("t7", [])}:
        return 2
    if m.get("t3_source") in set(B.get("t3", [])):
        return 3
    if m.get("t3_source") in T3_BANKS and B.get("t3") and m.get("t3_source") not in B["t3"]:
        return 5  # proxy bank
    return 4


OLD_DIRS = {"d", "d/f", "f", "b", "d/b", "u/f", "u/b", "u"}
OLD_MOTIONS = {"qcf", "qcb", "hcf", "hcb"}


def old_special_fires(inp):
    """Exact emulation of game/js/movesets.js parseSpecialInput + TekkenBuffer special match:
    a trailing run of '+1..4' parts is the button chord, the rest a motion whose directions the
    direction history can contain."""
    parts = inp.split("+")
    btn = []
    while parts and re.fullmatch(r"[1234]", parts[-1]):
        btn.insert(0, parts.pop())
    if not btn:
        return False
    motion = "+".join(parts)
    if motion in OLD_MOTIONS:
        return True
    dirs = [x.strip() for x in motion.split(",") if x.strip() and x.strip() not in ("n", "any")]
    dirs = [y for d in dirs for y in (["f", "f"] if d == "f,F" else ["b", "b"] if d == "b,B" else [d])]
    dirs = ["f" if d == "F" else "b" if d == "B" else d for d in dirs]
    return bool(dirs) and all(d in OLD_DIRS for d in dirs)


def reachable_old(k, specials):
    """Input forms the pre-2026-10-21 TekkenBuffer could fire (raw/dir button or chord, button
    string continuations, motion specials that parseSpecialInput can actually match)."""
    if k in specials and old_special_fires(k):
        return True
    parts = k.split(",")
    for p in parts:
        if not re.fullmatch(r"(?:(?:f|b|u|d|d/f|d/b|u/f|u/b)\+)?[1-4](?:\+[1-4])*", p):
            return False
    return all(re.fullmatch(r"[1-4]", p) for p in parts[1:])


# ---------------------------------------------------------------- merge one fighter
def bases_for(fid, cur, over):
    o = over.get(fid)
    auto = {}
    text = str(cur.get("tekken_base") or "").lower()
    for pat, b in BASE_TABLE:
        if re.match(pat, text):
            auto = {k: list(v) for k, v in b.items()}
            break
    if o:
        out = dict(auto)
        for k in ("t8", "t7", "t3"):
            if k in o:
                out[k] = list(o[k])
        out["donors"] = list(o.get("donors", []))
        out["exclude_proxy"] = bool(o.get("exclude_proxy"))
        out["why"] = o.get("why")
        return out
    auto.setdefault("donors", [])
    auto["exclude_proxy"] = False
    auto["why"] = f"auto from tekken_base {cur.get('tekken_base')!r}" if auto.get("t8") or auto.get("t7") or auto.get("t3") else None
    return auto


def merge_one(fid, cur, B, all_files):
    moves = cur.get("moves") or {}
    before = json.loads(json.dumps(cur))
    have_ids = {identity(m) for m in moves.values() if isinstance(m, dict) and identity(m)}
    display = cur.get("display") or fid.upper()
    added = collections.Counter()
    new = {}

    def add(nt, mv, tag):
        idt = identity(mv)
        if idt and idt in have_ids:
            return
        key = nt or mv["merge_source"].replace(":", ".")
        if key in moves or key in new:
            key = f"{nt}~{tag}" if nt else key
            i = 2
            while key in moves or key in new:
                key = f"{nt}~{tag}.{i}"
                i += 1
        new[key] = mv
        if idt:
            have_ids.add(idt)
        added[tag.split(".")[0]] += 1

    # T8 first (newest era), then T7, then T3
    t8_recv = {}
    for name in B.get("t8", []):
        body, rows = t8_rows(name)
        if not body:
            continue
        for r in rows:
            nt, mv = conv_t8(r, body, display)
            if nt and first_int(r.get("recv")) is not None:
                t8_recv.setdefault(nt, first_int(r.get("recv")))
            add(nt, mv, f"t8.{norm_name(body)}")
    for label in B.get("t7", []):
        for r in t7_rows(label):
            nt, mv = conv_t7(r, label, display, t8_recv)
            add(nt, mv, f"t7.{label}")
    for bank in B.get("t3", []):
        if bank not in T3_BANKS:
            continue
        for k, mv in t3_moves(bank).items():
            mv = dict(mv)
            mv["merge_source"] = f"t3:{bank}:row:{mv['t3_row']}"
            nt = notation_of(k, mv)
            add(nt, mv, f"t3.{bank}")
    for donor in B.get("donors", []):
        d = all_files.get(donor)
        if not d:
            continue
        for k, mv in (d.get("moves") or {}).items():
            if not isinstance(mv, dict):
                continue
            mv = dict(mv)
            mv["merge_source"] = f"donor:{donor}:{k}"
            mv["donor_fighter"] = donor
            nt = notation_of(k, mv)
            add(nt, mv, f"donor.{donor}")

    # animation for non-T3 moves: same base character's decoded T3 row
    t3_by_nt = collections.defaultdict(list)
    for bank in B.get("t3", []):
        if bank in T3_BANKS:
            for k, mv in t3_moves(bank).items():
                nt = notation_of(k, mv)
                if nt and not mv.get("t3_condition"):
                    t3_by_nt[nt].append((bank, mv))
    t3_all = [x for v in t3_by_nt.values() for x in v]
    for key, mv in new.items():
        if mv.get("t3_row") is not None or not t3_all:
            continue
        nt = mv.get("input")
        if nt in t3_by_nt:
            bank, src = t3_by_nt[nt][0]
            mv["anim_t3"] = {"bank": bank, "row": src["t3_row"], "match": "same-notation"}
        else:
            cls = mv.get("move_class")
            cand = [x for x in t3_all if x[1].get("limb") == mv.get("limb") and x[1].get("move_class") == cls] or \
                   [x for x in t3_all if x[1].get("limb") == mv.get("limb")] or t3_all
            bank, src = min(cand, key=lambda x: abs((x[1].get("startup") or 0) - (mv.get("startup") or 0)))
            mv["anim_t3"] = {"bank": bank, "row": src["t3_row"], "match": "nearest limb/class/startup (approximate)"}

    merged_moves = dict(moves)
    merged_moves.update(new)
    # slots: notation -> key
    slots, slot_tier = {}, {}
    old_spec = {sp.get("input") for sp in before.get("specials") or [] if isinstance(sp, dict)}
    order = list(moves.items()) + list(new.items())
    for idx, (k, m) in enumerate(order):
        if not isinstance(m, dict):
            continue
        nt = notation_of(k, m)
        if not nt and reachable_old(k, old_spec):
            nt = k
        if not nt:
            continue
        t = tier(m, B)
        if t == 5 and B.get("exclude_proxy"):
            continue
        rank = (t, 1 if (m.get("t3_condition") or m.get("t3_restriction")) else 0, 0 if k == nt else 1, idx)
        if nt not in slots or rank < slot_tier[nt]:
            slots[nt], slot_tier[nt] = k, rank
    # strings / specials appended for new notations
    strings = list(cur.get("strings") or [])
    specials = list(cur.get("specials") or [])
    have_s = {s.get("input") for s in strings if isinstance(s, dict)}
    have_sp = {s.get("input") for s in specials if isinstance(s, dict)}
    for k, m in new.items():
        nt = m.get("input")
        if not nt or slots.get(nt) != k:
            continue
        if m.get("move_class") == "string" and nt not in have_s:
            strings.append({"input": nt, "hits": re.split(r"[,~:]", nt.split(".")[-1]), "merge_source": m["merge_source"]})
            have_s.add(nt)
        if m.get("move_class") == "special" and N.is_motion(nt) and nt not in have_sp:
            specials.append({"input": nt, "name": m.get("name"), "merge_source": m["merge_source"]})
            have_sp.add(nt)

    out = dict(cur)
    out["moves"] = merged_moves
    out["strings"] = strings
    out["specials"] = specials
    out["slots"] = dict(sorted(slots.items()))
    old_play = sorted({k for k in moves if reachable_old(k, old_spec)})
    lost = [k for k in old_play if (notation_of(k, moves[k]) or k) not in slots]
    excused = [k for k in lost if B.get("exclude_proxy") and tier(moves[k], B) == 5]
    by_tier = collections.Counter(slot_tier[n][0] for n in slots)
    out["merge_sources"] = {
        "date": TODAY, "by": "tools/moveset-merge/merge_sources.py",
        "bases": {k: B.get(k) for k in ("t8", "t7", "t3", "donors") if B.get(k)},
        "why": B.get("why"), "exclude_proxy": B.get("exclude_proxy", False),
        "moves_before": len(moves), "moves_after": len(merged_moves), "added": dict(added),
        "slots": len(slots), "slots_by_priority": {["signature", "t8", "t7", "t3", "curated/donor", "proxy"][t]: n for t, n in sorted(by_tier.items())},
        "previously_playable_inputs": len(old_play),
        "owner_excluded_inputs": excused,
        "note": "Existing moves untouched. New moves carry merge_source; slots = default input map "
                "(editor can reassign any move). Damage scaled to WH 100 HP, raw in damage_raw.",
    }
    return out, before, lost, excused, added


# ---------------------------------------------------------------- engine annotations (top level only)
# Decoded T3 attack words (Tekken3Remake docs/research/code/combat.md "Attack levels, postures and
# guards"; HitClassify 0x80044D24): low 3 bits = postures the attack can hit (1 crouching, 2 standing,
# 4 down), bits 3-4 = guards that block it (0x08 crouching, 0x10 standing).
HIGH, MID, LOW, SMID, UNBL, THROW = 0x412, 0x217, 0x10F, 0x31F, 0x607, 0x800
_bank_rows = {}


def bank_attack_word(bank, row):
    if bank not in T3_BANKS:
        return None
    if bank not in _bank_rows:
        d = json.loads((REPO / f"teardown/tekken3/movesets/moveset_{bank}.json").read_text())
        _bank_rows[bank] = {m["row"]: int(m["attack_word"], 16) for m in d["moves"]}
    if isinstance(row, list):  # string moves carry one T3 row per hit: the last hit's word
        row = row[-1] if row else None
    w = _bank_rows[bank].get(row)
    return w if w else None


def word_from_label(label):
    """T8 wavu target ('m', ',h', 'th(h)', 'm!', 'sm') or T7 hit_level ('high, mid', 's. mid',
    'high throw') -> T3 attack word of the LAST hit."""
    if not label:
        return None
    toks = [t.strip().lower() for t in re.split(r",", str(label)) if t.strip() and t.strip() != "-"]
    if not toks:
        return None
    t = toks[-1]
    if "throw" in t or t.startswith("t"):
        return THROW
    if "!" in t or "unblock" in t:
        return UNBL
    if t.startswith(("s.", "sm", "sp")) or t == "s":
        return SMID
    if t.startswith(("sl", "l")) or "low" in t:
        return LOW
    if t.startswith("m") or "mid" in t:
        return MID
    if t.startswith("h") or "high" in t:
        return HIGH
    return None


STANCE_RE = re.compile(r"(?:Transition|Transitions|Cancel|Enter|Shift)s?\s+(?:to|into)?\s*(?:r\d+\s+)?([A-Z]{2,6})\b([^\n*;]*)")


_notes_by_id = None


def source_notes(m):
    """Full notes of the move's source record (earlier imports kept only a short summary)."""
    global _notes_by_id
    if _notes_by_id is None:
        _notes_by_id = {}
        for p in list(T8_FULL.glob("*.json")) + list(T8_BASE.glob("*.json")):
            j = json.loads(p.read_text())
            for r in j.get("moves", []) if isinstance(j, dict) else []:
                if r.get("notes"):
                    _notes_by_id.setdefault(("t8", r["id"]), wiki_text(r["notes"], 2000))
        for p in T7_DIR.glob("*.json"):
            if p.name == "SOURCE.json":
                continue
            j = json.loads(p.read_text())
            for r in (j["movelist"] if isinstance(j, dict) else j):
                if r.get("notes") not in (None, "-"):
                    _notes_by_id.setdefault(("t7", r.get("id")), str(r["notes"]))
    out = []
    if m.get("t8_id"):
        out.append(_notes_by_id.get(("t8", m["t8_id"]), ""))
    if m.get("t7_move_id"):
        out.append(_notes_by_id.get(("t7", m["t7_move_id"]), ""))
    return " ".join(out)


def stance_after_of(m):
    text = " ".join(str(m.get(k) or "") for k in ("note", "notes")) + " " + source_notes(m)
    for mm in STANCE_RE.finditer(html_unescape(text)):
        code, tail = mm.group(1), mm.group(2).lower()
        if re.search(r"\bwith\b|on hit|on block|on ch|hold|input", tail):
            continue  # conditional transition: needs an extra input; not automatic
        return code
    return None


def html_unescape(s):
    import html
    return html.unescape(s)


def annotate(fid, data):
    """Top-level engine data derived from the move records already in the file."""
    words, stances = {}, {}
    for k, m in (data.get("moves") or {}).items():
        if not isinstance(m, dict):
            continue
        w = None
        if m.get("t3_source") and m.get("t3_row") is not None:
            w = bank_attack_word(m["t3_source"], m["t3_row"])
        if w is None:
            w = word_from_label(m.get("hit_level") or m.get("t7_hit_level"))
        if w is None and (m.get("throw") or m.get("isGrab")):
            w = THROW
        if w is not None:
            words[k] = w
        st = stance_after_of(m)
        if st:
            stances[k] = st
    data["hit_words"] = words
    data["stance_after"] = stances
    bases = (data.get("merge_sources") or {}).get("bases") or {}
    for bank in bases.get("t3", []):
        if (REPO / f"game/assets/anim/t3/{bank}/skeleton.json").exists():
            data["anim_bank"] = bank
            break
    return data


# ---------------------------------------------------------------- guard
def canon_json(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def guard(fid, before, after, lost, excused):
    errs = []
    bm, am = before.get("moves") or {}, after.get("moves") or {}
    for k, v in bm.items():
        if k not in am:
            errs.append(f"move key lost: {k}")
        elif canon_json(am[k]) != canon_json(v):
            errs.append(f"move payload changed: {k}")
    for cat in ("strings", "specials"):
        b = collections.Counter(canon_json(x) for x in before.get(cat) or [])
        a = collections.Counter(canon_json(x) for x in after.get(cat) or [])
        for item, n in b.items():
            if a[item] < n:
                errs.append(f"{cat[:-1]} lost: {item[:80]}")
    for k in am:
        if k in bm:
            continue
        src = am[k].get("merge_source")
        if not src:
            errs.append(f"new move without merge_source: {k}")
    for k in set(lost) - set(excused):
        errs.append(f"previously playable input has no slot: {k}")
    for nt, k in (after.get("slots") or {}).items():
        if k not in am:
            errs.append(f"slot {nt} -> missing key {k}")
    return errs


def verify_sources(after):
    """Every merge_source must resolve to a record in a vendored dataset."""
    bad = []
    for k, m in (after.get("moves") or {}).items():
        s = m.get("merge_source") if isinstance(m, dict) else None
        if not s:
            continue
        kind = s.split(":", 1)[0]
        if kind == "t8":
            rid = s[3:]
            body = m.get("t8_source")
            ok = any(r["id"] == rid for name in [p.stem for p in T8_FULL.glob("*.json")]
                     if norm_name(name) == body for r in t8_rows(name)[1])
        elif kind == "t7":
            rid = s[3:]
            ok = any(r.get("id") == rid for r in t7_rows(rid.rsplit("_", 1)[0]))
        elif kind == "t3":
            _, bank, _, row = s.split(":")
            ok = any(str(v.get("t3_row")) == row for v in t3_moves(bank).values())
        elif kind == "donor":
            ok = True
        else:
            ok = False
        if not ok:
            bad.append(f"{k}: {s}")
    return bad


def file_style(original_text):
    """The json.dumps settings that reproduce this file byte-for-byte (indent / ensure_ascii /
    trailing newline vary across the repo's moveset files), so the diff shows only additions."""
    data = json.loads(original_text)
    best, best_diff = None, None
    for indent in (2, 1, 4, None):
        for ea in (False, True):
            for nl in ("\n", ""):
                t = json.dumps(data, indent=indent, ensure_ascii=ea) + nl
                if t == original_text:
                    return (indent, ea, nl), 0
                d = sum(1 for a, b in zip(t.splitlines(), original_text.splitlines()) if a != b) + \
                    abs(len(t.splitlines()) - len(original_text.splitlines()))
                if best_diff is None or d < best_diff:
                    best, best_diff = (indent, ea, nl), d
    return best, best_diff


def dump_like(path, data, original_text):
    (indent, ea, nl), _ = file_style(original_text)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=ea) + nl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--report", default=str(REPO / "docs/movesets/SOURCE-MERGE-2026-10-21.json"))
    a = ap.parse_args()
    over = json.loads((Path(__file__).resolve().parent / "bases.json").read_text())["override"]
    texts = {p.stem: p.read_text() for p in sorted(MS_DIR.glob("*.json"))}
    files = {k: json.loads(v) for k, v in texts.items()}
    only = set(filter(None, a.only.split(",")))
    report, failures, outs = {}, [], {}
    for fid, cur in files.items():
        if only and fid not in only:
            continue
        if not isinstance(cur, dict) or not isinstance(cur.get("moves"), dict):
            continue
        B = bases_for(fid, cur, over)
        if not any(B.get(k) for k in ("t8", "t7", "t3", "donors")):
            report[fid] = {"skipped": "no Tekken/teardown base with decoded data", "tekken_base": cur.get("tekken_base")}
            continue
        after, before, lost, excused, added = merge_one(fid, cur, B, files)
        errs = guard(fid, before, after, lost, excused) + [f"unresolved source {x}" for x in verify_sources(after)[:5]]
        if errs:
            failures += [f"{fid}: {e}" for e in errs[:20]]
        ms = after["merge_sources"]
        report[fid] = {k: ms[k] for k in ("bases", "why", "moves_before", "moves_after", "added", "slots",
                                         "slots_by_priority", "previously_playable_inputs", "owner_excluded_inputs")}
        outs[fid] = after
        print(f"{fid:24s} moves {ms['moves_before']:4d} -> {ms['moves_after']:4d}  slots {ms['slots']:4d} "
              f"(was playable {ms['previously_playable_inputs']:4d})  +{dict(added)}  {'GUARD FAIL' if errs else 'ok'}")
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    if a.only and Path(a.report).exists():
        # --only updates just those fighters' entries; the rest of the report stays as it was
        # (a 2026-10-21 '--only zui' run had replaced the whole 96-fighter report with one entry).
        prev = json.loads(Path(a.report).read_text())
        merged = prev.get("fighters", {})
        merged.update(report)
        failures = [f for f in prev.get("failures", []) if not any(str(f).startswith(fid) for fid in report)] + failures
        report = merged
    Path(a.report).write_text(json.dumps({"date": TODAY, "tool": "tools/moveset-merge/merge_sources.py",
                                          "fighters": report, "failures": failures}, indent=1, ensure_ascii=False) + "\n")
    if failures:
        print(f"\n{len(failures)} GUARD FAILURES — nothing written")
        for f in failures[:40]:
            print(" -", f)
        sys.exit(1)
    print(f"\nGUARD PASS: {len(outs)} fighters, no move/string/special/input lost")
    for fid, cur in files.items():
        if only and fid not in only:
            continue
        if isinstance(cur, dict) and isinstance(cur.get("moves"), dict):
            base = outs.get(fid, json.loads(json.dumps(cur)))
            before_moves = json.dumps(base.get("moves"), sort_keys=True)
            outs[fid] = annotate(fid, base)
            assert json.dumps(outs[fid].get("moves"), sort_keys=True) == before_moves, fid
    if a.write:
        for fid, data in outs.items():
            dump_like(MS_DIR / f"{fid}.json", data, texts[fid])
        print(f"wrote {len(outs)} files")
        build_index()


def build_index():
    """game/assets/movesets/index.json — what game/js/movesets.js loads at boot (the full
    per-fighter files load per fight via ensureMovesets())."""
    idx = {}
    for p in sorted(MS_DIR.glob("*.json")):
        if p.name == "index.json":
            continue
        d = json.loads(p.read_text())
        if not isinstance(d, dict) or not isinstance(d.get("moves"), dict):
            continue
        idx[p.stem] = {k: d.get(k) for k in ("display", "tekken_base", "t3_source", "anim_bank") if d.get(k) is not None}
        idx[p.stem]["moves"] = len(d["moves"])
        idx[p.stem]["inputs"] = len(d.get("slots") or {}) or len(d["moves"])
        idx[p.stem]["bytes"] = p.stat().st_size
    out = {"format": "wh-moveset-index/1", "tool": "tools/moveset-merge/merge_sources.py", "fighters": idx}
    (MS_DIR / "index.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"index.json: {len(idx)} fighters")


if __name__ == "__main__":
    main()
