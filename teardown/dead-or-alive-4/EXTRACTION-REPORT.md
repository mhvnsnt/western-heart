# DOA4 Full Extraction Report
**Date:** 2026-10-17  
**ISO:** doa4.iso (7,834,892,288 bytes, 30/30 parts verified)  
**Format:** Xbox 360 XGD (XEX2 at 0x3f23000)

## Extraction Tools

### 1. XGD Partition Extraction
**Tool:** `tools/extract_iso.py` (patched from sp00nznet/360tools)

**Discovery:** DOA4 uses a non-standard XGD layout. The XDVDFS partition is at
file offset `0x390000` (magic at `0x3a0000`), not the standard XGD2 offsets
(0x0FD90000, 0x0FDA0000).

**Patch:** Added `0x003A0000` to `KNOWN_OFFSETS` in extract_iso.py. The script's
existing adjusted-base logic (magic_off - 0x10000) correctly computes the
partition base.

**Result:** 14 files extracted (3.0GB total):
| File | Size | Contents |
|------|------|----------|
| default.xex | 16MB | Game executable (Xbox 360 XEX2) |
| chrone.afs | 349MB | Characters (ENCRYPTED) |
| chrtwo.afs | 522MB | Characters (ENCRYPTED) |
| chrthree.afs | 727MB | Characters (ENCRYPTED) |
| anm.afs | 2.9MB | Animations (ENCRYPTED) |
| mot.afs | 71MB | Motions (ENCRYPTED) |
| stg.afs | 777MB | Stages (ENCRYPTED) |
| avt.afs | 215MB | Avatars (standard AFS, 700 files) |
| snd.afs | 119MB | Sound (standard AFS, 201 files) |
| spr.afs | 171MB | Sprites (standard AFS, 53 files) |
| cmn.afs | 8.6MB | Common (standard AFS, 7 files) |
| dic/ | 480KB | Dictionaries (3 files) |

### 2. AFS Archive Extraction
**Tool:** `tools/afs_extract.py` (standard CRI AFS format)

**Result:** 961 files extracted from standard AFS archives:
- `extracted_afs/cmn/`: 7 files
- `extracted_afs/spr/`: 53 files
- `extracted_afs/snd/`: 201 files
- `extracted_afs/avt/`: 700 files

**File types identified:**
- `XPR2` (38 files) — Xbox 360 textures
- `AVAT` (27 files) — Avatar data
- `KBDS` (26 files) — Unknown
- `DNBW` (23 files) — Unknown (possibly models)

### 3. XEX Decryption
**Tool:** 360tools `extract_pe.py`

**Result:** `default.xex` (16MB) decrypted and decompressed to 22MB PE.
- Entry point: 0x8277E878
- Image base: 0x82000000
- Contains AFS loading code with string references to all .afs files
- CRI Middleware AFS library (`adxf_GetPtStat`)

## ENCRYPTION BLOCKER

### Status: 6 AFS archives use custom encryption
- chrone.afs (349MB), chrtwo.afs (522MB), chrthree.afs (727MB)
- anm.afs (2.9MB), mot.afs (71MB), stg.afs (777MB)

### Findings
1. **anm.afs** decrypts header to `AFS\0` with 4-byte XOR key `80b97b52`,
   but file count and entries are garbage. Key may be longer or algorithm differs.

2. **Other files** do NOT decrypt with the anm.afs key. Each file appears to
   use a unique key or different encryption.

3. **Entropy** 6.6-7.0 (not 8.0), indicating weak cipher, not strong encryption.

4. **PE analysis** shows CRI Middleware AFS library. The decryption is likely
   a custom Team Ninja layer on top of standard AFS.

### Next Steps
1. Install Ghidra and analyze `default.xex` (decrypted PE) to find the
   AFS decryption routine
2. Look for XOR keys or crypto constants near AFS string references
   (found at PE offset 0x21e8da)
3. Alternative: Run DOA4 in Xenia emulator and dump decrypted AFS from memory

## Files for Western Heart
- `tools/extract_iso.py` → `teardown/dead-or-alive-4/tools/`
- `tools/afs_extract.py` → `teardown/dead-or-alive-4/tools/`
- `extracted_afs/` (961 files) → GitHub Release (too large for git)
- This report → `teardown/dead-or-alive-4/EXTRACTION-REPORT.md`
