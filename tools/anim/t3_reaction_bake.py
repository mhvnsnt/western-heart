#!/usr/bin/env python3
"""Bake the Tekken 3 reaction, throw-victim and thrower clips of one runtime bank (lane E, 2026-10-24).

  game/assets/anim/t3/<dir>/reactions.pack.json   (format wh-anim-pack/1, the rows.pack.json layout)

Which slots: tools/anim/t3_reaction_tables.py (bank_plan) -- every move slot this bank DEFINES (own row or
divmot99 common row) that a hit, guard, air kind, KO collapse, throw victim, throw or default continuation can
start on a fighter using this bank. Slots the bank does not define are not baked here: the game fills them from
the opponent's bank (DivmotMergeSharedSlots), so they live in that bank's pack (contract: docs/anim/T3-REACTIONS.md).

Same unchanged pipeline as tools/anim/t3_row_bake.py: lab/tools/t3_motion_bake.py T3Space + sample_clip
(teardown/tekken3/tools/local/pose_assemble.py, bit-exact USA decode, divmot99 rows and streams included) +
TargetRig/retarget onto the same body KMD, stance and target rig as the bank's rows.pack.json (SHA-256 checked).
Re-encoded to the WH-Canonical-22 bone list (t3_bake_bank.CANON22); joints the 18-part T3 rigs lack (Spine, Neck,
toes) are identity, and local rotations are relative to the parents in the bank's skeleton.json, exactly like the
shipped wh-anim/1 bank clips. Nothing is authored. Extra per-clip tracks for the shared-frame throw contract:
  ax, ay, az  decoded root channels 0-2 (AnimDecodeRoot) in mm, in the move's heading frame converted like the
              bake (+Z forward, +Y up, +X = the T3 +x side, which the bake names Left): the root's offset from
              the move anchor. A throw anchors both fighters at the victim's root (combat.md "Throws").
  yaw0        radians: frame 0's Hips yaw in that heading frame -- the yaw retarget() normalises away (it turns
              every clip's first frame to +Z). A throw pair needs it to face each other in the shared frame.

Usage (T3REMAKE_RESEARCH = n0madic/Tekken3Remake tools/research):
  python3 tools/anim/t3_reaction_bake.py --bank paul [--bank anna ...] | --all [--limit N] [--merge]
"""
import argparse
import base64
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools/anim"))
sys.argv, _argv = sys.argv[:1], sys.argv   # t3_row_bake parses nothing at import; keep argv for us
import t3_row_bake as RB  # noqa: E402  (sets up lab/tools/t3_motion_bake + the BODY-EXTRACTION bodies)
import t3_reaction_tables as RT  # noqa: E402
sys.argv = _argv
TB = RB.TB
CANON22 = ["Root", "Hips", "Spine", "Chest", "Neck", "Head", "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
           "RightShoulder", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot",
           "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"]   # == t3_bake_bank.CANON22
T3DIR = REPO / "game/assets/anim/t3"

# runtime folder -> (motion key in t3_row_bake / t3_motion_bake BANKS, body key) -- the rows.pack.json recipe
DIR_CFG = {d: (d, d) for d in RT.BANK_DIRS}
DIR_CFG.update({"heihachi_on_jin": ("heihachi", "jin"), "king_on_pantera_leoman": ("king", "king"),
                "forestlaw_on_law": ("forestlaw", "forestlaw"), "heihachi": ("heihachi", "heihachi_own")})


def b64_i16(a):
    return base64.b64encode(np.ascontiguousarray(a, dtype="<i2").tobytes()).decode()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def inputs(d):
    """(kmd, stance, bank, target rig) for a runtime folder, cross-checked against its rows.pack.json."""
    motion_key, body = DIR_CFG[d]
    bank = REPO / "teardown/tekken3/animations" / f"{RT.BANK_DIRS[d]}.bin"
    pack = T3DIR / d / "rows.pack.json"
    if body == "heihachi_own":
        # heihachi/ = the own-rig divmot13 decode (t3anims.js T3_BANKS.heihachi_ownrig): Heihachi's own disc body
        # from tools/anim/t3_extract_bodies.py (BODY-EXTRACTION.json), onto the rig its skeleton.json names.
        e = json.loads((REPO / "teardown/tekken3/BODY-EXTRACTION.json").read_text())["heihachi"]
        kmd, stance = REPO / e["kmd"], REPO / e["stance_obj"]
        rig = json.loads((T3DIR / d / "skeleton.json").read_text())["source_glb"]
    else:
        kmd, _, stance = (TB.T3 / x for x in TB.BANKS[body])
        rig = RB.TARGET_GLB[body]
    if pack.exists():
        pk = json.loads(pack.read_text())
        legacy = f"teardown/tekken3/models/{body}/{body}.kmd"
        if pk["body_kmd"] != str(kmd.relative_to(REPO)) and pk["body_kmd"] == legacy:
            # rows.pack.json predates the BODY-EXTRACTION override (bosconovitch): keep its recipe, i.e. the
            # original t3_motion_bake remainder-bank body (models/<n>/<n>.kmd + pose-check <n>_stance75.obj)
            kmd, stance = REPO / legacy, TB.T3 / f"renders/pose-check/{body}_stance75.obj"
            rig = pk["target_rig"]
        if pk["target_rig"] != rig or pk["body_kmd"] != str(kmd.relative_to(REPO)) or pk["bank"] != str(bank.relative_to(REPO)):
            sys.exit(f"{d}: inputs differ from rows.pack.json ({pk['bank']}, {pk['body_kmd']}, {pk['target_rig']})")
        for p in (kmd, bank, REPO / rig):
            if p.name in pk["sha256"] and pk["sha256"][p.name] != sha(p):
                sys.exit(f"{d}: {p.name} SHA-256 differs from the one rows.pack.json was baked from")
    return kmd, stance, bank, rig


