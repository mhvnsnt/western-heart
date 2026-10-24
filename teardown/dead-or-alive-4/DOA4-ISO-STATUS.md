# DOA4 ISO — Verification and Extraction Status

**Date:** 2026-10-16  
**Status:** ✅ VERIFIED, ⏳ EXTRACTION BLOCKED (tooling)

## Verification
- **Size:** 7,834,892,288 bytes (exact match to expected: 29×262,144,000 + 232,716,288)
- **Assembly:** 30 parts downloaded from GitHub Release `doa4-iso-v1`, appended in strict sequential order (01→30)
- **Format confirmed:** Xbox 360 XGD
  - XEX2 magic found at offset 0x3f23000 (66,203,648 bytes)
  - Security sector data at 0x38e800
  - Manufacturing string "TC200106L0X11" at 0x38f040
- **Local path:** `~/workspace/doa4-bass/doa4.iso`

## Assembly History
The ISO was assembled over two sessions due to daemon restarts:
1. **Session 1:** Downloaded parts 02,03,04 but appended out-of-order (missing part_01 header). Fixed by re-downloading part_01 and prepending.
2. **Session 2:** Discovered `curl -C -` resume was corrupting files (servers ignoring Range headers, appending duplicate data). Rebuilt with fresh downloads only.
3. **Session 3 (final):** All 30 parts downloaded fresh, verified at exact byte sizes, appended sequentially with ISO-size verification before each append. Final verification: 7,834,892,288/7,834,892,288 bytes ✅

## Extraction Blocker
**Tool:** `extract-xiso` v2.7.1  
**Problem:** Only supports original Xbox (Xbox 1) ISOs. Checks for `MICROSOFT*XBOX*MEDIA` header at offset 0.  
**Why it fails:** DOA4 is Xbox 360 (XGD/XGD2 format), which uses a completely different disc structure. The XEX2 executable and security sectors are present, but extract-xiso cannot parse XGD.

**Needed:** Xbox 360 XGD extraction tool for Linux. Options:
- `wx360` or similar XGD parser
- Python FATX/XGD library
- Manual XGD structure parsing

## What's Available Now (Without ISO Extraction)
- ✅ DOA5 Bass Armstrong model (20MB, 4 variants) — `models/bass-armstrong/`
- ✅ Complete Bass movelist reference (278 lines) — `movesets/bass-armstrong/`
- ✅ DOA4 ISO (verified, stored locally) — ready for extraction when tooling is available

## Next Steps
1. Research and acquire Xbox 360 XGD extraction tool
2. Extract full file system from doa4.iso
3. Locate Bass Armstrong's character files (models, textures, animations)
4. Extract all other characters' models and movesets
5. Extract stages, audio, UI assets
