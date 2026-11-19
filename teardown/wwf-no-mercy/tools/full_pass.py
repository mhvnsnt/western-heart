#!/usr/bin/env python3
"""No Mercy full-ROM catalogue + data extraction (W3c-correct window).

Single decode pass over all 19,458 files:
- file-table.csv: fid, offset, len, encoded, decoded_len, db_type, db_label,
  magic8, verified, verify_note
- verifies every file's content against its VPWStudio DB type
- extracts: move tables, shop/nogroup menus, AkiText strings, AkiArchive,
  MenuBackground PNGs, Ci4Background analysis, font dumps
- sound: parses the 3 N64 PtrTablesV2 banks + VADPCM-decodes every wave to WAV
- sequences: dumps the 27 Sng sequences + 2 Binary FX from gameconfigmidi.ini

Sources: VPWStudio (AKI-Club, MIT) for file formats; SubDrag N64SoundLibrary
(N64AIFCAudio.cpp ReadAudioN64PtrWavetableV2 + decode/decode_8) for audio.
"""
import csv, json, os, re, struct, sys, zlib
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from lzss import asmik_decode

# Repo layout: FR is the teardown dir (parent of tools/); outputs land
# directly in its moves/, sound/, ui/, misc/, caw/ subdirs.
FR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The ROM is never committed; place WWF No Mercy (USA) (Rev-A).z64
# next to tools/ (the same convention as extract_all_models.py).
ROM = os.path.join(FR, "WWF No Mercy (USA) (Rev-A).z64")
FT, FIRST, NENT = 0x16C31D8, 0x1BD150, 19459
DB = os.path.join(FR, "tools", "NoMercy-FileTableDB.txt")
EXT = FR

def s8(v):
    return v - 0x100 if v & 0x80 else v

def rgba5551(v):
    r = (v >> 11) & 0x1F; g = (v >> 6) & 0x1F; b = (v >> 1) & 0x1F
    a = 255 if (v & 1) else 0
    return ((r << 3) | (r >> 2), (g << 3) | (g >> 2), (b << 3) | (b >> 2), a)

def write_png(path, w, h, rgba):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    rows = b''.join(b'\x00' + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                           chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))

# ---------------- verifiers ----------------
def verify_model(dec):
    if len(dec) < 8:
        return False, "too short"
    nv, nf = dec[1] & 0x7F, dec[2] & 0x7F
    expect = 8 + nv * 8 + nf * 3
    if expect == len(dec):
        return True, f"verts={nv} faces={nf}"
    if expect == len(dec) - 1 and dec[-1] == 0:
        return True, f"verts={nv} faces={nf} (+1 pad byte)"
    return False, f"len mismatch: header expects {expect}, file is {len(dec)}"

def verify_anim(dec):
    if len(dec) < 4:
        return False, "too short"
    if (len(dec) - 4) % 98 == 0:
        return True, f"frames={(len(dec) - 4) // 98} toki2={dec[:4].hex()}"
    return False, f"(len-4)%98={(len(dec) - 4) % 98}"

def verify_akitex(dec):
    if dec[:4] == b'TEX\x00':
        w, h = struct.unpack('>HH', dec[4:8])
        return True, f"{w}x{h} fmt={dec[8]}"
    return False, "no TEX magic"

def verify_ci(dec, want):
    if len(dec) < 8:
        return False, "too short"
    w, h = dec[0] + 1, dec[1] + 1
    if want == 8 and len(dec) == 8 + w * h:
        return True, f"{w}x{h}"
    if want == 4 and len(dec) == 8 + (w * h) // 2:
        return True, f"{w}x{h}"
    return False, f"dim header {w}x{h} vs len {len(dec)}"

def verify_pal(dec, want):
    if len(dec) == want:
        return True, f"{want // 2} colors"
    return False, f"len {len(dec)} != {want}"