def root_channels(bank_path, slot, step):
    """Decoded root channels 0-2 of the slot's stream at the frames sample_clip samples (pose_assemble's path)."""
    mb = TB.motion.parse_bank(bank_path.read_bytes())
    cp = bank_path.with_name("divmot99_common.bin")
    row = mb.move_index[slot]
    rb = TB.motion.parse_bank(cp.read_bytes()) if row >= TB.motion.COMMON_FLAG else mb
    w = rb.move_row(row % TB.motion.COMMON_FLAG)[0]
    ab = TB.motion.parse_bank(cp.read_bytes()) if w >= TB.motion.COMMON_FLAG else rb
    st = TB.motion.parse_anim(ab.data, ab.anim_offset(w % TB.motion.COMMON_FLAG))
    tab = TB.PA.usa_motion.UsaSplineTables(TB.usa_tables.EXE_PATH.read_bytes())
    return np.array([TB.PA.usa_motion.sample_pose(st, f, tab)[:3] for f in range(0, st.frames, step)], float)


def heading_yaw(rig, space, clip):
    """Frame 0's Hips yaw in the heading frame: inverse of the normalisation retarget() applies."""
    f0 = clip["frames"][0]
    if "Hips" not in f0:
        return None
    if rig.has("LeftArm") and rig.has("RightArm") and rig.p("LeftArm")[0] < rig.p("RightArm")[0]:
        return None     # Mixamo-facing rig (retarget's F); not used by any bank
    fw = f0["Hips"][0] @ np.array([0, 0, 1.0])
    y0 = math.atan2(fw[0], fw[2])
    c, s = math.cos(-y0), math.sin(-y0)
    used = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    corr = space.Ry.T @ used.T          # heading-frame orientation = corr . normalised orientation
    return math.atan2(corr[0, 2], corr[2, 2])


