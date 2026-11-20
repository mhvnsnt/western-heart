#!/usr/bin/env python3
"""Parse Tekken 5 Devil Within gym motion files (.dat) — structural decode.

Reads every extracted gym_*.dat in raw/romd_out/ and produces a per-clip
structural decode:

  header        32 bytes: bones [1], frames [2], field3 [3], field12 [12]
                field12 = frames * bones * 12 (logical values) for standard
                clips; sparse clips have a smaller field12.
  sub-header    32 bytes @32: u32 record_table_off (=72), bone_table_off,
                data_off, field3 (again). GYM1 magic @64.
  record table  16 bytes/bone @72: per bone
                  u16[0],u16[1]  channel pair (-1 = none)
                  u16[2]          type: low byte 3/7/11 (7 -> 6 bytes of
                                  data per frame-block entry; 3/11 -> 12 bytes
                                  = 3 float32); high byte 0/1 (flag)
                  u16[3]          index (records pair up: 0,0,1,1,2,2...)
                  u32 @+8, u32 @+12  cumulative data offset (identical pair)
  bone table    @bone_table_off: bone indices (u16) with 0xFFFF markers.
  data section  @data_off: per-frame blocks. The record-table cumulative
                offsets describe the layout WITHIN one frame block
                (bone i's entry at data_off + frame_block_start + off[i]).
                Frame blocks are variable-length (keyframe/delta encoding:
                a 13-frame file is NOT 13x the 1-frame size). The inner
                keyframe packing (how delta frames are delimited, and the
                6-byte type-7 encoding) is NOT yet reversed — see
                DW-DECODE-LOG.md §keyframe. Type-3/11 entries decode as
                3 float32 values; type-7 entries are carried as raw hex.

Output: dw-motion-bank.json (canon-named, see HEARTMIND-RENAME-MAP.md).
Canon laws applied (Jay 2026-11-07 ~22:19, revised 2026-11-07 ~22:32):
  - "Devil" appears ONLY in our own way/language, never the source game's
    way (never the source kit's sense). Source kit names are NOT used as
    canon names; the rename map's canon kit names are used instead.
  - "Jin" ONLY ever means the soul JIN (the Blade Soul). The source kit
    owner is never named as a canon fighter.
  - Names blocked on a Jay-call (HEARTMIND-JAY-CALLS.md) are flagged
    PROVISIONAL and given a clearly-marked provisional name; nothing is
    decided here.

Usage: python3 gym_parse.py <romd_out_dir> <dw-motion-index.json> <out.json>
"""
import json, struct, sys
from pathlib import Path

# Canon kit mapping (HEARTMIND-RENAME-MAP.md §1). Source group -> canon kit.
KIT = {
    'ikdv':      ('surge',        'Surge Kit',        'Soul Surge Form move donor (any fighter)'),
    'kmb1':      ('warden',       'Warden Kit',       'WARDEN OF THE THRESHOLD move donor'),
    'kob2':      ('drowned_ogre', 'Drowned Ogre Kit', 'THE DROWNED OGRE move donor'),
    'ozb3':      ('unmasked',     'Unmasked Kit',     'THE UNMASKED move donor'),
    'oz_extra':  ('unmasked',     'Unmasked Kit',     'THE UNMASKED move donor (extra slot)'),
    'ikt5':      ('unassigned',   'unassigned kit',   'UNMEASURED — kit owner unknown; do not wire'),
    'djin':      ('surge_bloom',  'Soul Surge Bloom', 'Soul Surge Form transformation/awakening data'),
}

