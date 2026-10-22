#!/usr/bin/env python3
"""DINF_400.BIN decrypt + manifest-header verify (T6 lane A, 2026-10-21).

Reads the sweep lane's ISO READ-ONLY (never copies it), extracts the 120-byte
DINF_400.BIN at LBA 230192, decrypts with the banked fixed keyset B
(K1=0xEBCF9603, K2=0xB3BEF6A4 -- hardcoded at EBOOT 0x88985BC, call 0x8AA2E58,
per teardown-completion checkpoints 2026-10-14), and parses the manifest header.

Keystream note: the 0x8AA2CA8 stream cipher is data-independent (k evolves from
counters only), so decrypting the first 30 words from a 286-word buffer gives
the same first 30 words regardless of padding. The real ROM call processes
t3 = 256 + ((120+3)>>2) = 286 words for length=120; we zero-pad to 286 words.
"""
import struct, sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sector_cipher import cipher_block

ISO = '/home/hatch/workspace/_t6r4-work/iso/tekken6-psp.iso'  # READ-ONLY reference
SECTOR = 2048
DINF_LBA = 230192
DINF_LEN = 120
K1 = 0xEBCF9603
K2 = 0xB3BEF6A4

def main():
    with open(ISO, 'rb') as f:          # read-only
        f.seek(DINF_LBA * SECTOR)
        sector = f.read(SECTOR)
    raw = sector[:DINF_LEN]
    n_words = 286  # 256 + ((120+3)>>2), per the ROM's own word count
    words = list(struct.unpack('<%dI' % n_words, raw.ljust(n_words * 4, b'\x00')))
    done, ret = cipher_block(K1, K2, words, DINF_LEN)
    pt = struct.pack('<%dI' % (DINF_LEN // 4), *words[:DINF_LEN // 4])

    print('words_processed=%d ret=%s' % (done, ret))
    print('magic: %r' % pt[:8])
    for i in range(0, DINF_LEN, 16):
        chunk = pt[i:i + 16]
        asc = ''.join(chr(c) if 32 <= c < 127 else '.' for c in chunk)
        print('  %03x: %s  %s' % (i, chunk.hex(' '), asc))
    if pt[:4] == b'DINF':
        print('DINF MAGIC CONFIRMED')
        # parse known fields (values verified 2026-10-14; re-checking here)
        print('entry_count(u32@+4) =', struct.unpack('<I', pt[4:8])[0])
        print('data_bytes(u32@+8)  =', struct.unpack('<I', pt[8:12])[0])
        tail = pt[16:].split(b'\x00')
        print('strings:', [s for s in tail if s][:8])
    else:
        print('DINF MAGIC NOT FOUND -- decrypt recipe mismatch')

if __name__ == '__main__':
    main()
