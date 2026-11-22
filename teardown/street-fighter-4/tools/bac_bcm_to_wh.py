"""bac/bcm -> Western Heart moveset converter (Lane 1B).

Reads the combined per-character JSON produced by running dantarion/sf4tools
(bac.py / bcm.py) against real SFIV / SFxT / USFIV game files, and emits a
Western Heart moveset JSON (schema v2, same contract as
game/assets/movesets/doa-kasumi.json).

Source facts used (all from the real format, via bac.py / bcm.py):
- BCM Moves: move name, input flags, restrictions, EX/Ultra cost,
  InputMotion name, Script name.
- BAC Scripts: TotalFrames, FirstHitboxFrame, LastHitboxFrame, IASAFrame,
  CommandLists (ANIMATION / HITBOX / PHYSICS / CANCELS / ...).
- BAC HitboxTable: per-hitbox Damage / Stun / OnHit / OnBlock / velocities /
  pushback, keyed by the HitboxData index the script's HITBOX commands point at.

Frame convention: SF runs at 60 fps. startup = FirstHitboxFrame / 60,
active = (LastHitboxFrame - FirstHitboxFrame + 1) / 60,
recovery = (TotalFrames - LastHitboxFrame) / 60. IASA is recorded in the note.

SF 6-button -> WH 4-button mapping (documented, deterministic):
  LP -> 1, MP -> 2, HP -> 1+2, LK -> 3, MK -> 4, HK -> 3+4.
Directions: FORWARD -> f, BACK -> b, DOWN -> d, UP -> u, combined with '/'
(e.g. DOWN|FORWARD -> d/f). Motion sequences come from the BCM Inputs table
(InputMotion name, e.g. QCF) and are rendered in WH comma notation
(e.g. QCF+P -> "d,d/f,f+1"); unknown motions fall back to the raw motion name
plus the button, and are flagged in the note.

What this converter does NOT do: skeletal animation clips. bac/bcm carry
moveset logic + frame data + hitboxes, NOT the .anm/.emm animation data.
anim_ref is therefore "sf4:<char>/<script>" (or sfxt:/usfiv:), a stable
reference the animation extraction can resolve later. No hand-tooled
substitute animation is invented.

Usage:
  python3 bac_bcm_to_wh.py <combined-char.json> [<combined-char.json> ...]
  python3 bac_bcm_to_wh.py --dir <dir-of-combined-json> --out <out-dir>
"""

import argparse
import json
import os
import re
import sys

FPS = 60.0

# BCM InputEnum bit values (util.py, dantarion/sf4tools).
DIR_BITS = [(0x02, "u"), (0x04, "d"), (0x08, "b"), (0x10, "f")]
BUTTON_BITS = [
    (0x40, "LP"), (0x80, "MP"), (0x100, "HP"),
    (0x200, "LK"), (0x400, "MK"), (0x800, "HK"),
]
# SF button -> WH Tekken-style button(s).
BUTTON_TO_WH = {"LP": "1", "MP": "2", "HP": "1+2",
                "LK": "3", "MK": "4", "HK": "3+4"}

# Known motion names (BCM InputMotion) -> WH comma-notation direction steps.
# Filled from real data as encountered; unknown motions fall back to the
# raw motion name (flagged in the note) rather than being guessed.
MOTION_DIRECTIONS = {
    "QCF": ["d", "d/f", "f"],
    "QCB": ["d", "d/b", "b"],
    "HCF": ["b", "d/b", "d", "d/f", "f"],
    "HCB": ["f", "d/f", "d", "d/b", "b"],
    "DP": ["f", "d", "d/f"],
    "RDP": ["b", "d", "d/b"],
    "360": ["f", "d/f", "d", "d/b", "b", "u/b", "u", "u/f"],
    "720": ["f", "d/f", "d", "d/b", "b", "u/b", "u", "u/f",
            "f", "d/f", "d", "d/b", "b", "u/b", "u", "u/f"],
}

GAME_PREFIX = {"SFIV": "sf4", "SFxT": "sfxt", "USFIV": "usfiv"}
GAME_DISPLAY = {"SFIV": "SFIV", "SFxT": "SFxT", "USFIV": "USFIV"}


def parse_flag_hex(flag_str):
    """util.flags() renders 'A|B=0x123'; recover the hex value."""
    m = re.search(r"=0x([0-9a-fA-F]+)$", str(flag_str or ""))
    if m:
        return int(m.group(1), 16)
    # bcm.py PRETTY mode may already have resolved some fields; fall back to 0.
    return 0


def flag_names(flag_str):
    """Return the label part of a 'A|B=0x..' flag string."""
    s = str(flag_str or "")
    return s.split("=")[0] if "=" in s else s


def wh_directions(value):
    """Direction bits -> ordered WH direction token, e.g. 0x14 -> 'd/f'."""
    parts = [tok for bit, tok in DIR_BITS if value & bit]
    # Canonical order: u/d first, then b/f (WH writes d/f, d/b, u/f, u/b).
    order = {"u": 0, "d": 0, "b": 1, "f": 1}
    parts.sort(key=lambda t: order[t])
    return "/".join(parts)


