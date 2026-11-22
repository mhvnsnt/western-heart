#!/usr/bin/env python3
"""VPW2 roster + moveset data extraction.

Parses (VPWStudio formats, AKI-Club, MIT):
- 130 WrestlerDefinitions @ ROM 0x3FBE4 (20 bytes each, VPW2 WrestlerCount)
- 17 StableDefinitions @ ROM 0x408BC (8 bytes each; ID2 lists via pointer)
- Wrestler names from AkiText file 0x006C (Shift_JIS, (full, short) pairs)
- Toki1 per-animation timing (file 0x034B, 36 bytes x 6,291 anims)
- Move damage (file 0x0277, 32 bytes x 2,302) + weapon damage (0x0276,
  32 x 100) + edit-mode damage (0x0062, 32 x 1,010) -- record layout from
  VPWStudio docs/movedamage.txt
- Reversals 0x027A-0x027F (576 B each; bit-packed, dumped raw + u16)
- Edit-mode move anims 0x0061 (u16 array, 1 header + 1007 pairs?)
- Wrestler params/moveset file pairs 0x0281+ (101 pairs, raw + manifest)
- BitPacking + MasterMoveMods code-segment tables (raw blobs)
- Blood 1bpp masks @ 0x40BB0/0x40CB0/0x40DB0/0x40EB0 (256 B each -> PNG,
  dimensions inferred 64x32)
- Re-decodes all 19 AkiText outputs to UTF-8 JSON (akitext emits Shift_JIS)

Known gap (same as No Mercy lane): params/moveset files are bit-packed per
VPWStudio's BitPacking tables; no parser exists. They are dumped raw with
a manifest linking each wrestler to its files.

Usage: python3 vpw2_roster.py   (run from vpw2/tools/)
Outputs: vpw2/extracted/roster/*.json, moveset/*.json + *.bin, text/*.json
"""
import hashlib
import json
import os
import re
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.path.dirname(HERE)
BASE = os.path.dirname(VPW2)
RAW = os.path.join(VPW2, 'extracted', 'raw')
ROM_PATH = os.path.join(BASE, 'vpw2-rom',
                        'Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64')
ROSTER_DIR = os.path.join(VPW2, 'extracted', 'roster')
MOVE_DIR = os.path.join(VPW2, 'extracted', 'moveset')
TEXT_DIR = os.path.join(VPW2, 'extracted', 'text')

WRESTLER_DEFS_OFF = 0x3FBE4
WRESTLER_COUNT = 130
STABLE_DEFS_OFF = 0x408BC
STABLE_COUNT = 17          # 136 bytes / 8
FIRST_ANIM_FILE = 0x1A90


def ptr_to_rom(ptr):
    return (ptr & 0x0FFFFFFF) + 0xC00


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def write_gray_png(path, w, h, px):
    """px: bytes of 0/255 grayscale, row-major."""
    def chunk(t, d):
        c = t + d
        return (struct.pack('>I', len(d)) + c +
                struct.pack('>I', zlib.crc32(c)))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)
    rows = b''.join(b'\x00' + bytes(px[y * w:(y + 1) * w])
                    for y in range(h))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                           chunk(b'IDAT', zlib.compress(rows, 6)) +
                           chunk(b'IEND', b''))


def load_akitext_strings(fid):
    """Parse akitext output file (Shift_JIS bytes, {"..."} per line)."""
    path = os.path.join(TEXT_DIR, f'{fid:04X}.txt')
    text = open(path, 'rb').read().decode('cp932', errors='replace')
    lines = text.split('\n')
    # split on \n only: splitlines() would also split on control chars
    # (0x0B/0x0C) that occur INSIDE strings
    if lines and lines[-1] == '':
        lines.pop()
    out = []
    for line in lines:
        if line.startswith('{"') and line.endswith('"}'):
            out.append(line[2:-2])
        else:
            out.append(line)
    return out


