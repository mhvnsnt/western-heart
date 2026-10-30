#!/usr/bin/env python3
"""Tekken 6 PSP — DATA401 bulk decryptor (CORRECTED, round 5, 2026-10-21).

Supersedes the round-3 `full_bulk_decrypt.py`. The round-3 driver called
`cipher_block` ONCE PER 2048-BYTE SECTOR with length=2048. That is the
bug that masqueraded as a "custom gzip" format for two rounds: the game
decrypts in 1024-BYTE units — one cipher call per 1024-byte block, with
t0 = the block's bulk-relative byte offset and length = 1024. A single
2048 call produces the right keystream for the first 1024 bytes of the
sector and a wrong keystream for the second 1024 bytes, so every file
in bulk_decrypted.bin had alternating good/corrupt 1024-byte blocks
(block map vs the game's own RAM copy of idx74: `=X=X=X=...`, F12 in
ROUND5-STATUS.md).

With per-1024 calls the whole chain is exact:
  sector cipher (bulk keys K1=0x24cfa8a4, K2=0x564928df)
  -> GZIP containers whose bodies are PLAIN zlib (0x78 0xda)
  -> 76/76 containers adler32-exact (see decode_all76.py).

Usage: bulk_decrypt.py <tekken6-psp.iso> <out_bulk_decrypted.bin>
Streams sector by sector; output = ISO sectors [BULK0, end) decrypted.
"""
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sector_cipher import cipher_block

BULK0 = 230256
K1, K2 = 0x24CFA8A4, 0x564928DF
BLOCK = 1024


def decrypt_bulk_bytes(raw, base_off, k1=K1, k2=K2):
    """Decrypt `raw` (bulk-relative byte offset `base_off`) with one
    cipher call per 1024-byte block — the game's own granularity."""
    out = bytearray()
    for boff in range(0, len(raw), BLOCK):
        chunk = raw[boff:boff + BLOCK]
        nw = len(chunk) // 4
        words = list(struct.unpack('<%dI' % nw, chunk[:nw * 4])) + [0] * 300
        cipher_block(k1, k2, words, len(chunk), base_off + boff, 0)
        out += struct.pack('<%dI' % len(words), *words)[:len(chunk)]
    return bytes(out)


def main():
    iso_path, out_path = sys.argv[1], sys.argv[2]
    iso_size = os.path.getsize(iso_path)
    s_end = iso_size // 2048
    print(f"ISO sectors: 0..{s_end - 1}, decrypting bulk {BULK0}..{s_end - 1}",
          flush=True)
    n = 0
    with open(iso_path, 'rb') as f, open(out_path, 'wb') as o:
        for s in range(BULK0, s_end):
            f.seek(s * 2048)
            data = f.read(2048)
            if not data:
                break
            o.write(decrypt_bulk_bytes(data, (s - BULK0) * 2048))
            n += 1
            if n % 20000 == 0:
                print(f"  ...{n} sectors", flush=True)
    print(f"done: {n} sectors -> {out_path}", flush=True)


if __name__ == '__main__':
    main()