def wh_buttons(value):
    """Button bits -> WH button token(s), e.g. HP -> '1+2'."""
    names = [name for bit, name in BUTTON_BITS if value & bit]
    wh = [BUTTON_TO_WH[n] for n in names]
    # Flatten chords: HP alone is '1+2'; LP+HP is also '1+2' (dedup, sorted).
    out = []
    for token in wh:
        for b in token.split("+"):
            if b not in out:
                out.append(b)
    out.sort(key=int)
    return "+".join(out) if out else ""


def motion_steps(motion_name):
    """BCM InputMotion name -> direction steps, or None if unknown."""
    if not motion_name or not isinstance(motion_name, str):
        return None
    key = motion_name.strip().upper()
    # Strip common suffixes: 'QCF_P', 'QCF+P', 'QCF LP', 'QCFP', 'QCF2'...
    key = re.sub(r"[^A-Z0-9]", "", key)
    for known, steps in MOTION_DIRECTIONS.items():
        if key == known or key.startswith(known):
            return steps
    return None


def wh_input_for_move(move):
    """Build the WH input string for one BCM move.

    Returns (input_string, notes_list).
    """
    notes = []
    raw_input = move.get("Input", "")
    value = parse_flag_hex(raw_input)
    dirs = wh_directions(value)
    btns = wh_buttons(value)
    motion = move.get("InputMotion")
    steps = motion_steps(motion) if isinstance(motion, str) else None
    if isinstance(motion, str) and motion not in ("", "-1") and steps is None:
        notes.append("unmapped motion '%s' (raw input flags %s)" % (motion, raw_input))
    if steps:
        # Motion + button, e.g. d,d/f,f+1. Trailing direction merges with button.
        seq = ",".join(steps[:-1] + [steps[-1] + ("+" + btns if btns else "")])
        return seq, notes
    if dirs and btns:
        return "%s+%s" % (dirs, btns), notes
    if btns:
        return btns, notes
    if dirs:
        return dirs, notes
    return "", notes


def script_frame_data(script):
    """Extract frame numbers from a BAC script dict."""
    if not isinstance(script, dict):
        return None
    return {
        "total": script.get("TotalFrames", 0) or 0,
        "first_hit": script.get("FirstHitboxFrame", 0) or 0,
        "last_hit": script.get("LastHitboxFrame", 0) or 0,
        "iasa": script.get("IASAFrame", 0) or 0,
    }


def hitbox_commands(script):
    """HITBOX command list of a BAC script (may be missing)."""
    if not isinstance(script, dict):
        return []
    cmds = script.get("CommandLists", {}) or {}
    return cmds.get("HITBOX", []) or []


def hitbox_damage(script, hitbox_table):
    """Max standing-hit damage/stun across the script's HITBOX commands.

    Each HITBOX command's HitboxData indexes the HitboxTable; entry [0] is
    HIT_STANDING. Returns (damage, stun, hitbox_type, hit_level) or Nones.
    """
    best = None
    for cmd in hitbox_commands(script):
        idx = cmd.get("HitboxData")
        if idx is None:
            continue
        entry = (hitbox_table or {}).get(str(idx)) or (hitbox_table or {}).get(idx)
        if not isinstance(entry, dict):
            continue
        standing = entry.get("0") or {}
        if not isinstance(standing, dict):
            continue
        dmg = standing.get("Damage", 0) or 0
        if best is None or dmg > best[0]:
            best = (dmg, standing.get("Stun", 0) or 0,
                    cmd.get("Type"), cmd.get("HitLevel"))
    return best if best else (None, None, None, None)


def guess_limb(move_name, script_name, hit_type, button_value):
    """Best-effort limb from names + buttons; honest fallback is armL."""
    text = ("%s %s" % (move_name, script_name or "")).lower()
    if "kick" in text or "knee" in text or "foot" in text or "leg" in text:
        return "legR"
    if "punch" in text or "palm" in text or "elbow" in text or "fist" in text \
            or "chop" in text or "slap" in text:
        return "armR"
    # Button fallback: any K button -> leg, else arm.
    if button_value & 0xE00:
        return "legR"
    return "armR"


def move_class_for(hit_type, has_hitbox, move_name):
    if hit_type == "GRAB":
        return "throw"
    if hit_type == "PROJECTILE":
        return "projectile"
    if has_hitbox:
        return "strike"
    text = (move_name or "").lower()
    if any(w in text for w in ("dash", "walk", "jump", "taunt", "focus", "stance")):
        return "movement"
    return "other"


