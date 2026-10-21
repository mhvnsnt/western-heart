#!/usr/bin/env python3
"""Bake EVERY Tekken 3 move row the WH movesets reference into one compact pack per bank.

Each WH move records the T3 row it was built from (`t3_row`, `anim_ref: t3:<bank>:row:<n>`).
Until now every attack played one of three generic clips (light/medium/heavy). This bakes
each referenced row's own animation from the owner's disc teardown, with the existing,
unchanged pipeline:
  lab/tools/t3_motion_bake.py  T3Space + sample_clip (pose_assemble.py bit-exact decode)
                               + TargetRig/retarget onto the bank's identity-rest rig
and writes game/assets/anim/t3/<bankdir>/rows.pack.json (format wh-anim-pack/1):
  bones   joint order (== skeleton.json joints)
  rows    { "<row>": { slot, stream_frames, n, q: base64 int16 [n][bones][4] (q*32767),
                       ry: base64 int16 [n] root height in mm, rx/rz likewise } }
A row is played through a move-index SLOT; the slot is any s with move_index[s] == row
(inverse of the bank's own slot table). Inputs are logged with SHA-256.

Usage (needs n0madic/Tekken3Remake tools/research on T3REMAKE_RESEARCH, as t3_motion_bake):
  python3 tools/anim/t3_row_bake.py --bank jin
  python3 tools/anim/t3_row_bake.py --bank heihachi --kmd-from jin   # Heihachi motion, Jin body (see --help)
"""
import argparse, base64, glob, hashlib, json, sys, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "lab/tools"))
import t3_motion_bake as TB  # noqa: E402  (sets up the decoder import paths)

SRC2BANK = {"king": "king", "demonio": "jin", "jin": "jin", "bryan": "bryan", "xiaoyu": "xiaoyu",
            "yoshimitsu": "yoshimitsu", "gunjack": "gunjack", "bosconovitch": "bosconovitch",
            "deviljin": "jin", "heihachi": "heihachi",
            # 2026-10-21: the banks PR #405 added (game/assets/anim/t3/<bank>/, rig
            # lab/game/assets/t3_<bank>_t3real.glb) bake their move rows too
            "paul": "paul", "lei": "lei", "nina": "nina", "hwoarang": "hwoarang", "eddy": "eddy",
            "julia": "julia", "anna": "anna"}
BANK_DIR = {"king": "king_on_pantera_leoman", "jin": "jin", "xiaoyu": "xiaoyu", "bryan": "bryan",
            "gunjack": "gunjack", "yoshimitsu": "yoshimitsu", "heihachi": "heihachi_on_jin"}
TARGET_GLB = {"king": "lab/game/assets/pantera_leoman.glb", "jin": "lab/game/assets/t3_jin.glb",
              "xiaoyu": "lab/game/assets/t3_xiaoyu.glb", "bryan": "lab/game/assets/t3_bryan.glb",
              "gunjack": "lab/game/assets/t3_gunjack.glb", "yoshimitsu": "lab/game/assets/t3_yoshimitsu.glb"}
# Remainder banks: their runtime skeleton.json comes from lab/game/assets/t3_<bank>_t3real.glb, so the
# rows retarget onto that same identity-rest rig. Body (KMD + slot-0 frame-75 stance) = the character's
# OWN disc body paired with its own motion bank by tools/anim/t3_extract_bodies.py (BODY-EXTRACTION.json,
# SHA-256 against the original BNS index). Run that tool first; its outputs are local (public repo).
REMAINDER = ["paul", "lei", "nina", "hwoarang", "eddy", "julia", "anna", "bosconovitch"]
_BODY = REPO / "teardown/tekken3/BODY-EXTRACTION.json"
if _BODY.exists():
    _bx = json.loads(_BODY.read_text())
    for _b in REMAINDER:
        _e = _bx.get(_b)
        if isinstance(_e, dict) and _e.get("kmd"):
            BANK_DIR[_b] = _b
            TARGET_GLB[_b] = f"lab/game/assets/t3_{_b}_t3real.glb"
            TB.BANKS[_b] = (str(Path(_e["kmd"]).relative_to("teardown/tekken3")),
                            str(Path(_e["bank"]).relative_to("teardown/tekken3")),
                            str(Path(_e["stance_obj"]).relative_to("teardown/tekken3")))


def referenced_rows(bank):
    rows = {}
    for f in sorted(glob.glob(str(REPO / "game/assets/movesets/*.json"))):
        d = json.load(open(f))
        if not isinstance(d, dict):
            continue
        mv = d.get("moves") or {}
        items = mv.values() if isinstance(mv, dict) else mv
        for v in items:
            if isinstance(v, dict) and "t3_row" in v:
                src = v.get("t3_source") or d.get("t3_source")
                if SRC2BANK.get(src) == bank and isinstance(v["t3_row"], int):
                    rows.setdefault(v["t3_row"], []).append(Path(f).stem)
            at = v.get("anim_t3") if isinstance(v, dict) else None
            if at and SRC2BANK.get(at.get("bank")) == bank and isinstance(at.get("row"), int):
                rows.setdefault(at["row"], []).append(Path(f).stem)
    return rows


