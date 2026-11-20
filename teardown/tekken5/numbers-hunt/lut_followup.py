#!/usr/bin/env python3
"""Follow up the LUT classifier's string hits: dump the decrypted ASCII
around each hit for the 11 string-hit entries + the pure-text entry 5
+ raw entry 240, so the strings can be attributed (or dismissed).
Usage: lut_followup.py <TK5DATA3_code.bin>
"""
import json, struct, sys, urllib.request
sys.path.insert(0, '/home/hatch/workspace/devil-within-decode/repo/teardown/tekken5/tools')
from romd_extract import decrypt_sector_data_fast

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"
ISO_OFF = 2074302464
TABLESTART = 0x0027B5B0
TABLECOUNT = 1571
SECTOR = 0x800
TARGETS = [5, 157, 159, 163, 167, 176, 240, 1419, 1422, 1438, 1464, 1534]

def fetch(iso_start, nbytes, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={iso_start}-{iso_start + nbytes - 1}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) != nbytes:
                raise RuntimeError(f"short read {len(data)} != {nbytes}")
            return data
        except Exception:
            if attempt == retries - 1:
                raise
            import time; time.sleep(5)

def main():
    with open(sys.argv[1], 'rb') as f:
        f.seek(TABLESTART)
        lut = f.read(TABLECOUNT * 8)
    entries = [struct.unpack_from('<II', lut, i * 8) for i in range(TABLECOUNT)]
    for idx in TARGETS:
        sector, size = entries[idx]
        nbytes = min(size, 4096)
        raw = fetch(ISO_OFF + sector * SECTOR, nbytes)
        dec = bytearray(raw)
        decrypt_sector_data_fast(dec, idx, len(dec))
        dec = bytes(dec)
        # pick buffer: the one with a known magic or more printable
        def score(b):
            return (b[:8] == b'TK5RESU1') * 100 + sum(1 for c in b if 32 <= c < 127)
        buf, mode = (dec, 'decrypted') if score(dec) >= score(raw) else (raw, 'raw')
        print(f"===== entry {idx} sector {sector} size {size} mode {mode} =====")
        print(f"  head hex: {buf[:32].hex()}")
        print(f"  head ascii: {''.join(chr(c) if 32 <= c < 127 else '.' for c in buf[:128])}")
        # all printable runs >= 8 with offsets
        import re
        for m in re.finditer(rb'[\x20-\x7e]{8,}', buf):
            print(f"  @{m.start():5d}: {m.group().decode()}")
        print()

if __name__ == '__main__':
    main()
