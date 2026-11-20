#!/usr/bin/env python3
"""JOB 1 probe 8: (1) T1[148] proper validation (bytes at ~804 MB, local);
(2) full record-vs-record diff (records 0/9/18/27); (3) relaxed record
census ([4:16] match) over 2 MB; (4) common decompressors on record 0
payload (zlib raw/gzip, lzma, bz2).
"""
import struct, sys, zlib, lzma, bz2
sys.path.insert(0, "tools-Tekken5_Tools")
import tk5psp_crypt

def word_sum(data):
    n = len(data) // 4
    words = memoryview(data)[:n * 4].cast("I")
    acc = sum(words) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

CODE = open("/tmp/dec_code.bin", "rb").read()
T1 = [struct.unpack_from("<II", CODE, 0x27B5B0 + 8 * i) for i in range(1571)]
CK1 = [struct.unpack_from("<I", CODE, 0x27E838 + 4 * i)[0] for i in range(1571)]
print("== T1[148] validation ==")
s, z = T1[148]
print(f"  T1[148] sector={s} size={z} ck={CK1[148]:#010x}")
with open("../raw/TK5DATA1.BIN", "rb") as f:
    f.seek(s * 2048)
    data = f.read(z)
print(f"  read {len(data)} bytes, head={data[:16]!r}")
raw = word_sum(data)
print(f"  word_sum(raw)={raw:#010x} match={raw == CK1[148]}")
buf = bytearray(data)
tk5psp_crypt.decrypt_sector_data_fast(buf, 148, len(buf))
ds = word_sum(bytes(buf))
print(f"  dec(seed=148) head={bytes(buf[:16])!r} word_sum={ds:#010x} match={ds == CK1[148]}")

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(2 * 1024 * 1024)
REC = 18432
print("\n== record diffs (bytes differing, of 18432) ==")
recs = {r: d[r * REC:(r + 1) * REC] for r in [0, 1, 2, 3]}
for a in range(4):
    for b in range(a + 1, 4):
        diff = sum(1 for x, y in zip(recs[a], recs[b]) if x != y)
        # longest common prefix after byte 32
        lcp = 0
        for x, y in zip(recs[a][32:], recs[b][32:]):
            if x != y:
                break
            lcp += 1
        print(f"  rec{a} vs rec{b}: diff={diff} lcp_after_32={lcp} "
              f"hdr_a={[hex(v) for v in struct.unpack('<8I', recs[a][:32])][:2]} "
              f"hdr_b={[hex(v) for v in struct.unpack('<8I', recs[b][:32])][:2]}")

print("\n== relaxed census ([4:16] == 08 00 00 00 2b 44 00 00 da 00 00 00) ==")
PAT = bytes.fromhex("080000002b440000da000000")
hits = [sec for sec in range(1024) if d[sec * 2048 + 4:sec * 2048 + 16] == PAT]
print(f"  count={len(hits)} first 30: {hits[:30]}")
print(f"  diffs: {[hits[i+1]-hits[i] for i in range(25)]}")
print(f"  type field [0:4] values at hits: {[struct.unpack('<I', d[h*2048:h*2048+4])[0] for h in hits[:12]]}")

print("\n== common decompressors on record 0 payload ==")
pay = d[32:REC]
for name, fn in [("zlib-raw", lambda b: zlib.decompress(b, -15)),
                 ("zlib", zlib.decompress),
                 ("gzip", lambda b: zlib.decompress(b, 31)),
                 ("lzma", lzma.decompress),
                 ("bz2", bz2.decompress)]:
    try:
        out = fn(pay)
        print(f"  {name}: OK out_len={len(out)} head={out[:32]!r}")
    except Exception as e:
        print(f"  {name}: FAIL {str(e)[:60]}")
