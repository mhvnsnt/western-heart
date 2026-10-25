# Chimera Build — Teardown Completion Status

**Updated:** 2026-10-23 (Tekken 5 row added by T5 extraction lane)
**Owner directive:** 100% teardown of every game. No gaps. No deferral.

---

## Scoreboard

| # | Game | Score | Status |
|---|------|-------|--------|
| 1 | Tekken 3 | **100%** ✅ | Complete: 7 fighters, 15 stages, 8,556 textures, pose solved, 3,247 moves |
| 2 | WWF No Mercy | **100%** ✅ | Complete: 5,787 anims, 3,570 models, 5,029 textures, 17 arenas |
| 3 | Virtua Fighter 5 | **100%** ✅ | Complete: 19 fighters + 38 stages on release `vf5-ps3-v1` |
| 4 | Urban Reign | **~95%** ✅ | VGS cracked, 509 files, **1,033 audio files extracted**. Missing: DCM semantics, inner PPK geometry |
| 5 | WWE WrestleMania XIX | **~80%** | Extraction done, ISO backed up. **Missing: format semantics** (watchdog lane active) |
| 6 | Soulcalibur II | **~60%** | Xbox version extracted. **Missing: PS2 filesystem RE** (owner decision needed) |
| 7 | Tekken 7 (King) | **~40%** | 5 King variants (T8 base, T8 S2, T3 legacy, T7 1P, Armor King). Full game never acquired |
| 8 | Tekken 6 (PSP) | **~30%** | Videos + structure done, EBOOT decrypted. **Missing: DATA401 models** (encrypted) |
| 9 | Eastern Mind | **~20%** | Game safe on release `eastern-mind-v1`. **Missing: extraction** |
| 10 | Tekken Tag Tournament 2 | **~15%** | 26/26 chunks on release. **Missing: download + STFS extraction** (downloading now) |
| 11 | Dead or Alive 4 | **~15%** | 30/30 chunks on release `doa4-iso-v1`. **Missing: reassemble + extract** |
| 12 | Soulcalibur VI | **~10%** | Mechanics doc only. Game binary not acquired (32GB) |
| 13 | Dead or Alive 6 | **~10%** | Mechanics doc only. Game binary not acquired (50GB+) |
| 14 | Tekken 5 (PS2) | **~15%** | ISO acquired + surveyed 2026-10-23, DW anim files located (`teardown/tekken5/`). **Missing: model/anim/moveset decode** (romD + TK5DATA0 formats → RE bench) |

---

## Per-Game Blockers & Unblock Paths

### Tekken 6 — DATA401 Models (30% → needs decrypt)
**What's done:** 46 ending videos, ISO structure map, 40-fighter roster, EBOOT.BIN decrypted via KIRK (valid ELF, 4.0MB). PAC system symbols confirmed in decrypted EBOOT (`packdatas_t`, `ReadInfo`, `ktRead`, `openPac`).
**What's missing:** All 3D models, textures, stages — locked in encrypted `DATA401.IDX` (26KB) + 384MB data region. Entropy 7.99/8.0 (AES-level). Earlier "data files are plain" claim was WRONG.
**Unblock path (pick one):**
1. **MIPS RE** (multi-day): Reverse-engineer decrypted EBOOT to find DATA401 key derivation. Have `psprecomp` + PPSSPP keys.
2. **PPSSPP live dump** (faster): Run PPSSPP with ISO, dump decrypted game data from memory. Guide ready at `teardown/tekken6/PPSSPP-LIVE-RUN-GUIDE.md`. Needs browser task with display.

### TTT2 — Download + STFS Extract (15% → downloading)
**What's done:** 26/26 chunks verified on release `ttt2-7z-v1`. STFS/GoD readers acquired (`zarmanager`). Teardown docs (INVENTORY, ROSTER 59 fighters, STAGES 29) in repo.
**What's missing:** Full 13.3GB download + STFS extraction + model/moveset pull.
**Status:** Download RESUMED 2026-10-13 22:42 UTC (6/26 parts active, background). ETA ~5hrs at GitHub speeds.
**Disk warning:** Extraction needs ~27GB peak (7z + extracted). Currently 17GB free. Disk cleanup worker active.

