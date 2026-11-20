#!/usr/bin/env python3
"""Tekken 6 PSP — decode ALL 76 DATA401 GZIP containers (round 5, 2026-10-21).

Self-contained batch: reads the ISO directly, decrypts each manifest
GZIP file's region with the corrected per-1024-byte sector cipher
(bulk_decrypt.decrypt_bulk_bytes), parses the 20-byte "GZIP" header,
decompresses the body with PLAIN zlib, and verifies length + adler32
against the header/trailer — the byte-exactness oracle.

Round-5 result: **76/76 adler-exact** (was 20/76 under the round-3
per-2048 decryption; the 56 "failures" were corrupted odd 1024-byte
blocks in our own decrypted bulk, not a game format — see F12/F13 in
ROUND5-STATUS.md).

Usage: decode_all76.py <tekken6-psp.iso> <manifest.json> <out_dir>
Writes <out_dir>/idxNN_entryEEE.bin per container + inventory.json
(sizes, sha256, magic classification, embedded GMO/COM signature
counts). Decoded game data stays OUT of the repo; the inventory
(hashes + classification only) is the committable artifact.
"""
import hashlib
import json
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bulk_decrypt import decrypt_bulk_bytes, BULK0


def classify(out):
    """Cheap content classification: leading bytes + embedded magics."""
    gmo = out.count(b'GMO\x00') + out.count(b'GMO ')
    com = out.count(b'COM\x00')
    return {'head16': out[:16].hex(), 'gmo_sigs': gmo, 'com_sigs': com}


def main():
    iso_path, manifest_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    manifest = json.load(open(manifest_path))
    gz = [f for f in manifest['files'] if f['magic'].startswith('GZIP')]
    iso = open(iso_path, 'rb')
    inventory = []
    npass = 0
    for idx, f in enumerate(gz):
        iso.seek((BULK0 + f['start_rel']) * 2048)
        raw = iso.read(f['size'])
        d = decrypt_bulk_bytes(raw, f['start_rel'] * 2048)
        if f['magic'] == 'GZIP+prefix16':
            d = d[16:]
        w = struct.unpack('<5I', d[:20])
        assert d[:4] == b'GZIP', f'idx{idx}: bad magic after decrypt'
        body = d[20:20 + w[4]]
        out = zlib.decompress(body)
        trailer = struct.unpack('>I', body[-4:])[0]
        ok = len(out) == w[3] and zlib.adler32(out) == trailer
        npass += ok
        name = f"idx{idx:02d}_entry{f['entry']}.bin"
        with open(os.path.join(out_dir, name), 'wb') as fh:
            fh.write(out)
        rec = {'idx': idx, 'entry': f['entry'], 'sub': f['sub'],
               'file': name, 'expect': w[3], 'out_len': len(out),
               'adler_ok': bool(ok), 'sha256': hashlib.sha256(out).hexdigest()}
        rec.update(classify(out))
        inventory.append(rec)
        print(f"idx{idx} entry{f['entry']} sub{f['sub']}: "
              f"{'PASS' if ok else 'FAIL'} out={len(out)}")
    with open(os.path.join(out_dir, 'inventory.json'), 'w') as fh:
        json.dump({'total': len(gz), 'adler_exact': npass,
                   'files': inventory}, fh, indent=1)
    print(f"TOTAL: {npass}/{len(gz)} adler-exact")
    return 0 if npass == len(gz) else 1


if __name__ == '__main__':
    sys.exit(main())