# init_obj per-file canon targets (rename map §1, CONFIRMED rows).
INIT_OBJ = {
    'gym_init_obj_boss1.dat': ('warden_body', 'WARDEN OF THE THRESHOLD — body/init', 'THE THRESHOLD boss body'),
    'gym_init_obj_boss2.dat': ('masks_body', 'THE MASKS — body/init', 'THE GALLERY OF MASKS boss body'),
    'gym_init_obj_boss3.dat': ('drowned_ogre_body', 'THE DROWNED OGRE — body/init', 'THE DROWNING ROOM boss body'),
    'gym_init_obj_boss5.dat': ('unmasked_body', 'THE UNMASKED — body/init', 'THE STILL POINT boss body'),
    # REAL filenames (dw-motion-index.json). The rename map's mon01-06 is wrong; do NOT use it.
    'gym_init_obj_mon_power1.dat':   ('wave_echo', 'Wave echo — archetype (power 1)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_mon_power2.dat':   ('wave_echo', 'Wave echo — archetype (power 2)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_mon_speed1.dat':   ('wave_echo', 'Wave echo — archetype (speed 1)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_mon_standard1.dat':('wave_echo', 'Wave echo — archetype (standard 1)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_mon_standard2.dat':('wave_echo', 'Wave echo — archetype (standard 2)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_mon_tricky1.dat':  ('wave_echo', 'Wave echo — archetype (tricky 1)', 'Wave enemy donor (any stage)'),
    # REAL tk filenames (dw-motion-index.json). The rename map's tk05/tk09/tk10/
    # tk11/tk12/tk14/tk15/tk16/tk17/tk19/tk21 do NOT exist — those rows name
    # files that are not in the index or the archive. The real tk family is
    # the second wave-enemy family, parallel to mon_ (same load lists, same
    # archetype names). Wave echo archetypes, same as mon_.
    'gym_init_obj_tk_power1.dat':   ('wave_echo', 'Wave echo — archetype (power 1, second family)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_tk_power2.dat':   ('wave_echo', 'Wave echo — archetype (power 2, second family)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_tk_speed1.dat':   ('wave_echo', 'Wave echo — archetype (speed 1, second family)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_tk_standard1.dat':('wave_echo', 'Wave echo — archetype (standard 1, second family)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_tk_standard2.dat':('wave_echo', 'Wave echo — archetype (standard 2, second family)', 'Wave enemy donor (any stage)'),
    'gym_init_obj_tk_tricky1.dat':  ('wave_echo', 'Wave echo — archetype (tricky 1, second family)', 'Wave enemy donor (any stage)'),
    # The rename map does NOT list these two. Flagged, not decided.
    # gym_init_obj_jin.dat: source Jin Kazama init. Map §0: Jin Kazama has NO
    # HeartMind target (his data is Demonio, RIN's vessel). No fighter target; do NOT wire as a fighter.
    'gym_init_obj_jin.dat': ('source_init_no_target', 'Source init — no canon fighter target',
                            'Source character init; Jin Kazama has no HeartMind fighter (map §0). Do NOT wire as a fighter.'),
    # gym_init_obj_devil.dat: source transform init. INFERENCE (not a map row):
    # same role as the djin transform files (Soul Surge Bloom donor). The
    # source name is Tekken way and is never used as a canon name.
    'gym_init_obj_devil.dat': ('surge_bloom_provisional', 'Soul Surge Bloom — init (PROVISIONAL, inference)',
                              'Source transform init; INFERENCE: Soul Surge Bloom donor (same role as djin transform). PROVISIONAL — Jay\'s call.'),
}

# dw_singles per-file canon targets (rename map §1).
# REAL filenames (dw-motion-index.json). The rename map's dw_init / dw_mon /
# dw_mo_shot / dw_mon_sj do NOT exist — those rows name files that are not
# in the index or the archive. The real dw_singles are below.
DW_SINGLES = {
    # Opaque tokens — no gloss, no canon target. Do not wire.
    'gym_dw_nog00.dat':   ('unassigned', 'unassigned — opaque token', 'UNMEASURED — opaque token; do not wire'),
    'gym_dw_raribxk.dat': ('unassigned', 'unassigned — opaque token', 'UNMEASURED — opaque token; do not wire'),
    'gym_dw_rarixk.dat':  ('unassigned', 'unassigned — opaque token', 'UNMEASURED — opaque token; do not wire'),
    'gym_dwfkao00.dat':   ('face_stub', 'Face — STUB (no face data in DW index)', 'Face system STUB; do not wire as a face'),
    # Jay-call #6: "Soul Beam" is PROPOSED and unanswered. Provisional name only.
    'gym_dwhadoh00.dat':  ('surge_beam_provisional', 'Surge Beam (PROVISIONAL — Jay-call #6: "Soul Beam" proposed, unanswered)',
                           'Soul Surge Form beam attack (PROPOSED name "Soul Beam" awaits Jay)'),
    'gym_dwup00.dat':     ('surge_trigger', 'Soul Surge Form — trigger', 'Soul Surge Form activation trigger'),
    # Heihachi-variant power-up. No rename-map row. Source variant; do not wire.
    'gym_dwup_hei.dat':   ('unassigned', 'unassigned — source variant', 'UNMEASURED — source Heihachi-variant trigger; no rename-map target; do not wire'),
}

FPS = 60.0

def parse_gym(path):
    d = path.read_bytes()
    h = struct.unpack_from('<16H', d, 0)
    bones, frames, field3, field12 = h[1], h[2], h[3], h[12]
    sub = struct.unpack_from('<4I', d, 32)
    rec_off, bone_off, data_off = sub[0], sub[1], sub[2]
    magic_ok = d[64:68] == b'GYM1'
    # record table: 16 bytes/bone
    recs = []
    for i in range(bones):
        r = struct.unpack_from('<8H', d, rec_off + i * 16)
        off = r[4] | (r[5] << 16)
        off2 = r[6] | (r[7] << 16)
        recs.append({
            'bone': i,
            'chan_a': r[0] if r[0] != 0xFFFF else -1,
            'chan_b': r[1] if r[1] != 0xFFFF else -1,
            'type': r[2],
            'type_low': r[2] & 0xFF,
            'type_high': (r[2] >> 8) & 0xFF,
            'index': r[3],
            'offset': off,
            'offset2': off2,
        })
    offs = [r['offset'] for r in recs]
    monotonic = all(offs[i] < offs[i + 1] for i in range(len(offs) - 1))
    types = sorted({r['type_low'] for r in recs})
    # bone table (u16s) — indices with 0xFFFF markers
    bone_table = list(struct.unpack_from(f'<{(data_off - bone_off) // 2}H', d, bone_off)) \
        if data_off > bone_off else []
    # data section
    data = d[data_off:]
    # first-frame values: for each bone, entry at off[i], length = next off - off
    # (last bone: type 7 -> 6 bytes, type 3/11 -> 12 bytes)
    # Channel kind is carried by the type LOW byte (measured):
    #   low=3  -> 3 float32 = SCALE (sx,sy,sz), near 1.0 (newhane00: 0.96-1.07)
    #   low=11 -> 3 float32 = POSITION (x,y,z) in millimetres
    #            (root ~origin; height bone Y ~1011-1054; side bone X -400)
    #   low=7  -> 6 bytes = ROTATION, packed (3 x i16, small values;
    #            angle scale NOT yet confirmed — carried raw)
    first_frame = []
    for i, r in enumerate(recs):
        if i + 1 < len(recs):
            n = offs[i + 1] - offs[i]
        else:
            n = 12 if r['type_low'] in (3, 11) else 6
        chunk = data[offs[i]:offs[i] + n]
        if r['type_low'] == 3 and len(chunk) == 12:
            vals = [round(v, 6) for v in struct.unpack('<3f', chunk)]
            first_frame.append({'bone': i, 'type': 3, 'channel': 'scale', 'bytes': n,
                                'floats': vals, 'sane': all(0.05 < abs(v) < 20 for v in vals)})
        elif r['type_low'] == 11 and len(chunk) == 12:
            vals = [round(v, 3) for v in struct.unpack('<3f', chunk)]
            first_frame.append({'bone': i, 'type': 11, 'channel': 'position_mm', 'bytes': n,
                                'floats': vals, 'sane': all(abs(v) < 10000 for v in vals)})
        elif r['type_low'] == 7 and len(chunk) == 6:
            i16 = list(struct.unpack('<3h', chunk))
            first_frame.append({'bone': i, 'type': 7, 'channel': 'rotation_packed',
                                'bytes': n, 'raw_hex': chunk.hex(),
                                'i16': i16, 'decoded': False,
                                'note': '3 x i16; angle scale unconfirmed'})
        else:
            first_frame.append({'bone': i, 'type': r['type_low'], 'bytes': n,
                                'raw_hex': chunk.hex(), 'decoded': False,
                                'note': 'unexpected length'})
    subtype = 'standard' if field12 == frames * bones * 12 else 'sparse'
    return {
        'bones': bones, 'frames': frames, 'field3': field3, 'field12': field12,
        'subtype': subtype,
        'duration_s': round(frames / FPS, 3),
        'record_table_off': rec_off, 'bone_table_off': bone_off, 'data_off': data_off,
        'magic_gym1': magic_ok,
        'record_offsets_monotonic': monotonic,
        'record_types': types,
        'record_offsets': offs,
        'bone_table_u16': bone_table,
        'data_bytes': len(data),
        'first_frame': first_frame,
    }

def main():
    out_dir, index_path, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    idx = json.loads(index_path.read_text())
    clips = []
    missing = []
    for group in idx['groups']:
        gid = group['id']
        for f in group['files']:
            name = f['name']
            if not name.startswith('gym_'):
                continue  # moj_stg / snd handled elsewhere
            p = out_dir / name
            if gid in ('init_obj',):
                canon = INIT_OBJ.get(name)
                if canon is None:
                    canon = ('unassigned', 'TK kit — unassigned',
                             'UNMEASURED — target unknown; do not wire until decode')
                kit_id, kit_name, role = canon
            elif gid in ('dw_singles',):
                canon = DW_SINGLES.get(name)
                if canon is None:
                    canon = ('unassigned', 'unassigned', 'UNMEASURED')
                kit_id, kit_name, role = canon
            else:
                kit_id, kit_name, role = KIT.get(gid, ('unassigned', 'unassigned kit',
                                                       'UNMEASURED — kit owner unknown; do not wire'))
            entry = {
                'source_file': name,
                'group': gid,
                'gloss': f.get('gloss', ''),
                'gloss_confidence': f.get('confidence', ''),
                'canon_kit_id': kit_id,
                'canon_kit': kit_name,
                'canon_role': role,
                # Wireable only when the kit is assigned AND not provisional /
                # stub / no-target. Provisional and no-target entries are
                # decoded and recorded, never wired.
                'wireable': (kit_id != 'unassigned' and 'STUB' not in kit_name
                             and 'provisional' not in kit_id
                             and 'no_target' not in kit_id),
            }
            if not p.exists():
                entry['status'] = 'MISSING — no file data in TK5DATA2 (name only in load lists)'
                missing.append(name)
                clips.append(entry)
                continue
            try:
                entry.update(parse_gym(p))
                entry['status'] = 'extracted + structurally decoded'
            except Exception as e:
                entry['status'] = f'PARSE ERROR: {e}'
            clips.append(entry)
    # summary
    n = len(clips)
    got = sum(1 for c in clips if 'bones' in c)
    wireable = sum(1 for c in clips if c.get('wireable') and 'bones' in c)
    bank = {
        'format': 'western-heart dw-motion-bank v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'canon_law': ('"Devil" only in our own way/language, never the source game\'s way. '
                      '"Jin" only ever means the soul JIN (the Blade Soul). '
                      'Names blocked on a Jay-call are PROVISIONAL, never decided here.'),
        'decode_status': ('Structural decode complete (header, record table, bone table, '
                          'data section, first-frame float32 values for type-3/11 bones). '
                          'Inner keyframe packing (delta frames, type-7 6-byte encoding) '
                          'NOT yet reversed — see DW-DECODE-LOG.md §keyframe.'),
        'clips_total': n, 'clips_extracted': got, 'clips_missing': len(missing),
        'clips_wireable_kit_assigned': wireable,
        'missing_files': missing,
        'clips': clips,
    }
    out_path.write_text(json.dumps(bank, indent=1))
    print(f"clips={n} extracted={got} missing={len(missing)} wireable={wireable}")
    print(f"wrote {out_path}")

if __name__ == '__main__':
    main()
