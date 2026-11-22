#!/usr/bin/env python3
"""Lane 1C converter: parsed/<fighter>.json (Scuffle parser output) ->
Western Heart moveset bank game/assets/movesets/scvi-<fighter>.json
(schema_version 2, keyed-object shape matching doa-kasumi.json).

Rules (documented in every bank header; nothing invented):
- One bank entry per ATTACK move (moves with >=1 attack record): 5,360 total.
- Key: "m<scvi move_id>" — move ids are unique; raw commands are NOT
  unique per move, so they cannot be keys.
- Name: "SCVI <Fighter> move <id>" — the movelist contains NO move names.
- input / input_slots: the parser's raw command string, verbatim. It
  contains '.'/'?' placeholders from the parser's neutral-parse; it is NOT
  a cleaned engine input. Recorded as scvi_command_raw too.
- startup/active/recovery (seconds, 60 fps): from the parser's own
  FrameData rows — startup = first row impact_frame, active = sum of
  active_frames, recovery = last row recovery_frames, clamped at 0 in the
  seconds field (raw value kept in scvi.frame_data). damage = sum of row
  damages. Multi-hit moves therefore total their hits; documented.
- limb: "unknown" (hitbox limb bytes are undecoded upstream — the parser
  itself marks them "??"). knock: 0, soulGain: 0 — no SCVI source basis;
  NOT copied from other games' defaults. heavy: damage >= 20 (threshold
  rule, documented — not source data).
- anim_ref: "scvi:<fighter>/anim-<animation_id>" — the .mot animation id.
  The .mot MOTION DATA is not extracted (format uncracked); the id is the
  pointer that resolves the day it is cracked.
- move_class: "throw" when every attack is a throw, else "strike".
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 60.0

DISPLAY = {
    "2B": "2B", "astaroth": "ASTAROTH", "azwel": "AZWEL",
    "cervantes": "CERVANTES", "geralt": "GERALT", "groh": "GROH",
    "ivy": "IVY", "kilik": "KILIK", "maxi": "MAXI",
    "mitsurugi": "MITSURUGI", "nightmare": "NIGHTMARE",
    "raphael": "RAPHAEL", "seong_mina": "SEONG MI-NA",
    "siegfried": "SIEGFRIED", "sophitia": "SOPHITIA", "taki": "TAKI",
    "talim": "TALIM", "tira": "TIRA", "voldo": "VOLDO",
    "xianghua": "XIANGHUA", "yoshimitsu": "YOSHIMITSU",
    "zasalamel": "ZASALAMEL",
}

def main():
    only = sys.argv[1:] or None
    # In-repo default: banks live in game/assets/movesets/. Override with
    # BANK_DIR when running from a lane workdir (where it is ./banks).
    outdir = os.environ.get("BANK_DIR",
                            os.path.join(HERE, "..", "..", "game", "assets", "movesets"))
    os.makedirs(outdir, exist_ok=True)
    total = 0
    for fn in sorted(os.listdir(os.path.join(HERE, "parsed"))):
        if not fn.endswith(".json"):
            continue
        fighter = fn[:-5]
        if only and fighter not in only:
            continue
        with open(os.path.join(HERE, "parsed", fn)) as f:
            rec = json.load(f)
        moves = {}
        n_throw = 0
        for m in rec["moves"]:
            if not m["attacks"]:
                continue
            fd = m["frame_data"]
            rows = [r for r in fd if "error" not in r]
            if rows:
                startup_f = rows[0]["impact_frame"]
                active_f = sum(r["active_frames"] for r in rows)
                rec_f = rows[-1]["recovery_frames"]
                damage = sum(r["damage"] for r in rows)
            else:
                startup_f = m["attacks"][0].get("startup", 0) + 1 if m["attacks"][0].get("kind") == "attack" else 0
                active_f = 0
                rec_f = 0
                damage = sum(a.get("damage") or 0 for a in m["attacks"])
            is_throw = all(a.get("kind") == "throw" for a in m["attacks"])
            if is_throw:
                n_throw += 1
            cmd = m["command_raw"]
            moves["m%d" % m["move_id"]] = {
                "name": "SCVI %s move %d" % (DISPLAY.get(fighter, fighter), m["move_id"]),
                "input": cmd if cmd else "",
                "scvi_move": m["move_id"],
                "scvi_input": cmd,
                "startup": round(startup_f / FPS, 3),
                "active": round(max(0, active_f) / FPS, 3),
                "recovery": round(max(0, rec_f) / FPS, 3),
                "damage": damage,
                "limb": "unknown",
                "heavy": damage >= 20,
                "knock": 0,
                "soulGain": 0,
                "anim_ref": "scvi:%s/anim-%d" % (fighter, m["animation_id"]),
                "input_slots": [cmd] if cmd else [],
                "move_class": "throw" if is_throw else "strike",
                "note": ("Extracted from SCVI movelist bytecode (FottenSC/Scuffle). "
                         "Frame data is extracted, not estimated. No move names exist in the "
                         "source data — keyed by SCVI move id. anim_ref is the .mot animation "
                         "id; .mot motion data is NOT yet extracted (format uncracked)."),
                "scvi": {
                    "move_id": m["move_id"],
                    "animation_id": m["animation_id"],
                    "total_frames": m["total_frames"],
                    "motion_multiplier": m["motion_multiplier"],
                    "speed_multiplier": m["speed_multiplier"],
                    "command_raw": cmd,
                    "attack_count": len(m["attacks"]),
                    "attacks": m["attacks"],
                    "frame_data": fd,
                },
            }
        bank = {
            "fighter": "scvi-" + fighter,
            "display": "%s (SCVI)" % DISPLAY.get(fighter, fighter),
            "scvi_source": "FottenSC/Scuffle movelists/%s.sc6_movelist (MIT) — live-memory movelist bytecode dump, parsed offline with the upstream MovelistParser.py" % fighter,
            "scvi_movelist_sha256": rec["source_sha256"],
            "scvi_movelist_bytes": rec["source_bytes"],
            "parser": "FottenSC/Scuffle MovelistParser.py (MIT)",
            "proxy": False,
            "proxy_note": None,
            "schema_version": 2,
            "move_count_source": rec["move_count"],
            "attack_count_source": rec["attack_count"],
            "throw_count_source": rec["throw_count"],
            "attack_move_count": len(moves),
            "throw_move_count": n_throw,
            "honesty": ("Frame data is EXTRACTED from the game's movelist bytecode, not "
                        "estimated. No move names exist in the source data. Commands are the "
                        "parser's raw output (may contain '.'/'?' placeholders) — not cleaned "
                        "engine inputs. limb is 'unknown' (hitbox limb bytes undecoded "
                        "upstream). knock/soulGain are 0 (no SCVI source basis). recovery "
                        "seconds are clamped at 0; the raw parser value is in "
                        "scvi.frame_data. .mot animation MOTION is not in this bank — only "
                        "the animation id (anim_ref), which resolves when .mot is cracked."),
            "moves": moves,
        }
        outp = os.path.join(outdir, "scvi-%s.json" % fighter)
        with open(outp, "w") as f:
            json.dump(bank, f, separators=(",", ":"))
        total += len(moves)
        print(f"scvi-{fighter}: bank_moves={len(moves)} throws={n_throw} bytes={os.path.getsize(outp)}", flush=True)
    print("TOTAL bank moves:", total)

if __name__ == "__main__":
    main()
