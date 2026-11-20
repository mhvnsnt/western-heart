#!/usr/bin/env python3
"""Final game-data pass: wrestler defs, costumes, enriched moves (menu +
anim/prop + damage join), fixed shop parse, movesets/params raw dumps,
reversals, font glyph sheets, archive analysis, sequence check, sound
bank rename to neutral names."""
import csv, json, os, re, struct, sys, zlib
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lzss import asmik_decode

# Repo layout: FR is the teardown dir (parent of tools/); outputs land
# directly in its moves/, sound/, ui/, misc/, caw/ subdirs.
FR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The ROM is never committed; place WWF No Mercy (USA) (Rev-A).z64
# next to tools/ (the same convention as extract_all_models.py).
ROM = os.path.join(FR, "WWF No Mercy (USA) (Rev-A).z64")
FT, FIRST = 0x16C31D8, 0x1BD150
EXT = FR
rom = open(ROM, 'rb').read()
table = struct.unpack('>19459I', rom[FT:FT + 19459 * 4])

def get(fid):
    loc, enc = table[fid - 1] & ~1, table[fid - 1] & 1
    nloc = table[fid] & ~1
    raw = rom[FIRST + loc:FIRST + nloc]
    return asmik_decode(raw) if enc else raw

def write_png(path, w, h, rgba):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    rows = b''.join(b'\x00' + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                           chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))

db = {}
for line in open(os.path.join(FR, "tools", "NoMercy-FileTableDB.txt")):
    m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', line.strip())
    if m:
        db[int(m.group(1), 16)] = (m.group(2), m.group(3))

# ---------- 1. Wrestler defs: 293 x 20B @ 0x465B8 ----------
wdefs = []
for i in range(293):
    r = rom[0x465B8 + i * 20:0x465B8 + (i + 1) * 20]
    id4, id2 = struct.unpack('>HH', r[0:4])
    theme, video, height, unk = r[4], r[5], r[6], r[7]
    weight, mv, pr, ap, pf = struct.unpack('>HHHHH', r[8:18])
    pad = struct.unpack('>H', r[18:20])[0]
    wdefs.append({"index": i, "wrestler_id4": id4, "wrestler_id2": id2,
                  "theme_song": theme, "entrance_video": video,
                  "height": height, "unknown": unk, "weight": weight,
                  "moveset_file": hex(mv), "params_file": hex(pr),
                  "appearance_index": ap, "profile_index": pf, "pad": pad})
# join names via moveset file labels ("Wrestler Moveset NNNN (Name)")
for w in wdefs:
    mv = int(w["moveset_file"], 16)
    label = db.get(mv, ("", ""))[1]
    mm = re.search(r'\(([^)]+)\)\s*$', label)
    w["name_from_moveset"] = mm.group(1) if mm else None
named = sum(1 for w in wdefs if w["name_from_moveset"])
print(f"wrestler defs: {len(wdefs)} records, {named} named via moveset labels")
json.dump(wdefs, open(os.path.join(EXT, 'misc', 'wrestler-defs.json'), 'w'), indent=1)

# ---------- 2. Costumes: 260 x 38B in file 0x0001 ----------
COSTUME_FIELDS = ["body_type", "skin_color", "ring_attire", "ring_attire_color1",
    "ring_attire_color2", "upper_attire", "upper_attire_color1",
    "upper_attire_color2", "entrance_attire", "entrance_attire_color1",
    "entrance_attire_color2", "entrance_weapon", "gloves", "gloves_color",
    "tattoo", "wristband", "wristband_color", "left_elbow_pad",
    "left_elbow_pad_color", "right_elbow_pad", "right_elbow_pad_color",
    "left_knee_pad", "left_knee_pad_color", "right_knee_pad",
    "right_knee_pad_color", "boots", "boots_color1", "boots_color2",
    "head_shape", "face_number", "hair_type", "hair_color", "front_hair",
    "facial_hair", "masks_etc", "hats_caps", "hats_caps_color", "portrait"]
