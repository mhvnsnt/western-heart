#!/usr/bin/env python3
"""VPW2 full-ROM census + raw extraction.

ROM: Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64, 32 MB,
SHA1 82dd25a044689eab57ab362fe10c0da6388c217a (verified against
AKI-Club/vpw2 vpw2.sha1). Source: archive.org item
virtual-pro-wrestling-2-freem-edition-20210128 (clean ROM zip).

File table @ 0x1310F40 (13,091 u32be entries, last = end sentinel),
file data base 0x152DF0, 1-based file IDs, low bit = LZSS-encoded flag
(decomp extract_baserom.sh; VPWStudio FileTable.cs).

Labels/types: VPWStudio FileTableDB/VPW2.txt (MIT, AKI-Club/VPWStudio).

Outputs:
  file-table.csv — one row per file (fid, offset, length, encoded,
    decoded_len, db_type, db_label, magic8, verified, verify_note)
  extracted/raw/XXXX.bin — every file LZSS-decoded (where flagged)
  census.json — counts by type + verification summary
"""
import csv
import hashlib
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lzss import asmik_decode

ROM = os.environ.get(
    'VPW2_ROM',
    '/home/hatch/workspace/grok-declined-items/lane-jp-sourcing/'
    'vpw2-rom/Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64')
DB = ('/home/hatch/workspace/grok-declined-items/lane-jp-sourcing/pulls/'
      'VPWStudio/VPWStudio/VPWStudio/FileTableDB/VPW2.txt')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

FT = 0x1310F40
FIRST = 0x152DF0
NFILES = 13090


def s8(v):
    return v - 0x100 if v & 0x80 else v


def verify_model(dec):
    if len(dec) < 8:
        return False, 'short'
    nv = dec[1] & 0x7F
    nf = dec[2] & 0x7F
    expect = 8 + nv * 8 + nf * 3
    if expect == len(dec) or (expect == len(dec) - 1 and dec[-1] == 0):
        return True, f'verts={nv} faces={nf}'
    return False, f'len mismatch expect={expect} got={len(dec)}'


def verify_anim(dec):
    if len(dec) < 4:
        return False, 'short'
    if (len(dec) - 4) % 98 == 0:
        return True, f'frames={(len(dec) - 4) // 98}'
    return False, f'(len-4)%98={(len(dec) - 4) % 98}'


def verify_texture(dec, typ):
    if typ == 'AkiTexture':
        if dec[:4] == b'TEX\x00' and len(dec) >= 0x10:
            w, h = struct.unpack('>HH', dec[4:8])
            return True, f'{w}x{h} fmt={dec[8]}'
        return False, 'no TEX magic'
    if typ in ('Ci4Texture', 'Ci8Texture'):
        if len(dec) >= 8:
            w, h = dec[0] + 1, dec[1] + 1
            return True, f'{w}x{h}'
        return False, 'short'
    if typ == 'I4Texture':
        return True, f'raw {len(dec)}B'
    if typ in ('Ci4Palette', 'Ci8Palette'):
        return True, f'{len(dec)}B palette'
    return True, ''


def load_db(path):
    db = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        m = re.match(r'([0-9A-Fa-f]{2,})=([^;]+);(.*)$', s)
        if m:
            db[int(m.group(1), 16)] = (m.group(2), m.group(3).strip())
    return db


def main():
    data = open(ROM, 'rb').read()
    sha1 = hashlib.sha1(data).hexdigest()
    assert sha1 == '82dd25a044689eab57ab362fe10c0da6388c217a', sha1
    print(f'ROM OK: {len(data)} bytes, sha1 {sha1}')
    tab = struct.unpack('>13091I', data[FT:FT + 4 * 13091])
    db = load_db(DB)
    print(f'DB entries: {len(db)}')

    rawdir = os.path.join(OUT, 'extracted', 'raw')
    os.makedirs(rawdir, exist_ok=True)

    rows = []
    census = {}
    verified = {'yes': 0, 'no': 0}
    total_decoded = 0
    for fid in range(1, NFILES + 1):
        entry = tab[fid - 1]
        loc, enc = entry & ~1, bool(entry & 1)
        nloc = tab[fid] & ~1
        off = FIRST + loc
        raw = data[off:FIRST + nloc]
        dec = asmik_decode(raw) if enc else raw
        total_decoded += len(dec)
        typ, label = db.get(fid, ('?', ''))
        with open(os.path.join(rawdir, f'{fid:04X}.bin'), 'wb') as f:
            f.write(dec)
        # verification by type
        ok, note = True, ''
        if typ == 'AkiAnimation':
            ok, note = verify_anim(dec)
        elif typ == 'AkiModel':
            ok, note = verify_model(dec)
        elif typ in ('AkiTexture', 'Ci4Texture', 'Ci8Texture', 'I4Texture',
                     'Ci4Palette', 'Ci8Palette'):
            ok, note = verify_texture(dec, typ)
        elif typ == 'Binary':
            printable = sum(1 for b in dec[:256] if 32 <= b < 127)
            note = f'printable {printable}/256 in head'
        elif typ == 'AkiText':
            note = f'{len(dec)}B text blob'
        elif typ == 'AkiArchive':
            note = f'{len(dec)}B archive'
        elif typ == 'MenuBackground':
            note = f'{len(dec)}B menubg'
        else:
            note = f'{len(dec)}B'
        verified['yes' if ok else 'no'] += 1
        c = census.setdefault(typ, {'count': 0, 'raw_bytes': 0,
                                    'decoded_bytes': 0, 'verified': 0,
                                    'failed': 0})
        c['count'] += 1
        c['raw_bytes'] += len(raw)
        c['decoded_bytes'] += len(dec)
        c['verified' if ok else 'failed'] += 1
        rows.append({
            'fid': fid, 'fid_hex': f'{fid:04X}',
            'rom_offset': f'0x{off:08X}', 'length': len(raw),
            'encoded': 1 if enc else 0, 'decoded_len': len(dec),
            'db_type': typ, 'db_label': label,
            'magic8': dec[:8].hex(),
            'verified': 'yes' if ok else 'no', 'verify_note': note,
        })

    with open(os.path.join(OUT, 'file-table.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = {
        'rom': 'Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64',
        'rom_sha1': sha1,
        'rom_size': len(data),
        'rom_source': 'archive.org item virtual-pro-wrestling-2-freem-edition-20210128, '
                      'file "Virtual Pro Wrestling 2 - Oudou Keishou (Japan).zip"',
        'file_table': hex(FT), 'data_base': hex(FIRST),
        'nfiles': NFILES,
        'total_decoded_bytes': total_decoded,
        'verified': verified,
        'by_type': census,
    }
    json.dump(summary, open(os.path.join(OUT, 'census.json'), 'w'), indent=1)
    print(f'{NFILES} files, {total_decoded} decoded bytes, '
          f"verified {verified['yes']} failed {verified['no']}")
    for t, c in sorted(census.items(), key=lambda kv: -kv[1]['count']):
        print(f"  {c['count']:6d} {t:16s} decoded={c['decoded_bytes']:>10d} "
              f"verified={c['verified']} failed={c['failed']}")


if __name__ == '__main__':
    main()
