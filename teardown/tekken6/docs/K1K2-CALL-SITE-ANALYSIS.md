# Tekken 6 PSP — K1/K2 Key Recovery: Call-Site Analysis

**Date:** 2026-10-14
**Task:** Find how per-sector K1/K2 key words are derived for DATA401 decryption
**Status:** DERIVATION SOLVED — K1/K2 are per-sector, extracted from encrypted sector data via EBOOT tables. No single static key exists.

---

## 1. Function signature of 0x8AA3298 (key setup)

Disassembled from decrypted EBOOT. Builds 16-byte header `[C1, C2, K1, K2]`:

```
0x8AA3298(header=a0, K1=a1, K2=a2, C1=a3, C2=t0)
```

- `v0 = a1 | a2`; if nonzero → **caller-provided path**: stores a1→header+8, a2→header+12
- if zero → **PRNG path**: calls 0x8B7B600 3× with nonzero-mixing, stores results
- C1/C2: if a3(t0) nonzero → store caller values; else copy from table at ~0x8C2B9F8

---

## 2. All 5 call sites to 0x8AA3298

| # | Address | K1 (a1) | K2 (a2) | C1 (a3) | C2 (t0) | Path |
|---|---|---|---|---|---|---|
| 1 | 0x08898404 | 0xE11CF772 (hardcoded) | 0xA0DC9EB4 (hardcoded) | 0x9F7E8F59 | 0x6C4A824A | Caller keys |
| 2 | 0x088985BC | 0xEBCF9603 (hardcoded) | 0xB3BEF6A4 (hardcoded) | 0xA9A8AAF2 | 0xAFF764AD | Caller keys |
| 3 | 0x08A9DBAC | 0 (→ PRNG) | 0 (→ PRNG) | 0 (→ table) | 0 (→ table) | PRNG keys |
| 4 | 0x08AA12A0 | from 0x8AA2E88 (sector) | from 0x8AA2E88 (sector) | 0xBCBD1C51 | 0xE8BDE039 | **Sector-extracted** |
| 5 | 0x08AA1330 | $s1 (stale) | from stack (0x8AA2E88) | 0 (→ table) | 0 (→ table) | Mixed |

Sites 1–2 are in the 0x0889xxxx module (different archive, hardcoded keys — NOT DATA401).
Site 3 uses pure PRNG (likely for temp/scratch crypto).
**Sites 4–5 are the DATA401 sector path** (function at 0x08AA1204).

---

## 3. K1/K2 extraction: 0x8AA2E88 (the key function)

Single call site: 0x08AA1274. Fully reversed:

```
0x8AA2E88(a0, buf=a1, &K1=a2, &K2=a3):
  # 1. CRC32 verify (poly 0xEDB88320, init 0xFFFFFFFF, NO final xor)
  crc = CRC32(buf[0:0x7FC])
  if crc != *(u32*)(buf + 0x7FC): return 0   # reject

  # 2. Key extraction via table indirection (2 iterations)
  for i in 0..1:
    idx = buf32[ OFF_TABLE[i] ] ^ MASK_TABLE[i]
    if idx >= 0x800: return 0                # reject
    *(&K1 + i) = buf32[idx]                  # K[i] = sector word at idx
  return 1
```

### EBOOT tables (from decrypted ELF)
- **Offset table** @0x8BCE788: `[0xF1, 0x1AB]` (word indices into sector)
- **Mask table** @0x8BCE780: `[0x38BFE591, 0xD3610818]`
- Loop runs while ptr != 0x8BCE790 → exactly 2 iterations

### Derivation formula
```
K1 = sector32[ (sector32[0xF1] ^ 0x38BFE591) ]
K2 = sector32[ (sector32[0x1AB] ^ 0xD3610818) ]
```
Each index must be < 0x800 (word index into 0x800-byte unit), else sector rejected.

### Caller context (0x08AA1274 in function 0x08AA1204)
```
0x8AA2E88(s3, s1, sp, sp+4)   # s1 = 0x800-byte encrypted unit, s3 = header
if return == 0: fail
# then at 0x08AA12A0:
0x8AA3298(s3, K1=*(sp), K2=*(sp+4), C1=0xBCBD1C51, C2=0xE8BDE039)
```

---

## 4. What this means

**There is no single K1/K2 to recover.** Each encrypted 0x800-byte sector carries its own keys, hidden via indirection:
1. Read two pointer-words from fixed positions (0xF1, 0x1AB)
2. XOR each with its mask to get the real index
3. Read K1/K2 from those indices

The CRC32 gate ensures the sector was read correctly before key extraction.

**To decrypt a DATA401 sector:**
1. Read 0x800-byte encrypted unit
2. Verify `CRC32(unit[0:0x7FC]) == unit32[0x1FF]`
3. `K1 = unit32[(unit32[0xF1] ^ 0x38BFE591)]`, `K2 = unit32[(unit32[0x1AB] ^ 0xD3610818)]`
4. Build header `[0xBCBD1C51, 0xE8BDE039, K1, K2]`
5. Run `sector_cipher.cipher_block(K1, K2, buf, 0x800)`

Python implementation: `tools/k1k2_extract.py` (tested, CRC algorithm verified against EBOOT's standard CRC32 table found at ELF fileoff 0x3adff8).

---

## 5. Open problem: locating valid sectors

CRC verification failed on all ISO sectors tested (ranges: 230000–230010, 249990–250010, 300000–300010, 400000–400010, plus spot checks at 230240/230241/250000). The sectors are high-entropy (encrypted) but CRC doesn't validate.

**Likely causes:**
- PSP UMD sectors may be descrambled by the drive layer before reaching the game (raw ISO bytes ≠ what the game sees)
- DATA401 data may be at LBAs not yet identified (only UMD_DATA.BIN in ISO9660 root; DATA401 accessed via raw reads or PAC container)
- The 0x800-byte unit may not be sector-aligned in the ISO

**Next steps:**
- Trace the file I/O imports (0x8B88D20/0x8B88CA8) in function 0x08AA1204 to find what file/LBA it reads
- Check if PPSSPP or UMD tools descramble sectors
- The `openPac` path for DATA401.IDX (`disc0:/PSP_GAME/USRDIR/DATA401.IDX`) suggests a PAC container — sector layout may follow PAC structure, not ISO9660

---

## 6. Files

- This doc: `docs/K1K2-CALL-SITE-ANALYSIS.md`
- Implementation: `tools/k1k2_extract.py`
- Cipher model: `tools/sector_cipher.py`
- Cipher docs: `tools/SECTOR-CIPHER-REVERSED.md`
- Disassembler: `tools/mips_dis.py`