def convert_char(combined):
    """Convert one combined bac/bcm JSON dict -> WH moveset JSON dict."""
    game = combined.get("game", "SFIV")
    char = combined.get("character", "unknown")
    prefix = GAME_PREFIX.get(game, "sf4")
    bac = combined.get("bac", {}) or {}
    bcm = combined.get("bcm", {}) or {}
    scripts = bac.get("Scripts", {}) or {}
    hitbox_table = bac.get("HitboxTable", {}) or {}
    moves = bcm.get("Moves", {}) or {}
    cancel_lists = bcm.get("CancelLists", {}) or {}

    fighter_id = "%s-%s" % (prefix, char.lower())
    out = {
        "fighter": fighter_id,
        "display": "%s (%s)" % (char.upper(), GAME_DISPLAY.get(game, game)),
        "sf_source": "%s — bac/bcm extracted from real game files via "
                     "dantarion/sf4tools (see teardown/street-fighter-4/)" % game,
        "sf_character": char,
        "sf_game": game,
        "schema_version": 2,
        "moves": {},
    }

    used_keys = {}
    for move_name, move in moves.items():
        if not isinstance(move, dict):
            continue
        script_name = move.get("Script")
        script = scripts.get(script_name) if isinstance(script_name, str) else None
        frames = script_frame_data(script)
        wh_input, notes = wh_input_for_move(move)
        dmg, stun, hit_type, hit_level = hitbox_damage(script, hitbox_table)
        has_hitbox = len(hitbox_commands(script)) > 0
        raw_value = parse_flag_hex(move.get("Input", ""))
        heavy = bool(raw_value & 0x100) or bool(raw_value & 0x800)  # HP or HK

        if frames and frames["total"]:
            startup = round(frames["first_hit"] / FPS, 3) if frames["first_hit"] else 0.0
            active = round(max(1, frames["last_hit"] - frames["first_hit"] + 1) / FPS, 3) \
                if frames["last_hit"] >= frames["first_hit"] and frames["first_hit"] else 0.033
            recovery = round(max(0, frames["total"] - frames["last_hit"]) / FPS, 3) \
                if frames["last_hit"] else round(frames["total"] / FPS, 3)
        else:
            startup, active, recovery = 0.0, 0.033, 0.0
            notes.append("no BAC script frames (script=%s)" % (script_name,))

        # Key by WH input; disambiguate close/far/EX twins.
        key = wh_input if wh_input else move_name
        if key in used_keys:
            restr = flag_names(move.get("PositionRestriction", ""))
            suffix = (" " + restr) if restr and restr != "NONE" else ""
            if not suffix and move.get("EXCost"):
                suffix = " EX"
            key = (wh_input if wh_input else move_name) + suffix
            n = 2
            while key in used_keys:
                key = "%s#%d" % (key, n)
                n += 1
        used_keys[key] = move_name

        note_bits = []
        note_bits.append("SF script %s; total %dF IASA %dF" % (
            script_name, frames["total"] if frames else 0,
            frames["iasa"] if frames else 0))
        if move.get("EXCost"):
            note_bits.append("EX cost %s" % move.get("EXCost"))
        if move.get("UltraCost"):
            note_bits.append("Ultra cost %s" % move.get("UltraCost"))
        if stun:
            note_bits.append("stun %s" % stun)
        if hit_level:
            note_bits.append("hit level %s" % hit_level)
        note_bits.extend(notes)
        # Cancels: which cancel lists reference this move's script.
        cancels = [lname for lname, members in cancel_lists.items()
                   if isinstance(members, list) and move_name in members]
        if cancels:
            note_bits.append("in cancel lists: %s" % ", ".join(cancels))

        out["moves"][key] = {
            "name": "%s %s" % (char.upper(), move_name),
            "input": wh_input or key,
            "sf_move": move_name,
            "sf_script": script_name if isinstance(script_name, str) else None,
            "sf_input_motion": move.get("InputMotion"),
            "startup": startup,
            "active": active,
            "recovery": recovery,
            "damage": int(dmg) if dmg is not None else 0,
            "limb": guess_limb(move_name, script_name, hit_type, raw_value),
            "heavy": heavy,
            "knock": 2.2,
            "soulGain": 8,
            "anim_ref": "%s:%s/%s" % (prefix, char.lower(), script_name)
                        if isinstance(script_name, str) else None,
            "input_slots": [wh_input] if wh_input else [],
            "move_class": move_class_for(hit_type, has_hitbox, move_name),
            "note": "; ".join(note_bits) + " (knock/soulGain are WH defaults, "
                    "not from source; animation clip extraction (.anm) still owed)",
        }

    out["move_count_source"] = len(moves)
    out["move_count_converted"] = len(out["moves"])
    return out