def b64_i16(a):
    return base64.b64encode(np.ascontiguousarray(a, dtype="<i2").tobytes()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True, choices=sorted(BANK_DIR))
    ap.add_argument("--kmd-from", help="body (KMD + stance + target rig) of another bank; for heihachi, whose "
                    "heihachi191 KMD has no hip/shoulder vertex data (PROCEDURAL_AUDIT): the motion stream is "
                    "Heihachi's own divmot13 bank, posed on that character's T3 skeleton.")
    ap.add_argument("--rows", help="comma list to override the referenced-row set")
    ap.add_argument("--extra-slots", default="", help="name=slot,... also baked into the pack (e.g. neutral=3)")
    ap.add_argument("--write-clips", default="", help="name=slot,... also written as wh-anim/1 JSON files next to the "
                    "pack (same format as t3_motion_bake --json-dir), for the per-state clips t3anims.js loads")
    a = ap.parse_args()
    body = a.kmd_from or a.bank
    kmd, _, stance = (TB.T3 / x for x in TB.BANKS[body])
    bank_path = TB.T3 / TB.BANKS[a.bank][1]
    tgt = TARGET_GLB[body]
    space = TB.T3Space(kmd, stance)
    rig = TB.TargetRig(REPO / tgt)
    mbank = TB.motion.parse_bank(bank_path.read_bytes())
    slot_of = {}
    for s, r in enumerate(mbank.move_index):
        if r < TB.motion.COMMON_FLAG and r not in slot_of:
            slot_of[r] = s
    want = {int(r): [] for r in a.rows.split(",")} if a.rows else referenced_rows(a.bank)
    sha = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (kmd, bank_path, TB.usa_tables.EXE_PATH)}
    sha[Path(tgt).name] = hashlib.sha256((REPO / tgt).read_bytes()).hexdigest()
    out = {"format": "wh-anim-pack/1", "bank": str(bank_path.relative_to(REPO)), "body_kmd": str(kmd.relative_to(REPO)),
           "target_rig": tgt, "bones": rig.names, "fps": None, "hand_keyed": False,
           "decoder": "teardown/tekken3/tools/local/pose_assemble.py + usa_motion.py",
           "tool": "tools/anim/t3_row_bake.py -> lab/tools/t3_motion_bake.py (T3Space, sample_clip, retarget)",
           "sha256": sha, "rows": {}, "missing": {}}
    jobs = [(str(r), slot_of.get(r), refs) for r, refs in sorted(want.items())]
    for kv in filter(None, a.extra_slots.split(",")):
        k, v = kv.split("=")
        jobs.append((k, int(v, 0), ["extra"]))
    t0 = time.time()
    for key, slot, refs in jobs:
        if slot is None:
            out["missing"][key] = "no move-index slot points at this row"
            continue
        try:
            clip = TB.sample_clip(space, kmd, bank_path, slot, 2)
        except (SystemExit, Exception) as e:
            out["missing"][key] = f"{type(e).__name__}: {str(e)[:120]}"
            continue
        tr, rt = TB.retarget(rig, space, clip)
        n = len(rt)
        q = np.array([tr[b][0] for b in rig.names], float).transpose(1, 0, 2)  # [n][bones][4]
        q *= np.where(q[..., 3:4] < 0, -1.0, 1.0)  # canonical sign (w >= 0) before quantizing
        rtv = np.array(rt, float)
        out["fps"] = clip["fps"]
        out["rows"][key] = {"slot": slot, "move_row": clip["move_row"], "stream_frames": clip["stream_frames"], "n": n,
                            "used_by": sorted(set(refs))[:12],
                            "q": b64_i16(np.round(np.clip(q, -1, 1) * 32767)),
                            "rx": b64_i16(np.round(rtv[:, 0] * 1000)), "ry": b64_i16(np.round(rtv[:, 1] * 1000)),
                            "rz": b64_i16(np.round(rtv[:, 2] * 1000))}
    for kv in filter(None, a.write_clips.split(",")):
        k, v = kv.split("=")
        slot = slot_of.get(int(v[4:])) if v.startswith("row:") else int(v, 0)
        if slot is None:
            out["missing"][k] = f"no move-index slot for {v}"
            continue
        try:
            clip = TB.sample_clip(space, kmd, bank_path, slot, 2)
        except (SystemExit, Exception) as e:
            out["missing"][k] = f"{type(e).__name__}: {str(e)[:120]}"
            continue
        tr, rt = TB.retarget(rig, space, clip)
        ex = {"source": "REAL decoded Tekken 3 motion (owner's disc teardown)", "bank": str(bank_path.relative_to(REPO)),
              "body_kmd": str(kmd.relative_to(REPO)), "slot": hex(slot), "move_row": clip["move_row"],
              "stream_frames": clip["stream_frames"], "fps": clip["fps"], "decoder": out["decoder"],
              "tool": "tools/anim/t3_row_bake.py --write-clips (t3_motion_bake.sample_clip + retarget)", "sha256": sha,
              "hand_keyed": False}
        d = REPO / "game/assets/anim/t3" / BANK_DIR[a.bank]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{k}.json").write_text(json.dumps({"format": "wh-anim/1", **ex, "bones": rig.names,
                                                 "rot_xyzw": {b: v[0] for b, v in tr.items()}, "root_t": rt},
                                                separators=(",", ":")))
    dst = REPO / "game/assets/anim/t3" / BANK_DIR[a.bank] / "rows.pack.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, separators=(",", ":")))
    print(f"{a.bank}: {len(out['rows'])} rows baked, {len(out['missing'])} missing, "
          f"{dst.stat().st_size/1e6:.2f} MB, {time.time()-t0:.0f}s -> {dst.relative_to(REPO)}")
    if out["missing"]:
        print(" missing:", dict(list(out["missing"].items())[:8]))


if __name__ == "__main__":
    main()
