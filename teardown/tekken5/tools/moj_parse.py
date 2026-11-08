#!/usr/bin/env python3
"""Structural inventory of Tekken 5 Devil Within stage map objects (moj_stg*.dat).

Each moj_stg file is a stage MAP OBJECT file (.moj), NOT stage text:
  head: dev build path  C:\temp\mapobj\stgNN.moj  (NUL-padded)
  then effect-archive references (stgNN_effnud.arc, stgNN_effmif.arc,
  stgNN.efp, stgNN_effnut.arc), then NUDP model containers, TIM2 textures,
  and MIF bone containers.

Measured structure (validated on all 4 files):
  NUDP: 'NUDP' magic; u32[1] = chunk byte length (distance to next NUDP);
        u32[2] = large value (unresolved); u32[3] = 0;
        u32[4..7] = float32 values (position / bounds — unresolved which).
  MIF:  'MIF' magic (+NUL); u32[3] = 0x05010000; u32[4] = small count
        (bone count?); u32[5] = 64; u32[6] = data size (multiple of 64);
        u32[7] = chunk size - 16 (distance to next MIF = u32[7] + 16).
  TIM2: 'TIM2' magic; standard PS2 texture header.

Canon stage names (HEARTMIND-RENAME-MAP.md §1, CONFIRMED):
  moj_stg00 -> THE THRESHOLD; moj_stg01 -> THE GALLERY OF MASKS;
  moj_stg02 -> THE DROWNING ROOM; moj_stg04 -> THE STILL POINT.
  (moj_stg03 does NOT exist — THE FURNACE has no DW stage donor.)
The NUDP float values and MIF bone contents (actual geometry, positions,
collision) are NOT yet parsed — that needs the NUDP model + MIF bone
formats reversed (ImHex patterns owed). This inventory records the
containers so that parse can be done per-container.

Usage: python3 moj_parse.py <romd_out_dir> <out.json>
"""
import json, struct, sys
from pathlib import Path

STAGES = {
    'moj_stg00.dat': 'THE THRESHOLD',
    'moj_stg01.dat': 'THE GALLERY OF MASKS',
    'moj_stg02.dat': 'THE DROWNING ROOM',
    'moj_stg04.dat': 'THE STILL POINT',
}

def find_all(data, magic):
    offs, i = [], 0
    while True:
        j = data.find(magic, i)
        if j < 0:
            break
        offs.append(j)
        i = j + 1
    return offs

def main():
    out_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    stages = []
    for name, canon in STAGES.items():
        p = out_dir / name
        if not p.exists():
            stages.append({'source_file': name, 'canon_stage': canon,
                           'status': 'MISSING'})
            continue
        d = p.read_bytes()
        # dev path at head (first NUL-terminated string)
        head_end = d.find(b'\x00')
        dev_path = d[:head_end].decode('ascii', 'replace')
        nudp_offs = find_all(d, b'NUDP')
        tim2_offs = find_all(d, b'TIM2')
        mif_offs = find_all(d, b'MIF')
        nudps = []
        for off in nudp_offs:
            u = struct.unpack_from('<8I', d, off)
            floats = [round(v, 3) for v in struct.unpack_from('<4f', d, off + 16)]
            nudps.append({'offset': off, 'chunk_bytes': u[1], 'field2': u[2],
                          'floats': floats})
        mifs = []
        for off in mif_offs:
            u = struct.unpack_from('<8I', d, off)
            mifs.append({'offset': off, 'field3': u[3], 'count': u[4],
                         'field5': u[5], 'data_bytes': u[6], 'chunk_minus16': u[7]})
        tim2s = []
        for off in tim2_offs:
            u = struct.unpack_from('<8I', d, off)
            tim2s.append({'offset': off, 'u32': list(u)})
        # validate NUDP tiling: chunk_bytes == distance to next NUDP
        tiling_ok = all(
            nudps[i]['chunk_bytes'] == nudps[i + 1]['offset'] - nudps[i]['offset']
            for i in range(len(nudps) - 1))
        stages.append({
            'source_file': name, 'canon_stage': canon, 'status': 'extracted',
            'size_bytes': len(d), 'dev_build_path': dev_path,
            'nudp_count': len(nudps), 'nudp_tiling_ok': tiling_ok,
            'tim2_count': len(tim2s), 'mif_count': len(mifs),
            'nudps': nudps, 'mifs': mifs, 'tim2s': tim2s,
        })
    inv = {
        'format': 'western-heart dw-stage-inventory v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'note': ('Stage MAP OBJECT files (.moj), not stage text. Geometry, '
                 'positions, and collision inside NUDP/MIF are NOT yet parsed.'),
        'stages': stages,
    }
    out_path.write_text(json.dumps(inv, indent=1))
    for s in stages:
        print(f"{s['source_file']} -> {s['canon_stage']}: "
              f"NUDP={s.get('nudp_count')} TIM2={s.get('tim2_count')} MIF={s.get('mif_count')} "
              f"tiling_ok={s.get('nudp_tiling_ok')}")

if __name__ == '__main__':
    main()
