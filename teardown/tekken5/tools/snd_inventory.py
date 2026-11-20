#!/usr/bin/env python3
"""Audio inventory for the Tekken 5 Devil Within sound files (snd_*.dat).

17 of 18 files start with magic P3Dp (u32 0x70443350). P3Dp header (16 bytes):
  magic P3Dp, then u16 fields: [0]=0x0A01 constant, [1]=sequential id
  (1-20, some missing), [2]=sample/clip count, [3]=count*104+16 (table size),
  [4]=data size/offset (unresolved), [5]=small count (1-6), [6]=0, [7]=mostly 4.
Entropy ~6.5 (compressed/encoded audio) except snd_c_tks.dat (0.39,
near-empty). The audio payload (VAG/ADPCM inside P3Dp) is NOT decoded.
snd_c02lei.dat is plain text (sound-position definitions + .evd script).

REAL filenames (dw-motion-index.json). The rename map's snd rows use WRONG
names for several files (snd_bg_blu.dat vs snd_bg_blu_se.dat, snd_boss_all /
snd_boss_last / snd_dmg_se / snd_gym_se / snd_last / snd_sys do not exist).
See DW-DECODE-LOG.md §map-corrections.

Canon sound roles (HEARTMIND-RENAME-MAP.md §1, PROVISIONAL unless noted):
  bg_lab/egy/blu_se -> stage themes (THE THRESHOLD / DROWNING ROOM / STILL POINT)
  c02lei -> voice donor (Rave); c10jin -> voice donor only, NO fighter target
  c15hei -> THE MASKS voice donor; c21jac -> WARDEN voice donor
  c30dvj -> Soul Surge Form voice donor (source name never used as canon)
  c_03_ogre / c_05_ogre -> ogre sounds; c_04_iseki -> ruins sounds
  c_boss / c_monst / chara_se / etc_se / system_se / title -> SFX pools

Usage: python3 snd_inventory.py <romd_out_dir> <dw-motion-index.json> <out.json>
"""
import json, math, struct, sys
from pathlib import Path
from collections import Counter

SND_ROLE = {
    'snd_bg_lab_se.dat': ('THE THRESHOLD — stage theme', 'Stage 1 music donor'),
    'snd_bg_egy_se.dat': ('THE DROWNING ROOM — stage theme', 'Stage 3 music donor'),
    'snd_bg_blu_se.dat': ('THE STILL POINT — stage theme', 'Stage 5 music donor'),
    'snd_c02lei.dat': ('Rave — voice donor', 'Voice donor (plain-text sound positions)'),
    'snd_c10jin.dat': ('voice donor only (no WH fighter target)', 'Voice donor only — Jin Kazama has no WH fighter; do not attach to a fighter'),
    'snd_c15hei.dat': ('THE MASKS — voice donor', 'Voice donor for THE MASKS'),
    'snd_c21jac.dat': ('WARDEN OF THE THRESHOLD — voice donor', 'Voice donor for WARDEN'),
    'snd_c30dvj.dat': ('Soul Surge Form — voice donor', 'Voice donor for Soul Surge Form (source name never used as canon)'),
    'snd_c_03_ogre.dat': ('Ogre sounds (03)', 'Ogre sound donor'),
    'snd_c_04_iseki.dat': ('Ruins sounds (04)', 'Ruins sound donor'),
    'snd_c_05_ogre.dat': ('Ogre sounds (05)', 'Ogre sound donor'),
    'snd_c_boss.dat': ('Boss theme / boss sounds', 'Boss battle sound donor'),
    'snd_c_monst.dat': ('Monster sounds', 'Monster sound donor'),
    'snd_c_tks.dat': ('Opaque token (near-empty)', 'Near-empty; no usable audio'),
    'snd_chara_se.dat': ('Character SFX pool', 'Character sound effects donor'),
    'snd_etc_se.dat': ('Misc SFX pool', 'Miscellaneous sound effects donor'),
    'snd_system_se.dat': ('System SFX pool', 'System sound effects donor'),
    'snd_title.dat': ('Title sounds', 'Title screen sounds donor'),
}

def entropy(data):
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return round(-sum((v / n) * math.log2(v / n) for v in c.values()), 2)

def main():
    out_dir, index_path, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    idx = json.loads(index_path.read_text())
    files = []
    for g in idx['groups']:
        if g['id'] != 'snd':
            continue
        for f in g['files']:
            name = f['name']
            p = out_dir / name
            role = SND_ROLE.get(name, ('unassigned', 'UNMEASURED'))
            entry = {'source_file': name, 'gloss': f.get('gloss', ''),
                     'canon_role': role[0], 'role_note': role[1]}
            if not p.exists():
                entry['status'] = 'MISSING'
                files.append(entry)
                continue
            d = p.read_bytes()
            entry['size_bytes'] = len(d)
            entry['entropy'] = entropy(d)
            if d[:4] == b'P3Dp':
                hdr = struct.unpack_from('<8H', d, 4)
                entry['container'] = 'P3Dp'
                entry['p3dp_header_u16'] = list(hdr)
                entry['p3dp_id'] = hdr[1]
                entry['p3dp_clip_count'] = hdr[2]
                entry['p3dp_table_bytes'] = hdr[3]
                entry['p3dp_field4'] = hdr[4]
                entry['p3dp_field5'] = hdr[5]
                entry['audio_decoded'] = False
                entry['status'] = 'extracted — P3Dp container, audio payload NOT decoded'
            else:
                entry['container'] = 'plain text'
                entry['audio_decoded'] = False
                entry['status'] = 'extracted — plain-text sound positions + event script'
            files.append(entry)
    inv = {
        'format': 'western-heart dw-audio-inventory v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'note': ('P3Dp audio payload (VAG/ADPCM) is NOT decoded. Headers + '
                 'entropy measured; the decode needs the P3Dp payload format reversed.'),
        'files': files,
    }
    out_path.write_text(json.dumps(inv, indent=1))
    print(f"snd files={len(files)} -> {out_path}")

if __name__ == '__main__':
    main()
