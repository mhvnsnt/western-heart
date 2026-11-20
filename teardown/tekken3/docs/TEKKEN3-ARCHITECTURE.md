# Tekken 3 (PS1) — Complete Architecture Teardown

**Source:** Tekken 3 (USA) SLUS-00402, analyzed from disc image
**Date:** 2026-10-12
**Purpose:** Study how the best PS1 fighting game was engineered, apply to our games

> STEAL-LIKE-AN-ARTIST: This is study material. We learn the techniques, we build our own original games.

---

## Disc Structure

```
Tekken 3 (USA)
├── Track 1 (DATA, MODE2/2352, ~630MB raw)
│   └── ISO 9660 filesystem (only 6 files visible!)
│       ├── SYSTEM.CNF                    → Boot config
│       └── TEKKEN3/
│           ├── SLUS_004.02    (1.2MB)    → Main executable (PSX-EXE)
│           ├── TEKKEN3.BNS    (37MB)     → Asset archive (models, textures, data)
│           ├── TEKKEN3.XAS    (488MB)    → XA audio/video streams (FMV, music)
│           ├── TEKKEN3.DA     (0 bytes)  → Placeholder
│           └── TEKKEN3.DMY    (0 bytes)  → Placeholder
├── Track 2 (AUDIO) → CD-DA music
└── Track 3 (AUDIO) → CD-DA music
```

**Key insight:** Only 6 files in the ISO filesystem. Almost everything lives in the BNS archive or streams from raw disc sectors. This is how PS1 games bypassed ISO filesystem overhead for performance.

---

## The Executable (SLUS_004.02)

| Property | Value |
|---|---|
| Format | PSX-EXE |
| Size | 1,185,792 bytes (0x121800) |
| .text base | 0x80010000 |
| .text size | 0x121000 (~1.18MB of code) |
| Entry point | 0x80079C70 |
| Stack | 0x801FFFF0 |
| Region | North America |

The entry point runs standard PS1 boot code (BSS clear, stack setup) — confirmed via disassembly.

### Character Names in Binary

Found via string scan: BRYAN, HEIHACHI, HWOARANG, JULIA, MOKUJIN, PANDA, TIGER, XIAOYU, YOSHIMITSU, plus UI strings (PLAYER SELECT, ROUND, FINAL ROUND, COMMAND).

---

## The BNS Archive (TEKKEN3.BNS)

| Property | Value |
|---|---|
| Size | 38,150,144 bytes (37MB) |
| Sectors | 18,628 (2048-byte logical sectors) |
| Records | 303 (indexed by table in executable) |

### BNS Table (in executable)

- **Location:** File offset `0x14C00` in SLUS_004.02 (virtual address `0x80024400`)
- **Format:** 303 entries × 8 bytes = `{ u32 sector, u32 size }` (little-endian)
- **Sector** is relative to start of TEKKEN3.BNS (not absolute disc LBA)
- **Verified:** 297/303 entries point to valid data within the BNS

### Record Inventory

| ID Range | Count | Type | Size Each | Likely Contents |
|---|---|---|---|---|
| 0–3 | 4 | Large data | ~515–725KB | Core game data (stages? shared assets?) |
| 4 | 1 | Empty | 0 bytes | Unused slot |
| 5–55 | ~51 | Mixed | 17–460KB | Textures, UI, misc data |
| 56–70 | 15 | Model candidates | ~18–23KB | Character models or parts |
| 71–275 | 52 | **3DMK models** | ~24–29KB | **Character/stage geometry** |
| 276–302 | 27 | Mixed | Various | Audio banks (VAB), misc |

### The 3DMK Model Format

52 records with `3DMK` magic signature. Each record:

```
Offset  Size    Contents
0       8       Pre-header (u32 type=0x1B, u32 unknown=0x64)
8       4       Magic: "3DMK"
12      12      Header fields
24      1512    Row table (27 rows × 56 bytes)
1536    ~25KB   Payload (vertex/normal/UV/face data)
```

Each **row** (56 bytes = 14× u32) contains offsets pointing into the payload:
- Words 0–2: Offsets to geometry streams (vertices, faces, UVs)
- Word 12: Conditional offset (present when word 10 == 1)

**This is a multi-part mesh format.** Each row = one mesh segment (body part). The 27 rows per record suggest characters are built from ~27 separate mesh pieces.

**Stepping pattern:** 3DMK records are spaced 4 IDs apart (71, 75, 79, 83...). This suggests groups of related records — possibly LOD variants, costume variants, or body-part groupings per character.

---

## Texture System (TIM)

- **8,556 TIM textures** found in the BNS archive
- Format: Standard PS1 TIM (4-bit, 8-bit, 16-bit, 24-bit)
- Dominant sizes: 32×32 (5,868), 64×64 (1,710), 48×48 (332)
- Small textures suggest heavy texture atlasing and tiling

**Lesson:** Tekken 3 uses MANY small textures rather than few large ones. This is a PS1 VRAM optimization — 1MB VRAM means you tile small textures aggressively.

---

## Audio System

- **TEKKEN3.XAS** (488MB): XA-ADPCM audio/video streams — FMV cutscenes, background music
- **VAB banks** in BNS: VH (sample headers) + VB (sample data) for sound effects
- 48 split sound banks identified
- Tracks 2–3: CD-DA audio (Red Book audio for music)

---

## What This Teaches Us

### 1. Asset Streaming Architecture
Tekken 3 doesn't load everything at once. The BNS table is an index — the game loads specific records on demand (character select → load character models, stage select → load stage). **Our games should do the same:** indexed asset packs, load on demand.

### 2. Multi-Part Character Models
Characters aren't single meshes — they're ~27 mesh segments. This allows:
- Per-part texture assignment (different materials per body part)
- Selective animation (only animate the parts that move)
- Memory efficiency (share parts between characters/costumes)

### 3. Texture Budget Discipline
8,556 textures, mostly 32×32 and 64×64. On PS1's 1MB VRAM, every texture is tiny and purposeful. **Lesson for our games:** even on modern hardware, disciplined texture budgets = better performance.

### 4. Separation of Code and Data
1.2MB executable + 37MB data archive + 488MB streams. Clean separation. The executable is PURE LOGIC — all content is data-driven.

---

## Tools Used

All open-source, pulled from GitHub:
- **tekken3recompiled** (fishb0nes98) — BNS/TIM/VAB/model tools, Python stdlib only
- **capstone** — MIPS disassembly for executable analysis
- **pycdlib** — ISO 9660 filesystem extraction
- Custom Python scripts for BIN→ISO conversion and table parsing

## Reproducibility

Every step is scripted in this repo. To redo this analysis on another PS1 game:
1. Extract BIN/CUE → convert Track 1 to ISO
2. Extract ISO filesystem with pycdlib
3. Find the asset archive (usually the largest .BIN/.DAT file)
4. Look for the index table in the executable (search for sector/size patterns)
5. Scan for magic signatures (TIM = `\x10\x00\x00\x00`, TMD = `A\x00\x00\x00`)
6. Document everything