# ---------------- parsers ----------------
def parse_moves(dec):
    """MenuItems_Moves: u8 count, entries of 11B header + NUL name."""
    if not dec:
        return None, "empty"
    n = dec[0]
    entries, o = [], 1
    for _ in range(n):
        if o + 11 > len(dec):
            return None, f"truncated at entry {len(entries)}"
        dmg = dec[o]
        prev, link, anim, rep, master = struct.unpack('>hhhhh', dec[o + 1:o + 11])
        j = dec.find(b'\x00', o + 11)
        if j < 0:
            return None, f"unterminated name at entry {len(entries)}"
        name = dec[o + 11:j].decode('shift_jis', 'replace')
        entries.append({"damage_info": dmg, "preview_pos": prev,
                        "move_link": link, "anim_id": anim,
                        "anim_file_id": hex(anim + 0x3322) if anim >= 0 else None,
                        "repeat_anim_id": rep, "master_move_id": master,
                        "name": name})
        o = j + 1
    return {"count": n, "entries": entries, "consumed": o,
            "trailing": len(dec) - o}, None

def parse_shop(dec):
    """MenuItems_Shop: entries until EOF: u32 price, u8 unlock, u8 type,
    u16 itemdata, u16 pad, NUL name, NUL description."""
    entries, o = [], 0
    while o < len(dec):
        if o + 10 > len(dec):
            return None, f"truncated header at {o}"
        price = struct.unpack('>I', dec[o:o + 4])[0]
        unlock, itype = dec[o + 4], dec[o + 5]
        itemdata = struct.unpack('>H', dec[o + 6:o + 8])[0]
        j = dec.find(b'\x00', o + 10)
        if j < 0:
            return None, f"unterminated name at {o}"
        name = dec[o + 10:j].decode('shift_jis', 'replace')
        k = dec.find(b'\x00', j + 1)
        if k < 0:
            return None, f"unterminated desc at {o}"
        desc = dec[j + 1:k].decode('shift_jis', 'replace')
        entries.append({"price": price, "unlock_id": unlock,
                        "item_type": itype, "item_type_name":
                        {0x43: "attire", 0x57: "wrestler", 0x4D: "move"}.get(itype, "?"),
                        "item_data": itemdata, "name": name, "description": desc})
        o = k + 1
    return {"count": len(entries), "entries": entries}, None

def parse_nogroup(dec):
    """MenuItems_NoGroup: u8 count, entries of u8 key + NUL name."""
    if not dec:
        return None, "empty"
    n = dec[0]
    entries, o = [], 1
    for _ in range(n):
        if o >= len(dec):
            return None, "truncated"
        key = dec[o]
        j = dec.find(b'\x00', o + 1)
        if j < 0:
            return None, "unterminated name"
        entries.append({"key": key, "name": dec[o + 1:j].decode('shift_jis', 'replace')})
        o = j + 1
    return {"count": n, "entries": entries, "trailing": len(dec) - o}, None

def parse_akitext(dec):
    """AkiText: u16be pointer table; first pointer = table size; strings at
    each nonzero pointer, NUL-terminated (some files end implicitly)."""
    if len(dec) < 2:
        return None, "too short"
    table_size = struct.unpack('>H', dec[0:2])[0]
    if table_size > len(dec) or table_size % 2:
        return None, f"bad table size {table_size}"
    ptrs = []
    for o in range(0, table_size, 2):
        p = struct.unpack('>H', dec[o:o + 2])[0]
        if p:
            ptrs.append(p)
    entries = []
    for p in ptrs:
        if p >= len(dec):
            entries.append({"ptr": p, "text": None, "note": "pointer at/past EOF"})
            continue
        j = dec.find(b'\x00', p)
        raw = dec[p:] if j < 0 else dec[p:j]
        entries.append({"ptr": p, "text": raw.decode('shift_jis', 'replace')})
    return {"table_size": table_size, "n_pointers": len(ptrs),
            "entries": entries}, None

