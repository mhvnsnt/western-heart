#!/usr/bin/env python3
"""TTT2 MOTA per-clip decoder (western-heart, 2026-11-03).

Decodes MOTA entries from the LZX-decoded data004.bin (X360, big-endian).
Layout cross-checked field-by-field against Kiloutre/TekkenMovesetExtractor
(ByteSwap.py AnimSwapper.Swap64Anim/SwapC8Anim, GUI_TekkenAnimationEditor.py
Animation.get0x64HeaderSize/getOffset/getFramesize, motasearch.py).

Type 0xC8 (200) — FULLY decoded + validated:
  +0  BE u16  type = 200
  +2  BE u16  track/bone count N
  +4  BE u32  frame count F
  +8  N x BE u32  per-track type values (same table as 0x64 header, widened)
  +8+4N  F frames x N tracks x 3 BE f32  (per-track triple per frame)
  Total size = 8 + 4N + 12*N*F  (exact match on entry 685: 35428 B)

Type 0x64 (100) — header + initial pose decoded; trailing stream NOT decoded
(Kiloutre's editor assigns frame_size=0 to 0x64; no public decoder exists):
  +0  BE u16  type = 100
  +2  BE u16  track count N
  +4  N x BE u16  per-track type values
  +4+2N  BE u16  frame count F
  +6+2N  BE u16  field A (unidentified; 1026/1028 on sampled entries)
  +8+2N  BE u16  count K of BE f32 values that follow (3 on sampled entries)
  +10+2N K x BE f32  root/global triple
  then per track: type in 4..7 -> 3 x BE i16 ; type >=8 -> 3 x BE f32
  then keyframe-index block: 4 * ((F+14)//16) bytes (+ optional 2, see spec)
  then a compressed per-track keyframe/delta stream (UNDECODED, reported as-is)

Kiloutre cross-validation: Kiloutre's own SwapAnimBytes() is run on the raw
BE bytes of a 0xC8 entry; the byte-swapped (LE) form is re-parsed and every
float must match this decoder's BE parse exactly.
"""
import struct, sys, json, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0] + '/kiloutre')
from ByteSwap import SwapAnimBytes  # Kiloutre's code, vendored in ./kiloutre

def be16(b, o): return struct.unpack('>H', b[o:o+2])[0]
def be32(b, o): return struct.unpack('>I', b[o:o+4])[0]
def bef(b, o):  return struct.unpack('>f', b[o:o+4])[0]
def bei16(b, o): return struct.unpack('>h', b[o:o+2])[0]

def decode_c8(entry: bytes):
    n = be16(entry, 2); f = be32(entry, 4)
    types = [be32(entry, 8 + 4*i) for i in range(n)]
    off = 8 + 4*n
    frames = []
    for fr in range(f):
        row = []
        for t in range(n):
            o = off + (fr*n + t)*12
            row.append([bef(entry, o), bef(entry, o+4), bef(entry, o+8)])
        frames.append(row)
    return {'type': 200, 'track_count': n, 'frame_count': f,
            'track_types': types, 'data_offset': off,
            'expected_size': off + 12*n*f, 'frames': frames}

def decode_64_header(entry: bytes):
    n = be16(entry, 2)
    types = [be16(entry, 4 + 2*i) for i in range(n)]
    f = be16(entry, 4 + 2*n)
    field_a = be16(entry, 6 + 2*n)
    k = be16(entry, 8 + 2*n)
    o = 10 + 2*n
    root = [bef(entry, o + 4*i) for i in range(k)]
    o += 4*k
    pose = []
    for t in range(n):
        if 4 <= types[t] < 8:
            pose.append({'encoding': 'i16x3', 'raw': [bei16(entry, o + 2*i) for i in range(3)]})
            o += 6
        else:
            pose.append({'encoding': 'f32x3', 'values': [bef(entry, o + 4*i) for i in range(3)]})
            o += 12
    groups = (f + 14)//16
    return {'type': 100, 'track_count': n, 'frame_count': f, 'field_a': field_a,
            'root_float_count': k, 'root_floats': root, 'track_types': types,
            'initial_pose': pose, 'keyframe_groups': groups,
            'header_end_editor_formula': o + 2 + 4*groups,
            'header_end_swapper_formula': o + 4*groups,
            'stream_bytes_after_editor_header': len(entry) - (o + 2 + 4*groups)}

def kiloutre_crosscheck_c8(entry: bytes, mine):
    swapped = SwapAnimBytes(list(entry))
    if swapped is None: return {'ok': False, 'why': 'Kiloutre swapper returned None'}
    sb = bytes(swapped)
    n = struct.unpack('<H', sb[2:4])[0]; f = struct.unpack('<I', sb[4:8])[0]
    if (n, f) != (mine['track_count'], mine['frame_count']):
        return {'ok': False, 'why': f'header mismatch LE n={n} f={f}'}
    off = 8 + 4*n; bad = 0
    for fr in range(f):
        for t in range(n):
            o = off + (fr*n + t)*12
            vals = struct.unpack('<fff', sb[o:o+12])
            if list(vals) != mine['frames'][fr][t]: bad += 1
    return {'ok': bad == 0, 'mismatched_triples': bad,
            'compared_triples': f*n}

if __name__ == '__main__':
    blob = open(sys.argv[1], 'rb').read()
    manifest = json.load(open(sys.argv[1] + '.mota-manifest.json'))
    table = manifest['tables'][0]
    uniq = sorted(set(e['offset_rel'] for e in table['entries']))
    def entry_bytes(e):
        i = uniq.index(e['offset_rel'])
        end = table['mota_offset'] + uniq[i+1] if i+1 < len(uniq) else None
        return blob[e['offset_abs']:end] if end else None
    out = {}
    e685 = [e for e in table['entries'] if e['index'] == 685][0]
    raw = entry_bytes(e685)
    dec = decode_c8(raw)
    dec['kiloutre_crosscheck'] = kiloutre_crosscheck_c8(raw, dec)
    dec['entry_size'] = len(raw); dec['mota_index'] = 685
    dec['sha256'] = hashlib.sha256(raw).hexdigest()
    json.dump(dec, open('clip0685_tracks.json', 'w'), indent=1)
    print('C8 entry 685:', dec['track_count'], 'tracks x', dec['frame_count'],
          'frames; size', len(raw), 'expected', dec['expected_size'],
          '; kiloutre crosscheck', dec['kiloutre_crosscheck'])
    hdrs = {}
    for idx in (1, 2, 3, 8):
        e = [x for x in table['entries'] if x['index'] == idx][0]
        raw = entry_bytes(e)
        h = decode_64_header(raw); h['entry_size'] = len(raw); h['mota_index'] = idx
        hdrs[idx] = h
        print(f"64 entry {idx}: {h['track_count']} tracks, {h['frame_count']} frames, "
              f"fieldA={h['field_a']} K={h['root_float_count']} root={h['root_floats']} "
              f"stream_after_header={h['stream_bytes_after_editor_header']} B")
    json.dump(hdrs, open('clip_type64_headers.json', 'w'), indent=1)