### Urban Reign — Audio Library (90% → offset puzzle)
**What's done:** 509 files, VGS decode cracked, 72 UI screens, 46 motion packs, 256 mission defs, AFS offset map (2,431 entries).
**What's missing:** ~1,032 audio files (SE/BGM, ~367MB ADX).
**Breakthrough (2026-10-13 22:50 UTC):** Parsed ISO9660 from release parts — real `DVD000.AFS` offset is **3,063,840,768** (the old listing had size/offset swapped). AFS magic verified, entry table matches map exactly. **COMPLETE:** 1,033 audio files extracted via parallel range-fetch (8 workers) → `teardown/urban-reign/audio/`, committed to main. No full ISO download needed. Extractor: `agent-ops/ur-extract/ur_audio_parallel.py`.

### WMXIX — Format Semantics (80%, watchdog lane active)
**What's done:** Full extraction, 126 wrestler OBJs, 170 YANM anims, 2,690 CAW parts, ISO backed up.
**What's missing:** ECD identity, base-ID generation fn, L/R final, ID-block semantics, CAW.gci (needs browser Dolphin).
**Status:** Watchdog lane active (attempts=28). NOT duplicated by this sweep — coordinating only.

### SCII — PS2 Filesystem (60%, owner decision needed)
**What's done:** Xbox version extracted. PS2 ISO (1.38GB) on release `soulcalibur2-ps2-v1`. TEARDOWN.md documents Namco proprietary PS2 FS.
**What's missing:** PS2 filesystem reverse-engineering to extract models/stages.
**Owner decision needed:** Xbox vs PS2 as primary source. Xbox is done; PS2 needs multi-day Namco FS RE.

### Tekken 7 — Full Game (40%, King-focused)
**What's done:** 5 King variants with exact poly counts (T8 base 50,950p, T8 S2 43,462p, T3 legacy 66,052t, T7 1P 54,612t, Armor King 48,870p). Pantera reskin/decals/tail done.
**What's missing:** Full 51GB game never acquired (no landing zone). Other fighters' models rely on rigmodels/DeviantArt pulls.
**Unblock path:** 51GB landing problem unsolved. TeraBox Premium (5TB) could receive it via browser upload if source found.

### DOA4 — Reassemble + Extract (15%, chunks done)
**What's done:** 30/30 chunks verified on release `doa4-iso-v1` (7.8GB total). Download checkpoint marked done.
**What's missing:** Re-download chunks → reassemble ISO → extract → teardown.
**Next step:** Needs ~16GB disk (7.8GB chunks + 7.8GB ISO + extraction). **Sequenced AFTER TTT2** — can't run both simultaneously (TTT2 needs 13GB download + 27GB extraction peak). TTT2 first, then DOA4.

### Eastern Mind — Extraction (20%)
**What's done:** Game safe on release `eastern-mind-v1` (549MB, byte-verified).
**What's missing:** Full extraction — bitmap/stage art, any 3D data, audio.
**Next step:** Download from release → extract → sort by Western Heart stage mapping.

### SCVI / DOA6 — Acquisition (10% each)
**What's done:** Full mechanics teardown docs (PR #44, #45).
**What's missing:** Game binaries (SCVI 32GB, DOA6 50GB+). Not on Archive.org.
**Unblock path:** Stepdown strategy (older versions) or owner-sourced copies.

---

## Disk Status
- **Current:** 83% (17GB free of 100GB)
- **Cleanup worker:** Active, moving to TeraBox/GitHub per SAFE-STORAGE-FIRST law
- **TeraBox:** 5TB Premium Plus (trial expires 2026-10-20), 128GB single-file upload
- **Pressure points:** TTT2 download (13GB) + extraction (27GB peak), DOA4 reassembly (16GB)