def parse_archive(dec):
    """AkiArchive: u32be count, count x u32be offsets, entries DW-aligned."""
    if len(dec) < 4:
        return None, "too short"
    n = struct.unpack('>I', dec[0:4])[0]
    if n > 1000 or 4 + n * 4 > len(dec):
        return None, f"implausible count {n}"
    offs = [struct.unpack('>I', dec[4 + i * 4:8 + i * 4])[0] for i in range(n)]
    entries = []
    for i, o in enumerate(offs):
        end = offs[i + 1] if i + 1 < n else len(dec)
        entries.append({"index": i, "offset": o, "size": max(0, end - o),
                        "first16": dec[o:o + 16].hex() if 0 <= o < len(dec) else None})
    return {"count": n, "offsets": offs, "entries": entries}, None

# ---------------- VADPCM (port of N64SoundLibrary decode/decode_8) ----------------
ITABLE = [0, 1, 2, 3, 4, 5, 6, 7, -8, -7, -6, -5, -4, -3, -2, -1]

def sign_extend(b, x):
    x &= (1 << b) - 1
    m = 1 << (b - 1)
    return (x ^ m) - m

def _decode_8(data, pos, out, index, pred1, lastsmp):
    """Decode 8 samples from 4 bytes at data[pos]; appends to out list;
    updates lastsmp (list of 8) in place. Returns new pos."""
    pred2 = pred1[8:16]
    tmp = []
    p = pos
    for i in range(8):
        if i & 1:
            nib = data[p] & 0x0F
            p += 1
        else:
            nib = (data[p] >> 4) & 0x0F
        tmp.append(sign_extend(index + 4, ITABLE[nib] << index))
    for i in range(8):
        total = pred1[i] * lastsmp[6] + pred2[i] * lastsmp[7]
        for x in range(i - 1, -1, -1):
            total += tmp[(i - 1) - x] * pred2[x]
        v = ((tmp[i] << 11) + total) >> 11
        out.append(-32768 if v < -32768 else (32767 if v > 32767 else v))
    lastsmp[:] = out[-8:]
    return p

def vadpcm_decode(data, book_order, book_npred, predictors):
    """data: VADPCM bytes (multiple of 9). Returns list of s16 samples."""
    out = []
    lastsmp = [0] * 8
    n = (len(data) // 9) * 9
    i = 0
    while i < n:
        hdr = data[i]
        index = (hdr >> 4) & 0xF
        pred = (hdr & 0xF) % max(1, book_npred)
        pred1 = predictors[pred * 16:pred * 16 + 16]
        i = _decode_8(data, i + 1, out, index, pred1, lastsmp)
        i = _decode_8(data, i, out, index, pred1, lastsmp)
    return out

def write_wav(path, samples, rate=22050):
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack('<%dh' % len(samples), *samples))

def parse_sound_bank(rom, ptr_off, tbl_off, bank_name):
    """Parse one N64 PtrTablesV2 bank. Returns (manifest_entries, stats)."""
    ctl = rom[ptr_off:tbl_off]  # ctl runs up to the wavetable start
    assert ctl[:15] == b'N64 PtrTablesV2', f"bad magic at {ptr_off:#x}"
    tbl = rom[tbl_off:]
    assert tbl[:14] == b'N64 WaveTables', f"bad tbl magic at {tbl_off:#x}"
    name = ctl[0x14:0x20].split(b'\x00')[0].decode('ascii', 'replace')
    count = struct.unpack('>I', ctl[0x20:0x24])[0]
    end_offsets = struct.unpack('>I', ctl[0x24:0x28])[0]
    end_extra = struct.unpack('>I', ctl[0x28:0x2C])[0]
    bank_offset = struct.unpack('>I', ctl[0x2C:0x30])[0]
    entries = []
    for x in range(count):
        ioff = struct.unpack('>I', ctl[bank_offset + x * 4:bank_offset + x * 4 + 4])[0]
        vol = ctl[end_offsets + x] if end_offsets + x < len(ctl) else None
        pan = ctl[end_extra + x] if end_extra + x < len(ctl) else None
        if ioff == 0:
            entries.append({"index": x, "empty": True, "volume": vol, "pan": pan})
            continue
        base, ln = struct.unpack('>II', ctl[ioff:ioff + 8])
        loop_off, pred_off = struct.unpack('>II', ctl[ioff + 0xC:ioff + 0x14])
        loop = None
        if loop_off:
            ls, le, lc = struct.unpack('>III', ctl[loop_off:loop_off + 12])
            loop = {"start": ls, "end": le, "count": lc}
        book = None
        if pred_off:
            order, npred = struct.unpack('>II', ctl[pred_off:pred_off + 8])
            ncoef = order * npred * 8
            coefs = list(struct.unpack('>%dh' % ncoef,
                                       ctl[pred_off + 8:pred_off + 8 + ncoef * 2]))
            book = {"order": order, "npredictors": npred, "predictors": coefs}
        entries.append({"index": x, "empty": False, "volume": vol, "pan": pan,
                        "wav_base": base, "wav_len": ln, "loop": loop,
                        "book": book,
                        "ctl_offset": ioff})
    return {"bank": bank_name, "name": name, "ptr_offset": hex(ptr_off),
            "tbl_offset": hex(tbl_off), "count": count,
            "ctl_size": len(ctl), "entries": entries}, tbl

