# DOA4 Custom AFS Encryption Analysis

**Date:** 2026-10-17  
**Analyst:** Subagent (Ghidra RE lane)  
**Status:** PARTIAL — Encryption scheme characterized, full keystream not recovered

## Summary

The 6 encrypted AFS archives (chrone.afs, chrtwo.afs, chrthree.afs, anm.afs, mot.afs, stg.afs — 2.4GB total) use a Team Ninja custom encryption layer on top of standard CRI AFS format. The encryption is a per-file keyed stream cipher (XOR-based). The 4-byte file-specific keys are recovered, but the full keystream generation algorithm remains unknown.

## Recovered File Keys (4-byte, Big-Endian XOR)

Each file's first 4 bytes decrypt to `AFS\0` (0x41465300) with these keys:

| File | Size | Key (BE) | Key Bytes |
|------|------|----------|-----------|
| anm.afs | 2.9MB | 0x80b97b52 | 80 b9 7b 52 |
| chrone.afs | 349MB | 0x7fc2f931 | 7f c2 f9 31 |
| chrtwo.afs | 522MB | 0x7ff843dc | 7f f8 43 dc |
| chrthree.afs | 727MB | 0xfe793a0f | fe 79 3a 0f |
| mot.afs | 71MB | 0x7d40a53e | 7d 40 a5 3e |
| stg.afs | 777MB | 0x7d4e3d2e | 7d 4e 3d 2e |

**Key observations:**
- Keys are unique per file (not shared)
- Keys are NOT stored in the PE binary (searched, not found)
- Keys are NOT simple hashes of filenames (tested MD5, SHA1, CRC32, djb2, sdbm, FNV-1a — no match)
- mot.afs and stg.afs keys are similar (both start with 0x7d), suggesting related derivation
- chrone.afs and chrtwo.afs keys both start with 0x7f

## Ciphertext Structure Analysis

### Repeating 8-byte Patterns

The encrypted files exhibit strong 8-byte repeating ciphertext patterns:

**chrthree.afs** (first 32 bytes):
```
[ 0]: bf3f690f 3eed06e3 | 3eae2660 3eed06e3
[16]: 3eae2660 3eed06e3 | 3eae2660 3f25c788
```
The 8-byte sequence `3eed06e33eae2660` repeats at offsets 0x4, 0xC, 0x14.

**chrtwo.afs**: 8-byte `3f31676a3eb35950` repeats 3x at 0x28, 0x30, 0x38.

**chrone.afs**: 8-byte `3f0b94d43e8542c1` repeats 3x at 0x2c, 0x34, 0x3c.

**anm.afs**: 8-byte `9bff641f6a636a63` repeats at 0x8, 0x18. Also `8bff7c1fafafafaf` repeats 8x at 0xC8-spaced intervals.

### Interpretation

The repeating ciphertext with 8-byte period suggests either:
1. **XOR with 8-byte repeating key** AND repeating plaintext, OR
2. **ECB block cipher** with 8-byte blocks, OR  
3. **Stream cipher** with short-period keystream

If (1) with 4-byte key extended: decrypting chrthree.afs[4:12] with key `fe793a0f` gives plaintext `c0943cecc0d71c6f` which repeats. This would imply the AFS header has repeating 8-byte plaintext — inconsistent with standard AFS format (would require num_files == entry0.offset, etc.).

**Most likely:** The keystream is longer than 4 bytes (not a simple repeat), and the observed repetitions are either coincidental or indicate a more complex keystream generation.

## Ghidra Analysis

### Setup
- **Ghidra:** 12.1.4 at `~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/`
- **JDK:** 21 (Temurin) 
- **Target:** `default_pe.bin` (23,068,672 bytes, PE32 Xbox PowerPC big-endian)
- **Language:** `PowerPC:BE:32:default`
- **Project:** `~/workspace/ghidra-projects/doa4/` (56MB, analyzed)

### Findings

1. **AFS filename strings** located in .rdata:
   - `cache:\spr.afs` @ 0x0061e8cd
   - `cache:\snd.afs` @ 0x0061e8ec  
   - `cache:\mot.afs` @ 0x0061e908
   - `cache:\cmn.afs` @ 0x0061e924
   - `cache:\chrthree.afs` @ 0x0061e964
   - `cache:\chrtwo.afs` @ 0x0061e988
   - `cache:\chrone.afs` @ 0x0061e9ac
   - **No xrefs** to these strings (indirect addressing)

