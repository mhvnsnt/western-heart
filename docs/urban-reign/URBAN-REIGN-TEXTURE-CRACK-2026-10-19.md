# Urban Reign PPK Texture Format — Crack Attempt WORKLOG

**Task:** CRACK THE URBAN REIGN PPK TEXTURE FORMAT (owner order 2026-10-19 ~03:42 CDT: "Find out how to decide and crack that format.")
**Lane:** ur-texcrack (subagent aedc4fdc)

## HOW TO DECIDE: The Decision Framework

When facing an unknown proprietary texture format, the decision process is:

1. **Survey the container** — Parse the PPK chunk table. Identify all chunks by type/size.
2. **Classify by content** — For each chunk: float-ratio test, entropy analysis, zero-count.
3. **Test standard formats FIRST** — Before assuming proprietary encoding, test:
   - Raw linear (8-bit, 4-bit, 16-bit) at standard dimensions
   - PS2-native swizzled (PSMT8/PSMT4) using verified deswizzle tables
   - Compressed (zlib, raw deflate)
4. **Look for external ground truth** — Community mods, recomp projects, emulator texture dumps.
5. **Document negative results** — A proven negative is progress, not failure.

## WHAT I DID

### 1. Container Survey (char001.ppk, char002.ppk, char036.ppk)
- Parsed chunk tables via GitHub API. Layouts vary per character.
- char001: 14 chunks. char002: 5 chunks (simpler). char036: 11 chunks.
- No chunk has clean texture dimensions (16,384 / 65,536 / 8,192 bytes).

### 2. The 16KB 0x8001 Chunk (char001 @ 0x2971)
- Size: 16,143 bytes. Entropy: 5.80. Zeros: 30% (4,819/16,143).
- **VERDICT: NOT a texture.** 30% zeros is impossible for texture data.
- It's structured records (repeating 0x43 patterns, mixed float/int data).
- Tested: 8-bit linear (128×128), 8-bit PS2-deswizzled, 4-bit — all noise.

### 3. PS2 Deswizzle Implementation
- Extracted PSMT8 block/column tables from urban-reign-recomp's `ps2_gs_memory.cpp`.
- Implemented `deswizzle8.py` with verified tables (BLOCK8, COL8).
- Tested on candidate regions — all produced noise, not images.
- **Either the data isn't PS2-swizzled, or it's not texture data.**

### 4. The 0x0002 Chunk Tail (423KB after vertex records)
- Found 423,168 bytes of mixed-content data after the last vertex separator.
- Entropy map revealed high-entropy regions:
  - Region A (0x04000-0x0F000): 44KB, ent 6.5-7.4
  - Region C (0x24000-0x26000): 8KB EXACTLY, ent 7.5
  - Region E (0x4F000-0x66000): 68KB, ent 6.5 consistent
- Tested Region C as 128×64 8-bit (linear, deswizzled, 4-bit) — all noise.
- Region E shows 16-byte record structure with `XX 00` headers — likely command/stream data, not textures.

### 5. External Ground Truth: urban-reign-redux
- Downloaded PaulT4.zip from GitHub releases (3.2MB).
- Contains 4 HD texture PNGs (1024×1024 RGBA).
- **VIEWED WITH OWN EYES**: It's Paul's character texture atlas (face, hair, torso with scorpion tattoo, clothes, eye).
- Filenames reveal originals were 128×128 (`r128x128` tag).
- **These are REAL, WORKING textures** — but for modded Tekken characters, not original Urban Reign fighters.

### 6. Compression Tests
- zlib, raw deflate on candidate chunks — all negative (except 0-byte false positive).

## DECISION

**The PPK texture pixel format is NOT cracked.** The high-entropy regions do not decode as textures using standard PS2 methods.

**However**, the practical path forward is clear:

### Recommended Path: Redux Textures
The urban-reign-redux project has 167 REAL textures (HD replacements). These are:
- Extracted from actual gameplay via PCSX2
- Verified working (I viewed one)
- Available via GitHub releases (character packs)

For the 72 original Urban Reign fighters, the full 167-texture pack (Google Drive, currently rate-limited) contains the original character textures.

### Long-term Path: Binary RE
Full Ghidra analysis of SLUS_212.09 (6.3MB executable) to find the texture loading function. This is multi-day work.

## HONEST FLAGS

1. **0 of 72 characters' textures decoded from PPKs.** The format remains undecoded.
2. **The redux textures I verified are for modded characters**, not the original 72 fighters.
3. **I did not fake any textures.** No procedural/generated textures created.
4. **The 16KB chunk is NOT texture data** — this corrects the assumption that it might be.

## Files
- `deswizzle8.py` — PSMT8 deswizzler with recomp-project tables (for future use)
- `test_*.png` — Test renders (all negative results, documented)
- `textures/CurrentRoster/` — Redux PaulT4 HD textures (reference)
- `char001.ppk`, `char002.ppk` — Local copies for analysis
