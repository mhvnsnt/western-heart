#!/usr/bin/env python3
"""tools/anim/t3_bake_bank.py — bake one Tekken 3 divmot bank into a game bank folder (2026-10-23, Claude session).

Same pipeline as the 2026-10-20 remainder banks (docs/anim/T3-REMAINDER-BANKS-20261020.md), for the banks that
were never decoded (ogre, kuma, gon, law): nothing is authored, every frame comes from the owner's disc.

  1. lab/tools/t3_motion_bake.py bakes the bank onto the character's own 18-part T3 rig
     (lab/game/assets/t3body_<bank>.glb from tools/anim/t3_extract_bodies.py) -> lab/game/assets/t3_<bank>_t3real.glb
     with the 26 universal move-index slots the shipped banks use (stance, walks, dashes, jumps, sidesteps,
     block, hit, ko, wins) plus light / medium / heavy picked from the bank's own decoded move table.
  2. Each clip is re-encoded to the shipped wh-anim/1 layout: the WH-Canonical-22 bone list, with Spine, Neck
     and the toes (bones the T3 rig lacks) as identity rotations, exactly like game/assets/anim/t3/anna/.
     t3_grab.json = t3_heavy.json, the convention of every shipped bank.

Light/medium/heavy rule (from teardown/tekken3/movesets/moveset_<bank>.json; universal-slot rows excluded):
  light  = the common 12-damage jab (attack word 0x010f, 44 frames), else the 0x010f 8-14 damage strike that
           comes out first;  medium = a 25-damage non-common strike of 50-70 frames, active frame nearest 23;
  heavy  = a 33-40 damage tagged power move of <= 100 frames, damage nearest 35, else the hardest strike.
  On the shipped banks this reproduces light 4/4 (anna, paul, hwoarang, bosconovitch) and heavy 3/4.

Usage (T3REMAKE_RESEARCH = n0madic/Tekken3Remake tools/research, as for t3_motion_bake.py):
  python3 tools/anim/t3_bake_bank.py ogre [kuma gon law]
Then: tools/anim/t3_bank_skeleton.py (skeleton.json) and tools/anim/t3_row_bake.py --bank <b> (rows.pack.json).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "teardown/tekken3/tools/local"))
sys.path.insert(0, os.environ.get("T3REMAKE_RESEARCH", "/workspace/t3anim/t3r/tools/research"))
import motion  # noqa: E402

UNIV = {"t3_stance": 0x0, "t3_stance_b": 0x1, "t3_stance_c": 0x2, "t3_neutral": 0x3, "t3_walk_fwd": 0x15,
        "t3_walk_back": 0x18, "t3_dash_fwd": 0x1b, "t3_backdash": 0x1e, "t3_crouch_hold": 0x28, "t3_crouch": 0x3b,
        "t3_jump_up": 0x7f, "t3_jump_fwd": 0x81, "t3_jump_back": 0x83, "t3_sidestep_a": 0x11b,
        "t3_sidestep_b": 0x11d, "t3_sidestep_c": 0x11f, "t3_sidestep_d": 0x121, "t3_hit": 0x9a2,
        "t3_hit_launch": 0x9fc, "t3_block": 0xa85, "t3_block_b": 0xa91, "t3_ko": 0xd66,
        "t3_win_lp": 0xd67, "t3_win_rp": 0xd68, "t3_win_lk": 0xd69, "t3_win_rk": 0xd6a}
CANON22 = ["Root", "Hips", "Spine", "Chest", "Neck", "Head", "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
           "RightShoulder", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot",
           "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"]
DIVMOT = {"ogre": "divmot14_ogre", "kuma": "divmot11_kuma", "gon": "divmot19_gon", "law": "divmot01_law"}
NOTES = {
    "root_t_note": "Sampled at the 30fps clip grid. t3anims.js ignores root_t (game drives root.position).",
    "stream_frames_note": "Count of stored rot_xyzw frames at 30fps. The King bank's stream_frames counts the 60fps "
                          "source motion stream (2x its stored rot frames); t3anims.js derives playback length from "
                          "the rot arrays + fps, so both conventions play identically.",
}


def attack_picks(bank):
    mb = motion.parse_bank((REPO / f"teardown/tekken3/animations/{DIVMOT[bank]}.bin").read_bytes())
    mi = mb.move_index
    univ_rows = {mi[s] for s in UNIV.values() if s < len(mi)}
    slot_of = {}
    for s, r in enumerate(mi):
        if r < motion.COMMON_FLAG and s not in UNIV.values():
            slot_of.setdefault(r, s)
    moves = json.load(open(REPO / f"teardown/tekken3/movesets/moveset_{bank}.json"))["moves"]
    mv = [m for m in moves if m["row"] in slot_of and m["row"] not in univ_rows and m["attack_class"] == 0]

    def first(cands, key):
        c = sorted(cands, key=key)
        return c[0]["row"] if c else None
    light = first([m for m in mv if m["damage"] == 12 and m["attack_word"] == "0x010f" and m["stream_frames"] == 44],
                  lambda m: m["row"]) or \
        first([m for m in mv if m["attack_word"] == "0x010f" and 8 <= m["damage"] <= 14],
              lambda m: (m["active_first"], m["row"]))
    medium = first([m for m in mv if m["damage"] == 25 and not m["common_anim"] and 50 <= m["stream_frames"] <= 70],
                   lambda m: (abs(m["active_first"] - 23), m["row"])) or \
        first([m for m in mv if 20 <= m["damage"] <= 28 and m["stream_frames"] <= 70],
              lambda m: (abs(m["damage"] - 25), m["row"]))
    heavy = first([m for m in mv if 33 <= m["damage"] <= 40 and m["anim_tag"] > 0 and not m["common_anim"]
                   and m["stream_frames"] <= 100], lambda m: (abs(m["damage"] - 35), m["row"])) or \
        first([m for m in mv if m["damage"] >= 28 and m["stream_frames"] <= 120], lambda m: (-m["damage"], m["row"]))
    return {"t3_light": slot_of[light], "t3_medium": slot_of[medium], "t3_heavy": slot_of[heavy]}


def bake(bank):
    rig_in = REPO / f"lab/game/assets/t3body_{bank}.glb"
    rig_out = REPO / f"lab/game/assets/t3_{bank}_t3real.glb"
    out_dir = REPO / f"game/assets/anim/t3/{bank}"
    clips = dict(UNIV, **attack_picks(bank))
    tmp = Path(tempfile.mkdtemp(prefix=f"t3bake-{bank}-"))
    spec = ",".join(f"{k}={hex(v)}" for k, v in clips.items())
    r = subprocess.run([sys.executable, str(REPO / "lab/tools/t3_motion_bake.py"), str(rig_in), str(rig_out),
                        "--bank", bank, "--clips", spec, "--json-dir", str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{bank}: t3_motion_bake failed\n{r.stderr[-2000:]}")
    report = json.loads(r.stdout[r.stdout.find("{"):])
    out_dir.mkdir(parents=True, exist_ok=True)
    import hashlib
    glb_sha = hashlib.sha256(rig_out.read_bytes()).hexdigest()
    written = []
    for name in clips:
        src = tmp / f"{name}.json"
        if not src.exists():
            print(f"{bank}: {name} not baked: {report.get(name)}")
            continue
        d = json.load(open(src))
        n = len(next(iter(d["rot_xyzw"].values())))
        rot = {b: d["rot_xyzw"].get(b) or [[0.0, 0.0, 0.0, 1.0]] * n for b in CANON22}
        out = {k: v for k, v in d.items() if k not in ("bones", "rot_xyzw")}
        out.update(bones=CANON22, rot_xyzw=rot, source_glb=str(rig_out.relative_to(REPO)), source_glb_sha256=glb_sha,
                   **NOTES)
        json.dump(out, open(out_dir / f"{name}.json", "w"), separators=(",", ":"))
        written.append(name)
    if (out_dir / "t3_heavy.json").exists():
        shutil.copyfile(out_dir / "t3_heavy.json", out_dir / "t3_grab.json")
        written.append("t3_grab")
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"bank": bank, "clips": len(written), "picks": {k: hex(clips[k]) for k in ("t3_light", "t3_medium", "t3_heavy")},
                      "missing": sorted(set(clips) - set(written))}))


if __name__ == "__main__":
    for b in sys.argv[1:]:
        bake(b)