2. **Dynamic filename construction** discovered:
   - Format string `%ls.anm%d.afs` @ file offset 0x285f41 (VA 0x00685f41)
   - Format string `%s:\anm.afs` @ file offset 0x28684b (VA 0x0068684b)
   - **No xrefs** to these either (highly optimized code)

3. **CRI AFS library** statically linked:
   - Error strings found: `E0040701:Illigal format(not AFS).(adxf_GetPtStat)`
   - Error strings found: `E20040917 : It is impossible to load AFS files in parallel.`
   - No `adxf_*` symbols (static link, no imports)
   - Only 10 unnamed external functions (import table stripped)

4. **No XOR-heavy functions** found (checked 5000 functions, none with 5+ XOR instructions)
   - Suggests decryption may use ADD/SUB, table lookup, or is inlined

5. **No AFS magic constant** (0x41465300) found in code (checked 191k instructions)
   - Decryption verification may be implicit or use memcmp

### Scripts Developed
Located in `~/workspace/ghidra-projects/doa4/`:
- `FindAfsDecrypt.java` — Find AFS strings and xrefs
- `FindAfsXrefs.java` — Aggressive xref search with data refs
- `FindAfsCallers.java` — Find CRI library callers
- `FindAfsMagic.java` — Search for AFS magic constant in code
- `FindXorLoops.java` — Find XOR-heavy functions
- `FindLis61.java` — Find PowerPC address construction for AFS strings
- `DecompileAround.java` — Decompile around specific addresses
- `FindFmtXrefs.java` — Find xrefs to format strings
- `ListImports.java` — List imported functions

## Hypotheses Tested (Ruled Out)

| Hypothesis | Result |
|------------|--------|
| 4-byte repeating XOR key | ❌ Bytes 4+ decrypt to garbage |
| Incrementing 4-byte key (key+i) | ❌ Block 1+ garbage |
| Key = MD5/SHA1/CRC32(filename) | ❌ No match |
| Key = djb2/sdbm/FNV-1a(filename) | ❌ No match |
| Key stored in PE binary | ❌ Not found (searched all forms) |
| 16-byte repeating key with standard AFS header | ❌ No valid (N, header_size) found for N=1..500 |
| Key table in .data/.rdata | ❌ Only code pointers found |

## Recommended Next Steps

### Option A: Dynamic Analysis (Highest Success Probability)
Run DOA4 in Xenia (Xbox 360 emulator) and dump decrypted AFS from memory:
1. Set up Xenia Canary with DOA4 ISO
2. Breakpoint on file read or AFS parse
3. Dump memory buffers after decryption
4. Extract assets from decrypted dumps

### Option B: Advanced Ghidra Analysis
1. Use Ghidra's data flow analysis to trace from file read syscalls
2. Use P-code emulation to execute decryption function
3. Search for the key derivation function (takes filename, outputs key)

### Option C: Cryptanalysis
The 8-byte repeating ciphertext pattern is the strongest lead. A cryptographer should:
1. Analyze the repeating patterns across all 6 files
2. Determine if it's ECB, CTR with short nonce, or repeating XOR
3. Use the known "AFS\0" plaintext to bootstrap

## Files
- **Ghidra project:** `~/workspace/ghidra-projects/doa4/` (56MB)
- **Decrypted PE:** `~/workspace/doa4-bass/default_pe.bin` (23MB)
- **Encrypted AFS:** `~/workspace/doa4-bass/extracted/*.afs` (2.4GB)
- **Scripts:** `~/workspace/ghidra-projects/doa4/*.java`
- **Prior report:** `~/workspace/doa4-bass/EXTRACTION-REPORT.md`

## Conclusion

The encryption is a per-file keyed XOR stream cipher. The 4-byte keys are recovered, but the full keystream generation remains unknown. The keys are not stored in the binary and are not simple filename hashes — they are likely derived via a custom algorithm or decrypted from an obfuscated table at runtime.

**This is a solvable problem** but requires either dynamic analysis (Xenia) or deeper Ghidra work (data flow/emulation) than static xref analysis could provide.