def convert_file(in_path, out_dir):
    with open(in_path) as f:
        combined = json.load(f)
    result = convert_char(combined)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "%s-%s.json" % (
        GAME_PREFIX.get(combined.get("game", "SFIV"), "sf4"),
        combined.get("character", "unknown").lower()))
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print("%s -> %s (%d moves)" % (
        in_path, out_path, result["move_count_converted"]))
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="*", help="combined char JSON file(s)")
    ap.add_argument("--dir", dest="indir", help="directory of combined JSONs")
    ap.add_argument("--sfxt-dir", dest="sfxtdir",
                    help="directory of sfxt-parsed JSONs (from sfxt_bcm.py); "
                         "converts SFxT .sfxt-bcm.json + .sfxt-bac.json pairs")
    ap.add_argument("--sfiv-dir", dest="sfivdir",
                    help="directory of sfiv-parsed JSONs (from sfiv_bac_bcm.py); "
                         "converts vanilla SFIV carved .sfiv-bcm.json + "
                         ".sfiv-bac.json pairs (char = parent dir name)")
    ap.add_argument("--out", dest="outdir", required=True,
                    help="output directory for WH moveset JSONs")
    args = ap.parse_args(argv)
    if args.sfxtdir:
        convert_sfxt_dir(args.sfxtdir, args.outdir)
        return
    if args.sfivdir:
        convert_sfiv_dir(args.sfivdir, args.outdir)
        return
    paths = list(args.inputs)
    if args.indir:
        paths += sorted(os.path.join(args.indir, fn)
                        for fn in os.listdir(args.indir)
                        if fn.endswith(".json") and fn != "sfiv-manifest.json"
                        and "manifest" not in fn)
    if not paths:
        ap.error("no input files given")
    for p in paths:
        convert_file(p, args.outdir)


# ---------------------------------------------------------------------------
# SFxT mode (sfxt-parsed JSON from sfxt_bcm.py).
#
# Everything here is grounded in the verified SFxT layout (see sfxt_bcm.py):
# - input_bits: LP=0x10, MP=0x20, HP=0x40, LK=0x80, MK=0x100, HK=0x200;
#   down=0x02, back=0x04, fwd=0x08, up=0x01 (up is INFERRED from the bit
#   pattern — no move observed with it; flagged where used).
# - position_restriction: 2 = standing, 1 = forward, 0 = any/crouch/air.
# - move_flags bit 0x5000-ish marks specials (0x5010/0x5020/0x5030).
# - Motion linkage is by MOVE-NAME prefix only (SYORYU_* -> SYORYU etc.);
#   motion -> WH steps only where the final-direction flag in the motion
#   record corroborates it (HADO ends fwd=QCF, SYORYU ends fwd+down=DP,
#   TATSUMAKI ends back=QCB, R_SYORYU ends back+down=RDP). YOGA/R_YOGA,
#   PANDORA, DASH, throws, SOKUTOU, SC_* stay UNMAPPED (note names the
#   candidate where one exists, never asserts it).
# - Script linkage is by NAME only (move base name -> script <base>1,
#   TC_ prefix stripped). Frame data and damage are NOT available: SFxT BAC
#   script bodies are not yet decoded, so startup/active/recovery/damage
#   are placeholders with an explicit pending note. Nothing is invented.
# ---------------------------------------------------------------------------

SFXT_BUTTON_BITS = [
    (0x10, "LP"), (0x20, "MP"), (0x40, "HP"),
    (0x80, "LK"), (0x100, "MK"), (0x200, "HK"),
]
SFXT_DIR_BITS = [(0x01, "u"), (0x02, "d"), (0x04, "b"), (0x08, "f")]
SFXT_BUTTON_TO_WH = {"LP": "1", "MP": "2", "HP": "1+2",
                     "LK": "3", "MK": "4", "HK": "3+4"}

# Motion name -> WH direction steps. Only the four corroborated by the
# motion record's final-direction flag (see sfxt_bcm.py docstring).
SFXT_MOTION_STEPS = {
    "HADO": ["d", "d/f", "f"],       # ends fwd (flag 8)
    "SYORYU": ["f", "d", "d/f"],     # ends fwd+down (flag 10)
    "TATSUMAKI": ["d", "d/b", "b"],  # ends back (flag 4)
    "R_SYORYU": ["b", "d", "d/b"],   # ends back+down (flag 6)
}

# Move-name prefix -> motion name (name linkage only).
SFXT_MOVE_MOTION = [
    ("SYORYU_", "SYORYU"), ("TATSUMAKI_", "TATSUMAKI"),
    ("AIR_TATSUMAKI_", "TATSUMAKI"), ("FA_TATUMAKI_", "TATSUMAKI"),
    ("DASH", "DASH"), ("BACKDASH", "BACKDASH"),
    ("THROW_F", "FRONT_THROW"), ("THROW_B", "BACK_THROW"),
]


def sfxt_motion_for_move(move_name, motions_by_name):
    """Return (steps_or_None, motion_name_or_None, note_or_None)."""
    for prefix, motion in SFXT_MOVE_MOTION:
        if move_name == prefix or move_name.startswith(prefix):
            if motion not in motions_by_name:
                return None, motion, "motion '%s' not in this file" % motion
            steps = SFXT_MOTION_STEPS.get(motion)
            if steps is None:
                return None, motion, "motion '%s' has no verified WH steps" % motion
            return steps, motion, None
    return None, None, None


def sfxt_script_for_move(move_name, scripts_by_base):
    """Name-based script link: strip TC_, match <base>1/<base> (any suffix)."""
    base = move_name[3:] if move_name.startswith("TC_") else move_name
    if base in scripts_by_base:
        return scripts_by_base[base]
    return None