def bake(d, limit=None, merge=False):
    kmd, stance, bank_path, rig_path = inputs(d)
    bank, common, want = RT.bank_plan(d)
    space = TB.T3Space(kmd, stance)
    rig = TB.TargetRig(REPO / rig_path)
    hip0 = {space.name[p]: v for p, v in space.P.items()}["Hips"]
    scale = rig.p("Hips")[1] / max(hip0[1], 1e-6)
    shas = {p.name: sha(p) for p in (kmd, bank_path, bank_path.with_name("divmot99_common.bin"), TB.usa_tables.EXE_PATH,
                                     REPO / rig_path)}
    out = {"format": "wh-anim-pack/1", "kind": "t3-reactions", "bank": str(bank_path.relative_to(REPO)),
           "body_kmd": str(kmd.relative_to(REPO)), "stance": str(stance.relative_to(REPO)), "target_rig": rig_path,
           "skeleton": f"game/assets/anim/t3/{d}/skeleton.json", "bones": CANON22, "fps": None, "hand_keyed": False,
           "keys": "rows are keyed by MOVE SLOT (hex), not by bank row: reaction records, throw-victim entries and "
                   "air kinds name slots. rec.move_row = bank row, or 0x40000000 + divmot99 row (rec.src).",
           "bones_note": "WH-Canonical-22 names; joints the source rig lacks are identity. Local rotations are relative "
                         "to the parents in skeleton.json (the 18-part T3 rigs hang Chest off Root), as for the "
                         "shipped wh-anim/1 bank clips.",
           "anchor_note": "ax/ay/az: decoded root channels 0-2, mm, move heading frame (+Z forward, +Y up, +X = the "
                          "bake's Left side); rx/ry/rz: hips delta from frame 0 in the yaw-normalised frame, rig "
                          "metres x1000 (same as rows.pack.json). yaw0: frame-0 Hips yaw (rad) in the heading frame.",
           "anchor_mm_to_rig_m": round(scale / 1000.0, 9),
           "decoder": "teardown/tekken3/tools/local/pose_assemble.py + usa_motion.py",
           "tool": "tools/anim/t3_reaction_bake.py -> lab/tools/t3_motion_bake.py (T3Space, sample_clip, retarget)",
           "plan": "tools/anim/t3_reaction_tables.py bank_plan", "sha256": shas, "rows": {}, "missing": {}}
    jobs = sorted(want.items())[:limit] if limit else sorted(want.items())
    dst = T3DIR / d / "reactions.pack.json"
    if merge and dst.exists():
        old = json.loads(dst.read_text())
        for k in ("bank", "body_kmd", "stance", "target_rig", "bones", "sha256"):
            if old.get(k) != out[k]:
                sys.exit(f"{d}: --merge refused, existing pack {k} differs")
        out["fps"] = old["fps"]
        kept = {f"{s:#x}" for s, _ in jobs} & set(old["rows"])
        for k in kept:
            out["rows"][k] = dict(old["rows"][k], roles=sorted(want[int(k, 16)]))
        jobs = [(s, r) for s, r in jobs if f"{s:#x}" not in kept]
        print(f"{d}: --merge keeps {len(kept)} clips, bakes {len(jobs)}", flush=True)
    t0 = time.time()
    for slot, roles in jobs:
        key = f"{slot:#x}"
        try:
            clip = TB.sample_clip(space, kmd, bank_path, slot, 2)
            tr, rt = TB.retarget(rig, space, clip)
            anc = root_channels(bank_path, slot, 2)
        except (SystemExit, Exception) as e:   # noqa: BLE001
            out["missing"][key] = f"decode failed: {type(e).__name__}: {str(e)[:160]}"
            continue
        n = len(rt)
        if len(anc) != n:
            out["missing"][key] = f"root channel frames {len(anc)} != pose frames {n}"
            continue
        ident = [[0.0, 0.0, 0.0, 1.0]] * n
        q = np.array([tr[b][0] if b in tr else ident for b in CANON22], float).transpose(1, 0, 2)  # [n][22][4]
        q *= np.where(q[..., 3:4] < 0, -1.0, 1.0)
        if not np.isfinite(q).all():
            out["missing"][key] = "non-finite rotation after retarget"
            continue
        if out["fps"] is not None and out["fps"] != clip["fps"]:
            sys.exit(f"fps mismatch: {out['fps']} vs {clip['fps']} at {key}")
        out["fps"] = clip["fps"]
        rtv = np.array(rt, float)
        y0 = heading_yaw(rig, space, clip)
        out["rows"][key] = {"slot": slot, "move_row": clip["move_row"],
                            "src": "common" if clip["move_row"] >= TB.motion.COMMON_FLAG else "own",
                            "stream_frames": clip["stream_frames"], "n": n, "roles": sorted(roles),
                            "yaw0": None if y0 is None else round(y0, 5),
                            "q": b64_i16(np.round(np.clip(q, -1, 1) * 32767)),
                            "rx": b64_i16(np.round(rtv[:, 0] * 1000)), "ry": b64_i16(np.round(rtv[:, 1] * 1000)),
                            "rz": b64_i16(np.round(rtv[:, 2] * 1000)),
                            "ax": b64_i16(np.clip(anc[:, 0], -32768, 32767)),
                            "ay": b64_i16(np.clip(-anc[:, 1], -32768, 32767)),
                            "az": b64_i16(np.clip(-anc[:, 2], -32768, 32767))}
    out["rows"] = dict(sorted(out["rows"].items(), key=lambda kv: int(kv[0], 16)))
    dst.write_text(json.dumps(out, separators=(",", ":")))
    print(f"{d}: {len(out['rows'])} clips, {len(out['missing'])} missing of {len(jobs)}, "
          f"{dst.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f}s -> {dst.relative_to(REPO)}", flush=True)
    for k, v in list(out["missing"].items())[:6]:
        print(f"  missing {k}: {v}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", action="append", choices=sorted(RT.BANK_DIRS), default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, help="bake only the first N slots (smoke test)")
    ap.add_argument("--merge", action="store_true", help="keep the clips already in the pack (same inputs, SHA-256 "
                    "checked) and bake only the planned slots it lacks")
    a = ap.parse_args()
    for d in (sorted(RT.BANK_DIRS) if a.all else a.bank):
        bake(d, a.limit, a.merge)