# ---------------- main pass ----------------
def load_db(path):
    db = {}
    for line in open(path):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', s)
        if m:
            db[int(m.group(1), 16)] = (m.group(2), m.group(3))
    return db

def main():
    rom = open(ROM, 'rb').read()
    print(f"ROM {len(rom)} bytes CRC32 {zlib.crc32(rom) & 0xFFFFFFFF:08X}")
    table = struct.unpack(f'>{NENT}I', rom[FT:FT + NENT * 4])
    db = load_db(DB)

    def get(fid):
        loc, enc = table[fid - 1] & ~1, table[fid - 1] & 1
        nloc = table[fid] & ~1
        return rom[FIRST + loc:FIRST + nloc], enc, FIRST + loc

    os.makedirs(os.path.join(EXT, 'ui', 'menubg'), exist_ok=True)
    os.makedirs(os.path.join(EXT, 'misc', 'archive'), exist_ok=True)
    os.makedirs(os.path.join(EXT, 'misc', 'fonts'), exist_ok=True)
    os.makedirs(os.path.join(EXT, 'misc', 'ci4bg'), exist_ok=True)
    os.makedirs(os.path.join(EXT, 'moves'), exist_ok=True)
    os.makedirs(os.path.join(EXT, 'sound', 'sequences'), exist_ok=True)

    rows = []
    verify_stats = defaultdict(Counter)
    binary_magics = Counter()
    binary_notes = []
    moves_all, moves_files = [], []
    shop_all, nogroup_all, akitext_all = [], [], []
    archive_info, font_info, ci4bg_info, menubg_info = [], [], [], []

    for fid in range(1, 19459):
        raw, enc, off = get(fid)
        dec = asmik_decode(raw) if enc else raw
        typ, label = db.get(fid, ('<no-db>', ''))
        magic8 = dec[:8].hex()
        ok, note = True, ''
        if typ == 'AkiModel':
            ok, note = verify_model(dec)
        elif typ == 'AkiAnimation':
            ok, note = verify_anim(dec)
        elif typ == 'AkiTexture':
            ok, note = verify_akitex(dec)
        elif typ == 'Ci8Texture':
            ok, note = verify_ci(dec, 8)
        elif typ == 'Ci4Texture':
            ok, note = verify_ci(dec, 4)
        elif typ == 'Ci8Palette':
            ok, note = verify_pal(dec, 512)
        elif typ == 'Ci4Palette':
            ok, note = verify_pal(dec, 32)
        elif typ == 'I4Texture':
            m = re.search(r'\|w:(\d+),h:(\d+)', label)
            if m and len(dec) * 2 == int(m.group(1)) * int(m.group(2)):
                ok, note = True, f"{m.group(1)}x{m.group(2)}"
            else:
                ok, note = False, f"label dims vs len {len(dec)}"
        elif typ == 'MenuItems_Moves':
            parsed, err = parse_moves(dec)
            if parsed is None:
                ok, note = False, err
            else:
                ok, note = True, f"{parsed['count']} entries, trailing={parsed['trailing']}"
                cat = re.match(r'\[([^\]]*)\]', label)
                for i, e in enumerate(parsed['entries']):
                    e2 = dict(e, file_id=hex(fid), file_index=i,
                              category=cat.group(1) if cat else '',
                              menu_label=label)
                    moves_all.append(e2)
                moves_files.append({"file_id": hex(fid), "label": label,
                                    "count": parsed['count'],
                                    "trailing": parsed['trailing'],
                                    "entries": parsed['entries']})
        elif typ == 'MenuItems_Shop':
            parsed, err = parse_shop(dec)
            if parsed is None:
                ok, note = False, err
            else:
                ok, note = True, f"{parsed['count']} items"
                shop_all.append({"file_id": hex(fid), "label": label, **parsed})
        elif typ == 'MenuItems_NoGroup':
            parsed, err = parse_nogroup(dec)
            if parsed is None:
                ok, note = False, err
            else:
                ok, note = True, f"{parsed['count']} entries"
                nogroup_all.append({"file_id": hex(fid), "label": label, **parsed})
        elif typ == 'AkiText':
            parsed, err = parse_akitext(dec)
            if parsed is None:
                ok, note = False, err
            else:
                ok, note = True, f"{parsed['n_pointers']} strings"
                akitext_all.append({"file_id": hex(fid), "label": label, **parsed})
        elif typ == 'AkiArchive':
            parsed, err = parse_archive(dec)
            if parsed is None:
                ok, note = False, err
            else:
                ok, note = True, f"{parsed['count']} entries"
                for e in parsed['entries']:
                    o, sz = e['offset'], e['size']
                    blob = dec[o:o + sz] if 0 <= o < len(dec) else b''
                    open(os.path.join(EXT, 'misc', 'archive',
                                      f"archive_{fid:04X}_{e['index']}.bin"), 'wb').write(blob)
                archive_info.append({"file_id": hex(fid), "label": label, **parsed})
        elif typ == 'MenuBackground':
            # 32B CI4 palette + 40 chunks of 64x30 CI4 = 320x240
            if len(dec) == 32 + 40 * 960:
                pal = [rgba5551(v) for v in struct.unpack('>16H', dec[:32])]
                rgba = bytearray(320 * 240 * 4)
                for c in range(40):
                    cx, cy = (c % 5) * 64, (c // 5) * 30
                    chunk = dec[32 + c * 960:32 + (c + 1) * 960]
                    for i in range(64 * 30):
                        idx = (chunk[i // 2] >> 4) & 0xF if i % 2 == 0 else chunk[i // 2] & 0xF
                        px, py = cx + (i % 64), cy + (i // 64)
                        o4 = (py * 320 + px) * 4
                        rgba[o4:o4 + 4] = bytes(pal[idx])
                fn = f"menubg_{fid:04X}.png"
                write_png(os.path.join(EXT, 'ui', 'menubg', fn), 320, 240, bytes(rgba))
                ok, note = True, "320x240 rendered"
                menubg_info.append({"file_id": hex(fid), "label": label, "file": fn})
            else:
                ok, note = False, f"decoded len {len(dec)} != 38432"
        elif typ == 'Ci4Background':
            open(os.path.join(EXT, 'misc', 'ci4bg', f"ci4bg_{fid:04X}.bin"), 'wb').write(dec)
            ci4bg_info.append({"file_id": hex(fid), "label": label,
                               "decoded_len": len(dec), "first32": dec[:32].hex()})
            ok, note = True, f"decoded {len(dec)}B dumped"
        elif typ in ('AkiLargeFont', 'AkiSmallFont'):
            open(os.path.join(EXT, 'misc', 'fonts', f"font_{fid:04X}.bin"), 'wb').write(dec)
            font_info.append({"file_id": hex(fid), "label": label, "type": typ,
                              "decoded_len": len(dec), "first32": dec[:32].hex()})
            ok, note = True, f"decoded {len(dec)}B dumped"
        elif typ == 'RawCi4TexPal':
            ok, note = True, f"raw len {len(dec)}"
        elif typ == 'Binary':
            if dec[:4] == b'\x00\x00\x02\x15':
                binary_magics['sng_sequence (00 00 02 15)'] += 1
                ok, note = True, "Sng music sequence"
            elif dec[:4] == b'TEX\x00':
                binary_magics['TEX container'] += 1
                ok, note = False, "has TEX magic but labeled Binary"
            else:
                printable = sum(1 for b in dec[:256] if 32 <= b < 127 or b in (0, 10))
                binary_magics['other'] += 1
                ok, note = True, f"no known magic (printable {printable}/256 in head)"
                if len(dec) > 10000:
                    binary_notes.append({"file_id": hex(fid), "label": label,
                                         "len": len(dec), "head": dec[:32].hex()})
        elif typ == '<no-db>':
            ok, note = False, "no DB entry"
        verify_stats[typ]['ok' if ok else 'BAD'] += 1
        rows.append({"fid": fid, "fid_hex": f"{fid:04X}", "rom_offset": f"0x{off:08X}",
                     "length": len(raw), "encoded": int(enc),
                     "decoded_len": len(dec), "db_type": typ,
                     "db_label": label, "magic8": magic8,
                     "verified": "yes" if ok else "NO", "verify_note": note})

    # ---- write catalogue CSV ----
    with open(os.path.join(FR, 'file-table.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"catalogue: {len(rows)} rows")

    # ---- moves ----
    json.dump({"files": moves_files, "total_entries": len(moves_all)},
              open(os.path.join(EXT, 'moves', 'moves.json'), 'w'), indent=1)
    with open(os.path.join(EXT, 'moves', 'moves.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=["file_id", "file_index", "category",
                                          "name", "damage_info", "preview_pos",
                                          "move_link", "anim_id", "anim_file_id",
                                          "repeat_anim_id", "master_move_id"])
        w.writeheader()
        for e in moves_all:
            w.writerow({k: e.get(k, '') for k in w.fieldnames})
    print(f"moves: {len(moves_files)} files, {len(moves_all)} entries")

    # ---- ui data ----
    json.dump(shop_all, open(os.path.join(EXT, 'ui', 'shop.json'), 'w'), indent=1)
    json.dump(nogroup_all, open(os.path.join(EXT, 'ui', 'nogroup.json'), 'w'), indent=1)
    json.dump(akitext_all, open(os.path.join(EXT, 'ui', 'akitext.json'), 'w'), indent=1)
    json.dump({"archives": archive_info, "fonts": font_info,
               "ci4backgrounds": ci4bg_info, "menubackgrounds": menubg_info},
              open(os.path.join(EXT, 'misc', 'ui-misc.json'), 'w'), indent=1)
    print(f"shop: {len(shop_all)} files, nogroup: {len(nogroup_all)}, "
          f"akitext: {len(akitext_all)} files, "
          f"{sum(a['n_pointers'] for a in akitext_all)} strings")

    # ---- sound banks ----
    sound_manifest = {"banks": []}
    banks = [("bank1_proset", 0x16F32A0, 0x16F6F10),
             ("bank2_sepack", 0x1858030, 0x185EDB0),
             ("bank3_music", 0x1967410, 0x1969880)]
    for bname, ptr_off, tbl_off in banks:
        info, tbl = parse_sound_bank(rom, ptr_off, tbl_off, bname)
        outdir = os.path.join(EXT, 'sound', bname)
        os.makedirs(outdir, exist_ok=True)
        n_wav, n_empty = 0, 0
        for e in info['entries']:
            if e['empty']:
                n_empty += 1
                continue
            base, ln = e['wav_base'], e['wav_len']
            blob = tbl[base:base + ln]
            book = e['book']
            samples = vadpcm_decode(blob, book['order'], book['npredictors'],
                                    book['predictors']) if book else []
            fn = f"{bname}_{e['index']:03d}.wav"
            write_wav(os.path.join(outdir, fn), samples)
            e['file'] = fn
            e['samples'] = len(samples)
            e['duration_s'] = round(len(samples) / 22050, 3)
            e['adpcm_order'] = book['order']
            e['adpcm_npredictors'] = book['npredictors']
            del e['book']
            n_wav += 1
        info['wavs'] = n_wav
        info['empty_slots'] = n_empty
        sound_manifest['banks'].append(info)
        print(f"sound {bname}: {info['count']} slots, {n_wav} WAVs, {n_empty} empty")

    # ---- Sng sequences (gameconfigmidi.ini U V1.1) ----
    seqs = [(0x29FBB8, 0x2A0A42), (0x2A0A42, 0x2A0C96), (0x2A0C96, 0x2A0F9C),
            (0x2A0F9C, 0x2A466A), (0x2A466A, 0x2A4B80), (0x2A4B80, 0x2AB5B4),
            (0x2AB5B4, 0x2AD706), (0x2AD706, 0x2AEBB4), (0x2AEBB4, 0x2B27EE),
            (0x2B27EE, 0x2B389C), (0x2B389C, 0x2B6C96), (0x2B6C96, 0x2B978C),
            (0x2B978C, 0x2B9A72), (0x2B9A72, 0x2BA210), (0x2BA210, 0x2BAB60),
            (0x2BAB60, 0x2BBA1A), (0x2BBA1A, 0x2BCE20), (0x2BCE20, 0x2BD5AA),
            (0x2BD5AA, 0x2BE1AE), (0x2BE1AE, 0x2BE85A), (0x2BE85A, 0x2BECF0),
            (0x2BECF0, 0x2BF0AA), (0x2BF0AA, 0x2BF44A), (0x2BF44A, 0x2BFB46),
            (0x2BFB46, 0x2C037A), (0x2C037A, 0x2C32E2), (0x2C32E2, 0x2C352E)]
    fx = [(0x1855F90, 0x185802A), (0x1965C50, 0x196740C)]
    seq_info = []
    for i, (a, b) in enumerate(seqs):
        blob = rom[a:b]
        fn = f"seq_{i:02d}_{a:06X}.sng"
        open(os.path.join(EXT, 'sound', 'sequences', fn), 'wb').write(blob)
        # containing file id(s)
        fids = [fid for fid in range(1, 19459)
                if FIRST + (table[fid - 1] & ~1) <= a < FIRST + (table[fid] & ~1)]
        seq_info.append({"index": i, "file": fn, "rom_range": [hex(a), hex(b)],
                         "len": len(blob), "magic": blob[:4].hex(),
                         "in_file_id": [hex(f) for f in fids]})
    for i, (a, b) in enumerate(fx):
        blob = rom[a:b]
        fn = f"binaryfx_{i}_{a:06X}.sng"
        open(os.path.join(EXT, 'sound', 'sequences', fn), 'wb').write(blob)
        seq_info.append({"index": f"fx{i}", "file": fn, "rom_range": [hex(a), hex(b)],
                         "len": len(blob), "magic": blob[:4].hex(),
                         "in_file_id": []})
    sound_manifest['sequences'] = seq_info
    json.dump(sound_manifest, open(os.path.join(EXT, 'sound', 'sound.json'), 'w'), indent=1)
    print(f"sequences: {len(seqs)} Sng + {len(fx)} Binary FX dumped")

    # ---- summary ----
    summary = {
        "verify_by_type": {t: dict(c) for t, c in verify_stats.items()},
        "binary_magics": dict(binary_magics),
        "binary_large_unidentified": binary_notes,
        "moves_total": len(moves_all),
        "moves_files": len(moves_files),
        "akitext_strings": sum(a['n_pointers'] for a in akitext_all),
        "sound_banks": [{k: v for k, v in b.items() if k != 'entries'}
                        for b in sound_manifest['banks']],
    }
    json.dump(summary, open(os.path.join(FR, 'work', 'full-pass-summary.json'), 'w'), indent=1)
    print("verify summary:")
    for t, c in sorted(verify_stats.items()):
        print(f"  {t:20s} ok={c['ok']:5d} BAD={c['BAD']:4d}")
    print("binary magics:", dict(binary_magics))
    print("DONE")

if __name__ == '__main__':
    main()
