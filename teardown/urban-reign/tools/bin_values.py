#!/usr/bin/env python3
"""Full per-mission .bin field table (missions 1-100) at disassembly-proven offsets.
Offsets proven by SLUS_212.09 disassembly (ao_mission.cpp module 0x271b60-0x274000
+ setters/getters 0x238470/0x238ba8/0x238bb8/0x274000/0x2385e0):
 0x00 u16 -> global 0x5E8C88 (setter 0x238ba8); 0x02 u16 -> global 0x59D124 (0x238470)
 0x08 i32 x0.001 player X; 0x0c i32 x0.001 player Z; 0x10 i16 /32768 player facing
 0x14 i32 x0.001 slot-1 X; 0x18 i32 x0.001 slot-1 Z; 0x1c i16 /32768 slot-1 facing
 0x1e i16 arg to 0x236200 (role unproven); 0x20 i16 slot-1 presence (-1 absent, -2 special)
 0x24 u16 fighter field; 0x28 sub-struct pointer; 0x74/0x76 i16 condition fields
 0xa8 u16 count of 172-byte records at 0x1d4; 0xac u16 fighter field
 0x15c u16 count of 28-byte records at 0x162; 0x1754/56/58 u16 x3 -> flag array 0xABF9A0[id]=1
 0x1d0 u16 count clamped to <=32 -> global 0x94D174
Output: mission_bin_fields.json (per-mission table + distributions).
"""
import struct, json
from pathlib import Path

