#!/usr/bin/env python3
"""K1/K2 key recovery for Tekken 6 PSP DATA401 sectors.

Implements EBOOT 0x8AA2E88 (CRC32 verify + per-sector key extraction):
  1. CRC32 (poly 0xEDB88320, init 0xFFFFFFFF, NO final xor) over first 0x7FC
     bytes of the 0x800-byte crypto unit must equal word at offset 0x7FC.
  2. K1 = sector[ (sector[0xF1] ^ 0x38BFE591) ]   (word index < 0x800)
     K2 = sector[ (sector[0x1AB] ^ 0xD3610818) ]   (word index < 0x800)
  Tables from decrypted EBOOT: offset @0x8BCE788, mask @0x8BCE780.

Then builds the 16-byte header [C1=0xBCBD1C51, C2=0xE8BDE039, K1, K2]
(call site 0x08AA12A0 convention) and decrypts with sector_cipher.cipher_block.
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sector_cipher import cipher_block

# EBOOT tables (decrypted ELF)
OFF_TABLE = [0xF1, 0x1AB]              # @0x8BCE788
MASK_TABLE = [0x38BFE591, 0xD3610818]  # @0x8BCE780
C1_CONST, C2_CONST = 0xBCBD1C51, 0xE8BDE039  # call site 0x08AA12A0

def make_crc32_table(poly=0xEDB88320):
    tbl = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ poly if c & 1 else c >> 1
        tbl.append(c & 0xFFFFFFFF)
    return tbl
CRC_TBL = make_crc32_table()

def eboot_crc32(data):
    """Exact replication of 0x8AA2E88 loop: init 0xFFFFFFFF, no final xor."""
    crc = 0xFFFFFFFF
    for b in data:
        crc = CRC_TBL[(b ^ crc) & 0xFF] ^ (crc >> 8)
    return crc & 0xFFFFFFFF

def extract_k1k2(unit):
    """unit: 0x800 bytes (list of 512 words or bytes). Returns (ok, K1, K2, reason)."""
    if isinstance(unit, bytes):
        words = list(struct.unpack('<512I', unit[:0x800]))
    else:
        words = list(unit[:512])
    raw = struct.pack('<512I', *words)
    # 1. CRC check
    calc = eboot_crc32(raw[:0x7FC])
    stored = words[0x7FC // 4]
    if calc != stored:
        return False, 0, 0, f"CRC mismatch calc={calc:#010x} stored={stored:#010x}"
    # 2. Key extraction via table indirection
    keys = []
    for i in range(2):
        idx = (words[OFF_TABLE[i]] ^ MASK_TABLE[i]) & 0xFFFFFFFF
        if idx >= 0x800:
            return False, 0, 0, f"key[{i}] index {idx:#x} >= 0x800"
        keys.append(words[idx])
    return True, keys[0], keys[1], "ok"

def decrypt_sector_unit(unit_bytes):
    """Full pipeline: verify + extract keys + decrypt. Returns (ok, plaintext_words, info)."""
    ok, k1, k2, reason = extract_k1k2(unit_bytes)
    info = {'crc': reason, 'k1': k1, 'k2': k2}
    if not ok:
        return False, None, info
    words = list(struct.unpack('<512I', unit_bytes[:0x800]))
    # cipher processes 768 words per the bit-exact model; pad to 768
    buf = words + [0] * (768 - 512)
    n, ret = cipher_block(k1, k2, buf, 0x800)
    info.update({'words_done': n, 'ret': ret})
    return True, buf, info

if __name__ == '__main__':
    iso = '/home/hatch/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso'
    sec = int(sys.argv[1]) if len(sys.argv) > 1 else 250000
    with open(iso, 'rb') as f:
        f.seek(sec * 2048)
        data = f.read(2048)
    print(f"Sector {sec}: {len(data)} bytes, nonzero={sum(1 for b in data if b)}/2048")
    ok, pt, info = decrypt_sector_unit(data[:0x800])
    print("CRC/extract:", info['crc'])
    if ok:
        print(f"K1={info['k1']:#010x} K2={info['k2']:#010x} words={info['words_done']} ret={info['ret']}")
        raw = struct.pack('<512I', *pt[:512])
        print("First 64 bytes of plaintext:", raw[:64].hex())
        # magic scan
        for magic in (b'GMO\x00', b'TIM2', b'\x00GMO', b'pgs.', b'\x7fELF'):
            if magic in raw[:0x800]:
                print(f"  MAGIC FOUND: {magic!r} at offset {raw.find(magic):#x}")
        # entropy check
        from collections import Counter
        c = Counter(raw[:0x800])
        print(f"  byte histogram: {len(c)} unique values, top={c.most_common(3)}")
    else:
        print("FAILED:", info['crc'])