def sfxt_wh_input(move, motion_steps):
    """WH input string from SFxT input_bits + position_restriction + name."""
    bits = move.get("input_bits", 0) or 0
    dirs = [tok for bit, tok in SFXT_DIR_BITS if bits & bit]
    order = {"u": 0, "d": 0, "b": 1, "f": 1}
    dirs.sort(key=lambda t: order[t])
    dir_tok = "/".join(dirs)
    btns = [SFXT_BUTTON_TO_WH[nm] for b, nm in SFXT_BUTTON_BITS if bits & b]
    btn_list = []
    for token in btns:
        for b in token.split("+"):
            if b not in btn_list:
                btn_list.append(b)
    btn_list.sort(key=int)
    btn_tok = "+".join(btn_list)
    notes = []
    if not dir_tok:
        # Position restriction carries the forward variant (5LPF: pos 1).
        if move.get("position_restriction") == 1:
            dir_tok = "f"
        else:
            # Jump/crouch direction lives in the move name (8LP, 9MP, 2LP).
            name = move.get("name", "")
            if name.startswith("9"):
                dir_tok = "u/f"
                notes.append("jump direction from move name (9 = u/f)")
            elif name.startswith("8"):
                dir_tok = "u"
                notes.append("jump direction from move name (8 = u)")
            elif name.startswith("2"):
                dir_tok = "d"
                notes.append("crouch direction from move name (2 = d)")
    if motion_steps:
        seq = ",".join(motion_steps[:-1] +
                       [motion_steps[-1] + ("+" + btn_tok if btn_tok else "")])
        return seq, notes
    if dir_tok and btn_tok:
        return "%s+%s" % (dir_tok, btn_tok), notes
    if btn_tok:
        return btn_tok, notes
    if dir_tok:
        return dir_tok, notes
    return "", notes


def convert_sfxt_char(bcm, bac):
    """Convert one SFxT character's parsed JSONs -> WH moveset JSON dict."""
    char = bcm.get("file", "unknown").rsplit(".", 1)[0].upper()
    scripts = bac.get("scripts", []) if bac else []
    scripts_by_base = {}
    for s in scripts:
        name = s.get("name", "")
        if not name:
            continue
        base = re.sub(r"\d+$", "", name)
        scripts_by_base.setdefault(base, name)
        scripts_by_base.setdefault(name, name)
    motions_by_name = {m["name"]: m for m in bcm.get("input_motions", [])}
    fighter_id = "sfxt-%s" % char.lower()
    out = {
        "fighter": fighter_id,
        "display": "%s (SFxT)" % char,
        "sf_source": "SFxT — bac/bcm extracted from real game files "
                     "(Street Fighter X Tekken PC) via lane-1b sfxt_bcm.py; "
                     "see teardown/street-fighter-4/",
        "sf_character": char,
        "sf_game": "SFxT",
        "schema_version": 2,
        "moves": {},
    }
    used_keys = {}
    for move in bcm.get("moves", []):
        move_name = move.get("name", "")
        if not move_name:
            continue
        steps, motion_name, motion_note = sfxt_motion_for_move(
            move_name, motions_by_name)
        wh_input, notes = sfxt_wh_input(move, steps)
        if motion_note:
            notes.append(motion_note)
        script_name = sfxt_script_for_move(move_name, scripts_by_base)
        bits = move.get("input_bits", 0) or 0
        heavy = bool(bits & 0x40) or bool(bits & 0x200)  # HP or HK
        limb = "legR" if bits & 0x380 else "armR"  # any K bit
        is_tc = move_name.startswith("TC_")
        if "EX" in move_name.split("_"):
            notes.append("EX variant (EX cost not decoded from SFxT BCM)")
        if script_name is None:
            notes.append("no BAC script linked by name "
                         "(script=%s)" % (move_name,))
        # Frame data + damage: pending BAC script-body decode (honest zeros).
        notes.append("BAC script body NOT yet decoded — startup/active/"
                     "recovery/damage are placeholders, pending the SFxT "
                     "script-body RE (see sfxt_bcm.py)")
        key = wh_input if wh_input else move_name
        if key in used_keys:
            suffix = " TC" if is_tc else ""
            if not suffix and move.get("position_restriction") == 1:
                suffix = " F"
            key = (wh_input if wh_input else move_name) + suffix
            n = 2
            while key in used_keys:
                key = "%s#%d" % (key, n)
                n += 1
        used_keys[key] = move_name
        if move_name.startswith("THROW_"):
            move_class = "throw"
        elif move_name in ("DASH", "BACKDASH", "FORWARD", "BACKWARD"):
            move_class = "movement"
        elif script_name:
            move_class = "strike"
        else:
            move_class = "other"
        note_bits = []
        note_bits.append("SFxT script %s" % (script_name or "unlinked"))
        if motion_name:
            note_bits.append("motion %s" % motion_name)
        note_bits.extend(notes)
        out["moves"][key] = {
            "name": "%s %s" % (char, move_name),
            "input": wh_input or key,
            "sf_move": move_name,
            "sf_script": script_name,
            "sf_input_motion": motion_name,
            "startup": 0.0,
            "active": 0.033,
            "recovery": 0.0,
            "damage": 0,
            "limb": limb,
            "heavy": heavy,
            "knock": 2.2,
            "soulGain": 8,
            "anim_ref": "sfxt:%s/%s" % (char.lower(), script_name)
                        if script_name else None,
            "input_slots": [wh_input] if wh_input else [],
            "move_class": move_class,
            "note": "; ".join(note_bits) + " (knock/soulGain are WH defaults, "
                    "not from source; frame data + damage pending SFxT "
                    "script-body decode; animation clip extraction (.anm) "
                    "still owed)",
        }
    out["move_count_source"] = len(bcm.get("moves", []))
    out["move_count_converted"] = len(out["moves"])
    out["moves_linked_to_script"] = sum(
        1 for m in out["moves"].values() if m.get("sf_script"))
    return out