def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def i16(b, o): return struct.unpack_from('<h', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def i32(b, o): return struct.unpack_from('<i', b, o)[0]

OUT = Path("/var/tmp/ur-census")
rows = []
for n in range(1, 101):
    b = open(f'/home/hatch/workspace/urban-reign-redux/decoded/inputs/mission_defs/mission{n:03d}.bin', 'rb').read()
    cnt28 = u16(b, 0x15c)
    rec28 = []
    for i in range(cnt28):
        base = 0x162 + i * 0x1c
        rec28.append({"u16_at_0": u16(b, base), "u32_at_10": u32(b, base + 10),
                      "bytes": b[base:base + 28].hex()})
    cnt172 = u16(b, 0xa8)
    rec172 = []
    for i in range(cnt172):
        base = 0x1d4 + i * 0xac
        rec172.append({"first_u32": u32(b, base), "bytes_head": b[base:base + 32].hex()})
    rows.append({
        "mission": n,
        "off00_area_id": u16(b, 0), "off02": u16(b, 2),
        "player_x_m": i32(b, 8) / 1000.0, "player_z_m": i32(b, 12) / 1000.0,
        "player_facing": i16(b, 16) / 32768.0,
        "slot1_x_m": i32(b, 20) / 1000.0, "slot1_z_m": i32(b, 24) / 1000.0,
        "slot1_facing": i16(b, 28) / 32768.0,
        "off1e": i16(b, 30), "off20_slot1_presence": i16(b, 32), "off24": u16(b, 36),
        "off74": i16(b, 116), "off76": i16(b, 118),
        "offa8_rec172_count": cnt172, "offac": u16(b, 172),
        "off15c_rec28_count": cnt28, "rec28": rec28, "rec172": rec172,
        "flag_id_0": u16(b, 0x1754), "flag_id_1": u16(b, 0x1756), "flag_id_2": u16(b, 0x1758),
        "off1d0_count_capped32": u16(b, 0x1d0),
    })

def dist(key):
    return sorted(set(r[key] for r in rows))

doc = {
    "source": "SLUS_212.09 (Urban Reign USA, SLUS-21209) disassembly, Capstone MIPS32 LE; mission .bin files mission001-100.bin",
    "proven_offsets": {
        "0x00": "u16 -> global 0x5E8C88 via setter 0x238ba8; read by game-state code (0x22b6a0 branch on mode 2..6). Values 0-25. NAME UNPROVEN (inference: mission area/scene id).",
        "0x02": "u16 -> global 0x59D124 via setter 0x238470. Values {0, 99} only.",
        "0x08": "i32, x0.001 -> player spawn X (metres). Range -28.15..51.22.",
        "0x0c": "i32, x0.001 -> player spawn Z (metres). Range -31.43..39.50.",
        "0x10": "i16, /32768 -> player spawn facing (fraction of full turn). Range -1..0.93.",
        "0x14": "i32, x0.001 -> slot-1 spawn X (metres).",
        "0x18": "i32, x0.001 -> slot-1 spawn Z (metres).",
        "0x1c": "i16, /32768 -> slot-1 spawn facing.",
        "0x1e": "i16, values {0,200,600,1000,1500}; loaded as $a1 in delay slot of jal 0x236200 (fighter-struct field copier, $a0=slot 1). Exact role UNPROVEN.",
        "0x20": "i16 slot-1 presence: -1 = no second fighter, -2 = special branch, else present.",
        "0x24": "u16 stored to fighter struct (+0x8C9A). Role UNPROVEN.",
        "0x28": "pointer to sub-struct (.bin+0x28) stored in fighter struct (+0x8CEC). Contents UNPROVEN.",
        "0x74/0x76": "i16 condition fields, tested together with 0x20 (0x2727c0-0x2727cc). Roles UNPROVEN.",
        "0xa8": "u16 (1-5) -> global 0x94D170 = count of 172-byte records at 0x1d4, copied into runtime fighter table (0x271d88).",
        "0xac": "u16 stored to fighter struct (+0x8DF4). Role UNPROVEN.",
        "0x15c": "u16 (0-2) = count of 28-byte records at 0x162 (u16@+0, u32@+10, stride 0x1c).",
        "0x1754/0x1756/0x1758": "u16 x3 -> each passed to 0x274000, which sets flag array 0xABF9A0[id]=1 (activation flags).",
        "0x1d0": "u16 (1-5) -> global 0x94D174, clamped to <=32 (0x20). Count, capped at 32. What it counts UNPROVEN.",
        "0x1884": "22x24B slot table: NO reader in SLUS_212.09 main .text or any DVP overlay (searched all literal 0x1884 offsets). Semantics UNPROVEN; likely editor/legacy data the game never reads.",
        "rest": "Bytes 0x1e0-0x206c except the 0x1754 trio have no reader in the mission module (complete $s5 access list). Semantics UNPROVEN.",
    },
    "distributions": {
        "off00_area_id": dist("off00_area_id"),
        "off02": dist("off02"),
        "off1e": dist("off1e"),
        "off20_slot1_presence": dist("off20_slot1_presence"),
        "off24": dist("off24"),
        "off74": dist("off74"),
        "off76": dist("off76"),
        "offa8_rec172_count": dist("offa8_rec172_count"),
        "offac": dist("offac"),
        "off15c_rec28_count": dist("off15c_rec28_count"),
        "flag_id_0": dist("flag_id_0"),
        "flag_id_1": dist("flag_id_1"),
        "flag_id_2": dist("flag_id_2"),
        "off1d0_count_capped32": dist("off1d0_count_capped32"),
    },
    "missions": rows,
}
(OUT / "mission_bin_fields.json").write_text(json.dumps(doc, indent=2))
print("wrote mission_bin_fields.json, missions:", len(rows))
print("off02 == 99 missions:", [r["mission"] for r in rows if r["off02"] == 99])
print("off20 == -1 (no slot-1) missions:", sum(1 for r in rows if r["off20_slot1_presence"] == -1))
print("off20 == -2 missions:", sum(1 for r in rows if r["off20_slot1_presence"] == -2))
print("off20 other missions:", sum(1 for r in rows if r["off20_slot1_presence"] not in (-1, -2)))
print("player spawn X range:", min(r["player_x_m"] for r in rows), max(r["player_x_m"] for r in rows))
print("player spawn Z range:", min(r["player_z_m"] for r in rows), max(r["player_z_m"] for r in rows))
