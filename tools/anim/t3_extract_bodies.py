#!/usr/bin/env python3
"""Extract each Tekken 3 character's OWN body (KMD) from the disc and build its bake rig.

Why: the bodies used so far were mislabeled. Matching record bytes against the original
BNS filename index (n0madic/Tekken3Remake docs/research/bns-original-index.md, SHA-256 per
record) shows teardown/tekken3/models/jin151 = chun3.kmd (JULIA), bryan183 = boss3.kmd
(OGRE), heihachi191 = moku3.kmd (MOKUJIN — hence "no hip/shoulder vertex data"),
gunjack215 = anna2.kmd (ANNA). Their banks were therefore posed on another character's
proportions. In the index every KMD is followed by its own motion bank (kmd, .vh, .arc,
divmotNN.bin), which pairs body and motion straight from the disc layout.

Per character (first costume):
  1. KMD bytes = TEKKEN3.BNS[bns_offset : +size] from teardown/tekken3/model-inventory.json,
     verified against the index SHA-256 and the 3DMK magic
     -> teardown/tekken3/models/<kmd-stem><record>/<kmd-stem>.kmd
  2. stance OBJ = pose_assemble(kmd, own bank, slot 0, frame 75) (same convention as the
     existing *_stance75.obj) -> teardown/tekken3/renders/pose-check/<char>_body_stance75.obj
  3. canonical bake rig = lab/tools/t3_to_gltf.py fighter <kmd> <obj> -> lab/game/assets/t3body_<char>.glb
Nothing is authored; every byte comes from the disc and the existing decoders.

Usage (T3REMAKE_RESEARCH as for t3_motion_bake.py):
  python3 tools/anim/t3_extract_bodies.py [--only bosconovitch,heihachi] [--index PATH]
"""
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
T3 = REPO / "teardown/tekken3"
BANK_FILE = {  # divmot number -> character (teardown/tekken3/animations/divmotNN_<char>.bin)
    0: "paul", 1: "law", 2: "lei", 3: "king", 4: "yoshimitsu", 5: "nina", 6: "hwoarang", 7: "xiaoyu",
    8: "eddy", 9: "jin", 10: "julia", 11: "kuma", 12: "bryan", 13: "heihachi", 14: "ogre",
    16: "gunjack", 17: "anna", 18: "bosconovitch", 19: "gon", 20: "forestlaw"}


def index_rows(path):
    rows = {}
    for line in open(path):
        m = re.match(r"\| (\d+) \| `([^`]+)` \| (\d+) \| (\d+) \| `([0-9a-f]+)` \|", line)
        if m:
            rows[int(m[1])] = (m[2], int(m[4]), m[5])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=os.path.join(os.environ.get("T3REMAKE_RESEARCH", ""), "../../docs/research/bns-original-index.md"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    idx = index_rows(a.index)
    inv = {r["sha256"]: r for r in json.load(open(T3 / "model-inventory.json"))["records"]}
    bns = T3 / "disc/files/TEKKEN3/TEKKEN3.BNS"
    only = set(filter(None, a.only.split(",")))
    seen, report = set(), {}
    for i in sorted(idx):
        name, size, sha = idx[i]
        if not name.endswith(".kmd"):
            continue
        bank = next((idx[i + k][0] for k in range(1, 5) if idx.get(i + k, ("",))[0].startswith("divmot")), None)
        num = int(bank[6:8]) if bank else None
        char = BANK_FILE.get(num)
        if not char or char in seen or (only and char not in only):
            continue
        if name.startswith("ogre"):  # True Ogre shares divmot14 with Ogre (boss*.kmd); Ogre's own body first
            continue
        rec = inv.get(sha)
        if not rec:
            report[char] = f"MISSING: {name} (sha {sha[:12]}) not in model-inventory.json"
            continue
        with open(bns, "rb") as f:
            f.seek(rec["bns_offset"])
            data = f.read(rec["size"])
        assert hashlib.sha256(data).hexdigest() == sha and data[8:12] == b"3DMK", name
        stem = name[:-4]
        kdir = T3 / "models" / f"{re.sub(r'[0-9]+$', '', stem)}{i}"
        kdir.mkdir(parents=True, exist_ok=True)
        kmd = kdir / f"{stem}.kmd"
        kmd.write_bytes(data)
        bankp = T3 / "animations" / f"divmot{num:02d}_{char}.bin"
        obj = T3 / "renders/pose-check" / f"{char}_body_stance75.obj"
        sys.path.insert(0, str(T3 / "tools/local"))
        sys.path.insert(0, os.environ.get("T3REMAKE_RESEARCH", "/workspace/t3anim/t3r/tools/research"))
        import pose_assemble as PA, usa_tables
        usa_tables.EXE_PATH = T3 / "disc/files/TEKKEN3/SLUS_004.02"
        txt, info = PA.assemble(kmd, bankp, 0, 75, usa_tables.EXE_PATH)
        obj.write_text(txt)
        glb = REPO / "lab/game/assets" / f"t3body_{char}.glb"
        r = subprocess.run([sys.executable, str(REPO / "lab/tools/t3_to_gltf.py"), "fighter", str(kmd), str(obj), str(glb)],
                           capture_output=True, text=True)
        if r.returncode != 0:  # this costume's KMD can't be fitted (e.g. a missing part): try the next costume
            report.setdefault("_failed_costumes", {})[name] = (r.stdout + r.stderr)[-160:]
            print(char, name, "-> fit failed, trying next costume")
            continue
        seen.add(char)
        report[char] = {"kmd": str(kmd.relative_to(REPO)), "bns_record": i, "kmd_sha256": sha, "bank": str(bankp.relative_to(REPO)),
                        "stance_obj": str(obj.relative_to(REPO)), "rig": str(glb.relative_to(REPO)) if r.returncode == 0 else None,
                        "rig_log": (r.stdout + r.stderr)[-300:]}
        print(char, name, "->", report[char]["rig"] or "RIG FAILED: " + report[char]["rig_log"][-200:])
    out = T3 / "BODY-EXTRACTION.json"
    prev = json.loads(out.read_text()) if out.exists() else {}
    prev.update(report)
    out.write_text(json.dumps(prev, indent=1) + "\n")


if __name__ == "__main__":
    main()