def convert_sfxt_dir(parsed_dir, out_dir):
    """Convert every SFxT char pair under parsed_dir (resource/CMN first)."""
    os.makedirs(out_dir, exist_ok=True)
    pairs = {}
    skipped_patch = 0
    for root, _dirs, files in os.walk(parsed_dir):
        for fn in files:
            if not fn.endswith(".sfxt-bcm.json"):
                continue
            stem = fn[:-len(".sfxt-bcm.json")]
            bac_path = os.path.join(root, stem + ".sfxt-bac.json")
            if not os.path.exists(bac_path):
                print("SKIP %s: no .sfxt-bac.json pair" % fn)
                continue
            # Prefer the base resource set over balance-patch duplicates:
            # patch/regulation/{latest,v2,v3,v4} hold the SAME characters at
            # different balance patches. Keep resource, skip patch entirely.
            prio = 0 if "/resource/CMN/battle/chara/" in root.replace("\\", "/") \
                else 1
            if stem in pairs:
                if prio >= pairs[stem][0]:
                    skipped_patch += 1
                    continue
            pairs[stem] = (prio, os.path.join(root, fn), bac_path)
    done = 0
    for stem, (_prio, bcm_path, bac_path) in sorted(pairs.items()):
        with open(bcm_path) as f:
            bcm = json.load(f)
        with open(bac_path) as f:
            bac = json.load(f)
        result = convert_sfxt_char(bcm, bac)
        out_path = os.path.join(out_dir, "sfxt-%s.json" % stem.lower())
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print("%s -> %s (%d moves, %d linked to scripts)" % (
            stem, out_path, result["move_count_converted"],
            result["moves_linked_to_script"]))
        done += 1
    print("sfxt: converted %d characters (%d patch duplicates skipped)" % (
        done, skipped_patch))


# ---------------------------------------------------------------------------
# Vanilla SFIV mode (sfiv-parsed JSON from sfiv_bac_bcm.py).
#
# Grounded in the verified vanilla layout (see sfiv_bac_bcm.py):
# - Input bits use the AE layout (util.py): LP=0x40, MP=0x80, HP=0x100,
#   LK=0x200, MK=0x400, HK=0x800; up=0x02, down=0x04, back=0x08, fwd=0x10.
#   (Verified: 2LP=0x44=LP+down, 6MP=0x90=MP+fwd, THROW_F=LP+LK,
#   SAVING=MP+MK, EX specials = all-punch/all-kick chords.)
# - move_flags bit 0x3000 marks specials (0x3010/0x3020/0x3050).
# - Motion linkage is by MOVE-NAME prefix; steps only for the motions
#   corroborated in SFxT by record flags (same moves, same inputs):
#   HADOKEN->QCF, SYORYUKEN->DP, TATSUMAKI->QCB. SHINKU_HADOKEN->QCF,QCF
#   is the standard double-QCF super input (flagged as conventional).
#   FIRE_HADOKEN->QCF is flagged as the projectile motion (role unverified).
#   DASH/BACK_DASH/throws/SAVING/METU stay UNMAPPED (note names the facts).
# - Script linkage is by NAME with the game's own spelling normalizations
#   (the data itself misspells: move HADOLEN vs script HADOKEN, move
#   TATUMAKI_EX vs script TATSUMAKI_EX, move METU_HADOKEN vs script
#   METU_HADOUKEN). Rapid variants strip the R prefix (R5LP->5LP).
# - Frame data: the BAC header fields read sane at delta 0 (5LP: 9,12,26,32)
#   BUT the field order is UNVERIFIED against known frame data (a jab with
#   9f startup contradicts SFIV frame data) — so startup/active/recovery/
#   damage are placeholders with the raw header values quoted in the note,
#   pending the USFIV cross-check (AE format will settle the field order).
# ---------------------------------------------------------------------------

# Motion name -> WH direction steps (see header note above).
SFIV_MOTION_STEPS = {
    "HADOKEN": ["d", "d/f", "f"],
    "SYORYUKEN": ["f", "d", "d/f"],
    "TATSUMAKI": ["d", "d/b", "b"],
    "SHINKU_HADOKEN": ["d", "d/f", "f", "d", "d/f", "f"],
    "FIRE_HADOKEN": ["d", "d/f", "f"],
}

