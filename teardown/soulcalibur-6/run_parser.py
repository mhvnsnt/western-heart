#!/usr/bin/env python3
"""Lane 1C driver v2: run FottenSC/Scuffle's MovelistParser OFFLINE against the
vendored movelists/*.sc6_movelist dumps and emit per-fighter structured
move tables (JSON) for conversion into Western Heart moveset banks.

Uses the upstream parser as a library — no format guessing here.
Frame data comes from the parser's own Move.get_frame_data() (called in
move order so Throw rows resolve against the preceding attack, as the
parser's own last_attack state requires).
Run from the lane workdir; expects ./scuffle-upstream/ (extracted tarball).
Writes ./parsed/<fighter>.json
"""
import json, os, sys, time, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
# In-repo default: this script lives in teardown/soulcalibur-6/, the parser
# in tools/anim/scvi-scuffle/. Override with SCUFFLE_DIR when running
# from a lane workdir (where it is ./scuffle-upstream).
UP = os.environ.get("SCUFFLE_DIR",
                    os.path.join(HERE, "..", "..", "tools", "anim", "scvi-scuffle"))
sys.path.insert(0, UP)
os.chdir(UP)  # parser load_json() reads Data/... relative to cwd

import MovelistParser as mp  # noqa: E402

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    only = sys.argv[1:] or None
    outdir = os.path.join(HERE, "parsed")
    os.makedirs(outdir, exist_ok=True)
    files = sorted(f for f in os.listdir("movelists") if f.endswith(".sc6_movelist"))
    for fn in files:
        fighter = fn[:-len(".sc6_movelist")]
        if only and fighter not in only:
            continue
        path = os.path.join("movelists", fn)
        t0 = time.time()
        ml = mp.Movelist.from_file(path)
        moves_out = []
        n_attack_moves = 0
        for m in ml.all_moves:
            try:
                com = ml.get_command_by_move_id(m.move_id)
            except Exception:
                com = None
            if isinstance(com, (list, tuple)):
                com = ",".join(str(c) for c in com)
            elif com is not None:
                com = str(com)
            attacks = []
            for a in m.attacks:
                if a.__class__.__name__ == "Throw":
                    attacks.append({"kind": "throw",
                                    "damage": getattr(a, "damage", None)})
                    continue
                try:
                    import GameplayEnums as ge
                    hl = ge.HitLevel(a.hit_level).name
                except Exception:
                    hl = a.hit_level
                attacks.append({
                    "kind": "attack",
                    "hitbox": a.hitbox,
                    "hit_level": hl,
                    "hit_level_raw": a.hit_level,
                    "startup": a.startup,
                    "active_end": a.active,
                    "damage": a.damage,
                    "chip": int.from_bytes(a.bytes[0x3C:0x3E], "little"),
                    "block_stun": a.block_stun,
                    "hit_stun": a.hit_stun,
                    "counter_stun": a.counter_stun,
                    "hit_effect_raw": int.from_bytes(a.bytes[0x50:0x52], "little"),
                    "counter_effect_raw": int.from_bytes(a.bytes[0x52:0x54], "little"),
                    "hit_launch": str(getattr(a, "hit_launch", "")),
                    "counter_launch": str(getattr(a, "counter_launch", "")),
                    "physics_hit_normal": list(a.physics_hit_normal),
                    "physics_hit_launch": list(a.physics_hit_launch),
                    "physics_block": list(a.physics_block),
                })
            # Parser's own frame-data rows (startup+1 impact, active, recovery,
            # block/hit/counter advantage inputs, damage, hit level, notes).
            fd_rows = []
            if attacks:
                n_attack_moves += 1
                try:
                    for fd in m.get_frame_data():
                        fd_rows.append({
                            "move_id": fd.id,
                            "command_raw": fd.com,
                            "whiff_frames": fd.whiff,
                            "impact_frame": fd.imp,
                            "block_stun": fd.bstun,
                            "hit_launch": str(fd.hlaunch),
                            "hit_stun": fd.hstun,
                            "counter_launch": str(fd.claunch),
                            "counter_stun": fd.cstun,
                            "damage": fd.dam,
                            "attack_type": str(fd.attack_type),
                            "active_frames": fd.active,
                            "recovery_frames": fd.rec,
                            "notes": [str(x) for x in (fd.notes or [])],
                        })
                except Exception as e:
                    fd_rows = [{"error": "get_frame_data failed: %s" % e}]
            moves_out.append({
                "move_id": m.move_id,
                "animation_id": m.animation,
                "anim_start_frame": int.from_bytes(m.bytes[0x02:0x04], "little", signed=True),
                "anim_max_frame_override": int.from_bytes(m.bytes[0x04:0x06], "little"),
                "motion_multiplier": m.motion_multiplier,
                "speed_multiplier": m.speed_multiplier,
                "total_frames": m.total_frames,
                "attack_indexes": list(m.attack_indexes),
                "command_raw": com,
                "attacks": attacks,
                "frame_data": fd_rows,
            })
        rec = {
            "fighter": fighter,
            "source": "FottenSC/Scuffle movelists/" + fn,
            "source_sha256": sha256_file(path),
            "source_bytes": os.path.getsize(path),
            "parser": "FottenSC/Scuffle MovelistParser.py (MIT)",
            "move_count": len(ml.all_moves),
            "attack_count": len(ml.all_attacks),
            "throw_count": len(ml.all_throws),
            "attack_move_count": n_attack_moves,
            "moves": moves_out,
        }
        outp = os.path.join(outdir, fighter + ".json")
        with open(outp, "w") as f:
            json.dump(rec, f, indent=1)
        print(f"{fighter}: moves={len(ml.all_moves)} attacks={len(ml.all_attacks)} "
              f"throws={len(ml.all_throws)} attack_moves={n_attack_moves} "
              f"bytes={os.path.getsize(outp)} secs={time.time()-t0:.1f}", flush=True)

if __name__ == "__main__":
    main()
