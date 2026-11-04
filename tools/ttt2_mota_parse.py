#!/usr/bin/env python3
"""TTT2 MOTA table parser (western-heart, 2026-11-03).
Parses the MOTA tables inside the LZX-decoded data004.bin (NRFI imge payload).
PROVEN layout (verified on the real bytes + Kiloutre/TekkenMovesetExtractor cross-check):
  NRFI envelope: ftyp(20) head(28) idgt(200) imge(payload) - BE u32 box sizes.
  MOTA table at payload offset P:
    +0  'MOTA'
    +4  u8 endianness (01 = big-endian, X360), +5..7 zero-ish (version 0x00010000 BE read)
    +8  BE u32 = 20 (header field)
    +12 BE u32 = entry count N
    +16 N x BE u32 offsets, RELATIVE TO MOTA START (P). Entry 0 offset 0 = null slot.
  Clip entries begin with BE u16 100 (0x0064) or 200 (0x00C8) - the same start
  marker as the game's wired T7 clips. Table 0: 1862/1875 marker hits (rest:
  entry0 null + shared-offset refs). All 6 nonzero tables in data004 pass.
Input: decoded data004 file (reassemble lzx-probe/decdata004/chunk*.bin in name
order from release ttt2-work-archive-2026-10-30 asset lzx__decdata004.tar.gz;
result must be 6,522,032 B, sha256 18b18d0ff2356219e9fac852eaa48f6b0a839479ea41f6d4b94069b5f86b2b21).
Output: JSON manifest of tables + per-entry offsets/sizes/sha256 + entry hex head.
"""
import struct, sys, json, hashlib

def main(path):
    blob = open(path, 'rb').read()
    assert blob[4:8] == b'ftyp', 'not NRFI'
    tables = []
    s = 0
    while True:
        i = blob.find(b'MOTA', s)
        if i < 0: break
        s = i + 1
        if i + 16 > len(blob): break
        _ver, _f8, cnt = struct.unpack('>III', blob[i+4:i+16])
        if cnt == 0 or cnt > 10000: continue
        offs = struct.unpack('>%dI' % cnt, blob[i+16:i+16+4*cnt])
        entries = []
        for k, o in enumerate(offs):
            p = i + o
            if p + 2 > len(blob):
                entries.append({'index': k, 'offset_rel': o, 'bad': True}); continue
            marker = struct.unpack('>H', blob[p:p+2])[0]
            nxt = offs[k+1] if k + 1 < cnt and offs[k+1] > o else None
            e = {'index': k, 'offset_rel': o, 'offset_abs': p, 'marker': marker}
            if nxt is not None:
                e['size'] = nxt - o
                e['sha256'] = hashlib.sha256(blob[p:i+nxt]).hexdigest()
            entries.append(e)
        hits = sum(1 for e in entries if e.get('marker') in (100, 200))
        tables.append({'mota_offset': i, 'count': cnt, 'marker_hits': hits, 'entries': entries})
        print(f"MOTA @ {i}: count={cnt} marker_hits={hits}")
    json.dump({'file': path, 'size': len(blob),
               'sha256': hashlib.sha256(blob).hexdigest(), 'tables': tables},
              open(path + '.mota-manifest.json', 'w'), indent=1)
    print('manifest written:', path + '.mota-manifest.json')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'data004-decoded.bin')