# Move-name prefix -> motion name (name linkage only).
SFIV_MOVE_MOTION = [
    ("SYORYUKEN_", "SYORYUKEN"), ("SYORYU_", "SYORYUKEN"),
    ("TATSUMAKI_", "TATSUMAKI"), ("TATUMAKI_", "TATSUMAKI"),
    ("AIR_TATSUMAKI_", "TATSUMAKI"), ("AIR_TATUMAKI_", "TATSUMAKI"),
    ("SHINKU_HADOLEN_", "SHINKU_HADOKEN"),
    ("SHINKU_HADOKEN_", "SHINKU_HADOKEN"),
    ("HADOLEN_", "HADOKEN"), ("HADOKEN_", "HADOKEN"),
    ("FIRE_HADOLEN", "FIRE_HADOKEN"),
    ("DASH", "DASH"), ("BACK_DASH", "BACK_DASH"),
]

# Script-name normalizations (the game's own spelling variants).
SFIV_SCRIPT_FIXES = [
    ("HADOLEN", "HADOKEN"),
    ("TATUMAKI", "TATSUMAKI"),
    ("METU_HADOKEN", "METU_HADOUKEN"),
]


def sfiv_motion_for_move(move_name, motions_by_name):
    for prefix, motion in SFIV_MOVE_MOTION:
        if move_name == prefix or move_name.startswith(prefix):
            if motion not in motions_by_name:
                return None, motion, "motion '%s' not in this file" % motion
            steps = SFIV_MOTION_STEPS.get(motion)
            if steps is None:
                return None, motion, "motion '%s' has no verified WH steps" % motion
            return steps, motion, None
    return None, None, None


def sfiv_script_for_move(move_name, scripts_by_name):
    base = move_name
    # Rapid variants strip the R prefix (R5LP -> 5LP).
    if re.match(r"^R[2589]", base):
        base = base[1:]
    if base in scripts_by_name:
        return scripts_by_name[base]
    # Only then try the game's spelling normalizations (HADOLEN vs HADOKEN,
    # TATUMAKI vs TATSUMAKI, METU_HADOKEN vs METU_HADOUKEN) — the exact
    # name wins first, because SHINKU_HADOLEN_L's script really is spelled
    # SHINKU_HADOLEN_L while HADOLEN_L's script is HADOKEN_L.
    fixed = base
    for wrong, right in SFIV_SCRIPT_FIXES:
        fixed = fixed.replace(wrong, right)
    if fixed in scripts_by_name:
        return scripts_by_name[fixed]
    # SAVING_EX -> EX_SAVING (reordered in the script table).
    if base == "SAVING_EX" and "EX_SAVING" in scripts_by_name:
        return "EX_SAVING"
    return None


def sfiv_wh_input(move, motion_steps):
    """WH input string from vanilla SFIV input_bits + position_restriction."""
    bits = move.get("input_bits", 0) or 0
    dirs = [tok for bit, tok in DIR_BITS if bits & bit]
    order = {"u": 0, "d": 0, "b": 1, "f": 1}
    dirs.sort(key=lambda t: order[t])
    dir_tok = "/".join(dirs)
    btns = [BUTTON_TO_WH[n] for bit, n in BUTTON_BITS if bits & bit]
    btn_list = []
    for token in btns:
        for b in token.split("+"):
            if b not in btn_list:
                btn_list.append(b)
    btn_list.sort(key=int)
    btn_tok = "+".join(btn_list)
    notes = []
    if not dir_tok:
        name = move.get("name", "")
        if name.startswith("9"):
            dir_tok = "u/f"
            notes.append("jump direction from move name (9 = u/f)")
        elif name.startswith("8"):
            dir_tok = "u"
            notes.append("jump direction from move name (8 = u)")
        elif name.startswith("2"):
            dir_tok = "d"
            notes.append("crouch direction from move name (2 = d)")
        elif move.get("position_restriction") == 1:
            dir_tok = "f"
    if motion_steps:
        seq = ",".join(motion_steps[:-1] +
                       [motion_steps[-1] + ("+" + btn_tok if btn_tok else "")])
        return seq, notes
    if dir_tok and btn_tok:
        return "%s+%s" % (dir_tok, btn_tok), notes
    if btn_tok:
        return btn_tok, notes
    if dir_tok:
        return dir_tok, notes
    return "", notes


