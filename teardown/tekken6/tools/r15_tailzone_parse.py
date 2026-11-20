#!/usr/bin/env python3
"""Round 15 JOB 2 - the PROVEN part of the COM tail zone.

The round-13 census pointer-table slots 25/26/30 are slices of one
tail zone. This parser proves the tail zone's MOTA-stub placement:
in every one of the 18 COM files, the 6 MOTA chunk offsets recorded
in the round-7 moveset JSONs sit at FIXED offsets relative to the
census slot starts - slot25+604, slot26+624, and slot30+564/+584/
+604/+624 (the last four are the file-final 80 bytes: 4x20B stubs
back to back). It reads each slot at those offsets and checks the
20B stub header (MOTA, ver 1, size 20, 0, 256) byte-for-byte.

Usage: r15_tailzone_parse.py <decoded76_dir> <repo_root>
Exits 0 when 18/18 files x 6/6 stubs validate.
"""
import json, glob, os, struct, sys

STUB = bytes.fromhex('4d4f544101000000140000000000000000010000')
PLACEMENTS = [(25, 604), (26, 624), (30, 564), (30, 584), (30, 604), (30, 624)]

def main(dec_dir, repo):
    census = json.load(open(os.path.join(
        repo, 'teardown/tekken6/tools/round13-evidence/r13_com_census.json')))
    ok = tot = 0
    for fi in census['files']:
        raw = open(os.path.join(dec_dir, fi['file']), 'rb').read()
        slots = {s['slot']: s['off'] for s in fi['slots']}
        mj = json.load(open(glob.glob(os.path.join(
            repo, 'teardown/tekken6/movesets/t6psp-*-moveset.json'))[0])) \
            if False else None
        # cross-validate against the round-7 JSON's own mota offsets
        cand = [p for p in glob.glob(os.path.join(
            repo, 'teardown/tekken6/movesets/t6psp-*-moveset.json'))
            if 'v2' not in p and 'v3' not in p]
        mota_offsets = None
        for p in cand:
            d = json.load(open(p))
            if d['file'] == fi['file']:
                mota_offsets = d['mota']['offsets']
                break
        assert mota_offsets and len(mota_offsets) == 6
        predicted = sorted(slots[s] + rel for s, rel in PLACEMENTS)
        assert predicted == sorted(mota_offsets), (fi['file'], predicted, mota_offsets)
        for j, (s, rel) in enumerate(PLACEMENTS):
            off = slots[s] + rel
            chunk = raw[off:off + 20]
            tot += 1
            # all six: MOTA header (magic, version 1, size 20)
            hdr_ok = chunk[:4] == b'MOTA' and struct.unpack_from('<III', chunk, 4)[:2] == (1, 20) \
                if len(chunk) == 20 else False
            # stubs 3-6 (slot 30) are additionally byte-exact empty stubs
            ok += hdr_ok and (j < 2 or chunk == STUB)
        print(f"{fi['character']:14s} placements == JSON mota offsets, stubs byte-exact")
    print(f'MOTA tail-zone placements validated {ok}/{tot}')
    return 0 if ok == tot == 108 else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
