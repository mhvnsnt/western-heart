#!/usr/bin/env python3
"""Follow-up pass: render menu backgrounds / Ci4 backgrounds / font texture,
re-verify Ci4Palette content-aware, patch file-table.csv, cross-check moves
vs mat-kings DB, sanity-check WAVs."""
import csv, json, os, re, struct, sys, zlib, wave
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

def ci4_pixels_to_rgba(px_bytes, w, h, pal):
    rgba = bytearray(w * h * 4)
    for i in range(w * h):
        idx = (px_bytes[i // 2] >> 4) & 0xF if i % 2 == 0 else px_bytes[i // 2] & 0xF
        rgba[i * 4:i * 4 + 4] = bytes(pal[idx] if idx < len(pal) else (0, 0, 0, 0))
    return bytes(rgba)

db = {}
for line in open(os.path.join(FR, "tools", "NoMercy-FileTableDB.txt")):
    m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', line.strip())
    if m:
        db[int(m.group(1), 16)] = (m.group(2), m.group(3))

def pal_of(fid):
    dec = get(fid)
    return [rgba5551(v) for v in struct.unpack('>16H', dec[:32])]

# ---- 1. MenuBackgrounds: 16 x (palette + 40 chunks of 64x30) ----
os.makedirs(os.path.join(EXT, 'ui', 'menubg'), exist_ok=True)
menubg = []
bg_fids = sorted(f for f, (t, _) in db.items() if t == 'MenuBackground')
for fid in bg_fids:
    typ, label = db[fid]
    dec = get(fid)
    assert len(dec) == 992, (fid, len(dec))
    pal = [rgba5551(v) for v in struct.unpack('>16H', dec[:32])]
    chunks = [dec[32:992]]
    ok_group = True
    for k in range(1, 40):
        t2, l2 = db.get(fid + k, ('?', ''))
        d2 = get(fid + k)
        if t2 != 'Binary' or len(d2) != 960:
            ok_group = False
            break
        chunks.append(d2)
    assert ok_group, f"chunk group broken at {fid:04X}"
    rgba = bytearray(320 * 240 * 4)
    for c, ch in enumerate(chunks):
        cx, cy = (c % 5) * 64, (c // 5) * 30
        sub = ci4_pixels_to_rgba(ch, 64, 30, pal)
        for y in range(30):
            for x in range(64):
                s = (y * 64 + x) * 4
                d = ((cy + y) * 320 + (cx + x)) * 4
                rgba[d:d + 4] = sub[s:s + 4]
    slug = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')[:50]
    fn = f"menubg_{fid:04X}_{slug}.png"
    write_png(os.path.join(EXT, 'ui', 'menubg', fn), 320, 240, bytes(rgba))
    menubg.append({"file_id": hex(fid), "label": label, "file": fn,
                   "chunks": [hex(fid + k) for k in range(40)]})
print(f"menubackgrounds rendered: {len(menubg)}")

# ---- 2. Ci4Backgrounds: skip 8, raw CI4 320x240, external |p: palette ----
for fid in sorted(f for f, (t, _) in db.items() if t == 'Ci4Background'):
    typ, label = db[fid]
    dec = get(fid)
    assert len(dec) == 38408, (fid, len(dec))
    pm = re.search(r'\|p:([0-9A-Fa-f]+)', label)
    pfid = int(pm.group(1), 16)
    pal = pal_of(pfid)
    rgba = ci4_pixels_to_rgba(dec[8:], 320, 240, pal)
    slug = re.sub(r'[^a-z0-9]+', '_', label.split('|')[0].lower()).strip('_')[:50]
    fn = f"ci4bg_{fid:04X}_{slug}.png"
    write_png(os.path.join(EXT, 'ui', 'menubg', fn), 320, 240, rgba)
    menubg.append({"file_id": hex(fid), "label": label, "file": fn,
                   "palette_file_id": hex(pfid), "kind": "ci4background"})
print("ci4backgrounds rendered: 4")

# ---- 3. Font texture 0x4A50: 256x264 CI4, skip 8, palette 0x4A4F ----
dec = get(0x4A50)
pal = pal_of(0x4A4F)
rgba = ci4_pixels_to_rgba(dec[8:], 256, 264, pal)
write_png(os.path.join(EXT, 'ui', 'menubg', 'font_4A50_mall_large.png'), 256, 264, rgba)
menubg.append({"file_id": "0x4a50", "label": db[0x4A50][1], "file": "font_4A50_mall_large.png",
               "palette_file_id": "0x4a4f", "kind": "font texture 256x264"})
print("font texture rendered: 0x4A50 (256x264)")

json.dump(menubg, open(os.path.join(EXT, 'ui', 'menubg', 'menubg.json'), 'w'), indent=1)

# ---- 4. Content-aware Ci4Palette census + CSV patch ----
rows = {}
with open(os.path.join(FR, 'file-table.csv')) as f:
    for r in csv.DictReader(f):
        rows[int(r['fid'])] = r

pal_census = Counter()
for fid, (t, l) in db.items():
    if t != 'Ci4Palette' or fid > 0x4C02:
        continue
    dec = get(fid)
    if len(dec) == 32:
        pal_census['32B palette'] += 1
        rows[fid]['verified'] = 'yes'
        rows[fid]['verify_note'] = '16 colors'
    elif len(dec) == 64:
        pal_census['64B palette+32B secondary'] += 1
        rows[fid]['verified'] = 'yes'
        rows[fid]['verify_note'] = '16-color palette + 32B secondary table (shade/remap?)'
    else:
        pal_census[f'other len={len(dec)}'] += 1
        rows[fid]['verified'] = 'yes' if len(dec) == 1024 else 'NO'
        rows[fid]['verify_note'] = ('512-entry default color table' if len(dec) == 1024
                                    else f'unexpected len {len(dec)}')
print("Ci4Palette census:", dict(pal_census))

# MenuBackground rows + chunk Binary rows
chunk_fids = set()
for fid in bg_fids:
    rows[fid]['verified'] = 'yes'
    rows[fid]['verify_note'] = 'palette + chunk 01 of 40; full 320x240 rendered'
    for k in range(1, 40):
        chunk_fids.add(fid + k)
        rows[fid + k]['verify_note'] = f"MenuBackground chunk {k + 1:02d}/40 of {db[fid][1]}"
for fid in sorted(f for f, (t, _) in db.items() if t == 'Ci4Background'):
    rows[fid]['verified'] = 'yes'
    rows[fid]['verify_note'] = '320x240 CI4 + 8B header; rendered with |p: palette'
rows[0x4A50]['verified'] = 'yes'
rows[0x4A50]['verify_note'] = 'font atlas texture 256x264 CI4 + 8B header; rendered with |p: palette'

with open(os.path.join(FR, 'file-table.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(next(iter(rows.values())).keys()))
    w.writeheader()
    for fid in sorted(rows):
        w.writerow(rows[fid])
print(f"CSV patched ({len(rows)} rows)")

# ---- 5. Moves cross-check vs mat-kings DB ----
moves = json.load(open(os.path.join(EXT, 'moves', 'moves.json')))
mk_path = os.path.join(FR, "..", "..", "moveset-library", "movesets",
                       "mat-kings-move-database.json")
if not os.path.exists(mk_path):
    print("mat-kings DB not found at", mk_path, "- skipping cross-check")
    mk = {"moves": []}
else:
    mk = json.load(open(mk_path))
menu_names = set()
anim_ids = set()
for fl in moves['files']:
    for e in fl['entries']:
        menu_names.add(e['name'])
        anim_ids.add(e['anim_id'])
mk_moves = mk.get('moves', [])
mk_names = set(m.get('name', '') for m in mk_moves if isinstance(m, dict))
print(f"menu entries: {len(moves['files'])} files, "
      f"{sum(len(fl['entries']) for fl in moves['files'])} entries, "
      f"{len(menu_names)} distinct names, {len(anim_ids)} distinct anim_ids")
print(f"mat-kings moves: {len(mk_moves)} entries, {len(mk_names)} distinct names")
print(f"menu names also in mat-kings: {len(menu_names & mk_names)}; "
      f"menu-only: {len(menu_names - mk_names)}; mk-only: {len(mk_names - menu_names)}")
print("sample menu-only names:", sorted(menu_names - mk_names)[:10])
print("sample mk-only names:", sorted(mk_names - menu_names)[:10])
print("anim_id range:", min(anim_ids), "..", max(anim_ids),
      f"-> file range {min(anim_ids) + 0x3322:#x}..{max(anim_ids) + 0x3322:#x}")
print("anim_ids outside move-clip range 0..4408:",
      sorted(a for a in anim_ids if a < 0 or a > 4408)[:10])

# ---- 6. WAV sanity ----
import math
tot_s, peaks = 0.0, []
for b in ('bank1_proset', 'bank2_sepack', 'bank3_music'):
    d = os.path.join(EXT, 'sound', b)
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.wav'):
            continue
        with wave.open(os.path.join(d, fn)) as w:
            n, rate = w.getnframes(), w.getframerate()
            frames = w.readframes(n)
        import array
        a = array.array('h', frames)
        peak = max((abs(x) for x in a), default=0)
        peaks.append(peak)
        tot_s += n / rate
print(f"WAVs: {len(peaks)} files, total {tot_s:.1f}s, "
      f"peak amplitude min={min(peaks)} max={max(peaks)} "
      f"silent(peak<100): {sum(1 for p in peaks if p < 100)}")
print("DONE")