def convert_sfiv_char(bcm, bac, char):
    """Convert one vanilla SFIV character's parsed JSONs -> WH moveset dict."""
    scripts_by_name = {}
    for s in bac.get("scripts", []):
        name = s.get("name", "")
        if name:
            scripts_by_name[name] = name
    motions_by_name = {m["name"]: m for m in bcm.get("input_motions", [])}
    script_headers = {s["name"]: s for s in bac.get("scripts", [])
                      if s.get("name")}
    fighter_id = "sf4-%s" % char.lower()
    out = {
        "fighter": fighter_id,
        "display": "%s (SFIV)" % char,
        "sf_source": "SFIV — bac/bcm carved from *.cmn.emz (zlib raw-deflate "
                     "after 16-byte header) in Street Fighter IV [Build 3584] "
                     "via lane-1b sfiv_bac_bcm.py; see teardown/street-fighter-4/",
        "sf_character": char,
        "sf_game": "SFIV",
        "schema_version": 2,
        "moves": {},
    }
    used_keys = {}
    for move in bcm.get("moves", []):
        move_name = move.get("name", "")
        if not move_name:
            continue
        steps, motion_name, motion_note = sfiv_motion_for_move(
            move_name, motions_by_name)
        wh_input, notes = sfiv_wh_input(move, steps)
        if motion_note:
            notes.append(motion_note)
        script_name = sfiv_script_for_move(move_name, scripts_by_name)
        bits = move.get("input_bits", 0) or 0
        heavy = bool(bits & 0x100) or bool(bits & 0x800)  # HP or HK
        limb = "legR" if bits & 0xE00 else "armR"  # any K bit
        is_rapid = bool(re.match(r"^R[2589]", move_name))
        if script_name is None:
            notes.append("no BAC script linked by name (script=%s)" % (move_name,))
        hdr = script_headers.get(script_name) if script_name else None
        if hdr:
            notes.append("BAC header raw first=%s last=%s iasa=%s total=%s "
                         "(field order UNVERIFIED against known frame data; "
                         "pending USFIV cross-check)" % (
                             hdr.get("first_hit"), hdr.get("last_hit"),
                             hdr.get("iasa"), hdr.get("total")))
        notes.append("BAC script body NOT yet decoded — startup/active/"
                     "recovery/damage are placeholders, pending the vanilla "
                     "script-body RE (see sfiv_bac_bcm.py)")
        key = wh_input if wh_input else move_name
        if key in used_keys:
            suffix = " R" if is_rapid else ""
            if not suffix and move.get("position_restriction") == 1:
                suffix = " F"
            key = (wh_input if wh_input else move_name) + suffix
            n = 2
            while key in used_keys:
                key = "%s#%d" % (key, n)
                n += 1
        used_keys[key] = move_name
        if move_name.startswith("THROW_"):
            move_class = "throw"
        elif move_name in ("DASH", "BACK_DASH"):
            move_class = "movement"
        elif script_name:
            move_class = "strike"
        else:
            move_class = "other"
        note_bits = []
        note_bits.append("SFIV script %s" % (script_name or "unlinked"))
        if motion_name:
            note_bits.append("motion %s" % motion_name)
        note_bits.extend(notes)
        out["moves"][key] = {
            "name": "%s %s" % (char, move_name),
            "input": wh_input or key,
            "sf_move": move_name,
            "sf_script": script_name,
            "sf_input_motion": motion_name,
            "startup": 0.0,
            "active": 0.033,
            "recovery": 0.0,
            "damage": 0,
            "limb": limb,
            "heavy": heavy,
            "knock": 2.2,
            "soulGain": 8,
            "anim_ref": "sf4:%s/%s" % (char.lower(), script_name)
                        if script_name else None,
            "input_slots": [wh_input] if wh_input else [],
            "move_class": move_class,
            "note": "; ".join(note_bits) + " (knock/soulGain are WH defaults, "
                    "not from source; frame data + damage pending vanilla "
                    "script-body decode; animation clip extraction (.anm) "
                    "still owed)",
        }
    out["move_count_source"] = len(bcm.get("moves", []))
    out["move_count_converted"] = len(out["moves"])
    out["moves_linked_to_script"] = sum(
        1 for m in out["moves"].values() if m.get("sf_script"))
    return out


def convert_sfiv_dir(parsed_dir, out_dir):
    """Convert every vanilla SFIV char pair under parsed_dir.

    Pairs live one per character directory (char = parent dir name);
    files are carved_0_0.sfiv-bac.json + carved_0_1.sfiv-bcm.json.
    """
    os.makedirs(out_dir, exist_ok=True)
    done = 0
    for root, _dirs, files in os.walk(parsed_dir):
        bcm_files = [f for f in files if f.endswith(".sfiv-bcm.json")]
        bac_files = [f for f in files if f.endswith(".sfiv-bac.json")]
        if not bcm_files or not bac_files:
            continue
        char = os.path.basename(root).upper()
        with open(os.path.join(root, bcm_files[0])) as f:
            bcm = json.load(f)
        with open(os.path.join(root, bac_files[0])) as f:
            bac = json.load(f)
        result = convert_sfiv_char(bcm, bac, char)
        out_path = os.path.join(out_dir, "sf4-%s.json" % char.lower())
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print("%s -> %s (%d moves, %d linked to scripts)" % (
            char, out_path, result["move_count_converted"],
            result["moves_linked_to_script"]))
        done += 1
    print("sfiv: converted %d characters" % done)


if __name__ == "__main__":
    main()
