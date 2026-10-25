#!/usr/bin/env python3
"""Build the T6 at3 voice-bank inventory from a bulk-decrypted DATA401 + solved IDX table.
Usage: t6_bank_inventory.py <bulk_decrypted.bin> <idx_decrypted.bin> <out.json>
Recorded streams: exact cue ranges from at3 records (pos = stream index).
Gap regions: exact byte ranges between/after recorded streams; their internal stream
split is decode work (AT3 frame sync + validated RIFF scan), NOT claimed here.
No audio bytes are written to the output — offsets/sizes/tags only.
Requires: the solved IDX plaintext table (see t6_idx_solve.py)."""
import struct, sys, json
def main():
    bulk_path, idx_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(idx_path, 'rb').read()
    e = struct.unpack('<%dI' % (len(raw)//4), raw)
    rows = [(e[i], e[i+1], e[i+2]) for i in range(0, len(e)-2, 3)]
    banks = []
    with open(bulk_path, 'rb') as f:
        for idx, (off, sz, tag) in enumerate(rows):
            if sz in (0, 0xFFFFFFFF): continue
            f.seek(off*2048); head = f.read(min(sz, 8192))
            if head[:4] != b'\x01\x02\x01\x00': continue
            hdr = struct.unpack('<8I', head[:32])
            gid, nstreams, dstart, dsize = hdr[2], hdr[3], hdr[4], hdr[5]
            f.seek(off*2048); d = f.read(sz)
            recs = {}; s = 0
            while True:
                i = d.find(b'at3', s, dstart)
                if i < 0: break
                rw = struct.unpack('<16I', d[i:i+64])
                if rw[0] == 3372129 and rw[1] == gid: recs[rw[2]] = dict(pos=rw[2], size=rw[5], data_off=rw[6])
                s = i + 1
            if not recs: continue
            streams = []; gaps = []; cursor = 0
            for pos in sorted(recs):
                r = recs[pos]
                if r['data_off'] > cursor:
                    gaps.append(dict(file_off=off*2048+dstart+cursor, size=r['data_off']-cursor))
                streams.append(dict(pos=pos, file_off=off*2048+dstart+r['data_off'], size=r['size']))
                cursor = r['data_off'] + r['size']
            if cursor < dsize:
                gaps.append(dict(file_off=off*2048+dstart+cursor, size=dsize-cursor))
            banks.append(dict(entry=idx, size=sz, tag='0x%08x' % tag, group=gid,
                              nstreams_header=nstreams, recorded_streams=streams, gap_regions=gaps,
                              gap_stream_total=nstreams-len(streams)))
    json.dump(dict(banks=banks, notes='recorded streams: exact cue ranges from at3 records. gap regions: exact byte ranges; internal stream split TBD by decode.'),
              open(out_path, 'w'), indent=1)
    print(f'banks={len(banks)} recorded={sum(len(b["recorded_streams"]) for b in banks)} gaps={sum(len(b["gap_regions"]) for b in banks)}')
if __name__ == '__main__': main()
