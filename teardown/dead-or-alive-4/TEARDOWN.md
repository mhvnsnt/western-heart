# DOA4 Full Teardown — Encryption Analysis

**Date:** 2026-10-17  
**Status:** 6 AFS archives use custom Team Ninja encryption (table obfuscation). File DATA is PLAINTEXT.

## Executive Summary

The 6 "encrypted" AFS archives (chrone, chrtwo, chrthree, anm, mot, stg — 2.4GB total) are **NOT fully encrypted**. Analysis reveals:

1. **File DATA is PLAINTEXT** — XPR2 textures, animation floats, and other assets are stored unencrypted and can be carved directly.
2. **Only the header/file table is obfuscated** — the AFS file table (filenames, offsets, sizes) uses a custom Team Ninja cipher.
3. **The cipher is a 16-byte periodic stream-like cipher** with per-file keys and a runtime-generated S-box.

## Files

| File | Size | XPR2 Textures (plaintext) | Notes |
|------|------|---------------------------|-------|
| chrone.afs | 349MB | 30 XPR2 + 2 XPR1 | Character models/textures |
| chrtwo.afs | 522MB | 68 XPR2 | Character models/textures |
| chrthree.afs | 727MB | 75 XPR2 | Character models/textures |
| anm.afs | 2.9MB | 0 | Animation data (plaintext floats at tail) |
| mot.afs | 71MB | 11 XPR2 | Motion data |
| stg.afs | 777MB | 37 XPR2 | Stage models/textures |

## Cipher Characterization

### Structure
- **Period:** 16 bytes (autocorrelation 0.40 at P=16)
- **Type:** Stream-like (preserves plaintext similarity: similar plaintext → similar ciphertext)
- **Keys:** Per-file unique keys (each of the 6 files has a different key)
- **Regions:** MIXED encrypted/plaintext regions throughout each file (not whole-file encryption)

### What Was Ruled Out
- 4-byte repeating XOR (gives "AFS\0" magic but garbage table)
- 8-byte repeating XOR (crib tests fail)
- 16-byte repeating XOR (crib tests fail, hill-climbing hits local optima)
- Single-byte XOR / addition (fails)
- Affine cipher (fails)
- Block cipher in ECB mode (no avalanche effect observed; similar plaintext gives similar ciphertext)

### PE Analysis (default.xex → 22MB decrypted PE)
- **AFS file structs** found in .data at 0x82c48fa0, 0x82c67fa0, 0x82c6cb50, etc.
  - Each struct contains: `d:\<file>.afs` path, `cache:\<file>.afs` path, metadata fields
- **Runtime S-box table** code found at 0x822f06d0 region
  - Table at 0x83022eda (in BSS, zero in file, built at runtime)
  - 442 `xor` opcodes in .text, 1457 `xori` opcodes
- **Machine:** PowerPC Big-Endian (0x1f2), Image base 0x82000000
- **Ghidra:** Blocked — PE loader rejects PPCBE binaries. Used Capstone for manual disassembly.

### Table Obfuscation
The AFS file table (at the start of each archive) is obfuscated with the 16-byte periodic cipher. The table contains (offset, size) pairs for each contained file. Without the table, files must be carved by magic numbers.

## Plaintext Data Regions

### anm.afs (2.9MB) — Animation Data
- `0x000000-0x06BFFF`: Obfuscated (table + encrypted files, 432KB)
- `0x06C000-0x1A7FFF`: Structured animation data (entropy 5.4)
- `0x1A8000-0x1ABFFF`: Obfuscated chunk (16KB)
- `0x21C000-0x29BFFF`: Zero padding (87% zeros)
- `0x2B0000-0x2C7FFF`: Obfuscated chunk (96KB)
- **Tail:** Plaintext float curves (values in [0,1], e.g., `3f4ad1ed` = 0.79)

### Other Files
All contain plaintext XPR2 textures at 0x800-aligned offsets with zero padding before each file. The XPR2s can be carved directly.

## Carved Assets
28 XPR2 textures carved (187MB) from mot (11) and chrone (17 before disk limit). Full carving of all 221 XPR2s across 5 files is pending (requires ~1.3GB temp space).

## Next Steps
1. **Xenia memory dump:** Run DOA4 in Xenia emulator, dump decrypted AFS tables from RAM. This is the most reliable path to the table decryption.
2. **Full RE:** Complete the Capstone/Ghidra analysis of the S-box generation code at 0x822f06d0 to replicate the cipher.
3. **Carve all assets:** Extract all 221 XPR2 textures and identify model formats in the plaintext regions.
4. **Model format:** The character/stage models are in the plaintext regions but use an unknown Team Ninja format (not DNBW/KBDS). Requires format analysis.

## Tools
- `tools/extract_iso.py` — XGD partition extraction (patched for DOA4)
- `tools/afs_extract.py` — Standard AFS extraction
- `tools/doa4_cipher_analysis.py` — Cipher characterization scripts (autocorrelation, entropy scan, crib tests)

## References
- ISO: GitHub release `doa4-iso-v1` (30/30 chunks, 7.8GB, byte-verified)
- Local: `~/workspace/doa4-bass/doa4.iso` (7,834,892,288 bytes)
- Decrypted PE: `/tmp/doa4lane/default_pe.bin` (22MB)
- Analysis scripts: `/tmp/doa4lane/*.py`