cdata = get(0x0001)
costumes = []
for i in range(len(cdata) // 38):
    rec = cdata[i * 38:(i + 1) * 38]
    costumes.append(dict({"index": i, "slot": i // 4, "attire": i % 4},
                         **{f: rec[j] for j, f in enumerate(COSTUME_FIELDS)}))
print(f"costumes: {len(costumes)} records (65 slots x 4 attires)")
os.makedirs(os.path.join(EXT, 'caw'), exist_ok=True)
json.dump(costumes, open(os.path.join(EXT, 'caw', 'default-costumes.json'), 'w'), indent=1)

# ---------- 3. Enriched moves: menu + anim/prop + damage ----------
dmg = get(0x01EF)
anims = struct.unpack('>%dh' % (len(get(0x01F0)) // 2), get(0x01F0))
props = struct.unpack('>%dh' % (len(get(0x01F1)) // 2), get(0x01F1))
BODY = ["Head", "Body", "Arms", "Legs", "Flying"]

def damage_record(i):
    d = dmg[i * 36:(i + 1) * 36]
    fly, link = struct.unpack('>HH', d[2:6])
    return {
        "damage_index": i,
        "flying_target_body_part": fly, "link": link,
        "damage": d[6], "spirit_gain": d[7],
        "spirit_drain": d[8] - 256 if d[8] > 127 else d[8],
        "blood_chance": d[9], "ko_chance": d[10],
        "offensive_param": d[11],
        "offensive_param_name": BODY[d[11]] if d[11] < 5 else f"?{d[11]}",
        "defensive_param": d[12],
        "defensive_param_name": BODY[d[12]] if d[12] < 5 else f"?{d[12]}",
        "attack_with": d[13], "unknown_0e": d[14], "unknown_0f": d[15],
        "attack_to": d[16], "unknown_11": d[17],
        "head_damage": d[18], "body_damage": d[19],
        "arm_damage": d[20], "leg_damage": d[21],
        "speed_flying_damage": d[22], "strike_reaction": d[23],
        "unknown_18": d[24], "unknown_19": d[25], "unknown_1a": d[26],
        "special_damage": d[27], "previous_move": d[28],
        "unknown_1d": d[29], "unknown_1e": d[30], "unknown_1f": d[31],
        "move_type": d[32], "additional_properties": d[33],
        "unknown_22": d[34], "unknown_23": d[35]}

dmg_all = [damage_record(i) for i in range(len(dmg) // 36)]
json.dump(dmg_all, open(os.path.join(EXT, 'moves', 'move-damage.json'), 'w'), indent=1)

moves = json.load(open(os.path.join(EXT, 'moves', 'moves.json')))
enriched = []
for fl in moves["files"]:
    cat = re.match(r'\[([^\]]*)\]', fl["label"])
    for idx, e in enumerate(fl["entries"]):
        m = e["master_move_id"]
        anim_v = anims[m] if 0 <= m < len(anims) else None
        prop_v = props[m] if 0 <= m < len(props) else None
        en = dict(e)
        en["file_id"] = fl["file_id"]
        en["file_index"] = idx
        en["category"] = cat.group(1) if cat else ""
        en["menu_label"] = fl["label"]
        en["anim_table_value"] = anim_v
        en["anim_table_matches_menu"] = (anim_v == e["anim_id"]) if anim_v is not None else None
        en["damage_index"] = prop_v
        en["damage"] = damage_record(prop_v) if prop_v is not None else None
        enriched.append(en)
json.dump(enriched, open(os.path.join(EXT, 'moves', 'moves-enriched.json'), 'w'), indent=1)
with open(os.path.join(EXT, 'moves', 'moves-enriched.csv'), 'w', newline='') as f:
    fields = ["file_id", "file_index", "category", "name", "damage_info",
              "preview_pos", "move_link", "anim_id", "anim_file_id",
              "repeat_anim_id", "master_move_id", "damage_index",
              "dmg_damage", "dmg_spirit_gain", "dmg_spirit_drain",
              "dmg_blood_chance", "dmg_ko_chance", "dmg_off_param",
              "dmg_def_param", "dmg_head", "dmg_body", "dmg_arm", "dmg_leg",
              "dmg_flying", "dmg_move_type"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for e in enriched:
        d = e["damage"] or {}
        w.writerow({"file_id": e["file_id"], "file_index": e["file_index"],
                    "category": e["category"], "name": e["name"],
                    "damage_info": e["damage_info"], "preview_pos": e["preview_pos"],
                    "move_link": e["move_link"], "anim_id": e["anim_id"],
                    "anim_file_id": e["anim_file_id"],
                    "repeat_anim_id": e["repeat_anim_id"],
                    "master_move_id": e["master_move_id"],
                    "damage_index": e["damage_index"],
                    "dmg_damage": d.get("damage", ""), "dmg_spirit_gain": d.get("spirit_gain", ""),
                    "dmg_spirit_drain": d.get("spirit_drain", ""),
                    "dmg_blood_chance": d.get("blood_chance", ""),
                    "dmg_ko_chance": d.get("ko_chance", ""),
                    "dmg_off_param": d.get("offensive_param_name", ""),
                    "dmg_def_param": d.get("defensive_param_name", ""),
                    "dmg_head": d.get("head_damage", ""), "dmg_body": d.get("body_damage", ""),
                    "dmg_arm": d.get("arm_damage", ""), "dmg_leg": d.get("leg_damage", ""),
                    "dmg_flying": d.get("speed_flying_damage", ""),
                    "dmg_move_type": d.get("move_type", "")})
n_dmg = sum(1 for e in enriched if e["damage"] is not None)
print(f"enriched moves: {len(enriched)} entries, {n_dmg} with damage records")
rb = [e for e in enriched if "Rock Bottom" in e["name"]]
print("Rock Bottom menu entries:", [(e["name"], e["category"], e["anim_id"],
      e["damage"]["damage"] if e["damage"] else None) for e in rb])

# ---------- 4. Shop (fixed: u8 count first) ----------
def parse_shop(dec):
    n = dec[0]
    entries, o = [], 1
    for _ in range(n):
        price = struct.unpack('>I', dec[o:o + 4])[0]
        unlock, itype = dec[o + 4], dec[o + 5]
        itemdata = struct.unpack('>H', dec[o + 6:o + 8])[0]
        j = dec.find(b'\x00', o + 10)
        name = dec[o + 10:j].decode('shift_jis', 'replace')
        k = dec.find(b'\x00', j + 1)
        desc = dec[j + 1:k].decode('shift_jis', 'replace')
        entries.append({"price": price, "unlock_id": unlock, "item_type": itype,
                        "item_type_name": {0x43: "attire", 0x57: "wrestler",
                                           0x4D: "move"}.get(itype, f"?{itype:#x}"),
                        "item_data": itemdata, "name": name, "description": desc})
        o = k + 1
    return {"count": n, "entries": entries, "trailing": len(dec) - o}

shop_all = []
for fid in (0x4AA9, 0x4AAA, 0x4AAB):
    p = parse_shop(get(fid))
    shop_all.append({"file_id": hex(fid), "label": db[fid][1], **p})
    print(f"shop {fid:04X}: {p['count']} items, trailing={p['trailing']}")
json.dump(shop_all, open(os.path.join(EXT, 'ui', 'shop.json'), 'w'), indent=1)
print("shop sample:", shop_all[0]["entries"][:3])

# ---------- 5. Movesets + params (raw; bit-packed, VPWStudio has no parser) ----------
ms_out, pm_out = [], []
for fid, (t, label) in sorted(db.items()):
    if fid > 0x4C02:
        continue
    if "Wrestler Moveset" in label:
        d = get(fid)
        ms_out.append({"file_id": hex(fid), "label": label, "len": len(d),
                       "u16": list(struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2])),
                       "hex": d.hex()})
    elif "Wrestler Params" in label:
        d = get(fid)
        pm_out.append({"file_id": hex(fid), "label": label, "len": len(d),
                       "bytes": list(d), "hex": d.hex()})
json.dump({"movesets": ms_out, "params": pm_out},
          open(os.path.join(EXT, 'misc', 'wrestler-movesets-params.json'), 'w'), indent=1)
print(f"movesets: {len(ms_out)} files, params: {len(pm_out)} files (raw dumps)")

# ---------- 6. Reversals ----------
rev = []
for fid in range(0x01F2, 0x01F8):
    d = get(fid)
    rev.append({"file_id": hex(fid), "label": db[fid][1], "len": len(d),
                "u16": list(struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2])),
                "hex": d.hex()})
json.dump(rev, open(os.path.join(EXT, 'moves', 'reversals.json'), 'w'), indent=1)
print("reversals: 6 files dumped (format undocumented in VPWStudio)")

# ---------- 7. Font glyph sheets ----------
os.makedirs(os.path.join(EXT, 'ui', 'fonts'), exist_ok=True)
font_sheets = []
for fid, (t, label) in sorted(db.items()):
    if t not in ('AkiLargeFont', 'AkiSmallFont') or fid > 0x4C02:
        continue
    d = get(fid)
    if t == 'AkiLargeFont':
        cw, chh, hdr, term = 24, 22, 3, True
    else:
        cw, chh, hdr, term = 16, 14, 2, False
    char_bytes = chh * cw // 8
    glyphs, o = [], 0
    while o < len(d):
        h = d[o:o + hdr]
        if term and len(h) == 3 and h[2] == 0x0A:
            break
        if o + hdr + char_bytes > len(d):
            break
        glyphs.append({"header": h.hex(), "pixels": d[o + hdr:o + hdr + char_bytes].hex()})
        o += hdr + char_bytes
    # render sheet: 16 glyphs per row
    cols = 16
    rows_n = (len(glyphs) + cols - 1) // cols
    W, H = cols * (cw + 2), rows_n * (chh + 2)
    rgba = bytearray(W * H * 4)
    for i, g in enumerate(glyphs):
        px = bytes.fromhex(g["pixels"])
        gx, gy = (i % cols) * (cw + 2), (i // cols) * (chh + 2)
        for y in range(chh):
            for x in range(cw):
                bit = (px[(y * cw + x) // 8] >> (7 - ((y * cw + x) % 8))) & 1
                v = 255 if bit else 0
                o4 = ((gy + y) * W + (gx + x)) * 4
                rgba[o4:o4 + 4] = bytes((v, v, v, 255))
    fn = f"font_{fid:04X}_{t.lower()}.png"
    write_png(os.path.join(EXT, 'ui', 'fonts', fn), W, H, bytes(rgba))
    font_sheets.append({"file_id": hex(fid), "type": t, "glyphs": len(glyphs),
                        "char_size": f"{cw}x{chh}", "sheet": fn})
    print(f"font {fid:04X} {t}: {len(glyphs)} glyphs {cw}x{chh}")
json.dump(font_sheets, open(os.path.join(EXT, 'ui', 'fonts', 'fonts.json'), 'w'), indent=1)

# ---------- 8. Archive entry analysis ----------
a = get(0x00F7)
offs = [struct.unpack('>I', a[4 + i * 4:8 + i * 4])[0] for i in range(4)]
arch = []
for i, o in enumerate(offs):
    end = offs[i + 1] if i + 1 < 4 else len(a)
    blob = a[o:end]
    arch.append({"index": i, "offset": o, "size": len(blob),
                 "ff_fraction": round(sum(1 for b in blob if b == 0xFF) / max(1, len(blob)), 3),
                 "zero_fraction": round(sum(1 for b in blob if b == 0) / max(1, len(blob)), 3),
                 "first64": blob[:64].hex(), "last64": blob[-64:].hex()})
    print(f"archive entry {i}: size={len(blob)} ff={arch[-1]['ff_fraction']} zero={arch[-1]['zero_fraction']}")
misc = json.load(open(os.path.join(EXT, 'misc', 'ui-misc.json')))
misc["archives"][0]["entry_analysis"] = arch
json.dump(misc, open(os.path.join(EXT, 'misc', 'ui-misc.json'), 'w'), indent=1)

# ---------- 9. Sequence magic check ----------
snd = json.load(open(os.path.join(EXT, 'sound', 'sound.json')))
for s in snd["sequences"]:
    blob = open(os.path.join(EXT, 'sound', 'sequences', s["file"]), 'rb').read()
    s["magic_verified"] = blob[:4].hex()
print("seq magics:", Counter(s["magic_verified"] for s in snd["sequences"]))

# ---------- 10. Rename sound banks to neutral names ----------
rename = {"bank1_proset": "bank1", "bank2_sepack": "bank2", "bank3_music": "bank3"}
for old, new in rename.items():
    os.rename(os.path.join(EXT, 'sound', old), os.path.join(EXT, 'sound', new))
    d = os.path.join(EXT, 'sound', new)
    for fn in os.listdir(d):
        if fn.startswith(old):
            os.rename(os.path.join(d, fn), os.path.join(d, fn.replace(old, new, 1)))
for b in snd["banks"]:
    b["bank"] = rename[b["bank"]]
    for e in b.get("entries", []):
        if "file" in e:
            e["file"] = e["file"].replace("bank1_proset", "bank1").replace(
                "bank2_sepack", "bank2").replace("bank3_music", "bank3")
json.dump(snd, open(os.path.join(EXT, 'sound', 'sound.json'), 'w'), indent=1)
print("sound banks renamed to bank1/bank2/bank3")
print("DONE")