# ---------------- move damage record (VPWStudio docs/movedamage.txt) ----------------
def parse_damage_records(blob, label):
    assert len(blob) % 32 == 0, f'{label}: len {len(blob)} not mult of 32'
    recs = []
    for i in range(len(blob) // 32):
        r = blob[i * 32:(i + 1) * 32]
        recs.append({
            'index': i,
            'unknown_00_03': r[0:4].hex(),
            'link': struct.unpack('>H', r[4:6])[0],
            'damage': r[6],
            'spirit_gain': r[7],
            'spirit_drain': r[8],
            'blood_chance': r[9],
            'tko_chance': r[10],
            'attack_param': r[11],
            'defense_param': r[12],
            'connect_point': r[13:17].hex(),
            'unknown_11': r[17],
            'head_damage': r[18],
            'body_damage': r[19],
            'arm_damage': r[20],
            'leg_damage': r[21],
            'speed_damage': r[22],
            'strike_reaction': r[23],
            'unknown_18_1d': r[24:30].hex(),
            'misc': r[30:32].hex(),
        })
    return recs


def main():
    rom = open(ROM_PATH, 'rb').read()
    os.makedirs(ROSTER_DIR, exist_ok=True)
    os.makedirs(MOVE_DIR, exist_ok=True)

    # ---- names (AkiText 006C) ----
    names = load_akitext_strings(0x006C)
    print(f'006C: {len(names)} strings')

    # ---- roster ----
    roster = []
    for i in range(WRESTLER_COUNT):
        off = WRESTLER_DEFS_OFF + i * 20
        d = rom[off:off + 20]
        (id4, id2, theme, name_call, height, weight, voice1, voice2,
         moveset_idx, params_idx, appear_idx,
         profile_idx) = struct.unpack('>HHBBBBBBHHHH', d[:18])
        term = struct.unpack('>H', d[18:20])[0]
        full = short = ''
        # profile_index is a STRING index into 006C (always even);
        # full name at that index, short name at the next.
        if 0 <= profile_idx + 1 < len(names):
            full = names[profile_idx]
            short = names[profile_idx + 1]
        roster.append({
            'slot': i,
            'id4': f'{id4:04X}', 'id2': f'{id2:02X}',
            'name': full, 'name_short': short,
            'profile_index': profile_idx,
            'theme_song': theme, 'name_call': name_call,
            'height_cm': height + 150, 'weight_kg': weight + 70,
            'voice1': voice1, 'voice2': voice2,
            'moveset_file_index': moveset_idx,
            'params_file_index': params_idx,
            'appearance_index': appear_idx,
            'terminator': term,
        })
    named = sum(1 for w in roster if w['name'])
    print(f'roster: {len(roster)} defs, {named} named, '
          f'{len(roster) - named} unnamed (edit/controller-pak slots)')
    json.dump({'source': 'ROM 0x3FBE4, 130 x 20-byte WrestlerDefinition '
                         '(VPWStudio GameSpecific/VPW2/WrestlerDefinition.cs)',
               'names_source': 'AkiText file 0x006C; profile_index is a '
                               'string index (always even): full name at '
                               'that index, short name at the next',
               'height_note': 'height_cm = stored + 150; '
                              'weight_kg = stored + 70',
               'wrestlers': roster},
              open(os.path.join(ROSTER_DIR, 'roster.json'), 'w'),
              ensure_ascii=False, indent=1)

    # ---- stables ----
    stables = []
    for i in range(STABLE_COUNT):
        off = STABLE_DEFS_OFF + i * 8
        wptr, name_idx = struct.unpack('>II', rom[off:off + 8])
        # Member bytes are 1-BASED ROSTER SLOT numbers (verified: stable 0
        # bytes 0B 01 02 0A 05 06 1A = slots 11,1,2,10,5,6,26 = Baba, Ogawa,
        # Kawada... wait no -- slots are 0-based in roster.json, so byte N
        # = roster slot N-1. Verified against all 3 AJPW stables and the
        # contemporary FAQ roster columns.)
        members = []
        if wptr:
            p = ptr_to_rom(wptr)
            while rom[p] != 0 and len(members) < 8:
                members.append(rom[p] - 1)
                p += 1
        sname = ''
        if 0 <= name_idx < len(names):
            sname = names[name_idx]
        stables.append({'slot': i, 'name': sname,
                        'name_index': name_idx,
                        'wrestler_pointer': f'{wptr:08X}',
                        'members': [
                            {'slot': m,
                             'id4': roster[m]['id4'],
                             'name': roster[m]['name']}
                            for m in members]})
    print(f'stables: {len(stables)}')
    json.dump({'source': 'ROM 0x408BC, 17 x 8-byte StableDefinition '
                         '(VPWStudio GameSpecific/VPW2/StableDefinition.cs)',
               'name_note': 'name_index is a string index into AkiText 006C',
               'members_note': 'members are 0-based roster slots (ROM bytes '
                               'are 1-based slot numbers); verified against '
                               'all 3 AJPW stables and the contemporary FAQ '
                               'roster columns',
               'stables': stables},
              open(os.path.join(ROSTER_DIR, 'stables.json'), 'w'),
              ensure_ascii=False, indent=1)

    # ---- Toki1 ----
    toki = open(os.path.join(RAW, '034B.bin'), 'rb').read()
    assert len(toki) == 6291 * 36, f'Toki1 len {len(toki)}'
    entries = []
    for i in range(6291):
        t = toki[i * 36:(i + 1) * 36]
        entries.append({
            'anim_index': i,
            'file_id': f'{FIRST_ANIM_FILE + i:04X}',
            'camera_end_status': t[0],
            'single_repeating': t[1],
            'unknown_02': t[2],
            'damage_frame_start': t[3],
            'damage_frame_end': t[4],
            'mist_fire_type': t[5],
            'mist_fire_frame': t[6],
            'reversal_only_start_frame': t[7],
            'first_vulnerable_frame': t[8],
            'reversal_frame': t[9],
            'breakaway_frame': t[10],
            'motion_effect': [t[11], t[12]],
            'camera_effect': [t[13], t[14]],
            'replay_frame': t[15],
            'unknown_10': t[16],
            'ground_hold_interrupt_frame': t[17],
            'unknown_12': t[18], 'unknown_13': t[19],
            'effects': [[t[20 + k * 2], t[21 + k * 2]] for k in range(8)],
        })
    json.dump({'source': 'file 0x034B, 36 bytes per animation, entry i = '
                         'anim file 0x1A90+i (VPWStudio Toki1TestDialog.cs)',
               'field_notes': 'frame fields are animation frame numbers; '
                              'effects are [frame, value] pairs; 0xFF = none',
               'entries': entries},
              open(os.path.join(MOVE_DIR, 'toki1.json'), 'w'), indent=1)
    print(f'toki1: {len(entries)} entries')

    # ---- move damage ----
    for fid, fn in ((0x0277, 'move_damage.json'),
                    (0x0276, 'weapon_damage.json'),
                    (0x0062, 'edit_move_damage.json')):
        blob = open(os.path.join(RAW, f'{fid:04X}.bin'), 'rb').read()
        recs = parse_damage_records(blob, fn)
        json.dump({'source': f'file 0x{fid:04X}, 32-byte records '
                             '(VPWStudio docs/movedamage.txt)',
                   'count': len(recs), 'records': recs},
                  open(os.path.join(MOVE_DIR, fn), 'w'), indent=1)
        print(f'{fn}: {len(recs)} records')

    # ---- reversals (bit-packed; raw + u16 dump) ----
    rev = {}
    for fid in range(0x027A, 0x0280):
        blob = open(os.path.join(RAW, f'{fid:04X}.bin'), 'rb').read()
        u16 = list(struct.unpack('>288H', blob))
        rev[f'{fid:04X}'] = {
            'label': {0x027A: 'Heavyweight', 0x027B: 'Heavy Special',
                      0x027C: 'Junior', 0x027D: 'Junior Special',
                      0x027E: 'Martial Arts', 0x027F: 'Heel'}[fid],
            'sha256': sha256(blob),
            'u16_values': u16,
        }
    json.dump({'source': 'files 0x027A-0x027F, 576 bytes each',
               'note': 'Bit-packed reversal tables; no decoder exists in '
                       'VPWStudio. u16 dump is for analysis, not a parse.',
               'tables': rev},
              open(os.path.join(MOVE_DIR, 'reversals.json'), 'w'), indent=1)
    print('reversals: 6 tables dumped')

    # ---- edit-mode move anims ----
    blob = open(os.path.join(RAW, '0061.bin'), 'rb').read()
    u16 = list(struct.unpack(f'>{len(blob) // 2}H', blob))
    json.dump({'source': 'file 0x0061, u16 array',
               'note': 'First u16 = 133 (count of move groups?). Remaining '
                       '2014 values form 1007 pairs; pairing is a '
                       'hypothesis, not a verified parse.',
               'header': u16[0], 'values': u16[1:]},
              open(os.path.join(MOVE_DIR, 'edit_mode_moves.json'), 'w'),
              indent=1)
    print(f'edit_mode_moves: {len(u16)} u16 values')

    # ---- params/moveset pairs ----
    db_path = os.path.join(BASE, 'pulls', 'VPWStudio', 'VPWStudio',
                           'VPWStudio', 'FileTableDB', 'VPW2.txt')
    pairs = []
    for line in open(db_path):
        m = re.match(r'([0-9A-Fa-f]{2,})=Binary;Wrestler (Params|Moveset) '
                     r'([0-9A-F]{4})$', line.strip())
        if m:
            pairs.append({'file_id': f'{int(m.group(1), 16):04X}',
                          'kind': m.group(2).lower(),
                          'wrestler_id4': m.group(3)})
    for p in pairs:
        blob = open(os.path.join(RAW, p['file_id'] + '.bin'), 'rb').read()
        p['len'] = len(blob)
        p['sha256'] = sha256(blob)
    # link wrestlers to their files by id4
    by_id4 = {}
    for p in pairs:
        by_id4.setdefault(p['wrestler_id4'], {})[p['kind']] = p['file_id']
    linked = sum(1 for w in roster if w['id4'] in by_id4)
    json.dump({'source': 'files 0x0281+, labeled "Wrestler Params/Moveset '
                         '<ID4>" in VPWStudio FileTableDB/VPW2.txt',
               'note': 'Bit-packed per VPWStudio BitPacking tables; no '
                       'parser exists. Raw files live in extracted/raw/.',
               'pairs': pairs,
               'roster_linked': f'{linked}/{len(roster)} wrestlers have '
                                'params+moveset files'},
              open(os.path.join(MOVE_DIR, 'params_moveset_manifest.json'),
                   'w'), indent=1)
    print(f'params/moveset: {len(pairs)} files, {linked}/{len(roster)} '
          f'wrestlers linked')

    # ---- code-segment tables (raw blobs) ----
    code_tables = {
        'bitpacking_main': (0x3E530, 268),
        'bitpacking_movegroup_wrestling': (0x3D4E0, 1530),
        'bitpacking_movegroup_combo': (0x3DADC, 1550),
        'bitpacking_movegroup_shoot': (0x3E0EC, 1080),
        'master_movemods_first_entries': (0x3E63C, 266),
        'master_movemods': (0x3E748, 3908),
        'master_movemod_pointers': (0x3F68C, 532),
    }
    ct = {}
    for name, (off, size) in code_tables.items():
        blob = rom[off:off + size]
        open(os.path.join(MOVE_DIR, f'{name}.bin'), 'wb').write(blob)
        ct[name] = {'rom_offset': hex(off), 'len': size,
                    'sha256': sha256(blob)}
    json.dump({'source': 'ROM offsets from VPWStudio DefaultGameData.cs '
                         '(VPW2_NTSC_J)',
               'tables': ct},
              open(os.path.join(MOVE_DIR, 'code_tables.json'), 'w'), indent=1)
    print(f'code tables: {len(ct)} blobs')

    # ---- blood masks ----
    blood = {}
    for name, off in (('face', 0x40BB0), ('neck', 0x40CB0),
                      ('chest1', 0x40DB0), ('chest2', 0x40EB0)):
        blob = rom[off:off + 256]
        px = bytearray(2048)
        for i in range(2048):
            px[i] = 255 if (blob[i // 8] >> (7 - i % 8)) & 1 else 0
        write_gray_png(os.path.join(ROSTER_DIR, f'blood_{name}.png'),
                       64, 32, px)
        blood[name] = {'rom_offset': hex(off), 'len': 256,
                       'sha256': sha256(blob),
                       'png': f'blood_{name}.png',
                       'png_dims': 'inferred 64x32, 1bpp'}
    json.dump(blood, open(os.path.join(ROSTER_DIR, 'blood.json'), 'w'),
              indent=1)
    print('blood: 4 masks -> PNG (64x32 inferred)')

    # ---- re-decode all AkiText to UTF-8 JSON ----
    text_manifest = {}
    for fn in sorted(os.listdir(TEXT_DIR)):
        if not fn.endswith('.txt'):
            continue
        fid = int(fn[:-4], 16)
        strs = load_akitext_strings(fid)
        out = os.path.join(TEXT_DIR, f'{fid:04X}.json')
        json.dump({'file_id': f'{fid:04X}', 'count': len(strs),
                   'strings': strs},
                  open(out, 'w'), ensure_ascii=False, indent=1)
        text_manifest[f'{fid:04X}'] = len(strs)
    print(f'text: {len(text_manifest)} files re-decoded to UTF-8 JSON, '
          f'{sum(text_manifest.values())} strings total')


if __name__ == '__main__':
    main()
