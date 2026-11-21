#!/usr/bin/env python3
"""Decode all 98 VPW2 wrestler movesets (+3 edit-mode) to JSON.

Chain (all verified against ROM code + data):
  moveset bitstream --(vpw2_moveset.decode_moveset)--> per move_id:
      {mod_value, flags, menu_item, slot}
  mod_value --(raw file 0278)--> AnimID --> move_anim_map.json
      (move name, category, file_id, .npy, Toki1 windows)
  mod_value --(raw file 0279)--> damage index --> move_damage.json
      (damage, spirit gain/drain, attack/defense params, body-part damage)

Output: decoded_movesets.json + decoded_movesets/<id4>.json
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vpw2_moveset import MOVESET_DIR, RAW_DIR, load_tables, decode_moveset

from vpw2_moveset import ROOT as EXTRACTED  # teardown/virtual-pro-wrestling-2/


def load_u16_table(fid):
    d = (RAW_DIR / f"{fid}.bin").read_bytes()
    return struct.unpack(f">{len(d)//2}H", d)


def main():
    out_dir = Path(__file__).parent / "decoded_movesets"
    out_dir.mkdir(exist_ok=True)
    tables = load_tables()
    anim_table = load_u16_table("0278")
    prop_table = load_u16_table("0279")
    mam = json.loads((MOVESET_DIR / "move_anim_map.json").read_text())
    by_anim = {
        a["anim_id"]: a for a in mam["animations"] if a.get("anim_id") is not None
    }
    md = json.loads((MOVESET_DIR / "move_damage.json").read_text())
    dmg = {r["index"]: r for r in md["records"]}
    roster = json.loads((EXTRACTED / "roster" / "roster.json").read_text())
    by_id4 = {w["id4"]: w for w in roster["wrestlers"]}
    man = json.loads((MOVESET_DIR / "params_moveset_manifest.json").read_text())

    all_out = {"source": "VPW2 moveset bitstream decoder (ROM-verified)",
               "decoder": "vpw2_moveset.py (encoder 0x80005578 / decoder 0x8000632C)",
               "wrestlers": []}
    n_anim_named = n_anim_total = 0
    for p in man["pairs"]:
        if p["kind"] != "moveset":
            continue
        data = (RAW_DIR / f"{p['file_id']}.bin").read_bytes()
        res = decode_moveset(data, tables)
        w = by_id4.get(p["wrestler_id4"], {})
        moves = []
        for mid in sorted(res["moves"]):
            m = res["moves"][mid]
            mv = m["mod_value"]
            entry = {
                "move_id": mid,
                "menu_item": m["menu_item"],
                "slot": m["slot"],
                "mod_value": mv,
                "flags": m["flags"],
            }
            if mv:
                anim_id = anim_table[mv]
                prop_idx = prop_table[mv]
                entry["anim_id"] = anim_id
                a = by_anim.get(anim_id)
                if a:
                    entry["move_name"] = a.get("move_name")
                    entry["category"] = a.get("category")
                    entry["file_id"] = a.get("file_id")
                    entry["npy"] = a.get("npy")
                    entry["toki1"] = a.get("toki1")
                    n_anim_total += 1
                    if a.get("move_name"):
                        n_anim_named += 1
                d = dmg.get(prop_idx)
                if d:
                    entry["damage_index"] = prop_idx
                    entry["damage"] = d["damage"]
                    entry["spirit_gain"] = d["spirit_gain"]
                    entry["spirit_drain"] = d["spirit_drain"]
                    entry["attack_param"] = d["attack_param"]
                    entry["defense_param"] = d["defense_param"]
                    entry["head_damage"] = d["head_damage"]
                    entry["body_damage"] = d["body_damage"]
                    entry["arm_damage"] = d["arm_damage"]
                    entry["leg_damage"] = d["leg_damage"]
                    entry["speed_damage"] = d["speed_damage"]
            moves.append(entry)
        rec = {
            "wrestler_id4": p["wrestler_id4"],
            "name": w.get("name"),
            "name_short": w.get("name_short"),
            "slot": w.get("slot"),
            "moveset_file_id": p["file_id"],
            "style": res["style"],
            "bits_used": res["total_bits"],
            "file_bits": res["file_bits"],
            "invalid": res["invalid"],
            "moves": moves,
        }
        all_out["wrestlers"].append(rec)
        (out_dir / f"{p['wrestler_id4']}.json").write_text(
            json.dumps(rec, indent=1, ensure_ascii=False)
        )
    # edit-mode movesets
    for fid, style_name in [("0346", "wrestling"), ("0348", "combo"), ("034A", "shoot")]:
        data = (RAW_DIR / f"{fid}.bin").read_bytes()
        res = decode_moveset(data, tables)
        assert res["style"] == style_name, (fid, res["style"])
        assert not res["invalid"], fid
        print(f"edit {fid} ({style_name}): OK, {len(res['moves'])} moves, "
              f"{sum(1 for m in res['moves'].values() if m['mod_value'])} set")
    out_path = Path(__file__).parent / "decoded_movesets.json"
    out_path.write_text(json.dumps(all_out, indent=1, ensure_ascii=False))
    print(f"wrote {out_path} ({len(all_out['wrestlers'])} wrestlers)")
    print(f"anim lookups: {n_anim_named}/{n_anim_total} named")
    print(f"total moves: {sum(len(w['moves']) for w in all_out['wrestlers'])}")


if __name__ == "__main__":
    main()
